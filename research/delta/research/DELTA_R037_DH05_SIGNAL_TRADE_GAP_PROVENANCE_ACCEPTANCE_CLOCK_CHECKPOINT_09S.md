# DELTA R037 — DH05 Signal/Trade Gap Provenance + Acceptance-Clock Ownership — Checkpoint 09S

**Status:** COMPLETE MATERIAL PROVENANCE CLUE / NON-PROMOTING CHALLENGER  
**Unit:** R037_DH05_SIGNAL_TRADE_GAP_PROVENANCE_AND_ACCEPTANCE_CLOCK_OWNERSHIP_DIAGNOSTIC  
**Parent:** R037_DH05_COMPLETED_BAR_BOUNDARY_INVALIDATION_CHECKPOINT_09R  
**Raw tick replay:** NOT IN THIS UNIT  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Purpose

09M–09R repeatedly failed to reconstruct the preserved historical trade-density gap through downstream execution persistence.

This bounded provenance diagnostic therefore asked whether the gap is instead structured by existing DH05 timeframe categories and previously preserved Checkpoint-08/09 semantics.

No raw tick data was accessed and no parameter was fitted.

## Provenance

- producer commit: `20689a8b985e1b30f76f46a1c24a03447c877e95`
- producer blob: `f23f2f97f38e5805b812c89aa32fe4aa97022258`
- producer SHA-256: `39635fb853d69f252171df2a583a412f2f73ff184f3dbcf671aa3635ef2c6087`
- result SHA-256: `bdf70beacf69f00b6f002190beae6cbc47905710368409664930783149948b27`

## Structural split

Frozen POST_QUAL signal counts versus preserved historical trades:

- A03: 192 -> 306 = **1.59x**
- S05: 9 -> 51 = **5.67x**
- S06: 651 -> 615 = **0.94x**
- S09: 11 -> 119 = **10.82x**
- S10: 227 -> 206 = **0.91x**
- S16: 7 -> 24 = **3.43x**

Acceptance-timeframe grouping is perfectly sign-separated in the six frozen vectors:

### acceptance_tf = S5
S06 + S10:
- both historical trades are **below** POST_QUAL signals;
- mean target/signal ratio: **0.9261**;
- aggregate absolute gap: **57**.

### acceptance_tf = S15
A03 + S05 + S09 + S16:
- all historical trades are **above** POST_QUAL signals;
- mean target/signal ratio: **5.3768**;
- aggregate absolute gap: **281**.

This is a strong fingerprint but not causal proof.

## Preserved Checkpoint-09 semantics

Checkpoint 09 documented two causal feature families:

**NEUTRAL**
- event M5 ATR;
- one-bar directional efficiency.

**STAGE_NORM_3BAR**
- reversal-timeframe ATR;
- signed 3-bar directional efficiency.

And two failure-clock interpretations:
- current/bounded failure clock;
- wait for causal reentry, then start max-failure clock.

Preserved aggregate count errors against historical trades:
- NEUTRAL_CURRENT: **289**
- NEUTRAL_WAIT_REENTRY: **286**
- STAGE_CURRENT: **264**
- STAGE_WAIT_REENTRY: **445**

None is universal parity.

## Predeclared categorical routers

### Acceptance-clock router

Rule:
- acceptance_tf = S5 -> NEUTRAL_CURRENT
- acceptance_tf = S15 -> NEUTRAL_WAIT_REENTRY

Fingerprint:
- A03 282 / 306
- S05 54 / 51
- S06 617 / 615
- S09 11 / 119
- S10 206 / 206
- S16 22 / 24

Aggregate error: **139**.

### Clock-topology router

Rule:
- acceptance_tf = S5 -> NEUTRAL_CURRENT
- acceptance_tf = S15 and reversal_tf = S5 -> NEUTRAL_WAIT_REENTRY
- acceptance_tf = S15 and reversal_tf = S1 -> STAGE_WAIT_REENTRY

Fingerprint:
- A03 **282 / 306**
- S05 **54 / 51**
- S06 **617 / 615**
- S09 **89 / 119**
- S10 **206 / 206**
- S16 **22 / 24**

Aggregate error: **61**.

For comparison:
- best 09L live clue: **304**
- 09R execution branch: **359**
- raw POST_QUAL signal-gap error: **338**

Thus the topology router is a large **provenance breakthrough candidate**, roughly 80% lower aggregate count error than 09L.

## Why it is not promoted

1. The transient Checkpoint-08/09 producer bytes are not recoverable.
2. Current DELTA semantics freeze max-failure age from FAILURE_CANDIDATE.
3. The S15/S1 branch is represented by only one frozen vector, S09.
4. Selecting a historical profile per category from six points can overfit even without numeric tuning.

Therefore this checkpoint does **not** alter the frozen current state machine.

## Decision

**Checkpoint 09S = QA PASS / MATERIAL CHALLENGER / NON-PROMOTING.**

The candidate merits an exact causal raw-tick challenger replay because it is composed only of previously documented semantics:
- current neutral failure clock;
- wait-reentry neutral clock;
- wait-reentry stage-normalized 3-bar reversal semantics;
- routing by existing acceptance/reversal timeframe categories.

## Next bounded unit

`R037_DH05_CONDITIONAL_FAILURE_CLOCK_CHALLENGER_REPLAY_NON_PROMOTING`

Requirements:
- run causally on canonical Stage-A ticks;
- preserve the current production/frozen branch as control;
- no numeric retuning;
- challenger may not be promoted from count fit alone;
- require S06 signal/trade/win/net and six-vector count comparison;
- if strong, require anti-overfit validation before any semantic unfreeze.
