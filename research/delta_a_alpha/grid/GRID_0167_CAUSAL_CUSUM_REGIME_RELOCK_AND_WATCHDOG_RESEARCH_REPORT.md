# GRID0167 — Online source-quote CUSUM change-point Watchdog and relock

**Date:** October 11, 2026. Scientific parent: J0166. **Active branch:** original `delta-A-alpha`. This document does not replace the complete owner-frozen V1 whitepaper and full governing conversation. Original source/EA unchanged; trading disabled, August sealed.

## Scientific question and preregistration

The owner hypothesizes a stronger regime-aware Watchdog, assisted by completed H4/H1/M15/M5 trend-within-trend, bounded L6 and global L7. Rather than adding another static regime identifier, can a *causally detected transition* decide when to relock an expert or allow a replacement, improving weak-hour performance and gross loss simultaneously?

Public reconstructible source logic—not external profitability evidence:
- MQL5 July 2026 CUSUM structural breakpoint implementation: https://www.mql5.com/en/articles/23043
- MQL5 August 2026 Bayesian Online Change-Point Detection explanation: https://www.mql5.com/en/articles/23482 (NOT implemented here; this cycle uses explicit CUSUM only)

Preregistration **before** running: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/grid/GRID_0167_NATIVE_QUOTE_CAUSAL_CUSUM_WATCHDOG_RELOCK_PREREG.md

Observed genuine source quote T2 midpoint updates once at least 15sec elapsed after last detector update; normalized actual midpoint displacement by twice source spread plus research fee, clipped to [-10,10], dual positive/negative CUSUM recurrence with drift0.5. Fixed thresholds3 and6; causal fresh-change states expire after60 or120 seconds. Per observed source T2, sign either allowed frozen expert B/Watchdog, or relocked to original frozen F. No source future quote, monthly identity, trading profit outcome or future market state enters change-point detection. The observed quote at current T2 is as-of usable state; no instantaneous broker fill guarantee.

## Exact seven-month test

**504 method-month evaluations**, 4/4 new deterministic tests; original J0162 frozen F quote-side per-month counts and means equal at machine precision. Every method preserves **3,332 original reference eligible UTC hours and 1,389 original weak**, with zero-supported hours retained. The full scientific lineage still uses original 57,527,562 Jan–Jul immutable Dukascopy quotes, original 279,486 T1 grid events, original 264,266 genuine T2 observations. May–July repeatedly inspected; NOT independent holdout. August not accessed.

| Source hypothetical rule at T2, cap8, confidence1.0 | Valid quoted outcomes | Previously weak hours supported | Mean BidAsk+fee USD/oz | Gross loss magnitude USD/oz | Months positive after extra $0.50 |
|---|---:|---:|---:|---:|---:|
| Original frozen F | 3,282 | 83 | +3.837 | 19,348 | 7/7 |
| J0162 matured economic Watchdog | 4,905 | 102 | +3.381 | 25,024 | 7/7 |
| Online CUSUM threshold3, 60s; aligned B otherwise Watchdog | **5,523** | **107** | +3.121 | **27,829** | **7/7** |
| Online CUSUM threshold6, 60s; aligned B otherwise Watchdog | 5,200 | 104 | +3.297 | 26,295 | 7/7 |
| Online CUSUM threshold3, 60s relock to frozen F on fresh change | 4,118 | 91 | +3.524 | **21,971** | 7/7 |

**Directional-change admission** adds 618 conditional quote marks over matured Watchdog but gross losses increase $2,805; weak-hour coverage only +5. **Relock-on-break** lowers gross loss by $3,053 versus Watchdog but loses 787 quote marks and 11 weak hours. Worst individual source mark of the leading methods remains around **−$124.82/oz**. Neither result satisfies the strict joint owner objectives. This is not a profitable system certification or small-account survivability result.

Source detector observed 191,623 causal spaced input quote events, with threshold3 registering 19,122 changes and threshold6 registering 4,788. This relatively high change rate may indicate overreactive detector to event sampled quote noise. No use of new data to adjust detector after observing outcomes in this cycle.

## Evaluation limitations and next question

- CUSUM's detected source-event state is **not itself a directional profitability signal**. It may be a useful **Watchdog reset/relock trigger** after independent confirmed regime persistence, completed structural role changes, and realized ticket outcomes.
- J0165 source quote recovery reversal increased gross losses; there is no rationale to invert funded positions automatically whenever a detector fires. L6 must use actual intermediate quote failure + bounded source-side stop and one shared global heat governor, and still survive tail loss constraints.
- All conditional profits are hypothetical source Bid/Ask marks with $0.02 research fee, +$0.50 modeled extra cost, and optimistic same-source-quote execution. Quote signals are not broker-completed trades and the R9 SYNTH 75% same-day qualified velocity objective remains untested.
- **Next suggested J0168 (not executed):** genuinely source-derived *persistence* of regime transitions instead of instant CUSUM events; tick-ordered change lifetime and watchlist relock, with closed H4/H1/M15/M5 direction persistence and observed liquidity/spread cost, combined one account-margined ticket budget. Avoid more aftertest optimization on Jan-Jul; need an external forward/demo or owner-approved holdout later. August remains SEALED.

All exact source code, change event counts, QA and month/day/week/hour panels are archived separately, referencing J0162–0166 original source ZIP; original V1 whitepaper not replaced. **Promotion decision: no new strategy promoted, continue research.**
