# XAUUSD R9 — High-volume PROFITABLE cycle teacher audit

**Research checkpoint:** 15 November 2026. **Status:** ARCHIVED MT5 TESTER TEACHER, **NOT** Coinexx chronological-tick/live certification. **No EA edits or broker orders.**

## The correct source — not the later V9 loss cohorts

- Original MT5 M1 HybridGate trade ledger: `R9_M1_Complete_Trade_Ledger_272352_Trades.csv.gz`, in **MT5_EXPAND**. Source file ID `1Xcm55tJZ6CtQgIbye7I2dnNL6_h_CCLY` and local SHA-256 `d5ecc033cb57e4a0b78ecb09f3a6e7cb3ce7c37ff05bdba0b1149a16cea6c33e`.
- Independent source audit workbook: `R9_Coinexx_MT5_Profitability_And_Trade_Behavior_Audit.xlsx`, Drive ID `1qgbADLGVuvf6K-XICsUdfeLVVhd31zZk`, reporting agreement with the MT5 tester headline. Its source workbook is `MT5_100__M1_GoldMuwahahaMiner_R9_HybridGate.xlsx` (not downloaded, >120 MB).
- Corresponding original *v1.90* MQL5 teacher: `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5` on `carson/mt5-r9-hybrid-gate-certification`, Git blob `7eecb5f1947017a01ce85b2520725de54749e523`.
- **All 272,352 completed MT5 tester trade records read**. No minute/tick library rebuilt. All clock references here are MT5 **broker-server** entry/exit seconds; not independently mapped to UTC.
- Tested symbol XAUUSD, fixed 0.01 lots, reported $100 starting tester balance; these numbers describe the *tester*, not a risk-certified account outcome.

## High-volume PROFIT teacher results

| Teacher-cycle dimension | Observed in archived MT5 tester |
|---|---:|
| Completed trades | **272,352** |
| Trades with net positive tester P&L | **236,079 (86.68%)** |
| **Total tester net** | **+$360,693.05** |
| Active entry-minute cycles | **192,487** |
| **Positive entry-minute cycles** | **178,511 (92.74%)** |
| **Double-entry cycles (initial + opposite rearm)** | **79,865** |
| Second-leg positive exits | **77,686 / 79,865 (97.27%)** |
| **Second-leg accumulated tester net** | **+$161,362.47 (44.74% of total)** |
| First-leg accumulated tester net | +$199,330.58 |
| First loser → second winner (same entry-minute) | **24,592** |
| First winner → second winner | **53,094** |
| Active exit-clock hours with net-positive tester P&L | **4,350 / 4,361 (99.75%)** |
| Active hours with >=50 completed exits | **2,998 / 2,998** positive |
| Active hours with >=100 completed exits | **117 / 117** positive |
| **Positive exit-clock trading days** | **192 / 192** |
| Reported mean active-day P&L | **+$1,878.61** |
| Best recorded exit-clock hour | 2026-01-29 17:00 broker time, **84 exits / +$1,327.13** |
| Best recorded day | 2026-02-02, **2,190 exits / +$11,615.25** |
| Best consecutive positive entry-minute run | 2026-03-19 10:49–19:34 broker time, **526 consecutive profitable entry minutes, 882 trades, +$3,049.34** |

Only **one or two entries per entry-minute were observed**, despite the original configuration permitting as many as three opposite-direction rearms; do not invent a third/fourth executed leg. Of the double-entry cycles, **100% of second entries reversed the first entry's direction**. Median gap between the first exit and the rearm entry: **16 seconds** (p10 **3 sec**, p90 **29 sec**).

All nine calendar months have positive MT5 tester net; the largest is **2026-03: +$75,698.63 on 40,985 exits**, and the smallest **2026-07: +$23,085.85 on 25,277 exits**. Across all nine months, the second leg has >95.8% tester winners and positive modeled monthly net in the archived trade ledger.

## The original *specific* minute-cycle mechanism to transfer

1. **Minute reset:** freeze a buy/sell bracket at the first observed quote of a new minute, ~ `mid ± $0.15` (total width $0.30).
2. **Qualified momentum:** allow BUY when Ask crosses upper bracket or SELL when Bid crosses lower; require completed observed one-second S1 closes (lookback 10) with direction displacement at least $0.15, efficiency ≥0.70 and observed 10-second range ≥$0.50. Also M5 ATR14/session spread gates.
3. **Initial risk:** approximately $0.30 stop from current liquidation-side quote, respecting broker stop distance (the allowed distance may change under real broker rules).
4. **Fast positive profit capture:** once liquidation-side price has moved at least $0.10 favorably from entry, ratchet a trailing stop approximately $0.03 behind Bid for BUY / Ask for SELL, constrained by broker limits; maximum nominal hold 30 seconds (not strictly guaranteed by the original implementation).
5. **Second-leg rearm:** on an observed close before minute rollover, arm **the opposite side**, requalify with completed causal S1 information and execute if its bracket is crossed. Up to three rearms configured, but at most one additional entry actually observed within an entry minute.
6. **Repeat:** new minute, new bracket, updated regime and bounded inventory. The essential trading unit is *first exit + opposite rearm + profit realization*, not a hand-picked single winner.

The archived exit reasons are counterintuitive: **247,411** trades are labeled `stop`, but **212,596** were NET WINNERS and those exits contributed **+$312,340.30** to total tester net. That is the **trailing stop protecting gains**, not initial stopped-out losses. The 24,941 timeout/other exits contributed another **+$48,352.75**. This is why focusing only on stop *counts* in V9 micro180 mislocated the actual profit mechanism.

## Source-verified issues needing certification before claiming profit transfer

The teacher's very high tester profits should not be equated with execution on independent original Coinexx ticks. Original audit flagged companion TickLogger's **SYNTH** run label and explicitly warns against certifying these MT5 profits as real-tick/live. The MQL teacher also has session clock, incomplete-second, fill-response and strict time-out risk-control limitations.

**Limited January 2 quote/time diagnostic:** On 1,083 archived teacher trades, using the original Coinexx January quote file and an *unverified same-clock alignment*, a nearest quote within 1 second could be found for **1,071 entries** and **1,072 exits**. Median absolute difference between tester entry price and same-side original quote was **$0.42/oz**, and exit difference **$0.63/oz**. This is **NOT a valid independent trade replay or an established broker-clock parity check**: quote-side, exact subsecond and server offset reconciliation remain necessary. It is an objective reason not to claim that +$360k is already live-feasible.

No raw tick stream was saved, no orders opened, and no original source modified. The fixed V9 micro180 source is **a different later strategy** and should not substitute for this v1.90 M1 teacher.

## Profit-first next bounded experiment (not a 60-hour settings sweep)

**Teacher→Coinexx original quote transfer** in this order:

1. **Choose fixed positive cycles**, before reviewing real results: a high-volume/economically strong day (2026-02-02), a long 526-minute high-frequency winner run (2026-03-19 10:49–19:34 broker time), and a later-regime ordinary day (e.g., 2026-07-24); add one simple January 2 first-minute audit for quote/server alignment.
2. **Source-clock certification:** reconcile original tester broker times to Coinexx ~ `time_msc`, no assumption that a whole-second deal timestamp proves quote-fill time. Pin symbol contract volume, fee, tick-size, stop/freeze and spread for every test.
3. **Replay the actual cycle**, not just existing V9 entry times: minute-anchored brackets, source-ordinal S1 quality, first executable Bid/Ask, dynamic trailing, opposite same-minute rearm, then next minute. No fabricated 1-second highs/lows or instant fill at a completed candle.
4. **Attribute profit mechanism by leg:** initial breakout P&L, opposite rearm P&L, favorable-to-trailing activation conversion, slippage, stop modify latency and rearm occupancy. Require high per-hour and per-day **net**, not only win rate, across every selected window.
5. **If source-exact replay diverges:** identify the precise causal mismatch (synthetic OHLC path, timestamp alignment, spread, stop placement, fill latency, or rearm state). Transfer the viable cycle component; never force a profitable backtest by tuning ratios on known later prices.
6. **Hard target:** positive complete-system model net after spread+fees; majority profitable completed trades; high turnover (at least 95% of reference *source-clock* opportunity rate where valid); account risk governor active and credible liquidation assumptions. Keep the pre-existing R9 and V9 branches untouched until this is independently evidenced.

**This is the correct profitable-cycle teacher and the next narrow source-exact replay target.**