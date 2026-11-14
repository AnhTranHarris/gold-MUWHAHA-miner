"""Frozen Coinexx R9 p5 model -> ORIGINAL R9 after-cost trade-lifecycle calibration.

Uses only EXISTING immutable 155-feature cache ZIPs and source-ordinal trade
ledger ZIP; never rebuilds ticks, changes the EA, or generates a new feature
archive. Replays five saved chronological LightGBM models without refitting
them. A small regularized economic head learns the ORIGINAL R9 outcome.

CAUTION: Cash head training uses IN-SAMPLE primary p5 on its training dates,
held-out primary p5 on its test month. May–Sep were already development-exposed.
The calibrated probability is NOT the value of an alternative holding/exit
action, nor any statement of live fill profitability.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import warnings
import zipfile

import joblib
import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import frozen_snapshot
from lineage_audit import MODEL_SHA

FOLD_NUMBERS = range(5, 10)
FULL = (
    "R9_M60_FullUniverse_DerivedCache_Part1_Months01-02-03_20261113.zip",
    "R9_M60_FullUniverse_DerivedCache_Part2_Months04-05-06_20261113.zip",
    "R9_M60_FullUniverse_DerivedCache_Part3_Months07-08-09_20261113.zip",
)
EVENT = (
    "R9_M60_Hazard_ExactEvent_Derived_2026_Part1_01to03_20261113.zip",
    "R9_M60_Hazard_ExactEvent_Derived_2026_Part2_04to06_20261113.zip",
    "R9_M60_Hazard_ExactEvent_Derived_2026_Part3_07to09_20261113.zip",
)
PRIORITY = "R9_M60_Coinexx_CUSUM_QuoteIntensity_Cache_JanSep_20261113.zip"
CANDIDATES = "R9_P1_Coinexx_9Month_SourceOrdinal_ASOF_CANDIDATE_CACHE_20261113.zip"
TRAINING = "R9_M60_JanSep_FullTraining_155Features_20261113.zip"
PARAMS = dict(loss="log_loss", alpha=5e-4, penalty="l2", max_iter=25,
              tol=1e-4, shuffle=False, random_state=20261114, average=True)

def cash_now(entry_price_u: int, liquidate_price_u: int, side: int,
             cash_per_quote_dollar: float, extra_roundtrip_cost: float) -> float:
    """Actual executable-side quote formula, using integer 0.01 XAU units."""
    if side not in (-1, 1) or entry_price_u <= 0 or liquidate_price_u <= 0:
        raise ValueError("Invalid executable quote or side")
    return (side * (liquidate_price_u - entry_price_u) / 100.0
            * cash_per_quote_dollar - extra_roundtrip_cost)

class Source:
    def __init__(self, root: Path):
        self.root = root
        paths = list(FULL) + list(EVENT) + [PRIORITY, CANDIDATES, TRAINING]
        missing = [p for p in paths if not (root / p).is_file()]
        if missing:
            raise FileNotFoundError("Original frozen source ZIP missing: " + ", ".join(missing))
        self.full = [zipfile.ZipFile(root / f) for f in FULL]
        self.event = [zipfile.ZipFile(root / f) for f in EVENT]
        self.priority = zipfile.ZipFile(root / PRIORITY)
        self.ledger = zipfile.ZipFile(root / CANDIDATES)
        self.training = zipfile.ZipFile(root / TRAINING)
        self.receipt = json.loads(self.ledger.read("source_receipt.json"))
        self.barrier = frozen_snapshot.source_barrier_features(root / TRAINING)
        self.names = [f"direct_test_{i:02d}_shadow.joblib" for i in FOLD_NUMBERS]
        for name in self.names:
            buf = self.training.read("models/" + name)
            if hashlib.sha256(buf).hexdigest() != MODEL_SHA[name]:
                raise ValueError("Original p5 model SHA256 mismatch: " + name)

    @staticmethod
    def _npz(z: zipfile.ZipFile, name: str):
        # Memory only; no duplicate .npz or extracted archive created.
        return np.load(io.BytesIO(z.read(name)), allow_pickle=False)

    def month(self, mm: str, k: float, c: float) -> dict:
        bucket = (int(mm) - 1) // 3
        with self._npz(self.full[bucket], f"full_derived/full_month_2026_{mm}.npz") as old, \
             self._npz(self.event[bucket], f"event_2026_{mm}.npz") as ev, \
             self._npz(self.priority, f"derived/priority_2026_{mm}.npz") as pr:
            ordinal = old["entry_ordinals"].astype("i8")
            t = old["entry_times"].astype("i8")
            side = old["side"].astype("i1")
            if not (np.array_equal(ordinal, ev["ordinal"]) and
                    np.array_equal(ordinal, pr["ordinal"]) and
                    np.array_equal(t, ev["entry"]) and
                    np.array_equal(t, pr["entry"]) and
                    np.array_equal(side, ev["r9_side"])):
                raise ValueError("Frozen source ordinal, time or side mismatch")
            if (old["features"].shape[1], ev["features"].shape[1],
                    pr["features"].shape[1]) != (145, 77, 23):
                raise ValueError("Original 145/77/23 feature archive altered")
            base = np.hstack((old["features"], ev["features"])).astype("f4")
            idx = (list(range(14)) + frozen_snapshot.OLD_HFT_IDX
                   + list(range(145, 145 + len(ev["feature_names"]))))
            spread = ev["spread"].astype("f4")
            stop = ev["stop"].astype("f4")
            target = ev["target"].astype("f4")
            analytical = self.barrier(ev["features"], spread, stop, target, side)
            meta = np.stack((side.astype("f4"), np.ones(len(side), dtype="f4"),
                             stop, target, spread), axis=1)
            x = np.concatenate((base[:, idx], pr["features"],
                                analytical, meta), axis=1).astype("f4")
            if x.shape != (len(side), 155) or np.isinf(x).any():
                raise ValueError("155-feature original model schema violated")
            ix = np.arange(len(side))
            col = np.where(side > 0, 0, 1)
            good = ev["cause"][ix, col] != -1
            y5 = ((ev["cause"][ix, col] == 1) &
                  (ev["hit_ms"][ix, col] >= 0) &
                  (ev["hit_ms"][ix, col] <= 5000))

        with gzip.GzipFile(fileobj=io.BytesIO(self.ledger.read(
                f"candidate_closes_2026_{mm}.csv.gz"))) as fh:
            rows = list(csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8")))
        n = len(rows)
        if n != len(side) or n != self.receipt["source_months"][mm]["entries"]:
            raise ValueError("Original R9 completed trade count mismatch")
        entries = np.fromiter((int(r["entry_ordinal"]) for r in rows), "i8", count=n)
        times = np.fromiter((int(r["entry_time_msc"]) for r in rows), "i8", count=n)
        sides = np.fromiter((int(r["side"]) for r in rows), "i1", count=n)
        price = np.fromiter((int(r["net_price_u"]) for r in rows), "i4", count=n)
        cash = price.astype("f8") / 100.0 * k - c
        if (not np.array_equal(entries, ordinal) or
            not np.array_equal(times, t) or not np.array_equal(sides, side)):
            raise ValueError("Original completed trade ordinals/time/side mismatch")
        # Validates signed trade quote-side pricing against immutable ledger.
        for i, r in enumerate(rows):
            if ((int(r["exit_price_u"]) - int(r["entry_price_u"])) *
                    int(side[i]) != price[i]):
                raise ValueError(f"Wrong Bid/Ask liquidation price at ordinal {ordinal[i]}")
        return {"x": x, "cash": cash.astype("f4"),
                "win": (cash > 0).astype("i1"), "y5": y5, "good": good}

    def direct_model(self, mm: str):
        name = f"direct_test_{mm}_shadow.joblib"
        raw = self.training.read("models/" + name)
        if hashlib.sha256(raw).hexdigest() != MODEL_SHA[name]:
            raise ValueError("Frozen model SHA mismatch: " + name)
        model = joblib.load(io.BytesIO(raw))["model"]
        if model.n_features_in_ != 155 or model.n_estimators != 95:
            raise ValueError("Incorrect model capacity or input count")
        return model

def make_context(x: np.ndarray, p5=None):
    """14 original R9 as-of features; add 155-head p5 as feature 15."""
    z = x[:, :14].astype("f8")
    return np.column_stack((z, p5)) if p5 is not None else z

def fit_normalization(x):
    med = np.nanmedian(x, axis=0)
    z = np.where(np.isfinite(x), x, med)
    lo, hi = np.percentile(z, [1, 99], axis=0)
    clipped = np.clip(z, lo, hi)
    mid = clipped.mean(axis=0)
    sd = clipped.std(axis=0)
    sd[sd < 1e-8] = 1
    return med, lo, hi, mid, sd

def normalize(x, stats):
    med, lo, hi, mid, sd = stats
    return ((np.clip(np.where(np.isfinite(x), x, med), lo, hi) - mid) /
            sd).astype("f4")

def fit_economic_head(x, y, x_test):
    """Bounded context-only and context+p5 cash heads; never place trades."""
    stats = fit_normalization(x)
    clf = SGDClassifier(**PARAMS)
    clf.fit(normalize(x, stats), y)
    pred = clf.predict_proba(normalize(x_test, stats))[:, 1]
    receipt = {"normalization": {key: value.tolist() for key, value in zip(
                   ("median", "p1", "p99", "center", "std"), stats)},
               "coef": clf.coef_[0].tolist(), "intercept": float(clf.intercept_[0]),
               "features": int(x.shape[1]),
               "params": PARAMS}
    return pred, receipt

def run(root: Path, k: float, c: float, output: Path) -> dict:
    if k <= 0 or c < 0 or not np.isfinite(k + c):
        raise ValueError("Account cash conversion must be >0 and extra cost >=0")
    source = Source(root)
    data = {f"{m:02d}": source.month(f"{m:02d}", k, c) for m in range(1, 10)}
    if sum(len(v["win"]) for v in data.values()) != 303934:
        raise ValueError("Original R9 nine-month universe changed")
    rows = []
    for m in FOLD_NUMBERS:
        mm = f"{m:02d}"
        prior = [f"{i:02d}" for i in range(1, m)]
        test = data[mm]
        X = np.concatenate([data[i]["x"] for i in prior])
        y = np.concatenate([data[i]["win"] for i in prior])
        primary = source.direct_model(mm)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            ptr = primary.predict_proba(X)[:, 1].astype("f4")
            p5 = primary.predict_proba(test["x"])[:, 1].astype("f4")
        base, base_receipt = fit_economic_head(
            make_context(X), y, make_context(test["x"]))
        plus, plus_receipt = fit_economic_head(
            make_context(X, ptr), y, make_context(test["x"], p5))
        ytest = test["win"]
        valid = test["good"]
        auc5 = float(roc_auc_score(test["y5"][valid], p5[valid]))
        archived = json.loads(source.training.read(
            f"outputs/fold_{mm}.json"))["models"]["direct_5sec"]["r9_direction_auc5"]
        if abs(auc5 - archived) > 1e-6:
            raise ValueError(f"Original fold AUC did not reproduce for month {mm}")
        q = np.quantile(p5, np.linspace(0, 1, 11))
        bucket = np.searchsorted(q[1:-1], p5, side="right")
        deciles = [{"decile": j + 1, "trades": int((bucket == j).sum()),
                    "mean_original_net_cash": float(test["cash"][bucket == j].mean()),
                    "original_win_fraction": float(ytest[bucket == j].mean())}
                   for j in range(10)]
        rows.append({"test_month": mm, "train_months": prior,
            "original_trades": len(ytest), "train_trades": len(y),
            "original_after_cost_win_fraction": float(ytest.mean()),
            "original_mean_net_cash": float(test["cash"].mean()),
            "frozen_original_side_auc5": auc5,
            "same_p5_auc_for_original_net_win": float(roc_auc_score(ytest, p5)),
            "r9_context_only_cash_auc": float(roc_auc_score(ytest, base)),
            "r9_context_plus_frozen_p5_cash_auc": float(roc_auc_score(ytest, plus)),
            "r9_context_plus_p5_AP": float(average_precision_score(ytest, plus)),
            "r9_context_plus_p5_brier": float(brier_score_loss(ytest, plus)),
            "p5_score_deciles_DESCRIPTIVE_ONLY": deciles,
            "cash_head_context_only": base_receipt,
            "cash_head_context_plus_p5": plus_receipt})
        print(f"eval {mm}: p5 fixed-label AUC {auc5:.6f} -> original trade "
              f"profit AUC {rows[-1]['same_p5_auc_for_original_net_win']:.6f}; "
              f"context+p5 cash AUC {rows[-1]['r9_context_plus_frozen_p5_cash_auc']:.6f}",
              flush=True)
    keys = ("frozen_original_side_auc5", "same_p5_auc_for_original_net_win",
            "r9_context_only_cash_auc", "r9_context_plus_frozen_p5_cash_auc")
    result = {"status": "ORIGINAL_R9_SHADOW_LIFECYCLE_ONLY_NO_EXIT_POLICY",
        "source": "SHA-pinned original five LightGBM models, 155-feature Coinexx caches and original R9 trade ledger",
        "n_original_train_and_test": 303934,
        "n_five_test_month_positions": sum(r["original_trades"] for r in rows),
        "cash_per_XAU_quote_dollar_ASSUMED": k,
        "extra_roundtrip_cash_cost_ASSUMED": c,
        "warning": "Primary model scores are in-sample on cash-head TRAIN months; "
                   "held-out on TEST months. Historical Jan–Sep already development-exposed. "
                   "Original R9 exit only; no counterfactual holding/rearming or broker fills.",
        "equal_month_auc_means": {key: float(np.mean([r[key] for r in rows]))
                                   for key in keys},
        "folds": rows}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-dir", type=Path, required=True)
    p.add_argument("--cash-per-one-xau-price-dollar", type=float, required=True)
    p.add_argument("--extra-roundtrip-cash-cost", type=float, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    run(a.source_dir, a.cash_per_one_xau_price_dollar,
        a.extra_roundtrip_cash_cost, a.output)

if __name__ == "__main__":
    main()
