# MICRO180 V16 — full-population R9 entry reconstruction (research-only)

**Scope: ENTRY ONLY.** Does not change original R9/MICRO180 EA, protective governor, trade holding strategy or broker execution. The entire original SYNTH R9 target population is retained: 192,487 first legs + 79,865 second legs = **272,352**, instead of V13/V15's hindsight-positive-only targets. No future target, trade net or A/B/C label is available to the online entry model.

## What is built

- `v16_full_teacher_bridge.py`: frozen-target loader, separate first/second clocks, 27-dimensional causally observed market-state vector and independent LightGBM entry controller. It reuses V14's forward-only Kalman local-linear filter, real observed minute bracket, completed 10/60/300-second displacement, 10/30-second efficiencies, realized volatility, causal intraminute high/low, completed M1 close slope and 5-minute structure. BUY executes at actual later REAL quote **Ask**, SELL at actual later REAL quote **Bid**.
- `v14_causal_synthetic_wave_entry.py`: preserved V14 online quote clock with an **optional** `require_touch_gate=False` for V16 supervised decision authority. The observed Brownian first-passage forecast remains an input feature, not a compulsory rejection filter. One quote-second lookahead is forbidden; every decision becomes eligible on a **later source quote**.
- `v16_train_and_replay.py`: direct streaming reader for a preexisting original REAL TickLogger `.csv.gz`, January 2026 chronological quote-row training/validation/holdout split, separate LightGBM models, validation-only threshold choice, original fixed position management for independent opposite rearm, full teacher entry comparator. Creates **two compact frozen model files and one metrics receipt**; it does not persist or rebuild raw quote data.
- `test_v16_full_teacher_bridge.py`: independent entry/quote eligibility contracts.

R9 SYNTH is treated as a **teacher for event identity/timing**, never as a source of executable future prices. The Coinexx REAL TickLogger event stream is the model's only observed quote state; teacher timestamps and prices are used offline for training and scored *after* the independent replay. The learned clock can approximate the SYNTH schedule but cannot deterministically reconstruct its past artificially generated intraminute OHLC trajectory from real quotes.

## Entry mechanisms, in formula form

- **Carry-over memory:** `s * [mid(t) - mid(t-h)]` for `h ∈ {3,10,30,60,180,300}` seconds; completed M1 and prior five-minute structure are included, without waiting for a new 5s or 15s current-minute bar.
- **Real minute breakout anchor:** `d_s = real_mid_at_first_quote_of_minute + s·15 cents`; the actual side-aware executable margin is `s · (BUY_Ask_or_SELL_Bid - d_s)`.
- **Latent-price reconstruction:** forward two-state local-linear Kalman filtering estimates latent price and signed velocity; no final/current M1 future extremum used.
- **Synthetic first-passage proxy:** drifted Brownian threshold probability from as-of latent gap, estimated variance and time remaining in minute; *a probability feature only*.
- **Generator-phase clock:** side/leg empirical conditional timing from original teacher entries; trained on Feb–Apr for the limited January REAL replay to exclude January clock labels from prior fitting.
- **Competing first/second entry heads:** separate LightGBM models trained on **ALL original trades** for observed candidate source seconds. The second controller is only permitted after its **own** first trade is observed closed in the frozen research harness.

### MT5 proxy implementation plan (not yet compiled)

The 27 features map to native `CopyTicks`, `iATR(PERIOD_M5)`, `iADXWilder`/`iADX` as optional context, `iMA` completed-bar slope and custom bounded completed-second quote ring / causal Kalman updates. The new entry controller is **Python research only**. No unsupported claim of MQL5/MT5 parity or live broker order qualification.

## Source and exact measured narrow replay

- Original merged reference SHA-256: `9c9ebf5889c309a10e4370e355b99d75ae54cf5ccfdaa5ebab9042206f3f8cc5`, 11,233,746 bytes, 272,352 targets (all outcomes).
- Direct read-only original TickLogger: `GoldMuwahaha_R9_TickLog_REAL_TESTER_20260101_000000_part01_of_10.csv.gz`, 94,307,288 bytes, SHA-256 `ae07db47b48b49695c6de47927171d7cf8c7bc28a85370d87d48957e2a20506e`.
- Experiment confines itself to **first 400,000 original quote rows**: 150,000 train, 100,000 validation, final **150,000 later rows** as independent quote-order evaluation; teacher clock fitted on Feb–Apr, therefore **not a strict historical end-to-end walk-forward backtest**. Never extrapolate these counts to all January or all nine months.
- Later source window: **531 teacher entry references** (382 first, 149 second); V16 independently produced **791** entries (500 first, 291 second), **498 same minute/leg**, **334 same direction**, **41 within ±2 seconds and ±5 cents**, **28 exact mapped quote matches**. Causal independent entry prices are observed source quotes, not guaranteed broker fills.
- Final untouched test-period quote matching is modest, but measured against the user's **correct full R9 entry target** for the first time with the Kalman/1–5m/clock interface actually driving entries. More data and cross-month generalization work remain; V16 is not release-certified.

## Reproduce without rebuilding source data

```bash
python -m unittest -v test_v16_full_teacher_bridge.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 python v16_train_and_replay.py \
  --merged /EXISTING/r9_synthetic_teacher_to_original_REAL_TickLogger_9m_trade_marks.csv.gz \
  --ticks /EXISTING/GoldMuwahaha_R9_TickLog_REAL_TESTER_20260101_000000_part01_of_10.csv.gz \
  --out /TEMP/compact_v16_result --train-end 150000 --valid-end 250000 --max-rows 400000
```

The saved files `result/v16_teacher_leg1.txt`, `result/v16_teacher_leg2.txt`, `result/v16_priors_febapr.json`, and `result/v16_full_entry_receipt.json` are small research outputs, not source data. They are included in the deliverable ZIP. Input source files themselves are **not** in the ZIP.

**Next engineering step:** determine which latent-phase and prior-minute structural features raise independent matched-second/quote-price recall on a larger source-ordered test without leaking R9 teacher events into the decision clock. Preserve the held-out comparator, keep all 272,352 original entries as target population, and promote no holding/exit redesign until entry transfer improves.