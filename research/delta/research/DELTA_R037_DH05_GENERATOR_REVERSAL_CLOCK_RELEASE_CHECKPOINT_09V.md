# DELTA R037 — Generator Release on Reversal-Clock Transition — Checkpoint 09V

**Status:** COMPLETE NEGATIVE QA / FUNNEL CLUE / TRADE-DENSITY VETO  
**Unit:** R037_DH05_GENERATOR_RELEASE_ON_REVERSAL_CLOCK_TRANSITION_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_GENERATOR_NEW_BOUNDARY_RELEASE_CHECKPOINT_09U  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Bounded question

Can serial generator ownership be released at a causal reversal-clock transition after RECLAIM but before terminal REVERSAL/SIGNAL?

Two preregistered transitions were tested without changing any numeric vector:

1. `RECLAIM_BAR_FAILED_REVERSAL_RELEASE` — release on the reclaim bar only when that completed reversal-timeframe bar fails the frozen reversal confirmation.
2. `NEXT_REVERSAL_BAR_RELEASE` — if the episode survives the reclaim bar, release on the next newly completed reversal-timeframe bar while the downstream episode continues.

This brackets the ownership window after earlier results showed:
- FAILURE_CANDIDATE / REENTRY release is too early;
- RECLAIM release is close but degrades total/downstream parity;
- newly revealed M5-boundary release is too late.

## Provenance / crash safety

Producer:
`research/delta/experiments/delta_r037_dh05_generator_reversal_clock_release_parity.py`

- producer commit: `8f1414c4f7c6949b0eeda62f600d220b959c4d71`
- producer blob: `670d9b2a36c00edf257d34d7b9bbc89f923f8c79`
- producer SHA-256: `1e1b315d0fb71cad24360f5e3f8b92b8b3d6eb66ae5fe0c1e95317e1f2da5a08`
- runtime result SHA-256: `d742acc8ef76a476d1ad7a1681e19e8ffab89a734a6fbdc6e2e58b87e5e3a54b`
- canonical January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Stage-A ticks: **4,205,709**
- official bounded replay: **15.05 s**
- peak RSS: **698,044 KB**
- exit code: **0**
- hard process timeout: **120 s**
- fresh isolated Numba cache
- atomic output write

A first launch used the wrong local relative source path and exited with `FileNotFoundError` before reading data or creating output. The source was unchanged; the official replay then used the verified canonical path and completed normally.

## Exact control

Serial POST_QUAL reproduced exactly before candidate scoring:

- total eight-stage funnel absolute error: **978**
- aggregate executable trade-count absolute error: **336**

## Results

### NEXT_REVERSAL_BAR_RELEASE

- total funnel error: **951** — 27 lower than control
- aggregate trade-count error: **346** — 10 worse than control
- generator releases: **3,795**
- no episode overflow
- no signal overflow

Six-vector executable results:

- A03: **195 trades / 78 wins / -$46.00**
- S05: **9 / 5 / -$1.25**
- S06: **661 / 278 / -$154.25**
- S09: **11 / 7 / -$1.13**
- S10: **229 / 104 / -$47.06**
- S16: **8 / 3 / -$2.09**

S06 historical fixture remains **672 signals / 615 trades / 307 wins / -$101.08**. Candidate S06 is **664 / 661 / 278 / -$154.25**.

### RECLAIM_BAR_FAILED_REVERSAL_RELEASE

- total funnel error: **1,032**
- aggregate trade-count error: **344**
- generator releases: **3,808**
- S06: **663 signals / 660 trades / 278 wins / -$153.73**

## Interpretation

The next-reversal-bar release is a real state-funnel clue: it improves the aggregate funnel from 978 to 951. But it fails the preregistered joint carry-forward rule because executable trade-density error worsens and S06 economics remain materially worse than the historical fixture.

This closes the simple universal reversal-clock release branch. Continuing to move the release one bar earlier/later would be threshold-like semantic chasing rather than provenance reconstruction.

The remaining high-value architectural clue is categorical ownership already present in durable evidence:
- S5 acceptance vectors S06/S10 are dense and need serial/suppressive behavior;
- S15 acceptance vectors A03/S05/S09/S16 are sparse;
- 09H immediate decoupling sharply repaired S05/S09/S16 but exploded S06/S10.

That supports a **non-promoting acceptance-timeframe-routed ownership challenger**. Because this split was discovered from six preserved vectors, any Stage-A improvement requires anti-overfit validation before semantic promotion.

## Decision

**Checkpoint 09V = QA PASS / NEGATIVE RESULT / NO SEMANTIC FREEZE.**

Reject:
- reclaim-bar-failed-reversal release as universal ownership rule;
- next-reversal-bar release as universal ownership rule.

Keep current serial POST_QUAL ownership as the control.

## Next bounded unit

`R037_DH05_ACCEPTANCE_TF_ROUTED_GENERATOR_OWNERSHIP_CHALLENGER_REPLAY_NON_PROMOTING`

Predeclared categorical architecture:
- acceptance_tf = S5 -> serial POST_QUAL ownership;
- acceptance_tf = S15 -> FAILURE_CANDIDATE generator release with independent downstream episodes;
- no numeric retuning;
- S06 economics are a veto;
- no promotion from Stage-A count fit alone;
- if material, perform anti-overfit validation before any semantic unfreeze.

No August. No SORB. No MQL5.
