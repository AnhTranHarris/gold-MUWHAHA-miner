# H1V2 / XAUUSD R13 — Broker-conditional source-exact entry geometry

Date: 2026-11-03 America/Chicago. Status: **RESEARCH ONLY / NEW SOURCE / 12 UNIT + REGRESSION TESTS PASSED / HISTORIC SOURCE UNMODIFIED / PERFORMANCE NOT APPROVED**.

This is a new, additive development continuation of the **complete original source-exact H1V2 audit**, R11S1–R11S5, R12, R12D-Q, R12BN and R12C. It is not a new EA and makes no changes to historic EA source or committed R9 v2. All prior negative studies remain immutable and must not be repeated as though they never happened.

## Source / branch / rollback

Original repaired R9 v2 (unchanged): `ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0`.
Original teacher (unchanged): `edce573d9c53b743dc5de1b0d741c81370af52c1`.
Original R11S4 (unchanged): `897ae6217874296fbc065089e5e138a0ec0bb43b`.
Original R12D-Q (unchanged): `c46d6bd30ec5a4a2ca120dcd46246114eadbed98`.
New isolated R13 branch created FROM source-exact current R12C HEAD: `83c63e5c56f36729c8da1c461a344f79c321ef25`. All source code is beneath `research/h1v2_r13_broker_adaptive_20261103`; no old paths modified. Branch publication must be separately verified; do not infer publication merely from this README.

Canonical original forensic audit (unabridged 85,961-character source): https://docs.google.com/document/d/1n8Zd37SH3k2mNYpCERHsGSeR5GL-vDNLDv780Bv5-Do/edit
Canonical R11 source ledger (251,650 characters): https://docs.google.com/document/d/1eGC-vxRDzu7FxQOY-3PPUfWzoVRrOZU5jaDozuuv0xI/edit
Current R12C/R13 append-only Drive progress ledger: https://docs.google.com/document/d/1iVv1tAmJlBWhNfXMcw2N50VEVIFrawMObGOzyfUGWmI/edit
R12 original raw append-only ledger: https://docs.google.com/document/d/1v0X5Vkif81qV784Ja6FVe5DfyQLx7RoEw-yjC4m7D1Y/edit

## The actual source domain and exact input quotes

- `R9_REAL_2026-02-02_ticks.csv.gz`, SHA256 `24e4b31935ead7b0eb039fe84dc8972c59500b362cac21721739f1b0c050b3d7`, MT5 **real-tick Strategy Tester mode** (not demonstrated live Coinexx execution). Full raw input separately archived and retained, not duplicated inside compact R13 code/trace ZIP.
- `R9_SYNTH_2026-02-02_ticks.csv.gz`, SHA256 `dcedb28f7453c80d2dec5ffe5d386dad1661134ba61765337155fbbaeb6213a2`, MT5 **synthetic Strategy Tester ticks** (not real broker ticks).
- `XAUUSD_DUKAS_2026_02_ticks.csv.gz`, SHA256 `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`, all **7,538,339** original Dukascopy February quotes, including independent actual archived Bid/Ask vendor quotation (not actual Coinexx fill data).
- Historical R9 terminal-source-to-UTC offset **-2 hours in February 2026**; Dukascopy timestamps already UTC. One focal source hour is **2026-02-02 06:00–07:00 UTC**, halo 05:54:00–07:00:45 ensures 300-second history and complete 30-second future label coverage. Neither source series is synthesized from the other.
- Original reference has 104 R9 SYNTH entry timestamps in 06 UTC and four exact 15-minute references **28, 27, 25, 24**.
- Original R11S1 full 15/30 horizon source algorithm, unchanged with SHA256 `c52de41072911ad53dedadfb3dba1899ea112e41a9e58e48ea29a7903e3ec475`.

## Price and timing invariants

Raw integer price unit **0.001 USD per quoted ounce**; this is NOT a USD cash P&L at 0.01 lots. BUY entry Ask, exit Bid; SELL entry Bid, exit Ask. Positive net favorable >=$0.10 **after the original synthetic research $.02 price-unit fee**. Hence a BUY entering at Ask must see future Bid >= entry Ask +0.12; SELL at Bid must see future Ask <= entry Bid -0.12. There is no magical spread netting. All first-favorable crossings occur at an actually observed quote **strictly later than entry millisecond**; no interpolation or hindsight-bin closing quote. No -$0.10 adverse movement from the opening **liquidation quote** is permitted at any observed quote across the full30s target (regardless of whether an earlier TP exit occurred), with complete 30s gap/source coverage; 15-second quote gap yields censor, not win.

The R11S1 original first-favorable<=15s + full30 safety stays a separate immutable control. New 5s and 30s first-favorable horizons are new **COUNTERFACTUAL LABELS**, and 30s favorable is NOT the original 15s correctness. Actual position occupancy in R13 is first source-quote TP after entry; a selected winner's first target is **already future known**. Earliest-finish greedy yields exact cardinality for a set of arbitrary fixed future-known intervals. It does not solve all portfolio quota optimization, liquidity, fill or capital questions. One-position occupancy strictly enforces next entry after previous observed exit quote.

## The 5 new broker geometry candidate lanes (complete event-level membership saved)

**BASE_250_1500** — first observed 250ms quote, source Bid/Ask spread <=$1.50, 15s drought reset, 300s fresh-history warmup; source-exact R12C control. **DENSE_1500** — all distinct observed milliseconds under same original $1.50 cap, no invention of a last quote in a time bin. **WIDE_REQUOTE_4000** — first observed 250ms or FIRST later truly observed within-bin price quote that narrows spread from bin first by >=$.02, source spread <=$4.00. This changes original risk gate and is **UNAPPROVED FOR RUNTIME**; actual spread is fully paid in favorability equation and remaining source is not treated as broker-fillable. **BROKER_CONTRACTION** — the same quote clock and $4 ceiling, source current spread <=80% of 300s **past-only** time-weighted spread EMA and 15s EMA no greater than 300s EMA. **DIRECTIONAL_MICROPATH** — same quote clock and $4 ceiling, both observed Bid and Ask 3s displacements agree in sign and each displacement magnitude exceeds CURRENT observed spread +$.12; it does NOT predict correct future direction and has no BUY-vs-SELL decision without future truth.

Candidate/feature prefix state is causal. Label outcome and which side to enter remain hindsight-privileged and cannot be used as features by a production EA. All 3 sources separately test original 5s, 15s and 30s favorable horizons while preserving full30 safety. There are **45 complete source x lane x horizon results** and **180 complete source x lane x horizon x quarter results**, no omitted 0-quota or losing quarter in this focal hour.

## Independent delayed market-entry counterfactual

Original FUTURE-selected winning entry and side are FROZEN. Simulated order submitted at latency 0, 100 or 500ms, then filled only at FIRST **actually observed** quote at or after target latency (reject if no fresh quote <=1000ms or if fill spread fails the corresponding original $1.50 / experimental $4.00 gate); nominal extra slippage 0/.02/.05 USD on EACH entry and exit, representing 0/.04/.10 round trip. A successful modeled trade exits on FIRST subsequently observed liquidation-side executable >=$.10 net and is marked strict GOOD only if no first30 opening-liq adverse from ACTUAL delayed fill for the complete full30 horizon. Failed/censored fills occupy the full 30 seconds; a quote reject never counts as a trade; one position at a time; no re-picking favorable timestamps after the delay. **Failed/neutral trade economic exits are not modeled, so no account P&L or real win rate is claimed.** Every one of **135** complete experimental stress scenarios has a full source-signal / delayed fill / firstTP-exit / outcome-code NPZ, and all **540** 15-minute source+lane+latency+slippage quarter rows are separately available and bucketed by ACTUAL fill time rather than signal time.

All exact original baseline FIRST250 horizon15 future-privileged signals reproduced: REAL tester **705**, SYNTH tester **1,853**, Dukascopy **6**. All 100ms/0-slippage baseline delayed source results independently equal the prior R12C: REAL **135 GOOD/73 FAIL**, SYNTH **1,128 GOOD/28 FAIL**, Dukascopy **1 GOOD/1 FAIL**. This is a frozen negative/positive contrast, not broker model cross-validation.

NEW SOURCE DISCOVERY at 100ms with widened $4 diagnostic: Dukascopy source **124 strict good /54 completed failure =69.6629%**; REAL tester **152 good /75 failure=66.9604%**; SYNTH tester retains 1,128 good/28 failure=97.5779%. Dukascopy full hour future-known source quote schedule under $4 diagnostic firstTP has **347 positions** (vs original6), but true 100ms modeled signal replay has only124 good/54 failure, 13 quote rejects and156 busy skips. All 4 Dukascopy 15-minute subperiods achieve their R9 SYNTH good count references at the 100ms wider gate, but **NONE achieves >=80% strict accuracy**: quarter (GOOD,FAIL): 06:00(30,14), 06:15(29,15), 06:30(37,12), 06:45(28,13). Even the entire hour fails joint accuracy/volume objective. At 500ms latency source performance deteriorates materially. No broadened execution gate was promoted.

## Second creative mechanism: broker-conditional **as-of horizon** choice

This was added **after reviewing the focal-hour grid** and is a research-exposed exploratory variant, NOT prospective pre-registered OOS. The chosen quote-horizon is **5s** when BOTH past 3s Bid and Ask movement magnitude >=2*(current spread+.12); otherwise **30s** when spread >=$1.50 and <=90% of previously observed 300s spread EMA, else **15s**. Future side, individual favorable outcome and optimal entry scheduling are still future privileged. Full30 -$0.10 safety unchanged, and independent original 15s strict label is reported even on selected 30s-horizon positions. Entire candidate-level past horizon decisions and full future outcomes are retained source ordinal by source ordinal. Three quote-source individually produced full selected trace CSV and 4 quarter rows, with 27 independent delay/friction scenarios and 108 quarter records, each supported by an exact full-ordinal NPZ.

Original strict15 among this selected dynamic-horizon future-known teacher is REAL 764/764, SYNTH 1,836/1,836, DUKAS 346/346; this is TAUTOLOGICAL future selection, not foresight. At 100ms/0 extra slippage: REAL 152 GOOD/76 failure **66.67%**, SYNTH 1,150 GOOD/27 failure **97.71%**, DUKAS 124 GOOD/54 failure **69.66%**. REAL and DUKAS fail 80%. This variant does not solve the real predictive action problem. A truly causal as-of side/WAIT hazard must be trained separately and tested on new unexposed chronology.

## Reproduce / scientific status

Run Python3 with numpy,pandas,numba,pytest and the unchanged four-source helper copies and three canonical original gzip paths mounted at /mnt/data. Run in order:

```
python src/r13_crossbroker_horizon_lanes.py
python src/r13_delayed_executable_stress.py
python src/r13_asof_dynamic_horizon_router.py
python src/r13_dynamic_delayed_stress.py
PYTHONPATH=src pytest -q tests
python -m compileall -q src tests
python verify_r13_full_artifacts.py
```

Audit full original R11S1 quote coverage and source quote ordinal. Check raw input gzip SHA and original R11S1 helper SHA **before** running. The new R13 results are an EXPOSED research hour, under nominal fee and modeled latency; not a blind OOS, not an actual Coinexx broker-fill record, not a Dukascopy fill record, no independent real-broker calibration, no MT5 MetaEditor compilation or live/paper/demo permission. A native Coinexx source quote is not a historical Coinexx fill; SYNTH strategy tester optimism explicitly observed.

Acceptance has NOT changed: >=85% original R9 SYNTH volume each month; >=80% strict correct per active day/week/month, and hourly/quarter as investigational goals; positive full-account on-policy net AFTER actual symbol tick value/commission/latency/slippage and controlled drawdown, both brokers independently. WAIT on unknown broker session/unknown model support; quotas are reporting and scientific objectives only, never an instruction to take negative expectancy trades.

## Comprehensive artifact inventory without truncation

`results/R13_ALL_45_SOURCE_LANE_HORIZON_RESULTS.csv` — every of 45 hourly lane/horizon outcome and source quote SHA.

`results/R13_ALL_180_SOURCE_QUARTER_LANE_HORIZON_RESULTS.csv` — every of 180 15-minute source/bucket baseline and alternative, including candidate counts, selected counts, independent crossing upper, exact reference and unqualified flag.

`results/R13_ALL_135_NEW_LANE_LATENCY_SLIPPAGE_SCENARIOS.csv` — 135 frozen source winner signal stress including good/fail/censor/reject/busy, completed accuracy, 104 reference and joint requirement.

`results/R13_ALL_540_QUARTER_DELAY_FRICTION_SCENARIOS.csv` — complete 540 15-minute fill-UTC-bucket stress variants with original reference and joint correctness+count outcomes.

`results/R13_ALL_27_ASOF_DYNAMIC_HORIZON_DELAY_SCENARIOS.csv` and `results/R13_ALL_108_ASOF_DYNAMIC_HORIZON_DELAY_QUARTERS.csv` — all 27 adaptive horizon source stress and 108 quarter outcomes.

`results/R13_{SOURCE}_ALL_ASOF_CANDIDATES_AND_SEPARATE_HORIZON_LABELS.npz` — every original source candidate quote ordinal, observed raw Bid/Ask, 3s motion/15s and300s spreads, lane bit membership, all six (BUY/SELL*5/15/30) separate future labels.

`results/R13_{SOURCE}_ALL_FUTURE_SELECTED_TRADE_SOURCE_ORDINALS.csv` — **ALL** exact 45 universe selected trade entry/exits, source raw ordinal, raw Bid/Ask, date/time, selected side, amount after fee, observed state, one-position result and horizon, without sample omissions.

`results/R13_{SOURCE}_{LANE}_lag{0|100|500}_slip{0|20|50}_ALL_FROZEN_SIGNALS_FULL_QUOTE_ORDINAL_OUTCOMES.npz` — all original source selected signals, each delayed fill, first TP exit, outcome code and nominal good price net, 135 individual immutable row-full traces.

`results/R13_{SOURCE}_ADAPTIVE_ASOF_HORIZON_V1_ALL_TRADE_ORDINALS.csv` and `...ALL_FOUR_QUARTERS.csv`, plus full source `...ALL_PAST_DECISION_HORIZONS_AND_FUTURE_LABELS.npz` — no truncation of dynamic source status/entry/exit.

`results/R13_{SOURCE}_DYNAMIC_HORIZON_STRESS_lag{0|100|500}_slip{0|20|50}_ALL_ORDINALS.npz` — every one of 27 individual dynamic-horizon scenario source quote-ordinal outcomes.

`src/*.py`, `tests/*.py`, `logs/*.stdout`, `logs/*.stderr`, `logs/*.log`, source hash receipt and full unabridged rendered CSV-derived report are retained under the zipped research package. SHA-256 member-by-member `R13_ALL_MEMBER_SHA256_MANIFEST.json`, `R13_SOURCE_EXACT_RECOVERY_PACKAGE_20261103.zip` and archive byte SHA are required before recovery.

## Next experimental falsifiers, not claims of working technology

1. Separate TRUE BROKER spread transport into raw spread / expected BID-ASK liquidation hazard / slippage tail / quote-age rejects, with a causal previous-event counterfactual at each observed quote. No claims of historical fill equality.
2. Source-conditional cause-specific competing risks: BUY/SELL/WAIT, time-to-TP vs time-to-first-adverse vs stale quote vs server reject, with explicit right censor; hierarchical Bayes prior shift across quote feeds and full uncertainty. Independent side calibration must precede routing.
3. Conditional dynamic **opportunity plateau** after latency (length and stability of as-of quote states) predicted prospectively, not omniscient trade jitter; penalize one-tick windows.
4. Spread compression / expansion signed event graph over real observed 50ms,250ms,1s,3s,15s,30s,60s,300s with 15m/1h/4h regime; true Bid/Ask quote-side leadership, not level-2 order book claims.
5. Differential execution contract: source-conditional session permission, actual Coinexx model spread, tick-size and symbol point, fill-reject and actual per-lot dollar PnL. Incompatible broker domain -> WAIT, not forced opportunity.
6. Time-censored latent regime/innovation detector with selective conformal confidence by independent nonoverlapping daily episodes, not millions of correlated adjacent 250ms labels as independent confidence.
7. Sequential stochastic occupancy / value-of-WAIT with endogenous future opportunity arrival intensity and risk-conditioned fixed 30s surveillance; source quote-ordinal replay without future trade admission.
8. Minimum 15-minute/hourly throughput considered as after-the-fact evaluation. Never use remaining target count as negative-risk admission gate.
9. Next full 4-month original DUKAS native experiment and independent MT5 REAL tester full 4-month data remain separate NOT DONE hypotheses. The 88-day source SYNTH archive is available as separate R12BN source; never conflate with certified Coinexx live broker execution.

## Recovery checkpoint after chat max-length / timeout

(1) Read complete R12C/R13 append-only Drive progress ledger, then the original full H1V2 audit (85K source), original R11 append-only ledger (251K), full R12 and R12DQ complete research, immutable branches. (2) Verify new archive SHA/member SHA/source SHA, and verify Github R13 branch head and compare to 83c63e5... parent (all new paths ADDED). (3) Re-run all 12 local tests and exact complete trace verifier. (4) Continue only unfinished falsifiable higher-priority stage, never repeat old negative grids or silently overwrite original data. No source-deployable authorization exists.
