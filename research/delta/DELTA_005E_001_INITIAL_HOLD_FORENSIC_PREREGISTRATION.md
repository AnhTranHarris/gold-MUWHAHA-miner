# DELTA 005E-001 — Initial-Hold Causal Forensic Census

**Status:** PREREGISTERED  
**Mode:** historical forensic discovery only  
**Candidate promotion:** prohibited in this unit  
**Focus:** ENTRY + INITIAL-HOLD  
**Holding-Trade + Exit + High-Profit:** deferred / out of scope  
**Stage-A:** [2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**August:** SEALED

## Why this unit exists

DELTA_005A tick-flow entry confirmation, DELTA_005B micro-retest continuation, DELTA_005C failed-break reversal, and DELTA_005D early invalidation all failed to create a large improvement in first-seconds persistence.

005D's best net cell improved net-loss magnitude only ~0.31% and reduced 5s/10s survival.

GOV-007/GOV-013 therefore require structural escalation rather than another local threshold sweep.

## Scientific question

At a fixed causal observation time after an original R9-style entry, which observable microstate combinations materially separate positions that survive the initial hold from positions that fail early?

This unit discovers state structure. It does not create or promote a trading rule.

## Causal observation horizons

For every original R9-style Stage-A trade that is still open at the horizon, snapshot only state visible by:

- entry / 0 ms
- 250 ms
- 500 ms
- 1000 ms
- 2000 ms
- 3000 ms

No later tick may enter a feature measured at an earlier horizon.

Trades that close before a horizon simply have no snapshot for that later horizon. Their absence/count is reported.

## Feature families

At each snapshot, record where supported:

### Boundary acceptance
- side-adjusted executable distance from the frozen R9 entry boundary;
- whether boundary has been revisited/lost since entry;
- side-adjusted unrealized price displacement from entry.

### Tick flow
- side-adjusted 250ms tick-count flow;
- side-adjusted 1000ms tick-count flow;
- fast-minus-slow flow change;
- side-aligned tick fraction since entry.

### Completed-S1 state
- current completed-S1 directional efficiency;
- change in efficiency from entry;
- side-adjusted completed-S1 displacement;
- completed-S1 range;
- completed-S1 turn count.

### Path state since entry
- causal MFE through the observation time;
- causal MAE through the observation time;
- tick-path efficiency since entry;
- favorable extreme-renewal count;
- tick count / arrival intensity since entry.

### Context
- R9 session code;
- modeled spread;
- trade side.

## Labels

Future information is permitted only as a retrospective label after features are frozen.

Primary labels:
- survives beyond 5 seconds under the unchanged parent lifecycle;
- survives beyond 10 seconds under the unchanged parent lifecycle.

Secondary diagnostic label:
- survives beyond 15 seconds.

The later trade P/L/winner outcome may be stored for audit but must not be used to define the current Entry + Initial-Hold success rule in this unit.

## Anti-leak rule

A feature at observation horizon H may use only ticks/state with timestamp <= H from entry.

Future 5s/10s/15s survival is a label, never a feature.

No matrix bin edge may be chosen by looking at label outcomes. Domain-fixed bins or outcome-blind distribution quantiles are allowed.

## Planned 2D interaction harvest

At minimum create matrices for:

1. boundary acceptance × 250ms flow;
2. boundary acceptance × 1000ms flow;
3. 250ms flow × 1000ms flow;
4. completed-S1 efficiency × boundary acceptance;
5. efficiency change × boundary acceptance;
6. MFE × MAE;
7. path efficiency × MAE;
8. side-aligned tick fraction × boundary acceptance;
9. S1 turn count × flow;
10. S1 range × boundary revisit;
11. session × boundary-acceptance state.

Generate these at multiple causal observation horizons, prioritizing 250ms, 500ms, 1s, 2s and 3s.

Each matrix must retain cell support counts alongside survival rates so tiny-sample cells cannot masquerade as breakthroughs.

## Ranking

For each feature/matrix, report:
- base survival rate at that horizon;
- best/worst supported cell rates;
- absolute separation in percentage points;
- support of the best cell;
- share of horizon observations in high-survival cells;
- stability across adjacent bins/horizons.

The goal is to identify broad, reconstructible state regions, not the single best cell.

## Output

- deterministic observation ledger or regenerable compact representation;
- horizon summary;
- fixed-bin definitions;
- 2D survival matrices;
- feature/matrix leverage ranking;
- candidate hypotheses for DELTA_005F or later.

## Decision boundary

005E cannot promote an EA rule.

A subsequent deterministic candidate must be separately preregistered and use only features that were causal at its decision horizon.

No mature Hold/Exit/High-Profit optimization is permitted.

August remains sealed.
