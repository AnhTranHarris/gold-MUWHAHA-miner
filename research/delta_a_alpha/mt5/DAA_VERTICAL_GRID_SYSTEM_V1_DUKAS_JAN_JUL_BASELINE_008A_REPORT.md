# Delta-A-alpha — V1 Frozen Skeleton Dukascopy Jan–Jul Baseline 008A

**Status:** COMPLETE PRE-MT5-COMPILE BASELINE  
**Frozen MT5 skeleton:** `delta-A-alpha-v1-mt5-skeleton-certified` @ `c81539633a0becc0dfe053f84ef80e6462848cd5`  
**EA version:** 1.05  
**Data:** canonical Dukascopy XAUUSD Jan–Jul 2026 ordered Bid/Ask ticks

## Critical interpretation

The current V1.05 EA is a **decision skeleton**, not yet an economically complete EA. It has no Buy/Sell/PositionOpen path.

Therefore the exact MT5 Strategy Tester expectation for the present EA is **zero physical trades**. The meaningful precompile baseline is its internal event/proposal stream.

For an economic diagnostic only, the baseline also shadow-executed the subset that already has an explicit lifecycle in V1.05: the unit-003 session routes with their encoded TP/SL/300-second horizon, exact Dukascopy Bid/Ask first passage, and a $0.02 research round-trip cost.

That session-route shadow is **not** the January/February vertical-grid system we previously discovered. Watchdog renewal children, unlocks/layer depth, native specialist lifecycles and recovery funding are not yet economically wired.

## Jan–Jul decision baseline

| Month | Ticks | Grid events | Session routes | Native states | Watchdog candidates | Scouts admitted | Failed-ignition shadows |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jan | 9,135,062 | 15,252 | 3,021 | 4,816 | 287 | 57 | 2,646 |
| Feb | 7,538,339 | 17,118 | 2,687 | 5,570 | 78 | 26 | 2,472 |
| Mar | 9,433,179 | 19,026 | 3,004 | 6,325 | 429 | 89 | 2,775 |
| Apr | 7,470,570 | 10,384 | 1,743 | 3,351 | 252 | 80 | 1,682 |
| May | 8,333,165 | 9,416 | 1,505 | 3,109 | 239 | 77 | 1,464 |
| Jun | 8,201,406 | 10,402 | 1,473 | 3,546 | 294 | 85 | 1,430 |
| Jul | 7,415,841 | 8,820 | 1,268 | 2,667 | 199 | 72 | 1,234 |
| **Total** | **57,527,562** | **90,418** | **14,701** | **29,384** | **1,778** | **486** | **13,703** |

Watchdog unlocks are **0 by construction in the exact frozen skeleton**, because no renewal children are physically executed yet and therefore no realized child outcome can call the Watchdog outcome-update API.

## Session-route shadow economics

| Month | Trades | Net | PF | Win | Expectancy | Balance DD | Positive days |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jan | 3,021 | -$3,406.92 | 0.309 | 13.84% | -$1.128 | $3,465.32 | 2/18 |
| Feb | 2,687 | -$2,882.27 | 0.294 | 12.13% | -$1.073 | $2,885.58 | 0/20 |
| Mar | 3,004 | -$2,578.81 | 0.356 | 12.35% | -$0.858 | $2,586.52 | 1/22 |
| Apr | 1,743 | -$1,376.01 | 0.329 | 12.62% | -$0.789 | $1,378.35 | 0/22 |
| May | 1,505 | -$931.29 | 0.405 | 15.22% | -$0.619 | $950.57 | 0/22 |
| Jun | 1,473 | -$1,075.39 | 0.336 | 13.31% | -$0.730 | $1,079.73 | 0/23 |
| Jul | 1,268 | -$1,080.87 | 0.229 | 11.51% | -$0.852 | $1,080.87 | 1/23 |
| **Total** | **14,701** | **-$13,331.56** | **0.321** | **12.97%** | **-$0.907** | — | **4/150** |

## What this tells us before MetaEditor

This is useful precisely because it failed economically.

The frozen architecture is producing a large, deterministic opportunity stream, but the **raw session route is not a standalone edge**. Approximately 93% of session-route watches fail the V1 2-second / $1.25 ignition test. That makes the recovery and renewal layers economically central rather than optional decorations.

The massive January/February results we previously established came from the *full layered mechanics*: high-velocity renewal children, Watchdog earned admission and layer depth, session/hour geometry, native specialist lifecycles, recovery, and physical capacity allocation. V1.05 currently contains their state/interfaces but not all of their economic execution.

## Practical MT5 expectation

If the owner compiles **the exact current V1.05**, Strategy Tester should show:

- no physical trades;
- no trading PnL;
- a populated deterministic diagnostic CSV;
- session/grid/event/native/Watchdog/recovery/arbiter/governor state transitions.

That is the correct parity test.

Do **not** compare MT5 PnL to R9 SYNTH yet, because there is no order adapter and the economically decisive renewal/native/recovery lifecycles are not fully funded.

## Recommended next engineering sequence

1. MetaEditor compile V1.05.
2. Match MT5 diagnostic counts/state against this Dukascopy baseline.
3. Once parity passes, add the physical execution/lifecycle adapter **without changing the frozen spine**.
4. Reconstruct the accepted January Watchdog/renewal mechanics and February vertical refinements as V2 layer implementations.
5. Run Jan→Jul sequentially, carrying each accepted refinement forward and regression-testing all prior months.
6. Only after that compare blind later months.

The baseline prevents us from mistaking an internally coherent skeleton for the high-performance trading machine.