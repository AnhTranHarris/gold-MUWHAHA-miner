# DELTA 005C-001 — Failed-Break / Sweep-Reversal Specialist

**Status:** PREREGISTERED  
**Mode:** historical Python simulation only  
**Campaign:** DELTA_005 Entry + Initial-Hold  
**Parent findings:** DELTA_005A-001 and DELTA_005B-001  
**Mature Hold/Exit/High-Profit optimization:** prohibited  
**August 2026:** sealed

## Research question

Does the first-touch population rejected by the mild-flow continuation specialist contain useful **opposite-direction failed-break behavior** rather than delayed continuation?

005A showed that hard flow filtering improves losses primarily by deleting activity.
005B showed that a simple continuation retest does not recover that activity.
005C therefore changes the ownership thesis rather than tightening either formula.

## Public reconstructible provenance

Open/public fakeout and sweep concepts used only as sequence inspiration:
- TradingView open-source Gold H1 breakout-failure/fakeout logic.
- Public liquidity-sweep/reclaim discussions.
- MQL5 Gold zone recovery/retest patterns.

No public profit claim is treated as evidence.

## Ownership router

At the first valid R9-style historical opportunity:

### Direct continuation owner
If 250 ms and 1 s tick flow agree with the original break direction, the direct continuation sleeve enters.

### Failed-break owner
If direct flow is not aligned, the break is handed to 005C.

005C waits for:
1. midpoint to establish the original virtual-boundary break;
2. midpoint to cross back through the broken boundary by the failure buffer;
3. 250 ms and 1 s tick flow to agree in the **opposite** direction;
4. the R9 regime/spread eligibility gate to remain open.

The reversal entry is opposite the original break:
- failed BUY break -> SELL;
- failed SELL break -> BUY.

The original completed-S1 directional condition is used to define the attempted break but is **not required to flip** before reversal entry; otherwise the specialist would use a slow hindsight-like confirmation for a fast failure event.

## Causality

All failure and flow conditions use only current/past ticks.
Sequence geometry uses modeled midpoint.
Execution remains modeled Ask/Bid.
No future MFE/MAE, target outcome, or post-entry label is used.

## Frozen grid

Failure depth beyond the broken boundary:
- $0.00
- $0.02
- $0.05

Opposite-flow threshold, applied to both 250 ms and 1 s flow:
- 0.00
- 0.10
- 0.20

Maximum break-to-failure-entry time:
- 1,000 ms
- 3,000 ms
- 5,000 ms

Total configurations: 27.

No new values may be introduced before the grid is saved and reviewed under GOV-013.

## State rules

- original break must occur before failed-break confirmation;
- failure must occur after the break;
- once ownership transfers to 005C, that break cannot later enter through 005A;
- minute reset cancels unfinished 005C state;
- timeout cancels unfinished state;
- one simulated position at a time;
- opposite reversal entry uses the same fixed 0.01-lot accounting surface.

## Downstream lifecycle

After reversal entry, the preserved R9-style hard stop, trail, max-duration, accounting, and post-exit state machine remain unchanged.

This is not mature-hold/exit/high-profit research.

## Required diagnostics

For every configuration:
- total trades/wins;
- direct continuation entries/wins where supported;
- failed-break reversal entries;
- reversal wins;
- reversal sleeve win rate;
- break attempts;
- timeout/cancel counts;
- gross positive/negative outcome;
- net result;
- balance drawdown;
- activity retention vs Stage-A parent;
- activity change vs 005A anchor;
- 1/3/5/10/15-second survival;
- MFE/MAE horizons.

## Decision

005C is valuable only if it converts a meaningful portion of rejected opportunities into a stronger opposite-direction population without destroying the direct-continuation sleeve.

If the reversal sleeve is weak, the next major leverage target becomes a dedicated **initial-hold state machine** rather than further entry-routing complexity.
