# H1V2 R12D-Q — full source-exact observed quote entry and quota-priority research

**Dated:** 2026-11-03 America/Chicago. **Classification:** in-sample, future-privileged hindsight-only; **NOT** a causal forecast, MetaTrader 5 EA update, trade-fill proof, broker-backtest result, economic profitability proof, out-of-sample approval, or authorization for demo/live funds.

## 0. Existing immutable research lineage and source bootstrap order

1. The **complete original H1V2 hourly forensic audit**, not a summary: https://docs.google.com/document/d/1n8Zd37SH3k2mNYpCERHsGSeR5GL-vDNLDv780Bv5-Do/edit
2. Its complete original lossless research ZIP (47 members), all 2,880 UTC hours, 246 infeasible 30-second hours and original R9/S1 source SHA: https://drive.google.com/file/d/1hsUSUyF3GJbtRSFR1c9mtDo-44EK_Rap/view
3. The **entire H1V2 R11 unsummarized ledger**: https://docs.google.com/document/d/1eGC-vxRDzu7FxQOY-3PPUfWzoVRrOZU5jaDozuuv0xI/edit
4. The **entire R12 append-only continuation ledger**: https://docs.google.com/document/d/1v0X5Vkif81qV784Ja6FVe5DfyQLx7RoEw-yjC4m7D1Y/edit
5. Frozen original H1V2 teacher SHA `edce573d9c53b743dc5de1b0d741c81370af52c1`; repaired R9 v2 v5 runtime SHA `ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0`; R11S5 parent `2bcd0372dfba415d7b28a84a3346011efbb32c2d`; original R12 research branch `carson/h1v2-r12-adaptive-tp-hour-quarter-oracle-20261103` head `69215c4061a57fb4745404e2aeac0d0ff502eb03`.
6. Current new **additive** branch `carson/h1v2-r12d-dense-asof-quarter-capacity-20261103` starts at R12 original head. ALL ORIGINAL PATHS REMAIN INTACT.

**Never substitute this README for the unabridged audit, individual all-hour/quarter CSV, entry quote-ordinal trace, full raw source, original R11S1 labels, or historical negative R2–R11 findings.**

## 1. Independent frozen benchmarks and exact source identity

- Dukascopy XAUUSD original quote sources Jan/Feb/Jun/Jul 2026, **32,290,648** quote ordinals. Source file hash (gzip bytes) January `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`, February `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`, June `34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2`, July `e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7`.
- R11S1 full frozen source ZIP monthly SHA: Jan `97d98454751f0037581cc706260a60f7bc8085e5ae3b92ca719474b719041dee`, Feb `ab014ab2ef6512b5870fcdc50f0828c33f8b3a09547d886225ad7915037e27dc`, Jun `4b46b337d84a2ab16be63c61edea9e98160d9a288b6ae14ddebe79ae484a1194`, Jul `2352e60f7f8c374d533ae3c91aac6def25adb47696ecb0728065c34d025f1ce5`.
- Original frozen R11S4 quote-position archive SHA `fba5a62a4d77d09450a9ac00522cff2532664a5e4d466573cb2a5694bec711fc` (source original 30sec occupancy). Original R9 SYNTH source events (not estimated hour/4): 27,980 Jan, 33,523 Feb, 31,758 June, 24,324 July = 117,585 exact original entry events across **11,520 complete UTC calendar quarters**, 7,521 R9-active quarters and 2,880 complete UTC hours, including original zero-reference intervals.
- Original R9 SYNTH indexed daily full quote-event source: https://docs.google.com/spreadsheets/d/1VIx7mDN-sHBj2kQ5-JueV4V-sIHnFhPadOYClgLG_I8/edit; historical server->UTC corrections frozen as -2h Jan/Feb and -3h Jun/Jul. Do not silently impose this on other brokers, live timezones or unknown dates.

## 2. What was changed — source-verified mechanism, NOT the existing H1V2 EA

Original H1V2/R11S1 hindsight candidate selector enters only on FIRST observed source quote of each occupied 250ms bin. It requires spread <=$1.50, quote drought reset after >15,000ms and >=300,000ms observed fresh-history warmup, no same-ms post-entry fill. BUY entry at Ask, liquidation at Bid; SELL entry Bid, liquidation Ask. Original strict labeled successful iff first favorable nominal +$0.10 net after $0.02 fee by <=15,000ms AND no -$0.10 opening-liquidation adverse movement anywhere over complete source-covered 30,000ms after entry. Missing quote coverage causes CENSORED, not WIN. The R11S4 saved teacher instead reserves the position for ALL 30,000ms even after the +$0.10 first favorable event.

**R12 (preserved predecessor)**: after strict future-good selection, source quote path is traversed to first quote at which net liquidating position reaches +$0.10 after nominal $0.02. Position is released AFTER that quote. Strict future 30-second observability and no-adverse label stays separate and still required, even though it observes some post-exit quotes. Earliest finishing interval schedule is exact max-cardinality for intervals `[entry, first_future_TP_quote]` with strictly `next_entry_ms>prior_exit_ms`. It is future-privileged, not a real order-fill guarantee.

**R12D**: new AS-OBSERVED candidate reassessment clocks per raw source quote ordinal. Every decision is made only after that quote exists. A quote arriving inside already-occupied 250ms bin can be a DISTINCT source decision candidate, never a last quote chosen by knowing there were no later quotes. Three independently versioned clock variants: first observed 50ms bin; first original 250ms quote plus first subsequent observed spread narrowing by >=$0.02 inside the bin; all distinct-ms observed quotes. They are separately future-labeled and never added as simultaneous positions. The mandatory 15s quote-drought reset, 300s warmup, <=$1.50 spread admission, no same-ms fill, executable BUY/SELL prices and full original 15/30 strict label remain unchanged. The first-250ms population and BOTH original side labels pass exact raw quote ordinal parity on all four months (not just counts). Novel strict-positive quote ordinals and first-TP exit timestamps are independently recomputed from exact full raw source, not interpolated from original first250 events.

**R12D-Q**: a quota-priority local exact future-privileged interval repair on the all distinct-ms source. The global earliest first-TP scheduling greedily maximizes total position count but can sacrifice one target quarter near boundaries. The repair never decreases total count, never breaks single-position chronology, never demotes an already-satisfied quarter, and never changes original S1 first15/full30 strict labels or nominal after-fee +$0.10 profit check. In Feb16 13:00 UTC the strict source has 91 candidate timestamps and local theoretical quota 11. A prior 12:45 quarter surplus crossing trade blocked its first valid entry; removing one surplus trade allows 11 local source quote exact first-TP trades. Previous quarter still exceeds required 9; 13:00 newly meets required 11; month total stays 90,357. Every selected original and modified row rechecked against original raw Bid/Ask at entry/exit ordinal, monotonic time and explicit nonoverlap. Only R12D-Q new CSVs and receipts are written, not prior R12/R11/original H1V2 files.

## 3. All-four-month independently source-replayed and joined data

| Original source month | R11S4 fixed 30s positions | R12 first250 / first TP positions | R12D-Q all observed distinct-ms / first TP positions | R12D-Q active quarters meeting EXACT original SYNTH reference | Independent source-impossible remaining | R12D-Q active HOURS meeting R9 quota |
|:--|--:|--:|--:|--:|--:|--:|
| Jan 2026 | 35,652 | 88,233 | 96,576 | 1,831/1,878 | 47 | 476/480 |
| Feb 2026 | 33,640 | 82,027 | 90,357 | 1,693/1,819 | 126 | 439/458 |
| Jun 2026 | 40,296 | 101,889 | 110,577 | 1,936/1,954 | 18 | 497/497 |
| Jul 2026 | 35,813 | 75,928 | 81,781 | 1,853/1,870 | 17 | 480/482 |
| FOUR MONTHS | **145,401** | **348,077** | **379,291** | **7,313/7,521** | **208** | **1,892/1,917** |

**No exceptions concealed:** June density increased FUTURE-selected positions but did NOT improve June quota coverage over predecessor; 18 June quarter deficits remain. February candidate shortage dominates remaining 126 source-impossible quarters. No change to fixed S1 policy, real execution, stop/trail EA or portfolio risk. All 208 impossible quarter proofs apply ONLY to this exact source, timestamp admission, quote-derived future strict label, one-open-position firstTP interval, and original R9 SYNTH reference. They do not prove impossibility across distinct broker quote feeds or different risk/target contracts. The original complete source matched outputs contain **every single one of the 11,520 intervals and 2,880 hours** and the **entire 208 witness set**, not representative samples.

## 4. Newly tested domain-mismatch hypothesis; no price manipulation

The original R11S4 extreme failures clustered in high-Dukascopy-spread hours. The new independent read of exact R9 SYNTH daily ticklogger quotes for the entire original ten count-starved hours (Jan30; Feb2; Feb5; Feb6) verified original compressed input SHA, original unabridged event-count/clock mapping and source spread from both recorded Bid-Ask and point-based spread fields. All ten R9 SYNTH source-hour median spreads were $0.18–$0.24, with **zero observed logger quote rows above $1.50**, whereas corresponding Dukascopy hour medians were $2.120–$3.157 and 93.2–99.5% of quote rows had spread above $1.50. Every exact original SYNTH entry event count in these ten hours matches the historical reference. This is a **measured source-domain mismatch**, not permission to widen the original spread gate or paste SYNTH quotes into Dukascopy future labels.

A *separate experimental R12B native-source teacher* reads the exact original Strategy Tester SYNTH logger for Feb2 06UTC. Its 28,978 observed distinct-ms eligible quote candidates produce 12,563 future-labelled first15 favorable/full30 no-adverse opportunities and a maximum 2,137 first-TP nonoverlap positions within that hour, versus the original R9 SYNTH 104 entries and Dukascopy only 4 positions under old fixed30. All four original source 15m quota counts 28/27/25/24 are feasible in this synthetic-native hypothetical source. **THIS IS NOT REAL-TICK / LIVE BROKER EXECUTION OR CAUSAL FORECASTING.** No 4-month native SYNTH teacher results have been claimed, and a full source-native test program should be a distinctly versioned next branch/experiment.

## 5. Falsification and negative findings

1. Sparse v5 new candidate density is **not** the single cause of all quarter-hour failures: more candidate quote events did not increase June quota coverage. Do NOT loop once again through arbitrary entry clock subdivisions when all distinct millisecond as-of source decisions are already exhausted.
2. Source-independent identical 30sec reservation is an overly restrictive *holding duration* model compared with an actually exited first-TP position; however, the improved future oracle cannot be described as satisfying the original S4 exact fixed30 contract or a real broker TP fill.
3. The 30sec no-adverse-survival criterion intentionally observes after an early hypothetical TP exit; this is a stricter research label than actual realized P&L lifecycle. Never drop that strict requirement under the original `R11S1` label name to raise quotas.
4. The source native R9 SYNTH test logger differs from Dukascopy both by spread and by synthetic tick sequence and may exhibit Strategy Tester path effects. Do NOT train on native SYNTH hindsight and claim live Coinexx accuracy.
5. The R11S2 36 full-month student policies failed joint source volume + >=80% strict accuracy. The oracle's 100% future-picked success cannot become a predictor feature or a measured causal edge. No new R12 student has been fitted here.
6. The source R9 parser initially hit a real 31-column-versus-30 expected schema failure; the old R12 prior generator rebuilt correct source and independently matched all 2,880 original R9 hours. The new crossfeed diagnostic initially hit a float-formatted `raw_quotes=46067.0` source CSV conversion issue and repaired only its own parser. R12B initial header mismatch `utc_entry_ms` vs `entry_utc_ms` likewise corrected in new code only; never hide unsuccessful attempts.

## 6. Recovery and exact full re-execution

**Required runtimes:** Python 3.11+, numpy, pandas, numba, pytest, and exact archived original full raw quote gzip source files and R11S1 full label ZIPs downloaded from original source links. `r12_tp_oracle.py` belongs to original immutable R12 branch, NOT duplicated/replaced by this new branch. Restore it to `/mnt/data/h1v2_r12/source/r12_tp_oracle.py`. Original R11S1 `entry_survivability.py` and R11 `entry_contract.py` must be exact bytes to `/mnt/data/h1v2_r12/upstream/` with SHA `c52de41072911ad53dedadfb3dba1899ea112e41a9e58e48ea29a7903e3ec475` and `b720a609eb13bc025a706b8fe1601e4fa8d1df9fa9908eb808222f5ac96d34cb` respectively (source copies included in this recovery kit). The unmodified R11S1 labels full original ZIPs and Dukascopy GZs are top-level `/mnt/data` exactly as the source-generated scripts require. `r12_dense_requote.py` checks dependency SHA and aborts on mismatch. R12Q original complete R9 15-minute per-month benchmark and original R12 quote traces must be in `/mnt/data/h1v2_r12/results` (included as original external link refs in manifest; never generate reference estimates).

Run four isolated source epochs, preserving all output and logging each command independently:

```
PYTHONPATH=/mnt/data/h1v2_r12/source:/mnt/data/h1v2_r12/upstream python /mnt/data/h1v2_r12/source/r12_dense_requote.py --month 01
PYTHONPATH=/mnt/data/h1v2_r12/source:/mnt/data/h1v2_r12/upstream python /mnt/data/h1v2_r12/source/r12_dense_requote.py --month 02
PYTHONPATH=/mnt/data/h1v2_r12/source:/mnt/data/h1v2_r12/upstream python /mnt/data/h1v2_r12/source/r12_dense_requote.py --month 06
PYTHONPATH=/mnt/data/h1v2_r12/source:/mnt/data/h1v2_r12/upstream python /mnt/data/h1v2_r12/source/r12_dense_requote.py --month 07
PYTHONPATH=/mnt/data/h1v2_r12/source:/mnt/data/h1v2_r12/upstream python /mnt/data/h1v2_r12/source/r12d_quota_priority.py --month 01
PYTHONPATH=/mnt/data/h1v2_r12/source:/mnt/data/h1v2_r12/upstream python /mnt/data/h1v2_r12/source/r12d_quota_priority.py --month 02
PYTHONPATH=/mnt/data/h1v2_r12/source:/mnt/data/h1v2_r12/upstream python /mnt/data/h1v2_r12/source/r12d_quota_priority.py --month 06
PYTHONPATH=/mnt/data/h1v2_r12/source:/mnt/data/h1v2_r12/upstream python /mnt/data/h1v2_r12/source/r12d_quota_priority.py --month 07
python /mnt/data/h1v2_r12/source/assemble_r12dq_full_fourmonths.py
PYTHONPATH=/mnt/data/h1v2_r12/source:/mnt/data/h1v2_r12/upstream pytest -q /mnt/data/h1v2_r12/tests/test_r12_tp_oracle.py /mnt/data/h1v2_r12/tests/test_r12d_asof_and_priority.py
```

All created source data must be byte-hashed and compared against the **specific member SHA manifest**; never treat quoted month counts in this README as replacement of the full program output. Recovery scripts are allowed to read original files but never modify original H1V2 / R11 / R12 results or `MQL5` production EA. The R12D source uses a fixed researcher `/mnt/data` path; use this documented workspace layout rather than rewriting paths and accidentally changing source/feature version without rerunning all tests. All bundle members have exact SHA in `SOURCE_EXACT_RECOVERY_MEMBER_MANIFEST.json`.

**Restarts:** read this README, then FULL 85K original audit, FULL 249K R11 ledger, FULL append-only R12 ledger including latest numbered entry, verify original parent/active branch HEAD and member SHA, restore original quote archives and labels, rerun only the incomplete experiment. Never repeat completed negatives or promote frozen future-optimal performance as live alpha.

## 7. Additional research hypotheses — no fabricated successes

**R12-N1: Source-native dual-teacher transfer.** Train two separate hindsight action labels from original R9 SYNTH source and Dukascopy source; each requires its own spread gate, raw quote id, no synthetic midprice interpolation and exact original R9 clock. Compare per-UTC-quarter feasible upper envelopes, then **only** assess a past-only action model on real tick data with 1-pos order execution. This is the strongest investigation priority following the observed hour-by-hour crossfeed mismatch. It has a completed one-hour probe only, NOT four-month source-native teacher results.

**R12-N2: Endogenous slot shadow pricing.** On each observed quote, estimate as-of expected conditional firstTP elapsed time distribution, adverse competing hazard, and the value of preserving a free slot through the next quote. Use an occupancy constrained dynamic treatment regime with 15-minute quota target as EVALUATION only, never as forcing unqualified trades. Train on strictly earlier days; future-selected greedy membership must not be inference feature.

**R12-N3: As-of multiscale confidence expansion.** Evaluate rolling original 250ms, 50ms, 1s, 5s, 15s, 30s, 60s and full 300s real-time observed quote/event sequence as a causal event graph with spread compression, signed Bid/Ask asynchronous microstructure, quote-age volatility and true elapsed-time timestamp. Mandatory future-mutation invariant and chronology-purged cross-feed controls. Repeating R7 static bins or R10 48-quote-only representation already failed; keep negative controls.

**R12-N4: Risk-bearing trade exits and strict diagnostic coexistence.** In a completely separate version, distinguish full30 post-entry quote-survival diagnostic from whether a CLOSED position could lose after exit; test explicit TP/SL/trailing stop with executable prices, gap, slippage, exit price priority and liability. The original full30 label and >=80% strict day/week/month must remain directly reported (not silently redefined). A classically positive realized trade does not satisfy strict full30 by implication.

**R12-N5: Stochastic broker-domain robustness.** Source event timestamp / spread differences between synthetic broker tester and Dukascopy real quote feed are severe in short acute hours; penalize policies sensitive to those domains, enforce max-trade slippage/margin and dealer fill constraints, and require genuine real broker tick replay. A backfilled economic calendar or future actual release time must not enter as-of features; R11S5 MT5 news unknown until historically verified.

**R12-N6: Feasible only if source quotes exist.** The original 208 infeasible R12D-Q quarter certificates prove no optimizer can solve those quarters using only individually strict full30 source-good events with as-of observed distinct-millisecond quote admission and firstTP one-open-position intervals. Further improvements must change source domain or an explicitly versioned risk/price/exit assumption. No pretending the certified bound has been surpassed without changing a documented assumption and recreating all source outputs.

## 8. Hard nonpromotion and QA

Every source event has immutable raw gzip/input file SHA and entry quote ordinal. New candidate decisions use only observed current/past quotes. Future S1 labels and optimal TP timestamps are CALCULATED OFFLINE and used to choose entries with future knowledge; NO learned predictor or real order execution exists. Full outcome evaluation requires per-position spread/fee/slippage, fill delay, stops/trail and capital path, full 120 active calendar days and ISO week, empirical >=80% strict correctness and >=85% original R9 SYNTH monthly count, positive economic value on frozen out-of-sample and on-policy Coinexx real tick data. No such qualification has been established. NO production MQL5 changes or auto-trading are permitted from this result.
