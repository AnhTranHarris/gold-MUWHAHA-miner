# GRID-0105 — Pre-session grid opportunity improvement, repeated causal experiments

**Classification:** Research-only, shadow-event breakthrough in **opportunity-movement capacity**, **not** profitable directional trading, **not** an implemented or activated Vertical Grid layer. **Date:** 10 October 2026. **Owner spine remains untouched.**

## Discovery and source constraints

This phase tests the OmegaFX/MegaJoctan creator-inspired grid event generation path **before** Sydney/Tokyo/London/New York session-aware refinement and **before** the L1–L7 funded quality governor. It extends frozen GRID-0104: unique midquote-crossing virtual events with a current/past-quote EWMA of bid/ask spread, gap `max(0.75 XAUUSD, 1.5 × EWMA_spread)` and 7-second emission cooldown. The grid uses no physical accumulating losing positions, no Martingale size changes, no margin/P&L, and no trading. The grid is a candidate-event generator, not an order-placement engine.

**Source checks:** Pure CUSUM/change-point regime ideas and bounded restartable grid states appear in [MQL5 Taranto-inspired regime-adaptive grid article](https://www.mql5.com/en/articles/21833), and [Kaufman Efficiency Ratio source](https://www.tradingview.com/script/2Ghnhfqg-Kaufman-Efficiency-Ratio-Gate-NovaLens/) explains drift-versus-path-noise. These motivated *candidate questions*, not claimed third-party result replication. A [MetaQuotes grid-vs-Martingale primer](https://www.mql5.com/en/articles/8390) argues for relating grid spacing to anticipated price travel and explicitly warns about jumps and Martingale sizing. All formulas below are our independently reproducible hypotheses.

**Protected source:** January original Dukascopy `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz` 9,135,062 observed ticks; February original `XAUUSD_DUKAS_2026_02_ticks.csv(3).gz` 7,538,339 ticks. Chronological original bid/ask, unchanged. All measurements use original source quotes, no manufactured Coinexx spread and no R9 original-entry labels for direction. Frozen comparison counts Jan R9 Gamma HybridGate SYNTH 27,980 entries / 21 original active report dates; February 33,523 entries. R9 reports are benchmarks, not correct BUY/SELL teachers.

## Repeated creative/hypothesis cycles (audited)

1. **Directional microstructure:** separately measured prior 1s/5s/15s/30s/60s/120s/300s/900s price displacement, prior sampled price-path efficiency and location, virtual progression sign/streak, source spread and inter-event age. Tested 8 named hand-authored direction policies and regularized Ridge / boosted-tree models with 0–1.0×spread prediction thresholds at 30/120/300s; trained on January 1–18 only, held Jan 19–31 and February for contrasting. These use causal features but did not show a stable positive after-spread bid/ask forward direction result; no direction predictor promoted.
2. **Two-stage intrinsic-time event physics:** tested a *grid crossing first*, then wait for a new tick to establish a continuation or retrace of 0.15/0.3/0.5/1.0 grid steps, within 30/120s expiry (16 variants) at 7s cooldown. A unit test exposed a reversed inequality in the initial candidate implementation; the source was corrected **before final rerun**, and the seven deterministic tests then passed. Neither response type supported cross-month positive quote-side 120s expected signed return; none is promoted as a physical entry. This is useful reproducible adversarial evidence, not a performance claim.
3. **Magnitude capacity before deciding direction:** Instead of pretending to know BUY/SELL, ask: *Does the past/current grid event occur in a price-motion state whose observed displacement has room to overcome market friction?* Tested 7 past-only feature families at predeclared thresholds, then algebraic dual-horizon combinations, with exact daily-source counts and day-block bootstrap rather than naïve independent-event confidence bounds.

## Promotable research mechanism: as-of price movement relative to cost

At virtual crossing event `t`:

```
mid(t)             = [Bid(t) + Ask(t)] / 2
spread(t)          = Ask(t) - Bid(t)
prior_mid(t-300s)  = last ORIGINAL source quote at or before (t - 300s)
K5(t)              = abs(mid(t) - prior_mid(t-300s)) / max(spread(t), 0.10 USD)
GRID0105_capacity  = [K5(t) >= 2.0]
```

All inputs are known by time `t`; **neither future midpoint nor future trade direction is an input**. The `0.10` numeric floor is a research safety divisor, *not* a realistic or guaranteed broker spread. The gate screens *shadow opportunities* for recent economically meaningful displacement. It should be recorded as an opportunity **capacity feature**, not a guaranteed economic entry signal or a compulsory final V1 rejection rule.

### Same formula across full original January and February

| Measure | Prior GRID-0104 raw event tape | GRID-0105 K5 >= 2 shadow events |
|---|---:|---:|
| **January raw candidates** | 55,732 | **42,771 (76.7% preserved)** |
| **February raw candidates** | 53,958 | **41,230 (76.4% preserved)** |
| Jan candidates / original SYNTH monthly trades | 1.992× | **1.529×** |
| Feb candidates / original SYNTH monthly trades | 1.610× | **1.230×** |
| **Jan report days with count ≥75% same-day R9 SYNTH entries** | 21/21 | **21/21*** |
| Jan early fraction where future 120s `abs(mid_delta)` exceeds 2×current spread | 49.972% | **52.497% (+2.525 pp)** |
| Jan late same measurement | 68.819% | **70.223% (+1.404 pp)** |
| February same measurement | 61.803% | **63.686% (+1.883 pp)** |

\* Daily R9 Jan report clock alignment assumed UTC+2 and is **provisional**. The above daily gate counts are **RAW stage-zero events**, not quality-qualified physically executable trades. We do not claim the 75% final acceptance was achieved. February exact daily R9 entries were not loaded, so daily report-aligned 75% floor there is unmeasured.

**January training split:** events January 1–18 up to (January 19 00:00 UTC - 15 min); later Jan from +15min; February is a repeated-parameter cross-month check. Because this is an *iterative* grid research process, February was inspected during the broader candidate campaign, so **February is not an untouched blind holdout** and should not be promoted as a proof of an edge. A newly reserved month will be needed for true lock-box validation.

### Calendar-block uncertainty, not IID overlapping events

Evaluating each quote-positive UTC day separately, excluding <100-event days, on the feature K5 >= 2:

| Measure | January | February |
|---|---:|---:|
| Source days analyzed | 23 | 22 |
| Days with improvement in forward 120-second 2×spread motion criterion | 22 | **20** |
| Mean day-level percentage-point increase | +1.892 | **+1.521** |
| Day-bootstrap 95% interval of average daily improvement | [+1.340, +2.483] pp | **[+0.886, +2.141] pp** |

Bootstrap resamples whole source calendar days 10,000 times with deterministic seed 20261010, recognizing that individual overlapping 120-second quote horizons are strongly dependent. These descriptive intervals do not remove model-selection bias or imply a profitable trading strategy.

## Additional virtual opportunity classes examined

- Strict `K5 >= 3` is a **higher-movement-capacity state** (January raw 36,954; February 35,414; February 2×spread motion rate 65.072%), but only **18/21 January** provisional R9 daily-volume comparisons reached the 75% event count floor; **therefore it cannot replace K5>=2 as sole stage-zero opportunity stream**.
- The dual-sensor `K5>=3 OR |mid(t)-mid(t-15s)|/spread(t)>=1` retained January 49,871 and February 48,751 raw events, all 21 January provisional daily raw count floors, but exhibited **less movement-capacity discrimination** than standalone `K5>=2`. Keep it as an optional complementary shadow feature, not a profitable directional strategy.
- Direction-confirmation experiments were explicitly assessed on **later available executable bid/ask quotes** and never on guaranteed midpoint fills. Because their actual after-spread quote-side mean remained negative, no directional entry policy or position management rule is certified by GRID0105.

## Decision and stop boundary

**Accept as an INFORMATION-QUALITY BREAKTHROUGH (not a trading edge):** the GRID-0104 cost-normalized candidate clock supplemented by the causal five-minute **motion-to-friction `K5` feature**, with an exploratory `>=2` threshold. It improves a measurable cost-overcoming *motion-capacity* statistic on full January/February quotes while keeping monthly RAW opportunity volume above the original R9 reference and provisional 21/21 January daily RAW count comparisons. The fact a price will move by more than costs in *some* direction is NOT knowledge of which way to BUY/SELL, nor that the trade could be filled, held profitably, or safely liquidated.

**Do not activate L1 session-aware optimization yet**. Per owner's rules, grid-only generation, financially executable direction quality and true daily qualified opportunity coverage still need reliable verification. Preserve correct layers: creator-grid genesis first; then L1–L7 coherent quality after the owner-defined stage gate. Do not reimport invalidated earlier Jan/Feb derived strategies or Martingale. $100,000 remains hypothetical **future funded discovery** starting capital, unused in these tests; smaller $100–$300 is a later preferred path. No positions, stops, take profits, P&L, profit factor or account drawdown were simulated here.

## Reproduction

Companion ZIP bundles the verified GRID0103/0104 creator-derived shadow scanner, GRID0105 scripts, deterministic seven-test suite, text reports and raw-causality JSON. Run from Python 3.11 with NumPy, pandas, numba and scikit-learn; original downloaded Dukascopy CSV.gz files must be supplied as-is under the script path, no network and no MT5 required. Do not label `grid_event_economic_geometry.py` a profitable strategy: it emits **research events only**.
