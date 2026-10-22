"""F294: research-only causal quote-revision changepoint adapter (F01/F02).

Uses only established F273 source-native as-of quote/event features. Does not
use F293 fitted risk, labels, future bars or unapproved data. Not validated
on broker source events and not approved for trading.

Timestamp collision contract: events with equal UTC millisecond timestamps
receive one identical quote-state snapshot (no artificial within-ms ordering).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Sequence
import numpy as np

REQUIRED = (
    "sr1","sr3","sr5","sr10","sr30","sr60","sr300","sr900","sr3600",
    "r1","r3","r5","r10","r30","r60","r300","r900","r3600",
    "quote_direction_1","quote_direction_3","quote_direction_10",
    "quote_direction_30","spread","sprd_1","sprd_10",
    "side_sign_imb_1","side_sign_imb_10",
    "log_quote_rate_1s","log_quote_rate_10s",
    "m5_phase","m15_phase","h1_phase",
)
OUTPUTS = (
    "f294_side_curve_1_10","f294_side_curve_3_30",
    "f294_side_curve_10_300","f294_side_curvature",
    "f294_raw_curve_1_10","f294_quote_revision_shock",
    "f294_quote_response_disagreement","f294_spread_shock",
    "f294_quote_activity_shock","f294_side_return_imbalance",
    "f294_htf_coherence","f294_positive_cusum",
    "f294_negative_cusum","f294_quote_positive_cusum",
    "f294_quote_negative_cusum","f294_revision_running_scale",
    "f294_previous_event_gap_s","f294_updown_imbalance",
    "f294_shock_times_htf","f294_contradiction_times_cusum",
)

def _finite(x: float) -> float:
    return float(np.clip(np.nan_to_num(float(x), nan=0., posinf=0., neginf=0.), -1.e6, 1.e6))

@dataclass
class OnlineQuoteState:
    previous_ms: int | None = None
    side_mean: float = 0.
    quote_mean: float = 0.
    side_scale: float = .1
    quote_scale: float = .1
    pos_cusum: float = 0.
    neg_cusum: float = 0.
    pos_quote: float = 0.
    neg_quote: float = 0.

    def consume(self, timestamp_ms: int, side_impact: float, quote_impact: float) -> float:
        if self.previous_ms is not None and timestamp_ms < self.previous_ms:
            raise ValueError("Time regression: expected ascending UTC timestamps")
        gap_s = 0. if self.previous_ms is None else (timestamp_ms-self.previous_ms)/1000.
        if gap_s >= 900.:
            self.side_mean = self.quote_mean = 0.
            self.side_scale = self.quote_scale = .1
            self.pos_cusum = self.neg_cusum = self.pos_quote = self.neg_quote = 0.
        decay=float(np.exp(-gap_s/120.))
        side_impact=_finite(side_impact); quote_impact=_finite(quote_impact)
        ds=np.clip((side_impact-self.side_mean)/max(.1,self.side_scale),-20.,20.)
        dq=np.clip((quote_impact-self.quote_mean)/max(.1,self.quote_scale),-20.,20.)
        self.pos_cusum=float(np.clip(max(0.,decay*self.pos_cusum+ds-1.25),0.,250.))
        self.neg_cusum=float(np.clip(max(0.,decay*self.neg_cusum-ds-1.25),0.,250.))
        self.pos_quote=float(np.clip(max(0.,decay*self.pos_quote+dq-1.25),0.,250.))
        self.neg_quote=float(np.clip(max(0.,decay*self.neg_quote-dq-1.25),0.,250.))
        alpha=float(np.clip(1-np.exp(-max(gap_s,.25)/90.),.002,.10))
        old_side=self.side_mean;old_quote=self.quote_mean
        self.side_mean+=alpha*(side_impact-self.side_mean)
        self.quote_mean+=alpha*(quote_impact-self.quote_mean)
        self.side_scale=max(.1,(1-alpha)*self.side_scale+alpha*abs(side_impact-old_side))
        self.quote_scale=max(.1,(1-alpha)*self.quote_scale+alpha*abs(quote_impact-old_quote))
        self.previous_ms=int(timestamp_ms)
        return gap_s

def _feature(d: Mapping[str,float],state:OnlineQuoteState,t:int)->np.ndarray:
    v=lambda name:_finite(d[name])
    c1=v("sr1")-.1*v("sr10")
    c3=v("sr3")-.1*v("sr30")
    c10=v("sr10")-(1./30.)*v("sr300")
    raw=v("r1")-.1*v("r10")
    quote=v("quote_direction_1")-v("quote_direction_10")
    contradiction=quote-v("side_sign_imb_1")
    spread=v("sprd_1")-v("sprd_10")
    activity=v("log_quote_rate_1s")-v("log_quote_rate_10s")
    discrepancy=c1-v("side_sign_imb_1")
    htf=float(np.clip((v("m5_phase")+v("m15_phase")+v("h1_phase"))/3.,-100.,100.))
    gap=state.consume(t,c1,quote)
    return np.array((
        c1,c3,c10,c1-c3,raw,quote,contradiction,spread,activity,
        discrepancy,htf,state.pos_cusum,state.neg_cusum,state.pos_quote,
        state.neg_quote,state.side_scale,gap,
        (state.pos_cusum-state.neg_cusum)/(1+state.pos_cusum+state.neg_cusum),
        c1*htf,contradiction*(state.neg_cusum-state.pos_cusum),
    ),dtype=np.float32)

def build_changepoint_features(timestamps_ms:np.ndarray,
        source_features:Mapping[str,np.ndarray])->np.ndarray:
    t=np.asarray(timestamps_ms,dtype=np.int64);n=len(t)
    if np.any(np.diff(t)<0):raise ValueError("Non-monotonic UTC")
    for name in REQUIRED:
        if name not in source_features or len(source_features[name])!=n:
            raise ValueError("Missing/misaligned source feature "+name)
    out=np.empty((n,len(OUTPUTS)),dtype=np.float32)
    state=OnlineQuoteState(); i=0
    while i<n:
        j=int(np.searchsorted(t,t[i],side="right"))
        snapshot={name:source_features[name][i] for name in REQUIRED}
        val=_feature(snapshot,state,int(t[i]))
        out[i:j,:]=val;i=j
    return out

def build_from_f273_npz(npz_path:str,feature_list:Sequence[str])->np.ndarray:
    with np.load(npz_path) as arr:
        X=arr["X"];t=arr["t"]
        lookup={name:X[:,i] for i,name in enumerate(feature_list) if name in REQUIRED}
        return build_changepoint_features(t,lookup)

if __name__=="__main__":
    # SYNTHETIC SOFTWARE TEST, NOT HISTORICAL PREDICTIVE VALIDATION.
    n=8;t=np.array([1000,2000,2000,4000,5000,10000,10000,15000],dtype=np.int64)
    f={s:np.zeros(n,dtype=np.float32) for s in REQUIRED}
    f["sr1"][:]=[0,1,1,2,4,5,5,2]
    f["r1"][:]=f["sr1"]
    f["quote_direction_1"][:]=[0,2,2,-1,-3,-5,-5,0]
    f["m15_phase"][:]=[0,1,1,1,0,-1,-1,0]
    a=build_changepoint_features(t,f)
    assert a.shape==(n,len(OUTPUTS)) and np.isfinite(a).all()
    assert np.array_equal(a[1],a[2]) and np.array_equal(a[5],a[6])
    changed={k:v.copy() for k,v in f.items()}
    changed["sr1"][-1]=100;changed["quote_direction_1"][-1]=-100
    b=build_changepoint_features(t,changed)
    assert np.array_equal(a[:-1],b[:-1]) and not np.array_equal(a[-1],b[-1])
    print("F294 SYNTHETIC SMOKE PASS: 20 features, timestamp-grouping, future perturbation invariant")
