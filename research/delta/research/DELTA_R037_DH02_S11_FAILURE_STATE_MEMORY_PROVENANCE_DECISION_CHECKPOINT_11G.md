# DELTA R037 — DH02-S11 Failure-State Memory Provenance Decision — Checkpoint 11G

**Status:** COMPLETE PROVENANCE-LIMITATION FREEZE  
**Unit:** R037_DH02_S11_FAILURE_STATE_MEMORY_PROVENANCE_AND_INTERACTION_DECISION  
**Parent:** R037_DH02_S11_FAILURE_PERSISTENCE_STATE_MEMORY_CHECKPOINT_11F  
**Vector:** DH02-S11 / `50d1bb2e656e`  
**Surface:** provenance-only / no raw-tick access  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Question

After 11F showed that failure-pending latch/reset variants remove only one executable winner and do not repair the excess gross-loss tail, does surviving DH02 source material independently justify any more same-sample tick-memory recuts?

## Source evidence

The original DH02 white paper says:

- RETESTING may tolerate shallow penetration;
- a **completed S1/S5 acceptance** beyond the invalidation buffer sends the event to FAILED;
- a **single adverse tick is not enough** unless it breaches the broker hard stop.

R004 preserves causal failure acceptance as a factor family.

The immutable S11 vector later fixes:
- `acceptance_dwell = tick persistence`;
- `failure_acceptance = tick persistence`;
- penetration buffer = **0.1172 ATR**.

However, neither the white paper nor surviving preregistration material specifies an exact historical tick-memory/reset algorithm for that categorical label.

## 11F localization

Historical target:
**75 trades / 41 raw-positive wins / GP +9.39 / GL -17.60 / net -8.21**

11F control:
**106 / 42 / +7.80 / -35.10 / -27.30**

All tested latch interpretations converge to:
**105 / 41 / +7.49 / -35.09 / -27.60**

The removed trade is a winner. Gross-loss is effectively unchanged. Therefore the failure-memory recut fails the causal/economic selection rule.

## Decision

Freeze only the general source-supported semantic:

**Failure acceptance must be causal and persistent; a single adverse tick is insufficient.**

Do **not** invent or promote an exact historical tick-memory/reset algorithm.

Do **not** run additional same-sample failure-memory recuts.

Preserve the 11D `CONFLICT_BREAK_CONSUME_UNTIL_NEW_BOUNDARY` implementation separately as:

`NON_PROMOTING_SOURCE_COMPATIBLE_CHALLENGER`

It remains useful as a reconstruction surrogate but is **not** historical truth.

S11 stream disposition:

`PROVENANCE_LIMITED_BEST_RECONSTRUCTION_11D_NON_PROMOTING`

Exact historical S11 parity is **not** claimed.

## Crash / timeout safety

11G is provenance-only. Evidence and producer were committed before execution. The local execution copy reproduced the exact Git blob IDs before running:

- evidence blob: `e81ee16dc9ad341c3dda79849e190a365d63e9ee`
- producer blob: `9960b102e66037503febc1a2076614b97489738c`

Official result SHA-256:

`1c6f2745818a4ef6985bf21110477461a73b6645577bcd576a00587ee3fec948`

No market replay was required.

## Next bounded unit

`R037_DH02_S08_CLEANROOM_PARITY_RECONSTRUCTION`

Reconstruct the frozen DH02-S08 specialist independently from its immutable vector, original DH02 grammar, preserved historical fixture, and canonical Stage-A tick surface. No numeric retuning.
