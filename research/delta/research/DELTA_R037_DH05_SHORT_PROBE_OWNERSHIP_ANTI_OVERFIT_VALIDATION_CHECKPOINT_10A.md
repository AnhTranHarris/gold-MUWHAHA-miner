# DELTA R037 — Short-Probe Ownership Anti-Overfit Validation — Checkpoint 10A

**Status:** COMPLETE LATE-JAN CROSS-SURFACE ROBUSTNESS PASS / EFFECT TINY / NON-PROMOTING  
**Unit:** R037_DH05_SHORT_PROBE_OWNERSHIP_ANTI_OVERFIT_VALIDATION  
**Parent:** R037_DH05_SHORT_PROBE_RELATIVE_ACCEPTANCE_BAR_OWNERSHIP_CHECKPOINT_09Z  
**Holdout:** 2026-01-18T12:00:00Z through final January tick  
**Warmup:** 2026-01-14T00:00:00Z to holdout boundary, indicator/boundary state only  
**Surfaces:** P50 / P75 / P90  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Timeout recovery context

The repeated ChatGPT message-delivery timeout did not erase 09Z. GitHub already contained the committed 09Z producer, causal result, report, rebuild manifest, and workbook checkpoint. Only the final CURRENT_STATE advance had been interrupted.

That cursor gap was repaired first and the DELTA rebuild artifact gate passed before this unit began.

## Predeclared validation

The 09Z router was frozen before holdout compute:

`max_probe_age_s < acceptance_tf_seconds`

- short probe relative to acceptance bar: release upstream generator at FAILURE_CANDIDATE while downstream failed-break episode continues independently;
- otherwise: retain SERIAL_POST_QUAL ownership.

Selected: S05 / S09 / S16.  
Serial: A03 / S06 / S10.

No threshold was changed. No same-holdout recut was allowed.

The anti-overfit gate was intentionally threshold-free: candidate aggregate net had to be no worse than serial control on **every** P50/P75/P90 holdout surface.

Passing this gate was preregistered as robustness evidence only, not automatic historical-semantic promotion.

## Runtime provenance

Producer:
`research/delta/experiments/delta_r037_dh05_short_probe_ownership_anti_overfit_validation.py`

- commit: `054c1a4a2b2b902928f1c9fb4007b8dda2f3e6f2`
- blob: `469df0e3dba832c0eda1461dd945b40a65484f85`
- SHA-256: `9c8ff7c0e48adf9a64571ea2a6ec3cb7fdec088b7e72eb098ac4072fd72d459d`
- runtime result SHA-256: `3ac7a2a4879bf82261a321215ea3fcb641470d13580de4f08d3f0ee8e86b7de7`
- canonical January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- ticks loaded from warmup start: **6,076,533**
- elapsed: **19.32 s**
- peak RSS: **989,144 KB**
- exit: **0**
- hard timeout: **180 s**
- fresh Numba cache: **YES**
- Python faulthandler: **YES**
- atomic output: **YES**

## Holdout result

| Surface | Control Trades | Candidate Trades | Control Wins | Candidate Wins | Control Net | Candidate Net | ΔNet | Δ summed vector DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P50 | 897 | 898 | 427 | 428 | -$163.28 | -$163.20 | **+$0.08** | $0.00 |
| P75 | 894 | 895 | 410 | 411 | -$179.65 | -$179.58 | **+$0.07** | **-$0.07** |
| P90 | 892 | 893 | 362 | 363 | -$291.72 | -$291.68 | **+$0.04** | **-$0.04** |

The preregistered no-worse-net gate passes on all three surfaces.

## Where the difference comes from

For all three surfaces:

- **S05:** 7 -> 8 signals, 7 -> 8 trades, and the added trade is a winner.
- **S09:** unchanged at 2 signals / 2 trades.
- **S16:** 7 -> 8 signals, but executable trades remain 7 because the extra signal is not admitted by the position/latch lifecycle.

Therefore the cross-surface pass is real and causally reproducible, but extremely small. The router contributes one additional admitted S05 winning trade per holdout surface.

## Scientific interpretation

Checkpoint 10A is useful because 09Z was derived from Stage-A parity evidence and could have been a same-sample fingerprint artifact. It does **not** reverse direction on an independent later-January window, and its tiny positive effect is consistent across P50/P75/P90.

However:

1. the effect is only one additional admitted trade per surface;
2. S09 shows no change;
3. S16's extra generator signal is filtered before execution;
4. holdout economics cannot prove what the missing historical DH05 helper actually did.

So 10A validates **robustness/no-harm**, not historical semantic identity.

## Decision

**Checkpoint 10A = ANTI-OVERFIT ROBUSTNESS PASS / EFFECT TINY / NON-PROMOTING.**

Keep 09Z as a robust non-promoting challenger. Do not freeze it as final DH05 semantics solely from this result.

Do not:
- recut the holdout;
- retune vectors;
- integrate SORB;
- open August;
- optimize mature exits;
- begin MQL5.

Compact checkpoint:
`research/delta/reference/DELTA_R037_DH05_SHORT_PROBE_OWNERSHIP_ANTI_OVERFIT_VALIDATION_CHECKPOINT_10A.json`

## Next bounded unit

`R037_DH05_SHORT_PROBE_OWNERSHIP_PROVENANCE_PROMOTION_DECISION`

Purpose: combine 09Y structural provenance, 09Z causal Stage-A parity gain, and 10A independent holdout robustness to decide whether the router has enough non-circular evidence to become a frozen parity hypothesis. If provenance remains insufficient, close this ownership family without further same-sample recuts and resume the next unresolved DH05 parity mechanism.
