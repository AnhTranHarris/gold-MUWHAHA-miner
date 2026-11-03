"""R11 forensic research-only H1V2/v5 eligibility shadow comparison.

Not a replacement for the original H1V2 teacher. The H1V2 branch uses
>=300000 ms gap reset; repaired v5 scientific contract reports >15000 ms
epoch resets followed by 300000 ms of observed fresh history.
This reproduces only those public gate components: it is NOT full v5
online/offline feature or trade-policy parity. No future quote is consulted.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class AdmissionContract:
    spread_max: float = 1.50
    warmup_ms: int = 300_000
    gap_reset_ms: int = 300_000
    gap_reset_inclusive: bool = True
    slot_ms: int = 250

H1V2_ORIGINAL = AdmissionContract()
V5_SHADOW = AdmissionContract(gap_reset_ms=15_000, gap_reset_inclusive=False)

def candidate_mask(t, bid, ask, contract: AdmissionContract):
    """Causal, prefix-invariant first-observed occupied-slot admission mask.

    Same-ms source ordinal is preserved; only the first source ordinal of
    each occupied time slot can be a candidate, matching the original H1V2.
    """
    t=np.asarray(t,dtype=np.int64)
    b=np.asarray(bid,dtype=np.float64)
    a=np.asarray(ask,dtype=np.float64)
    if not (t.ndim==b.ndim==a.ndim==1 and len(t)==len(b)==len(a)):
        raise ValueError("quote vector shapes differ")
    if len(t)==0:
        return np.empty(0,dtype=np.bool_)
    if np.any(t[1:]<t[:-1]) or not (np.isfinite(b).all() and np.isfinite(a).all()):
        raise ValueError("invalid chronology or nonfinite prices")
    if np.any(a<b):
        raise ValueError("inverted quote input")
    if contract.slot_ms<=0 or contract.warmup_ms<0 or contract.gap_reset_ms<=0:
        raise ValueError("invalid admission contract")
    accepted=np.zeros(len(t),dtype=np.bool_)
    epoch=int(t[0])
    prev=int(t[0])
    prev_slot=-1
    for i in range(len(t)):
        now=int(t[i])
        if i:
            dt=now-prev
            reset=dt>=contract.gap_reset_ms if contract.gap_reset_inclusive else dt>contract.gap_reset_ms
            if reset:
                epoch=now
        slot=now//contract.slot_ms
        first_in_slot=(i==0 or slot!=prev_slot)
        good_spread=(a[i]-b[i]<=contract.spread_max)
        accepted[i]=first_in_slot and good_spread and (now-epoch>=contract.warmup_ms)
        prev=now
        prev_slot=slot
    return accepted

def compare_source(t,bid,ask,original=H1V2_ORIGINAL,shadow=V5_SHADOW):
    h=candidate_mask(t,bid,ask,original)
    v=candidate_mask(t,bid,ask,shadow)
    return dict(
        h1v2_count=int(h.sum()),v5_shadow_count=int(v.sum()),
        intersection=int(np.count_nonzero(h&v)),
        original_only=int(np.count_nonzero(h&~v)),
        shadow_only=int(np.count_nonzero(v&~h)),
        h1v2_indices=np.flatnonzero(h),v5_shadow_indices=np.flatnonzero(v),
        both_indices=np.flatnonzero(h&v),
        contract_note="V5_SHADOW only mirrors documented gap/spread/warmup, not production full eligibility",
    )

def original_candidate_parity(t,bid,ask,original_candidate_fn):
    """External original H1V2 exact function must match before comparisons publish."""
    got=np.flatnonzero(candidate_mask(t,bid,ask,H1V2_ORIGINAL))
    want=np.asarray(original_candidate_fn(t,bid,ask),dtype=np.int64)
    if not np.array_equal(got,want):
        raise AssertionError("original H1V2 candidate source parity failure")
    return int(len(got))
