# DELTA R037 — DH05 Signal-to-Execution Mandate Persistence Parity — Checkpoint 09M

**Status:** COMPLETE NEGATIVE QA / BLANKET EXECUTION-MANDATE REENTRY REJECTED  
**Unit:** R037_DH05_SIGNAL_TO_EXECUTION_MANDATE_PERSISTENCE_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_POST_SIGNAL_INTRABAR_REARM_EDGE_CHECKPOINT_09L  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Bounded question

Can one causal POST_QUAL generator signal authorize more than one executable trade through a separate downstream mandate, without manufacturing extra generator signals?

The generator was frozen to the exact 09F one-shot stream. Candidate mandate clocks reused only existing quantities:
- vector `max_failure_age`;
- frozen R9 30-second execution horizon.

Profiles tested:
- one permitted re-entry;
- unlimited re-entry while the mandate remained alive.

No frozen generator threshold was retuned.

## Provenance

- producer: `research/delta/experiments/delta_r037_dh05_signal_to_execution_mandate_parity.py`
- producer commit: `94367f76a848381303654b542c4c2cf5f04d89a3`
- producer blob: `33cbedaf83c9acb244eadfd9325adcd8e5612997`
- producer SHA-256: `12e73a4d150ce2aeefa3e2c9d7310f763b2b74af18e066506ee04d82a9394583`
- result SHA-256: `dc6f09064fb52fd6fa8dcfac079e36d38eae6812e0308286f43b929b31f85223`
- runtime: **10.45 s**
- max RSS: about **701 MB**
- exit status: **0**

Canonical January source and 4,205,709 Stage-A ticks reproduced exactly.

## Result

The one-shot execution control remains:
- aggregate trade-count absolute error: **336**;
- S06: **651 signals / 649 trades / 274 wins / -$150.35**.

Every blanket mandate profile is worse.

### One re-entry only

**EXEC30_ONE_REENTRY**
- aggregate trade-count error: **1,127**
- S06: **1,284 trades / 561 wins / -$294.18**
- S06 execution re-entries: **633**

**MAXFAIL_ONE_REENTRY**
- aggregate trade-count error: **1,143**
- S06: **1,300 trades / 569 wins / -$296.18**
- S06 execution re-entries: **649**

Representative six-vector EXEC30 counts:
- A03 **380 vs 306**
- S05 **18 vs 51**
- S06 **1284 vs 615**
- S09 **22 vs 119**
- S10 **450 vs 206**
- S16 **14 vs 24**

### Unlimited while mandate alive

- EXEC30_UNLIMITED aggregate error: **7,611**
- MAXFAIL_UNLIMITED aggregate error: **11,380**
- S06 rises to **4,906** and **8,689** trades respectively.

## Interpretation

The preserved trades>signals fingerprints do not support a blanket time-persistent execution command.

A correct downstream multiplicity mechanism, if one exists, must be conditional on market/state transitions. It must add opportunities primarily where the reversal thesis remains valid while suppressing dense S06/S10 repetition.

The next bounded hypothesis is therefore **state-persistent execution mandate**, not time-persistent mandate:
- generator signal remains singular;
- a downstream execution mandate can re-enter only while the reversal thesis remains causally valid or is reconfirmed;
- no additional generator signal is counted.

## Decision

**Checkpoint 09M = QA PASS / NEGATIVE RESULT / NO SEMANTIC FREEZE.**

Reject:
- fixed max-failure-age mandate with automatic re-entry;
- fixed 30-second mandate with automatic re-entry;
- unlimited automatic re-entry.

Keep frozen:
- upstream 09C/09D/09E hypotheses;
- 09F POST_QUAL diagnostic branch;
- serial pre-reversal ownership;
- frozen R9/Coinexx execution.

Do not retune vectors, access August, integrate SORB, optimize mature exits, or begin MQL5.

## Next bounded unit

`R037_DH05_REVERSAL_STATE_PERSISTENT_EXECUTION_MANDATE_PARITY_RECONSTRUCTION`

Test only conditional execution re-entry tied to causal reversal-state persistence/reconfirmation while leaving generator counts unchanged.
