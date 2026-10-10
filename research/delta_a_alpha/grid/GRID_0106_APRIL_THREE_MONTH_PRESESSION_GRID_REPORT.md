# GRID-0106 — April added: three-month original-tick grid physics research

**10 October 2026 · Pre-Vertical Grid, no session intelligence, no trades · Discovery-tier candidate, not financially validated trading edge**

## Owner mandate

Advance beyond small metric improvements; use April as an additional original Dukascopy XAUUSD month while keeping GRID-0103→0105 creator-derived inventory-free virtual-grid lineage. Do not activate Sydney/Tokyo/London/New York session adaptation, HTF/MTF or other Vertical Grid quality layers until grid opportunity/direction reliability justifies it. $100,000 is a **future** hypothetical funded research account; no capital is deployed in this shadow study. No Martingale lot escalation, physical buy-against-loss inventory or future-data signals.

## Original market surfaces (SHA-256 checked, source files read only)

| Month | Source-chronological Bid/Ask quotes | Exact gz SHA-256 | R9 Gamma HybridGate SYNTH monthly entries |
|---|---:|---|---:|
| January | 9,135,062 | `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5` | 27,980 |
| February | 7,538,339 | `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d5` | 33,523 |
| April | 7,470,570 | `30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f` | 31,758 |
| **Total** | **24,143,971** | | **93,261** |

Original files: `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`, `..._02_...`, `..._04_...`; prices integer 1/1000 USD. R9 benchmark comes from the existing immutable `research/delta_a_alpha/benchmarks/R9_REAL_SYNTH_JAN_JUL_2026.json`. R9 entry signs are **not** labels of correct direction. April has now been inspected for refining research and is **not a pristine future lock-box**.

## Mechanism and research questions

Use GRID-0104 causal virtual price anchors: when mid crosses gap `max($0.75,1.5×as-of EWMA(0.001) Bid/Ask spread)`, emit at most one unique event every 7 seconds. The **event price anchor advances irrespective of whether a physical trade could be opened**; this is progression memory rather than losing-grid accumulation.

At each event at `t` compute solely as-of displacement (last observed quote at or before `t-300 seconds`) and contemporaneous spread:

`K5(t) = abs(mid(t)-mid(t−300s)) / max(Ask(t)−Bid(t), 0.10)`.

**New combined hypothesis:** **two event tiers** with a single price-cell event clock:
- **K5≥2 breadth tier:** retain enough nonduplicate candidate information to support the owner's volume ambition.
- **K5≥4 high-motion tier:** a *subset* of breadth tier, indicating stronger already-observed motion per unit of friction; does not prescribe BUY, SELL, hold, exit or position count.

This is not the same as using the strict tier alone. In a source-month-specific January *offline evaluation*, the strict tier attained the **raw** daily 75%-of-SYNTH entry-count comparison on only **11/21** benchmark dates, while the breadth tier attained **21/21**, under unverified provisional **UTC+2** report-time normalization. Neither is the owner’s final **qualified and executable** trading acceptance result. February and April have monthly R9 trade-count references but not certified per-day corresponding entry ledgers in this experiment.

## Three-month causal evaluation

Metric: At a candidate event, ask whether absolute midpoint movement to the first available market quote 120 seconds later (within 10-second quote tolerance) exceeds **two times the observed entry spread**. Future observations are for measurement **only**, never model inputs. No commission/slippage/stop/fill/hold optimization; even a valid movement outcome does not establish an actionable correct direction.

| Metric | January | February | April |
|---|---:|---:|---:|
| GRID-0104 source-event count, before horizon check | 55,732 | 53,958 | **51,781** |
| Breadth-tier `K5≥2`, horizon-valid events | 42,729 | 41,177 | **38,740** |
| High-motion-tier `K5≥4`, horizon-valid events | **31,648** | **30,159** | **27,527** |
| R9 SYNTH monthly entries | 27,980 | 33,523 | 31,758 |
| Strict-tier monthly count / R9 entries | **1.13×** | **0.90×** | **0.87×** |
| Base all-events future 120s capacity | 62.17% | 61.79% | **59.00%** |
| **Strict-tier future 120s capacity** | **67.68%** | **66.38%** | **64.32%** |
| Strict-tier absolute uplift | **+5.52 pp** | **+4.59 pp** | **+5.32 pp** |

Daily-block paired comparisons versus unfiltered same-day grid population (source-positive UTC quote days with >=100 baseline horizon-valid events):

| | January | February | April |
|---|---:|---:|---:|
| Days improved | 22 / 23 | **22 / 22** | **25 / 25** |
| Equal-weight mean **daily** capacity uplift | +4.435 pp | +4.246 pp | **+5.146 pp** |
| Descriptive 95% day-resampled interval | [+3.255,+5.669] pp | [+3.243,+5.360] pp | **[+4.381,+5.925] pp** |

These descriptive resampled intervals **do not correct for hypothesis screening/selection bias**, overlapping 120s labels or reuse of months during research. The higher capacity is partly **by design** because a stricter recent-motion threshold preferentially selects more-active conditions. The result is repeatable *feature discrimination*, not a money-making or prediction breakthrough.

## Direction and capital reality

Within the grid-only research scope, 14 explicit direction choices (creator reversal, crossing continuation, prior 15/60/300s drift, fade, agreement, countertrend pullback) across forward horizons 30/120/300/600 seconds were evaluated on the original entry/exit Bid/Ask sides. **None established stable positive average executable-side markout across all three months**, even prior to commission, slippage and actual fill uncertainty. No candidate trade is opened; no equity, win-rate of closed positions, PF or R9-level net profit is measured. Do not confuse a 64–68% two-sided *movement magnitude* measure with a 64–68% trading win rate or direction accuracy.

A parallel self-normalization experiment varied tier threshold using **only the prior hour’s event density**, testing seven threshold cutoffs and three gradual formulas. The April raw counts remained high, but these density switches did **not** improve the cross-month movement-quality/velocity frontier against the simple nested tiers. They remain research hypotheses, not promoted mechanisms. No session clock or calendar month label is used as a trading feature.

## Research promotion decision

**Retain as stage-zero scientific information:** one causal virtual event clock, cost-aware spacing, virtual rung genealogy, two **nested** as-of motion/friction tiers, and source-observed forward outcomes for eventual direction-quality research. **Do not activate session-aware geometry** or register the high-motion tier as a completed strategy. The breakthrough is that April independently exhibits similar within-grid **movement-capacity stratification** after the prior January/February observations, while the broad tier remains available for velocity. It does **not** satisfy the owner's final qualified/tradable daily volume requirement, let alone R9 economic outcomes.

**Next harder gate:** build a pre-session grid-only direction/abstention *causal* policy that demonstrates **positive after-Ask/Bid quote-side expectation** on a new time partition and maintains the owner's real trade-velocity floor, with latency stress and one future shared $100k research account only after whole Vertical Grid integration. Do not apply a preferred direction learned from future outcomes or retroactively optimize by April dates.

## Source research

- MQL5 regime-adaptive grid article with ATR-dynamic grid spacing and change-point logic: https://www.mql5.com/en/articles/21833 (includes risk mechanisms; we do NOT adopt lot scaling)
- TradingView's open-source grid volatility/structural spacing: https://www.tradingview.com/script/NtSoWuHM-Adaptive-Fractal-Grid-Scalping-Strategy/
- TradingView's open-source trend/volatility adaptive grid: https://www.tradingview.com/script/V5IjGQvo-Advanced-Adaptive-Grid-Trading-Strategy/

The named algorithm and numerical thresholds are **our testable hypotheses**, not third-party claims of performance. Earlier invalidated legacy Jan/Feb derived modules were NOT imported.

## Reproducibility

All new study scripts, pure-test kernel, nine passing deterministic tests, daily-block JSON, 14-signal quote-side horizon evidence, original source scanner code from the clean GRID-0104 artifact and source SHA metadata are in `GRID0106_APRIL_THREE_MONTH_CAUSAL_SOURCE_AND_EVIDENCE.zip`. Original 200+ MB compressed tick data must be supplied separately; excluded from archive. No MT5 terminal is necessary.
