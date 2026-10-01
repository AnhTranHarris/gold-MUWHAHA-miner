# BETA064 missing multidesk helper recovery — R9B/R9C forensic checkpoint

**Status:** ACTIVE RECOVERY / RECOVERY_UNCERTIFIED  
**Lineage:** BETA only  
**Alpha/GAMMA:** prohibited and not used  
**August:** sealed  
**MQL5:** prohibited during recovery

## Confirmed causal-lineage defect

The Checkpoint-01 causal erratum (commit `b23d3fb608e175e15568088ca1bd1be825bbd346`) explicitly suspended the historical 2,097-trade / 90.56% Entry→Hold panel because [t,t+5s) bars were left-edge stamped at t and therefore contained future intra-bar information.

No committed causal parent-generator/prediction-table rebuild exists between that erratum and the subsequent session-gapfill work.

The session-gapfill records/code then explicitly:

1. treat Checkpoint-01 as the frozen/authoritative control;
2. reserve all **2,097** Checkpoint-01 positions first;
3. add **2,973** gap-fill trades;
4. report **5,070 = 2,097 + 2,973**.

Therefore at least the 2,097 inherited base positions in the Checkpoint02/03 lineage are the historically suspended Checkpoint-01 panel.

This does **not yet prove** that every later session/C02C/C02D addition uses the same defective state table. The lineage of `beta064_allmonths_predictions.pkl` remains unresolved.

**Result:** Major Checkpoint 03 observed metrics remain preserved research artifacts, but causal/MT5 Entry-parity certification is suspended until reconstruction is complete.

## R9A alignment test

January original Dukascopy ticks were rebuilt into corrected right-edge completed 5-second state.

At frozen January selected timestamps, simple source-grounded masks had the following same-side recall:

| Specialist | corrected RIGHT edge | historical LEFT sensitivity | causal previous-bar emission |
|---|---:|---:|---:|
| E7 | 4.55% | 100.00% | 15.15% |
| E9 | 22.14% | 98.47% | 16.03% |
| E10 simple release | 2.56% | 43.59% | 0.00% |
| E12 | 0.00% | 100.00% | 6.33% |

A causal “same event emitted one completed bar later” explanation is therefore rejected.

## R9C candidate-population reconstruction

Frozen base Entry LightGBM metadata gives a hard January FIT population fingerprint:

**30,579 training candidates.**

Using the evidence-backed simple E3/E5–E12 mechanism masks plus exact V2 E1/E2/E4:

- firing on every qualifying five-second bar produces ~105k FIT rows and is implausible;
- emitting only FALSE→TRUE event transitions reduces the total to **32,552**;
- adding three BETA-consistent gates:
  - E5 `eff15 >= 0.30`
  - E9 `eff15 >= 0.30`
  - E10 `tick_z >= 0.50`
  yields **30,613**, only **+34 (+0.111%)** from the frozen 30,579.

Historical-state selected-ledger recall from the base masks:

| Specialist | Jan selected historical-state recall |
|---|---:|
| E5 | 40/40 = 100% |
| E6 | 140/141 = 99.29% |
| E7 | 66/66 = 100% |
| E8 | 2/2 = 100% |
| E9 | 129/131 = 98.47% |
| E10 | 38/39 = 97.44% |
| E11 | 268/268 = 100% |
| E12 | 79/79 = 100% |

This is strong forensic evidence that the lost helper used event-style mechanism proposals aligned to the historical left-edge five-second state.

The remaining 34 rows must **not** be tuned away only to match the count. Exact E3/E8 boundary semantics, deduplication/warmup behavior, or another source-grounded gate must explain them.

## Recovery rule

The reconstruction must maintain two explicit modes:

- **HISTORICAL_LEFT_EDGE_FORENSIC** — only for reproducing the old defective lineage and discovering the lost implementation.
- **CAUSAL_RIGHT_EDGE** — the only mode eligible for a future replacement checkpoint and eventual MT5 work.

Historical-left-edge results may never be promoted to MT5.

## Remaining certification gates

1. exact Jan FIT candidate identity, not merely count ~=30,579;
2. timestamp/side/specialist/raw-score/horizon/checkpoint parity;
3. exact one-second `quote_pressure` and `qv_imb` parity;
4. frozen base model probability identity;
5. frozen session-router probability/authority identity;
6. establish whether session additions inherited left-edge predictions;
7. corrected-right-edge Jan→Mar replay;
8. replacement causal checkpoint;
9. only then MT5 Entry-parity work.

Authoritative crash/retry log:
Google Doc `BETA064 beta064_multidesk_loop.py Recovery Log — Crash/Retry Continuity`, ID `1VJaUMULaTonJxTRCiWKsof_bHSsjg1ouSfLVCKDepi8`.
