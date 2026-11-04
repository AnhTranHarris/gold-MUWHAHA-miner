# H1V2 R18 — Two-Feed Multiscale, Multihorizon, Broker-Adaptive Entry Research

**SCIENTIFIC CLASS: FUTURE-PRIVILEGED OFFLINE HINDSIGHT. NOT AN AS-OF BUY/SELL PREDICTOR. NO MT5 EA PROMOTION OR DEALER FILL CERTIFICATION.** Original R9 v2 repaired runtime, H1V2 teacher, R11S1–R17 source and prior results are unchanged. R18 is additive and isolated.

## Immutable source governor

Parent GitHub SHA: `41ed0cc66bd4b3ee5262b4c6bb28b73808a88d54` (original R17). Repaired R9 v2 runtime: `ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0`. Original H1V2 teacher `edce573d9c53b743dc5de1b0d741c81370af52c1`.

Full R18 re-audit documents (NOT substitutes):
- https://docs.google.com/document/d/1G8enmU_dEAm0i7qQb_zsyZHx5vJUGgZvNwewjfr5vPI/edit
- https://docs.google.com/document/d/1cPeYUsP-c_RITV_rWtCKNbzJkE2ppdgZ8pdNhUR5H7g/edit
- https://docs.google.com/document/d/1ZNguYaxZ84TOo7w8DvRHF2T_QbVXPcaAn0gVAX-fWPY/edit
- https://docs.google.com/document/d/1UV_F2VOazU36XDS2YN9B-tVSgvg8ESTz0mAI1I_L4II/edit
- https://docs.google.com/document/d/15ymqAiqFCIbioFaD2H-0Cvw4LsLGoWzYYpyF7Hb4DAk/edit

**Active append-only research log (read first):** https://docs.google.com/document/d/1aN6HOvsVj4_OQyCxsUeH8lkuUkYoW6rHH8kQbIc7Q7U/edit

Existing R11S1 source-exact one-sided rolling extrema helper SHA256 `c52de41072911ad53dedadfb3dba1899ea112e41a9e58e48ea29a7903e3ec475`. Existing R13 as-of prefix engine SHA256 `e90da8141639428d173d7587d44f251748130e690c1f5f754594727ba691ed7e`. These are vendored **byte-exact, unchanged** under `upstream/`, and the new source refuses drift. R11 auxiliary `entry_contract.py` is recovered from original GitHub file blob `a1014b28d5aae2f7cd3efc0db25d68fc12339e5e`; a local Google-Docs-exported **format-normalized** transport exists, and the byte-exact GitHub source should be restored under `upstream/` before full external reproduction. This is imported by original `entry_survivability.py` but its candidate functions are not called by the R18 rolling-extrema path.

## Data sources — two different feeds, not dealer executions

1. **MT5_BROKER_EXPORT:** Full native quote export `XAUUSD_MT5_BROKER_2026_MM_ticks_ALL.csv.gz` in PRIMARY Drive folder https://drive.google.com/drive/folders/1XzHug6HYQdSKIbKuGhBTOUHawAXynIb4 . This export was obtained from the original Coinexx-linked MT5 research workflow, but historical deal fills, exact broker commission and slippage are NOT certified here. Both original MT5 R9 Strategy Tester REAL and SYNTH are separate archives; do not equate this broker export to either.
2. **DUKASCOPY_RAW:** Full raw `XAUUSD_DUKAS_2026_MM_ticks.csv.gz` in PRIMARY Drive folder https://drive.google.com/drive/folders/1lSCfO_awUKkbR4I6xDTy9orjIl0SrgIV . No assumption of live Dukascopy fill priority.

All eight raw gzip SHA256 constants are in `src/r18_broker_multihorizon.py:PINS`. Inputs are independently rehashed before any run; mismatch is fatal. Both sides are at original observed Bid/Ask source quote ordinals. Source prices use integer **$0.001/oz**, never account USD profit. BUY pays ask and liquidates bid, SELL receives bid and covers ask. Nominal fee $0.02 quoted-price, profit target +$0.10 quoted-price; actual account cash commissions require independent verification.

**Clock validation:** MT5 `time_msc` is historical source-server clock, aligned against Dukascopy raw UTC one-minute last-quote midpoints on first SIX full-calendar days of each source month. Unique best shifts Jan/Feb **−2h**, June/July **−3h**. Median absolute matched-minute midpoints $0.075/$0.130/$0.060/$0.055 respectively. Adjacent UTC shifts have much larger median discrepancy. These are empirically supported clock-normalization research assumptions, NOT evidence of MT5 dealer execution permissions or a substitute for historical broker timezone metadata. In-production historical clock offsets must be independently verified across complete months, especially DST transitions.

## Mechanism architecture and noninterchangeable labels

*Original control* `ORIGINAL_S1_F15_SAFE30`: favorable executable +$0.10 nominal net first quote **≤15 seconds**, **no opening-liquidation −$0.10 adverse through complete 30s**, quote coverage/censor exactly as original pinned R11S1, even AFTER a favorable touch. This label never changes.

*Distinct new contract* `NEW_FIRST_TOUCH_{15,30,45,60}_BEFORE_ADVERSE`: reach +$0.10 nominal price net at the first actually observed quote by the named bound, **before** any −$0.10 opening-liquidation adverse touch, with no hidden >15s quote gap prior to first TP. Position reservation ends at first favorable quote. This explicitly allows **post-exit** price retracements that would fail original full30 S1. It is NOT the original R9 $0.30 stop/$0.03 trail/timeout; those must be separately replayed before economic approval. Longer horizon cannot be reclassified as original strict15. All trade-entry source ordinals and future-selected side are preserved in per-month original-quote-ordinal NPZ.

*Observed-as-of admission lanes*: original BASE first250 ≤$1.50, DENSE ≤$1.50, WIDE first250/intrabin squeeze ≤$4; R18_VOLATILITY_COMPENSATED (current spread vs actually observed prior 15s/60s price displacement and spread EMA); R18_WATCH60_SPREAD_PERSISTENCE and R18_WATCH60_FLOW_RECOVERY (at most 60s watch from actually observed wide spread, two *later* observed confirmations, reset on >15s raw quote gap); R18_100MS_BROKER_GRID (new first100ms clock, state-dependent quote price); R18_ADAPTIVE_UNION_4000 (union, no forced trades); R18_WIDE_8000_FIRST250_DIAGNOSTIC (unapproved high-spread admission with full bid/ask pricing); full observed ≤$4 R16 diagnostic control.

**Both BUY and SELL are independently labeled OFFLINE** at each actually observed candidate; future-privileged side enters ONLY the hindsight selected interval scheduler, which maximizes historical disjoint profitable first-target intervals. No oracle may be read into a live model or claimed as prospective accuracy. Candidate as-of gates use no label/outcome future information. There is no trained BUY/SELL/WAIT policy in R18. A good future-known bound is a research capacity ceiling, not a deployable policy.

## Full-calendar reproducibility

Required original raw + source reference files in `--root`:
- Eight raw gzip files with names and hashes above.
- Original UTC-aligned source quarter reference `R12DQ_COMPLETE_ALL_11520_SOURCE_QUARTERS_S4_R12_R12DQ.csv`, itself SHA-pinned per output receipt. Reference is NOT an hour count divided by four. Original Jan27,980 / Feb33,523 / Jun31,758 / Jul24,324 original R9 SYNTH UTC-trade counts.
- `upstream/r13_crossbroker_horizon_lanes.py` + `upstream/entry_survivability.py` byte-exact source, and `upstream/entry_contract.py` authentic restored import dependency.

Run each source/month separately, one at a time, preserving original source SHA and its own full quart/hour receipt:

```
python -m pytest tests/test_r18_source_contracts.py -q
python src/r18_broker_multihorizon.py --source DUKASCOPY_RAW --month 01 --root /mnt/data --output results
python src/r18_broker_multihorizon.py --source MT5_BROKER_EXPORT --month 01 --root /mnt/data --output results
# repeat separately for 02,06,07 and both feeds
```

Each source/month emits its **50 complete lane×outcome records**, every one of its calendar 15-minute rows and hourly rows including zero-reference periods, complete future-selected side/entry/exit source ordinals, a fresh original source SHA + output SHA manifest receipt, and original log. Do not average away broker/day/month failures. All outputs remain nondeployable and must be compared against 85% R9 monthly trade volume, 80% meaningful strict correctness, positive executable net after true costs, as-of causal student, latency/friction and fully realized account replay.

## Current scientific boundary

An original source S1 15/30 control reproducing earlier R12 counts is a regression invariant. An increased selected historical count in a distinct 60s first-touch contract is **not an 80% forecast win rate**, and firstTP labels ignore realized failed-position cash P&L. No fill rejection/slippage, real Coinexx/Dukascopy dealer data, initial account ruin, real MT5 compile, or independent OOS deployment approval is provided by this code. The proper future falsifier is frozen-signal observed-fill 100ms/500ms latency and full source-broker cost/exit account replay; never reselect hindsight winners after stress.
