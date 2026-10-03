# DELTA R037 — DH02-S11 Failure Persistence State Memory — Checkpoint 11F

**Status:** COMPLETE STRONG NEGATIVE LOCALIZATION / FULL PARITY NOT ACHIEVED  
**Unit:** R037_DH02_S11_FAILURE_PERSISTENCE_STATE_MEMORY_PARITY_FINGERPRINT  
**Parent:** R037_DH02_S11_CONTEXT_INVALID_BREAK_PROVENANCE_DECISION_11E  
**Vector:** DH02-S11 / `50d1bb2e656e`  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Question

Does `failure_acceptance = tick persistence` use a causal FAILURE_PENDING latch that survives temporary improvement during RETESTING, rather than requiring consecutive adverse-buffer ticks?

The penetration buffer remains frozen at **0.1172 ATR**. No S11 numeric threshold was changed.

## Profiles and result

Historical target: **75 trades / 41 raw-positive wins / GP +9.39 / GL -17.60 / net -8.21**

| Profile | Trades | Raw+ wins | GP | GL | Net |
|---|---:|---:|---:|---:|---:|
| Control: consecutive buffer ticks | 106 | 42 | +7.80 | -35.10 | -27.30 |
| Boundary-reclaim latch | 105 | 41 | +7.49 | -35.09 | -27.60 |
| Retest-zone-exit latch | 105 | 41 | +7.49 | -35.09 | -27.60 |
| Breach then next pre-break tick | 105 | 41 | +7.49 | -35.09 | -27.60 |

All three latch interpretations converge to the same executable signal fingerprint:
`a84535b4be9952b5ed3be640ac2a1d94ce0284fc2f08b1321cf6f5b7961762d4`.

The control contains:
- 165 failure-pending starts;
- 37 resets;
- 128 confirms.

Boundary-reclaim latch:
- 144 starts;
- 15 resets;
- 129 confirms.

The alternative memory changes are active, but they remove only **one executable trade**.

## Critical economic finding

The removed trade is a **winner**, not part of the excess loss tail.

- winners: 42 → **41** (numerically matches historical count)
- GP: +7.80 → **+7.49** (worse)
- GL: -35.10 → **-35.09** (essentially unchanged)
- net: -27.30 → **-27.60** (worse)

Therefore the lower trade-count error is not a useful reconstruction breakthrough. It achieves the historical winner count by deleting profitable activity while leaving the residual gross-loss problem intact.

## Decision

**Checkpoint 11F = QA PASS / STRONG NEGATIVE LOCALIZATION / HISTORICAL PARITY FAIL.**

Reject failure-pending latch/reset semantics as the explanation for the residual DH02-S11 loss population.

Do not combine them with the non-promoting 11D challenger merely because each lowers trade count; 11F's marginal effect is economically adverse and does not target the residual loss tail.

Producer:
`research/delta/experiments/delta_r037_dh02_s11_failure_persistence_state_memory.py`  
Commit: `b97586d0f970fd9dd831725a5f9be9b1e529a967`  
Blob: `f40a27cd133d132816dd9bba8e796887c7bcb5b7`

Compact result:
`research/delta/reference/DELTA_R037_DH02_S11_FAILURE_PERSISTENCE_STATE_MEMORY_CHECKPOINT_11F.json`  
Commit: `c909337d6c7abcfcd215c50321223066a8729d5c`  
Blob: `3277f3b14e8dc32ec99294c5faefa933e474204e`  
SHA-256: `5af614dabbcb57e449580ab968107c0f66648087dcc599da92c4fa6330ed0333`

Official replay completed in approximately **8.71 seconds** under the hardened bounded runner; the exact 11B control signal fingerprint reproduced.

## Next bounded unit

`R037_DH02_S11_FAILURE_STATE_MEMORY_PROVENANCE_AND_INTERACTION_DECISION`

Disposition expected from this result: close failure-memory recuts unless independent provenance says otherwise, preserve the 11D invalid-context-break challenger separately, then move the residual search to a different source-grounded event/rebreak semantic rather than numeric threshold tuning.
