# GRID-001 January Volatility-Expansion Route 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_VOL_EXPANSION_ROUTE_001`  
**Status:** FROZEN BEFORE COMPUTE  
**Role:** high-confidence route inside the R9 Delta-A-alpha grid opportunity engine

## Hypothesis

A grid event occurring during a short-over-long volatility expansion may have materially different continuation economics than the broad event population.

This unit formalizes an earlier scratch clue on the **current A05 adaptive lattice**. The scratch result is hypothesis-generating only.

## Event clock

Use A05 from Adaptive Spacing Screen 001:
- completed-M1 ATR(14);
- gap = 0.50 × ATR;
- clamp $0.75–$5.00;
- quantize $0.10;
- frozen per event.

## Volatility expansion state

At event time, using completed M1 bars only:

`expansion_ratio = ATR14 / ATR240`

Two frozen gates:
- 1.75
- 2.00

These are a sensitivity pair, not an optimizer.

## Continuation proof

Only events passing the expansion gate are eligible.

From the event midpoint:
- require movement in the crossing/continuation direction by **1.00 event gap**;
- proof must occur within **3 seconds**;
- otherwise abstain.

No opposite-direction trade is allowed in this unit.

## Physical trade

After proof:
- one fixed 0.01 continuation trade;
- entry at executable Ask for long / Bid for short;
- target = **+1.50 event gaps** from actual entry;
- stop = **original event midpoint**;
- exit must occur by the original event timestamp + 5 minutes;
- no horizon reset;
- no second trade or recovery.

## Single-owner rule

At most one physical route-owned trade may be open at once.

Any event born while a route trade is active is suppressed for this unit.

## Economics

- fixed 0.01;
- $0.02 round-trip commission;
- modeled executable P75 Bid/Ask;
- zero slippage on the frozen research surface;
- no averaging;
- no Martingale.

## Required outputs

For both 1.75 and 2.00:
- eligible events before proof;
- proven candidates;
- single-owner trades;
- suppressed events;
- trades/active day;
- net / gross profit / gross loss / PF / expectancy / win rate;
- discovery and validation;
- max balance drawdown;
- max equity drawdown;
- minimum equity delta;
- $100/$200/$300 positive-equity diagnostic;
- target/stop/timeout counts.

## Advancement

This route becomes a January **candidate mechanism**, not a promoted system, only if:
- full PF > 1;
- discovery and validation are both non-negative or near-neutral with the same qualitative sign;
- both 1.75 and 2.00 sensitivity gates remain qualitatively useful;
- drawdown is compatible with $100 starting-equity diagnostics;
- result does not depend on multiple simultaneous grid positions.

No further threshold/target tuning is authorized in this unit.

August sealed. Main `delta` read-only. MQL5 unauthorized.
