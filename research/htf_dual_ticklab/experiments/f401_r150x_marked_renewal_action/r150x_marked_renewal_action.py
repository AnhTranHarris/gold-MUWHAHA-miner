"""R150X source-native action-time research, strictly market-only at inference.

Three orthogonal mechanisms: (A) six-clock marked quote renewal intensities,
(B) separate future-only hypothetical order first-passage economics, and
(C) independent completed-HTF correct-opportunity rescue interface.

No teacher/truth/current-or-matured outcome is accepted by inference methods.
No fitted probabilities, actual order fills, or MT5 deployment claims.
Uses integer UTC ms and raw integer bid/ask in 0.001 USD units.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
import numpy as np

WINDOWS_MS = (250, 500, 1000, 5000, 15000, 30000)
PER_WINDOW = ("n_quotes", "favorable_mark_rate", "adverse_mark_rate",
              "favorable_share", "interarrival_cv", "path_efficiency",
              "signed_net_usd", "spread_widen_fraction", "last_quote_age_ms")
FEATURE_NAMES = tuple(f"renewal_{w}ms_{f}" for w in WINDOWS_MS for f in PER_WINDOW)
FORBIDDEN_RUNTIME = ("truth", "teacher", "oracle", "label", "matured", "r24", "r148b", "r150g")
assert len(FEATURE_NAMES) == 54 and not any(y in x for x in FEATURE_NAMES for y in FORBIDDEN_RUNTIME)

@dataclass(frozen=True)
class QuotePrefix:
    t: np.ndarray
    bid: np.ndarray
    ask: np.ndarray

    def __post_init__(self):
        t=np.asarray(self.t,dtype=np.int64)
        b=np.asarray(self.bid,dtype=np.int64)
        a=np.asarray(self.ask,dtype=np.int64)
        if t.ndim!=1 or b.ndim!=1 or a.ndim!=1 or not(len(t)==len(b)==len(a)):
            raise ValueError("aligned one-dimensional raw quotes required")
        if not len(t) or np.any(t[1:]<t[:-1]) or np.any(b<=0) or np.any(a<=b):
            raise ValueError("nonchronological/invalid bid-ask source")
        for v in (t,b,a): v.setflags(write=False)
        object.__setattr__(self,"t",t);object.__setattr__(self,"bid",b);object.__setattr__(self,"ask",a)

@dataclass(frozen=True)
class RenewalObservation:
    decision_ms: int
    last_quote_ms: int
    side: int
    vector: np.ndarray
    eligible_windows: tuple[bool,...]
    asof_contract: str="raw quote timestamp < decision_ms"


def marked_renewal_snapshot(quotes:QuotePrefix, *, decision_ms:int, side:int,
                            alpha:float=.5, beta_seconds:float=1.)->RenewalObservation:
    """Gamma-Poisson *quote-mark rate proxies*, NOT calibrated price-target probabilities.

    Six clocks share one exact raw tape. No zero-volume candle fabrication, no
    lookahead, and no outcome-derived runtime state. A quote revision is not
    exchange traded volume or aggressor flow.
    """
    if side not in (-1,1):raise ValueError("original direction must be +1/-1")
    if alpha<=0 or beta_seconds<=0:raise ValueError("proper positive Gamma prior required")
    t,b,a=quotes.t,quotes.bid,quotes.ask
    d=int(decision_ms)
    end=int(np.searchsorted(t,d,side="left"))
    if end==0:raise ValueError("no earlier native quote")
    v=[];valid=[]
    for width in WINDOWS_MS:
        lo=int(np.searchsorted(t,d-width,side="left"))
        # Include the previous quote before window start solely to calculate the
        # first within-window mark; never use any quote >= decision.
        start=max(0,lo-1)
        tt=t[start:end];bb=b[start:end];aa=a[start:end]
        mask=tt[1:]>=d-width
        mids=(bb.astype(np.float64)+aa.astype(np.float64))*.5
        dm=np.diff(mids)[mask]*side/1000.
        dt=np.diff(tt)[mask]
        fav=int(np.count_nonzero(dm>0));adv=int(np.count_nonzero(dm<0))
        obs_seconds=max(width/1000.,1e-9)
        lam_f=(alpha+fav)/(beta_seconds+obs_seconds)
        lam_a=(alpha+adv)/(beta_seconds+obs_seconds)
        n=int(end-lo)
        den=max(1,fav+adv)
        pos=dm[dm!=0]
        abs_path=float(np.abs(dm).sum());net=float(dm.sum())
        cv=float(np.std(dt)/max(np.mean(dt),1.)) if len(dt)>1 else 0.
        sp=(aa-bb).astype(np.int64)
        widening=int(np.count_nonzero(np.diff(sp)[mask]>0))
        v.extend((float(n),lam_f,lam_a,fav/den,cv,abs(net)/(abs_path+1e-9),
                  net,widening/max(1,len(dm)),float(d-int(t[end-1]))))
        valid.append(n>0)
    out=np.asarray(v,dtype=np.float32)
    if not np.isfinite(out).all():raise ValueError("nonfinite market-only renewal state")
    out.setflags(write=False)
    return RenewalObservation(d,int(t[end-1]),side,out,tuple(valid))

@dataclass(frozen=True)
class CompletedGeometry:
    """R120 publisher's side-aligned completed-bar state, never forward-filled."""
    side:int
    published_at_ms:int
    last_completed_bar_end_ms:int
    m1_trend:float
    m5_trend:float
    m15_trend:float
    h1_trend:float
    grid_proximity:float
    micro_slope_250ms:float
    micro_slope_30s:float
    session_anchor_trend:float



def bind_r120_published_state(*, micro92, macro36, side:int, published_at_ms:int,
                              last_completed_bar_end_ms:int)->CompletedGeometry:
    """Adapt the ORIGINAL R120 92+36 features; no new HTF/bar computation.

    R120 trend, micro slopes and session anchors are already side-aligned.
    The actual latest completed-bar end is supplied by the verified publisher;
    it is never inferred from a current/incomplete bar.
    """
    x=np.asarray(micro92,dtype=np.float64);h=np.asarray(macro36,dtype=np.float64)
    if x.shape!=(92,) or h.shape!=(36,) or not np.isfinite(x).all() or not np.isfinite(h).all():
        raise ValueError("R120 original micro92/macro36 source vector required")
    if side not in (-1,1):raise ValueError("original side required")
    # R120 m*11 micro, session 3*6, and completed HTF 4*9.
    active=np.array([x[66],x[72],x[78]])>0.5
    anchors=np.array([x[67],x[73],x[79]])
    anchor=float(np.mean(anchors[active])) if active.any() else 0.
    # R120 grid quartile distance is already normalized to [0,0.5].
    grid=float(np.min(h[[14,23,32]]))
    return CompletedGeometry(side,int(published_at_ms),int(last_completed_bar_end_ms),
        float(h[0]),float(h[9]),float(h[18]),float(h[27]),grid,
        float(x[0]),float(x[55]),anchor)

@dataclass(frozen=True)
class RescueEvidence:
    aligned_votes:int
    countertrend_micro:bool
    at_completed_grid:bool
    anchor_agrees:bool
    qualified:bool


def correct_opportunity_rescue(geom:CompletedGeometry, *, decision_ms:int,
                               side:int)->RescueEvidence:
    """Independent correct-preservation *proposal*; thresholds are not fitted.

    Caller must bind genuine R120 completed geometry and causal timestamps.
    This produces only evidence; it does not veto, keep, or override an order.
    """
    if side not in (-1,1):raise ValueError("invalid side")
    if geom.side!=side:raise ValueError("R120 state belongs to a different original side")
    if geom.published_at_ms>=decision_ms or geom.last_completed_bar_end_ms>geom.published_at_ms:
        raise ValueError("unpublished/future HTF state")
    vals=np.array([geom.m1_trend,geom.m5_trend,geom.m15_trend,geom.h1_trend,
                   geom.grid_proximity,geom.micro_slope_250ms,geom.micro_slope_30s,
                   geom.session_anchor_trend],dtype=float)
    if not np.isfinite(vals).all() or not(0<=geom.grid_proximity<=1):
        raise ValueError("invalid source-published geometry")
    votes=int(np.sum(vals[:4]>0))
    counter=bool(geom.micro_slope_250ms<0 and geom.micro_slope_30s>0)
    at_grid=bool(geom.grid_proximity<=.125)
    anchor=bool(geom.session_anchor_trend>0)
    return RescueEvidence(votes,counter,at_grid,anchor,
                          bool(votes>=3 and counter and at_grid and anchor))

@dataclass(frozen=True)
class HypotheticalExecution:
    action: str
    decision_ms:int
    submit_ms:int
    filled:bool
    fill_ms:int|None
    fill_price_raw:int|None
    exit_ms:int|None
    exit_reason:str
    exit_price_raw:int|None
    pnl_usd_per_ounce:float|None
    quotes_examined:int
    evidence_type:str="hypothetical L1 side-aware path, not broker execution"


def hypothetical_first_passage(quotes:QuotePrefix, *,decision_ms:int,side:int,
                              action:Literal["MARKET","LIMIT","ABSTAIN"],
                              still_unsubmitted:bool, latency_ms:int=0,
                              limit_price_raw:int|None=None,ttl_ms:int=2000,
                              horizon_ms:int=30000,target_raw:int=300,
                              stop_raw:int=450,commission_usd_per_ounce:float=0.)->HypotheticalExecution:
    """OFFLINE future-path label, never an inference-time feature.

    BUY fills at ask and exits at bid; SELL fills at bid and exits at ask.
    Quote-touch is optimistic L1 hypothetical execution, not guaranteed fill.
    No old t0+30 truth is used; horizon starts from the *new* fill clock.
    """
    if side not in (-1,1) or latency_ms<0 or ttl_ms<0 or horizon_ms<=0:
        raise ValueError("invalid intent physics")
    if target_raw<=0 or stop_raw<=0 or commission_usd_per_ounce<0:
        raise ValueError("invalid price/cost assumptions")
    if not still_unsubmitted:raise PermissionError("cannot retroactively alter a submitted/filled order")
    if action not in ("MARKET","LIMIT","ABSTAIN"):raise ValueError("unrecognized action")
    if action=="LIMIT" and (limit_price_raw is None or limit_price_raw<=0):
        raise ValueError("limit price required")
    d=int(decision_ms);sub=d+latency_ms
    if action=="ABSTAIN":return HypotheticalExecution(action,d,sub,False,None,None,None,"ABSTAIN",None,None,0)
    t,b,a=quotes.t,quotes.bid,quotes.ask
    i=int(np.searchsorted(t,sub,side="left"));n=0
    fill=None
    while i<len(t) and t[i]<=sub+ttl_ms:
        n+=1
        if action=="MARKET" or (side==1 and a[i]<=limit_price_raw) or (side==-1 and b[i]>=limit_price_raw):
            fill=i;break
        i+=1
    if fill is None:
        return HypotheticalExecution(action,d,sub,False,None,None,None,"NO_TOUCH",None,None,n)
    price=int(a[fill] if side==1 else b[fill]);entry=int(t[fill])
    for j in range(fill+1,len(t)):
        if t[j]>entry+horizon_ms:break
        n+=1
        exit_price=int(b[j] if side==1 else a[j])
        signed=side*(exit_price-price)
        if signed>=target_raw or signed<=-stop_raw:
            reason="TARGET" if signed>=target_raw else "STOP"
            pnl=signed/1000.-commission_usd_per_ounce
            return HypotheticalExecution(action,d,sub,True,entry,price,int(t[j]),reason,exit_price,pnl,n)
    return HypotheticalExecution(action,d,sub,True,entry,price,None,"CENSORED",None,None,n)
