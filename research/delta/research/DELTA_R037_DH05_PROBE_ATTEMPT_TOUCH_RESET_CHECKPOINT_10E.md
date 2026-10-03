# DELTA R037 — DH05 Attempt Rearm Completion — Checkpoint 10E

**Status:** COMPLETE NEGATIVE QA / TOUCH-RESET REARM REJECTED  
**Unit:** R037_DH05_PROBE_RESIDUAL_ATTEMPT_REARM_COMPLETION_PROVENANCE_RECONCILIATION  
**Parent:** R037_DH05_PROBE_ATTEMPT_STRICT_BEYOND_CHECKPOINT_10D  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Bounded question

After 10D proved contact-inclusive probe opening is required by the historical fingerprint, does an active pre-failure attempt complete/rearm when price merely returns to the boundary, rather than requiring a strict move to the pre-break side?

No numeric vector, boundary source/width, ownership/release topology, acceptance, failure, reversal, or execution rule changed.

Profiles:
- TOUCH_RESET_STRICT_REBREAK: active attempt closes at signed <= 0; reset tick cannot reopen; later signed > 0 opens a new attempt.
- TOUCH_RESET_CONTACT_REBREAK: same reset, but a later signed >= 0 observation may reopen; same-tick close/reopen forbidden.

## Crash-safe replay

Producer commit: `db97b9129fdda643e01cab6f459f5f3830675bf0`  
Blob: `dba6f776eb4c7804b59265937f875e2e08a74d5e`  
SHA-256: `ce490e496091ac767718225d29de9cc9c42b1530747d6f1a51c76f87019b0122`

Commit-bound recovery artifact: run **37145530316**, artifact **11281199318**. Syntax compilation and exact blob checks passed before canonical compute.

Runtime: **20.17 s**, peak RSS **699,464 KB**, hard timeout **120 s**, fresh Numba cache, faulthandler, atomic output. Full result SHA-256: `f8fce86f2de000b208ae2da86a6cc07d173646d95bf04632818d4fb31d3f5d16`.

Exact 09Z control reproduced first: probe error **449**, total error **782**.

## Result

| Profile | Probe abs error | Total abs error | Trade-count abs error | S06 veto |
|---|---:|---:|---:|---|
| 09Z control | **449** | **782** | **335** | — |
| TOUCH_RESET_STRICT_REBREAK | 1,885 | 2,246 | 335 | **true** |
| TOUCH_RESET_CONTACT_REBREAK | 5,026 | 5,381 | 334 | **true** |

TOUCH_RESET_STRICT_REBREAK probe counts:
A03 6937; S05 8201; S06 3820; S09 8181; S10 6744; S16 8192.

TOUCH_RESET_CONTACT_REBREAK probe counts:
A03 7531; S05 8801; S06 4041; S09 8834; S10 7283; S16 8726.

The restrained profile already overproduces probes materially while qualification/downstream changes remain comparatively small. The looser contact-rebreak branch is decisively worse.

## Interpretation

10D and 10E now bracket the attempt-counter semantics:

- requiring strict beyond-L attempt creation removes too many probes;
- allowing boundary touch to complete/rearm an active attempt creates too many probes;
- the existing 09Z contact-inclusive opening plus strict pre-break-side reset remains the strongest universal causal reconstruction.

The remaining 449 probe error is mixed-sign across the six frozen vectors, so another universal opening/reset recut is increasingly unsupported without independent historical provenance.

## Decision

**10E = NEGATIVE QA PASS.**

Reject boundary-touch completion/rearm. Preserve the 09Z attempt counter as the strongest non-promoting reconstruction.

## Next bounded unit

`R037_DH05_PROBE_RESIDUAL_ATTEMPT_COUNTER_PROVENANCE_DECISION`

Determine whether any independent historical source justifies another universal attempt-counter semantic. If not, freeze the unresolved residual as a provenance limitation rather than fit it retrospectively.
