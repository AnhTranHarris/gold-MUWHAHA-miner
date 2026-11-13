# Gold MUWHAHAHA R9 — QRB/QAF feature retention in MT5 (shadow-only)

Status: source-integrated into isolated **research branch**, **NOT trained-approved**, **NOT production deployed**. This change does NOT alter BUY/SELL/WAIT decisions or stops with the default settings.

## Why retain quote-flow features when its matched AUC increment was negative?

Owner explicitly elected to keep investigating the quote-activity analogues of OBV and CMF. In the previously completed five-fold five-second matching benchmark, exact-event trend reached 0.7078 / 0.7181 / 0.7388 / 0.7370 / 0.7266 for May–Sep; adding QRB/QAF scored 0.7076 / 0.7177 / 0.7383 / 0.7360 / 0.7258, a tiny *decrease*, not demonstrated standalone alpha. The overall improvement above AUC 0.6 came from the new counterfactual hazard target and event-time trend. The hard owner gate (AUC >= 0.75, target > 0.80), positive expectancy and high trade-volume criteria still apply before trading integration.

## Modules and configuration

- `Experts/GoldMuwahahaM60QuoteFlows.mqh`: ring-buffered millisecond Bid/Ask revisions; seven 100/500/1000/3000/5000/15000/60000 ms QRB/signed-fraction/spread-pressure/activity features; completed-second QAF on 5/15/60 second trailing windows; CSV telemetry at *existing R9-qualified entry times only*.
- `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`: source-exact R9 v1.90 baseline inherited; adds the optional include, three shadow inputs, initialization, observation, qualified-entry snapshot, and close. **With `InpM60QuoteFlowShadowEnabled=false` (default), no historical data is allocated or file created, and original trading decision/stop/rearm branches execute identically.**
- Enable shadow locally in a dedicated demo/Strategy Tester copy only, not live trading. A per-chart, account+magic-specific CSV is created in MT5 `Terminal/Common/Files/` when enabled. Existing R9 BUY/SELL execution and management are unchanged even when shadow on.
- `InpM60QuoteFlowCapacity` defaults to 32768 event rows, maximum 131072. If more events arrive during 60 seconds than fit, the oldest observations are dropped; the 60-second feature becomes `NA` rather than falsely complete. The history retains one predecessor beyond the 60s lookback when available.
- CSV uses a special `source=ON_TICK_UNVERIFIED_PARITY` field; `NA` indicates insufficient observed quote history. A CSV row is generated after R9 spread/ATR/S1 gates qualify a direction and before the existing order-send attempt. The number of rows therefore depends on old R9 entry eligibility, not all possible market decisions.

## Mathematical definitions

Let $m_j=(bid_j+ask_j)/2$, $s_j=ask_j-bid_j$, and let $j$ index the **observed order** of quote updates, including equal-millisecond events. For an eligible trailing window, let $k$ be the first observed quote with timestamp >= $t-W$ and $n$ the candidate's last observed quote.

- **QRB** = $\sum_{j=k+1}^{n}\operatorname{sign}(m_j-m_{j-1})$.
- **Signed fraction** = QRB / $(1+N_{\uparrow}+N_{\downarrow})$.
- **Spread pressure** = $(N_{\text{widen}}-N_{\text{tighten}})/(1+N_{\text{quote revisions}})$.
- **Activity** = $\log(1+1000N_{\text{quote revisions}}/(t_n-t_k))$ with milliseconds.
- **QAF** = $\sum_{c\in \text{completed 1s bars}} N_c(2C_c-H_c-L_c)/(H_c-L_c)$ divided by $\sum_c N_c$, and zero contribution for a flat second; excludes the current incomplete second.

These are **quote-count proxies**, not actual contracts traded, market buy/sell orders, Level 2 depth, true `iOBV` market volume or institutionally observed aggressive flow. Python source-of-truth is `research/coinexx_r9_chronological/minute60_competing_hazards/src/event_engine.py`. The shadow header matches those equations, not the research classifier. No winning model coefficients or utility thresholds are inserted into MT5.

## Safety and validation before deployment

1. Original MQL5 R9 source SHA-1 (git blob) before shadow addition is `7eecb5f1947017a01ce85b2520725de54749e523`. **Never replace or modify that parent branch or production EA.**
2. Run the Python math/feature contract tests and original 15 research tests. Independent unit tests validate equal-millisecond event ordering, seven lookbacks, QAF completed-second semantics and no invented volume.
3. This environment does **not** have MetaEditor; **MQL5 compile and MT5 broker Strategy Tester parity remain NOT verified**. A change cannot be called deployable or certified until it compiles and completes a non-regression Strategy Tester comparison: shadow OFF must match unmodified R9 trades exactly; shadow ON must match those trades and permit telemetry inspection. Under substantial tick rates, compare event loss versus `CopyTicks` historical replay and measure OnTick latency.
4. MT5 `OnTick` coalesces updates while a prior event is processing. The extra computation/logging can amplify missing events. This implementation is intentionally off by default, with zero trading integration until parity and threshold checks succeed. A dedicated separate tick collector may be needed for lossless microstructure parity.
5. No enhancement is accepted as profitable until *new* unseen time periods pass the owner's AUC>=0.75 gate, after-cost expectancy and high trade-frequency. Historical May–Sep months are development-exposed.

Sources: MQL5 `MqlTick`, `OnTick`, `FileOpen`, `FileWrite` docs. This module is original research code, not copied from external projects.
