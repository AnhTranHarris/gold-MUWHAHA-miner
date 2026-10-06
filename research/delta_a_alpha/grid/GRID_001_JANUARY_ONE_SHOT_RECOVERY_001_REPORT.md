# GRID-001 January One-Shot Opportunity Recovery 001

**Status:** COMPLETE / BLIND RECOVERY REJECTED / RECOVERY OPPORTUNITY RETAINED

## Question

After an A10/A15 continuation event fails the frozen early-thesis rule, should the system immediately flip once into the opposite direction, or retire the event?

## Frozen recovery contract

The parent continuation trade used Early Thesis Failure 001 unchanged:

- favorable proof at +0.25 event gap;
- early failure at -0.50 event gap;
- confirmed +1.00 TP / -1.00 hard stop;
- five-minute original event horizon.

Only EARLY_THESIS_FAILURE events could recover.

Recovery:
- one opposite-direction trade only;
- entry at the same executable quote where the failed continuation exits;
- +1.00 event-gap TP;
- -1.00 event-gap SL;
- no horizon reset;
- no second flip;
- fixed 0.01;
- no Martingale;
- $0.02 round-trip commission per leg.

## A10

Early-failure eligible:
- **7,118 events / 44.10%**

Blind recovery leg:
- net: **-$1,253.36**
- PF: **0.8941**
- expectancy: **-$0.1761**
- wins: **46.77%**

RETIRE parent:
- **-$1,445.11 / PF 0.9375**

ONE-SHOT RECOVERY:
- **-$2,698.47 / PF 0.9075**

Therefore blind recovery worsens the system.

But the diagnostic selective oracle that recovers only when the recovery leg is profitable reaches:
- full January: **+$9,131.54 / PF 1.5267**
- discovery: **+$1,708.44 / PF 1.2794**
- validation: **+$7,423.10 / PF 1.6615**

## A15

Early-failure eligible:
- **4,553 events / 40.90%**

Blind recovery leg:
- net: **-$1,085.16**
- PF: **0.8878**
- expectancy: **-$0.2383**
- wins: **46.74%**

RETIRE parent:
- **-$673.97 / PF 0.9661**

ONE-SHOT RECOVERY:
- **-$1,759.13 / PF 0.9290**

Again, blind recovery worsens the system.

Selective oracle:
- full January: **+$7,910.57 / PF 1.5242**
- discovery: **+$1,036.52 / PF 1.2524**
- validation: **+$6,874.05 / PF 1.6259**

## Structural interpretation

The opportunity-recovery hypothesis survives, but not as an automatic stop-and-reverse rule.

Roughly **47%** of early-failure events have a profitable opposite-direction recovery leg. That is below the threshold required for blind flipping, especially after friction.

However, the selective oracle is positive in both chronological segments and materially stronger in the final third. This means early thesis failure often leaves a valuable opportunity alive.

The next research bottleneck is therefore:

> **RECOVERY ADMISSION**

At the exact early-failure timestamp, use only causal information already available to decide:

- FLIP once;
- WAIT / RE-ARM;
- RETIRE.

The question is no longer whether recovery exists. It does.

The question is whether the recoverable subset can be identified without future information.

## Decision

REJECT:
- blind immediate opposite-direction recovery;
- tuning recovery TP/SL before admission is solved;
- multiple recovery flips.

KEEP:
- early failure as a recovery decision point;
- exactly-one-flip architecture;
- A10/A15 adaptive geometry;
- counterfactual recovery shadow as a diagnostic ceiling.

NEXT:
**causal recovery-admission lab at the early-failure timestamp.**

Candidate feature families should focus on information created by the failure itself:
- time-to-failure normalized by event gap;
- failure velocity / overshoot;
- recent directional efficiency;
- reclaim/acceptance state;
- event gap / local volatility;
- parent/child event age;
- whether adverse movement is accelerating or exhausting.

No session/news categories yet.

August remains sealed. Main `delta` remains read-only. MQL5 remains unauthorized.
