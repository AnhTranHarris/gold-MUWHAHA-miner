# R20 source-exact H1V2 broker-adaptive first-passage capacity falsification

**RESEARCH ONLY. NOT A CAUSAL BUY/SELL/WAIT POLICY; NOT AN MT5 EA; NO TRADING APPROVAL.**

Original immutable R9 repaired source HEAD: `ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0`.
Parent R19 full source HEAD: `0c8aaa8430bdd668ab6e8585cb75e702f21b1f9f`.
Parent multi-cycle R18/R19 full evidence in MT5_EXPAND:
- [Original five-volume forensic audit](https://drive.google.com/drive/folders/1ilumXIGt_xiadwsrYtIH5HDopYEw-gcn)
- [R18 source and full research archives](https://drive.google.com/drive/folders/1ChZ3K0mSC64XY3BbhoUWPH-BcQsSFTEo)
- [R19 full source and all 46 original negative 15-minute quarters](https://drive.google.com/drive/folders/12lTCJ04QtCmhnkWOz5RfI94V-y4E8qH7)
- [R20 full 8 source-month lossless source-ordinal archives and append-only crash log](https://drive.google.com/drive/folders/1js4s1eNZ7dXvaaRsB6tBLhg-vqnw3XAP)
- [R20 append-only Google Doc](https://docs.google.com/document/d/1k4f4YQ6_vjZ2S8Erw3HJRaqy8-cpr9JApmMK0iWgjH8/edit)

## Complete new mechanisms, unchanged frozen incumbents

`src/r20_residual_quote_hazard.py` generates six experimental candidate/fill/horizon admission scenarios from actually observed raw quote ordinals only inside R19-S3 unfilled original 15-minute quota buckets. Both sides are independently labeled by offline first +$0.10 net before opening liquidation adverse <=-$0.10, with true bid/ask, frozen nominal $0.02 quote-price cost, source gap/censor, +100/500ms first available quote delayed fill, no future quotes as input admission. The source schedule only adds retrospectively qualifying intervals without changing any R19 original winner interval. Existing booked intervals have R19's 100ms/0slip/cap4, while C5 add-ons assume 500ms/slip20/cap8: **the combined set is not a uniform executable policy**.

`src/r20_isolated_quarter_repack.py` computes exact restricted local quarter cardinality upper by scheduling R19 retained future winners and new R20 chosen candidate futures jointly, ignores interquarter conflicts; it is **not** universal raw-source mathematical infeasibility.

`src/r20_spread_hysteretic_stop.py` independently evaluates BUY/SELL terminal outcomes for 100ms/0slip/cap8 spread, adverse 0.10/0.20/0.50/1.0 USD quote-price or max(0.10,min(1.0,0.25*current_spread)) against +0.10 net in <=60s. Full terminal outcomes STOP/PROFIT/TIMEOUT/CENSORED retained; only future winners are retrospectively scheduled into unoccupied R19 source slots. The original R11 15s favorable full30 zero adverse label is not modified or automatically passed under these alternative stop rules.

The original 2026 Jan/Feb/Jun/Jul eight source-months (four Dukascopy, four Coinexx-linked MT5 historical export) are hash-checked at runtime. Quote values are **integer 0.001 USD/oz**, not cash position P&L. R9 SYNTH UTC reference quotas and 15-minute, 1h, UTC day, month, clipped ISO week are exact. 

## Reproduction prerequisites

These research files intentionally reuse pinned upstream `r18_*.py` and `r19_*.py` source, raw gzip files and binary selected quote-ordinal arrays with original names under `/mnt/data/`. A clone of **this Git branch alone cannot execute the four-month job without recovering the recorded R18/R19 original source and archive dependencies from Drive**, verifying SHA and reconstructing their specified `/mnt/data/` paths. Do not substitute synthetic tick bars or generate replacement quotes. Use Python 3.11, numpy, pandas and numba.

```bash
python -m pytest -q tests/test_r20_contracts.py tests/test_r20_adaptive_stop.py
python src/r20_residual_quote_hazard.py --help
python src/r20_isolated_quarter_repack.py --help
python src/r20_spread_hysteretic_stop.py --help
python verify_r20_source_experiment.py --help
python verify_r20_adaptive_stop.py --help
```

Full 8×11 scenario results, all 43 residual quota failures, 138240+115200 full UTC quarter rows, 34560+28800 hourly rows, 2640 daily rows, 440 month-clipped weeks, all quote ordinal NPZ, full original monthly raw SHA and result member SHA are saved in the R20 Drive folder; archive packages are primary scientific evidence. An independent source quote verifier passed every source-month in each new scenario; Git branch tests use synthetic adversarial fixtures but **do not assert profitable causal trading**.

## Result/status

- Original R19-S3 hindsight quota pass: 14,996/15,042 active source-quarter, 3,831/3,834 active source-hour (two historical feed domains combined).
- C1 only expands to every distinct-ms quote at original cap4, no new future winner and no quota gain.
- C2 cap8 first-60sec & lag100 adds 1 extra retrospectively successful interval but no quota gain.
- C5 cap8 lag500 +20 quote-unit slip per leg adds five historical winners, changes pass to 14,997/15,042 quarter and 3,832/3,834 hour, in a **mixed original/new execution contract**.
- C8 different adverse stop price geometry at lag100/cap8 achieves at most 14,999/15,042 quarter and 3,832/3,834 hour. It is a changed risk contract; 43 quarter and 2 hour targets still miss. Across all independent two-sided trials the aggregate quoted-price outcome is strongly negative. This is not a deployable alpha candidate.

None of the experiments fits a prospective causal BUY/SELL/WAIT predictor, tests broker-reported dealer fills, calculates account cash P&L, verifies actual R9 trail/timeout, or uses blind OOS dates. Do not promote hindsight hit rate to live performance.
