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

## R10 exact historical call-chain recovery

The preserved V2 freeze bundle contains `beta064_frozen_monthly_ps088_hold08.py`, which directly exposes the historical Checkpoint-01 execution path:

`beta064_MM_1s.pkl -> historical feat_from_d(d) -> v2.add_extra(v1.candidates(b), b) -> v1.make_labels -> v1.add_model_features -> frozen Jan-FIT models`.

This is exact source evidence that:

- `v1.candidates(b)` from the lost helper was the parent proposal generator;
- E1/E2/E4 were then removed/replaced by the exact V2 rules;
- the historical `feat_from_d` used left-edge Pandas five-second timestamps without the later +5s completion shift;
- the corrected `beta064_causal_core.py` differs by explicitly shifting the five-second index to right-edge completion time.

The historical and corrected feature builders otherwise preserve the same main state family: price/spread/tick aggregation, multiscale returns and efficiency, volatility/ATR, prior 5m/15m/60m structure, tick_z, daily quote-activity-weighted value, vwap state, range ratio and UTC ORB state.

Exact historical generic UTC ORB timing is now recovered:
- ORB starts at 08:00 and 13:30 UTC;
- first 15 minutes define the range;
- historical active window is [ORB end, ORB end + 90 minutes).

A preserved contemporaneous BETA source, `beta064_session_entries.py`, also supplies literal mechanism/score-family corroboration:
- ORB accepted break: `65 + 8*eff60 + 4*tick_z`;
- sweep/reclaim: `67 + 8*eff15 + 3*tick_z`;
- failed break: `66 + 6*tick_z`;
- compression release: `64 + 7*tick_z`;
- VWAP reclaim: `60 + 8*eff60`.

These are corroborating BETA evidence for E3/E5/E7/E10/E12 in the recovery scaffold, but they remain non-authoritative for the lost parent `candidates()` until candidate/model parity passes.

The exact call-chain recovery further confirms that the inherited 2,097 Checkpoint-01 base positions are tied to the suspended left-edge feature path. Historical-left-edge reconstruction is forensic only; a future MT5-eligible checkpoint must be rebuilt on corrected right-edge state.

Authoritative crash/retry log:
Google Doc `BETA064 beta064_multidesk_loop.py Recovery Log — Crash/Retry Continuity`, ID `1VJaUMULaTonJxTRCiWKsof_bHSsjg1ouSfLVCKDepi8`.


## R11 cross-month replication and edge-emission correction

The current source-grounded parent mechanism masks were replayed on original Dukascopy historical-left-edge five-second state at the frozen C02C selected timestamps for February and March.

Selected-mask recall remained high:

| Specialist | Feb recall | Mar recall |
|---|---:|---:|
| E3 ORB | 100.00% | 100.00% |
| E5 VWAP Reclaim | 98.39% | 92.59% |
| E6 Value Reversion | 99.23% | 99.57% |
| E7 Sweep/Reclaim | 100.00% | 100.00% |
| E8 Level Bounce | 100.00% | 100.00% |
| E9 Level Break | 94.41% | 95.83% |
| E10 Compression Release | 100.00% | 100.00% |
| E11 Kinetic Ignition | 100.00% | 100.00% |
| E12 Failed Expansion | 100.00% | 100.00% |

This strongly corroborates the recovered mechanism families beyond January.

However, the prior universal FALSE->TRUE edge-emission hypothesis is rejected:

- E6 edge recall = 0/130 Feb and 0/231 Mar;
- E11 edge recall = 166/403 (41.19%) Feb and 200/592 (33.78%) Mar;
- E9 edge recall = 125/161 (77.64%) Feb and 161/216 (74.54%) Mar;
- E10 edge recall = 71/80 (88.75%) Feb and 62/78 (79.49%) Mar.

Therefore the earlier Jan-FIT 30,613 versus frozen 30,579 count is a numerical clue only, not near-source certification. The lost helper likely used specialist-specific persistence/debounce/gating semantics.

### Session-lineage escalation

Git chronology after the causal erratum is now explicit:

- 12:47:22Z b23d3fb...: Checkpoint-01 causal timestamp erratum.
- 12:47:25Z / 12:54:30Z: right-edge dual-tick diagnostic records.
- 13:27:00Z 5e3f5d...: session authority child is added explicitly over frozen Checkpoint-01.
- 13:27:03Z aef6187...: record says all 2,097 frozen Checkpoint-01 positions are reserved first and session trades gap-fill around them.
- preserved beta064_session_router.py loads beta064_allmonths_predictions.pkl as its upstream candidate/probability table.

No durable BETA source has yet been found proving beta064_allmonths_predictions.pkl was regenerated from corrected right-edge state after the erratum.

Current classification:
- 2,097 base positions: confirmed historical-left-edge contaminated.
- 2,973 session additions: high-risk / presumed inherited from the same frozen prediction lineage unless contrary BETA evidence is recovered.
- Checkpoint02/03 remain historical observed artifacts, not causal MT5-certified systems.

The recovery scaffold has been amended so its universal edge-emission hypothesis cannot be mistaken for recovered source.
