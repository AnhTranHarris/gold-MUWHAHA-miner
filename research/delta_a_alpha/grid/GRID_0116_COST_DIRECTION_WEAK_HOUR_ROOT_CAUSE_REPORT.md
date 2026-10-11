# GRID0116 — Negative-profit root cause: signed directional midpoint displacement vs real source Bid/Ask friction

2026-10-10. Original Delta-A-alpha frozen pre-L1 geometry. **Source-native quantitative decomposition**, not a new trade proposal. Jan–Jul original chronological 57,527,562 Dukascopy quotes. Original GRID0108 K2/K4 event scanner, J0111 causally observed T1, J0114 causally observed T2, GRID0109 immutable month-specific historical weak-hour labels used ONLY for analysis. All 3,332 original weekday baseline hours and 1,389 original weaker-hour cohort retained. No sessions, MTF, trading activation, Martingale or August. J0116 preregistered GitHub before evaluation.

## Exact algebra, checked on every quote

A valid signed quote-side marked return in USD/oz at future observed horizon is exactly:

  source executable net = signed change of source midpoint - 0.5 x source entry spread - 0.5 x actual source exit spread - $0.02 fee.

This identity holds for BUY at Ask, SELL at Bid, and the future actual opposing quote side, no midpoint fills or future choice of sign. Evaluated **6 frozen signal families x 3 horizons x 7 source months = 126 horizon-family-month cells**, with per-month original UTC hour and weak-hour breakdown. Do not call the signed future midpoint a causal prediction: it is an AFTER-ENTRY outcome label measuring why the already elected sign failed.

## Pooled seven-month signed 120-second decomposition

| Frozen entry family | Valid T1/T2 quotes | Average favorable signed midpoint move | Average source two-sided quote friction and $0.02 fee | Observed quote-side net |
|---|---:|---:|---:|---:|
| Original T1 f40 race | 279,311 | +$0.0171 | $0.7989 | −$0.7817 |
| REJECT05 | 140,154 | +$0.0184 | $0.8199 | −$0.8015 |
| FALSE_BREAK_R2 | 41,813 | +$0.0435 | $0.7350 | −$0.6916 |
| FALSE_BREAK_DEEP_R2 | 37,472 | +$0.0481 | $0.7366 | −$0.6885 |
| ACCEPT_STRONG | 169,910 | −$0.0077 | $0.7861 | −$0.7938 |
| RACE_FALSEBREAK_ACCEPTDEEP | 233,719 | +$0.0210 | $0.8008 | −$0.7798 |

**MAIN EXPLANATORY DISCOVERY**: Strongest causal small sampled mean midpoint advantage is about +$0.048/oz and the actual quote friction about $0.737/oz—roughly 15.3 TIMES the midpoint advantage. Filtering/retest confirmation does not fix that gap. Source Bid/Ask friction, especially February, is the binding economic constraint; some cohorts ALSO have negative midpoint drift, especially February in revisit/reclaim.

## Per-month failure pattern on original weak UTC-hour cohort

| 2026 month | Original weak-hour baseline net | FALSE_BREAK_DEEP_R2 weak-hour signed midpoint | FALSE_BREAK_DEEP_R2 weak-hour friction | FALSE_BREAK_DEEP_R2 weak-hour net | Weak hours supported / old weak hours |
|---|---:|---:|---:|---:|---:|
| Jan | −$0.819 | +$0.026 | $0.726 | −$0.699 | 104/207 |
| Feb | −$1.079 | −$0.303 | $1.066 | −$1.369 | 78/160 |
| Mar | −$0.852 | +$0.106 | $0.809 | −$0.703 | 158/203 |
| Apr | −$0.800 | +$0.170 | $0.698 | −$0.529 | 77/179 |
| May | −$0.646 | −$0.089 | $0.590 | −$0.679 | 117/210 |
| Jun | −$0.674 | +$0.087 | $0.613 | −$0.525 | 108/195 |
| Jul | −$0.724 | +$0.123 | $0.647 | −$0.524 | 65/235 |

This rigorously separates two mechanisms of failure: **insufficient signed movement vs source quote fee/spread**, sometimes accompanied by wrong-sign midpoint drift (February and May). Revisited cell is a conditional clue, not a profitable selector or an explanation for every monthly/hourly failure. March, April, June, July show positive sign-side midpoint in some previously weak hours but after actual quote costs still have negative average marked value and often poor support. Beware small filtered cohort and overlapping hypothetical signals. No broker/MT5 fills, no realized NAV/PF/DD/profit or R9 daily opportunity qualification exists in this stage.

## Scientific interpretation

This invalidates any claim that entry timesteps alone or cherry-picked causal stop/target layers rescue the original 120sec sign deficiency. It **does not invalidate** the prior GRID0108 150/150 daily UNSIGNED future-movement uplift or prior GRID0109 1,943/3,332 eligible-hour movement lift. Those are different measurands. Subsequent creative experiments must target forecasting economically significant $ displacement *conditioned on as-of observable state*, not merely accumulating more small grid ticks or deleting failing UTC bins. No calendar/month/hour as signal. Exit quote-cost before promotion, independent unseen data certification needed; August remains sealed. All original data and discoveries preserved.

Public reconstructible inspiration, not XAUUSD proof: https://www.mql5.com/zh/articles/18842 , https://www.tradingview.com/script/UUftcSTg/ ; full bid-ask fill caveat https://www.reddit.com/r/algotrading/comments/1fxtvhv/ .
