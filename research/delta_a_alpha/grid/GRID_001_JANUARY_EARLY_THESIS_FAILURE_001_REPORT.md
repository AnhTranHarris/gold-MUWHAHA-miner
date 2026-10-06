# GRID-001 January Early Thesis Failure 001

**Status:** COMPLETE / PARTIAL STRUCTURAL SUCCESS  
**Dataset:** full January 2026 canonical Dukascopy XAUUSD ordered ticks  
**Surface:** `DUKAS_COINEXX_LIKE_P75`

## Question

Can adaptive-lattice continuation reduce gross loss by requiring early favorable evidence before granting the trade its full loss budget?

## Frozen contract

Lattices:
- A10
- A15

Direction:
- continuation only

State:
- starts `UNCONFIRMED`;
- proof of life at **+0.25 event gap**;
- provisional early-failure exit at **-0.50 event gap**;
- after confirmation, original **+1.00 TP / -1.00 hard stop** applies;
- 5-minute horizon;
- fixed 0.01 economics;
- $0.02 round-trip commission;
- no averaging;
- no Martingale;
- no physical overlap/margin model in this unit.

This was intentionally one proof-of-life rule only. No threshold sweep was performed.

## A10

Baseline continuation:
- net: **-$1,753.09**
- gross profit: **$26,651.73**
- gross loss: **-$28,404.82**
- PF: **0.9383**
- expectancy: **-$0.1086/event**

Early-thesis-failure:
- net: **-$1,445.11**
- gross profit: **$21,685.67**
- gross loss: **-$23,130.78**
- PF: **0.9375**
- expectancy: **-$0.0895/event**

Effect:
- gross loss reduced by **$5,274.04 / 18.57%**
- full-January net improved by **$307.98**
- **44.10%** of events failed before confirmation
- **55.89%** reached proof-of-life

Discovery:
- baseline: **-$2,350.07 / PF 0.7702**
- early-failure: **-$1,989.22 / PF 0.7566**

Validation:
- baseline: **+$596.98 / PF 1.0328**
- early-failure: **+$544.11 / PF 1.0364**

A10 therefore reduces the loss budget materially and improves aggregate net, but it does so while cutting gross profit and does not cleanly improve PF in both chronological segments.

## A15

Baseline continuation:
- net: **-$514.19**
- gross profit: **$23,330.11**
- gross loss: **-$23,844.30**
- PF: **0.9784**
- expectancy: **-$0.0462/event**

Early-thesis-failure:
- net: **-$673.97**
- gross profit: **$19,192.52**
- gross loss: **-$19,866.49**
- PF: **0.9661**
- expectancy: **-$0.0605/event**

Effect:
- gross loss reduced by **$3,977.81 / 16.68%**
- full-January net worsened by **$159.78**
- **40.90%** of events failed before confirmation
- **58.92%** reached proof-of-life

Discovery:
- baseline: **-$1,108.84 / PF 0.8247**
- early-failure: **-$1,030.86 / PF 0.8066**

Validation:
- baseline: **+$594.65 / PF 1.0339**
- early-failure: **+$356.89 / PF 1.0245**

A15 confirms the gross-loss-control effect, but the universal proof rule over-prunes profitable paths.

## Structural interpretation

This experiment answers the primary question positively but only halfway.

The state-machine concept works:

> weak continuation should not automatically receive the same loss budget as a continuation event that demonstrates favorable path behavior.

Both A10 and A15 reduce gross loss by roughly **17–19%**.

However, the fixed proof/failure rule is too indiscriminate. It also cuts eventual winners. Therefore this is not permission to tune `0.25` and `0.50` repeatedly.

The more important next question is what an **early-failure event means**.

Once continuation fails quickly, three possibilities exist:

1. the opportunity is dead → RETIRE;
2. new information is needed → RE-ARM WAIT;
3. the failure itself is evidence of a wrong initial direction → one bounded RECOVERY FLIP.

That is exactly the opportunity-recovery problem defined in the Delta-A-alpha architecture.

## Decision

KEEP:
- unconfirmed/confirmed trade state;
- conditional risk budget;
- early thesis-failure concept;
- A10/A15 adaptive lattice.

DO NOT PROMOTE:
- universal +0.25/-0.50 thresholds as final logic;
- threshold micro-optimization;
- physical execution candidate yet.

NEXT:
**analyze early-failure events directly and test one-shot causal recovery versus retirement.**

The next unit should preserve event identity and allow at most one bounded opposite-direction recovery after early failure. It must compare:
- no recovery / retire;
- one-shot recovery;
- counterfactual opportunity ceiling after early failure;
- discovery vs validation behavior.

August remains sealed. Main `delta` remains read-only. MQL5 remains unauthorized.
