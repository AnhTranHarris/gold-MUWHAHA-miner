# DELTA R037 — DH05 Boundary/Probe Attempt-Ledger Parity — Checkpoint 09C

**Status:** COMPLETE MATERIAL PARITY CLUE / FULL PARENT PARITY NOT YET ACHIEVED  
**Unit:** R037_DH05_BOUNDARY_SOURCE_AND_PROBE_ELIGIBILITY_PARITY_RECONSTRUCTION  
**Parent:** R032-C03_PLUS_DH02_S11_S08  
**Prior durable unit:** R037_DH05_CLEANROOM_PARITY_CHECKPOINT_09B  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB integrated replay:** NOT STARTED / BLOCKED

## Recovery result

The message-delivery timeout did not erase scientific state. Checkpoint 09B and the SORB preregistration/source-QA artifacts were already durable. Recovery therefore resumed only the first incomplete unit.

A second durability audit confirmed a real historical-source gap: the transient R005/R006/R032 DH05 producing Python bytes were never committed or preserved in the current Drive/Library inventories. Their hashes and output fingerprints remain durable, but the source bytes cannot be rolled back from Git history.

The committed Checkpoint-09B clean-room producer under-produced the earliest probe funnel by roughly 2–4x, so downstream reclaim/reversal tuning was correctly stopped.

## Bounded question

Can the Checkpoint-03 early funnel be explained by:
1. a different causal meaning of frozen `boundary_source = M5 swing`; and/or
2. a different definition of a DH05 `probe` observation,
without retuning any numeric DH05 vector?

The post-commit diagnostic source is:

`research/delta/experiments/delta_r037_dh05_boundary_probe_parity.py`

Source commit: `9d8b3d0b53deedb69e81ffd132feb82888176c71`  
Blob: `0cc173633ba8f91771b11ab2d39cc659340b6c3d`  
Source-file SHA-256: `84093a3f5ce39d09c4241bfba4c7244770ba7b2ea4f7df041bbc28498e08a8f9`

The official post-commit replay used the canonical January source:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**.

## Major parity breakthrough

The best reconstruction is:

- **symmetric two-bar confirmed M5 swings**; and
- while an event is still pre-failure, a return to the pre-break side causally re-arms the same boundary, so the next crossing is counted as a new **probe attempt**.

This is a counter/attempt-ledger interpretation; it does not manufacture a new economic trade and does not alter a frozen threshold.

Across all six preserved M5-swing vectors, the Checkpoint-03 probe target totals **40,190**. The new diagnostic misses by only **626 probes = 1.5576% absolute aggregate error**.

The Checkpoint-03 qualified target totals **4,592**. The diagnostic misses by **383 = 8.3406%**.

That is a very large improvement over Checkpoint 09B, whose clean-room producer was thousands of probes short.

## Width comparison

| M5 symmetric swing width | Probe abs error | Qualified abs error | Total funnel abs error |
|---|---:|---:|---:|
| 1 | 10,795 | 773 | 14,458 |
| **2** | **626** | **383** | **3,718** |
| 3 | 7,858 | 1,087 | 12,859 |

Width 2 is therefore the only tested symmetric boundary definition that materially approaches the preserved early-funnel fingerprint.

## Six-vector width-2 fingerprint

Stage order: `probe / qualified / accepted / failure / reentry / reclaim / reversal / signal`.

- **A03:** target 6731/1009/207/797/432/266/187/187; actual **6705/882/367/753/399/252/183/183**
- **S05:** target 7875/318/28/290/51/15/9/9; actual **7699/245/48/230/49/17/8/8**
- **S06:** target 3470/1606/245/1358/1211/683/617/617; actual **3563/1589/735/1284/848/465/433/433**
- **S09:** target 7748/208/40/168/61/40/9/9; actual **7651/163/116/134/39/29/8/8**
- **S10:** target 6496/1316/202/1106/623/294/206/206; actual **6526/1216/465/948/549/268/189/189**
- **S16:** target 7870/135/43/92/37/18/8/8; actual **7666/114/104/50/10/9/2/2**

## Scientific interpretation

Checkpoint 09B's statement that the entire upstream boundary source was wrong was too broad. Most of the probe deficit can be explained by a **probe-attempt counting/state semantic mismatch**, plus a likely one-bar difference in M5 swing confirmation width.

The remaining mismatch is now localized much more tightly:

- acceptance is too permissive for S06/S10/S09 under the current reconstruction;
- failure/reentry conversion remains too weak, especially S06;
- reclaim/reversal remains downstream of that state mismatch.

Therefore the next correct question is **not another boundary search and not parameter tuning**. It is exact causal reconstruction of the **ACCEPTED vs FAILURE_CANDIDATE vs REENTRY transition semantics** while preserving:
- symmetric M5 width 2 as the active parity hypothesis;
- repeated pre-failure same-boundary probe-attempt ledger;
- all six frozen numeric vectors.

## Decision

**Checkpoint 09C = QA PASS / MATERIAL RECONSTRUCTION BREAKTHROUGH / FULL PARITY FAIL.**

Freeze as a parity hypothesis:
1. symmetric two-bar confirmed M5 swing boundary;
2. repeated causal same-boundary pre-failure probe-attempt counting.

Do **not** yet claim historical DH05 parity.

Do not:
- retune numeric vectors;
- execute Checkpoint 10;
- integrate SORB;
- use August;
- start MQL5.

## Next bounded unit

`R037_DH05_ACCEPTANCE_FAILURE_REENTRY_SEMANTICS_PARITY_RECONSTRUCTION`

Goal:
reproduce the preserved Checkpoint-03 accepted/failure/reentry funnel using the frozen 09C boundary/probe hypothesis before any later reclaim/reversal or economic integration work.

Official result SHA-256:
`c7afe32a538c1168523a664f67ed1f32f394f8ea7f537e92dbc6c590f2e64cf5`

Compact checkpoint manifest:
`research/delta/reference/DELTA_R037_DH05_BOUNDARY_PROBE_CHECKPOINT_09C.json`
