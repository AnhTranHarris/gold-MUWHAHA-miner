# Delta-A-alpha — Pre-Research Rollback Checkpoint 001

**Checkpoint:** `DAA_ROLLBACK_PRE_OPPORTUNITY_RECOVERY_RESEARCH_001`  
**Date:** 2026-10-06  
**Purpose:** Immutable rollback point before community/GitHub research begins for the next GRID-001 event-clock phase.

## Scientific state frozen here

Parent side branch: `delta-A-alpha`

Main `delta` remains read-only.

Last completed unit:
`DAA_GRID_001_BOUNDED_STAGE_A_SCREEN_01`

Next scientific unit:
`DAA_GRID_001_EVENT_CLOCK_SINGLE_TRADE_STAGE_A_SCREEN_01`

Physical grid inventory is retired. The retained component is the high-density grid event clock.

## Owner architecture directive

Delta-A-alpha is not building a standalone grid EA that later competes with the specialist stack.

The grid layer is a **system-wide opportunity engine** intended to sit beneath or beside the future specialist portfolio. Its role is to:

1. produce a dense stream of causal XAUUSD opportunity events;
2. recover opportunity after an initial wrong-direction interpretation instead of simply accepting a missed or poisoned event;
3. minimize repeated wrong-direction trades;
4. distinguish mean-reversion, continuation, and abstention states;
5. keep fixed-size risk bounded;
6. support a future portfolio of roughly 6 to 16 trading specialists;
7. reduce how much profit-gap recovery each later specialist must accomplish individually;
8. help the combined system approach or exceed the R9 SYNTH benchmark.

The grid layer is therefore infrastructure for opportunity discovery, routing, and recovery—not permission for uncapped averaging.

## Opportunity-recovery objective

Opportunity recovery is now a first-class research dimension.

A candidate mechanism should be evaluated not only on whether its first directional decision is correct, but also on whether it can:

- detect that the initial directional thesis has degraded or failed;
- avoid repeatedly re-entering the same wrong direction;
- preserve the event/opportunity rather than discarding it unnecessarily;
- reclassify the event causally as continuation, mean reversion, or no-trade;
- recover with bounded fixed 0.01 ownership;
- avoid doubling, Martingale, or loss-dependent sizing;
- remain compatible with realistic small-account survivability.

Recovery quality must be measured separately from raw win rate.

## Community-source expansion

Public GitHub is an explicit community-research source from this checkpoint forward.

Rationale: public repositories often contain reconstructible implementations, helper logic, tests, state machines, execution assumptions, and failure-handling mechanisms that are more useful than promotional strategy descriptions.

GitHub findings may be used only when:
- code is public and inspectable;
- logic is reconstructible;
- licensing/attribution constraints are respected;
- no opaque binary or black-box mechanism is promoted;
- discovered logic is independently tested on the Delta-A-alpha causal tick surface before adoption.

GitHub joins the existing multilingual/community source pool. It does not replace independent validation.

## Frozen risk and execution constraints

- Symbol: XAUUSD
- Fixed lot: 0.01 only
- Martingale: PROHIBITED
- Loss-dependent lot escalation: PROHIBITED
- Small-account survivability targets: $100 / $200 / $300
- Ordered tick execution with executable Bid/Ask
- Main `delta`: READ ONLY
- August 2026: SEALED
- MQL5 implementation: NOT AUTHORIZED

## Benchmark role

Canonical R9 SYNTH Jan-Jul remains the guiding-light performance target:
- net profit: +$309,122.85
- trades: 219,342
- win rate: 87.14063%
- profit factor: 20.036229
- expected payoff: +$1.409319/trade
- average velocity: 1,472.09 trades/active day

The objective is not to copy R9 SYNTH mechanics. The benchmark defines the performance frontier the combined Delta-A-alpha architecture should approach or exceed.

## Current GRID-001 evidence

Forensic source-style grid:
- very high opportunity density;
- 98.87% closed win rate;
- unacceptable hidden inventory tail;
- failed $100/$200/$300 survivability.

Bounded physical-grid screen:
- all 12 preregistered variants negative;
- physical grid inventory retired.

Research consequence:
**retain event density, discard physical averaging inventory.**

## Next research direction

The next lane is:

`GRID EVENT CLOCK -> OPPORTUNITY RECOVERY -> SINGLE-TRADE BOUNDED OWNERSHIP -> SPECIALIST ROUTING`

Research should seek mechanisms for:
- directional state classification;
- wrong-direction detection;
- rapid causal recovery/reversal when justified;
- cooldown/rearm logic;
- event identity and duplicate suppression;
- continuation vs mean-reversion separation;
- abstention when neither direction has sufficient evidence;
- maintaining high event throughput without serially multiplying bad trades.

## Rollback rule

The snapshot branch created from this checkpoint is a rollback/reference branch only.

Do not perform new research directly on the rollback branch.

If later research becomes corrupted, overfit, poorly documented, or architecturally confused, restore from this checkpoint and reapply only independently validated post-checkpoint units.

## Documentation rule

Every scientifically meaningful positive or negative result after this checkpoint must be persisted before the next dependent experiment begins.

Chat is coordination, not authoritative storage.
