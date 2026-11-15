# R9 v1.94 dual-entry → holding → exit: source-exact forensic audit
**2026-11-14. Audit only — no code modification, retraining, new market files, or deployment.**
Source parent: `3a786ffa0dd4cd1c20348a6fd71811d5e74d4bbf`; dual-entry Python blob `b56ada74360c410ee33b0c07888e9c2d85303e4a`; existing EA MQL5 blob `07222b1a3800c9cc826abe10a4ce6afbd97b0af5`.

## Source-confirmed historical baseline
Frozen January–September source: 72,129,347 actual historical Coinexx Bid/Ask quote records. New four-lane OR entry 419,389 trades, -$162,656.05 modeled after-cost net, $189,771.14 gross realized losing cash, 0/9 positive months, versus old R9 303,934 trades and -$120,212.46 modeled net. K=1 cash per $1 XAU move at 0.01 lots, C=$0.20 incremental cost, both broker-unverified; the original spread is charged through Ask/Bid. All nine months are research-exposed. Partitions use seven-day causal warmups, so the run is NOT guaranteed to reproduce uninterrupted engine state or real MT5 fills.

The new entry was closed with **original** R9 stop, trailing and 30-second timeout; $0.10 and $1.75 NET goals were NOT applied. Of 419,389 trades, **413,464 (98.59%)** ended with `stop` reason (includes both losing initial and profitable trailing stops); **5,925 (1.41%)** timed out. Mean hold about 5.79s. Original-exit final NET >=$0.10 in 14.21%, >=$0.50 in 3.74%, >=$1.75 in 0.293%. These are NOT favorable first-passage or MFE probabilities.

The 15-second basket/15-second breakout lane appeared on **417,806 (99.62%)** accepted positions; the four lanes overlap, so lane-attributed P&L cannot be added or treated as independent strategy performance.

## Fatal or high-risk findings before a cash-exit certification
1. **P0: Cash arms are not exit-only changes.** `ManagedR9._manage_position` only invokes original R9 timeout/trailing for `mode=='original'`. Cash-mode uses the alternative policy and **120-second** stranded hold; stop logic runs, but original 30s timer and 0.03 trailing are no longer equivalent. First freeze the original stop and time management for apples-to-apples comparisons. No completed cash exit study of this new four-lane universe exists.
2. **P0: The v1.94 compiled EA does not implement a persistent 25% capital-equity emergency ceiling or universal $2 cash-stop ceiling.** `GoldMuwahahaR9PortfolioGovernor.mqh` already applies stricter daily gross-loss 4–12%, terminal-local locking and **10% PEAK** drawdown, but the peak anchor is keyed by **date** and can reset daily. Preserve stricter controls; add distinct persistent strategy-start and lifetime peak anchors, account-wide across all positions/agents. The historical nine-month replay did not run a binding governor.
3. **P0: Trailing activation does not guarantee any profit NET.** The original exit activates at +0.10 XAU PRICE move relative to executable entry and trails by about 0.03 price. At K=1 and C=$0.20, if that new stop fills exactly at +0.07 price gross it realizes approx **-$0.13 cash**, before any other slippage or stop-distance widening. A +$0.10 NET floor requires actual liquidation cash mathematics, not pip count.
4. **P1: 5s basket can reset both-side entry permission** while flat, even after earlier opposite-only rearm. It has a four-entry source-minute limit, but still raises turnover. Treat 5s candidate detection separately from 15/30s permission until incremental causal evidence says otherwise.
5. **P1: Observed-second coverage is sparse-sensitive.** Breakout requires 4/8 observed completed seconds and recency <=2s, but not continuous 15/30s coverage. S1 quality uses last 10 observed completed seconds without an explicit actual elapsed-time bound. Add wall-clock coverage/interarrival and freshness.
6. **P1: BUY midpoint spikes can come from Ask widening; SELL midpoint drops can come from Bid widening.** Entry and cash exit must be validated against the liquidation side: future BUY **Bid**, future SELL **Ask**, respectively.
7. **P1: MQL5 OnTick coalesces events** during processing. Source-exact Python processing of every 5s quote may diverge live. Only a bounded, deduplicated `CopyTicks`/catch-up design and demo transaction tests can resolve this, not prettier synthetic M1 reports.
8. **P1: Historical source has LAST/VOLUME/VOLUME_REAL/FLAGS columns but not verified valid traded volume.** Python parser retains these fields, but the dual entry consumes only quote-derived signals. Do NOT label quote count as executed volume, OFI, VPIN, delta, DOM liquidity or actual microprice.
9. **P1: Only original 155-feature entry timings had old AUC estimates.** No old high-AUC model is valid at the new entry timestamps, and owner has deferred it.

## Asymmetric multi-quant signal hypotheses — not backtest-validated
At quote time t, set midpoint `m=(Bid+Ask)/2`, spread `s=Ask-Bid`. Use only past observed completed seconds and side-specific distributions. Let `ER_h=abs(m_t-m_{t-h})/[sum(abs(delta m_u))+epsilon]`, after checking valid wall-clock coverage, and let `sigma_h` be a robust past-only quote volatility scale.

**BUY:** 5s persistence candidate; previous-15/30s *completed Bid-close* breakout `Z_buy,h=(Bid_t-max(BidClose_u))/sigma_h>threshold_buy,h`; spread is stable (shock below conditional limit); closed-M1 plus-DI minus minus-DI and adaptive MA slope are not adverse; quote intensity/gaps acceptable; estimated side-specific first-passage expected **NET cash** after the executed Ask-fill/expected Bid-exit is positive. An isolated Ask-only jump cannot trigger BUY.

**SELL:** 5s persistence candidate; previous-15/30s *completed Ask-close* breakout `Z_sell,h=(min(AskClose_u)-Ask_t)/sigma_h>threshold_sell,h`; spread stable; closed-M1 minus-DI dominance and descending adaptive MA not adverse; quote continuity acceptable; estimated side-specific first-passage expected NET cash from Bid-fill/expected Ask-cover is positive. An isolated Bid-only dip cannot trigger SELL.

No weight, threshold, resulting profitability, or directional superiority has been learned or certified. Fit separate buy/sell/session-specific costs, hazards and gates on earlier chronological samples. A 5s *trigger* should not automatically imply permission to send a market order.

**Competing first-passage objective:** distinguish who hits a realistic **NET** profit barrier (0.10, 0.50, 1.00, 1.75) or adverse barrier (-2.00 or the tighter original stop) **first** before a stated finite hold horizon, with quote gaps, broker costs and slippage scenarios. Then use a conservative lower confidence bound on post-cost incremental cash expectancy to select entry or **ABSTAIN**. AUC is not a substitute for this.

## Hold/exit asymmetry and exact cash geometry
For illustrative `K=1,C=.20`:
`NET_buy(t)=K*(Bid_liquidate(t)-Ask_fill)-C`; `NET_sell(t)=K*(Bid_fill-Ask_cover(t))-C`.
To *observe* +$0.10 NET, BUY needs Bid >= Ask_fill + **0.30 XAU price**, SELL needs Ask <= Bid_fill - **0.30**. +$1.75 NET needs a favorable executed-side movement of **1.95 XAU price**, in addition to entry spread already included by comparing executed sides.

**Fixed-comparator exit arms** (NOT yet tested): (A) original 30-second timeout/trail/stop; (B) first observable >=$0.10 NET -> request harvest without widening any stop or changing timer; (C) at >=$0.10 NET, pursue up to $1.75 **only** after a broker-accepted legal stop protects >=$0.10 in ideal fills *and* validated incremental hold-vs-exit utility is positive, else harvest. (D) optional posterior hazard-based early stop on deteriorating quotes, separately after entry-only baseline stabilizes. The real broker may slip/reject, so cash stops and upper TP amounts are objectives, not realized guarantees. A fixed -$2 realized cash max is impossible to guarantee through price gaps.

**Cash-risk admission:** reject any order whose broker-calibrated `OrderCalcProfit` stop loss + costs/slippage stress exceeds `min($2, remaining daily gross budget, remaining lifetime peak loss budget, remaining 25%-from-start capital budget)`; don't widen original tighter protective SL. All account risk anchors must persist across restarts and participating terminals, include floating losses and commission, and flatten/reject if any stricter limit trips. Independent 25% cap is not permission to loosen existing 10% peak governor. A $0.10 win vs $2 loss needs 95.24% wins under the oversimplified fixed-two-payoff assumption; $1.75 win vs $2 loss requires 53.33%: real net expectancy depends on actual win/loss magnitudes and adverse fill tails.

## Native MT5 indicators vs Coinexx feasibility
| Signal | MT5 indicator | Source status / approved proxy |
|---|---|---|
| Higher-frame range and tradeable volatility | `iATR(PERIOD_M5)`, `iATR(PERIOD_M1)` | Bid-OHLC **available from original ticks**; must match closed-bar alignment, seeding |
| M1 directional regime | `iADXWilder` and +DI/−DI | Bid-OHLC available; ensure exact Wilder indicator parity rather than silently substituting `iADX` |
| Trend adaptation | `iMA(MODE_EMA)`, `iAMA`, `iFrAMA` | Close M1/M5 source available; use only closed bars, quote-only subminute efficiency is a distinct feature |
| Consolidation/volatility | `iBands`, `iStdDev`, `iRSI` | Bid-bar series available; a 5s/15s indicator must be custom, not nonexistent native timeframe |
| Tick activity | `iVolumes(...,VOLUME_TICK)` | Actual source quote-row intensity is available, not necessarily identical to broker iVolumes |
| MFI/OBV/VWAP/OFI | `iMFI(...,VOLUME_TICK)`, `iOBV(...,VOLUME_TICK)` | Only **tick-count proxies**, no validated real-volume VWAP, no true signed order flow or market depth; use spread shock, Bid/Ask change synchronicity, quote-rate variation as correctly labeled alternatives |
| Real DOM | `MarketBookGet` if broker offers market depth | **NOT in historical Coinexx quote data**; live DOM cannot be reconstructed from Bid/Ask alone |

Official API validation: https://www.mql5.com/en/docs/indicators ; https://www.mql5.com/en/docs/event_handlers/ontick ; https://www.mql5.com/en/docs/series/copyticks ; https://www.mql5.com/en/docs/trading/ordercalcprofit ; https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants .

## Next gate
Do **not** repair outcomes by retuning all indicators. The minimum next research is a compact **on-policy original-source per-position path audit**: buy/sell separately, quote-side MFE/MAE, first-hit timing/hazard, initial vs trailing vs timeout stop cause, spread/gaps, protected-stop legality, session volatility and conditional hold-minus-harvest utility at 1,3,5,10,15,30 seconds. Reuse the original exact Coinexx source parser; emit only compact trade summaries, NEVER duplicate monthly ticks, Dukascopy or the 155-feature library. Independently evaluate a small predeclared entry-veto set with the original exit, THEN exit arms with identical entry chronology. Freeze and test later untouched data before MT5 promotion.

**Verdict:** Existing four-lane OR entry **FAILS** economic baseline. New cash-hold design is **UNVALIDATED** and its legacy simulator comparison is confounded. Engineering direction: 5s observation → 15s structural validation → 30s executable-side persistence, selective cash-aware harvesting, optional evidence-backed protected runner, strict per-trade and account-global risk controls. No live promotion or MQL5 rewrite authorized by this audit.
