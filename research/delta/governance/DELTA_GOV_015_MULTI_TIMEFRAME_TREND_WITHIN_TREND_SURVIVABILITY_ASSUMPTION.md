# DELTA GOV-015 — Multi-Timeframe Trend-Within-Trend Survivability Assumption

**Effective:** 2026-10-02  
**Branch:** `delta`  
**Status:** MANDATORY / HUMAN-REVISABLE ASSUMPTION  
**Layer:** TRADE CONTEXT / SURVIVABILITY ARCHITECTURE  
**Research metrics:** NOT DEFINED BY THIS CONTRACT  
**Evidence loading:** NOT AUTHORIZED BY THIS CONTRACT

## 1. Purpose

DELTA assumes that trade survivability cannot be governed only by session state, news/event state, or single-timeframe direction.

The eventual system must also be **trend-within-a-trend aware across multiple causally reconstructed timeframes** so that a trade can be interpreted in the context of the larger and smaller structures surrounding it.

This is an architectural assumption only. It does not define a candidate, optimization target, parameter set, metric threshold, or promotion gate.

## 2. Trend is hierarchical

DELTA must not represent market direction as one flat binary trend flag.

At minimum, future trend-aware logic must be capable of distinguishing relationships among:

- higher-timeframe structural direction;
- intermediate swing / regime direction;
- lower-timeframe execution direction;
- local pullback or countertrend movement inside a broader trend;
- local continuation inside a broader trend;
- structural transition, exhaustion, or reversal conditions;
- compression and expansion occurring inside a broader directional structure.

A lower-timeframe move against a higher-timeframe trend is not automatically invalid. It may represent a pullback, retracement, reversal attempt, liquidity event, or specialist-specific opportunity.

## 3. Trend-within-trend awareness

The system should understand relationships such as:

- lower timeframe aligned with intermediate and higher timeframe;
- lower timeframe countertrend inside a dominant higher-timeframe trend;
- intermediate timeframe pullback inside a higher-timeframe trend;
- lower timeframe reversal that is still only a retracement at a higher level;
- higher-timeframe trend weakening while lower timeframes transition first;
- nested trend continuation after local retracement;
- conflicting timeframe structures;
- timeframe convergence toward the same directional state;
- timeframe divergence indicating instability or transition.

The goal is contextual awareness rather than forced universal alignment.

## 4. Survivability role

The future survivability layer may use multi-timeframe trend context to help determine, when later researched and validated:

- whether a trade should be allowed to breathe through a local pullback;
- whether an adverse move is normal retracement or structural invalidation;
- whether initial-hold behavior should differ under aligned versus conflicting structures;
- whether a specialist should retain, transfer, or surrender ownership;
- whether a continuation trade has structural support above its execution timeframe;
- whether a countertrend trade requires a different specialist or tighter lifecycle;
- whether a local reversal should be treated as noise, retracement, or possible regime transition.

This contract does not freeze how any of those decisions are implemented.

## 5. Multi-timeframe hierarchy

GOV-002 remains authoritative for the tick-rooted timeframe hierarchy.

Trend-within-trend logic may draw from the established nested hierarchy:

`TICKS -> S0.25 -> S1 -> S5 -> S15 -> S30 -> S45 -> M1 -> M2 -> M3 -> M4 -> M5 -> M6 -> M10 -> M12 -> M15 -> M20 -> M30 -> H1 -> H2 -> H3 -> H4 -> H6 -> H8 -> H12 -> D1`

A future implementation may use only a subset of these timeframes, but the relationship among selected timeframes must remain explicit.

## 6. Causality and right-edge discipline

All multi-timeframe trend state must obey existing DELTA causality rules.

No trend state may use:

- an incomplete future bar as if it were closed;
- a future swing confirmation before it became knowable;
- future highs or lows;
- retroactively perfect trend labels;
- future regime classification;
- any indicator value that depends on unavailable future observations.

Completed bars become visible only at their right edge under GOV-002.

## 7. Trend state must be reconstructible

Any future trend-within-trend mechanism must be reconstructible from explicit public or independently derivable logic.

Permitted future building blocks may include, subject to later research:

- swing structure;
- higher-high / higher-low and lower-high / lower-low logic;
- slope or directional persistence;
- moving-average relationships;
- volatility-normalized directional movement;
- breakout / reclaim / retest structure;
- trend strength;
- range compression / expansion;
- price position inside higher-timeframe structure;
- causal support/resistance or market-structure state.

This list is illustrative only and does not approve or select any method.

Opaque, non-reconstructible trend classifiers are not promoted by this assumption.

## 8. Relationship to session and news awareness

Trend-within-trend awareness is orthogonal to:

- session-aware routing under GOV-008;
- news/event awareness under GOV-009.

A trade may therefore be evaluated simultaneously by:

- session context;
- news/event context;
- multi-timeframe structural trend context;
- specialist-specific opportunity logic.

No one context automatically overrides the others unless a later tested router explicitly defines precedence.

## 9. Relationship to specialists

Different specialists may legitimately operate under different nested-trend relationships.

Examples include:

- continuation specialist;
- pullback specialist;
- countertrend specialist;
- reversal specialist;
- breakout specialist;
- post-news continuation specialist;
- mean-reversion specialist inside a larger directional structure.

The architecture must therefore support explicit specialist ownership rather than requiring every specialist to agree with one universal trend direction.

## 10. No metric or research authorization

This contract does not define:

- a trend score;
- alignment percentage;
- required number of agreeing timeframes;
- hard trend filter;
- survivability metric;
- hold-time target;
- profit target;
- drawdown target;
- candidate formula;
- optimization grid;
- research threshold.

Those belong to later candidate research and must be discovered under the existing spreadsheet-first and tick-replay workflow.

## 11. No automatic trade suppression

Multi-timeframe disagreement must not automatically become a blanket no-trade rule.

The purpose of this assumption is to make DELTA aware of nested structure so the system can distinguish:

- favorable conflict;
- normal retracement;
- dangerous structural opposition;
- transition;
- continuation;
- specialist-specific countertrend opportunity.

Any eventual suppression rule must be evidence-based and specialist-specific.

## 12. Future MT5 reconstruction

If a successful candidate later uses trend-within-trend state, the final MT5 handoff must explicitly document:

- selected timeframes;
- trend-state definitions;
- update timing;
- bar-completion semantics;
- state-transition ordering;
- specialist use of the trend state;
- interaction with session/news routing;
- exact formulas and parameters;
- parity fixtures.

MQL5 coding remains owner-authorized only under existing governance.

## 13. August

August 2026 remains sealed.

This contract does not authorize August access.
