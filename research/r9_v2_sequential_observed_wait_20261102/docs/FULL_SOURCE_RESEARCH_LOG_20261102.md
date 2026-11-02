# R9 v2 — Source-Exact Sequential Quote-Response Next Research Stage

**Date:** 2026-11-02 UTC (2026-11-01 America/Chicago owner session). **Classification:** additive research source; NOT approved, not MT5 compiled, no live trades. **No source deletion / model overwrite.**

## 1. ORIGINAL COMPLETE SOURCES — MANDATORY SOURCE READ, NEVER REPLACE WITH THIS NAVIGATION DOCUMENT

The exact unabridged previous research is preserved in its own native documents, immutable GitHub branch source, and source-byte archives. This document is an additive log, **not** a substitute for any executable source, 250ms label NPZ, model weight, experiment ledger, or prior research log.

- Full original v2 design and complete 12-layer specification: https://docs.google.com/document/d/1vJPgj_nWadWVALQC0UWB68evqSkKuKwz7KIF_LhXqkA/edit
- Original complete 8-source baseline: https://docs.google.com/document/d/1YZZ8imbGfYUXdtKICasFFw3QPxpcUB2QLiBQANuR44Q/edit
- Previous eight-source causal teacher and student development: https://docs.google.com/document/d/10W8PTGCXAi1wRPoIP44_1OwEozH97h0ouL2ejsXxrv8/edit
- Previous ordered first-event student training: https://docs.google.com/document/d/1moZNDhkf-oBjYBzh6dEHQiGMbq-FAh52jke7TcmJmoM/edit
- Exact same-tick paired BUY/SELL research log: https://docs.google.com/document/d/1qeI5ZTk5La3lj1Ncf_6dhDHTFDqLUi1LnilH3oV0Tr0/edit
- Full latest 250ms all-event NOW/DELAY and WAIT student log: https://docs.google.com/document/d/1yurW_yYdCnPQdhxqexL9TgUqyFkj4muMUPuUmUriufw/edit
- Original R9 v2 Python frozen model source: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/carson/r9-probabilistic-entry-router-v2-20261101/research/r9_probabilistic_entry_router_v2
- Full previous source exact 250ms action/WAIT student: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/carson/r9-v2-250ms-action-timing-wait-student-20261102/research/r9_v2_250ms_action_timing_20261102
- Full previous stable, unapproved high throughput runner: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/carson/r9-v2-high-volume-event-stream-repair-20261101/research/r9_v2_high_volume_event_stream_repair_20261101
- Previous original full source ZIP: https://drive.google.com/file/d/1A7F-l0NhdgtYYlmhLABGP1zt-0pyf-_4/view

## 2. EXACT LATEST RESEARCH RECOVERED — DO NOT DUPLICATE

The previous all-event 250ms action-timing research completed all 8 source/month datasets, not sampled: Coinexx Jan/Feb/Jun/Jul and Dukascopy Jan/Feb/Jun/Jul. It processed 64,515,445 real chronological source ticks, 26,578,537 eligible decision events and 212,628,296 full teacher-only NOW/+250ms/+1s/+3s BUY/SELL action labels. Each of the 8 three-outcome NOW students FAILED the >=80% calibration. The distinct SAME-SIDE WAIT-rescue Bayesian student achieved held-out AUC Coinexx 0.7316/0.7529/0.7595/0.7644 and Dukascopy 0.7082/0.7260/0.7326/0.7214, but precision was only roughly 18-32% and NO model was approved. Earlier 8-source fixed-baseline veto, ordered first-passage veto, and paired opposite-side veto LightGBM studies were also complete and rejected. Their raw research artifacts, rejected model weights, original source and hashes remain immutable. **Do not rerun any identical negative family.**

The past eight source/months are 4 distinct calendar months on each of 2 independent feeds (NOT eight different calendar months). March, April, May, August and September remain outside this training family. Previously created complete binary 250ms label archives are indexed by `FULL_EIGHT_RECOVERY_INDEX.json` on the source GitHub branch and the source log, not replaced by summaries.

## 3. OWNER ACCEPTANCE CONTRACT

Every *selected completed nonoverlapping trade* must be labeled independently:
- CORRECT: executable liquidation-side net >= +0.10 favorable barrier first, then positive R9-style stop/trail/timeout net and actual close by +30 seconds;
- INCORRECT: the first adverse threshold occurs, or a witnessed later barrier path closes nonpositive;
- NEUTRAL: no relevant first barrier within the available horizon, missing/ambiguous/censored case; never merge this into incorrect, never count it as correct.

For each source and calendar month Jan/Feb/Jun/Jul require >=85% of R9 SYNTH monthly 27,980/33,523/31,801/24,382 completed trades; floors 23,783/28,495/27,031/20,725 per source. Independently require >=80% strict first-15-second success and >=80% strict first-30-second success on every active calendar DAY, every week and the complete month; no zero-trade pass. All net returns after realistic cost stress must be positive; drawdown and margin controls cannot be waived. Monthly counts of the original teacher are reference, not Dukascopy synthetic trades.

**Scientific honesty:** Hindsight is allowed ONLY when assigning offline teacher labels to already timestamped decisions. It must NEVER enter current features, delay choice, order entry, pricing, or recalibration against the heldout period. Real quote-side bid/ask and original source event ordering are required. Do not use retrospectively sorted winners to meet 85% volume.

## 4. NEW DISTINCT ADDITIVE HYPOTHESIS BUILT — REAL WAIT THEN ACT

A true *online two-stage sequential quote-response* specialist has now been coded in `src/sequential_entry.py`. It reuses the ORIGINAL high-volume `FastClock`, complete bid/ask event Hawkes-style bank, rolling 5m windows, original 15m/1h/4h features, and original R9 `TickExactActivePath`; it does not substitute another basic new tick engine or erase the previous source. On an observed eligible completed 250ms quote slot, a candidate is marked PENDING using only `specialist_evidence` as of t. No order is submitted yet. Subsequent quote updates at t+>=250ms <=3s are ACTUALLY OBSERVED; if both executable bid and ask have moved at least 0.02 with the proposed direction and spread does not expand beyond its prior causal limit, a position is entered NOW at this new actual quote. If two-sided adverse quote motion is observed, the pending idea is rejected. A 3s expiry cancels it; none of these uses hindsight-best-delay/side labels. After closing, separate correct/incorrect/neutral and first-15s/30s counters update.

The additive `OnlineThreeClass` is a strictly prequential categorical Bayesian learner using 7 features from *observed* confirmation (bid-response, ask-response, two-sided echo, spread delta, midpoint confirmation, elapsed wait bins, current spread). Its histograms update ONLY after a trade has actually closed. Its posterior is a shadow-only, uncalibrated forecast; it does not permit or veto orders and makes NO 80% guarantee. No SYNTH teacher at runtime. The next research step is to verify conditioning, chronological reliability and NP calibration on disjoint training periods, then gate future online decisions in a second independently frozen policy. A shadow-only model is not a trained deployable student.

## 5. FIRST MECHANISM/CAUSAL INTEGRATION PROBES, NOT FULL-MONTH TRAINING

- Coinexx January first 250,000 raw quotes: 6,877 nonoverlapping closed positions; 1,896 CORRECT within 15s; 1,958 strict CORRECT within 30s; INCORRECT 4,500; NEUTRAL 419; modeled net -$1,319.78. Uncalibrated past-only shadow model produces 6,677 as-of predictions after 200 observed completed positions; score >=.30 selects 962 retrospective *score-threshold diagnostic* cases with 30.04% CORRECT, never 80%.
- Dukascopy January first 250,000 raw quotes: 3,967 nonoverlapping closed positions; 377 CORRECT within 15s; 433 strict CORRECT within 30s; INCORRECT 2,913; NEUTRAL 621; modeled net -$3,265.612. After warmup, shadow p(correct) median ~0.088, far from calibration.
- This is only a **500,000 raw tick integration sample** after prior FULL eight source-month training had completed; it is NOT another full-month backtest, NOT new 8-source optimization, and cannot be used as monthly-volume evidence.
- Unit tests: 5 pass, covering WAIT actual observation, distinct three classes, teacher omission, prequential update/normalization, zero day is not passing and monthly floor/day failure isolation. Original v2 and complete previous eight source-month source are unchanged.

## 6. DOCUMENTED GAPS; NO APPROVAL OR FAKE SUCCESS

No new full eight-source on-policy sequential run was completed within this continuation. The first new sequential learner is trained only prequentially on its observed integration-prefix closed positions, not fitted on all eight source months. Its current forward probability rankings are uncalibrated and its behavior has negative sample P&L. It is NOT entitled to a trained-v2 model, profit or 80% success claim. No MT5 compile or order execution was requested or performed. Prior eight source-month fitted models are scientifically rejected and preserved rather than silently repeated.

## 7. NEXT SCIENTIFIC WORK FROM THIS EXACT CHECKPOINT

Restore the complete new source as packaged and verify all hashes, then connect a higher-capacity *state-conditioned* BUY/SELL/WAIT Bayesian + Hawkes + NP model to the genuine post-WAIT observed quote features. Train only on earlier source dates/months, reserve separate calibration and chronologically later check dates, and execute complete on-policy single-position eight-source/month runs in independently checkpointed chunks. Record all source-day and source-week denominators including no-trade intervals; no volume cap or sampled substitute; compare against original v2 throughput and SYNTH floor. Test independent slippage and stop-level stresses and equity constraints before any strategy promotion. Do not try to 'pass' 80% by excluding trading days. Retain original 250ms teacher label NPZ weights (no re-labeling of prior experiments).

**This log is a literal, additive research continuation and provenance index. The FULL original source code, datasets, and failed model evidence remain the working source of truth.**
