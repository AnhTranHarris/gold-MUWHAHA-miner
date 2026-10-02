# DELTA R003 — Causal Direction + Initial-Hold Research Vocabulary

**Status:** RESEARCH_ONLY / NO TESTING / NO ACTIVE CANDIDATE  
**Parent:** `DELTA_004_COINEXX_LIKE_DUKASCOPY_RESEARCH_SURFACE`  
**Scope:** ENTRY + INITIAL-HOLD  
**Drive document:** https://docs.google.com/document/d/1ei6AcvQUO1Wzx4EUlVaCGWjdl6pCBajcjrzWEtMs3-w/edit  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Core research definitions

- **Direction** = signed orientation of a causally observable state.
- **Character** = behavior of that state: orderly/trending, noisy, compressed, expanding, stressed, mean-reverting, transitional, normal/unclassified.
- **Structural direction** = latest causally confirmed higher-order structure. Future pivots may not be projected backward.
- **Intermediate swing direction** = medium-horizon impulse/pullback state inside structural direction.
- **Fast execution direction** = shortest-horizon direction usable by an entry specialist from causal ticks/completed bars.
- **Trend strength** = magnitude, not sign.
- **Pullback** = lower-level counter-direction move while parent structure remains causally intact.
- **Reversal** = explicit change of directional ownership; not merely a losing trade or lower-timeframe disagreement.
- **Transition** = prior ownership weakening/conflicting while opposite ownership is not yet confirmed.
- **Breakout** = causal crossing of a boundary known before the cross.
- **Acceptance** = post-break evidence that the new side is sustaining.
- **Retest** = return toward the broken boundary without invalidation.
- **Rebreak** = renewed move away from the retest in breakout direction.
- **Failed break** = attempted breakout that loses acceptance and causally reclaims the prior side with opposite confirmation.
- **Compression / expansion** = low-energy state followed by causal movement/volatility increase, with exact estimator pending.
- **Intrinsic-time directional change** = threshold reversal from a running extreme; event clock advances on price events.
- **Overshoot** = continuation after directional-change confirmation until the next opposite change event.
- **Quote pressure** = DELTA-available top-of-book/tick proxy; never call it true centralized OFI without data support.
- **Hysteresis** = stronger evidence may be required to flip a state than to maintain it.
- **Specialist ownership** = event grammar assigns the opportunity to a specific specialist.
- **Router** = context controller deciding which specialist may evaluate an opportunity.

## Initial-hold state machine vocabulary

`UNCONFIRMED -> PERSISTING / STALLING / RETREATING -> INVALIDATED or MATURE_HANDOFF`

- UNCONFIRMED: filled, but continuation not established.
- PERSISTING: early path remains consistent with specialist thesis.
- STALLING: progress weakens without structural invalidation.
- RETREATING: adverse move exceeds ordinary continuation noise, but thesis may remain valid.
- INVALIDATED: specialist thesis causally broken.
- MATURE_HANDOFF: initial-hold phase succeeded; future mature hold/exit layer would take control. That later layer remains out of scope.

## Candidate grammar

Every future candidate must eventually define:

`CONTEXT -> ARM -> CONFIRM -> ENTER -> INITIAL-HOLD STATE -> INVALIDATE or MATURE_HANDOFF`

Minimum required fields:
1. causal inputs;
2. update clock/event;
3. arm condition;
4. confirmation condition;
5. expiration;
6. invalidation;
7. reset/rearm;
8. ownership transfer;
9. output state;
10. live features vs offline labels.

## Offline-only labels

Later research may label 250ms, 1s, 3s, 5s, 10s, and 15s survival/MFE/MAE outcomes. These are forbidden as live features.

## Research implication

The vocabulary is intentionally compatible with:

`context/regime -> specialist entry event -> specialist-aware initial hold`

rather than one global R9 direction filter and one generic early lifecycle.

## Sources

- https://www.mql5.com/en/articles/23852
- https://www.mql5.com/en/articles/23043
- https://www.mql5.com/en/articles/22940
- https://www.mql5.com/en/articles/23628
- https://www.mql5.com/en/articles/23814
- https://arxiv.org/abs/2007.14874

## Gate

No thresholds, optimization, Stage-A candidate, Python replay, August access, or MQL5 implementation has been authorized.
