# DELTA R037 — DH03-S06 Pending Attempt Validity — Checkpoint 13E

**Status:** COMPLETE NEGATIVE LOCALIZATION / FULL PARITY NOT ACHIEVED  
**Unit:** R037_DH03_S06_PENDING_ATTEMPT_VALIDITY_AND_SUPERSESSION_PARITY_RECONSTRUCTION  
**Parent:** R037_DH03_S06_EVENT_ATTEMPT_ADMISSION_CHECKPOINT_13D  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

The exact frozen 13C generator (1,586 signals, SHA `261b6ad5...`) and 13D controls reproduced.

13E traced every original pullback episode to its causal death:
- parent opposition: 4 episodes
- structural invalidation: 489
- max-age expiry: 654
- active at Stage-A end: 0

Pending admission profiles were nested without new numbers:
- unconditional pending: 1,586 trades / 703 raw-positive / net -358.07
- parent-valid: identical
- parent+structure-valid: identical
- full original-event validity: **1,584 trades / 702 raw-positive / 689 official / net -357.71**

Only **2 of 83** pending tokens were invalidated before flat observation, both by the frozen max-pullback-age expiry. Parent opposition and structural invalidation removed **zero** pending tokens.

Therefore causal pending-token lifetime does not explain the historical target of 1,563 trades. The canonical full-event rule is retained as a causal constraint, but no pending TTL or validity number will be tuned.

The residual returns upstream to event/reclaim identity. The DH03 white paper requires a *causally known fast pivot/reclaim level* but does not explicitly require that the pivot be revealed after the original pullback start. 13B/13C showed:
- strict post-pullback pivot + fresh-exhaustion rearm: 1,513 executed trades;
- unrestricted any-causal pivot + fresh-exhaustion rearm: 1,672 trades.

The historical 1,563 lies between them. The next unit will test source-compatible **event/rearm boundary rules**, not numeric thresholds.

Official runtime: **11.63 s**; peak RSS **698,588 KB**.  
Raw result SHA-256: `7621dcb5286a7aca531762a7869b5f6d36e66072382287e49c78e54bf1a21d26`.

## Next bounded unit

`R037_DH03_S06_PENDING_EVENT_IDENTITY_AND_REARM_BOUNDARY_PARITY_RECONSTRUCTION`
