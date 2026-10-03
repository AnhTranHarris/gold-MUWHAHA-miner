# DELTA R037 — DH02-S11 Clean-Room Parity Reconstruction — Checkpoint 11A

**Status:** COMPLETE CLEAN-ROOM PARITY FAIL / MISMATCH LOCALIZED  
**Unit:** R037_DH02_S11_CLEANROOM_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_PROBE_ATTEMPT_COUNTER_PROVENANCE_DECISION_CHECKPOINT_10F  
**Vector:** DH02-S11 / fingerprint `50d1bb2e656e`  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Bounded question

Can the frozen DH02-S11 historical standalone fixture be reconstructed from the surviving DH-02/DH-01 grammar, immutable vector, R005 execution fixture, canonical Stage-A ticks, and frozen R9 downstream lifecycle without retuning any numeric threshold?

Historical standalone target:
- 75 trades
- 41 raw-positive wins
- GP +$9.39
- GL -$17.60
- net -$8.21

## Frozen reconstruction

The producer uses:
- width-2 causally confirmed M5 swings;
- completed S1 break observation;
- ATR(14) from completed S15, frozen at break;
- S11 BreakNorm / retest zone / penetration / ages unchanged;
- causal tick-persistence acceptance/failure;
- completed S5 rebreak;
- four-completed-S5-bar SignedEfficiency;
- one boundary + original break direction = one event;
- frozen R9 stop/trail/30-second max-hold execution.

The bounded ambiguity matrix tested only event concurrency/context:
1. dual-side event / no context diagnostic;
2. dual-side event / conflict-only veto;
3. single-global event / conflict-only veto.

No numeric vector value changed.

## Official replay

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**.

Final producer:
`research/delta/experiments/delta_r037_dh02_s11_cleanroom_parity.py`

Producer commit:
`4ed945b7ddada94c91c59add2e3f786179a1cf89`

Producer blob:
`b240a8e45d61f886f08604b0af62f3aaecec517a`

Producer SHA-256:
`7327a408ef4b73843d4a044145600cf63291de6a9e96fa128f6429562cca3966`

Evidence blob:
`243c73476640f09b2f4ef43eff16cd4050d62454`

Official bounded execution completed in approximately **8.31 seconds** under the hardened timeout runner.

## Results

| Profile | Signals/trades | Raw-positive wins | GP | GL | Net |
|---|---:|---:|---:|---:|---:|
| No context diagnostic | 166 | 71 | +16.88 | -52.05 | -35.17 |
| **Conflict-only veto** | **106** | **42** | **+7.80** | **-35.10** | **-27.30** |
| Single-global + conflict veto | 106 | 42 | +7.80 | -35.10 | -27.30 |
| Historical target | **75** | **41** | **+9.39** | **-17.60** | **-8.21** |

The dual-side and single-global conflict-veto profiles are identical in this reconstruction, so simultaneous opposite-side event ownership is not causing the residual.

The conflict-only context removes 60 trades relative to the context-free diagnostic and moves raw-positive wins from 71 to 42. The historical target is 41 wins. Therefore the context mechanism is directionally important, but the reconstructed eligible population remains **31 trades too large** and contains materially too much gross loss.

## Localization

This checkpoint does **not** support threshold retuning.

The residual is now localized primarily to:
- the exact historical meaning of categorical `tick persistence` for break acceptance/failure; and/or
- exact DH01 `conflict-only veto` state semantics.

Because S11 trade count is 106 versus 75 while raw-positive wins are 42 versus 41, the historical implementation appears to have rejected a substantial additional low-quality event subset. That must be reconstructed semantically, not fitted numerically.

## Decision

**Checkpoint 11A = bounded QA PASS / exact historical parity FAIL / mismatch localized.**

Do not:
- alter S11 thresholds;
- infer that 106-trade reconstruction is historical truth;
- start S08;
- integrate SORB;
- access August;
- begin MQL5.

Compact result SHA-256:
`6f718bebc5f3812791f2e6fc16894aba089c64b9d91e268777b8836362f1db0a`

## Next bounded unit

`R037_DH02_S11_TICK_PERSISTENCE_AND_CONTEXT_SEMANTICS_PARITY_FINGERPRINT`

Test only reconstructible categorical semantics for `tick persistence` and the conflict-only context gate against the frozen 75/41/economic fixture. No numeric threshold search.
