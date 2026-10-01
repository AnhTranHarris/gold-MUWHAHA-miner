# BETA064 multidesk_loop Recovery — R14 Source Archaeology, Right-Edge Rebuild, and Safe Rollback

**Date:** 2026-10-01  
**Lineage:** independent BETA only  
**August 2026:** SEALED  
**MQL5:** NOT AUTHORIZED  
**Historical Checkpoint 03:** PRESERVED FOR FORENSICS; CAUSAL/MT5 ENTRY PARITY SUSPENDED

## Decision

R14 finishes the missing-helper repair campaign without fabricating historical parity.

The lost transient `beta064_multidesk_loop.py` could not be recovered exactly from the surviving GitHub/Drive artifacts, revision history, model-freeze bundles, selected ledgers, or predecessor source. The surviving evidence is sufficient to reconstruct a transparent new right-edge causal helper, but it is not sufficient to certify the old 5,469-trade Checkpoint-03 candidate/probability surface.

The corrected right-edge rebuild was executed Jan-Jul on the canonical Dukascopy corpus with August unopened. It fails the frozen Entry survivability requirements by a very large margin. Therefore the repair outcome is a **safe rollback**, not a retune of the old checkpoint.

The active causal research base is rolled back to **BETA063**, the last causally audited durable Entry/Hold research base with its 62/62 QA record and reproducibility contract. BETA064 Major Checkpoints 01/02/03 remain historical/forensic artifacts only until a genuinely new causal Entry checkpoint is independently built and validated.

## What was recovered exactly

The recovery preserved or independently verified:

- Jan-Jul canonical Dukascopy raw tick corpus and ordered executable Bid/Ask chronology.
- Corrected completed-five-second RIGHT-edge observability.
- Exact V2 E1/E2/E4 specialist replacements.
- Frozen Entry feature order and LightGBM family/parameters.
- Frozen offline Entry->Initial-Hold label geometry.
- Frozen session-router and Hold artifacts as historical learned artifacts.
- Historical selected ledgers and historical Checkpoint-03 observed metrics.
- Base-first ownership/session-child logic as historical routing logic.

None of those surviving artifacts authorizes the historical candidate/probability surface when its parent proposal generator is not source-equivalent.

## Source archaeology result

### quote_pressure

BETA039 directly preserves the predecessor BETA026 formula:

`quote_pressure1 = original_side * (up_quote_count - down_quote_count) / max(1, up_quote_count + down_quote_count)`

This proves the predecessor value was already candidate-side signed and rules out double-signing it.

BETA064's one-second cache, however, exists before a candidate side is known. R14 therefore uses the transparent market-direction form:

`quote_pressure = (up_quote_count - down_quote_count) / max(1, up_quote_count + down_quote_count)`

This is classified **SUPPORTED RECONSTRUCTION**, not historical parity.

### qv_imb

No exact historical BETA064 qv builder was recovered. R14 explicitly uses:

`qv_imb = (sum_bid_volume - sum_ask_volume) / max(epsilon, sum_bid_volume + sum_ask_volume)`

This is also **SUPPORTED RECONSTRUCTION**, not historical parity.

### E3/E5-E12 emission

The mechanism families and broad gates are strongly supported by surviving records, but exact historical debounce/emission/raw-score semantics are not fully recoverable. R14 uses the R11 source-supported mechanism masks with event-edge emission for the new causal rebuild only.

## Forensic checksum against the frozen January FIT population

The frozen Entry model was trained on exactly **30,579** January FIT rows.

Using the reconstructed mechanism masks on the historical LEFT-edge state only as a forensic checksum:

- event-edge emission: **30,618** FIT proposals
- difference from frozen training population: **+39 rows / +0.13%**
- side-edge emission: 31,624
- 30-second debounce: 32,242
- persistent-state emission: 101,897

The near-exact event-edge count is important evidence about historical emission density, but it is not source parity. E6 selected timestamps frequently occur deep inside the broad persistent mask, proving the broad mask itself is not the exact historical event clock.

## Frozen-model probability parity attempt

The frozen Entry models were replayed against multiple plausible q/p and qv semantics and nearby time offsets.

No combination reproduced historical probabilities. Best probability errors remained materially large; time-shift zero was best. Therefore the old `beta064_allmonths_predictions.pkl` lineage cannot be reconstructed merely by choosing a q/p or qv formula.

Conclusion: exact historical Checkpoint-03 candidate/probability parity is **not recoverable from current evidence**.

## New corrected RIGHT-edge rebuild

R14 rebuilt one-second caches directly from raw Jan-Jul ticks, then applied the corrected five-second RIGHT-edge causal state and retrained the Entry models using only the historical Jan FIT/CAL chronology.

### January source-equivalent population size

- January total candidate/label rows: 128,369
- Jan FIT rows: **30,616**
- Jan CAL rows: **5,749**
- Jan post-CAL diagnostic rows: 92,004

The R14 FIT population is only **37 rows above** the historical 30,579-row frozen population. That confirms the broad candidate-density reconstruction is close while also proving that density parity is not enough.

### Raw causal label behavior

| Partition | Rows | Survival | Favorable first passage | Diagnostic net |
|---|---:|---:|---:|---:|
| Jan FIT | 30,616 | 11.9447% | 4.4389% | -$24,086.174 |
| Jan CAL | 5,749 | **11.5672%** | **3.7050%** | **-$4,266.005** |
| Jan post-CAL diagnostic | 92,004 | 19.1253% | 10.2778% | -$72,160.297 |

This is not a small degradation. The historical high-survivability checkpoint is not reproduced once the candidate state is made genuinely observable at the right edge.

### Model/gate behavior

Historical base gate: `p_surv >= 0.88 && entry_score >= 0.30`.

Frozen-style R14 Jan-Jul replay:

- 0.80 / 0.30: 3 trades, 33.33% survival, -$5.667
- 0.85 / 0.30: 0 trades
- **0.88 / 0.30: 0 trades**
- 0.90 / 0.30: 0 trades
- 0.92 / 0.30: 0 trades
- 0.95 / 0.30: 0 trades

A broad Jan-CAL threshold scan with minimum 20 one-position proposals found a maximum observed survival of only:

- **57.1429% survival**
- 21 trades
- 14.2857% favorable-first-passage
- **-$18.553**
- PF 0.26694

Even the best causal calibration region is nowhere near the 85% checkpoint floor and remains economically negative.

## Why R14 does not proceed to Hold

The old project contract requires Entry to survive before the Initial-Hold model can be treated as a valid next stage. R14's causal Entry replacement fails that gate. Running the old Hold model on a failed/non-equivalent Entry population would create another provenance error, so the Hold stage is intentionally not promoted.

The frozen Hold artifact remains preserved as historical research evidence only.

## Rollback target

The recovery does **not** hard-reset or delete history.

Instead:

1. BETA064 Checkpoints 01/02/03 remain immutable historical records.
2. Their authority is changed to **FORENSIC_ONLY / CAUSAL_CERTIFICATION_SUSPENDED**.
3. The active causal research base is **BETA063**, because it has a durable reproducibility contract, original executable quote-side treatment, causal +5-second update semantics, and **62/62 QA assertions passed**.
4. R14 is retained as the explicit failed causal reconstruction so future work cannot accidentally repeat the same recovery path.
5. Any future BETA064 successor must receive a **new checkpoint identity** and must earn its result on corrected right-edge chronology. It may not inherit the Checkpoint-03 name.
6. August remains sealed.
7. No MQL5 work is authorized by this recovery.

## Durable R14 artifacts

GitHub:

- `research/recovery/beta064_multidesk_loop_RIGHTEDGE_R14.py`
- `research/recovery/BETA_064_MULTIDESK_LOOP_R14_SOURCE_ARCHAEOLOGY_AND_RIGHTEDGE_REBUILD.md`
- `research/recovery/BETA_064_MULTIDESK_LOOP_R14_STATE.json`
- `research/results/BETA_064_R14_JAN_MODEL_DIAGNOSTIC.csv`
- `research/results/BETA_064_R14_JAN_CAL_THRESHOLD_AUDIT_TOP20.csv`
- `research/results/BETA_064_R14_RIGHTEDGE_GATE_SUMMARY.csv`

Local executed artifacts/hashes retained during R14:

- rebuild runner SHA-256: `75beaf3aac12c28b79cb0fcca1174cff73b0b78bc1ebaff404e73e74e0644780`
- gate summary SHA-256: `114cc9e0282d3dafe98788f834d134118e03ebf7ec45556c3564375f31f9c69d`
- Jan CAL threshold audit SHA-256: `695435f97aacc41598c29534ea01d9c443477ad6adb14f5c33eacce7e89d1b78`
- Jan model diagnostic SHA-256: `7ef86d7300de6ac13cdc65c71bef0ca49ac52f7d207087b497229e412b260af1`
- retrained Entry models SHA-256: `13f0b03c626a9c90faba0a61773fc892f3b6cd2c4be97de92255992caa837cc9`
- Jan-Jul prediction table SHA-256: `e7f9325dabe6c65944bc3104bf9d6670c7b103d7a923eca8841dc9d04bebdd1f`

Large local model/prediction files are evidence from this run, not promoted deployment artifacts.

## Final recovery verdict

**Missing-helper recovery: CLOSED.**  
**Exact historical Checkpoint-03 parity: NOT RECOVERED.**  
**Historical Checkpoint-03 authority: SUSPENDED / FORENSIC ONLY.**  
**New R14 right-edge multidesk checkpoint: REJECTED FOR PROMOTION.**  
**Safe active causal research base: BETA063.**  
**August: SEALED.**  
**MQL5: NOT AUTHORIZED.**

The repair is complete because the branch can no longer silently inherit a causally invalid checkpoint. The next scientific task is a new causal Entry architecture, not another attempt to reverse-engineer the old left-edge economics.
