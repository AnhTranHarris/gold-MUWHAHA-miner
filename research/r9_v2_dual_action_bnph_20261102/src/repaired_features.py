"""Causal path-aware feature contract for the R9 v2 entry repair.

The historical 102-feature vector remains frozen for parity diagnostics. The new
learner consumes only non-specialist execution/time + 15m/1h/4h context from that
vector and adds an ordered raw Bid/Ask grid plus six-mark quote excitation state.
The old hand-weighted `evidence` and `lane_reversal` fields are intentionally not
part of the repaired model contract.
"""
from __future__ import annotations
import bisect, math
from dataclasses import dataclass
import numpy as np

FEATURE_VERSION='r9_v2_ordered_quote_grid_v5'
LEGACY_FEATURE_COUNT=102
GAP_RESET_MS=15000
FRESH_WARMUP_MS=300000
LEGACY_HORIZONS_MS=(250,500,1000,5000,15000,45000,300000,900000,3600000,14400000)
LEGACY_WIN=('mid_disp','spread_avg','bid_disp','ask_disp','event_pressure','spread_change_events','rv','quote_rate','price_path_eff')
LEGACY_NAMES=tuple(['spread','last_bid_move','last_ask_move','last_spread_change','last_mid_move',
                    'micro_bid_ask_imbalance','evidence','lane_reversal','utc_hour_sin','utc_hour_cos','utc_dow_sin','utc_dow_cos']+
                   [f'{c}_{h}ms' for h in LEGACY_HORIZONS_MS for c in LEGACY_WIN])
_CONTEXT_BASE=('spread','last_bid_move','last_ask_move','last_spread_change','last_mid_move','micro_bid_ask_imbalance',
               'utc_hour_sin','utc_hour_cos','utc_dow_sin','utc_dow_cos')
_CONTEXT_HTF=tuple(f'{c}_{h}ms' for h in (900000,3600000,14400000)
                   for c in ('mid_disp','spread_avg','event_pressure','rv','quote_rate','price_path_eff'))
CONTEXT_NAMES=_CONTEXT_BASE+_CONTEXT_HTF
CONTEXT_INDICES=tuple(LEGACY_NAMES.index(n) for n in CONTEXT_NAMES)
CONTEXT_FEATURE_COUNT=len(CONTEXT_INDICES)
assert 'evidence' not in CONTEXT_NAMES and 'lane_reversal' not in CONTEXT_NAMES

GRID_LAGS_MS=tuple(range(250,5001,250))+(7500,10000,15000,30000,45000,60000,120000,300000)
GEOMETRY_WINDOWS_MS=(5000,15000,30000,45000,60000,300000)
SEGMENTS_MS=((250,500),(500,1000),(1000,2000),(2000,5000),(5000,15000),
             (15000,30000),(30000,45000),(45000,60000),(60000,120000),(120000,300000))
EXCITATION_TAUS_MS=(250,1000,5000,15000,45000)

def _tag(ms:int)->str:return f'{ms//1000}s' if ms%1000==0 else f'{ms}ms'

@dataclass(frozen=True)
class QuotePoint:
    utc_ms:int;bid:float;ask:float
    @property
    def mid(self):return .5*(self.bid+self.ask)
    @property
    def spread(self):return self.ask-self.bid

class LaggedQuoteGeometry:
    """Raw quote history sampled strictly at-or-before each causal lag point."""
    def __init__(self,keep_ms=305_000,gap_reset_ms=GAP_RESET_MS):
        self.keep_ms=int(keep_ms);self.gap_reset_ms=int(gap_reset_ms);self.t=[];self.b=[];self.a=[]
    def append(self,q):
        t=int(q.utc_ms);bid=float(q.bid);ask=float(q.ask)
        if ask<bid or bid<=0:raise ValueError('invalid quote')
        if self.t and t<self.t[-1]:raise ValueError('nonchronological')
        if self.t and t-self.t[-1]>self.gap_reset_ms:
            # Subminute geometry is continuous-path evidence. A quote drought is
            # missing path, not a long price move, so start a fresh geometry epoch.
            self.t.clear();self.b.clear();self.a.clear()
        self.t.append(t);self.b.append(bid);self.a.append(ask)
        if len(self.t)>10000 and self.t[0]<t-self.keep_ms-5000:
            cut=bisect.bisect_left(self.t,t-self.keep_ms)
            if cut>2500:self.t=self.t[cut:];self.b=self.b[cut:];self.a=self.a[cut:]
    def coverage_ms(self):
        return 0 if len(self.t)<2 else int(self.t[-1]-self.t[0])
    def _sample(self,lag):
        if not self.t:raise ValueError('uninitialized')
        j=bisect.bisect_right(self.t,self.t[-1]-lag)-1
        return 0 if j<0 else j
    def snapshot(self):
        if not self.t:raise ValueError('uninitialized')
        t=self.t[-1];bid=self.b[-1];ask=self.a[-1];mid=.5*(bid+ask);spread=ask-bid
        sampled={};out=[]
        for lag in GRID_LAGS_MS:
            j=self._sample(lag);pb=self.b[j];pa=self.a[j];pm=.5*(pb+pa);ps=pa-pb;age=t-self.t[j]
            sampled[lag]=(pm,pb,pa,ps,age)
            out.extend((bid-pb,ask-pa,spread-ps,min(1.5,age/max(1.,float(lag)))))
        for short,long in SEGMENTS_MS:
            sm,sb,sa,ss,_=sampled[short];lm,lb,la,ls,_=sampled[long]
            out.extend((sb-lb,sa-la,ss-ls))
        current=(0,mid)
        for horizon in GEOMETRY_WINDOWS_MS:
            pts=[current]+[(lag,sampled[lag][0]) for lag in GRID_LAGS_MS if lag<=horizon]
            pts.sort(reverse=True);vals=[x[1] for x in pts];ages=[x[0] for x in pts]
            hi=max(vals);lo=min(vals);rng=hi-lo;ih=vals.index(hi);il=vals.index(lo)
            diffs=[vals[k]-vals[k-1] for k in range(1,len(vals))]
            path=sum(abs(x) for x in diffs);disp=vals[-1]-vals[0]
            signs=[1 if x>1e-12 else -1 if x<-1e-12 else 0 for x in diffs];nz=[x for x in signs if x]
            turns=sum(nz[k]!=nz[k-1] for k in range(1,len(nz)))
            out.extend((disp/(path+1e-9),(2*(vals[-1]-lo)/(rng+1e-9)-1) if rng>1e-12 else 0.,
                        (ages[il]-ages[ih])/max(1.,float(horizon)),turns/max(1,len(nz)-1),rng))
        return np.asarray(out,np.float32)

def grid_feature_names():
    names=[]
    for lag in GRID_LAGS_MS:
        tag=_tag(lag);names += [f'grid_bid_{tag}',f'grid_ask_{tag}',f'grid_spread_delta_{tag}',f'grid_coverage_{tag}']
    for short,long in SEGMENTS_MS:
        names += [f'seg_bid_{_tag(short)}_{_tag(long)}',f'seg_ask_{_tag(short)}_{_tag(long)}',f'seg_spread_{_tag(short)}_{_tag(long)}']
    for h in GEOMETRY_WINDOWS_MS:
        tag=_tag(h);names += [f'geom_signed_eff_{tag}',f'geom_terminal_pos_{tag}',f'geom_extreme_order_{tag}',f'geom_turn_rate_{tag}',f'geom_range_{tag}']
    return tuple(names)

def excitation_vector(h):
    raw=np.asarray(h['raw_multi_tau'],dtype=np.float64)
    if raw.shape!=(len(EXCITATION_TAUS_MS),6):raise ValueError('unexpected six-mark excitation shape')
    out=[]
    for row in raw:
        bu,bd,au,ad,sw,sn=row
        out.extend(((bu-bd)/(bu+bd+1e-9),(au-ad)/(au+ad+1e-9),(bu+au-bd-ad)/(bu+au+bd+ad+1e-9),
                    (sn-sw)/(sn+sw+1e-9),math.log1p(max(0.,float(row.sum())))))
    out.extend((float(h['direction']),float(h['spread_pressure']),float(h['entropy'])))
    return np.asarray(out,np.float32)

def excitation_feature_names():
    names=[]
    for tau in EXCITATION_TAUS_MS:
        tag=_tag(tau);names += [f'exc_bid_dir_{tag}',f'exc_ask_dir_{tag}',f'exc_price_dir_{tag}',f'exc_spread_balance_{tag}',f'exc_burst_{tag}']
    return tuple(names+['exc_intensity_direction','exc_intensity_spread','exc_intensity_entropy'])

GRID_NAMES=grid_feature_names();EXCITATION_NAMES=excitation_feature_names()
REPAIRED_FEATURE_NAMES=CONTEXT_NAMES+GRID_NAMES+EXCITATION_NAMES
REPAIRED_FEATURE_COUNT=len(REPAIRED_FEATURE_NAMES)
ORIENTED_NAMES=frozenset(n for n in REPAIRED_FEATURE_NAMES if n in ('last_bid_move','last_ask_move','last_mid_move') or
    n.startswith(('mid_disp_','event_pressure_','grid_bid_','grid_ask_','seg_bid_','seg_ask_','geom_signed_eff_',
                  'geom_terminal_pos_','geom_extreme_order_','exc_bid_dir_','exc_ask_dir_','exc_price_dir_')))

def compose_repaired_features(legacy_x,geometry,hawkes_features):
    legacy=np.asarray(legacy_x,dtype=np.float32)
    if legacy.shape!=(LEGACY_FEATURE_COUNT,):raise ValueError('legacy feature contract mismatch')
    context=legacy[np.asarray(CONTEXT_INDICES,dtype=np.int64)]
    z=np.concatenate((context,geometry.snapshot(),excitation_vector(hawkes_features))).astype(np.float32,copy=False)
    if z.shape!=(REPAIRED_FEATURE_COUNT,) or not np.isfinite(z).all():raise ValueError('repaired feature contract violation')
    return z

def repaired_action_views(X):
    """Diagnostic side-oriented views; runtime uses independent BUY/SELL models."""
    X=np.asarray(X,dtype=np.float32)
    if X.ndim==1:X=X.reshape(1,-1)
    if X.shape[1]!=REPAIRED_FEATURE_COUNT:raise ValueError('repaired feature count mismatch')
    z=np.repeat(X,2,axis=0);sides=np.tile(np.asarray([1.,-1.],np.float32),len(X))
    oriented=np.asarray([i for i,n in enumerate(REPAIRED_FEATURE_NAMES) if n in ORIENTED_NAMES],dtype=np.int64)
    z[:,oriented]*=sides[:,None]
    return np.column_stack((z,sides)).astype(np.float32,copy=False)
