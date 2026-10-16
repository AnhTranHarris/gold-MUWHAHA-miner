# XAUUSD HTF — Constructive Indicator/Regime Discovery R01 (evidence-pinned, UNPROMOTED)

Date: 2026-10-16  
Scope: existing independent XAUUSD HTF research, not a new EA project.  
Existing branch: `carson/htf-shared-signal-arbiter-v0.1`, descendant of `f9ca199d5c7627678b725c915e4c6eab279029da`.  
All original authorized tick sources/UTC and existing engine code remain unchanged.

## CANONICAL ORIGINAL EXPERIMENT ARCHIVE
MT5_EXPAND `04_EXPERIMENT_RESULTS_AND_VALIDATION` direct file:
https://drive.google.com/file/d/1-Jx7niKmyZUcw8Px_jBmyqltf--NyLP6/view

Filename: `XAUUSD_HTF_Parameter_Discovery_R01_2026-10-16.zip`  
Exact size: 19,381,299 bytes  
SHA-256: `9f59be775f0f0c93990950e8bd3fc81aa247098c5dfa5d237a760c6de19f4d9b`  
Verified: uploaded using MT5_EXPAND, then downloaded back; SHA-256 MATCH, ZIP CRC PASS; archive 141 members.

**Read the original scripts, full grid CSV, all trade ledgers and checksums inside this archive. This file is a pointer, NEVER an evidence substitute.**

## AUTHORIZED TICKS (originals remain PRIMARY, outside the ZIP)
- Coinexx Jan 2026 7,699,274 ticks, SHA256 `1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8`
- Dukascopy Jan 2026 9,135,062 ticks, SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Coinexx Feb 2026 7,102,818 ticks, SHA256 `5de772aab4d15ebf18aa48850e847c98e2bcb639064790bbed9d87a598c3bf05`
- Dukascopy Feb 2026 7,538,339 ticks, SHA256 `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`
Jan-Feb Coinexx offset -120 min, Dukascopy native UTC. All original compressed bytes rehashed. Each broker replayed independently, never pooled.

## CONTRIBUTION — CORRECTION OF FAILURE-ONLY RESEARCH
The 5,400 configurable mechanism/indicator combinations screened Fibonacci H1 swing location, H1 and M1 RSI thresholds, ATR-normalized quote-weighted anchor deviation, quote-activity state, named UTC session buckets, and 1/3/5/10/15-minute horizons. QWAP is NOT consolidated executed-volume VWAP.
- 312 training-positive configurations with minimum 20 training opportunities.
- 11 configurations had positive average hypothetical quote-sided markout across all 6 January broker/time blocks (only six of those had >=7 observations per each block).
- These are *opportunity markouts*, not integrated account profit.

Original tick execution shortlists:
- Jan Coinexx R01_02971 stop .5xM5 ATR/target 1.2x ATR, $100 start +21.89 USD in 65 closed trades, Dukascopy same -51.18 USD; same Feb settings were negative.
- Jan Coinexx R01_03897 stop 1xM5 ATR/target 2.4x ATR, $200 start +91.19 USD; Dukascopy -8.148 USD.
- Continuous Jan-Feb Coinexx R01_03897 on one $200 account +67.76 USD (equity max DD $97.35), Dukascopy same account setting -104.402 USD (DD $128.578). **Neither portability nor survivability is certified.**
- February parameters locked *from the January search*, not retuned on February; historical tape already observed, not prospective holdout.

## STATUS / LIMITS
`EXPLORATORY_RESEARCH_IN_PROGRESS`; zero strategy promotions. Original negative Jan96 remains immutable in MT5_EXPAND failed-research folder. This constructive search FOUND candidates but not a robust two-broker investor-approved integrated EA. Fixed illustrative broker execution settings and estimated 5% trade-risk guard are NOT approved thresholds. Fixed UTC session windows need canonical DST logic. RSI/ATR indicator **periods**, complete Fibonacci geometry, VWAP proxy anchoring and causal S5/S15 tick entry timing remain material dimensions **not fully optimized**. Multiple testing, overlapping signals, large marked drawdowns, price-quote spread differences, retrospective exposure and absence of real fill receipts all remain.

## PRECISE NEXT ACTION
**Do not restart original-source audit or re-run failed Jan96 as new discovery.** Read above archived code/grid/trade-ledger evidence; implement a separate source-locked, frozen-parameter experimental mechanism using S5/S15 tick-derived causal features, adaptive ATR stop/target/time-exit, dynamic quote/volume proxy, and regime/session-specific choice of Fibonacci/RSI/QWAP roles. Ensure chronology, next-tick fill, latency, broker-specific spread and margin. Add a single shared-account whole-system comparison against the current baseline, 2 brokers × $100/$200 × 0/250/1000ms and full continuous January-July scored evidence with real broker ticks as authorized; proceed month by month retaining accepted settings and all weak periods. Never describe optimization-selected January/February as untouched OOS. Missing investor numeric thresholds remain TBD. Deployment/MQL5 trading OFF.
