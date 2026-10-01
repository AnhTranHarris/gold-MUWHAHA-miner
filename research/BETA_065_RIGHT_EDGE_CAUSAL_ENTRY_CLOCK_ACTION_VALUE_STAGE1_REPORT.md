# BETA065 Stage-1 — Corrected RIGHT-Edge Causal Entry Clock + Action-Value Research

**Date:** 2026-10-01  
**Lineage:** independent BETA  
**Parent contract:** BETA063  
**Status:** COMPLETED NULL RESULT / NOT PROMOTED  
**August 2026:** SEALED / NOT READ  
**MQL5:** NOT AUTHORIZED

## Purpose

This is the first post-R18 new science unit. It deliberately does **not** reconstruct or inherit BETA064 Checkpoint-01/02/03 economics, the missing `beta064_multidesk_loop.py`, LEFT-edge caches, or guessed historical helper thresholds. The unit asks whether new RIGHT-edge causal opportunity clocks plus low-capacity specialist action-value models can discover executable after-spread value on the original January Dukascopy quote sequence.

## Source and timing

- Canonical January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`.
- Loaded 4,205,709 source ticks from `1767308400596` through `1768600799050`. The nominal diagnostic wall extends through Jan 18 12:00 UTC, but the source has no later market quotes after Friday Jan 16 21:59:59 UTC inside that wall.
- Completed 250 ms / 1 s / 5 s bars are observable only at their RIGHT edge.
- Raw V8 boundary interactions use actual observed tick time and source ordinal.
- BUY entry uses Ask, SELL entry uses Bid; exits use the opposite executable quote; $0.02 research round-trip fee is added.

## New independent clocks

1. `MICRO250_PERSIST`: completed 250 ms persistence with explicit state/retrigger/reset.
2. `V8_M1_BOUNDARY`: reconstructed public V8-style first-minute midpoint ±$0.50 interaction with bounded opposite-side rearm.
3. `RETEST_RENEW_1S`: completed 1 s displacement → retest → same-direction renewal finite-state clock.

The complete pre-ownership surface contains **371,013** proposals:

- MICRO250: 311,549
- V8 boundary: 36,572
- retest/renew: 22,892

Split counts: FIT 164,448, CAL 29,976, DIAGNOSTIC 176,589.

## Result

The frozen economic rule was **SKIP whenever predicted best executable action value ≤ $0**. On CAL, *every* predicted LONG/SHORT value remained below zero. The maximum CAL predicted best value was **-0.0773 dollars/trade**. Therefore no configuration produced the preregistered minimum of 20 positive-value CAL trades. The correct selected policy is:

> **SKIP_ALL — no trade is better than knowingly paying negative expected spread-adjusted value.**

No threshold was weakened and no negative-value trade was admitted to manufacture activity. Consequently the selected FIT/CAL/DIAGNOSTIC ledger contains zero trades and BETA065 does **not** pass the >10% review gate.

## Why the null result is still informative

The clocks do contain **hindsight capacity** at a 30-second horizon, but the tested causal models cannot identify the correct action in advance. Examples (hindsight side selection, not a strategy):

| Specialist / split | 30 s oracle-side mean after cost | oracle positive |
|---|---:|---:|
| MICRO250 / CAL | $0.113 | 42.7% |
| V8 M1 / CAL | $-0.002 | 37.2% |
| RETEST/RENEW / CAL | $0.181 | 45.2% |
| MICRO250 / diagnostic | $0.253 | 49.0% |
| RETEST/RENEW / diagnostic | $0.327 | 52.8% |

By contrast, simply following each clock's original direction remains about **-$0.7 to -$0.8/trade** after executable Dukascopy spread. This sharply narrows the problem: **the next bottleneck is causal side/phase discrimination and wait-vs-act timing, not lack of movement and not proposal count.**

## QA

Independent QA passed **25/25** checks, including canonical source SHA, strict chronology, RIGHT-edge 250 ms and 1 s event alignment, synthetic right-edge fixture, event identity between proposal/prediction surfaces, finite features, artifact hashes, August sealed state, and the negative CAL value surface.

## Promotion decision

**REJECT FOR PROMOTION / KEEP AS DURABLE NULL RESULT.**

BETA063 remains the rollback parent. `CURRENT_STATE.json` must not advance to BETA065 as a promoted checkpoint.

## Recorded next scientific action

The next bounded unit should keep these three RIGHT-edge clocks and attack the demonstrated gap directly: **30-second causal action discrimination plus explicit WAIT_SHORT option value**, using nonlinear but bounded specialist interactions and preserving the same pre-ownership surface. The unit must preregister before testing, train only on FIT, select only on CAL, and must not use the diagnostic span to choose features/thresholds. If a new action model still cannot produce positive CAL expected value, the clocks themselves should be demoted rather than relaxing the economic gate.