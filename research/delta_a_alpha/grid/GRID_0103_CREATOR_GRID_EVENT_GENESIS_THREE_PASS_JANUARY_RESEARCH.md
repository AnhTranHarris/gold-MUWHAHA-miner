# GRID-0103 — improved creator-grid event genesis, three clean-room January passes

**Status:** FULL-JANUARY CAUSAL SHADOW-RESEARCH COMPLETE, **ZERO FUNDED TRADES; NO POSITIVE EDGE OR QUALIFIED-OPPORTUNITY CLAIM**.
**Original immutable input:** `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`, SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`, 9,135,062 timestamp-ordered original Dukascopy Bid/Ask ticks.
**Benchmark:** ORIGINAL Jan R9 Gamma HybridGate SYNTH 27,980 entries, 21 active report days. R9 SYNTH is a volume and P/L reference, **not a teacher of correct BUY/SELL signs**.
**Full reproducible tests/scripts and unchanged January shadow-event tapes:** attached ChatGPT artifact `GRID_0103_SOURCE_TESTS_FULL_JANUARY_RESEARCH.zip` and separately source-only `GRID0103_VERIFIED_SOURCE_ONLY.tar.gz`. Source must be preserved alongside this checkpoint; do NOT reconstruct from historical retired Jan/Feb models. Seven deterministic clean source tests passed locally.
**New owner law:** `research/delta_a_alpha/governance/OWNER_GRID_GENESIS_NO_MARTINGALE_100K_DISCOVERY_20261010.md`.

## The creator's reconstructed mechanics and what we change
Source [MegaJoctan Python Grid Bot](https://github.com/MegaJoctan/omegafx-youtube-shared-files/tree/main/Python%20Grid%20Bot): 48-H1 rolling extremes, contrarian buy after drop below rolling high by grid gap, sell after rise above rolling low by grid gap; subsequent level anchored to latest same-side physical position; initial example no stop and later 2× Martingale. Actual published tester is US500/1m-OHLC, not XAUUSD ordered real ticks.

**KEEP**: completed-bar extrema, tick-observed grid-level crossings, unique level genealogy, notional/progression rung, 2 directional hypotheses per event, session/overlap and observed micro-momentum metadata.
**REMOVE**: no-stop held loss, physical averaging, all loss-progression lot multiplication, implicit intrabar future OHLC, position-linked shadow event requirement, exact-hour tick equality, and both-direction universal Ask comparisons.
**No trades at stage zero**: all outputs are event-only observations; positions, margin, fees, equity/PF, TP/SL, 0.01 lot and $100k capital are not action inputs.

## Explicit research questions
- Can we approach the eventual R9 per-day *opportunity discovery* requirement **without** physically opening multiple losing positions?
- Does the creator's completed-H1 rolling-boundary trigger alone have sufficient volume, and can virtual level re-anchoring generate more?
- How much event de-duplication is necessary to prevent a rapidly oscillating gold quote creating fake opportunities?
- Should gap size adapt to prior completed-minute volatility, observed spread and session geometry, rather than fixed EURUSD-style points?
- Is BUY after drop or SELL after rise actually a correct direction on executable XAUUSD Bid/Ask? Should later vertical HTF quality select the opposite **continuation** hypothesis instead?
- Does a deeper shadow Martingale-style rung mark exhausted mean reversion or imminent trend continuation, without authorizing a larger lot?
- How does time to next observable broker-executable quote change the event lifecycle?
- Which subfamilies have enough spread-adjusted forward movement to justify *subsequent* full V1 admission?
- What is the eventual collision/risk budget on a single actual funded account, separated from stage-zero density?
- Can four independent session/overlap hypotheses coexist in one full V1, with no session alone authorizing an order?

## Pass 1: event-mechanism choices, original January tick quotes
| Clean **shadow** generator | Events | BUY | SELL | Relative to R9 January |
|---|---:|---:|---:|---:|
| Source-inspired only: 48 completed H1 extreme crossings, $1 gap | 1,302 | 1,015 | 287 | 0.05× |
| $1 virtual ladder, no cooldown | 138,620 | 68,712 | 69,908 | 4.95× |
| $0.50 virtual ladder, no cooldown | 378,387 | 187,717 | 190,670 | 13.52× |
| $0.75 virtual ladder, 1s cooldown | 152,724 | 75,231 | 77,493 | 5.46× |
| Prior-completed-minute adaptive gap, $0.40–$1.80 clamp | 176,855 | 87,537 | 89,318 | 6.32× |

## Pass 2: one event per observed tick; virtual *opportunity*, not Martingale size
| Hypothesis | Unique January candidates | Fraction of original R9 Jan entry count |
|---|---:|---:|
| $0.75 gap / 5s dedup | 92,709 | 3.31× |
| **$0.75 gap / 15s dedup** | **54,210** | **1.94×** |
| $0.75 gap / 30s dedup | 35,200 | 1.26× |
| $1 gap / 15s | 43,430 | 1.55× |
| $0.50 gap / 30s | 42,182 | 1.51× |
| completed-M1 dynamic gap / 15s | 64,907 | 2.32× |

Under a *tentative and UNVERIFIED* Coinexx report clock UTC+2 January normalization, the $0.75/15s raw tape exceeded 75% of the corresponding benchmark report-day entry count on 21/21 active days. **That is not the binding qualified-and-executable 75% rule**; no L1–L7 admission/funded execution was performed. Do not describe it as meeting the final owner acceptance.

## Pass 3: test spread, direction, rung and source-known micro-momentum independently
On $0.75/15s candidates: BUY/SELL 54,210, first rung 27,592, second 13,486, depths3–5 11,447, depths6+ 1,685. Median native source spread **$0.696** (92.8% of grid gap); in **37.316%** of candidates spread > $0.75. At 250ms hypothetical observation lag median absolute next-observed mid displacement $0.09 (12.389% already move ≥ half gap); at 1000ms displacement $0.165 (24.829% ≥ half gap). This is a *quote-age diagnostic*, not simulated fills.

At 30 seconds forward, among 54,184 valid quote horizon observations, after hypothetical instantaneous entry spread and prior to commission/slippage:
- contrarian direction positive **28.999%**, opposite continuation **29.025%**; mean quote-side markouts −$0.872 vs −$0.807.
- Spread <= 0.75 gap: **9,031 raw candidates**; conditional 30s contrarian-positive 32.447%, continuation-positive 30.863%; average contrarian markout still −$0.517.
- Spread <= 0.5 gap: just **429 raw events** (0.791% of tape)—extreme cheap-spread gate destroys velocity; no promotion.
- Spread > full gap: 20,229 raw events; mean contrarian markout −$1.285.
- Prior 15sec price movement (entry-known) stratifications also failed to reveal a strong, profitable directional rule.
At 120sec, contrarian-positive 38.923%, continuation-positive 38.144% overall, while mean quote-side marks stayed negative.

**Therefore neither BUY-on-down-grid nor SELL-on-up-grid is a proven directional strategy.** The event generator MUST export *both* reversion and continuation hypotheses, with final choice delegated to the single connected L0–L7 layer stack only after future tests.

Session event distribution for $0.75/15s: London only 9,666; London/NY 12,681; NY only 11,283; Sydney only 2,397; Sydney/Tokyo overlap 13,718; Tokyo only 4,465. Session classes are DST-aware market-clock **diagnostic labels**, not standalone orders or verified Coinexx hours.

## Capital and scientific boundary
OWNER NEW DIRECTIVE: hypothetical **$100,000 starting balance as later funded research default**, while $100–$300 becomes eventual preferred funding goal rather than an early hard optimization gate. **No capital was used in these ZERO-ORDER shadow passes**. When actual whole-system simulation begins, shared capacity, realized fills, stop/exit lifecycle, gross loss, equity drawdown, account solvency and latency remain mandatory at every balance.

**Reject:** creator's physical adverse grid, doubling, unlimited inventory, high closed-win-rate as predictive accuracy, unthrottled event floods, standalone session/H1 trading.
**Retain for next independent hypothesis:** virtual price-cell/rung event clock with controlled spacing/cooldown, completed-bar alternatives, metadata by broker/session, both directions, observed spread-to-gap and pre-event momentum, prospective regime and Watchdog quality inputs.
**Further evidence needed:** independent February and later months, truly calibrated Coinexx clock/feed and broker conditions, complete L1–L7 coherent execution, out-of-sample conditional directional accuracy and eventual R9 profitability and trade-volume gates.

Source research: https://www.mql5.com/zh/articles/8390 ; https://www.mql5.com/ja/articles/7013 ; https://www.tradingview.com/script/NtSoWuHM-Adaptive-Fractal-Grid-Scalping-Strategy/ ; https://www.tradingview.com/script/V5IjGQvo-Advanced-Adaptive-Grid-Trading-Strategy/ ; https://www.reddit.com/r/algotrading/comments/1mpxpq6
