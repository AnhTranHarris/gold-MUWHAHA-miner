# R9 Micro180 v3 asymmetric quant overlay — controlled research

**Branch: `carson/r9-micro180-v3-quant-objective-audit-20261114`. Research only.**
This adds `asymmetric_v3.py` as an **opt-in** layer on the existing R9 Micro180 fork. It does not overwrite the original R9 .mq5, alter source data, train the old high-AUC model, or promote demo/live trading.

## Layered design
1. Original ms-ordered 180s ring and 5s/15s baskets (no fabricated seconds).
2. Original executable Bid-side BUY and Ask-side SELL 15s/30s breakout and cross-clock rearm.
3. NEW optional separate BUY/SELL quant score based on **signed executable-side directional efficiencies for 5, 15, 30 and 180 seconds**, fraction of simultaneously advancing Bid and Ask completed seconds, realized quote-intensity ratio (labelled a PROXY, not transaction volume), spread shock relative to recent completed quotes, overextension beyond completed 180s range, and closed M1 EMA/DI bias if present.
4. Existing cash objective: >=$0.10 modeled net liquidation => first harvesting opportunity; $1.75 preferred model close threshold; no intended $2 risk more than available stop/first quote can realize. Default protected continuation OFF; the overlay score is NOT an empirically calibrated hold-utility probability.
5. Existing account governor ON unless researcher explicitly disables it. Stricter daily and peak controls are retained. No claim of cross-terminal governor consistency.

**Predeclared untrained BUY score:**
`S_B=.28*ER5+.27*ER15+.15*ER30+.06*ER180+.16*BidAskCoMove+.08*(QuoteRateRatio-1)+.10*M1Bias-.25*SpreadShock-.12*ExtremeExtension`.
**SELL:**
`S_S=.25*ER5+.28*ER15+.17*ER30+.07*ER180+.16*BidAskCoMove+.08*(QuoteRateRatio-1)+.09*M1Bias-.29*SpreadShock-.12*ExtremeExtension`.

Each `ER` is signed direction-consistent efficient displacement of the **liquidation quote** (BUY Bid; SELL Ask) divided by its observed absolute quote travel. Neither score is a fitted probability. Distinct coefficient values are hypotheses only; the research must test both directions and session segments separately.

## Reproduction without new data files
```bash
python research/coinexx_r9_chronological/micro180_20261114/run_asymmetric_v3.py \
  --ticks /EXISTING_READONLY/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz \
  --limit 150000 --output /tmp/asymmetric_v3_smoke.json
python -m unittest discover -s research/coinexx_r9_chronological/micro180_20261114 -p 'test_*.py' -v
```
Use `--limit 0` for an entire source file, only when intended. `--expected-source-sha256` optionally requires a matching original archive SHA. No raw tick outputs.

## Objective and hard rejection gate
Frozen original R9 Jan–Sep benchmark: **303,934 trades** and **-$120,212.46 modeled cash**. Existing selective Micro180 research benchmark: **61,258** trades and **-$24,158.30** modeled cash, 0/9 profitable months, research governor OFF. The latter DOES NOT satisfy high-volume or positive NET performance. The existing additional 150,000-quote profile diagnostics showed 274, 797 and 969 trades with negative cash for progressively relaxed filters; reversing sign also lost money. These are IN-SAMPLE partial-source diagnostics, not month performance.

The v3 overlay must be tested on fresh source chronology against the same configurations and correct cash fees, with a *simultaneous* objective of >= original R9 completed trade count, strictly positive after-cost net per validation month and no severe per-trade/account losses. Do **not** force a threshold selected on these nine repeatedly inspected months and call it independent OOS. A feature with negative net cannot be “repaired” merely by increasing volume or cherry-picking the best month. If feasibility fails, report **NO PASS** and do not deploy. Account-sized constraints can make the desired throughput infeasible.

## MT5 indicator interface and parity blocker
The existing **separate demonstration-disabled MQL5 fork** already uses `iADXWilder`, `iMA` EMA, `iATR` M1/M5 and source-tick `CopyTicks` with equal-ms cursor. This v3 Python-specific overlay does **NOT** have verified native-MQL5 score parity. It must remain research-only until code parity, real MetaEditor compiler results, broker OrderCalcProfit/commission, terminal CopyTicks catch-up, fills and slippage have been checked. Old R9 version and legacy MODEL155 unchanged.

**No claims of optimized profitability, MT5 compilation, or guaranteed $2 cash floor.**
