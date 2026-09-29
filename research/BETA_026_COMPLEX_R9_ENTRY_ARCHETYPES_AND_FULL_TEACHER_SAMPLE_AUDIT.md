# BETA 026 — Complex R9 missed-entry strategies: original Dukascopy tick test + original teacher sample

**Date:** 2026-09-29. **State:** COMPLETED research diagnostic, NOT approved BETA EA or funded BETA015 simulation; August SEALED. **Lineage:** beta only; R9 REAL/SYNTH/OVERFIT and previous Gamma studies are historical reference, not inherited EA code.

## Scientific evidence of SYNTH misses

Historical R9 REAL↔SYNTH selected same-minute/same-side/ordinal pairs **165,630**: median |entry time difference| **10.115 sec**; 72.312% >5 sec; REAL earlier 47.247% / later 52.740%. S1 displacement correlation **0.8705** vs completed-S1 path efficiency correlation only **0.0236**; just **54.672%** are first cycle on both original logs. Difference is sequence/order, second-level movement quality and repeated-entry ownership, not merely shared M1 OHLC or ATR. Causal future timing cannot be known from the synthetic teacher.

## Source-based reconstructible mechanisms

MQL5 Chinese completed-bar liquidity sweep (https://www.mql5.com/zh/articles/18379); Japanese MQL5 sequential breakout→retest confirmation (https://www.mql5.com/ja/articles/19968); open-source TradingView liquidity sweep→CHoCH/structure change (https://www.tradingview.com/script/HCXJM3dW-CHOCH-Liquidity-Sweep-Detector/); Korean open-source sweep+EMA+BOS (https://kr.tradingview.com/script/iueqDnDD-13-EMA-Breakout-Liquidity-Sweep-BOS-Confirmation-A-A/). These explain deterministic ideas, NOT demonstrated XAUUSD profitability. Tested reconstructed causal **sweep/reclaim/MSS/range fade/multi-specialist direction masks**, micro-delayed pending-entry FSM, conditional same-minute bracket recross/reset opportunities, transparent shallow decision-tree direction router. An elaborate full sweep→FVG→retest stack was identified as future hypothesis but NOT separately tested in this checkpoint. No claim of exact vendor-script reproduction.

## Method

**57,527,562** original ordered Dukascopy XAUUSD Bid/Ask quotes, Jan–Jul 2026. All S1/M1/M5 context derived from original tick sequence, only completed bar state usable; all candidate market fill prices original observed Bid/Ask with 0.01-lot one-ounce 0.02 USD commission assumption; horizons +15 sec observed quote max 2s next-quote freshness. JAN–FEB explored **242** static/FSM/reset/tree combinations, frozen selected mechanisms checked Mar–Jul, which are already inspected historical data and NOT blind OOS. Synthetic teacher clocks posthoc matching only, never decisions. BETA025 first-cycle R9-like control remains source-nonparity owing to $1.20 relaxed spread vs original Coinexx R9's 25-point cap, and omission of actual exit-enabled rearm / full fills. BETA005 17-layer source cache certification incomplete. Not a BETA015 prop-capital replay.

## Seven-month results, selected historical same-side R9 teacher pair cohort

| Raw-tick entry model | Markers | +15s positive/valid | % correct | SYNTH same-side ±5s on 165,630 pre-pairs | Mean entry+15s USD |
|---|---:|---:|---:|---:|---:|
| Existing E060 1-entry firstcycle | 191,674 | 34,784/183,222 | 18.985% | 34,394 | -0.7236 |
| weak S1 + 250ms reversal | 191,674 | 35,046/183,222 | 19.128% | 33,279 | -0.7207 |
| sweep OR MSS structural flip | 191,674 | 35,029/183,222 | 19.118% | 32,517 | -0.7212 |
| microstructural + regime multi-specialist V2 | 191,674 | 35,008/183,222 | 19.107% | 33,099 | -0.7208 |
| up to 2 reset events/min, 10s cooldown, $0.30 bracket recross, S1 eff ≥0.70, either side | 235,694 | 43,744/226,464 | 19.316% | 41,670 | -0.7216 |

The selected-pair multi-event +**7,276 SYNTH matches** is **NOT unbiased full original-SYNTH teacher recall**; its source subset was preselected as SAME minute and side, plus more independent signals mechanically increase overlap. Multiple markers can overlap positions; NO real sequential account/EA settlement simulated. All average after-cost markouts negative. Static routes lost correct July entries; no strategy promoted.

## CRITICAL source-bias falsification: ALL original R9 source entries on four complete days

To correct the selected-pair bias, independently read original R9 REAL+SYNTH 31-column **full daily** log files on 2026-01-02, 02-20, 05-20 and 07-20. Original all-entry markers **SYNTH 5,105**, **REAL 6,192**. Same clock adjustment established in BETA024: Coinexx server UTC -2h Jan/Feb, -3h May/Jul. Deterministic 1-to-1 order-preserving timestamp match ±5s, side assessed AFTER matching:

| Four complete sampled market days | Dukascopy first-entry | Dukascopy two-event candidate | Change |
|---|---:|---:|---:|
| Independent entry markers | 5,103 | 6,142 | +1,039 |
| **ALL ORIGINAL SYNTH** side-matched | **1,022** | **1,102** | **+80 (+7.8%)** |
| **ALL ORIGINAL REAL** side-matched | **2,976** | **3,855** | **+879 (+29.5%)** |
| Independent Dukascopy correct/valid +15s | 629/4,814 (13.07%) | 826/5,833 (14.16%) | positive fraction +1.09pp |

All four sampled SYNTH matched-event increments positive (+18,+15,+31,+16), but original REAL increments much larger (+233,+147,+294,+205). July sampled 15s correct fraction fell 12.052%→11.838%. Therefore the BETA025/026 selected-pair clock gains **mostly reproduce original R9 REAL extra entry/rearm activity**, not the desired synthesized timing. Source matching over ALL **149** daily original teacher streams remains **INCOMPLETE** (four day sample only). Treat sample as falsification of overclaim, not proof of all-month performance.

## Conceptual MT5 mapping — research plan ONLY, not authorized EA code

`OnTick`: update raw quote clock, completed S1/M1/M5 features; R9 bracket event `candidate_id`; maintain state `BREAK_EXTEND / SWEEP / RECLAIM / MSS / CONFIRMED / EXPIRED` only after observed ticks; specialist activates at its own first eligible observed tick, never retroactively; original stop/fill/position state must be reconciled before allowing same-minute rearm. Per-broker point, digits, spread, session, commission and contract values are explicit. Full original SYNTH **unselected** entry timing/side/recall and cost-adjusted Dukascopy correctness are separate scientific gates. Next reconstruct full chronological single-position ledger under BETA015 when funded simulation is requested, and full original 149-day source event matching for unbiased teacher attribution. Do not promote a strategy on count inflation or a selected teacher label.

## Reproduction and QA

Full BETA026 local bundle `BETA026_COMPLEX_ENTRY_CAUSAL_RESEARCH_BUNDLE.zip`, SHA256 `fb95c0f3b7396a35ae322ff061c26dfe0e697ba70f626e7ebfd44ff51fb730e2`, contains 30 source/results files plus SHA manifest, including scripts to derive tick-level source features, FSM, same-minute opportunity scanner, Jan–Feb trees, four original-source day audit, and QA. Original user-owned large tick source bytes intentionally not bundled. **2,275 assertions PASS** including seven-month first-cycle BETA025 source parity, all-original 4-day one-to-one matching, no retroactive confirmation, and teacher-independent signal signatures. No MT5 EA code or broker deployment; August SEALED; approved_beta_ea=null.
