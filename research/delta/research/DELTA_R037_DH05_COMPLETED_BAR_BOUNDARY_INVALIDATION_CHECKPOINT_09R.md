# DELTA R037 — DH05 Completed-Bar Boundary Invalidation + GLOBAL NO_REARM — Checkpoint 09R

**Status:** COMPLETE NEGATIVE QA / COMPLETED-BAR INVALIDATION REJECTED / GENERATOR-OWNERSHIP PIVOT  
**Unit:** R037_DH05_COMPLETED_BAR_BOUNDARY_INVALIDATION_WITH_GLOBAL_NO_REARM_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_BOUNDARY_VALID_EXECUTION_MANDATE_CHECKPOINT_09Q  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Bounded question

Does evaluating original-boundary retake only on a newly completed causal bar close repair the 09Q downstream mandate?

Tested invalidation clocks:
- vector reversal timeframe close;
- frozen acceptance timeframe close.

Tested retry eligibility:
- LOSING_EXIT;
- MAXHOLD_ONLY.

Exact GLOBAL NO_REARM and singular 09F POST_QUAL generator semantics remained frozen.

## Provenance

- producer commit: `f28f1f3171a899c6f7cf5e863b7d396abc272de5`
- producer blob: `d3050c1b321da3922b694b5c3d6a6a848b77b01d`
- producer SHA-256: `72fcca468c1bb470659176bf6ad9fb37bebb95c28b218ab8ea0c9416d7efef81`
- result SHA-256: `72bff0871e349e05826cdad50a3c6c21e1c6ff4bfcd682729cb09eb7423c5ca0`
- runtime: **10.35 s**
- max RSS: **698,968 KB**
- exit: **0**

## Result

No profile beats the 09L aggregate-error clue of **304**.

| Profile | Aggregate error | S06 trades | S06 wins | S06 reentries |
|---|---:|---:|---:|---:|
| REVTF_CLOSE__MAXHOLD_ONLY | **359** | 676 | 287 | 27 |
| ACCTF_CLOSE__MAXHOLD_ONLY | 359 | 676 | 287 | 27 |
| ACCTF_CLOSE__LOSING_EXIT | 616 | 969 | 393 | 321 |
| REVTF_CLOSE__LOSING_EXIT | 622 | 953 | 387 | 304 |

Leading MAXHOLD fingerprint:
- A03 **199 / 306**
- S05 **9 / 51**
- S06 **676 / 615**
- S09 **11 / 119**
- S10 **230 / 206**
- S16 **7 / 24**

Acceptance-close + LOSING_EXIT:
- A03 **309 / 306**
- S05 **16 / 51**
- S06 **969 / 615**
- S09 **19 / 119**
- S10 **322 / 206**
- S16 **16 / 24**

## Interpretation

Moving boundary invalidation from tick-touch to completed-bar close does not solve the family.

The repeated 09M–09R result is now structurally consistent:
- downstream multiplicity can increase sparse populations;
- the same mechanism overproduces S06/S10 before S05/S09 approach historical density;
- conservative retry rules leave S05/S09 essentially at their singular-generator counts.

This points away from execution scheduling as the primary missing historical mechanism.

A separate provenance clue deserves a bounded diagnostic before more tick-level variants:

Using the frozen 09F POST_QUAL signal counts:
- A03: 192 signals -> 306 historical trades = **1.59×**
- S05: 9 -> 51 = **5.67×**
- S06: 651 -> 615 = **0.94×**
- S09: 11 -> 119 = **10.82×**
- S10: 227 -> 206 = **0.91×**
- S16: 7 -> 24 = **3.43×**

Every severe trades>signals gap occurs in the four vectors with **acceptance_tf = S15**. The two **acceptance_tf = S5** vectors already need mild suppression rather than multiplicity.

That is a six-vector fingerprint, not yet proof of causality. It must be checked against the preserved Checkpoint-08/09 stage-normalization/wait-reentry fingerprints and historical vector provenance before any new rule is tested.

## Decision

**Checkpoint 09R = QA PASS / NEGATIVE RESULT / NO NEW SEMANTIC FREEZE.**

Reject:
- reversal-timeframe close invalidation as the missing universal execution rule;
- acceptance-timeframe close invalidation as the missing universal execution rule.

Next, do not add another execution reentry heuristic.

## Next bounded unit

`R037_DH05_SIGNAL_TRADE_GAP_PROVENANCE_AND_ACCEPTANCE_CLOCK_OWNERSHIP_DIAGNOSTIC`

Use only durable six-vector fingerprints and preserved Checkpoint-08/09 controls to determine whether the S15-vs-S5 split indicates a missing generator/ownership semantic or merely coincidental parameter correlation. No raw-data retuning and no economic optimization.
