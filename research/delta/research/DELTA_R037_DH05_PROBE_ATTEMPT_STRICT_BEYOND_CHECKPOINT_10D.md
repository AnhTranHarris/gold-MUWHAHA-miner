# DELTA R037 — DH05 Causal Probe-Attempt Identity — Checkpoint 10D

**Status:** COMPLETE NEGATIVE QA / STRICT-BEYOND ATTEMPT CREATION REJECTED  
**Unit:** R037_DH05_PROBE_RESIDUAL_CAUSAL_ATTEMPT_IDENTITY_PROVENANCE_RECONCILIATION  
**Parent:** R037_DH05_PROBE_RESIDUAL_BOUNDARY_EPOCH_CHECKPOINT_10C  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Question and provenance

The original DH-05 white paper says PROBE occurs when midpoint trades *beyond* L. The clean-room reconstruction counts a new attempt on boundary contact. This unit tested whether equality contact was the remaining probe-count defect without changing any frozen numeric vector, swing source/width, ownership topology, acceptance semantics, or execution rules.

Profiles:
- STRICT_REATTEMPT_BEYOND: initial seeding unchanged; repeated attempts require signed displacement > 0.
- STRICT_ALL_BEYOND: initial and repeated attempts both require strict displacement beyond L.

## Crash-safe replay

Producer: `research/delta/experiments/delta_r037_dh05_probe_attempt_strict_beyond.py`  
Commit: `12a0da73233f149bf52aa983eec92e86e199950f`  
Blob: `6afba6e129b0735a1b1d1918109715208c759412`  
Producer SHA-256: `9cb64ca51a3ef28a82621b74c71030bf993e6a74ff418125d5fea50fcce6cdd9`

Official replay ran from GitHub recovery artifact run **37145180805**, artifact **11281952799**. Exact producer/helper Git blobs and canonical January SHA were verified before compute.

Runtime: **18.94 s**, peak RSS **699,392 KB**, hard timeout **120 s**, fresh Numba cache, Python faulthandler, atomic output. Full result SHA-256: `98fe1d481f25122e9b6ef43e83991c9d773685f8a4032334c2167598ff772872`.

Exact 09Z control reproduced first: probe error **449**, total error **782**.

## Result

| Profile | Probe abs error | Total abs error | Trade-count abs error | S06 veto |
|---|---:|---:|---:|---|
| 09Z control | **449** | **782** | **335** | — |
| STRICT_REATTEMPT_BEYOND | 2,855 | 3,194 | 336 | false |
| STRICT_ALL_BEYOND | 4,098 | 4,435 | 336 | false |

STRICT_REATTEMPT_BEYOND probe counts:
A03 6147; S05 7286; S06 3370; S09 7273; S10 5954; S16 7305.

STRICT_ALL_BEYOND probe counts:
A03 6001; S05 7019; S06 3240; S09 7063; S10 5790; S16 6979.

The striking feature is that qualification/downstream stages barely move while probe counts collapse. For STRICT_REATTEMPT_BEYOND stage absolute errors are:
`2855 / 54 / 31 / 61 / 36 / 35 / 61 / 61`.

## Interpretation

The preserved historical DH05 counter cannot be reconstructed by requiring strict price displacement beyond L at attempt creation. Boundary contact/equality observations are necessary to reproduce the historical probe density.

This does not prove the prose definition was wrong; it localizes a likely distinction between the narrative economic PROBE concept and the historical diagnostic attempt counter.

## Decision

**10D = NEGATIVE QA PASS.**

Reject strict-beyond attempt creation. Preserve contact-inclusive opening semantics for parity reconstruction.

Do not retune vectors, boundary source/width, ownership, acceptance clocks, SORB, August, or MQL5.

## Next bounded unit

`R037_DH05_PROBE_RESIDUAL_ATTEMPT_REARM_COMPLETION_PROVENANCE_RECONCILIATION`

Test the opposite edge of attempt identity: what causal condition completes/resets a same-boundary attempt before the next contact-inclusive probe may be counted.
