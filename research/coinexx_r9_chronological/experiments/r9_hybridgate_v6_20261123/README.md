# R9 HybridGate V6 — Source-preserving Coinexx tick/candle research

**Status:** Heavy January–September 2026 in-sample research; NOT a certified trading EA. No live trading or funded-account claim. Do not merge into main or any approved/production R9 branch.

## Source and rollback

- Exact upstream original MQL5 blob: `7eecb5f1947017a01ce85b2520725de54749e523`, `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`, branch `carson/mt5-r9-hybrid-gate-certification`. Original remains immutable.
- Separate derived EA: `Experts/GoldMuwahahaMiner_R9_TickBridgeV6_Research.mq5`. Research magic 16559, **InpV6EnableTrading=false** by default. Source-original bracket, S1 gate, M5 ATR, session, stop, trail, same-minute opposite rearm remain intact when experimental switches are disabled.
- Research observer: `Include/R9HybridGate_TickCandlesV6.mqh`: tick-built 250 ms, 1 s, 5 s, 15 s, 30 s, M1, M5, M15, H1 completed Bid OHLC, source-order and equal-ms handling, no forward candle content.
- Native source audit: `Scripts/R9HybridGate_CoinexxTickCandleAuditV6.mq5`: bounded CopyTicksRange source streaming with **no order actions**. CopyTicksRange/native MT5 and the externally exported Coinexx TickLogger must be reconciled; an EA's OnTick can coalesce events.
- **MQL5 compilation and terminal replay not performed here**. The clone is source-level research only.

## Exact Python/C++ execution observations (local reproducible package)

- Complete Jan–Sep original Coinexx TickLogger: 72,129,347 chronological quotes, no raw copy in branch.
- Frozen original R9 SYNTH booked targets: 272,352 trades, +$360,693.05 nine-month outcome. This is a stipulated historical learning target, not independently executed real-tick P&L.
- Preserved January independent causal R9 replay: 32,179 trades, -$6,696.70 including the documented $0.02 completed-trade fee. An updated C++17/zlib V6 replay using new completed-candle infrastructure reproduced the preserved January ledger **byte-for-byte** in baseline mode.
- Complete original-causal R9 entry stream Jan–Sep: 303,298 observed trades, net -$65,367.16 including $0.02/closed position. All nine monthly trade counts and net amounts reconcile to archived independent control.
- Crucial source-first-passage finding: from **these same independent R9 entry quote ordinals**, perfect *future-informed* selection of only profitable exits within 30 seconds would total at most +$239,570.39 across nine months, less than the +$324,623.75 aggregate 90%-target requirement. Every month also misses its own 90% criterion under this restricted oracle. It is an offline upper bound **over this fixed set of R9 entry events**, not a limit on redesigned trade clocks or a fundable strategy.
- Therefore stop/trail filtering of original entry events cannot solve the task. New high-frequency source-causal **minute-cycle entry geometry and first/rearm-state policy** is mandatory.

## Strict scientific workflow

1. Read immutable original R9 source and two frozen merge archives; audit R9's minute/bracket/S1/M5 ATR/rearm state machine.
2. Build all candles directly from **original tick sequence** (not SYNTH OHLC, not future source ticks). Include as-of 250ms/1s/5s/15s/30s/M1/M5/M15/H1 state and true wall-clock continuity.
3. Use full nine-month merged outcomes only for historical supervised mechanism discovery and frozen monthly economic benchmarks. **No individual trade ID correspondence quota**.
4. Observe source-specific viable / nonviable entry-to-exit and recovery paths; research multidimensional structural hypotheses, not generic standalone trend/mean-reversion replacements.
5. Modify the R9 minute-cycle bracket/early/late/rearm architecture, then independently replay full actual Coinexx bid/ask ticks in bounded C++17/Python batches with one 2-cent trade fee and no doubled spread.
6. Evaluate EACH month, volume, stopout/cash survival, risk, microsecond/ordinal causality and price-path verification; rejected mechanisms feed the next design iteration. Avoid large duplicate warehouses; preserve only compact receipt/source artifacts.
7. Only after heavy in-sample success, independent **real MT5 Every tick based on real ticks** compile/test to assess terminal-event, broker stop/fill, spread, margin, slippage and forward-test behavior.

## Safety and evidence limits

OnTick does not guarantee delivery of every original tick; native CopyTicksRange validation is mandatory. The C++ engine's default quote-side fills have no slippage, queue, broker stop-level, execution rejection or margin/stopout. 0.01 lot is modeled as one XAU ounce using the original documented source convention, with a $0.02 round-trip fee. Before deployable testing independently reconfirm broker contract size, fee statements, and actual account risk.

**Do not promote this source research branch or turn on the research EA's trading switch until independent MQL5 compilation and terminal parity are passed.**
