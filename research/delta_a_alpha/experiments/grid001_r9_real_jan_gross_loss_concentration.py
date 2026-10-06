from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

CANONICAL_NET = -6651.62
CANONICAL_GP = 3785.28
CANONICAL_GL = -10436.90


def econ(df: pd.DataFrame, mask: np.ndarray) -> dict:
    x = df.loc[mask]
    if len(x):
        deals = np.concatenate(
            [
                x.entry_deal_cashflow.to_numpy(float),
                x.exit_deal_cashflow.to_numpy(float),
            ]
        )
    else:
        deals = np.array([], float)

    gp = float(deals[deals > 0].sum()) if len(deals) else 0.0
    gl = float(deals[deals < 0].sum()) if len(deals) else 0.0
    net = float(x.net_cashflow.sum())

    return {
        "trades": int(len(x)),
        "trade_share_pct": 100.0 * len(x) / len(df),
        "net": net,
        "gross_profit": gp,
        "gross_loss": gl,
        "pf": gp / abs(gl) if gl < 0 else None,
        "gross_loss_share_pct": 100.0 * abs(gl) / abs(CANONICAL_GL),
        "gross_profit_share_pct": 100.0 * gp / CANONICAL_GP,
        "hypothetical_veto_net_improvement": -net,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("context_rows", type=Path)
    ap.add_argument("ticks", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.context_rows)
    tick_times = pd.read_csv(
        args.ticks,
        compression="gzip",
        usecols=["timestamp_ms_utc"],
        dtype={"timestamp_ms_utc": "i8"},
    ).timestamp_ms_utc.to_numpy()

    split_ms = int(tick_times[2 * len(tick_times) // 3])
    df["segment"] = np.where(df.entry_utc_ms < split_ms, "discovery", "validation")

    rel_map = {-1: "OPPOSED", 0: "NEUTRAL", 1: "ALIGNED", 2: "CONFLICT"}
    phase_map = {0: "NONE", 1: "EARLY", 2: "MATURE", 3: "EXTENDED"}
    df["owner_rel_name"] = df.owner_relation.map(rel_map)
    df["phase_name"] = df.owner_phase.map(phase_map)

    def vol_bin(v):
        if pd.isna(v):
            return "NA"
        if v < 1.0:
            return "<1.00"
        if v < 1.75:
            return "1.00-1.75"
        if v < 2.0:
            return "1.75-2.00"
        return ">=2.00"

    df["vol_bin"] = df.vol_ratio_atr14_atr240.map(vol_bin)

    def age_bin(v):
        if pd.isna(v):
            return "NA"
        if v < 5:
            return "<5s"
        if v < 30:
            return "5-30s"
        if v < 120:
            return "30-120s"
        return ">=120s"

    for lattice in ("A05", "A10", "A15"):
        df[f"{lattice}_age_bin"] = df[f"{lattice}_event_age_s"].map(age_bin)
        df[f"{lattice}_rel_name"] = df[f"{lattice}_event_relation"].map(
            {-1: "OPPOSED", 0: "NA", 1: "ALIGNED"}
        )

    rel = df[
        ["A05_event_relation", "A10_event_relation", "A15_event_relation"]
    ].to_numpy()
    consensus = np.full(len(df), "MIXED", object)
    consensus[np.all(rel == 1, axis=1)] = "ALL_ALIGNED"
    consensus[np.all(rel == -1, axis=1)] = "ALL_OPPOSED"
    df["lattice_consensus"] = consensus

    groups = []

    def add(family, key, mask):
        mask = np.asarray(mask, bool)
        groups.append(
            {
                "family": family,
                "key": key,
                "full": econ(df, mask),
                "discovery": econ(df, mask & (df.segment == "discovery")),
                "validation": econ(df, mask & (df.segment == "validation")),
            }
        )

    for relation in ("ALIGNED", "OPPOSED", "CONFLICT", "NEUTRAL"):
        add("F1_OWNER_RELATION", relation, df.owner_rel_name == relation)

    for tf in (5, 15):
        for relation in ("ALIGNED", "OPPOSED"):
            add(
                "F2_OWNER_TF_REL",
                f"{tf}m_{relation}",
                (df.owner_tf == tf) & (df.owner_rel_name == relation),
            )

    for tf in (5, 15):
        for relation in ("ALIGNED", "OPPOSED"):
            for phase in ("EARLY", "MATURE", "EXTENDED"):
                add(
                    "F3_OWNER_TF_REL_PHASE",
                    f"{tf}m_{relation}_{phase}",
                    (df.owner_tf == tf)
                    & (df.owner_rel_name == relation)
                    & (df.phase_name == phase),
                )

    for vb in ("<1.00", "1.00-1.75", "1.75-2.00", ">=2.00", "NA"):
        add("F4_VOL_EXPANSION", vb, df.vol_bin == vb)

    for lattice in ("A05", "A10", "A15"):
        for relation in ("ALIGNED", "OPPOSED"):
            add(
                "F5_LATEST_EVENT_REL",
                f"{lattice}_{relation}",
                df[f"{lattice}_rel_name"] == relation,
            )
            for age in ("<5s", "5-30s", "30-120s", ">=120s"):
                add(
                    "F5_LATEST_EVENT_REL_AGE",
                    f"{lattice}_{relation}_{age}",
                    (df[f"{lattice}_rel_name"] == relation)
                    & (df[f"{lattice}_age_bin"] == age),
                )

    for value in ("ALL_ALIGNED", "ALL_OPPOSED", "MIXED"):
        add("F6_LATTICE_CONSENSUS", value, df.lattice_consensus == value)

    for relation in ("OPPOSED", "ALIGNED"):
        for phase in ("EARLY", "MATURE", "EXTENDED"):
            add(
                "F7_OWNER_REL_PHASE",
                f"{relation}_{phase}",
                (df.owner_rel_name == relation) & (df.phase_name == phase),
            )
        for vb in ("<1.00", "1.00-1.75", "1.75-2.00", ">=2.00"):
            add(
                "F7_OWNER_REL_VOL",
                f"{relation}_{vb}",
                (df.owner_rel_name == relation) & (df.vol_bin == vb),
            )

    candidates = []
    for group in groups:
        full = group["full"]
        discovery = group["discovery"]
        validation = group["validation"]
        scale = (
            full["gross_loss_share_pct"] >= 20.0
            or full["hypothetical_veto_net_improvement"] >= 0.20 * abs(CANONICAL_NET)
        )
        stable = discovery["net"] < 0 and validation["net"] < 0
        efficient = full["gross_loss_share_pct"] > full["gross_profit_share_pct"]
        if scale and stable and efficient:
            candidates.append(group)

    result = {
        "schema": "delta-a-alpha-r9-real-jan-gross-loss-concentration-v1",
        "unit": "DAA_GRID_001_R9_REAL_JAN_GROSS_LOSS_CONCENTRATION_001",
        "status": "COMPLETE",
        "canonical": {
            "net": CANONICAL_NET,
            "gross_profit": CANONICAL_GP,
            "gross_loss": CANONICAL_GL,
        },
        "candidate_gate_count": len(candidates),
        "candidates": candidates,
        "all_groups": groups,
    }

    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
