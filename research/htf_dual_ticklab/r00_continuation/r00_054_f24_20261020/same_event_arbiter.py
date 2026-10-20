"""R00-054 F24: research-only same-event BUY/SELL arbiter; labels NEVER enter inference."""
import numpy as np

def correct(event_ids, quote_indices, timestamps_ms, base_side, p_up, p_down, frozen_edge=0.):
    ids=np.asarray(event_ids); q=np.asarray(quote_indices); t=np.asarray(timestamps_ms)
    b=np.asarray(base_side); u=np.asarray(p_up); d=np.asarray(p_down)
    if not all(len(v)==len(b) for v in (ids,q,t,u,d)): raise ValueError("event count changed")
    if np.any(~np.isin(b,[-1,1])) or np.any(q<0) or np.any(np.diff(t)<0): raise ValueError("invalid source event")
    if frozen_edge<0 or not np.isfinite(frozen_edge) or np.any(~np.isfinite(u+d)) or np.any(u<0) or np.any(d<0) or np.any(u+d>1+1e-8): raise ValueError("invalid posterior")
    flip=b*(d-u)>frozen_edge
    return dict(event_id=ids.copy(),quote_index=q.copy(),time_ms=t.copy(),side=np.where(flip,-b,b),flip=flip)

def paired_score(baseline, proposed, realized_direction):
    b=np.asarray(baseline); p=np.asarray(proposed); y=np.asarray(realized_direction)
    if len(b)!=len(p) or len(b)!=len(y) or np.any(~np.isin(b,[-1,1])) or np.any(~np.isin(p,[-1,1])) or np.any(~np.isin(y,[-1,0,1])): raise ValueError("invalid paired study")
    switched=b!=p
    rescued=int(np.sum(switched & (p==y)))
    damaged=int(np.sum(switched & (b==y)))
    neutral=int(np.sum(switched & (y==0)))
    assert rescued+damaged+neutral==int(np.sum(switched))
    return dict(events=len(b),emitted=len(b),rescued=rescued,damaged=damaged,neutral_flips=neutral,net=rescued-damaged,baseline_correct=int(np.sum(b==y)),candidate_correct=int(np.sum(p==y)))
