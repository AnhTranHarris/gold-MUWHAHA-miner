# DELTA R037 — DH03-S06 Event Attempt Admission / Execution — Checkpoint 13D

**Status:** COMPLETE MATERIAL ADMISSION CLUE / FULL HISTORICAL PARITY NOT ACHIEVED  
**Unit:** R037_DH03_S06_EVENT_ATTEMPT_ADMISSION_AND_EXECUTION_PARITY_RECONSTRUCTION  
**Parent:** R037_DH03_S06_EVENT_MULTIPLICITY_CHECKPOINT_13C  
**Vector:** DH03-S06 / `a3a086b7344c`  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Bounded question

With the exact 13C 1,586-signal generator frozen, what happens to a fully causal ENTRY_ELIGIBLE attempt that arrives while the one-position execution ledger is occupied?

No generator timing, numeric threshold, exit, lot, or surface changed.

## Crash-safe execution

13D evidence and producer were committed before compute. Their local Git blobs matched GitHub exactly before execution. The producer also fails closed unless it first reproduces the exact 13C generator and the 13C drop-occupied execution control.

Official replay:
- elapsed **11.24 s**
- peak RSS **697,844 KB**
- raw-result SHA-256 `bf226137cda9b030851dae3317443383ad3659bfc166b648d29e0b386d0313c2`
- canonical Stage-A ticks **4,205,709**
- August not accessed.

## Exact control

The frozen 13C signal stream reproduced exactly:
- **1,586 signals**
- signal SHA `261b6ad5a1cab4dd4378ec40af7fdde4e5178e82694089b3bf2a28bc6bebfdea`

DROP_OCCUPIED reproduced 13C exactly:
- **1,513 trades**
- **674 raw-positive wins**
- **661 official wins**
- GP **+$137.12**
- GL **-$476.26**
- net **-$339.14**
- DD **$339.14**
- **73** signals rejected while occupied.

## Admission results

| Profile | Trades | Raw+ wins | Net | DD | Key admission behavior |
|---|---:|---:|---:|---:|---|
| DROP_OCCUPIED control | 1,513 | 674 | -339.14 | 339.14 | 73 occupied signals discarded |
| EXIT_TICK_LATCH_DROP | 1,509 | 673 | -337.42 | 337.42 | 4 additional exit-tick signals discarded |
| PENDING_FIRST_AFTER_OBSERVATION | **1,586** | **703** | -358.07 | 358.07 | 83 pending attempts created and all admitted |
| PENDING_LATEST_AFTER_OBSERVATION | **1,586** | **703** | -358.07 | 358.07 | identical to first-pending; no replacements occurred |

Historical target:
**1,563 trades / 690 raw-positive wins / GP +151.82 / GL -490.75 / net -338.93 / DD 339.25**

## Interpretation

A one-token pending specialist attempt is a plausible missing admission dimension, but **unconditional pending validity is too permissive**.

The historical fixture lies tightly between the two causal controls:
- drop occupied: **1,513**
- historical: **1,563**
- admit every pending attempt: **1,586**

So the historical stream needs **50 more trades than DROP**, but **23 fewer than admit-all pending**.

First-pending and latest-pending are identical because no second signal ever arrives while an existing pending token is waiting. Therefore **supersession order is not the current defect**.

The localized residual is now: **what causally invalidates a pending ENTRY_ELIGIBLE attempt before the post-exit position-observation boundary?**

Candidate validity events must come from already-frozen DH03 state:
- original pullback expiry;
- parent-direction loss/opposition;
- structural invalidation;
- episode transition to a new pullback identity;
- or another explicit source-grounded state transition.

No TTL fitting is permitted.

## Decision

**Checkpoint 13D = QA PASS / MATERIAL ADMISSION CLUE / FULL PARITY FAIL.**

Carry forward only as a diagnostic:
- occupied ENTRY_ELIGIBLE attempts may be pending rather than automatically discarded;
- same-tick post-exit execution remains unproven;
- unconditional pending validity is rejected;
- first-vs-latest supersession is irrelevant in this fixture.

Freeze all 13C entry/event semantics and every S06 threshold.

## Next bounded unit

`R037_DH03_S06_PENDING_ATTEMPT_VALIDITY_AND_SUPERSESSION_PARITY_RECONSTRUCTION`

Goal: test only causal pending-token invalidation against the still-frozen 13C signal stream and one-position execution lifecycle.
