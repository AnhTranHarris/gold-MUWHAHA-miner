# DELTA R037 — Acceptance-Timeframe Metadata Provenance Reconciliation — Checkpoint 09X

**Status:** COMPLETE PROVENANCE RECONCILIATION / LEDGER CORRECTED  
**Unit:** R037_DH05_ACCEPTANCE_TF_METADATA_PROVENANCE_RECONCILIATION  
**Parent:** R037_DH05_ACCEPTANCE_TF_ROUTED_GENERATOR_OWNERSHIP_CHECKPOINT_09W  
**Raw tick replay:** NOT REQUIRED  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose

During 09W recovery, the historical Checkpoint-09S metadata was found to disagree with the frozen DH05 vector tuple used by current causal replays.

This bounded unit answers only:
1. which vector differs;
2. what the corrected 09S count-only diagnostic would have shown;
3. whether later causal Checkpoint 09T must be reopened.

No trading threshold changed.

## Provenance

Producer:
`research/delta/experiments/delta_r037_dh05_acceptance_tf_metadata_provenance_reconciliation.py`

- producer commit: `d67f6a1c562a107a07e8072939a389581316d9fb`
- producer blob: `d5c634b6a498d33a3843c090cca344e6e4cd326f`
- producer SHA-256: `2c5a17afbbe1e98195c591b27b6ae634165cd7d752a7786fe7e87ce5585d6f53`
- runtime result SHA-256: `54e1d9b0df19b3a247d4495e553345b265b1348716edcd61be0b9fbfac6cc2e7`
- runtime: **0.83 s**
- peak RSS: **134,452 KB**
- exit code: **0**
- hard timeout: **30 s**

## Exact mismatch

Only **S16** differs.

Checkpoint 09S hard-coded:
- S16 acceptance_tf = **15**
- S16 reversal_tf = **5**

The live frozen DH05 tuple used by the causal reconstruction has:
- S16 acceptance_tf = **5**
- S16 reversal_tf = **5**

This is not a newly introduced change. Earlier committed clean-room producers already encode S16 as 5/5:
- 09B clean-room producer;
- 09C boundary/probe producer;
- 09D acceptance/failure/reentry producer.

Therefore 09S contains the isolated stale/mistyped categorical metadata.

## Corrected 09S historical diagnostic

Original 09S count-only results:
- acceptance-clock router error: **139**
- clock-topology router error: **61**
- acceptance-TF sign split: claimed perfect.

Corrected with frozen S16 = 5:
- acceptance-clock router error: **153**
- clock-topology router error: **75**
- acceptance-TF sign split: **NOT perfect**.

Correct live groups:
- S5: S06, S10, S16
- S15: A03, S05, S09

Target-minus-POST_QUAL-signal signs:
- S5: S06 **-36**, S10 **-21**, S16 **+17**
- S15: A03 **+114**, S05 **+42**, S09 **+108**

Thus S16 explicitly breaks the claimed S5 negative-gap uniformity.

## Does 09T need reopening?

**No.**

Checkpoint 09T did not rely on the stale 09S META table at runtime. It derived acceptance/reversal categories from the live frozen `VECTORS` tuple and then causally replayed the challenger on canonical Stage-A ticks.

09T already rejected:
- acceptance-timeframe conditional failure clock;
- clock-topology router;
- universal wait-reentry;
- universal stage-normalized carry-forward.

Correcting the historical 09S label cannot reverse that later causal falsification.

## Decision

**Checkpoint 09X = QA PASS / PROVENANCE CORRECTION.**

Correct the research interpretation:
- 09S remains a historical clue only;
- remove the “perfect acceptance-timeframe sign separation” claim from active reasoning;
- keep 09T negative causal result intact;
- do not alter current frozen DH05 semantics.

## Next bounded unit

`R037_DH05_GENERATOR_RELEASE_TOPOLOGY_PROVENANCE_HARVEST`

Purpose: harvest the already completed 09H/09I/09U/09V/09W per-vector generator-release evidence using corrected categorical metadata, identify only reconstructible non-numeric topology candidates, and stop if no clean category survives.

No August. No SORB. No MQL5.
