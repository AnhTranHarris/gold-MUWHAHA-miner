# DELTA R037 — DH05 Partial Decoupling Release Point — Checkpoint 09I

**Status:** COMPLETE NEGATIVE QA / REENTRY + RECLAIM RELEASE REJECTED  
**Unit:** R037_DH05_PARTIAL_DECOUPLING_RELEASE_AT_REENTRY_OR_RECLAIM_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_DECOUPLED_GENERATOR_FAILURE_EPISODE_CHECKPOINT_09H  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Bounded question

Checkpoint 09H showed that releasing the probe generator immediately at FAILURE_CANDIDATE was too early: S05/S09/S16 improved sharply, but S06/S10 exploded. This unit therefore tested only two later causal release boundaries while the downstream failed-break episode continued independently:

- generator release at **REENTRY**;
- generator release at **RECLAIM**.

Each was tested with frozen 09E acceptance and the 09F post-qualification acceptance chronology. No numeric vector changed.

## Producer

Path:
`research/delta/experiments/delta_r037_dh05_partial_release_parity.py`

Commit:
`83429333e336d217e1b9392d02e4575210a64276`

Git blob:
`ee5d2b4216226104981b652aa0bc8f372453532f`

File SHA-256:
`3d8715d12b740448eab501e25b0b3eaa3165d7fbffe4982442c2fd0b3ba54430`

Official runtime output SHA-256:
`622b35f43d66cbbea63734e818f44cc3ca9453aad91b1998828b87c30f781ffe`

Runtime: ~22.0 s; peak RSS ~699 MB.

The committed Git blob matched the local producer byte-for-byte before official compute.

## Result

| Profile | Probe+qualified error | First-five error | Downstream error | Total error |
|---|---:|---:|---:|---:|
| CONTROL_09E | **554** | 920 | **144** | 1,064 |
| POST_QUAL_BASE | 697 | 818 | 160 | **978** |
| RELEASE_REENTRY_09E | 8,174 | 11,580 | 2,295 | 13,875 |
| RELEASE_REENTRY_POST_QUAL | 8,166 | 11,478 | 2,366 | 13,844 |
| RELEASE_RECLAIM_09E | 692 | 1,060 | 194 | 1,254 |
| RELEASE_RECLAIM_POST_QUAL | 626 | **793** | 239 | 1,032 |

### REENTRY

REENTRY release reproduces the Checkpoint-09H density explosion and is decisively rejected.

### RECLAIM

RECLAIM release is much safer. Under POST_QUAL:

- A03 = 6791/1015/218/797/450/276/197/197
- S05 = 7742/310/33/277/54/19/9/9
- S06 = 3621/1627/252/1375/1227/707/663/663
- S09 = 7697/207/42/165/64/40/11/11
- S10 = 6525/1322/207/1115/651/318/236/236
- S16 = 7713/132/53/79/33/19/8/8

RECLAIM release improves first-five error relative to serial POST_QUAL (818 -> 793), but it worsens downstream error 160 -> 239 and total error 978 -> 1032. It therefore fails the carry-forward rule.

## Decision

**Reject REENTRY and RECLAIM generator-release points.**

The active reconstruction keeps serial generator ownership. The high-value remaining distinction is downstream:

- first reversal confirmation / signal event;
- repeated transition-based signals inside the same failed-break episode;
- one-position executable admission.

This matches the older Checkpoint-09 recovery directive and the authoritative S06 fixture of **672 generator signals -> 615 executed trades**.

## Next bounded unit

`R037_DH05_SIGNAL_MULTIPLICITY_AND_EXECUTABLE_ADMISSION_PARITY_RECONSTRUCTION`

Requirements:
1. instrument signal timestamps and episode IDs;
2. one-signal-per-failure control;
3. test only transition-based rearmed repeated-signal semantics;
4. replay executable one-position admission separately;
5. compare S06 672-generator / 615-executed gap and all six historical trade-density targets;
6. no hindsight suppression, no threshold retuning.

No SORB. No August. No MQL5.
