# BETA 024 — R9 REAL/SYNTH/OVERFIT ↔ independent Dukascopy event-clock audit

**Date:** 2026-09-29  
**Lineage:** independent `beta`. Retired branches referenced for source archaeology only; no code or strategy inheritance.  
**Status:** COMPLETED 165,630-event source-paired diagnostic. NOT full 236,647 REAL / 219,342 SYNTH event-population parity, profitable backtest, funded BETA015 replay, or approved MQL5 candidate. **August SEALED**.

## Why this audit exists

Previous independent Dukascopy tick-Python research and Coinexx↔Dukascopy clock calibration existed before BETA. BETA018–023 omitted their source-specific event bridge and incorrectly described all cross-feed teacher alignment as unverified. That was a continuity mistake, NOT a reason to invalidate the Dukascopy independent market-data research environment or replace it with Coinexx-only training.

Original source roles remain different: Dukascopy ORIGINAL ordered Bid/Ask ticks = independent causal execution-research feed; Coinexx R9 REAL original Strategy Tester + ticklogger = actual historical broker comparison; Coinexx R9 SYNTH = generated-tick aspirational teacher; R9 OVERFIT = quarantined retrospective labels/scores, NEVER allowed as live signals or same-month promotion evidence.

## What was independently reconstructed

Recovered the seven original R9 REAL↔SYNTH paired source datasets (165,630 same-minute/same-side/ordinal selected pairs, NOT identical matched fills), all seven paired OVERFIT teacher-score files, complete Jan-02 original REAL and SYNTH raw logger daily streams, and all original Dukascopy January–July tick files. Recomputed Coinexx server-clock offset for 149 dates by minimizing same-side executable entry-price difference to as-of Dukascopy quotes. Jan–Feb shift = -2h, Mar 2–6 = -2h, Mar 9 onward = -3h, Apr–Jul = -3h. Monthly median absolute price residual for R9 REAL historical entry: Jan $0.245; Feb $0.335; Mar $0.285; Apr $0.245; May $0.195; Jun $0.195; Jul $0.225. These ARE NOT exact-quote identities.

Original Jan-02 independent full-tick log control: REAL 341,569 quote rows and 1,525 ENTRY markers; SYNTH 330,217 quote rows and 1,083 ENTRY markers. At a <=5s as-of Dukascopy quote age with -2h clock correction, REAL 1,521/1,525 and SYNTH 1,079/1,083 were quote-alignable; REAL price residual median $0.295, SYNTH $0.435.

Historical original R9 source pairs were crosswalked to Dukascopy's existing BETA023 **first R9-style causal entry signal per minute** using order-preserving one-to-one temporal matching (directions scored only AFTER timing matches) at +/-1s, 5s, 15s, and 30s. At +/-5s, monthly Dukascopy parent-event coverage against *paired historical source subsets* was:
- REAL Jan 46.97%, Feb 53.54%, Mar 62.35%, Apr 51.91%, May 46.19%, Jun 51.79%, Jul 40.44%; aligned-event side agreement ~99%.
- SYNTH Jan 21.00%, Feb 25.10%, Mar 27.53%, Apr 22.94%, May 20.40%, Jun 22.07%, Jul 17.95%; aligned-event side agreement ~80.8%–86.4%.

This supports the **direction of source-faithfulness** for the independently rebuilt R9-like control, but does NOT certify R9 full EA/event identity: BETA023 allows $1.20 Dukascopy spread, is first-cycle only and does NOT replicate the original Coinexx 25-point spread gate, fill/rearm logic or funded account.

## Paired sample — identical valid observation denominators, independent Dukascopy quote markouts

At each historical Coinexx REAL/SYNTH entry timestamp separately (after corrected clock mapping), only **last observed Dukascopy Bid/Ask at-or-before the historical timestamp**, age <=1s, is used; exit horizon is **first observed quote at/after +h** within 2s gap. +$0.02 roundtrip commission assumed. These are OFFLINE cross-broker entry-clock diagnostics, not executable policies. The SYNTH-generated entry clock is unavailable causally on REAL/Dukascopy data.

| Horizon | Pairs valid at both timestamps | REAL-clock % profitable | SYNTH-clock % profitable | Mean improvement at SYNTH clock, $/oz |
|---|---:|---:|---:|---:|
| +3s | 140,226 | 9.52% | 10.98% | +0.082 |
| +5s | 139,899 | 13.81% | 17.12% | +0.142 |
| +15s | 139,507 | 25.31% | 36.25% | +0.402 |
| +30s | 139,179 | 32.73% | 47.83% | +0.655 |

The result indicates the synthetic teacher often chooses a different historical second with more favorable *later* independent-feed movement within a selected same-minute/same-direction cohort; it **does not** mean the SYNTH clock is a valid live strategy or that 36% can be compared to the R9 SYNTH 87.14% MT5 full-trade win rate.

All 165,630 selected pair entries also joined exactly on (R9 REAL entry time_msc, side) to the 7-month OVERFIT teacher score corpus; 0 duplicates and 0 missing scores. Overfit survival score >=0.90 retained 13,642/165,630 (8.2%) and the corresponding R9 REAL-time DUKA +15s positive markout was 34.85% versus the 24.77% unfiltered selected cohort. **This overfit score learned on the same months and is NOT a causal BETA signal or OOS evidence.**

## Portable broker-research and scientific boundaries

1. Every BETA strategy must execute using ordered original Dukascopy Bid/Ask ticks; all MTF bars reconstructed from the raw tick chronology and made visible only on closure. No bar-fill approximations.
2. Benchmark *both* per-event alignment to historical R9 REAL/SYNTH teacher (timing/direction/coverage) and independently executable Dukascopy entry quality (precision, recall, correct entries, loss/opportunity retention). Direct broker ticks cannot be identical; requiring identical feed rows would contradict the independent-feed design.
3. Record source-specific UTC mapping, point/price scale, spread and fee, contract size, stop-distance, quote age, broker session/DST, slippage, lot precision, and execution capabilities. Tune hypotheses on independent feed and separately validate translated EA on Coinexx and additional brokers when their real tick data are available; never assert all brokers certified.
4. Preserve BETA015 risk profile for any new FUNDED sim; this audit is not funded. Preserve BETA005 incomplete materialized 17-layer parity task. August stays SEALED, no owner MQL5 authorization, approved_beta_ea=null.
5. Full original R9 all-entry crosswalk (unpaired trades, original broker stop/rearm/concurrency/fees), same-feed executable R9 Python-to-MT5 parity, broker-portfolio validation, and future uninspected validation remain UNVERIFIED.

## Sources / independently checkable artifacts

- Original paired source corpus: https://drive.google.com/drive/folders/1ES78vXb2mFsOsa50BiwCLsT6BXgLe-Oe (03_TEACHER_PAIRS_MONTHLY, 05_TEACHER_SCORES_MONTHLY).
- Original daily raw logger index: https://drive.google.com/drive/folders/11GY1A1pFkwHfaylt2n_-P7Bd4dJ9zFO4 (REAL/SYNTH Jan-02 daily source GZIP).
- Historical source-clock DST matching (ARCHIVAL ONLY): https://docs.google.com/spreadsheets/d/19MoWRLNm3gE-AnT9ve9AzcMM-QqTi757cU5V6ORtjkc/edit .
- Prior actual REAL↔SYNTH paired tick audit: https://docs.google.com/document/d/1vT8JxT7pG7Ry-TMjEZRYGY3nAJC1slS8AnW3ieL033A/edit .
- Original R9 code: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/r9-tick-logger/Experts/GoldMuwahahaMiner_R9_TickLogger.mq5 .
- Existing BETA018 guidance: research/BETA_018_ENTRY_FIRST_R9_TEACHER_AND_BLIND_VALIDATION_PROTOCOL.md .
- Reproducibility package produced in same session (local artifact; not embedded in GitHub): BETA024_CROSS_BROKER_R9_TEACHER_ALIGNMENT_REPORT.md; BETA024_R9_COINEXX_DUKA_ALIGNMENT_SUMMARY.json; BETA024_R9_COINEXX_DUKA_EVENT_ALIGNED_LEDGER.csv.gz (SHA-256 66237d28e0056591648c5d5437feb2e15d82472876615bcc66c73cc3f8c17f06); BETA024_COINEXX_DUKA_EVENT_CROSSWALK.py; BETA024_SOURCE_PAIRED_EVENT_LEDGER.py; BETA024_INDEPENDENT_CROSSFEED_QA.py. QA PASS 16 groups, all 149 dates and one-to-one teacher join.

**Status:** source-specific paired crossfeed bridge recovered/verified, independent Dukascopy laboratory valid for causal testing by design; exact multi-broker fill parity/entire R9 trade universe still outstanding, and cannot be assumed.
