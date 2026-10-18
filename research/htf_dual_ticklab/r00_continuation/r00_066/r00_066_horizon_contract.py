"""R00 diagnostic label contract. Isolated repair; does not alter prior archives.

This function is for *post-decision scoring and training labels only*, never
for an entry feature or event selector. Keep each broker's raw quote tape separate.
"""
from __future__ import annotations

from typing import NamedTuple
import numpy as np


class HorizonObservation(NamedTuple):
    known_future: np.ndarray
    markout: np.ndarray
    direction: np.ndarray
    future_index: np.ndarray


def observe_horizon(
    source_time_ms: np.ndarray,
    mid: np.ndarray,
    decision_time_ms: np.ndarray,
    decision_quote_index: np.ndarray,
    *,
    horizon_ms: int = 30_000,
    quote_tolerance_ms: int = 2_000,
    displacement_usd: float = 0.10,
) -> HorizonObservation:
    """First *observed* quote at/after t+horizon, but before t+horizon+tol.

    Misses and neutral displacement are zero-direction, rather than excluded.
    For a buy/sell score, correctness is side == direction and direction != 0.
    """
    t=np.asarray(source_time_ms,dtype=np.int64)
    price=np.asarray(mid,dtype=np.float64)
    et=np.asarray(decision_time_ms,dtype=np.int64)
    ix=np.asarray(decision_quote_index,dtype=np.int64)
    if horizon_ms<=0 or quote_tolerance_ms<=0 or displacement_usd<=0:
        raise ValueError('horizon, tolerance, displacement must be positive')
    if not len(t) or len(price)!=len(t) or np.any(np.diff(t)<0):
        raise ValueError('nonempty same-sized chronologically sorted source quotes required')
    if np.any(ix<0) or np.any(ix>=len(t)) or not np.array_equal(t[ix],et):
        raise ValueError('decisions must cite actual original quote indices and timestamps')
    target=et+horizon_ms
    future_ix=np.searchsorted(t,target,side='left')
    exists=future_ix<len(t)
    valid=exists.copy()
    valid[exists] &= t[future_ix[exists]] < target[exists]+quote_tolerance_ms
    markout=np.full(len(et),np.nan,dtype=np.float64)
    markout[valid]=price[future_ix[valid]]-price[ix[valid]]
    label=np.zeros(len(et),dtype=np.int8)
    label[valid & (markout>displacement_usd)]=1
    label[valid & (markout < -displacement_usd)]=-1
    return HorizonObservation(valid,markout,label,np.where(exists,future_ix,-1))
