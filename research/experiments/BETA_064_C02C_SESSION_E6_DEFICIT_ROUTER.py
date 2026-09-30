"""
BETA064 Checkpoint-02C research child.
Consumes frozen BETA064 candidate ledger plus the C02C E6 causal-feature ledger.
Does NOT modify Major Checkpoint 02 and does NOT define Hold->Exit.
"""

import numpy as np
import pandas as pd

META = "/mnt/data/beta064_session_meta_all.pkl"
E6_FEATURES = "/mnt/data/beta064_ckpt02c_e6_scored.pkl"

BASE_PS = 0.88
BASE_ES = 0.30
PRE_PS = 0.89
PRE_ES = 0.08
DEFICIT_PS = 0.9145

FROZEN_SESSION_PS = {
    "AUSTRALIA": 0.920,
    "ASIA": 0.900,
    "MIDEAST": 0.915,
    "EUROPE": 0.910,
    "UK": 0.925,
    "NY": 0.925,
}

ALLOWED = {
    "E5_VWAP_RECLAIM",
    "E6_VALUE_REVERSION",
    "E7_SWEEP_RECLAIM",
    "E9_LEVEL_BREAK",
    "E10_COMPRESSION_RELEASE",
    "E11_KINETIC_IGNITION",
    "E12_FAILED_EXPANSION",
}


def frozen_base_schedule(g):
    z = g[(g.p_surv >= BASE_PS) & (g.entry_score >= BASE_ES)].copy()
    z = z.sort_values(["time", "entry_score"], ascending=[True, False])
    chosen = []
    busy = pd.Timestamp("1900-01-01", tz="UTC")
    for r in z.itertuples():
        if r.time < busy:
            continue
        chosen.append(r.Index)
        busy = r.time + pd.Timedelta(seconds=int(r.horizon))
    return z.loc[chosen].sort_values("time")


def outside_reserved(candidates, reserved):
    if len(reserved) == 0:
        return np.ones(len(candidates), dtype=bool)
    rs = reserved.time.astype("int64").to_numpy() // 1_000_000
    re = rs + reserved.horizon.to_numpy(np.int64) * 1000
    cs = candidates.time.astype("int64").to_numpy() // 1_000_000
    ce = cs + candidates.horizon.to_numpy(np.int64) * 1000

    p = np.searchsorted(rs, cs, side="right") - 1
    prev_overlap = (p >= 0) & (cs < re[np.maximum(p, 0)])
    n = np.searchsorted(rs, cs, side="left")
    next_overlap = (n < len(rs)) & (
        ce > rs[np.minimum(n, len(rs) - 1)]
    )
    return ~(prev_overlap | next_overlap)


def earliest_finish_schedule(z):
    z = z.copy()
    z["end"] = z.time + pd.to_timedelta(z.horizon, unit="s")
    z = z.sort_values(
        ["end", "ps_b75", "es_b75"],
        ascending=[True, False, False],
    )
    chosen = []
    busy = pd.Timestamp("1900-01-01", tz="UTC")
    for r in z.itertuples():
        if r.time < busy:
            continue
        chosen.append(r.Index)
        busy = r.end
    return z.loc[chosen].drop(columns="end").sort_values("time")


def e6_child_ok(r, e):
    session = r.session_authority

    # New York: efficient short-horizon turn, low friction,
    # not excessively far from evolving session value.
    if session == "NY":
        return (
            r.ps_b75 >= 0.920
            and float(e.eff60) >= 0.30
            and float(e.friction) <= 0.14
            and float(e.session_value_z) >= -2.5
        )

    # UK: strong immediate turn but weak five-minute directional ownership.
    if session == "UK":
        return (
            r.ps_b75 >= 0.905
            and float(e.eff60) >= 0.40
            and float(e.eff300) <= 0.10
            and float(e.session_value_z) >= -4.0
        )

    # Other E6 sessions stay on the frozen parent authority.
    return r.ps_b75 >= FROZEN_SESSION_PS.get(session, 9.0)


def candidate_ok(r, e6_lookup):
    if r.ps_b75 < PRE_PS or r.es_b75 < PRE_ES:
        return False

    if r.specialist == "E6_VALUE_REVERSION":
        try:
            e = e6_lookup.loc[(r.time, r.side)]
        except KeyError:
            return False
        return e6_child_ok(r, e)

    # Do not expand E11 because it is already condition-cell saturated.
    if r.specialist == "E11_KINETIC_IGNITION":
        return r.ps_b75 >= FROZEN_SESSION_PS.get(
            r.session_authority, 9.0
        )

    # Under-covered non-E6 desks share the C02C authority.
    return r.ps_b75 >= DEFICIT_PS


def run():
    d = pd.read_pickle(META).copy()
    e6 = pd.read_pickle(E6_FEATURES).set_index(["time", "side"])
    d["base"] = (
        (d.p_surv >= BASE_PS) & (d.entry_score >= BASE_ES)
    )

    monthly = []
    selections = []

    for month, g in d.groupby("month"):
        base = frozen_base_schedule(g).copy()
        base["child_source"] = "FROZEN_BASE"

        c = g[
            (~g.base)
            & g.specialist.isin(ALLOWED)
        ].copy()
        c = c.loc[outside_reserved(c, base)]

        keep = np.array(
            [candidate_ok(r, e6) for r in c.itertuples()],
            dtype=bool,
        )
        session_child = earliest_finish_schedule(c.loc[keep]).copy()
        session_child["child_source"] = "C02C_DEFICIT_ROUTER"

        combined = pd.concat([base, session_child]).sort_values("time")
        selections.append(combined)

        monthly.append(
            {
                "month": int(month),
                "trades": len(combined),
                "survival": float(combined.survive.mean()),
                "fp": float(combined.fp_win.mean()),
                "diagnostic_value": float(combined.resolved_pnl.sum()),
                "base": len(base),
                "session_child": len(session_child),
            }
        )

    selected = pd.concat(selections).sort_values("time")
    monthly = pd.DataFrame(monthly)

    # C02C research acceptance guard.
    assert (monthly.survival >= 0.85).all()

    return selected, monthly


if __name__ == "__main__":
    selected, monthly = run()
    print(monthly.to_string(index=False))
    print("trades", len(selected))
    print("weighted survivability", selected.survive.mean())
    print("first-passage success", selected.fp_win.mean())
    print("diagnostic value", selected.resolved_pnl.sum())
