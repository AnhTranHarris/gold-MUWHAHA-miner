# BUILD-02 Session + Timeframe Awareness — January Report

**Unit:** `DAA_GRID_SYSTEM_BUILD_02_SESSION_TIMEFRAME_AWARENESS`  
**Candidate:** `STMR-001`  
**Status:** ACCEPTED AS JANUARY SESSION/TIMEFRAME RESEARCH FLOOR  
**External validation:** NOT YET — Jan-Jul remains required later.

## Structural result

The session/timeframe research produced one durable mechanism family:

**Session–Timeframe Morphing Router (STMR)**

Instead of asking whether all timeframes agree, STMR assigns ownership:
- H4/H1 describe the slower environment;
- M15 describes the intraday phase;
- M5 can initiate a handoff;
- ordered ticks own first-touch grid timing and fills;
- session boundaries restart the finite grid cycle and spatial memory.

Generic recrossing, timer-only rearm, generic sweep fading, timeframe unanimity, and state-episode micro-lattices were rejected during exploratory screening.

## Clean preregistered January replay

Canonical Dukascopy source:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Surface:
`DUKAS_COINEXX_LIKE_P75`

Fixed lot:
`0.01`

Maximum simultaneous grid-owned positions:
`3`

Aggregate January result after warmup:
- trades: **867**
- net: **+$416.23**
- PF: **1.602**
- win rate: **39.56%**
- expected payoff: **+$0.4801/trade**
- active days: **20**
- trades/active day: **43.35**

January split:
- through Jan 16: **167 trades, +$56.21, PF 1.476**
- Jan 17 onward: **700 trades, +$360.02, PF 1.628**

Both halves remained positive. This split is a January stability diagnostic, not external OOS proof.

## Route ledger

| Route | Trades | Net | PF | Expected payoff |
|---|---:|---:|---:|---:|
| Asia reversal initiation | 173 | +$80.19 | 1.644 | +$0.4635 |
| London micro relay | 189 | +$69.81 | 1.508 | +$0.3694 |
| Overlap lower-TF takeover | 367 | +$208.13 | 1.623 | +$0.5671 |
| NY mixed-macro relay | 41 | +$17.71 | 1.700 | +$0.4320 |
| Late-NY lower takeover | 97 | +$40.39 | 1.576 | +$0.4164 |

Every executed route was positive in the exact concurrent portfolio.

The overlap route is responsible for roughly half of the January net and is strongly concentrated in the later January half. Treat that as concentration risk requiring later month validation.

## Risk / survivability diagnostic

- max balance drawdown: **$68.50**
- max equity drawdown: **$71.01**
- minimum equity relative to initial start: **-$0.29**
- max simultaneous positions: **3 / 0.03 lots**
- theoretical $100-start minimum equity: **$99.71**
- theoretical $200-start minimum equity: **$199.71**
- theoretical $300-start minimum equity: **$299.71**
- average hold: **11.7 sec**
- maximum hold: **251.3 sec**
- TP exits: **343**
- SL exits: **524**
- age exits: **0**
- forced residual liquidations: **0**

The large peak-to-trough drawdown and small minimum-from-start are not contradictory: the account first accumulated gains, then experienced drawdown from a higher equity peak.

## R9 perspective

This build is not near R9 SYNTH throughput yet.

R9 SYNTH January:
- 27,980 trades
- +$41,520.82 net
- PF 21.04
- +$1.4839 expected payoff
- ~1,332 trades/day

STMR-001:
- 867 trades
- +$416.23
- PF 1.602
- +$0.4801 expected payoff
- 43.35 trades/day

The important result is architectural, not milestone attainment:

**session/timeframe awareness changed the grid from a losing bounded physical mechanism into a positive, bounded, short-horizon event router on January ticks.**

It currently contributes only a small fraction of the required whole-system throughput, so later dimensions must add opportunity recovery rather than simply filter STMR harder.

## Important negative finding

M1 confirmation was not automatically beneficial. Adding another agreement layer frequently reduced or destroyed the edge.

The strongest current relay is:

`H4/H1 environment -> M15 phase -> M5 handoff -> tick first-touch`

This supports the project's anti-voting architecture.

## Durable implementation

System integration:
`research/delta_a_alpha/experiments/grid_system_session_timeframe.py`

Preregistration:
`research/delta_a_alpha/grid/DAA_GRID_SYSTEM_BUILD_02_SESSION_TIMEFRAME_AWARENESS_PREREG.md`

Source hunt:
`research/delta_a_alpha/research/DAA_GRID_SESSION_TIMEFRAME_SOURCE_HUNT_003.md`

The system integration module binds session handoffs to BUILD-01 finite-cycle restarts and writes timeframe states into BUILD-01's role contract. It contains no MT5 order authority.

A portable local replay helper was independently rebuilt and reproduced the clean result byte-for-byte at the metric level. Local helper SHA-256:
`deb2323932a2ae34d0e0433a501e949f652e8f6dc45930cf5192a7b741c82768`

The GitHub connector rejected the large replay/result payload mutation through its safety layer; this report therefore records the verified result while avoiding any attempt to bypass that connector guard.

## Scientific decision

**ACCEPT STMR-001 as the January session/timeframe floor.**

Do not interpret this as Jan-Jul promotion or MT5 authorization.

Next whole-system work should build vertically on STMR-001. Elastic geometry is the logical next dimension because session-local fixed gaps are already route-dependent, but they remain static inside each route.
