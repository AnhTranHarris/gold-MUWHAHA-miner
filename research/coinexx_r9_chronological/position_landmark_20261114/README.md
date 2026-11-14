# R9 v1.94 — Coinexx position-level continuation value, 1s and 3s

Research-only package. The compiled R9 v1.94 EA and the frozen 155-feature LightGBM model are not modified. May–September original R9 positions were observed using ORIGINAL Coinexx ticklogger sources. A scored position must be alive at the quote used for the 1s or 3s landmark; an unobserved quote is never interpolated. Each month is SHA-256/source-ordinal/time/Bid-Ask exact-matched to the existing original R9 ledger.

## Files

- `continuation_landmarks.py` — reads the original 155-feature cache ZIPs, immutable fold model, original trade ledger, and original monthly Coinexx ticklogger gzip; writes only compact **temporary landmark snapshots** and one summary JSON. No market-data rebuild.
- `train_continuation_value.py` — four expanding May→Jun, May–Jun→Jul, May–Jul→Aug, May–Aug→Sep cash-value folds. Compares identical context with and without frozen original P5. Training-only normalization, cost scenario and CVaR sensitivity.
- `day_bootstrap.py` — 200 source-day paired resamples without model refits.
- `test_landmark.py` — five passing deterministic tests for cash quoting, no future price access, original-position survival, stop geometry, and frozen-P5 ablation.
- `R9_V194_POSITION_LANDMARK_CONTINUATION_REPORT_20261114.md` — exact methodology, folds, economic and risk verdict.
- `R9_V194_POSITION_LANDMARK_CONTINUATION_RESULTS_20261114.json` — machine-readable results (no raw ticks).

## Reproduce on existing local original Coinexx source files

The original nine monthly files, frozen `R9_M60_*` cache ZIPs, original LightGBM ZIP, and original R9 candidate cache ZIP must be present under `--root`. No downloads are initiated by these scripts. For this test only May–September original ticklogger files are scanned.

Python 3.11+ and installed dependencies `numpy pandas scipy numba joblib lightgbm scikit-learn`.

```
python continuation_landmarks.py --root /YOUR_EXISTING_SOURCE_FILES --months 5 6 7 8 9 --output landmark_source_report.json --cache-dir /tmp/r9_landmark_small
python train_continuation_value.py --cache-dir /tmp/r9_landmark_small --pred-dir /tmp/r9_predictions_small --output continuation_value_fourfold.json
python day_bootstrap.py --pred-dir /tmp/r9_predictions_small --output day_bootstrap.json --bootstrap 200
python -m unittest discover -s . -p test_landmark.py -v
```

The temporary landmark snapshots total about 8 MB, rather than 72M quotes; delete after verifying the compact output. No source files are overwritten, no MT5 EA is compiled or attached, and no order is placed.

## Important interpretation

The outcome is **original R9 final liquidation cash minus observed EXIT NOW liquidation cash** for *positions surviving the original policy* at the landmark. This is a matched observational payoff, not independent on-policy early exit. R9's future opposite-direction rearms, subsequent entries, account-wide loss governor, broker rejected orders, and real commission/fill prices are **not** reconstructed from this frozen ledger. The `eta * C_rearm` term of the requested equation cannot be identified here: η is explicitly zero in the reported risk sensitivity. A positive short-horizon AUC cannot be substituted for positive after-cost continuation value. No new live control is authorized.
