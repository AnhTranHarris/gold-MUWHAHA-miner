# DELTA R037 — DH05 Boundary-Valid Execution Mandate + GLOBAL NO_REARM — Checkpoint 09Q

**Status:** COMPLETE NEGATIVE QA / TICK-LEVEL BOUNDARY VALIDITY REJECTED / INVALIDATION CLOCK LOCALIZED  
**Unit:** R037_DH05_BOUNDARY_VALID_EXECUTION_MANDATE_WITH_GLOBAL_NO_REARM_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_GLOBAL_NO_REARM_REVERSAL_HYSTERESIS_CHECKPOINT_09P  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Bounded question

Can a singular frozen POST_QUAL generator signal create a longer-lived downstream execution mandate that remains valid while price stays on the reversal side of the original failed-break boundary, with exact GLOBAL NO_REARM limiting repeat execution?

Re-entry eligibility profiles:
- ANY_EXIT
- STOP_ONLY
- LOSING_EXIT
- MAXHOLD_ONLY

The generator remained singular and exact. No numeric vector was retuned.

## Provenance

- final producer commit: `220cf16591d600e6df06c6ce679316b7041edb6a`
- producer blob: `a32f895fa868abc39a09a871a902282c7b65875b`
- producer SHA-256: `d485a50f9fb097c9760c6810c02ded3bad6ba9eeb2ca9d4cabb0825d1abe82f6`
- result SHA-256: `adbe2a5806971ffb9a5b761c8e00d3d9d8b4cf12421614349f7b40fe9366cd20`
- runtime: **10.41 s**
- max RSS: **698,284 KB**
- exit: **0**
- clean per-unit Numba cache.

Source QA caught and fixed a prereplay arithmetic assertion (raw generator-count error is 338, not 334) before official compute. The hypothesis was unchanged.

## Result

No profile beats the 09L clue at aggregate error **304**.

| Profile | Aggregate error | S06 trades | S06 wins | S06 reentries |
|---|---:|---:|---:|---:|
| MAXHOLD_ONLY | **343** | 657 | 278 | 26 |
| LOSING_EXIT | 583 | 906 | 367 | 275 |
| STOP_ONLY | 4,411 | 3,011 | 1,332 | 2,381 |
| ANY_EXIT | 13,653 | 4,622 | 2,088 | 3,994 |

### MAXHOLD_ONLY

- A03 **193 / 306**
- S05 **9 / 51**
- S06 **657 / 615**
- S09 **11 / 119**
- S10 **227 / 206**
- S16 **7 / 24**

This is controlled but does not repair sparse density.

### LOSING_EXIT

- A03 **249 / 306**
- S05 **14 / 51**
- S06 **906 / 615**
- S09 **19 / 119**
- S10 **296 / 206**
- S16 **16 / 24**

Loss-only retries materially move the sparse vectors, but dense S06/S10 overproduce.

## Interpretation

The useful clue is no longer the mandate lifetime itself; it is the **invalidation clock**.

09Q invalidates the downstream mandate immediately on an intrabar/tick retake of the original boundary. That may be too aggressive relative to the completed-bar causal grammar already established elsewhere in DH05.

The next bounded question therefore preserves:
- singular generator;
- original-boundary mandate identity;
- GLOBAL NO_REARM;
- controlled LOSING_EXIT and MAXHOLD_ONLY retry modes;

and changes only whether the original boundary is considered retaken on a **completed causal bar close** instead of the first tick touch.

No new price threshold is required.

## Decision

**Checkpoint 09Q = QA PASS / NEGATIVE RESULT / NO NEW SEMANTIC FREEZE.**

Reject:
- ANY_EXIT boundary mandate;
- STOP_ONLY boundary mandate;
- tick-level boundary invalidation as sufficient parity solution.

Retain diagnostic clue:
- LOSING_EXIT improves sparse-vector density but needs stronger dense-vector suppression and/or less aggressive causal mandate invalidation.

## Next bounded unit

`R037_DH05_COMPLETED_BAR_BOUNDARY_INVALIDATION_WITH_GLOBAL_NO_REARM_PARITY_RECONSTRUCTION`

Test completed-bar original-boundary invalidation using existing reversal-timeframe and acceptance-timeframe clocks, with only LOSING_EXIT and MAXHOLD_ONLY downstream retry semantics.
