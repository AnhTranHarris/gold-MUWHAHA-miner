# R9 v1.90 — Entry / Hold / Exit source audit and quantitative research plan
2026-11-13. SOURCE READ-ONLY. NO LIVE DEPLOYMENT AUTHORIZATION.

## Source and research goals
Exact source commit 8729a6345655a7b4ea31facc81982004ee2b8921, path Experts/GoldMuwahahaMiner_R9_HybridGate.mq5, blob SHA-1 7eecb5f1947017a01ce85b2520725de54749e523. Original EA has 461 lines; link: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/8729a6345655a7b4ea31facc81982004ee2b8921/Experts/GoldMuwahahaMiner_R9_HybridGate.mq5

Owner accepts the current research AUC below 0.75 as sufficient to proceed; AUC is not net P&L. Targets: preserve high-volume executed trading, aspirational average AFTER-COST realized P&L >= USD 1.75 per completed trade, and mean hold <=30 seconds. Evaluate all completed trades at 0.01 lot plus full equity/margin survivability, not average winning trade alone.

## Entry trace (source lines 187-238, 251-314, 329-341, 372-402, 405-427)
- At first observed tick of each minute, establish BUY threshold = (Bid+Ask)/2 + $0.15 and SELL threshold = midpoint - $0.15; fixed bracket thereafter until next minute. The entry condition is a level test, not a strict below-to-above crossing. BUY gets priority if both pass.
- Spread <=25 points, completed M5 ATR(14) must exceed session minimum (London 2.00, overlap/New York 1.75, off-session 2.50), except turning off entire regime gate also bypasses spread gate. Session computation presumes broker-to-UTC offset configured correctly; default 0 has not been verified against Coinexx server.
- Complete observed one-second Bid candles form the S1 quality filter: 10 closes, 9 changes; directional efficiency >=0.70, range >=$0.50, signed displacement >=$0.15. Default max turns 9 cannot reject a sequence with at most 8 nonzero sign reversals. Ten observed seconds need not be consecutive wall-clock seconds, so gaps can leak stale evidence.
- Tick-only OnTick callback may coalesce incoming quote events: official MQL5 docs say incoming NewTick events are skipped while an event is pending/running. It is not a lossless feed.
- Market BUY pays actual Ask, market SELL pays actual Bid. Initial BUY SL = current Bid minus max($0.30, broker stops+tick); SELL SL = current Ask plus that distance. No fixed TP. Actual loss-from-fill can be approximately $0.30 plus the entry spread, before slippage/fees, not just $0.30.
- Accepting DONE / PLACED / DONE_PARTIAL / NO_CHANGES as equivalent and recording opened time without confirmed deal+filled volume is unsafe. Position tracking returns only first matching symbol/magic position, not all hedged exposures.

## Hold, exit and lifecycle (lines 316-387, 405-427)
- Tick checks age; elapsed >=30 sec triggers a synchronous market close request. No OnTimer means stale/missing ticks can leave positions open far past their intended lifetime; no timer can guarantee closure when a market is shut. Historical audit includes one ~49-hour weekend exception.
- Trailing becomes eligible only when liquidation-side gain from actual open price >=$0.10. BUY candidate SL = Bid-$0.03; SELL candidate = Ask+$0.03, adjusted for broker min stop+tick and tightened only. Trailing-stop exit can be profitable; stop-exit reason is not a losing-trade classification.
- Freeze level is not explicitly considered, and server retcodes are not reconciled with final stop modifications. Per-tick synchronous position modifications increase callback occupancy.
- At minute boundary StartMinuteCycle resets rearm count and pending state BEFORE position reconciliation. Missing OnTradeTransaction makes fast enter/exit, partial-fill, stop-out and across-minute rearm state uncertain.
- No explicit daily-loss/equity drawdown, margin-aware limits or complete position lifecycle restore.

## Historical evidence and non-equivalence
The preserved Coinexx MT5 M1 Jan–Sep Strategy Tester audit reports 272,352 completed trades, +$360,693.05 tester net, mean +$1.3244 per trade after recorded charges, mean hold 17.24 seconds, after-cost win rate 86.68%, and 192 active trading days (~1,418.5 trades/day). Those are not real-tick or funded-account certification. A +$1.75 mean across the same hypothetical trade denominator would require +$0.4256/trade, ~32.1% more than the synthetic tester reference, before confronting real execution.
The November 13 Coinexx R9/M60 155-feature model scored retrospective May–Sep mean pooled five-second AUC 0.738513 and R9-original-side AUC 0.723175, but its strict utility policy authorized zero positive-utility entries. The later 182-feature quote-pressure additions did not improve average AUC. These are hypothetical action labels at frozen R9 timestamps, not profitable complete EA trades. Preserve exposed-month status. Avoid another sweep of the already failed CUSUM/intensity/pressure classifier variants.

## Advanced quantitative improvement modules, prioritized by direct economic relevance

1. QUOTE-SIDE NET EDGE and causal execution geometry: validate K = account USD P&L per $1.00 XAUUSD price change for actual volume via broker symbol profit calculation. For BUY use exit Bid minus fill Ask; for SELL fill Bid minus exit Ask. Net = K * favorable quote-side move - verified cash commission - actual slippage - swap. Target price displacement from the paid fill to liquidation side is G_req = (USD 1.75 + expected future dollar charges)/K, not a midpoint movement of 1.75. Spread is already paid through quote-side entry/exit and must not be charged again. At all eligible R9 timestamps compute executable BUY, SELL and WAIT utility, not just directional AUC.

2. PATH-DEPENDENT COMPETING-RISK FIRST PASSAGE: Model favorable net-threshold event, adverse stop, and no-hit/time expiry, conditional on as-of state. Cause-specific hazards lambda_plus and lambda_minus lead to survival S(t)=exp[-integral_0^t(lambda_plus+lambda_minus)du] and favorable-first cumulative incidence F_plus(T)=integral_0^T S(u)lambda_plus(u)du. Trailing stops change threshold over time, so include running favorable excursion and current stop state. Estimate probability and CASH payoff within 1,3,5,10,15,20,30s. The existing +0.50/-0.30 barrier AUC work does not establish a net 1.75-per-trade economic target.

3. SEQUENTIAL ENTRY / VALUE OF WAIT: Compare immediate original R9 entry vs WAIT up to a short predeclared (e.g. <=1-3s) causal price/Ask/Bid confirmation and a genuinely shifted entry quote. V(X,t) = max{EU(BUY NOW),EU(SELL NOW),E[V(X_next,t+dt)] - delay opportunity cost}. Include missed trades, fill latency, stop geometry and account occupancy. Never reuse the future label of the original unshifted entry as if it were the shifted-entry result.

4. REGIME-STATE CUSUM AND ORDERED QUOTE SEQUENCES as auxiliary timing states only: CUSUM_plus(t)=max(0,CUSUM_plus(t-1)+DeltaMid/sigma_past-k); use parallel bid/ask updates, spread shocks, quote cadence, confirmed multiscale structural geometry. The prior CUSUM, marked-intensity and Hawkes-like price-only classifier feature additions showed tiny or negative incremental AUC and must NOT be repeated unchanged. Only use these formula families if paired with the different entry-delay or stop-hazard economic target and a prespecified incremental test.

5. DEPTH-TWO PATH SIGNATURES/LÉVY AREA for independent structural timing evidence only: A_ms=0.5 * sum[(m_(i-1)-m_0)*DeltaSpread_i-(Spread_(i-1)-Spread_0)*DeltaMid_i]. This preserves event order of price/spread revisions lost to aggregated indicators. Original R9 path-signature shadow work already exists and some variants failed: do not rerun it unchanged. Test only new objective (shifted fills / stop hazard), predeclared added cost and causal timestamp invariance.

6. CONDITIONAL HARVEST/RUNNER EXIT POLICY: Once position has an ACTUAL confirmed fill, V(x,t)=max{net liquidation now, expected risk-adjusted continuation net}, bounded by <=30sec policy intent, server stop, spread, quote gaps, available volume increments, and tail exposure. This may retain favorable moves longer or exit deteriorating ones earlier; it must beat R9's fixed 0.10 activation/0.03 trailing benchmark under exact tick quote-side replay before any deployment. Partial liquidation cannot be presumed at 0.01 lot.

## Narrow implementation and validation order
(A) Source pin + nonregression fixtures, existing tick engines and saved ledgers reused, no new data export or duplicate archive. (B) OnTradeTransaction fill/partial/close state machine, timer-backed position deadline, DST/server timezone review, stop/freeze checks and account-level circuit breaker on an ISOLATED branch, with compilation and broker-verified reconciliation. (C) Source-exact original on-policy trade replay and feasibility audit of quote-side USD 1.75 achieved before <=30sec while retaining ALL candidate times and chronological account occupancy. (D) Only then implement one action-value/competing-hazard module at a time and a conditional exit mechanism, preserve prior source and negative results, train strictly on earlier months, test future unexposed dates when available, require full-system cost, frequency, latency, drawdown and margin validation. Neither compile nor fresh tick replay was performed for this source audit.

## References
MQL5 OnTick https://www.mql5.com/en/docs/event_handlers/ontick
MQL5 OnTimer https://www.mql5.com/en/docs/event_handlers/ontimer
MQL5 OnTradeTransaction https://www.mql5.com/en/docs/event_handlers/ontradetransaction
MQL5 CTrade Buy https://www.mql5.com/en/docs/standardlibrary/tradeclasses/ctrade/ctradebuy
MQL5 symbol contract properties https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants
Competing risks https://pmc.ncbi.nlm.nih.gov/articles/PMC5326634/
Choi (2026) incremental financial path signatures https://doi.org/10.1002/for.70176
