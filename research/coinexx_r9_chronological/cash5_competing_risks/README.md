# R9 v1.94 — Conditional five-second Coinexx cash competing-risks (research only)

This small, self-contained package reuses **existing** previously source-verified original R9 five-second cash labels and **frozen original out-of-fold LightGBM predictions**. It does not recreate raw ticks, modify source caches, retrain the approved 155-feature classifier, or change a trade.

Run using Python 3.11+ with `numpy`, `pandas`, `scikit-learn` and the existing source folder:

```
python competing_cash5.py --root /path/to/existing/coinexx_source_folder --output scorecard.json
python robustness.py --root /path/to/existing/coinexx_source_folder --output robustness.json --bootstrap 200
python -m unittest discover -s tests -v
```

Required already-existing paths relative to `--root`:

- `R9_P1_Coinexx_9Month_SourceOrdinal_ASOF_CANDIDATE_CACHE_20261113.zip`
- `R9_M60_JanSep_FullTraining_155Features_20261113.zip`
- `r9_auc_strength_work/cache/micro_2026_MM.npz` for MM=05–09
- `r9_auc_strength_work/pred_fold_MM.npz` for MM=05–09

The small NPZ files were created and source-hash checked in the *previous* bounded 155-vs-171 AUC experiment; **this package does not recreate them**. If you lack those small files, do not substitute invented data or claim the score can be reproduced. Reread original archive provenance before obtaining a new copy.

Favorable-first: net +0.10 before adverse net −0.65 using illustrative K=1 and additional C=.20 per original R9 entry; otherwise none or gap-censored. Models compare R9 as-of context vs context + frozen p5 using only earlier genuinely held-out P5 months. June–Sep results are independent **conditional cash event prediction**, not a tested trading improvement.

The exact original R9 v1.94 EA and v1.90 rollback remain unchanged. No live model inference, MQL5 compilation or filled MT5 trade data are included in this experiment.