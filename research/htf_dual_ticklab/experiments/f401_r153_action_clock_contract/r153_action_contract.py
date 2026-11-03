"""R153: source-clock eligibility guard for hypothetical T1/T2/limit action proposals.

Research only. Does not mutate R00-054 original orders, original event identities,
or claim execution. Runtime inputs contain no original truth or hindsight labels.
"""
from __future__ import annotations
import numpy as np

ACTION_ABSTAIN, ACTION_T1, ACTION_T2, ACTION_LIMIT = range(4)

def guard_hypothetical_actions(actions, t0, t1, t2, t1_valid, t2_valid,
                               limit_eligible, already_submitted=None):
    """Guard T1=[t0+15s,t0+16s), T2=[t1+5s,t1+6s), and passive T1 intent.

    This is a *new unsubmitted action* proposal, never a cancellation of a
    filled original t0 order. The submitted flag is accepted for source
    integration only; it never authorizes modifying existing orders.
    """
    a = np.asarray(actions, dtype=np.int8)
    t0, t1, t2 = [np.asarray(v, dtype=np.int64) for v in (t0, t1, t2)]
    v1, v2, vl = [np.asarray(v, dtype=bool) for v in (t1_valid, t2_valid, limit_eligible)]
    n = len(a)
    if any(len(v) != n for v in (t0,t1,t2,v1,v2,vl)):
        raise ValueError('length mismatch')
    if not np.isin(a, [0,1,2,3]).all():
        raise ValueError('unknown action')
    if already_submitted is not None and len(already_submitted) != n:
        raise ValueError('submitted flag length mismatch')
    t1_ok = v1 & (t1 >= t0 + 15000) & (t1 < t0 + 16000)
    t2_ok = t1_ok & v2 & (t2 >= t1 + 5000) & (t2 < t1 + 6000)
    permitted = ((a==0) | ((a==1)&t1_ok) | ((a==2)&t2_ok) | ((a==3)&t1_ok&vl))
    out = a.copy()
    out[~permitted] = 0
    reasons = np.zeros(n, dtype=np.int8)
    reasons[~permitted] = 1
    return out, reasons

def audit_original_signal_protection(original_order_ids, proposed_actions):
    """Shadow-only contract: never emits commands to modify original orders."""
    ids = np.asarray(original_order_ids)
    actions = np.asarray(proposed_actions)
    if len(ids) != len(actions):
        raise ValueError('length mismatch')
    if not np.isin(actions,[0,1,2,3]).all():
        raise ValueError('invalid action')
    return {'original_orders_modified': 0,
            'shadow_proposals': int(np.count_nonzero(actions)),
            'original_order_count': int(len(ids))}
