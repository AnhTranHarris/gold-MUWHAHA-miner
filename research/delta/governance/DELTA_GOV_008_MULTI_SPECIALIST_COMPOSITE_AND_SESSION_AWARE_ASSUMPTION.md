# DELTA GOV-008 — Multi-Specialist Composite Architecture and Session-Aware Assumption

**Effective:** 2026-10-01  
**Branch:** `delta`  
**Status:** MANDATORY / HUMAN-REVISABLE  
**Evidence loading:** NOT AUTHORIZED

## 1. Owner-defined architectural assumption

DELTA assumes the eventual system will be a **multi-specialist composite**, not a single universal strategy.

This is an owner-defined DELTA design assumption. It is not evidence imported from any prior internal research lineage.

The system may contain multiple independently testable specialists that handle different:
- market sessions;
- volatility states;
- trend/range states;
- momentum/reversal states;
- liquidity/path regimes;
- entry patterns;
- hold/persistence conditions;
- exit/harvest conditions;
- execution conditions.

No individual specialist is required to solve every market condition or every primary human metric.

## 2. Session-aware operating regions

DELTA must be capable of session-aware specialization across the owner-defined operating regions:

- Australia
- Asia
- Russia
- India
- Middle East
- Europe
- UK
- New York

These labels define required research coverage areas.

Exact:
- UTC boundaries;
- broker-time boundaries;
- local-market reference clocks;
- daylight-saving treatment;
- overlap rules;
- transition buffers;
- holiday handling;

must be frozen in a later dedicated session-timing contract before production comparison or MT5 translation.

DELTA must not invent permanent session hours merely from these labels.

## 3. Two evaluation layers

DELTA distinguishes between:

### A. Specialist-level evaluation

A specialist is evaluated against its declared scope.

Its manifest must identify:
- intended session(s);
- intended market state/regime;
- intended primary metric target(s);
- allowed timeframe inputs;
- activation conditions;
- deactivation conditions;
- trade/opportunity population;
- baseline slice used for comparison.

A narrow specialist is not penalized for failing to trade outside its declared scope.

Its baseline comparison must use the corresponding scoped population whenever possible rather than comparing a regional/session specialist against an unrelated whole-system population.

### B. Composite-system evaluation

The assembled DELTA system is evaluated across the full intended operating surface.

The composite is responsible for the aggregate owner-primary metrics:
- winning trade count;
- net profit;
- gross loss;
- maximum drawdown.

The composite must also preserve:
- total trade count;
- opportunity count;
- trade-count retention;
- per-specialist contribution;
- routing/ownership behavior;
- overlap/conflict resolution.

The full primary-category objective belongs to the composite system, not necessarily to any one specialist.

## 4. Candidate types

DELTA recognizes at least four candidate object types:

1. **SPECIALIST**
   - narrow mechanism for one or more sessions/regimes/conditions.

2. **SPECIALIST_BUNDLE**
   - two or more specialists intentionally combined for complementary coverage.

3. **ROUTER_ORCHESTRATOR**
   - deterministic causal logic that decides which specialist owns or may act on an opportunity.

4. **COMPOSITE_SYSTEM**
   - the complete evaluated system containing specialists plus routing/ownership/execution logic.

Every research artifact must declare its object type.

## 5. Composition is a first-class research operation

DELTA may improve the system by:
- building a new specialist;
- replacing a weak specialist;
- combining complementary specialists;
- splitting one broad specialist into narrower experts;
- merging redundant specialists;
- changing session coverage;
- changing router/ownership logic;
- changing precedence in overlap periods;
- assigning different specialists to different nested timeframe structures;
- allowing a specialist to contribute primarily to one primary human metric while another specialist targets another.

Composition is not a workaround. It is a core DELTA research mechanism.

## 6. Specialist success does not require all four primary metrics

A specialist may be considered useful when it materially improves its declared target metric(s) within its declared scope and integrates without violating composite constraints.

For example, one specialist may primarily contribute:
- winning-trade count;

while another contributes:
- gross-loss reduction;

and another contributes:
- drawdown control or net-profit expansion.

DELTA must not reject a useful narrow specialist solely because it does not independently achieve the full system-wide R9 SYNTH performance surface.

## 7. Composite-level primary goals

The complete DELTA composite is the canonical object used for system-wide progress toward the R9 SYNTH primary categories.

Specialist research feeds the composite.

Therefore DELTA may pursue primary-category goals through complementary specialists working together rather than forcing one candidate to dominate all four categories simultaneously.

The final composite scorecard must show:
- aggregate primary metrics;
- each specialist's contribution;
- session/regime coverage;
- routing decisions;
- conflict/overlap handling;
- whether gains are additive, redundant, or cannibalizing.

## 8. Metric-lock semantics in a multi-specialist system

GOV-006 remains active, but its canonical system-wide lock attaches to the **accepted composite configuration** that achieved the lock.

A system-level lock must preserve:
- exact composite version;
- specialist membership;
- specialist versions;
- router/orchestrator version;
- configuration;
- metric value;
- evaluation window;
- result identity.

A single specialist does not automatically own a system-wide metric lock merely because it contributed strongly.

If a specialist is replaced or modified, the resulting composite must re-demonstrate preservation of every inherited system lock.

A specialist may have its own scoped research lock if explicitly declared, but that does not substitute for the composite-system lock.

## 9. Five-percent preservation still applies

When the composite locks a primary metric under GOV-006, future composite descendants may not deteriorate that metric by 5% or more from the locked composite anchor.

This applies even when the descendant introduces:
- a new specialist;
- a new session module;
- a router change;
- a different ownership rule;
- a new regime detector;
- a different timeframe interaction.

Creative composition may expand the system but may not erase previously secured composite performance.

## 10. GOV-005 specialist interpretation

GOV-005's 80% hard target / 85% preferred target may be applied at two levels:

### Specialist scope
When the owner defines a narrow specialist target, its improvement is measured against the corresponding scoped baseline population.

### Composite scope
When judging overall system promotion, the full composite is measured against the corresponding whole-system baseline/reference surface.

The 17% warning and 25% hard deterioration rules must be interpreted against the appropriate declared scope.

No experiment may switch between scoped and whole-system denominators after seeing results.

## 11. GOV-007 creative authority

GOV-007 explicitly permits multi-specialist creativity.

When progress stalls, DELTA may:
- create a new specialist instead of endlessly modifying an existing one;
- split a generalist into session/regime specialists;
- combine multiple partial winners;
- redesign routing;
- change ownership during session overlaps;
- use different nested-timeframe feature sets for different specialists;
- create protective specialists whose main purpose is loss/drawdown control;
- create opportunity specialists whose main purpose is trade-count/winning-trade expansion.

This is expected behavior, not an exception.

## 12. Router and overlap requirements

Because sessions overlap, the eventual composite must have explicit causal ownership rules.

Before promotion, DELTA must preserve:
- which specialists were eligible at each decision point;
- which specialist proposed each trade;
- which specialist ultimately owned the trade;
- why competing proposals were blocked or superseded;
- whether simultaneous positions are permitted;
- portfolio/risk interaction across specialists.

No hidden or post-hoc routing is permitted.

## 13. Research implication

DELTA should search for a **team of complementary specialists**, not a mythical universal strategy.

A specialist that solves one difficult slice of the market can be valuable even if its standalone full-window metrics look incomplete.

The scientific question becomes:

**Which combination of causal specialists, routing rules, and session/regime ownership produces the strongest composite system while preserving accumulated metric locks and activity?**

## 14. Human-review authority

This architecture assumption is human-revisable.

The owner may later:
- add/remove session regions;
- redefine specialist scope;
- require one specialist to cover multiple sessions;
- change overlap/ownership policy;
- change whether locks attach only to composite or also to selected specialist scopes;
- change the number of specialists.

## 15. No evidence-load authorization

This contract defines architecture and evaluation semantics only.

It does **not** authorize loading R9 REAL, R9 SYNTH, R9 OVERFIT, Coinexx reports, R9 ticklogs, or Dukascopy tick files. Existing owner evidence-loading restrictions remain active.
