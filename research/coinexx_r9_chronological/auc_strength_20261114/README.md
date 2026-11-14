# R9 v1.94 — Coinexx-only AUC strengthening research

Research-only Python package, dated 2026-11-14. No MetaTrader EA or broker orders are changed. **The original 155-feature model won the matched experiment; the 171-feature candidate is NOT a deployable improvement.**

## Contents

- `micro_events.py`: source-ordered streaming extraction of 16 as-of 10/50/250ms Bid/Ask path features, and a separately labeled illustrative 5-second net-cash first-event outcome. Strict original one-based global ordinals, side, entry price and SHA-256 validation. Does not store or rebuild raw ticks.
- `train_auc.py`: exact 155-feature original contract assembly from pre-existing frozen cache archives, SHA-pinned 95-tree saved LightGBM model replay, five monthly direct AUC comparisons, distinct cash5 LightGBM companion and source-session diagnostics.
- `summarize.py`: previous-heldout-only session Platt calibration, 160 paired full-source-day resamples per fold, statistical summary and conservative non-promotion gate.
- `tests/test_micro_auc.py`: six causal/no-future, price, ordinal and calibration contract unit tests.
- `R9_V194_AUC_STRENGTH_FORENSIC_REPORT_20261114.md`: results interpretation, tables and scope limits.
- `r9_auc_strength_final.json`: compact machine-readable five-fold results. **Does not contain original raw market data, saved models or customer account data.**

## Verification

Python >=3.11 with numpy, pandas, scipy, numba, lightgbm, scikit-learn, joblib. Avoid live MT5 use.

```bash
python -m unittest discover -s tests -v
python micro_events.py --source-dir /existing/original/coinexx --cache-dir ./cache --months 1 2 3 4 5 6 7 8 9
python train_auc.py --source-dir /existing/original/coinexx --micro-dir ./cache --output verify.json --verify-only
python train_auc.py --source-dir /existing/original/coinexx --micro-dir ./cache --output first_fold.json --folds 5
# Repeat --folds 6, 7, 8, 9 with their corresponding output names.
python summarize.py --work-dir . --source-dir /existing/original/coinexx --output scorecard.json
```

The `--source-dir` must contain the ORIGINAL nine Coinexx XAUUSD monthly `.csv.gz` files plus the ORIGINAL 3 full-derived, 3 exact-event, one priority, one original candidate ledger, and one 155-feature model archive ZIP. Use the files already in the primary Google Drive and original project files; no independent source reconstruction, new historical broker exports or model-engine rebuild is authorized. `--micro-dir` contains at most ~2.1 MB of compact, source-verified snapshots and can be deleted after the run.

The original direct model AUCs are verified to 1e-6 before any comparison. Evaluation outputs are retrospective and were previously research-exposed. An apparent AUC gain does not prove actual after-cost profit, live execution readiness or causal policy improvement.

## Original source preservation

Original deployed R9 v1.94 standalone commit: `813baf96f2b381be5fc7896aac8b08a966114948`. Original critical v1.90 rollback: `8729a6345655a7b4ea31facc81982004ee2b8921`. Both are unchanged.