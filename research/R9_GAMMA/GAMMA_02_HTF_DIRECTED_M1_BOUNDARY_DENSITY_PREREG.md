# GAMMA-02 — HTF-Directed M1 Boundary Density Preregistration

**Parent branch:** carson/r9-gamma-02-velocity-geometry-research  
**Parent checkpoint:** feda57b51f24e5bcbf8f83fdd3851b3ca544c27d  
**Discovery month:** January 2026 ordered Dukascopy Bid/Ask ticks only  
**August:** SEALED

## Hard objective

Increase correct-direction opportunity density aggressively enough that later specialist layers can approach R9-SYNTH-class trade velocity and profitability. Small cosmetic improvement is not sufficient.

R9 SYNTH remains the hard reference ceiling:
- +$309,122.85 Jan-Jul net
- PF 20.036
- 219,342 trades
- 87.14% win rate
- +$1.409319 expectancy/trade
- ~16 second average hold

The current earned January quality anchor is the fast runner-shadow frontier:
- +$1,425.30
- 1,400 trades
- PF ~1.9875
- +$1.018 expectancy/trade
- ~10 second shadow lifecycle
- explicit maximum combined exposure 7 x 0.01 lots

## Community-derived mechanics to test

These are hypotheses only; no community performance claim is inherited.

1. Break -> retest -> re-break state machines around fresh levels.
2. Favorable-direction pyramiding / add-on entries only after price proves continuation.
3. Multi-specialist execution rather than forcing one lifecycle across all states.
4. M1 execution under higher-timeframe confluence.
5. Explicit aggregate exposure/heat measurement.

## Creative hypothesis family A — Fresh M1 directional ladder

Every new M1 minute creates a fresh causal anchor. HTF state owns direction. A trade opportunity exists only when price crosses a new favorable boundary away from the minute anchor. Multiple levels may fire in a strong minute, but each level is one-shot.

Purpose: turn one directional state into many distinct breakout opportunities without repeated-tick duplication.

## Family B — Pullback / re-break recycler

After a trend-direction boundary fires, re-arm only if price causally retraces inside the level by a minimum reset distance and then re-breaks in the HTF direction.

Purpose: harvest repeated auction pulses while rejecting continuous beyond-boundary spam.

## Family C — Favorable-extreme stair-step

Maintain the live session/minute favorable extreme. Each new extension by a fixed step creates another independent entry opportunity. No add-on is allowed unless price has moved favorably since the prior add.

Purpose: emulate disciplined pyramiding / trend harvesting without averaging down.

## Family D — Campaign heartbeat

When a strong HTF alignment state is live in London / overlap / New York, create a bounded campaign. Additional entries require BOTH elapsed time and price still being on the favorable side of the minute anchor / micro reference.

Purpose: high trade count during sustained directional auctions without using raw tick velocity as the direction predictor.

## HTF permission states

Discovery will compare:
- ALIGN4: H4 = H1 = M15 = M5 != 0.
- MACRO3: H4 = H1 = M15 != 0; M5 may be pullback or aligned.
- MACRO2: H4 = H1 != 0; lower timeframes determine entry timing.
- Existing funded STMR sleeve state, as the strict control.

London / overlap / New York windows receive priority. Asia and late-session states remain available as controls, not the volume target.

## Scientific constraints

- Ordered executable Bid/Ask.
- Completed-bar HTF states only.
- Fixed 0.01 per ticket.
- No Martingale, no loss-dependent sizing, no averaging down.
- Every duplicate/re-entry requires an explicit causal reset, favorable extension, or elapsed-time condition.
- Transaction cost stays encoded in the existing harness.
- Exposure and maximum simultaneous positions reported explicitly.
- January is discovery and may overfit; no promotion without later Jan-Jul replay.
- No MQL5 build in this unit.
- Parent STMR/GAMMA-01 savepoint is immutable.

## Atomic research discipline

Each mechanism family is run as a bounded job and immediately persisted as:
1. exact helper,
2. exact JSON result,
3. compact summary,
4. GitHub checkpoint.

A timed-out job with no final artifact is NOT evidence and will be rerun only in the missing chunk.
