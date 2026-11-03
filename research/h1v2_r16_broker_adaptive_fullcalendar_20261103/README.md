# H1V2 R16 — Source-exact four-month broker-adaptive hindsight entry research

**Research only — no deployable MT5 EA, no broker fill certification, no causal prediction.** This directory contains only new additive R16 code, tests, and immutable derived outputs. The existing H1V2, R9 v2 repaired runtime, R11S1 fixed labels, R11S4 oracle, R12/R12D, R13/R14/R15 branches/archives must never be replaced with this result.

## Provenance / restart: source exact

- Immutable H1V2 teacher Git HEAD `edce573d9c53b743dc5de1b0d741c81370af52c1`.
- Immutable R9 V2 repaired code Git HEAD `ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0`.
- R15 additive parent branch `carson/h1v2-r15-asof-watch60-crossfeed-20261103` Git HEAD `1da637cc3def47fd586f598fa98dbe6881c6c048`. Original R15 three-feed Feb2 06UTC research and all negative delayed stress preserved.
- Original complete 85KB unabridged forensic audit: https://docs.google.com/document/d/1n8Zd37SH3k2mNYpCERHsGSeR5GL-vDNLDv780Bv5-Do/edit
- Original R11 full append-only 251KB ledger: https://docs.google.com/document/d/1eGC-vxRDzu7FxQOY-3PPUfWzoVRrOZU5jaDozuuv0xI/edit
- New active append-only R12–R16 recovery and execution ledger: https://docs.google.com/document/d/1iVv1tAmJlBWhNfXMcw2N50VEVIFrawMObGOzyfUGWmI/edit
- Full R15 unsummarized report: https://drive.google.com/file/d/1SAjN5aBEOY5daE8ylelOd6_V__VwVCHt/view
- Full R15 214-member source/stress archive: https://drive.google.com/file/d/1ST2Uigrlx_u1bGmokYY1InngSbhfkVgb/view
- Prior original 11,520 quarter-hour R12D source proofs: https://drive.google.com/file/d/1zmK60Y3BMPjlVYPZ5YQn8NNm-6FZFmG-/view
- MT5_EXPAND R12–R16 research folder: https://drive.google.com/drive/folders/1vpHz_U-eVFyiC4Tf6YLgFlCK3HN3vP7L

### Frozen exact source geometry

Original Dukascopy quotes for Jan/Feb/Jun/Jul 2026 are `timestamp_ms_utc, bid_raw, ask_raw` in integer `$0.001 XAUUSD quote-price units`, 32,290,648 total records. Input zip file SHA pins are verified by the original R12 loader. Candidate admission is only from actual **observed prefix** quotes with no later same-ms oracle. All lanes require fresh 300s after a >15s quote drought. Original first 250ms and first $1.50 gate are untouched controls.

BUY pays entry **Ask** and closes at observed future **Bid**; SELL receives entry **Bid** and closes at future **Ask**. Nominal original research fee $0.02 quote-price and net profit target $0.10: BUY favorable Bid >= entry Ask + $0.12; SELL favorable Ask <= entry Bid - $0.12. A candidate qualifies the EXACT ORIGINAL S1 strict 15/30 target only when favorable is observed by 15,000 ms AND its opening-liquidation quote never experiences a **-$0.10** adverse price excursion through the entire 30,000ms, with exact observed source coverage and no >15s source quote gap; missing data censored. These two labels are separately verified against the full original R11S1 source quote ordinals for every month.

For each newly permitted candidate, the future-selected oracle closes at the FIRST actual observed later-ms target quote. It allocates at most one position until that quote, never one new trade before previous exit. The nearest-finish interval greedy is exact global maximum **number of disjoint future-known strict winners** for a fixed candidate lane; it does NOT prioritize quota attainment and cannot establish as-of action predictability. Independently optimistic local quarter upper bounds reset previous-quarter occupancy, and are bounds for **that exact changed lane**, not source-wide universally.

### R16 distinct, noninterchangeable experimental lanes

1. `BASE_250_1500`: original first actually observed quote of each 250 ms bin with spread ≤$1.50. Recomputed exact R11S1 original future-good quote ordinal labels; exact R12 first-TP selected counts reproduce 88,233 / 82,027 / 101,889 / 75,928.
2. `DENSE_1500`: ALL observed distinct-ms quotes with current spread ≤$1.50; preserves original R12D future selected counts 96,576 / 90,357 / 110,577 / 81,781, although an earlier quota-priority R12DQ schedule can meet ONE more Feb quarter than R16 max-cardinality greedy.
3. `WIDE_REQUOTE_4000`: R13 original as-of first250 or first actually observed within-bin $0.02+ spread squeeze with current spread ≤$4.00. **Experimental broker-specific price geometry**, never the original R9 runtime admission.
4. `BROKER_CONTRACTION`: within R13 as-of clock, spread ≤0.8 of previously observed 300s spread EMA; short 15s EMA no greater than 300s EMA.
5. `DIRECTIONAL_MICROPATH`: as-of 3s same-sign Bid and Ask movement and minimum movement at least actual current spread + fee + $0.10.
6. `WATCH60_COOL_1500`: wide-observed seed $2–4, then new actual quote after 250–60000ms with current spread ≤$1.50 and at least 30% contraction. Observation is NOT a position; entry is only at actual confirmed quote.
7. `WATCH60_COOL_2500`: wide $2.80–4 seed; later actually observed quote current spread ≤$2.50, at least 20% contraction, 15s EMA ≤300s EMA. New spread gate unapproved.
8. `BUDGETED_MULTI_REGIME`: DENSE ≤$1.50 OR current widened spread ≤$4 with as-of 15s EMA≤300s EMA and coherent 3s Bid/Ask movement individually exceeding spread+fee+target. This is an economic geometry admission heuristic, not a learned direction predictor.
9. `FULL_WIDE_DENSE_DIAGNOSTIC`: all distinct-ms observed spread ≤$4.00, a deliberately wide **unsafe admission pressure bound**, not a permitted runtime policy.

**Original R15 60s post-entry target FULL60 is a different label and was empirically worse for the focal Feb2 hour. R16 watches 60s BEFORE entry, never extending original post-entry good15/safe30 or holding overlapping positions.**

### Independent latency & two-leg slippage tests

`r16_source_delayed_fills.py` replays every frozen future-selected signal without retrospectively replacing it by a later entry when 0/100/500ms latency or slippage changes. Entry fills on FIRST observed quote at or after source signal + latency, no interpolated quote; fill price checks original lane-specific cap ($1.50 or research $4.00), freshness ≤1000ms, and pays slip on BOTH entry and liquidation legs. Outcomes are GOOD, completed BAD, rejected, occupied skip, or right censored. Completed failed entries reserve full30, not a fictitious instant exit; GOOD release on first actually observed target quote. Per-hour/quarter R9 SYNTH references are exact original raw daily source UTC event counts, not hour/4. The frozen future-selected reference is not a causal forecast; delayed completed correctness and original quarter quota are RETROSPECTIVE FRAGILITY measures only. Missing actual failed-position stop/trail/account P&L prohibits any profit inference.

### Quant failure and safety ledger

- F01: initial implementation watch reset only detected >15s raw gaps immediately preceding an **admitted** candidate; a quote gap inside **excluded spread** quote records could be skipped. New `watch_prefix` computes raw full-source gap prefix and invalidates stale watch across any hidden gap. Initial complete source results and their SHA preserved under `failure_preservation/R16_F01_before_watch_gap_repair` (12 preliminary files); **after fix reran all four full source months, not just synthetic tests**. Historical R15/source unchanged.
- F02: running a test module via dynamic import with `Numba @njit(cache=True)` created an unusable cached module name `<dynamic>` when subsequent main-script code tried to unpickle it. Full 2026-Jan rerun aborted early before result writes; a reconstructed diagnostic retained as `logs/retest_01_numba_cache_error.log` (the original terminal traceback was not independently preserved as exact raw output); corrected R16-only routines to `@njit(cache=False)`. Source tests fully rerun, all four source months then completed.
- F03: initial synthetic stress test fixture rose $0.30 over 15s against a BUY actual $0.50 spread, which cannot mathematically achieve entry Ask+$0.12. The intentionally strict code returned 0 BAD, and three incorrect TEST expectations failed. The fixture alone was corrected to rise $1.05 in 15s, exact fee and side preserved. All tests passed after repair; source stress code unchanged.

### Local reproduction and exact validation (research container)

Materialize original SHA-pinned raw source files at `/mnt/data/XAUUSD_DUKAS_2026_NN_ticks.csv.gz`, original full R11S1 ZIPs at `/mnt/data/R11S_NN_FULLMONTH_FIXED15_30_SURVIVAL_FULLPOP_LABELS_CALENDARS_SOURCE_20261103.zip`, and verified original R12D complete quarter/hour CSV source references at `/mnt/data/R12DQ_COMPLETE_ALL_11520_SOURCE_QUARTERS_S4_R12_R12DQ.csv` and `/mnt/data/R12DQ_COMPLETE_ALL_2880_SOURCE_HOURS_S4_R12_R12DQ.csv`; and unpack prior R12 / R13 source into identical local paths. R16 fail-closes if R13 source SHA, R12 source SHA or original R11S1 helper SHA changes. Original SHA pins are in those exact source files; no reconstruction from this README.

```bash
python -m pytest -q /mnt/data/h1v2_r16_broker_adaptive/tests/test_r16_contracts.py /mnt/data/h1v2_r16_broker_adaptive/tests/test_r16_stress.py
for M in 01 02 06 07; do python /mnt/data/h1v2_r16_broker_adaptive/src/r16_fullcalendar_broker_adaptive.py --month "$M"; done
for M in 01 02 06 07; do python /mnt/data/h1v2_r16_broker_adaptive/src/r16_source_delayed_fills.py --month "$M"; done
```

All direct saved candidate/quote ordinal NPZ, selected one-position trace NPZ, all nine mechanism calendars (all UTC 15m/1h including zero trade), 35-source scenario outputs and their each per-signal NPZ are preserved inside per-month source-exact archives; a 4-month catalog and SHA manifest includes complete provenance. This README is *not* a replacement for data, source, the unabridged forensic audit, prior failed results or active append-only progress log.

### Open falsifiers — no invented proof

A. True live Coinexx historical real account Bid/Ask fill/commission/latency feed and independent date-matched Dukascopy path with session calendars; R9 SYNTH vs R9 REAL tester are distinct **tester** domains, not live brokers. Prior R13–R15 only tested one acute Feb2 hour at source-verified 3-feed resolution, not these four whole Coinexx months. B. True source 15m/1h/4h trend, volatility, spread quantiles, liquidity shock and high-order market-structure as-of features with purged LOMO and truly new unexposed dates. C. Separately calibrated independent BUY/SELL/WAIT economic cause-specific hazards with correct right censor and CVaR, time-conditional occupancy option value and reproducibility. D. Strict positive real account P&L under costs, dynamic stop/trail, live fills, max drawdown, session closures, trades/day/week and >85% original monthly SYNTH count with strict >=80% *on-policy* daily/week/month correct. E. No unapproved runtime gate relaxation or quota-forced negative expectancy. Original current R9 v2 EA remains untouched and not deployable based on hindsight.
