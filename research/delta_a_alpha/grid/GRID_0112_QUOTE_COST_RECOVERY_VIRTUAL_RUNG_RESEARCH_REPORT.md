# GRID0112 — Cost-Recovery and Virtual-Rung State Research on Original XAUUSD Bid/Ask Ticks
2026-10-10 Chicago. Research ONLY. Branch delta-A-alpha, following scientific J0111; new preregistration Git commit 1cfd59d68e02ca78a6b06b9a65370de9c184e390. Original J0111 archive: https://drive.google.com/file/d/1hvw_Dr5x3hO5sOzTHPPbxbFJDhKBnv5B/view

## Exact original source and experimental design
Original unchanged Dukascopy JAN–JUL 2026 57,527,562 source quotes, frozen GRID0108 source-code event_scan, GRID0111 T1 K2 RACE f40 first-observed quote; recreated all Jan–Jul T0/K2/K4 lane counts. Cost-friction, prior quote-side T0→T1 price recovery, virtual signed rung count (60/300sec), and recent quote momentum (15/60sec) are computed ONLY from observations known by T1. These are observable state features, not a T0 trade, not L1 session/MTF, not funded Martingale or trade orders. All seven months have previously been inspected; May–July is a chronological secondary diagnostic, NOT a true blind holdout. August remains SEALED.

## Signed quote-path results: 15 variants × 7 months = 105 completed setting-months; NONE positive at any pooled 30, 120, or 600 sec horizon
Source Bid/Ask, T1 entry quote, first actual quote at or after horizon (<=10sec late), opposite quote-side liquidation, subtract $0.02 USD hypothetical 1oz research fee once. NOT actual broker fill or P/L. All 15 tested mechanisms remained negative in **every one of seven months** at each tested 30/120/600s horizon. One current measured bottleneck is that pre-execution quote-state filters can reduce spread friction but also discard most high-volume T1 candidates and fail to solve signed direction.

| As-of T1 state mask | Raw T1 | Retained hours / 3332 | Signed positive hours | 30s avg $ | 120s avg $ | 600s avg $ |
|---|---:|---:|---:|---:|---:|---:|
| NO_NEW_FILTER_REFERENCE | 279,486 | 3,300 | 60 | -0.7865 | -0.7817 | -0.8227 |
| friction_065 | 92,011 | 2,896 | 391 | -0.6853 | -0.6943 | -0.7655 |
| friction_085 | 269,130 | 3,292 | 64 | -0.7594 | -0.7613 | -0.8002 |
| spread_contract_080 | 23,387 | 1,557 | 441 | -0.6667 | -0.6378 | -0.7045 |
| spread_contract_100 | 163,951 | 3,237 | 185 | -0.7485 | -0.7502 | -0.7863 |
| recovered_000 | 39,574 | 2,179 | 425 | -0.7636 | -0.7900 | -0.9209 |
| recovered_minus025 | 190,347 | 3,217 | 143 | -0.6978 | -0.7029 | -0.7591 |
| flow60_agree2 | 61,310 | 2,622 | 463 | -0.8120 | -0.8651 | -0.9827 |
| flow60_disagree2 | 59,311 | 2,615 | 676 | -0.7956 | -0.6882 | -0.6955 |
| flow300_agree2 | 105,599 | 3,078 | 389 | -0.7966 | -0.8498 | -0.9617 |
| flow300_disagree2 | 105,126 | 3,129 | 632 | -0.7726 | -0.6952 | -0.6402 |
| mom15_agree | 168,001 | 3,242 | 181 | -0.7860 | -0.8005 | -0.8630 |
| mom60_agree | 161,875 | 3,204 | 240 | -0.7874 | -0.8124 | -0.8983 |
| friction_085_FLOW60 | 58,549 | 2,605 | 476 | -0.7766 | -0.8503 | -0.9741 |
| friction_085_MOM15 | 161,564 | 3,235 | 193 | -0.7582 | -0.7797 | -0.8486 |

Only descriptive partial advances, not tradable: (i) requiring T1 observed spread contraction <=0.80 of T0 reduces pooled 120s loss to -$0.6378 but retains only 23,362 quote-valid 120s cases and 1,557 supported UTC baseline hours (versus 3,300 for unchanged J0111 K2 race)—a severe activity collapse; (ii) virtual event-flow **disagreement** at 60s/300s modestly lowers mean loss, indicating that treating past virtual-rung pressure as universal continuation is inappropriate. Neither reaches positive expectancy; none promoted.

## Complete monthwise history
| Month | Original quotes | Original virtual T0 | K2 | K4 | T1 K2 race f40 | Native T1 spread $ median |
|---|---:|---:|---:|---:|---:|---:|
| 01 | 9,135,062 | 55,732 | 42,782 | 31,674 | 40,192 | 0.6800 |
| 02 | 7,538,339 | 53,958 | 41,233 | 30,190 | 38,614 | 0.8700 |
| 03 | 9,433,179 | 79,343 | 63,870 | 49,826 | 61,719 | 0.7770 |
| 04 | 7,470,570 | 51,781 | 38,774 | 27,536 | 36,004 | 0.7000 |
| 05 | 8,333,165 | 51,402 | 39,185 | 28,345 | 36,511 | 0.5800 |
| 06 | 8,201,406 | 57,277 | 43,510 | 31,838 | 40,879 | 0.6100 |
| 07 | 7,415,841 | 40,952 | 28,593 | 18,723 | 25,567 | 0.6600 |

Each original month has full JSON result with all variants, costs, valid horizons and day/hour counts; hour/day ledgers include zero-support baseline hours. Complete original baseline eligibility: 3,332 weekday UTC hours. Method groupings by source datetime appear only in analysis, **not** decisions. Source original 181 UTC-day ledger remains in GRID0108 and is not rebuilt.

## Source reconstruction, independent QA and decisions
The J0112 program imports the **unchanged** GRID0111 source; GRID0111 itself imports the original GRID0108 scanner. The source package includes these exact code files and two test suites. GRID0111 prior test set 9/9 PASS; GRID0112 new no-future, spread, cost-recovery-state and no-session tests 4/4 PASS. All candidate masks are boolean as-of T1; output per month is JSON, native-hours CSV, and native-days CSV. Inputs original Dukascopy source hashes and all output files are enumerated in the ZIP manifest.

**DECISION:** No causal positive signed trade mechanism. Do not promote GRID0111 or GRID0112 sign strategies, no MT5 code, no L1/HTF/Vertical L3–L7, no source mutation, no lot scaling, no Martingale. Carry forward the accepted *unsigned* K2/K4 geometry, the new measurable T1 quote-friction and virtual-rung information only as diagnostic features.

## Next high-leverage hypothesis (untested here)
The still-open first-principles research question is **payoff convexity and rejection of quote-cost dominance**, not merely raising count of virtual T0 crossings. Novel grid-native research options: causal state-dependent first-passage competing risk (favorable dollar barrier before adverse barrier), bid/ask spread-change hazard at confirmed T1, virtual unique-cell first-touch/reentry expiration, and as-of churn/quote-arrival intensity. Require test of incremental *signed* expectation and count retention, not only better unsigned movement. Source cannot provide centralized market-by-order depth, so no synthetic volume imbalance. A meaningful positive trade edge may ultimately require owner-authorized future L1 session or MTF structural context, but neither is currently unlocked.

## Public inspiration (concept, not profitability evidence)
- Creator OmegaFX grid: https://github.com/MegaJoctan/omegafx-youtube-shared-files/tree/main/Python%20Grid%20Bot
- Chinese MQL5 confirmation retest: https://www.mql5.com/zh/articles/18486 (opening-time logic explicitly NOT used)
- Japanese MQL5 false-break reversal: https://www.mql5.com/ja/articles/18259
- TradingView reconstructible retest/failed-breakout states: https://www.tradingview.com/script/ZUAYemgd-Supply-and-Demand-Zones-Flux-Charts/
- Reddit quote-side backtesting context: https://www.reddit.com/r/algotrading/comments/1fxtvhv/

## Original reproducibility artifacts
Full tested Python source, both unit-test suites, Jan–Jul month/day/hour outputs, and SHA manifest: https://drive.google.com/file/d/1W5oQMqlJZEeqHpZY_CkHwAYbVxmp_BN2/view (SHA256 a49ac7556abd6b19d74ca86679e6f4498c1b99a994c639cd24a56f60fcb508a6).
