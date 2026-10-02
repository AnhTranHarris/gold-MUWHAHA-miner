# DELTA R004 — Multivariate Preregistration Baskets and Bounded Variant Design

**Status:** RESEARCH_ONLY / NO TESTING  
**Active parent:** `DELTA_004_COINEXX_LIKE_DUKASCOPY_RESEARCH_SURFACE`  
**Scope:** ENTRY + INITIAL-HOLD  
**Active promoted candidate:** NONE  
**August 2026:** SEALED  
**MQL5:** NOT AUTHORIZED

## Research decision

R004 does **not** use one-variable-at-a-time optimization as the default research design.

The owner explicitly requires a basket of variables capable of supporting:
- configuration changes;
- modifications;
- adjustments;
- restructures;
- evidence-supported component combinations.

R004 therefore bounds the **architecture and factor space**, not a single local threshold neighborhood.

## Quant design principle

A full Cartesian grid is not the default because run count grows exponentially with dimensionality.

Future replay design should instead use:
- balanced/fractional-factorial screening for categorical architecture factors where appropriate;
- scrambled Sobol or Latin-hypercube style space-filling coverage for bounded continuous/ordinal factors;
- focused higher-resolution interaction designs only after evidence identifies important factor groups.

References:
- NIST fractional-factorial design guidance:
  https://www.itl.nist.gov/div898/handbook/pri/section3/pri3345.htm
- SciPy QMC guidance:
  https://docs.scipy.org/doc/scipy/tutorial/stats/quasi_monte_carlo.html

This is a testing-design rule only. No sample vectors have yet been generated and no replay is authorized by this unit.

## Canonical Drive artifact

Google Doc:

`DELTA R004 — Multivariate Preregistration Baskets and Bounded Variant Design`

https://docs.google.com/document/d/1Yc3urBpxDfgvk4O1pyHCclaQTfgdJbQox6o7t2OrdVs/edit

Stage folder:

https://drive.google.com/drive/folders/1iCg7Ptl8zRQ-5QUFGSuB7sPTqsNKzxiX

## Working workbook additions

Canonical working workbook:

https://docs.google.com/spreadsheets/d/1C2EOJ2WDZgVMcGG8s1WPY46-Q4U8QQXUhZytqPJVsY0/edit

New tabs:
- `12 Prereg Baskets`
- `13 Bounded Variants`
- `14 Interaction Reservations`

## Shared variable families

R004 preregisters factor families across:

1. structural context;
2. event definition;
3. volatility/timing;
4. micro-persistence;
5. initial-hold hysteresis/invalidation.

This allows coherent multivariate variants rather than isolated threshold tuning.

## Primary basket coverage

### DH-01 — shared context
Includes:
- structure-source policy;
- execution swing-confirmation width;
- signed-efficiency threshold;
- volatility-normalized directional displacement;
- parent-state hysteresis;
- nested-conflict policy.

### DH-02 — Breakout Retest Rebreak
Includes:
- boundary source;
- parent-context policy;
- break confirmation timeframe;
- BreakNorm threshold;
- acceptance dwell;
- retest-zone width;
- penetration buffer;
- retest age;
- rebreak timeframe;
- rebreak efficiency;
- rebreak displacement;
- complete event age;
- causal failure acceptance.

### DH-03 — Pullback Continuation
Includes:
- parent timeframe bundle;
- parent-state policy;
- pullback-start timeframe;
- normalized pullback depth;
- pullback age;
- countertrend efficiency;
- exhaustion decline;
- no-new-extreme confirmation count;
- reclaim source;
- reacceleration timeframe/efficiency;
- structural invalidation buffer.

### DH-06 — Quote-Pressure Initial-Hold
Includes:
- pre-entry baseline window;
- minimum tick count;
- directional efficiency;
- StepBalance;
- BidAskImpulse;
- RetreatFraction;
- SpreadStress;
- TickRateRatio;
- agreeing-window count;
- state composition policy;
- sparse-tick policy.

DH-06 remains explicitly a quote-pressure proxy and is not called true centralized order-flow imbalance.

### DH-07 — Specialist-Aware Initial Hold
Includes:
- soft-adverse confirmation count;
- hysteresis policy;
- ESTABLISHING checkpoint;
- INITIAL_HOLD_SURVIVED checkpoint;
- specialist-boundary buffer;
- STALL tolerance;
- RETREAT tolerance;
- spread-stress policy;
- immutable hard structural invalidation precedence.

## Bounded variant families

R004 documents coherent variant families instead of single-factor points.

DH-02:
- density-preserving;
- balanced;
- structure-heavy;
- transition-cautious.

DH-03:
- shallow-fast;
- balanced continuation;
- deep-structural;
- transition-sensitive.

DH-06:
- permissive persistence;
- balanced;
- pressure-strict;
- stress-cautious.

DH-07:
- structure-only control;
- balanced hysteresis;
- quote-assisted;
- breathing-room tolerant.

DH-04 and DH-05 remain in the research set with their own multivariate parameter baskets and are not discarded.

## Reserved structured combinations

These are normal evidence-oriented specialist/shared-component stacks and do not by themselves trigger GOV-018:

- R9 bracket + DH-01 + DH-06 observer + DH-07 observer
- DH-02 + DH-01
- DH-02 + DH-01 + DH-06
- DH-02 + DH-01 + DH-06 + DH-07
- DH-03 + DH-01
- DH-03 + DH-01 + DH-06
- DH-03 + DH-01 + DH-06 + DH-07
- DH-04 + DH-01 + DH-06 + DH-07
- DH-05 + DH-01 + DH-06 + DH-07

Cross-specialist routing, merged formulas, and novel specialist synthesis remain GOV-018-gated.

## Planned evidence sequence

### Wave 0 — measurement controls
R9 bracket with DH-01 context labels and DH-06/DH-07 observer-only outputs.

### Wave 1 — specialist attribution
DH-02, DH-03, DH-04, DH-05 independently.

### Wave 2 — shared-component attribution
DH-06 attached first as observer, later as modifier only if preregistered evidence supports it.

### Wave 3 — initial-hold attribution
DH-07 variants, with mature holding/exit logic frozen.

### Wave 4 — structured integration
Specialist + DH-01 + DH-06 + DH-07 combinations that survived attribution.

### Wave 5 — router/heavy synthesis
Only after complementary ownership evidence exists or GOV-018 is triggered.

## Search-space rules

- no exhaustive Cartesian sweep by default;
- no one-variable-at-a-time assumption;
- no hidden within-run threshold adaptation;
- every future configuration receives an immutable ID and complete parameter vector;
- continuous factors stay inside preregistered bounds;
- categorical choices stay inside declared level sets;
- interaction families must be named before their replay batch;
- activity retention remains visible;
- restructuring after failure creates a new documented variant version rather than mutating the old version.

## Current gate

- parameter baskets: DOCUMENTED
- bounded variant families: DOCUMENTED
- exact replay sample vectors: NOT GENERATED
- Stage-A preregistration run sheet: NOT GENERATED
- testing: NOT STARTED
- active candidate: NONE
- performance evidence: NONE
- GOV-018 heavy synthesis: DORMANT
