"""Train NEW R9 dual-basket entry admissions, Jan-Sep Coinexx SOURCE-EXACT.

Uses ORIGINAL read-only monthly gzip and pinned source-ordinal receipt; no tick
rebuilding, exports, feature archive, uploaded datasets, or re-trained M60 model.
First pass builds labels from the new basket's actual trade occupancy/exit
logic. A frozen model gets a second chronological ON-POLICY July-Sep replay.
Training labels are entry-side strategy outcomes, not abstract future-bar tags.

Jan-Jun fit -> July choose conservative admission -> August check -> September
frozen *development-exposed* evaluation. Only AFTER September is evaluated is
an optional Jan-Sep IN-SAMPLE model fitted for a genuinely later period.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import os
import sys
import time
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for sub in ("src", "variable_cash_horizon_20261114", "dual_basket_20261114"):
    sys.path.insert(0, str(ROOT / sub))

from coinexx_r9.r9_baseline import R9Config, R9HybridGateBaseline
from coinexx_r9.ticks import iter_coinexx_ticks
from on_policy_cash_replay import ResearchCash, QuoteRegime
from run_coinexx import source_sha, verify_month, reuse_only_identical_market_context
from dual_basket import DualBasketCash, DualBasketSpec, FEATURE_NAMES

MONTHS = tuple(f"{n:02d}" for n in range(1, 10))
FIT_MONTHS = MONTHS[:6]
PICK_MONTH = "07"
CHECK_MONTH = "08"
FROZEN_MONTH = "09"
CUTOFF_QUANTILES = (0., 0.01, 0.03, 0.05)
MODEL_SPEC = {
    "model": "sklearn.ensemble.HistGradientBoostingRegressor",
    "max_iter": 100, "learning_rate": 0.05, "max_leaf_nodes": 12,
    "min_samples_leaf": 200, "l2_regularization": 25.0,
    "loss": "squared_error", "random_state": 20261114,
    "label_cash_clip": [-2.0, 1.75],
}

@dataclass(frozen=True)
class LabeledEntry:
    month: str
    ordinal: int
    time_msc: int
    features: tuple[float, ...]
    modeled_net_cash: float
    side: int


def labeled_positions(entries: list[dict], trades: list, bounds: list[int],
                      months: tuple[str, ...], cash: ResearchCash) -> list[LabeledEntry]:
    """Match actual executed candidate entries to their own causal exit labels.

    Only entries with a COMPLETED exit enter the model. A trade near a split
    boundary that exits after that boundary is purged from the earlier fit.
    """
    if len(bounds) != len(months) or sorted(bounds) != bounds:
        raise ValueError("Month ordinal boundaries invalid")
    by_entry = {int(e["ordinal"]): e for e in entries}
    if len(by_entry) != len(entries):
        raise ValueError("Duplicate entry ordinals in chronological candidate population")
    out = []
    for tr in trades:
        e = by_entry.get(tr.entry_ordinal)
        if e is None:
            raise AssertionError("Trade not matched to an entry in the new universe")
        features = tuple(float(v) for v in e.get("features", ()))
        if len(features) != len(FEATURE_NAMES) or not all(math.isfinite(v) for v in features):
            raise ValueError("Missing or invalid as-of dual-basket feature vector")
        index = bisect.bisect_right(bounds, tr.entry_ordinal)
        if index >= len(months):
            raise ValueError("Entry ordinal exceeds source receipt")
        month = months[index]
        out.append(LabeledEntry(
            month, tr.entry_ordinal, tr.entry_time_msc, features,
            tr.net_price_u / 100.0 * cash.k - cash.cost, tr.side))
    return out


def embargoed_fit(entries: list[LabeledEntry], cutover_utc_ms: int,
                 embargo_ms: int = 120_000) -> list[LabeledEntry]:
    """Purge last 120 seconds of June and any future labels from fit."""
    return [r for r in entries if r.month in FIT_MONTHS
            and r.time_msc < cutover_utc_ms - embargo_ms]


def train_fixed_model(rows: list[LabeledEntry]):
    """Only fixed-capacity, clipped-loss model; no broad hyperparameter sweep."""
    import numpy as np
    from sklearn.ensemble import HistGradientBoostingRegressor
    if len(rows) < 1000:
        raise ValueError("Insufficient as-of new-entry training positions")
    X = np.asarray([r.features for r in rows], dtype=np.float32)
    y = np.clip(np.asarray([r.modeled_net_cash for r in rows], dtype=np.float64),
                -2.0, 1.75)
    model = HistGradientBoostingRegressor(**{
        k: v for k, v in MODEL_SPEC.items() if k not in
        ("model", "label_cash_clip")
    })
    model.fit(X, y)
    return model


def scores(model: Any, rows: list[LabeledEntry]) -> list[float]:
    import numpy as np
    if not rows:
        return []
    return [float(v) for v in model.predict(
        np.asarray([r.features for r in rows], dtype=np.float32))]


def rank_cutoffs(train_scores: list[float]) -> dict[float, float]:
    import numpy as np
    if not train_scores:
        raise ValueError("No training scores")
    s = np.asarray(train_scores, dtype=np.float64)
    return {q: float(np.quantile(s, q)) if q else float("-inf")
            for q in CUTOFF_QUANTILES}


def diag(rows: list[LabeledEntry], values: list[float], cutoff: float) -> dict:
    if len(rows) != len(values):
        raise ValueError("Score and action rows not aligned")
    keep = [r.modeled_net_cash for r, p in zip(rows, values)
            if math.isfinite(p) and p >= cutoff]
    allnet = [r.modeled_net_cash for r in rows]
    n = len(rows)
    gross = lambda a: -sum(min(v, 0.) for v in a)
    return {
        "candidate_positions": n, "offline_kept": len(keep),
        "offline_retention_fraction": round(len(keep) / n, 8) if n else None,
        "offline_original_net": round(sum(allnet), 5),
        "offline_subset_net": round(sum(keep), 5),
        "offline_subset_net_delta": round(sum(keep) - sum(allnet), 5),
        "offline_subset_gross_losses": round(gross(keep), 5),
        "offline_original_gross_losses": round(gross(allnet), 5),
        "offline_frac_ge_010": round(sum(x >= .10 - 1e-9 for x in keep)
                                        / len(keep), 7) if keep else None,
        "warning": "OFF-POLICY subset only; gating changes future trade occupancy",
    }


def choose_predeclared_cutoff(rows: list[LabeledEntry],
                              values: list[float],
                              cutoffs: dict[float, float]) -> tuple[float, dict]:
    """July-only bounded selection; never force a gate if net is negative.

    No-gate is the priority fallback. A nonzero rejection fraction must show
    positive full-month net and >=95% offline candidate retention; then still
    requires separate subsequent ON-POLICY checks.
    """
    diagnostics = {str(q): diag(rows, values, cutoff)
                   for q, cutoff in cutoffs.items()}
    best = 0.
    best_net = -math.inf
    for q in CUTOFF_QUANTILES:
        d = diagnostics[str(q)]
        if (d["offline_retention_fraction"] is not None and
            d["offline_retention_fraction"] >= .95 and
            d["offline_subset_net"] > 0 and
            d["offline_subset_net"] > best_net):
            best, best_net = q, d["offline_subset_net"]
    return best, diagnostics


class FrozenAdmission:
    """Frozen, deterministic model applied at the *actual* new entry quote."""
    def __init__(self, model: Any, cutoff: float) -> None:
        if not (math.isfinite(cutoff) or cutoff == float("-inf")):
            raise ValueError("Invalid frozen gate")
        self.model, self.cutoff = model, cutoff
        self.queries = 0
        self.rejections = 0

    def accept(self, features: tuple[float, ...]) -> bool:
        if len(features) != len(FEATURE_NAMES) or not all(
                math.isfinite(f) for f in features):
            raise ValueError("Unexpected or invalid as-of entry feature schema")
        self.queries += 1
        if self.cutoff == float("-inf"):
            return True
        # sklearn accepts a 2-D sequence. Keep live candidate inference
        # lightweight and independent of a needless per-quote numpy import.
        score = float(self.model.predict([features])[0])
        ok = math.isfinite(score) and score >= self.cutoff
        if not ok:
            self.rejections += 1
        return ok


def metrics_by_month(sim, bounds: list[int], cash: ResearchCash) -> dict:
    """Entry-month cash and realized tail metrics; not verified MT5 fills."""
    stats = {m: {"trades": 0, "net": 0., "gross_loss": 0.,
                 "trades_ge_010": 0, "trades_ge_175": 0}
             for m in MONTHS}
    hours = {m: defaultdict(float) for m in MONTHS}
    values = {m: [] for m in MONTHS}
    cumulative = defaultdict(float)
    peak = defaultdict(float)
    peak_dd = defaultdict(float)
    for t in sim.trades:
        i = bisect.bisect_right(bounds, t.entry_ordinal)
        if i >= len(MONTHS):
            raise ValueError("Trade entry ordinal beyond source")
        key = MONTHS[i]
        row = stats[key]
        net = t.net_price_u / 100. * cash.k - cash.cost
        row["trades"] += 1
        row["net"] += net
        row["gross_loss"] += max(0., -net)
        row["trades_ge_010"] += net >= .10 - 1e-9
        row["trades_ge_175"] += net >= 1.75 - 1e-9
        hours[key][t.entry_time_msc // 3_600_000] += net
        values[key].append(net)
        cumulative[key] += net
        peak[key] = max(peak[key], cumulative[key])
        peak_dd[key] = max(peak_dd[key], peak[key] - cumulative[key])
    for key, v in stats.items():
        v["net"] = round(v["net"], 4)
        v["gross_loss"] = round(v["gross_loss"], 4)
        v["active_entry_hours"] = len(hours[key])
        v["net_per_active_hour"] = round(
            v["net"] / max(1, len(hours[key])), 5)
        v["negative_entry_hours"] = sum(h < 0 for h in hours[key].values())
        v["max_realized_cash_drawdown_within_entry_month"] = round(peak_dd[key], 4)
        tail = sorted(values[key])[:max(1, int(len(values[key]) * .05))]
        v["closed_trade_cvar95_loss"] = (
            round(-sum(tail) / len(tail), 5) if values[key] else None)
    return stats

def original_source_pass(args, receipt: dict, cash: ResearchCash):
    cfg = R9Config()
    control = R9HybridGateBaseline(cfg)
    regime = QuoteRegime()
    cash_arm = DualBasketCash(cfg, cash, protected_stretch=False, regime=regime)
    reuse_only_identical_market_context(control, cash_arm)
    bounds = []
    offset = 0
    baseline_start = 0
    receipt_log = []
    for mm in MONTHS:
        src = args.data / f"XAUUSD_MT5_BROKER_2026_{mm}_ticks_ALL.csv.gz"
        if not src.is_file():
            raise FileNotFoundError(f"Need original local gzip: {src}")
        want = receipt["source_months"][mm]["source_sha256"]
        actual = source_sha(src)
        if actual != want:
            raise AssertionError(f"Source checksum mismatch {mm}, stop")
        t0 = time.monotonic()
        count = 0
        first_source_msc = None
        last_source_msc = None
        for tick in iter_coinexx_ticks(src, strict=True, ordinal_offset=offset):
            if first_source_msc is None:
                first_source_msc = tick.time_msc
            last_source_msc = tick.time_msc
            regime.update(tick)
            control.on_tick(tick)
            cash_arm.on_tick(tick)
            count += 1
        if count != receipt["source_months"][mm]["rows"]:
            raise AssertionError(f"Source row count mismatch {mm}")
        verified = verify_month(control, baseline_start, mm, args.receipt_zip, receipt)
        baseline_start = len(control.trades)
        offset += count
        bounds.append(offset)
        row = dict(month=mm, rows=count, sha256=actual, exact_original_trade_parity=bool(verified),
                   first_source_msc=first_source_msc, last_source_msc=last_source_msc,
                   original_trade_count=verified, dual_cash010_trade_count=len(cash_arm.trades),
                   runtime_s=round(time.monotonic()-t0, 2))
        receipt_log.append(row)
        print("SOURCE " + json.dumps(row, sort_keys=True), flush=True)
    records = labeled_positions(cash_arm.entries, cash_arm.trades, bounds, MONTHS, cash)
    return control, cash_arm, records, bounds, receipt_log


def on_policy_replay(args, cash: ResearchCash, model: Any,
                     cutoff: float, bounds: list[int], receipt: dict):
    """Second exact-source pass; candidate rejection changes subsequent entries."""
    cfg = R9Config()
    market = R9HybridGateBaseline(cfg)
    regime = QuoteRegime()
    harvest = DualBasketCash(cfg, cash, protected_stretch=False, regime=regime)
    stretch = DualBasketCash(cfg, cash, protected_stretch=True, regime=regime)
    reuse_only_identical_market_context(market, harvest, stretch)
    if cutoff == float("-inf"):
        selector_h = selector_s = None
    else:
        selector_h = FrozenAdmission(model, cutoff)
        selector_s = FrozenAdmission(model, cutoff)
    offset = 0
    for mm in MONTHS:
        if mm in (PICK_MONTH, CHECK_MONTH, FROZEN_MONTH):
            harvest.entry_selector = selector_h
            stretch.entry_selector = selector_s
        path = args.data / f"XAUUSD_MT5_BROKER_2026_{mm}_ticks_ALL.csv.gz"
        count = 0
        for tick in iter_coinexx_ticks(path, strict=True, ordinal_offset=offset):
            regime.update(tick)
            market.on_tick(tick)
            harvest.on_tick(tick)
            stretch.on_tick(tick)
            count += 1
        if count != receipt["source_months"][mm]["rows"]:
            raise AssertionError(f"On-policy {mm} second-pass row count changed")
        offset += count
        if offset != bounds[int(mm)-1]:
            raise AssertionError("Second-pass original ordinals diverged")
        print("ON_POLICY " + json.dumps({
            "month": mm, "rows": count,
            "harvest_total_trades": len(harvest.trades),
            "stretch_total_trades": len(stretch.trades),
        }, sort_keys=True), flush=True)
    return {
        "cash010_immediate": metrics_by_month(harvest, bounds, cash),
        "cash010_stretch175": metrics_by_month(stretch, bounds, cash),
        "portfolio": {
            name: {
                "total_trades": report.get("trades"),
                "net_cash": report.get("net_cash"),
                "gross_realized_losses": report.get("gross_realized_losses"),
                "closed_trade_cvar95_loss": report.get("closed_trade_cvar95_loss"),
                "max_account_peak_drawdown_cash": report.get("max_account_peak_drawdown_cash"),
                "source_day_cash_negative_count": report.get("source_day_cash_negative_count"),
                "governor_halts": report.get("governor_halts"),
            }
            for name, report in (
                ("cash010_immediate", harvest.report()),
                ("cash010_stretch175", stretch.report()),
            )
        },
        "inference_calls": {
            "cash010": selector_h.queries if selector_h else 0,
            "stretch175": selector_s.queries if selector_s else 0,
        },
    }


def main(args):
    if args.months != list(MONTHS):
        raise ValueError("Nine-month training must use exactly 01..09, chronological")
    for mm in MONTHS:
        if not (args.data / f"XAUUSD_MT5_BROKER_2026_{mm}_ticks_ALL.csv.gz").is_file():
            raise FileNotFoundError(f"Original quote file {mm} not present at {args.data}")
    if not args.receipt.exists():
        raise FileNotFoundError(f"Frozen source-ordinal receipt missing: {args.receipt}")
    cash = ResearchCash(args.k, args.c, args.start_capital, governor=False)
    args.receipt_zip = zipfile.ZipFile(args.receipt)
    try:
        receipt = json.loads(args.receipt_zip.read("source_receipt.json"))
        if set(MONTHS) - set(receipt["source_months"]):
            raise AssertionError("Frozen receipt does not cover all nine original months")
        original, entries, rows, bounds, verified = original_source_pass(args, receipt, cash)
    finally:
        args.receipt_zip.close()

    # Purge against the EXACT first observed July source-native timestamp,
    # never an assumed UTC offset or a fabricated month-boundary quote.
    cutover = next(r["first_source_msc"] for r in verified
                   if r["month"] == PICK_MONTH)
    if cutover is None:
        raise AssertionError("Missing original July boundary timestamp")
    train_rows = embargoed_fit(rows, cutover)
    july = [r for r in rows if r.month == PICK_MONTH]
    august = [r for r in rows if r.month == CHECK_MONTH]
    september = [r for r in rows if r.month == FROZEN_MONTH]
    if not all((len(train_rows) >= 1000, july, august, september)):
        raise ValueError("Insufficient full nine-month candidate labels")

    model = train_fixed_model(train_rows)
    s_train = scores(model, train_rows)
    cutoffs = rank_cutoffs(s_train)
    j_scores = scores(model, july)
    chosen_q, july_choices = choose_predeclared_cutoff(july, j_scores, cutoffs)
    a_scores = scores(model, august)
    a_choices = {str(q): diag(august, a_scores, threshold)
                 for q, threshold in cutoffs.items()}
    # August is a veto, not a second optimization surface.
    if chosen_q:
        d = a_choices[str(chosen_q)]
        if (d["offline_retention_fraction"] is None or
            d["offline_retention_fraction"] < .95 or
            d["offline_subset_net"] <= 0):
            chosen_q = 0.
    cutoff = cutoffs[chosen_q]
    s_scores = scores(model, september)
    s_preliminary = diag(september, s_scores, cutoff)
    # September is scored ONCE with the already chosen gate.
    on_policy = on_policy_replay(args, cash, model, cutoff, bounds, receipt)
    ungated = metrics_by_month(entries, bounds, cash)
    original_metrics = metrics_by_month(original, bounds, cash)
    target = on_policy["cash010_immediate"]
    comparators = {}
    for mm in (PICK_MONTH, CHECK_MONTH, FROZEN_MONTH):
        r, b = target[mm], ungated[mm]
        pct = r["trades"] / b["trades"] if b["trades"] else None
        comparators[mm] = {
            "on_policy_cash010_net": r["net"], "ungated_cash010_net": b["net"],
            "on_policy_cash010_gross_loss": r["gross_loss"],
            "ungated_cash010_gross_loss": b["gross_loss"],
            "on_policy_position_count": r["trades"],
            "ungated_position_count": b["trades"],
            "retention_fraction": round(pct, 6) if pct is not None else None,
            "on_policy_approved": bool(
                pct is not None and pct >= .95 and r["net"] > 0 and
                r["gross_loss"] <= b["gross_loss"] and
                r["net"] > b["net"]),
        }
    report = {
        "research_only": True, "actual_training_executed": True,
        "model_identity": "NEW_DUAL_BASKET_CASH010_ENTRY_REGRESSOR_NOT_M60",
        "source_parity": verified, "feature_names": FEATURE_NAMES,
        "fixed_model_spec": MODEL_SPEC, "train_months": FIT_MONTHS,
        "selection_month": PICK_MONTH, "veto_month": CHECK_MONTH,
        "frozen_exposed_test_month": FROZEN_MONTH,
        "train_entries": len(train_rows), "month_candidate_counts": {
            mm: sum(r.month == mm for r in rows) for mm in MONTHS},
        "cutoff_candidates_july": july_choices,
        "cutoff_veto_august": a_choices,
        "selected_rejection_quantile": chosen_q,
        "frozen_cutoff": cutoff if math.isfinite(cutoff) else None,
        "no_gate_selected": cutoff == float("-inf"),
        "september_off_policy_diagnostic_not_final": s_preliminary,
        "baseline_old_R9": original_metrics,
        "baseline_ungated_new_cash010": ungated,
        "frozen_on_policy": on_policy,
        "comparative_heldout_metrics": comparators,
        "approved_for_mt5": False,
        "approval_notes": [
            "Even if July/Aug/Sept pass, prior research exposure and broker parity forbid live promotion",
            "Quote-side K/C, fills, rejected stops, MQL5 OnTick queue and account governor remain unverified",
            "No final Jan-Sep model was scored on its own training rows as heldout",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # No model gets silently replaced by a fit on previously evaluated months.
    import joblib
    frozen_path = args.output.with_suffix(".presept_model.joblib")
    joblib.dump({"model": model, "cutoff": cutoff,
                 "schema": FEATURE_NAMES, "train_months": FIT_MONTHS,
                 "status": "research_only"}, frozen_path)
    with frozen_path.open("rb") as f:
        report["frozen_presept_sha256"] = hashlib.file_digest(f, "sha256").hexdigest()
    if args.final_all_nine:
        full = train_fixed_model(rows)
        full_scores = scores(full, rows)
        full_cutoff = rank_cutoffs(full_scores)[chosen_q]
        full_path = args.output.with_suffix(".jansep_INSAMPLE_ONLY.joblib")
        joblib.dump({"model": full, "cutoff": full_cutoff,
                     "schema": FEATURE_NAMES, "train_months": MONTHS,
                     "status": "INSAMPLE_ONLY_UNSCORED_FUTURE_MONTH_REQUIRED"}, full_path)
        with full_path.open("rb") as f:
            model_sha = hashlib.file_digest(f, "sha256").hexdigest()
        report["optional_full_jansep_fit"] = {
            "trained_entries": len(rows), "status": "IN_SAMPLE_ONLY",
            "model_file": str(full_path), "model_sha256": model_sha,
            "next_action": "freeze and assess truly unseen post-September quotes"}
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2, default=list) + "\n")
    print("TRAINING_REPORT " + str(args.output), flush=True)
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", required=True, type=Path,
                   help="Existing local folder of ORIGINAL monthly Coinexx .csv.gz")
    p.add_argument("--receipt", required=True, type=Path,
                   help="Existing pinned SourceOrdinal candidate-cache ZIP")
    p.add_argument("--months", nargs="+", default=list(MONTHS))
    p.add_argument("--k", type=float, default=1.0)
    p.add_argument("--c", type=float, default=.20)
    p.add_argument("--start-capital", type=float, default=100000.)
    p.add_argument("--no-final-all-nine", dest="final_all_nine",
                   action="store_false", default=True,
                   help="Opt out of full Jan-Sep IN-SAMPLE ONLY fit after frozen September evaluation")
    p.add_argument("--output", type=Path, default=Path("R9_DUAL_JANSEP_TRAIN_REPORT.json"))
    main(p.parse_args())
