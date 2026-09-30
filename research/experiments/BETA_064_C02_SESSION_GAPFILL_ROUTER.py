"""
BETA064 Checkpoint-02 Session Gap-Fill Router
Research-only Python harness/specification.

Purpose:
- preserve all Major Checkpoint-01 Entry->Hold trades unchanged;
- add session-conditioned opportunities only while the baseline is idle;
- require month-level Entry->Hold survivability >= 0.87 in research optimization;
- Hold+Exit remains out of scope;
- August remains sealed.

Required precomputed causal meta table:
    /mnt/data/beta064_session_meta_all.pkl

That table is built from Jan-Jul Dukascopy XAUUSD tick chronology and contains
the frozen E1-E12 specialist candidates plus causal model outputs and offline
first-passage labels.
"""

import pandas as pd
import numpy as np
from numba import njit

DATA_PATH = "/mnt/data/beta064_session_meta_all.pkl"

SESSIONS = ["AUSTRALIA", "ASIA", "MIDEAST", "EUROPE", "UK", "NY"]
SESSION_DEFINITIONS = {
    "AUSTRALIA": ("Australia/Sydney", 8, 17),
    "ASIA": ("Asia/Tokyo", 9, 18),
    "MIDEAST": ("Asia/Dubai", 8, 17),
    "EUROPE": ("Europe/Berlin", 8, 17),
    "UK": ("Europe/London", 8, 17),
    "NY": ("America/New_York", 8, 17),
}

# Final conservative session authorities after month-by-month refinement.
SESSION_SURVIVAL_THRESHOLDS = {
    "AUSTRALIA": 0.920,
    "ASIA": 0.900,
    "MIDEAST": 0.915,
    "EUROPE": 0.910,
    "UK": 0.925,
    "NY": 0.925,
}

# Checkpoint-01 remains authoritative control.
BASE_P_SURVIVE = 0.88
BASE_ENTRY_SCORE = 0.30

# Session gap-fill candidates must still be high-quality before the
# session-specific authority is applied.
SESSION_PRECHECK_P_SURVIVE = 0.89
SESSION_PRECHECK_ECONOMIC_SCORE = 0.08

# These are the specialists with enough session-conditioned empirical support
# to participate in Checkpoint-02 gap filling.
SESSION_ELIGIBLE_SPECIALISTS = {
    "E5_VWAP_RECLAIM",
    "E6_VALUE_REVERSION",
    "E7_SWEEP_RECLAIM",
    "E9_LEVEL_BREAK",
    "E10_COMPRESSION_RELEASE",
    "E11_KINETIC_IGNITION",
    "E12_FAILED_EXPANSION",
}

RESEARCH_MONTH_SURVIVABILITY_FLOOR = 0.87


@njit
def replay_additions(t_ms, horizon_s, survive, fp_win, pnl, session_code,
                     p_session_survive, thresholds):
    """Chronological one-position replay for session additions only."""
    busy_until = -10**18
    n = 0
    surv = 0.0
    fp = 0.0
    net = 0.0

    for i in range(len(t_ms)):
        sc = session_code[i]
        if sc < 0:
            continue
        if p_session_survive[i] < thresholds[sc]:
            continue
        if t_ms[i] < busy_until:
            continue

        n += 1
        surv += survive[i]
        fp += fp_win[i]
        net += pnl[i]
        busy_until = t_ms[i] + horizon_s[i] * 1000

    return n, surv, fp, net


def frozen_base_schedule(g):
    """Reproduce frozen Major Checkpoint-01 one-position ownership."""
    z = g[(g.p_surv >= BASE_P_SURVIVE) &
          (g.entry_score >= BASE_ENTRY_SCORE)].copy()
    z = z.sort_values(["time", "entry_score"], ascending=[True, False])

    chosen = []
    busy_until = pd.Timestamp("1900-01-01", tz="UTC")
    for r in z.itertuples():
        if r.time < busy_until:
            continue
        chosen.append(r.Index)
        busy_until = r.time + pd.Timedelta(seconds=int(r.horizon))

    return z.loc[chosen].sort_values("time")


def build_checkpoint02():
    d = pd.read_pickle(DATA_PATH).copy()
    session_code = {s: i for i, s in enumerate(SESSIONS)}
    thresholds = np.array(
        [SESSION_SURVIVAL_THRESHOLDS[s] for s in SESSIONS], dtype=float
    )

    d["is_base"] = (
        (d.p_surv >= BASE_P_SURVIVE) &
        (d.entry_score >= BASE_ENTRY_SCORE)
    ).astype(np.int8)

    d["session_code"] = (
        d.session_authority.map(session_code).fillna(-1).astype(np.int8)
    )
    d["session_specialist_allowed"] = (
        d.specialist.isin(SESSION_ELIGIBLE_SPECIALISTS).astype(np.int8)
    )

    monthly = []
    selected = []

    for month, g in d.groupby("month"):
        base = frozen_base_schedule(g).copy()
        base["source"] = "CHECKPOINT01"
        selected.append(base)

        base_start = base.time.astype("int64").to_numpy() // 1_000_000
        base_end = (
            base_start + base.horizon.to_numpy(np.int64) * 1000
        )

        add = g[
            (g.is_base == 0) &
            (g.session_specialist_allowed == 1) &
            (g.ps_b75 >= SESSION_PRECHECK_P_SURVIVE) &
            (g.es_b75 >= SESSION_PRECHECK_ECONOMIC_SCORE)
        ].copy()

        add_start = add.time.astype("int64").to_numpy() // 1_000_000
        add_end = add_start + add.horizon.to_numpy(np.int64) * 1000

        # Gap-fill rule: an added trade must fit entirely outside every
        # already-reserved frozen Checkpoint-01 interval.
        if len(base_start):
            prev = np.searchsorted(base_start, add_start, side="right") - 1
            prev_overlap = (
                (prev >= 0) &
                (add_start < base_end[np.maximum(prev, 0)])
            )

            nxt = np.searchsorted(base_start, add_start, side="left")
            next_overlap = (
                (nxt < len(base_start)) &
                (add_end > base_start[np.minimum(nxt, len(base_start)-1)])
            )
        else:
            prev_overlap = np.zeros(len(add), dtype=bool)
            next_overlap = np.zeros(len(add), dtype=bool)

        add = add.loc[~(prev_overlap | next_overlap)]
        add = add.sort_values(["time", "es_b75"], ascending=[True, False])

        t_ms = add.time.astype("int64").to_numpy() // 1_000_000
        h = add.horizon.to_numpy(np.int64)
        survive = add.survive.to_numpy(float)
        fp = add.fp_win.to_numpy(float)
        pnl = add.resolved_pnl.to_numpy(float)
        sc = add.session_code.to_numpy(np.int8)
        ps = add.ps_b75.to_numpy(float)

        busy_until = -10**18
        chosen = []

        for i in range(len(add)):
            if sc[i] < 0:
                continue
            if ps[i] < thresholds[sc[i]]:
                continue
            if t_ms[i] < busy_until:
                continue

            chosen.append(add.index[i])
            busy_until = t_ms[i] + h[i] * 1000

        session_add = d.loc[chosen].copy()
        session_add["source"] = "SESSION_GAPFILL"
        selected.append(session_add)

        combined = pd.concat([base, session_add]).sort_values("time")
        monthly.append({
            "month": int(month),
            "trades": len(combined),
            "survival": float(combined.survive.mean()),
            "first_passage_success": float(combined.fp_win.mean()),
            "diagnostic_value": float(combined.resolved_pnl.sum()),
            "session_adds": len(session_add),
        })

    selected = pd.concat(selected).sort_values("time")
    monthly = pd.DataFrame(monthly)

    assert (monthly.survival >= 0.85).all()
    return selected, monthly


if __name__ == "__main__":
    selected, monthly = build_checkpoint02()
    print(monthly.to_string(index=False))
    print("weighted survivability:",
          np.average(monthly.survival, weights=monthly.trades))
