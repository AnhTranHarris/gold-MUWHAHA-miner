"""Causal path-aware feature contract for the R9 v2 entry repair.

The frozen 102-feature vector remains available as historical context. This
contract adds an ordered quote-time grid and six-mark multi-timescale quote
excitation state. Entry geometry is never reconstructed from M1 OHLC.
"""
from __future__ import annotations
import bisect
from dataclasses import dataclass
import math
import numpy as np

FEATURE_VERSION = 'r9_v2_ordered_quote_grid_v2'
LEGACY_FEATURE_COUNT = 102
GRID_LAGS_MS = tuple(range(250, 5001, 250)) + (7500, 10000, 15000, 30000, 45000, 60000, 120000, 300000)
GEOMETRY_WINDOWS_MS = (5000, 15000, 30000, 45000, 60000, 300000)
SEGMENTS_MS = ((250,500),(500,1000),(1000,2000),(2000,5000),(5000,15000),
               (15000,30000),(30000,45000),(45000,60000),(60000,120000),(120000,300000))
EXCITATION_TAUS_MS = (250, 1000, 5000, 15000, 45000)

def _tag(ms:int) -> str:
    return f'{ms}ms' if ms < 1000 else f'{ms//1000}s'

@dataclass(frozen=True)
class QuotePoint:
    utc_ms: int
    bid: float
    ask: float
    @property
    def mid(self):
        return .5*(self.bid+self.ask)
    @property
    def spread(self):
        return self.ask-self.bid

class LaggedQuoteGeometry:
    """Bounded raw quote history with fixed causal lag sampling.

    Each grid point is the last quote at-or-before t-lag. A future quote is never
    borrowed to fill a missing slot. Dense 250 ms lags preserve the first 5 s;
    longer lags carry the 15/30/45/60 s and rolling five-minute geometry.
    """
    def __init__(self, keep_ms=305_000):
        self.keep_ms = int(keep_ms)
        self.t=[]; self.b=[]; self.a=[]

    def append(self, q):
        t=int(q.utc_ms); bid=float(q.bid); ask=float(q.ask)
        if ask < bid or bid <= 0:
            raise ValueError('invalid quote')
        if self.t and t < self.t[-1]:
            raise ValueError('nonchronological')
        self.t.append(t); self.b.append(bid); self.a.append(ask)
        if len(self.t) > 10000 and self.t[0] < t-self.keep_ms-5000:
            cut=bisect.bisect_left(self.t, t-self.keep_ms)
            if cut > 2500:
                self.t=self.t[cut:]; self.b=self.b[cut:]; self.a=self.a[cut:]

    def _sample(self, lag_ms:int):
        if not self.t:
            raise ValueError('uninitialized')
        target=self.t[-1]-int(lag_ms)
        j=bisect.bisect_right(self.t,target)-1
        if j < 0:
            j=0
        return j

    def snapshot(self):
        if not self.t:
            raise ValueError('uninitialized')
        t=self.t[-1]; bid=self.b[-1]; ask=self.a[-1]
        mid=.5*(bid+ask); spread=ask-bid
        sampled={}; out=[]
        for lag in GRID_LAGS_MS:
            j=self._sample(lag)
            pb=self.b[j]; pa=self.a[j]; pm=.5*(pb+pa); ps=pa-pb
            age=t-self.t[j]
            sampled[lag]=(pm,pb,pa,ps,age)
            db=bid-pb; da=ask-pa
            out.extend((mid-pm, db, da, spread-ps,
                        (db-da)/(abs(db)+abs(da)+1e-6),
                        min(1.5, age/max(1.,float(lag)))))
        for short,long in SEGMENTS_MS:
            sm,sb,sa,ss,_=sampled[short]
            lm,lb,la,ls,_=sampled[long]
            out.extend((sm-lm, sb-lb, sa-la, ss-ls))
        current=(0,mid)
        for horizon in GEOMETRY_WINDOWS_MS:
            pts=[current]
            for lag in GRID_LAGS_MS:
                if lag <= horizon:
                    pts.append((lag,sampled[lag][0]))
            pts.sort(reverse=True)
            vals=[x[1] for x in pts]; ages=[x[0] for x in pts]
            hi=max(vals); lo=min(vals); rng=hi-lo
            ih=vals.index(hi); il=vals.index(lo)
            path=sum(abs(vals[k]-vals[k-1]) for k in range(1,len(vals)))
            disp=vals[-1]-vals[0]
            signs=[]
            for k in range(1,len(vals)):
                d=vals[k]-vals[k-1]
                if d>1e-12: signs.append(1)
                elif d<-1e-12: signs.append(-1)
            turns=sum(signs[k]!=signs[k-1] for k in range(1,len(signs)))
            out.extend((
                disp/(path+1e-9),
                (2*(vals[-1]-lo)/(rng+1e-9)-1) if rng>1e-12 else 0.,
                (ages[il]-ages[ih])/max(1.,float(horizon)),
                turns/max(1,len(signs)-1),
                rng,
            ))
        return np.asarray(out,np.float32)

def grid_feature_names():
    names=[]
    for lag in GRID_LAGS_MS:
        tag=_tag(lag)
        names += [f'grid_mid_{tag}',f'grid_bid_{tag}',f'grid_ask_{tag}',
                  f'grid_spread_delta_{tag}',f'grid_move_asym_{tag}',f'grid_coverage_{tag}']
    for short,long in SEGMENTS_MS:
        names += [f'seg_mid_{_tag(short)}_{_tag(long)}',f'seg_bid_{_tag(short)}_{_tag(long)}',
                  f'seg_ask_{_tag(short)}_{_tag(long)}',f'seg_spread_{_tag(short)}_{_tag(long)}']
    for h in GEOMETRY_WINDOWS_MS:
        tag=_tag(h)
        names += [f'geom_signed_eff_{tag}',f'geom_terminal_pos_{tag}',f'geom_extreme_order_{tag}',
                  f'geom_turn_rate_{tag}',f'geom_range_{tag}']
    return tuple(names)

def excitation_vector(hawkes_features:dict):
    """Turn six-mark recency state into model inputs, never ad-hoc profit boosts."""
    raw=np.asarray(hawkes_features['raw_multi_tau'],dtype=np.float64)
    if raw.shape != (len(EXCITATION_TAUS_MS),6):
        raise ValueError('unexpected six-mark excitation shape')
    out=[]
    for row in raw:
        bu,bd,au,ad,sw,sn=row
        out.extend((
            (bu-bd)/(bu+bd+1e-9),
            (au-ad)/(au+ad+1e-9),
            (bu+au-bd-ad)/(bu+au+bd+ad+1e-9),
            (sn-sw)/(sn+sw+1e-9),
            math.log1p(max(0.,float(row.sum()))),
        ))
    out.extend((float(hawkes_features['direction']),float(hawkes_features['spread_pressure']),
                float(hawkes_features['entropy'])))
    return np.asarray(out,np.float32)

def excitation_feature_names():
    names=[]
    for tau in EXCITATION_TAUS_MS:
        tag=_tag(tau)
        names += [f'exc_bid_dir_{tag}',f'exc_ask_dir_{tag}',f'exc_price_dir_{tag}',
                  f'exc_spread_balance_{tag}',f'exc_burst_{tag}']
    names += ['exc_intensity_direction','exc_intensity_spread','exc_intensity_entropy']
    return tuple(names)

GRID_NAMES=grid_feature_names()
EXCITATION_NAMES=excitation_feature_names()
REPAIRED_FEATURE_NAMES=tuple([f'legacy_{i:03d}' for i in range(LEGACY_FEATURE_COUNT)])+GRID_NAMES+EXCITATION_NAMES
REPAIRED_FEATURE_COUNT=len(REPAIRED_FEATURE_NAMES)
ORIENTED_NAMES=frozenset(
    n for n in REPAIRED_FEATURE_NAMES
    if n.startswith(('grid_mid_','grid_bid_','grid_ask_','grid_move_asym_',
                     'seg_mid_','seg_bid_','seg_ask_','geom_signed_eff_',
                     'geom_terminal_pos_','geom_extreme_order_','exc_bid_dir_',
                     'exc_ask_dir_','exc_price_dir_'))
)

def compose_repaired_features(legacy_x, geometry:LaggedQuoteGeometry, hawkes_features:dict):
    legacy=np.asarray(legacy_x,dtype=np.float32)
    if legacy.shape != (LEGACY_FEATURE_COUNT,):
        raise ValueError('legacy feature contract mismatch')
    z=np.concatenate((legacy,geometry.snapshot(),excitation_vector(hawkes_features))).astype(np.float32,copy=False)
    if z.shape != (REPAIRED_FEATURE_COUNT,) or not np.isfinite(z).all():
        raise ValueError('repaired feature contract violation')
    return z

def repaired_action_views(X):
    """Canonical [BUY,SELL] side-relative views plus an explicit side scalar."""
    X=np.asarray(X,dtype=np.float32)
    if X.ndim==1:
        X=X.reshape(1,-1)
    if X.shape[1] != REPAIRED_FEATURE_COUNT:
        raise ValueError('repaired feature count mismatch')
    z=np.repeat(X,2,axis=0)
    sides=np.tile(np.asarray([1.,-1.],np.float32),len(X))
    oriented=np.asarray([i for i,n in enumerate(REPAIRED_FEATURE_NAMES) if n in ORIENTED_NAMES],dtype=np.int64)
    z[:,oriented]*=sides[:,None]
    return np.column_stack((z,sides)).astype(np.float32,copy=False)
