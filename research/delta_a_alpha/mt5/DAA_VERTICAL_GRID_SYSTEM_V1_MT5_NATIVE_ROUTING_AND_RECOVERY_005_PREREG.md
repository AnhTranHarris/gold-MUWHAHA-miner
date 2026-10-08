# Delta-A-alpha — Vertical Grid System V1 MT5 Unit 005
## Native Routing and Wrong-Direction Recovery

**Status:** IMPLEMENTATION CONTRACT  
**Parent:** unit 004 Watchdog campaign state  
**Execution:** observe-only / shadow recovery

## Objective

Complete the V1 decision-layer skeleton above the session lattice:

- trend-within-trend structural ownership;
- bounded wrong-direction failed-ignition observation;
- opposite-direction recovery proposals;
- no physical order authority.

## Native structural modes

Unit 005 classifies fresh event birth state into:

- NATIVE_MACRO_CONTINUATION
- NATIVE_LOWER_TAKEOVER
- NATIVE_PULLBACK_RECLAIM
- NATIVE_MACRO_SPLIT_TRANSFER

These are structural categories, not month-specific fitted selectors.

## Recovery shadow

Every fresh valid unit-003 route may start a shadow recovery watch.

Default V1 engineering values:
- ignition window: 2 seconds;
- required favorable excursion: 1.25 price units;
- recovery campaign horizon: 120 seconds.

The watch uses executable-side marking:
- long original: Bid marks the exit-side move;
- short original: Ask marks the exit-side move.

If the route fails to achieve the required favorable excursion within the already-elapsed ignition window, unit 005 emits a single shadow recovery proposal in the opposite direction.

This proposal is NOT funded and is NOT yet a deployable recovery admission rule. February research showed that generic reversal is insufficient; the Jan-Jul refinement phase must determine which causal states may fund recovery.

## Safety

- no order-send path;
- no Martingale;
- no loss-dependent sizing;
- one recovery proposal maximum per market tick;
- bounded watch lifetime;
- daily bounded watch memory.

## Acceptance

- native state categories deterministic;
- recovery uses only already-observed ticks;
- executable-side marking;
- 2s/1.25/120s defaults present;
- opposite direction only after failed ignition;
- no order-send path;
- CI pass.

## Next unit

`DAA_VERTICAL_GRID_SYSTEM_V1_MT5_PROPOSAL_ARBITER_AND_HEAT_GOVERNOR_006`
