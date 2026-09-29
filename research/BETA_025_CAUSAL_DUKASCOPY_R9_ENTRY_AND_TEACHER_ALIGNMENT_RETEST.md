# BETA 025 — Causal Dukascopy tick entry retest against repaired R9 teacher cross-feed bridge

**Date:** 2026-09-29  
**Lineage:** independent `beta` research; prior R9/retired Gamma are historical forensic evidence, not build parents.  
**Status:** COMPLETED exploratory entry screen (NOT a trading EA, original MT5 full-entry replay, BETA015 funded replay, or broker certification). August SEALED.

## Sources and reproducibility

- **Original unaggregated Dukascopy XAUUSD bid/ask ticks:** Jan–Jul 2026, **57,527,562** ordered ticks. Reconstructed completed S1 observed-second quality bars and completed M5 Wilder ATR from original ticks; source order preserved for equal timestamps. No invented candles or bar-only fills.
- **Cross-feed clock and teacher source:** existing BETA024 149-day verified R9 REAL↔SYNTH↔OVERFIT ↔ Dukascopy bridge. Jan–Feb Coinexx server ahead of UTC 2 hours; March DST transition; Apr–Jul 3 hours. **165,630** original selected same-minute/same-side/ordinal REAL/SYNTH pairs. This is not the complete **219,342** SYNTH or **236,647** REAL trade population.
- **Historical R9-like control:** one first-cycle R9-origin tick candidate per UTC minute. Original source's completed-S1/M5/session filter copied into causal raw Dukascopy replay, but source-spread research cap $1.20 is intentionally different from native Coinexx R9's ~$0.25 gate; full broker R9 fill/rearm equivalence is NOT asserted.
- Tested **152** source-relative microtiming/direction parameter rules and **85** original R9 eligibility thresholds in January–February discovery; froze bounded subsets and checked Mar–Jul (previously inspected, not truly OOS). Tested **21** combined specialist variants on every month's complete original tick source.
- Quote execution: BUY at observed Ask, exit observed Bid; SELL at Bid, exit Ask, $0.02 roundtrip assumed for one-ounce 0.01-lot position. **Fixed original-event +15s** quote assessment for same-origin timing comparisons, and separately entry-relative +15s; no retroactive entry when a pending rule times out. One-to-one order-preserving ±1, ±5 and ±15s teacher event time matches, side scored after time matching. Teacher data used **only for post-hoc scoring**, never for signal features or execution decisions.
- **QA: 654 assertions passed**, including unit temporal no-future checks, quote-side/fee fixture, one-to-one teacher matching, original hash and parent-count/accuracy comparison against BETA023 on all seven months. BETA005 materialized 17-layer parity unfinished; funded BETA015 accounting not run because this is entry-diagnostic research.

## Historical selected-pair and independent execution metrics (Jan–Jul)

| Candidate | Origin first-cycle count | Positive / evaluable +15s | Positive fraction | SYNTH same-side +/-5s / 165,630 | Mean +15s after-cost markout |
|---|---:|---:|---:|---:|---:|
| R9-like source control | 176,145 | 32,133 / 168,820 | **19.034%** | **32,957 (19.898%)** | -$0.7255 |
| S1 efficiency floor 0.60 only | 191,081 | 34,722 / 182,803 | 18.994% | 33,967 (20.508%) | -$0.7242 |
| Midpoint coherence for ambiguous crossed buy/sell brackets only | 176,785 | 32,270 / 169,386 | 19.051% | 33,290 (20.099%) | -$0.7234 |
| **S1 floor 0.60 + midpoint-coherent bracket** | **191,674** | **34,784 / 183,222** | **18.985%** | **34,394 (20.766%)** | -$0.7236 |
| Above plus 250ms weak-S1 opposing-motion reversal | 191,674 | 35,046 / 183,222 | 19.128% | 33,279 (20.092%) | -$0.7207 |
| Above plus nonstrong-S1 500ms pressure reversal | 191,674 | 35,310 / 183,222 | **19.272%** | 30,779 (18.583%) | -$0.7178 |

**Do not conflate metrics.** Teacher-match-oriented S1 floor0.60+coherent midpoint adds **1,437** same-side source SYNTH matches (**+4.36% relative to the original matched count**) and adds **2,651** positive 15s observations but **decreases precision** 19.034%→18.985% because trade volume increases. Selected teacher same-side match gains on Jan, Feb, Mar, Apr, May, Jun, Jul are respectively **+205, +186, +303, +180, +187, +151, +225**.

Pressure-reversal has the highest same-feed +15s positive-entry fraction of the studied short list but the lowest selected-teacher alignment among these examples. The modest balanced 250ms weak-efficiency reversal improves both aggregate accuracy and teacher count versus control but loses teacher alignment in one month (June). No variant has a positive mean +15s executable markout. No jump toward original R9 SYNTH full-trade historical win rate was demonstrated; that 87.14% tester figure measures a different strategy-lifecycle population.

## Decision, limits, and handoff

**NO PROMOTION.** Preserve source-style R9 first-cycle controls. Retain (i) weakened S1 eligibility with quote-midpoint ambiguous-bracket resolution as a candidate teacher-timing/coverage layer, and (ii) weak-S1 250ms micro reversal as a separately testable post-eligibility timing/direction specialist. Do not merge them into a declared EA winner or optimize exits yet. Direction inversion can look stronger on independent +15s quotes while becoming less correlated with original SYNTH teacher event sides; optimize both metrics separately.

Research portability requires independent original Dukascopy tick discovery followed by authorized native MT5 real-tick EA testing and, when data exist, second-broker validation with point size/contract/commissions/spread/stops/session/quote-age explicit. Unlike a source-identity test, exact Dukascopy↔Coinexx quote/fill equivalence is neither necessary nor claimed.

Further gaps: BETA005 complete multi-layer cached-candle feature parity; full source R9 all-entry rearm, execution and risk replay; fresh out-of-period test (August remains sealed); native MQL5 authorization, compile and multi-broker forward tests.

**Full reproducibility artifact:** `BETA025_R9_TICK_RETEST_REPRODUCIBILITY_BUNDLE.zip` from the BETA025 conversation, SHA-256 `ca65b8f571e338dcd9b101b250ee2ecd5df50f78f96c52bcd393283afb497f70`, includes the raw summary JSON, per-month results, all Python research scripts and 654-check QA script. This ZIP is an attachment **not** stored in GitHub. The controlling local report is `BETA025_R9_ENTRY_RETEST_RESEARCH_REPORT.md`.
