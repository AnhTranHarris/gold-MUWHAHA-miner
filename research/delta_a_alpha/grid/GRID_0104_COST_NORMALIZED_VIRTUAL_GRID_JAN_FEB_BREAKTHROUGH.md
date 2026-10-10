# GRID-0104 — Pre-Vertical Grid cost-normalized event geometry
**Date:** October 10, 2026. **Status:** TWO-MONTH SHADOW-OPPORTUNITY GEOMETRY ADVANCE; NOT PROFITABLE SIGNAL / NOT FUNDED STRATEGY.

## Verified breakthrough
Creator-derived virtual grid becomes **spread-aware but position-free**: each observed unique XAUUSD Bid/Ask quote updates a causal low-pass spread estimate, `E_spread(t) = 0.999*E_spread(t-1)+0.001*(Ask(t)-Bid(t))`. Virtual gap `G(t)=max($0.75, 1.5*E_spread(t))`; price crosses a virtual rung when current mid differs from the prior virtual anchor by at least G. Consume at most one observed-price crossing per tick, advance virtual anchor to current midpoint, and emit at most one research event per **7 seconds**. This is grid rung/anchor *information*, NOT a physical buy-the-dip or sell-the-rip operation, risk model, strategy or Martingale. No sessions, H4/H1/M15/M5 trade-quality stages or portfolio execution in this phase.

## Same algorithm, unaltered February cross-check (original Dukascopy tick surface)
| | Jan 2026 | Feb 2026 |
|---|---:|---:|
| Raw source ticks | 9,135,062 | 7,538,339 |
| ORIGINAL R9 Gamma HybridGate SYNTH historical entry count | 27,980 | 33,523 |
| Fixed $0.75/15s baseline RAW events | 54,210 | 60,603 |
| **G=maximum(0.75,1.5×EWMA spread)/7s RAW events** | **55,732** | **53,958** |
| Gross raw event count / original R9 monthly entries | **1.99×** | **1.61×** |
| Fixed baseline event spread > step | 37.32% | 75.00% |
| **Cost-aware new event spread > adaptive step** | **1.68%** | **2.38%** |
| Median raw source spread / adaptive step | 0.668 | 0.672 |
| Abs next 120-second midpoint change greater than entry spread (evaluation only) | 79.79% | 79.76% |

**Measurement nuance:** price-gap-versus-spread reduction is partly by design, NOT proof of better profit or entry direction. Changing event cadence from 15s to 7s is part of the complete candidate and was tested as a combined geometry change, so no isolated causal attribution of the improvement to gap alone. `quote-side direction` tests on January early vs late subsets revealed **no stable, after-native-spread profitable directional sign rule**; thus both reversal and continuation remain exploratory hypotheses. Median spread/step remains ~0.67, and 95%+ of adaptive events still have spread > half the step—future edge not certified.

**January reporting-clock caveat:** the provisional R9 entry report UTC+2 alignment produced ≥75% original daily completed-entry count in 21/21 January report days for this **raw event tape**. Broker offset not conclusively certified, and **raw candidates are NOT quality-qualified executable opportunities**. February daily benchmark tape was unavailable in this experiment; only exact monthly R9 count is used for February. The contract's daily 75% executable opportunity and R9-level profitability goals remain UNMET / UNTESTED at the whole-system level.

## Research lineage, no prior derived engine contamination
Source ideas: [creator original](https://github.com/MegaJoctan/omegafx-youtube-shared-files/tree/main/Python%20Grid%20Bot) rolling-extreme levels; [adaptive single-quote grid concept](https://github.com/jilongjia/adaptive-grid-strategy) uses separate volatility-driven quote widths and anchor state; [open-source adaptive-grid discussion](https://www.tradingview.com/script/V5IjGQvo-Advanced-Adaptive-Grid-Trading-Strategy/) motivates market-sensitive spacing. The formulas and cooldown are **our reproducible new grid hypothesis** rather than claims of creator's original code.

January nine geometry variants and February six fixed-parameter repetitions were tested on chronological original native Dukascopy Bid/Ask, with a separate 15-hypothesis conditional BUY/SELL direction screen on early/late January. Five deterministic regression tests passed. All early/late directional selectors with positive early appearance remained negative after native Bid/Ask spread in later January; none promoted.

**Repository policy:** NO new full V1 funded code; this is a standalone pre-L1 master grid opportunity candidate. Traditional martingale, auto adverse inventory, loss-dependent volume, future labels, per-calendar-month routing remain prohibited. $100k future hypothetical research account unchanged. No financial P&L or PF was generated. Next scientific gateway is to improve direction/executable coverage at the grid-only stage on independent source data and eventually compare session-specific self-adjustment; do NOT silently activate sessions before strong qualified evidence.

Reproducibility: exact tested scripts, five tests, and January/February JSON results are in the ChatGPT conversation artifact `GRID0104_CAUSAL_RESEARCH_PACKAGE.zip`; keep original source/tick files read-only. Source file `grid_event_economic_geometry.py` imports immutable `grid_event_research.py` from clean GRID-0103 bundle.
