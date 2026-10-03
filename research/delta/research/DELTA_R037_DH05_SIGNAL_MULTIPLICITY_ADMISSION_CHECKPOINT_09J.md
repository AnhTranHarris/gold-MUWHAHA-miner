# DELTA R037 — DH05 Signal Multiplicity / Executable Admission Parity — Checkpoint 09J

**Status:** COMPLETE BOUNDED QA / WEAK MULTIPLICITY CLUE / NO CARRY-FORWARD  
**Unit:** R037_DH05_SIGNAL_MULTIPLICITY_AND_EXECUTABLE_ADMISSION_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_PARTIAL_RELEASE_POINT_CHECKPOINT_09I  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Bounded question

Can the large historical gap between one first-signal marker per failed-break episode and executable trade density be explained by a reconstructible transition-based repeated-signal rule plus the frozen one-position-at-a-time R9/Coinexx admission lifecycle?

No frozen numeric vector was retuned.

## Producer / crash safety

Producer:
`research/delta/experiments/delta_r037_dh05_signal_multiplicity_admission_parity.py`

Final producer commit:
`dc92e35e81714b2d2ff9f5b85703581a2257908a`

Blob:
`f17a229a2e995d0a928db8899304bbeeb71ffd84`

File SHA-256:
`1224830d3d147ec97a14d79bb1e8c16199a3c78b0b5885e0f7c0b38a871b6240`

Official output SHA-256:
`8b4dc71e9c4e9a9266b98067d0e0f44112bdb5775ade070d4c4cdb4b3b873333`

Runtime: **20.02 s**, max RSS **700,140 KB**, external hard timeout **120 s**.

The producer fails closed unless:
- the Checkpoint-09E stage-error fingerprint reproduces exactly;
- the Checkpoint-09F POST_QUAL per-vector funnel reproduces exactly;
- no preallocated signal buffer overflows.

Two implementation errors were caught before accepted output:
1. initial admission replay had the wrong commission/initial-stop details;
2. the first multiplicity extension accidentally made RECLAIM a continuously required predicate instead of a latched state transition.

Both were repaired and committed before the accepted replay. Failed attempts wrote no checkpoint JSON.

## Frozen admission fixture

The standalone execution replay mirrors the R032/R9 lifecycle:
- BUY Ask entry / Bid exit;
- SELL Bid entry / Ask exit;
- initial protective stop $0.30 from the executable stop-side quote;
- $0.10 trail activation;
- $0.03 trail distance;
- integer-second 30 s maximum hold;
- $0.01 entry + $0.01 exit commissions;
- one position at a time.

A same-exit-tick position-observation latch was tested separately rather than assumed.

## Signal rules tested

1. **ONE_SHOT_POST_QUAL** — exact 09F serial control.
2. **REVERSAL_CONDITION_TOGGLE_REARM** — after first signal, rearm only after reversal predicate becomes false, then true again.
3. **RECLAIM_LOSS_REGAIN_REARM** — after first signal, rearm only after reclaim is lost then causally restored.
4. **BOUNDARY_RECYCLE_REARM** — after first signal, rearm only after price causally revisits the original-break side and then returns to the failed-break side.

No signal-every-qualifying-bar shortcut was used.

## Exact controls

POST_QUAL first-signal counts reproduced:
- A03 192
- S05 9
- S06 651
- S09 11
- S10 227
- S16 7

The 09E aggregate stage-error control also reproduced exactly.

## Results

### One-shot control

Aggregate six-vector executable-trade-count absolute error: **336**.

S06:
- generator signals **651** vs target **672**;
- trades **649** vs target **615**;
- official wins **274** vs target **307**;
- net **-$150.35** vs target **-$101.08**.

### Leading weak clue — boundary recycle

Aggregate trade-count error improves only **336 -> 324**.

S06:
- signals **648**
- unique signal episodes **575**
- repeated signals **73**
- trades **647**
- wins **275**
- net **-$149.42**

Against historical S06:
- signals **672**
- trades **615**
- wins **307**
- net **-$101.08**

Six-vector boundary-recycle trade density:
- A03 **203** vs target 306
- S05 **9** vs target 51
- S06 **647** vs target 615
- S09 **11** vs target 119
- S10 **228** vs target 206
- S16 **7** vs target 24

The exit-tick observation latch does not change the leading profile.

### Rejected rules

**REVERSAL_CONDITION_TOGGLE_REARM** grossly overproduces, including 2,143 S06 generator signals and 1,844 S06 trades in the no-latch replay.

**RECLAIM_LOSS_REGAIN_REARM** also overproduces S06 materially (869 signals / 831 trades in the no-latch replay).

## Interpretation

This checkpoint confirms that repeated-signal eligibility exists as a plausible architectural dimension, but the tested rearm transitions do not reconstruct the historical family.

The sparse vectors are especially diagnostic:
- S05 remains 9 trades vs 51 historical;
- S09 remains 11 vs 119;
- S16 remains 7 vs 24.

Therefore their deficit is not explained by ordinary reversal-toggle, reclaim-toggle, boundary-recycle, or exit-tick latch semantics under the current post-failure lifetime.

This localizes the next question to **post-signal episode persistence / invalidation**: the historical failed-break thesis may remain actionable after the first reversal for longer than the current max-failure lifetime, with a distinct causal invalidation event.

## Decision

**Checkpoint 09J = QA PASS / WEAK ARCHITECTURE CLUE / NO SEMANTIC FREEZE.**

Keep frozen:
- 09C boundary and attempt ledger;
- 09D acceptance interpretation;
- 09E probe clock;
- 09F post-qualification acceptance chronology as diagnostic branch;
- 09I serial pre-reversal episode ownership.

Do not promote any 09J repeated-signal rule.

Do not retune vectors, integrate SORB, access August, optimize mature exits, or begin MQL5.

## Next bounded unit

`R037_DH05_POST_SIGNAL_EPISODE_PERSISTENCE_AND_INVALIDATION_PARITY_RECONSTRUCTION`

Test only causal post-first-signal lifetime/invalidation semantics while keeping the upstream state machine and numeric vectors frozen.