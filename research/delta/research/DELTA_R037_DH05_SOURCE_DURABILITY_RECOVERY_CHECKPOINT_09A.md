# DELTA R037 — DH05 Diagnostic Source Durability Recovery — Checkpoint 09A

**Status:** COMPLETE QC / SOURCE BYTES NOT RECOVERED / CLEAN-ROOM REBUILD REQUIRED  
**Parent:** R032-C03_PLUS_DH02_S11_S08  
**Science checkpoint salvaged through:** R037_DH05_FAILURE_REENTRY_PERSISTENCE_CHECKPOINT_09  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Why this QA gate exists

Message-delivery timeout recovery found that R037 DH05 Checkpoints 04–09 were durably preserved as GitHub reports/manifests and, through Checkpoint 08, workbook records. Checkpoint 09 was subsequently reconciled into the workbook.

However, the producing Python bytes for the DH05 semantic diagnostics were not committed to the live `delta` tree and were not found in the current Drive or Library inventories. Only source SHA-256 identities were preserved.

Under DELTA durability/rebuildability governance, report + result + source hash is not enough to authorize the next behavior-changing diagnostic when the producing source itself cannot be independently rerun.

## Recovery audit performed

The recovery audit checked:

1. live `delta` recursive Git tree for R037/DH05 diagnostic source;
2. GitHub commit file lists for Checkpoints 04–09;
3. Google Drive search for the historical transient R006 producer names:
   - `r005_specialists.py`
   - `secondary_vectors.json`
   - `dh05_results.jsonl`
4. Project/Library search for the Checkpoint-08/09 source hashes and DH05 producer names;
5. mounted runtime cache for recoverable R037/DH05 source.

Result: **no authoritative producing Python bytes were recovered**.

The GitHub tree contains the checkpoint reports and JSON manifests, but no corresponding DH05 diagnostic producer.

## Scientific evidence preserved

The completed checkpoint outputs remain valid **salvage evidence** because their reports/manifests/hashes are mutually consistent and the workbook records the same bounded conclusions.

Do not rerun or discard:
- Checkpoint 04 — active-boundary freeze rejected;
- Checkpoint 05 — reclaim-clock-only repair rejected;
- Checkpoint 06 — reclaim-buffer-only repair rejected;
- Checkpoint 07 — reversal displacement-origin-only repair rejected;
- Checkpoint 08 — reversal-TF ATR + 3-bar efficiency gives exact S06 672 generator signals but not parity;
- Checkpoint 09 — failure/reentry clock is high-leverage, but neither universal interpretation reproduces the family.

## Rejected recovery shortcut

A fresh local clean-room probe was attempted from the surviving white-paper semantics and frozen six-vector parameters. It did **not** reproduce Checkpoint-03 funnel counts.

That probe is therefore rejected and is not a scientific continuation source. Its outputs must not be used to advance the DH05 parity result.

## Required reconstruction gate

Before Checkpoint 10, build and commit a durable clean-room DH05 diagnostic engine that reproduces all of the following without numeric-vector retuning:

### Checkpoint-03 neutral baseline
Trade/signal fingerprint:
- A03 187
- S05 9
- S06 617
- S09 9
- S10 206
- S16 8

### Checkpoint-08 semantic cross
- 1-bar efficiency + M5 event ATR: 187 / 9 / 617 / 9 / 206 / 8
- 1-bar efficiency + reversal-TF ATR: 258 / 14 / 691 / 41 / 251 / 14
- 3-bar efficiency + M5 event ATR: 145 / 5 / 558 / 9 / 151 / 6
- 3-bar efficiency + reversal-TF ATR: 247 / 10 / 672 / 41 / 225 / 14

### Checkpoint-09 failure-clock cross
Neutral:
- current: 187 / 9 / 617 / 9 / 206 / 8
- wait-for-reentry: 282 / 54 / 653 / 11 / 317 / 22

Stage-normalized 3-bar:
- current: 247 / 10 / 672 / 41 / 225 / 14
- wait-for-reentry: 393 / 86 / 717 / 89 / 383 / 38

The rebuilt producer must additionally emit event/failure IDs and signal timestamps so the subsequent signal-multiplicity/admission unit can be run from a durable source.

## Advancement criteria

Source reconstruction passes only if:
1. producing Python is committed before new Checkpoint-10 results;
2. Stage-A source/surface identity is unchanged;
3. six frozen M5-swing DH05 vectors are unchanged;
4. the checkpoint fingerprints above are exactly reproduced or any deterministic difference is explicitly reconciled before proceeding;
5. August is never loaded;
6. no SORB integration occurs;
7. no MQL5 is written.

## Pointer

**Next:** `R037_DH05_DIAGNOSTIC_ENGINE_CLEANROOM_REBUILD_AND_CHECKPOINT03_08_09_PARITY`

Only after that PASS may the project run:

`R037_DH05_PARITY_SIGNAL_MULTIPLICITY_AND_EXECUTABLE_ADMISSION_DIAGNOSTIC`.

