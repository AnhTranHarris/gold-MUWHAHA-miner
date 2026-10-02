# DELTA R002 — Direction + Initial-Hold Causal Vocabulary and Pre-Backtest Shortlist

**Date:** 2026-10-02  
**Branch:** `delta`  
**Status:** RESEARCH_ONLY / PRE-BACKTEST / NO ACTIVE CANDIDATE  
**Parent:** `DELTA_004_COINEXX_LIKE_DUKASCOPY_RESEARCH_SURFACE`  
**Scope:** ENTRY + INITIAL-HOLD  
**Testing:** NOT AUTHORIZED IN THIS UNIT  
**August 2026:** SEALED  
**MQL5:** NOT AUTHORIZED

## 1. Purpose

Convert the R001 public/community scan into:

1. a causal vocabulary for direction + initial-hold research;
2. a qualitative workbook harvest;
3. a bounded pre-backtest shortlist of complete candidate packages.

“Highly viable” means **high research viability**, not empirical profitability.

No candidate metrics, SYNTH-gap closure, win rate, net profit, gross-loss reduction, drawdown improvement, or activity-retention result is claimed in this unit.

## 2. Working workbook

Google Sheet:

**DELTA R001 Direction+Hold Research Harvest — PRE-BACKTEST — 2026-10-02**

ID: `1LexrgMTYvgDXoeKHvVC4taiLGlENi5vvY2-8tmLNFcs`

The workbook is a copy of the GOV-014 template and adds:

`R001 Viability Harvest`

Qualitative screen dimensions:

- direct R9 failure fit;
- reconstructibility;
- causal input availability;
- activity-preservation potential;
- specialist distinctness;
- source triangulation;
- complexity;
- explicit falsifier.

The performance scorecard remains blank by design.

The tick backtest queue is set to:

`RESEARCH_HOLD_NO_TESTING_AUTHORIZATION`

## 3. Causal vocabulary

### 3.1 Nested direction state

Direction is hierarchical, not one bullish/bearish bit.

Allowed research states include:

- `ALIGNED_CONTINUATION`
- `PULLBACK_WITHIN_TREND`
- `COMPRESSION_WITH_DIRECTIONAL_BIAS`
- `STRUCTURAL_TRANSITION`
- `FAILED_BREAK`
- `CONFLICT_NOISE`

Lower-timeframe disagreement is not automatically invalid.

### 3.2 Entry event

Entry must map to a reconstructible event, for example:

- R9 bracket break;
- structural breakout;
- retest/rebreak;
- pullback resumption;
- compression expansion;
- failed-break reversal.

### 3.3 Initial-hold state

Immediately after fill, a candidate may transition through:

- `PERSIST`
- `STALL`
- `RETREAT`
- `INVALIDATE`

Possible causal inputs:

- displacement;
- directional efficiency;
- quote-change asymmetry;
- spread behavior;
- tick-arrival intensity;
- structural reclaim / return;
- volatility-normalized retreat.

Future MFE, MAE, or hindsight labels are forbidden from live state.

### 3.4 Quote-pressure proxy

DELTA may build a **quote-pressure proxy** from available Bid/Ask/top-of-book tick behavior.

Do not call it true OFI unless the source data contains the required order-book quantities.

## 4. Highly viable pre-backtest packages

### DH-C01 — R9 Bracket Salvage + Nested Direction + Hold Hysteresis

**Research viability:** VERY HIGH.

Keep R9's entry event generator, add nested directional context and causal early-hold hysteresis.

Why it advances:
- preserves R9 opportunity density;
- directly isolates whether entry replacement is necessary;
- lowest causal ambiguity.

Primary falsifier:
If direction+hold repair cannot distinguish favorable/failing R9 bracket entries without major activity starvation, the bracket entry is likely a material bottleneck.

### DH-C02 — Breakout -> Retest -> Rebreak + Nested Direction + Persistence Hold

**Research viability:** VERY HIGH.

Breakout becomes an observation state. Entry occurs only after causal retest and renewed directional acceptance/rebreak.

Primary sources:
- https://www.mql5.com/en/articles/19968
- https://www.mql5.com/en/articles/18259
- https://www.tradingview.com/script/7LQpgDXj-MTF-Breakout-Retest/

Primary falsifier:
Retest confirmation destroys too much activity or merely delays entry without improving early persistence.

### DH-C03 — Pullback -> Resumption Specialist + Nested Trend + Persistence Hold

**Research viability:** VERY HIGH.

Higher-level structure remains intact while the fast horizon intentionally countertrends. Entry occurs on causal resumption/re-acceleration.

Primary sources:
- https://www.forexfactory.com/thread/1350785-trend-channel-adxvma-supply-demand-mtf-system
- https://www.mql5.com/ja/articles/21581
- Chinese XAUUSD architecture clue only: https://www.mql5.com/zh/market/product/129029

Primary falsifier:
Normal pullback cannot be distinguished from genuine reversal soon enough to improve survival.

### DH-C04 — Compression -> Expansion Continuation + Nested Direction + Persistence Hold

**Research viability:** HIGH.

Enter directional expansion from a causally compressed/ranging state inside an allowed direction/regime.

Primary source:
- https://www.mql5.com/en/articles/15311

Primary falsifier:
Compression state is unstable across sessions or selects late/noisy bursts rather than persistent impulses.

### DH-C05 — Failed-Break Reversal Specialist + Structural Return + Persistence Hold

**Research viability:** HIGH.

Opposite-side ownership requires a causal failed-break signature rather than R9's generic opposite rearm.

Primary source:
- https://www.mql5.com/en/articles/18259

Primary falsifier:
Failure state is too late or too sparse to own a useful opportunity population.

## 5. Reserve packages

### DH-C06 — Structure-Quality Breakout + Swing/R² Validation + Persistence Hold

**Research viability:** HIGH / RESERVE.

Source:
- https://www.mql5.com/ja/articles/19625

More complex than C02; keep as reserve until simpler breakout state is characterized.

### DH-C07 — Session-Range Breakout + Trend/Vol Context + Persistence Hold

**Research viability:** MEDIUM-HIGH / NARROW SPECIALIST.

Source:
- https://www.mql5.com/en/articles/17239

Potential session-owned specialist, not global replacement.

## 6. Deferred composite

### DH-C08 — Multi-Specialist Direction+Hold Router

**Architecture viability:** HIGH.  
**Testing eligibility:** DEFERRED.

Potential router inputs:

- session;
- news/event state;
- nested trend;
- volatility;
- structure.

Potential owned specialists:

- C02 breakout-retest;
- C03 pullback-resumption;
- C04 compression-expansion;
- C05 failed-break reversal;
- C01 retained as diagnostic R9 salvage path.

Do not combine yet.

GOV-018 remains dormant until:
- explicit owner activation;
- a specific reconstructible evidence-trigger; or
- mandatory escalation after bounded GOV-014 harvesting fails to yield an integration-viable candidate.

## 7. Information-value order for eventual testing

When the owner later authorizes testing:

1. C01 first as diagnostic control;
2. C02 and C03 next as the strongest structurally distinct entry replacements;
3. C04 and C05 after those;
4. C06/C07 as reserves;
5. C08 only after single-specialist characterization.

This is **not** a profitability ranking.

It is an attribution-preserving research order.

## 8. Quant/community support used

Reconstructible/technical sources include:

- MQL5 regime-adaptive strategy selection:
  https://www.mql5.com/en/articles/17781
- MQL5 microstructure regime classification:
  https://www.mql5.com/en/articles/22940
- TradingView open-source MTF ADX:
  https://www.tradingview.com/script/E5uYlnA5/
- Cont, Kukanov & Stoikov OFI:
  https://arxiv.org/abs/1011.6402
- FX order-flow short-horizon research:
  https://www.nber.org/papers/w12682

Important limitation:
DELTA cannot transfer calibrations from NQ, equities, or opaque community products into XAUUSD. These sources support mechanism ideas only.

## 9. Durable shortlist document

Google Doc:

**DELTA R001 Direction+Hold — Highly Viable Pre-Backtest Candidate Shortlist — 2026-10-02**

ID: `1Nx06ehgmswgwwjDY7CKpP4IAX5Vj0j0FZJtAX8lvMBs`

## 10. State

- initial research: ACTIVE
- qualitative workbook harvesting: COMPLETE FOR R001 PASS
- candidate performance testing: NOT STARTED
- Stage-A preregistration: NOT STARTED
- active candidate: NONE
- active candidate version: NONE
- primary metric locks: NONE
- GOV-018 heavy synthesis: DORMANT
- August: SEALED
- MQL5: NOT AUTHORIZED


## 11. R002 refined supporting-state harvest

The working R001 harvest workbook now also carries five supporting causal-state hypotheses:

- `HYP-DH-009` — Breakout Acceptance / Rejection State
- `HYP-DH-010` — Pullback vs Structural Reversal Discriminator
- `HYP-DH-011` — Post-Fill Persistence / Retreat Balance
- `HYP-DH-012` — Regime Transition Hysteresis
- `HYP-DH-013` — Activity-Preserving Specialist Arbitration

These are not additional promoted candidates. They are supporting state definitions used to make C01–C08 implementable and falsifiable.

The reusable GOV-014 template has been restored to template-only state. Research-specific harvesting lives in the working workbook:

https://docs.google.com/spreadsheets/d/1LexrgMTYvgDXoeKHvVC4taiLGlENi5vvY2-8tmLNFcs/edit

Canonical shortlist Doc:

https://docs.google.com/document/d/1Nx06ehgmswgwwjDY7CKpP4IAX5Vj0j0FZJtAX8lvMBs/edit

The alternate timeout-era R002 shortlist Doc was renamed with a `ZZ_SUPERSEDED_` prefix and must not be used as current research authority.

### Fresh source reinforcement

Additional reconstructible sources reviewed during this refinement include:

- MQL5 custom regime detector/adaptive EA:
  https://www.mql5.com/en/articles/17737
  https://www.mql5.com/en/articles/17781
- Chinese MQL5 ORB breakout -> retest -> second-break logic:
  https://www.mql5.com/zh/articles/18486
- Chinese MQL5 breakout-pullback + momentum confirmation:
  https://www.mql5.com/zh/articles/18842
- Japanese MQL5 breakout/retest implementation:
  https://www.mql5.com/ja/articles/19968
- TradingView open-source volatility-contraction continuation:
  https://www.tradingview.com/script/Qje2aFax-VCP-Continuation-Breakout-Indicator-v1-3/
- Hierarchical short/long trend-state research:
  https://arxiv.org/abs/2007.14874

No threshold, candidate metric, Stage-A preregistration, or Python replay was created by this refinement.
