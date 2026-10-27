# R00-054 A01 reproducibility — research-only negative

This branch extends the existing R15/F44 research; it does not replace, modify, or rebuild either approved original-tick replay engine. Run only on immutable original archived source-event scores and original R9 quota reference. The score arrays are not native bid/ask quotes.

## Source inputs (read-only)

Place these user-archived original files at the following paths, or pass alternate absolute paths to the main script:

- `/mnt/data/source/R00_054_F44_OUT_OF_FIT_COOPERATIVE_ERROR_ARBITER_20261020.zip` — SHA256 `9f08a8c77c7f9c8f4fe5e4dd364a1b4a22e6e25f2cfacba364cd88a4a047fa5e`
- `/mnt/data/source/R00_054_FILTER08_FOUR_MONTH_70PCT_OVERFIT_RESEARCH_20261019.zip` — SHA256 `7edaddf30f3a19cafd364a270333c6f87962960233f9d10ccbfb6e2a3b23b2ad`

Python 3.13.5, numpy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0, pytest 9.0.2 (observed run environment). All score arrays must preserve original order and t0, side, truth. Never use original same-month FILTER08 fitted teacher score as input.

## Commands

From the directory containing `r00_054_a01_chronological_session_hazard.py`:

```bash
python -m pytest -q test_chronological_session_hazard.py
python r00_054_a01_chronological_session_hazard.py fit --f44 /mnt/data/source/R00_054_F44_OUT_OF_FIT_COOPERATIVE_ERROR_ARBITER_20261020.zip --original /mnt/data/source/R00_054_FILTER08_FOUR_MONTH_70PCT_OVERFIT_RESEARCH_20261019.zip --out /mnt/data/r00_054_20261026_a01
sha256sum /mnt/data/r00_054_20261026_a01/frozen_models.pkl /mnt/data/r00_054_20261026_a01/frozen_thresholds.json
python r00_054_a01_chronological_session_hazard.py transfer --f44 /mnt/data/source/R00_054_F44_OUT_OF_FIT_COOPERATIVE_ERROR_ARBITER_20261020.zip --original /mnt/data/source/R00_054_FILTER08_FOUR_MONTH_70PCT_OVERFIT_RESEARCH_20261019.zip --out /mnt/data/r00_054_20261026_a01
python r00_054_a01_independent_quota_recount.py
```

The independent quota script has explicit archived working paths at the top; change only those paths if reproducing elsewhere. It intentionally joins June and July event arrays before UTC grouping. The main script's per-source-file `candidate_quota` diagnostic fields are **not authoritative at UTC month boundaries**, especially Coinexx June30 22:00–23:59 UTC; use the independent joint-month recount for all 90%-R9 hour/day/week/month pass/fail decisions. The original F44 baseline should have 0 new R9 quota failures; A01 has 30 new Dukascopy hourly failures.

Original frozen thresholds are committed separately as `R00_054_A01_FROZEN_FEB_THRESHOLDS_20261026.json` (byte-identical original local JSON). Recomputed frozen model pickle SHA256 should be `dbc3a36b1f79441030a50881bc0eb675ab96db4d8490c857673b1e03c0846dd5` in the recorded environment; do not unpickle untrusted files.

The complete original 15-member ZIP with saved four masks, model, reports and manifest has SHA256 `5fb26111e6f8d6ef11310d0979c3dec973a6c3521d63f98d5112c10bd0c3b70a`, but cloud upload failed. This GitHub branch contains exact source/tests/thresholds and results receipt, **not** the binary ZIP or model pickle. A user-accessible local conversation artifact may still hold the complete ZIP. No owner approval, MT5 deployment, economic edge or blind validation is implied.
