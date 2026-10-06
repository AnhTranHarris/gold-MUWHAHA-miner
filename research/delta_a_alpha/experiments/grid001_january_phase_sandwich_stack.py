from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from numba import njit

from grid001_january_event_label_lab import load, materialize, DAY_MS, PRICE_SCALE
from grid001_january_early_thesis_failure import m1_atr_gap, gen_events
from grid001_january_vol_expansion_route import vol_ratio_events, candidate_trades

COMMISSION = 0.02


@njit(cache=True)
def proof_details(t, a, b, ei, ed, eg, horizon=300000):
    n = ei.size
    pi = np.full(n, -1, np.int64)
    xi = np.full(n, -1, np.int64)
    sideout = np.zeros(n, np.int8)
    pnl = np.zeros(n, np.float64)

    for k in range(n):
        i = int(ei[k])
        side = -1 if ed[k] < 0 else 1
        g = int(eg[k])
        end = t[i] + horizon
        e0 = a[i] if side > 0 else b[i]
        proof = max(1, int(round(0.25 * g)))
        fail = max(1, int(round(0.50 * g)))

        p = -1
        j = i + 1
        while j < t.size and t[j] <= end:
            px = b[j] if side > 0 else a[j]
            if side > 0:
                if px <= e0 - fail:
                    break
                if px >= e0 + proof:
                    p = j
                    break
            else:
                if px >= e0 + fail:
                    break
                if px <= e0 - proof:
                    p = j
                    break
            j += 1

        if p < 0:
            continue

        pi[k] = p
        sideout[k] = side
        entry = a[p] if side > 0 else b[p]
        tp = entry + g if side > 0 else entry - g
        sl = entry - g if side > 0 else entry + g
        ex = entry
        last = p
        q = p + 1

        while q < t.size and t[q] <= end:
            last = q
            if side > 0:
                if b[q] >= tp or b[q] <= sl:
                    ex = b[q]
                    break
            else:
                if a[q] <= tp or a[q] >= sl:
                    ex = a[q]
                    break
            q += 1
        else:
            ex = b[last] if side > 0 else a[last]

        xi[k] = last
        pnl[k] = ((ex - entry) if side > 0 else (entry - ex)) / PRICE_SCALE - COMMISSION

    return pi, xi, sideout, pnl


def state_age_series(t, mid, tf_ms):
    bucket = t // tf_ms
    starts = np.r_[0, np.flatnonzero(bucket[1:] != bucket[:-1]) + 1]
    ends = np.r_[starts[1:] - 1, len(t) - 1]
    bars = bucket[starts]
    closes = mid[ends].astype(float)

    ser = np.full(len(closes), np.nan)
    if len(closes) >= 7:
        d = np.abs(np.diff(closes))
        cs = np.r_[0.0, np.cumsum(d)]
        j = np.arange(6, len(closes))
        net = closes[j] - closes[j - 6]
        path = cs[j] - cs[j - 6]
        ser[j] = np.divide(net, path, out=np.zeros_like(net), where=path > 0)

    state = np.zeros(len(closes), np.int8)
    state[ser >= 0.50] = 1
    state[ser <= -0.50] = -1

    age = np.zeros(len(closes), np.int32)
    for i in range(len(closes)):
        if state[i] == 0:
            age[i] = 0
        elif i > 0 and state[i] == state[i - 1]:
            age[i] = age[i - 1] + 1
        else:
            age[i] = 1

    return bars, state, age


def map_state(t, query_idx, bars, state, age, tf_ms):
    qb = t[query_idx] // tf_ms
    bi = np.searchsorted(bars, qb, side="left") - 1
    s = np.zeros(len(query_idx), np.int8)
    ag = np.zeros(len(query_idx), np.int32)
    ok = bi >= 0
    s[ok] = state[bi[ok]]
    ag[ok] = age[bi[ok]]
    return s, ag


def owner_state(t, ei, ed, pi, b5, s5, a5, b15, s15, a15):
    opened = pi >= 0
    idx = np.where(opened, pi, ei)

    st5, ag5 = map_state(t, idx, b5, s5, a5, 300000)
    st15, ag15 = map_state(t, idx, b15, s15, a15, 900000)
    event_side = np.where(ed < 0, -1, 1).astype(np.int8)

    owner_tf = np.zeros(len(ei), np.int8)
    owner_dir = np.zeros(len(ei), np.int8)
    owner_age = np.zeros(len(ei), np.int32)
    relation = np.zeros(len(ei), np.int8)

    same = (st15 != 0) & (st5 == st15)
    own15 = (st15 != 0) & ((st5 == 0) | same)
    own5 = (st5 != 0) & (st15 == 0)
    conflict = (st5 != 0) & (st15 != 0) & (st5 != st15)

    owner_tf[own15] = 15
    owner_dir[own15] = st15[own15]
    owner_age[own15] = ag15[own15]

    owner_tf[own5] = 5
    owner_dir[own5] = st5[own5]
    owner_age[own5] = ag5[own5]

    relation[(owner_dir != 0) & (owner_dir == event_side)] = 1
    relation[(owner_dir != 0) & (owner_dir == -event_side)] = -1
    relation[conflict] = 2

    phase = np.zeros(len(ei), np.int8)
    phase[(owner_age >= 1) & (owner_age <= 2)] = 1
    phase[(owner_age >= 3) & (owner_age <= 6)] = 2
    phase[owner_age >= 7] = 3

    return owner_tf, relation, phase


@njit(cache=True)
def parent_reclaim_details(t, a, b, ei, ed, eg, pi, eligible, horizon=300000):
    n = ei.size
    ri = np.full(n, -1, np.int64)
    xi = np.full(n, -1, np.int64)
    sides = np.zeros(n, np.int8)
    pnl = np.zeros(n, np.float64)

    for k in range(n):
        if not eligible[k] or pi[k] < 0:
            continue

        i = int(ei[k])
        p = int(pi[k])
        child = -1 if ed[k] < 0 else 1
        parent = -child
        g = int(eg[k])
        end = t[i] + horizon
        ref_mid = 0.5 * (a[p] + b[p])
        need = max(1, int(round(0.25 * g)))

        q = p + 1
        r = -1
        while q < t.size and t[q] <= end:
            mid = 0.5 * (a[q] + b[q])
            if parent > 0:
                if mid >= ref_mid + need:
                    r = q
                    break
            else:
                if mid <= ref_mid - need:
                    r = q
                    break
            q += 1

        if r < 0:
            continue

        ri[k] = r
        sides[k] = parent
        entry = a[r] if parent > 0 else b[r]
        tp = entry + g if parent > 0 else entry - g
        sl = entry - g if parent > 0 else entry + g
        ex = entry
        last = r
        q = r + 1

        while q < t.size and t[q] <= end:
            last = q
            if parent > 0:
                if b[q] >= tp or b[q] <= sl:
                    ex = b[q]
                    break
            else:
                if a[q] <= tp or a[q] >= sl:
                    ex = a[q]
                    break
            q += 1
        else:
            ex = b[last] if parent > 0 else a[last]

        xi[k] = last
        pnl[k] = ((ex - entry) if parent > 0 else (entry - ex)) / PRICE_SCALE - COMMISSION

    return ri, xi, sides, pnl


def stats(x):
    x = np.asarray(x, float)
    gp = float(x[x > 0].sum())
    gl = float(x[x < 0].sum())
    return {
        "n": int(len(x)),
        "net": float(x.sum()),
        "gross_profit": gp,
        "gross_loss": gl,
        "pf": gp / abs(gl) if gl < 0 else None,
        "expected": float(x.mean()) if len(x) else None,
        "win_pct": 100 * float((x > 0).mean()) if len(x) else None,
    }


def add_candidates(store, route, priority, event_idx, entry_idx, exit_idx, side, pnl, mask):
    ids = np.flatnonzero(mask & (entry_idx >= 0) & (exit_idx >= 0))
    for k in ids:
        store.append(
            (
                int(entry_idx[k]),
                int(priority),
                int(exit_idx[k]),
                int(event_idx[k]),
                int(side[k]),
                float(pnl[k]),
                route,
            )
        )


def equity_metrics(t, a, b, candidates, start=100000.0):
    balance = start
    peak_balance = start
    peak_equity = start
    min_equity = start
    max_balance_dd = 0.0
    max_equity_dd = 0.0

    for entry_idx, _, exit_idx, _, side, pnl, _ in candidates:
        entry = a[entry_idx] if side > 0 else b[entry_idx]
        balance_entry = balance - 0.01

        peak_balance = max(peak_balance, balance_entry)
        max_balance_dd = max(max_balance_dd, peak_balance - balance_entry)

        q = entry_idx
        while q <= exit_idx:
            floating = ((b[q] - entry) if side > 0 else (entry - a[q])) / PRICE_SCALE
            equity = balance_entry + floating
            peak_equity = max(peak_equity, equity)
            max_equity_dd = max(max_equity_dd, peak_equity - equity)
            min_equity = min(min_equity, equity)
            q += 1

        balance += pnl
        peak_balance = max(peak_balance, balance)
        max_balance_dd = max(max_balance_dd, peak_balance - balance)
        peak_equity = max(peak_equity, balance)
        max_equity_dd = max(max_equity_dd, peak_equity - balance)
        min_equity = min(min_equity, balance)

    return balance - start, max_balance_dd, max_equity_dd, min_equity - start


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    t, source_ask, source_bid = load(args.source)
    a, b, max_error2 = materialize(t, source_ask, source_bid)
    mid = (a.astype(np.int64) + b.astype(np.int64)) / 2.0

    b5, s5, age5 = state_age_series(t, mid, 300000)
    b15, s15, age15 = state_age_series(t, mid, 900000)

    store = []
    component_pre = {}

    # R0 — A05 volatility-expansion route, frozen threshold 2.0.
    g05 = m1_atr_gap(t, b, 0.5)
    ei05, ed05, eg05 = gen_events(t, a, b, g05)
    vr = vol_ratio_events(t, b, ei05)
    ce, cn, cx, cs, cp, _, _, _ = candidate_trades(
        t, a, b, ei05, ed05, eg05, vr, 2.0
    )
    component_pre["R0_VOL_EXP_2.0"] = len(cp)
    for j in range(len(cp)):
        store.append(
            (
                int(cn[j]),
                0,
                int(cx[j]),
                int(ce[j]),
                int(cs[j]),
                float(cp[j]),
                "R0_VOL_EXP_2.0",
            )
        )

    for mult, name in ((0.5, "A05"), (1.0, "A10"), (1.5, "A15")):
        gaps = m1_atr_gap(t, b, mult)
        ei, ed, eg = gen_events(t, a, b, gaps)
        pi, xi, side, pnl = proof_details(t, a, b, ei, ed, eg)
        owner_tf, relation, phase = owner_state(
            t, ei, ed, pi, b5, s5, age5, b15, s15, age15
        )
        opened = pi >= 0

        if name == "A05":
            m = opened & (owner_tf == 15) & (relation == -1) & (phase == 3)
            component_pre["R1_A05_15m_OPP_EXT_CHILD"] = int(m.sum())
            add_candidates(
                store, "R1_A05_15m_OPP_EXT_CHILD", 4,
                ei, pi, xi, side, pnl, m
            )

        elif name == "A10":
            m = opened & (owner_tf == 15) & (relation == 1) & (phase == 3)
            component_pre["R2_A10_15m_ALIGN_EXT_CHILD"] = int(m.sum())
            add_candidates(
                store, "R2_A10_15m_ALIGN_EXT_CHILD", 3,
                ei, pi, xi, side, pnl, m
            )

            mr = opened & (owner_tf == 5) & (relation == -1) & (phase == 2)
            ri, rxi, rs, rp = parent_reclaim_details(t, a, b, ei, ed, eg, pi, mr)
            component_pre["R3_A10_5m_OPP_MAT_RECLAIM"] = int(np.sum(ri >= 0))
            add_candidates(
                store, "R3_A10_5m_OPP_MAT_RECLAIM", 3,
                ei, ri, rxi, rs, rp, ri >= 0
            )

        else:
            m = opened & (owner_tf == 15) & (relation == 1) & (phase == 3)
            component_pre["R4_A15_15m_ALIGN_EXT_CHILD"] = int(m.sum())
            add_candidates(
                store, "R4_A15_15m_ALIGN_EXT_CHILD", 2,
                ei, pi, xi, side, pnl, m
            )

            mr = opened & (owner_tf == 15) & (relation == -1) & (phase == 2)
            ri, rxi, rs, rp = parent_reclaim_details(t, a, b, ei, ed, eg, pi, mr)
            component_pre["R5_A15_15m_OPP_MAT_RECLAIM"] = int(np.sum(ri >= 0))
            add_candidates(
                store, "R5_A15_15m_OPP_MAT_RECLAIM", 2,
                ei, ri, rxi, rs, rp, ri >= 0
            )

    # Single grid-system owner. Priority breaks exact-entry-time ties.
    store.sort(key=lambda x: (x[0], x[1]))
    accepted = []
    current_exit = -1
    suppressed = 0

    for candidate in store:
        if candidate[0] <= current_exit:
            suppressed += 1
            continue
        accepted.append(candidate)
        current_exit = candidate[2]

    pnls = np.array([c[5] for c in accepted], float)
    events = np.array([c[3] for c in accepted], np.int64)
    split = 2 * len(t) // 3
    discovery = events < split
    validation = ~discovery

    active_days = (
        len(np.unique(t[[c[0] for c in accepted]] // DAY_MS))
        if accepted else 0
    )

    _, balance_dd, equity_dd, min_delta = equity_metrics(t, a, b, accepted)

    routes = {}
    for route in sorted(component_pre):
        pre = [c for c in store if c[6] == route]
        acc = [c for c in accepted if c[6] == route]
        routes[route] = {
            "pre_owner_candidates": len(pre),
            "accepted": len(acc),
            "suppressed": len(pre) - len(acc),
            "accepted_net": float(sum(c[5] for c in acc)),
        }

    out = {
        "schema": "delta-a-alpha-grid001-january-phase-sandwich-stack-v1",
        "unit": "DAA_GRID_001_JANUARY_PHASE_SANDWICH_STACK_001",
        "status": "COMPLETE",
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "ticks": int(len(t)),
        "candidate_count_pre_owner": len(store),
        "suppressed_by_single_owner": suppressed,
        "routes": routes,
        "combined": {
            "trades": len(accepted),
            "trades_per_active_day": float(len(accepted) / active_days) if active_days else 0.0,
            "full": stats(pnls),
            "discovery": stats(pnls[discovery]),
            "validation": stats(pnls[validation]),
            "max_balance_drawdown": float(balance_dd),
            "max_equity_drawdown": float(equity_dd),
            "min_equity_delta": float(min_delta),
            "small_account": {
                str(x): {
                    "min_equity": float(x + min_delta),
                    "positive_equity": bool(x + min_delta > 0),
                }
                for x in (100, 200, 300)
            },
            "r9_real_jan_net_loss_recovery_pct": float(pnls.sum() / 6651.62 * 100),
            "r9_real_jan_remaining_net_additive_proxy": float(-6651.62 + pnls.sum()),
            "half_net_loss_target_progress_pct": float(pnls.sum() / 3325.81 * 100),
        },
        "max_midpoint_quantization_error_price": float(max_error2 / (2 * PRICE_SCALE)),
    }

    args.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
