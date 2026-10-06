# GRID-001 January Event-Label Lab 001

**Status:** COMPLETE STRUCTURAL DIAGNOSTIC  
**Dataset:** full January 2026 canonical Dukascopy XAUUSD ordered ticks  
**Surface:** `DUKAS_COINEXX_LIKE_P75`

## What was tested

The creator's grid was converted into a **virtual event lattice**. The source-like H1/48-bar rolling extreme and chained $1 spatial logic were retained, but no physical averaging positions were opened.

Every event was evaluated in two bounded shadow interpretations:
- mean reversion;
- continuation.

Each shadow used:
- 1-gap target;
- 1-gap adverse bound;
- 5-minute maximum horizon;
- executable Bid/Ask;
- $0.02 round-trip commission;
- forced executable exit at horizon if unresolved.

This was deliberately an event-label experiment rather than another grid strategy.

## Event supply

January produced **130,133 virtual events** across **22 active event days**, or about **5,915 events/day**.

For scale, canonical R9 SYNTH January generated 27,980 trades, roughly 1,332 trades/active day.

Therefore the grid/lattice produces much more opportunity density than the final system needs. We can reject or shadow a large majority of events and still retain R9-scale throughput.

## Naive direction baselines

Always mean reversion:
- net: **-$34,543.89**
- PF: **0.656**
- expected payoff: **-$0.265/event**
- wins: **40.60%**

Always continuation:
- net: **-$22,453.82**
- PF: **0.762**
- expected payoff: **-$0.173/event**
- wins: **43.22%**

Neither universal interpretation is viable.

## Direction-oracle ceiling

An impossible future-aware oracle that selects the better of MR or continuation for each event produced:

- net: **+$114,890.26**
- PF: **6.05**
- expected payoff: **+$0.883/event**
- wins: **83.82%**

Exactly one interpretation was profitable on about **83.82%** of events; both were negative on about **16.18%**.

This is not a candidate strategy. It is a research ceiling proving that the event clock contains substantial directional opportunity if classification can be improved.

The same qualitative result strengthened in the final one-third tick validation segment:
- oracle net: **+$86,889.39**
- oracle PF: **6.62**
- oracle expected payoff: **+$0.952/event**

## Pre-crossing classification probe

Causal features tested included:
- signed displacement from 1s through 5m;
- path length;
- directional efficiency;
- event pace;
- virtual chain depth;
- rolling-H1 range position.

A coarse efficiency router did not solve the problem. Its best full-January result remained **-$31,369.03 / PF 0.683**.

A shallow decision-tree probe trained only on the first 2/3 of January ticks also failed to beat the simpler always-continuation baseline on the final 1/3 validation segment.

This is useful negative evidence: **the direction is not reliably encoded in the simple path state immediately before the crossing.**

## Structural interpretation

The first major January result is:

> The grid is already generating more than enough opportunities. The bottleneck is determining what a crossing means.

This changes the next mutation.

Instead of adding more pre-event filters, the next experiment should allow the lattice crossing to become an **observation trigger**. The system may watch a short causal post-crossing probe before committing capital.

Candidate concept:

`EVENT -> OBSERVE 0.25–5s -> CONT / MR / ABSTAIN -> bounded 0.01 entry`

That is still causal because the physical entry occurs only after the observation interval.

If the event initially moves one way and then reclaims, that path itself may contain the directional information that was missing before the crossing.

## Decision

KEEP:
- virtual lattice;
- very high event density;
- dual counterfactual labels;
- event identity.

REJECT:
- automatic contrarian semantics;
- automatic continuation semantics;
- simple pre-crossing efficiency router as sufficient solution.

NEXT:
**causal post-crossing observation / probe gate**, followed only if justified by early-failure and opportunity-recovery work.

No Jan–Jul promotion has occurred. August remains sealed.
