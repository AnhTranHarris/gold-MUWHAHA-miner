# R23H hourly / quarter research — source-exact full-run evidence

**Date**: 2026-11-04 America/Chicago. **Research classification**: historic four-month R23 future-informed ceiling preserved; new January 2 two-feed engineering pilot trained heavily in sample; **not a tradable strategy**.

## Exact preserved predecessor sources

R23 immutable 12 scenario × 8 source-month full calendars and future-selected quote ordinal negative/positive/censored NPZ live in original independent source archives:
- DUKASCOPY source-month ZIP: https://drive.google.com/file/d/1K_v9ZKCD66_GtLd1o94IF780DvDXCmiz/view
- Coinexx-linked MT5 broker export source-month ZIP: https://drive.google.com/file/d/1tOOuaWNJxmsMEunUHrc0uZE2rUFIFQw4/view
- R23 global source+test+receipts: https://drive.google.com/file/d/1mcg57NStAmInyR_goYac-9wEA9hZ8tdj/view
- R23 complete native source report: https://docs.google.com/document/d/1TBfwf2faJlb9YT1HXUxhQImcIU0ddLF1g266ohXmCt8/edit
- Frozen R24 source + models + 72-member archive: https://drive.google.com/file/d/1noemVZHdmQYNxBnW7N2patrkb5HO760C/view

These large predecessor source byte streams are not duplicated in this new archive. The original R9 synthetic research count is a reference not a tick feed. Four UTC months exposed in-sample: 2026-01,02,06,07. UTC quarters 11520, source reference-positive quarters 7521, active hours 1917. Quota reference monthly [27980,33523,31758,24324], total 117585.

## This new additive archive structure

- `src/r23_hourly_reconciliation.py`: independently verifies **all** 96 original full-month R23 scenario results, no sampling; source-count and selected-count parity at month, day, hour, quarter; expected calendar rows; original source SHA when January raw mounted; writes atomic receipts. Chooses an optimistic **best original scenario per historical bucket** solely as a diagnostic, with explicit future privilege and cross-boundary occupancy caveat.
- `src/r23_causal_firstday_gate.py`: implements a NEW 13-feature ordered quote-revision grammar on top of the frozen 47-feature R24 causal input path, 15s separate target-first, adverse-stop, quote-gap and complete-15s-survival heads for both sides plus 10s WAIT; daily source-exact 8h lookback, +90s lookahead for target-only label creation; original quote ordinals; 100ms real next quote fills; sample-and-fit heavily in sample on original Jan2, not fresh OOS. **STOP was enforced when rare gap head had no sampled positives (both feeds): all policies WAIT; no artificial positive precision or volume.**
- `frozen_r24_archive/source/r24_firstpass_engine.py`: original unmodified source from exact 72-member source ZIP. It is a frozen dependency; not a separate competing engine rewrite.
- `tests/*.py`: strict future-quote prefix invariance, same-ms ordinal, gap crossing a horizon, full-horizon survival distinct from target, WAIT future supervision and calendar provenance.
- `results/DUKASCOPY_RAW/{01,02,06,07}` and `results/MT5_BROKER_EXPORT/{01,02,06,07}`: **ALL** original R23 scenario-by-day/hour/quarter unabridged source tables, new per-hour/per-quarter hindsight best-case diagnostic source lines, every source-month atomic SHA receipt.
- `results/{SOURCE}/01/2026-01-02`: **ALL** causal engineering input candidate historical original ordinals, two sided × 15/30/60 sec five-cause labels, full15 held and true gap label, WAIT10 label, as-of features, saved individual LightGBM training head models, all 24 hours/96 quarters and all selected trades (zero after failclose), source SHA atomic receipt.
- `results/REPLAY_STDOUT.log` and per-feed day pilot run/failure logs, full manifest. Failures preserved; a tool execution runtime stack during first Dukas attempt is included in the research progress ledger and logs.

## Historic archive reanalysis results: original future-informed ceiling

Dukas: Jan 1878/1878 original active 15min; Feb 1817/1819; Jun 1954/1954; Jul 1869/1870. All four months hourly quota 1917/1917. Coinexx-linked MT5 all 7521/7521 active 15min; 1917/1917 active hours. These are from the frozen R23 archive, not a new trained causal predictor. The remaining Dukas original reference quarters are `2026-02-06T21:45:00Z` best 15 vs R9 18, `2026-02-12T23:00:00Z` best 13 vs R9 24, and `2026-07-17T20:45:00Z` best 9 vs R9 15. Each best scenario's post-hoc per-period switching can violate single-position global chronology; it is not a tradable or even a coherent global policy.

## January 2, 2026 dual-feed NEW causal engineering negative

Original Jan raw SHA verified byte-for-byte: Dukas d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5; Coinexx-linked 1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8.

Dukas Jan02 as-of 1s source signals 65914, true +100ms-fill 60882, training sample 25000. MT5 73395 signals, 69899 observed fills, 25000 sampled training. Both 15s gap heads had too few positive training labels and were NOT trained. At first execution, fail-closed exception HEAD_MISSING_POLICY_FAIL_CLOSED; preserved as negative. In recovered execution, any missing head assigns NaN unknown probability and no action can pass eligibility; all WAIT. Therefore selected=0 and all daily/hourly/quarter actual executable claims FAIL, not a trivial 100% accuracy. Test source unit tests 8 PASS, compileall PASS.

This is not a four-month causal training result; Jan2 is merely a scientific engineering pilot. Even successful same-day fit would be overfit and would not certify profit, trade volume or actual broker fill.

## Outstanding gates — exact continuation

1. Preserve and read back uploaded archive and ledger; commit the isolated research source to the new GitHub branch without replacing original R23/R24. Verify GitHub HEAD before and after.
2. Address **rare event** quote-gap model through month-level calibrated shared-risk estimation, source-day risk sets, and conservative uncertainty; do not zero-fill or invent daily news/gap probabilities. Establish a proper competing-risk likelihood and horizon-monotone cumulative incidences, rather than interpreting independent binary heads as a partition of 1.
3. Run day-by-day month-specific, two-feed raw quote source Jan/Feb/Jun/Jul, keep 8h HTF and 300s fresh-gap prefixes, >=60s future label halos, exact original global source quote ordinals, full month-to-quarter calendars and zero-reference periods. June Coinexx source requires original July halo and UTC offset/DST provenance; no synthetic stitching.
4. Fit genuine new hierarchical broker×session×regime marked-order competing-hazard model with independent waiting-time opportunity arrival. Evaluate one-position historical initial entry correctness and full-H survival, every 15min and hourly R9 volume count, preserve wrong and censored causes. Compare with R24S7-0006 complete original negative baseline and R23 future oracle, not just its positive trades.
5. Broker operations calendar UNKNOWN until account-specific verified permissions; MQL5 historical economic calendar terminal export source exists but uncompiled/unrun. ForexFactory pre-release vintage and actual data as known then UNKNOWN; mark missing not no-news. Genuine actual/forecast releases must have a verified first-known publication timestamp.
6. Later EA entry/hold/exit and portfolio risk/cash study separate. No MT5 EA changes, no demo/live orders, no broker execution proof.

## Reproduction commands

```bash
python -m pytest -q tests
python -m compileall -q src
python src/r23_hourly_reconciliation.py --dukas /mnt/data/R23_DUKASCOPY_RAW_COMPLETE_FOUR_MONTH_ALL_SCENARIOS_QUARTER_HOUR_DAY_BIDASK_ORDINALS_20261103.zip --mt5 /mnt/data/R23_MT5_BROKER_EXPORT_COMPLETE_FOUR_MONTH_ALL_SCENARIOS_QUARTER_HOUR_DAY_BIDASK_ORDINALS_20261103.zip --dukas-jan /mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv.gz --mt5-jan /mnt/data/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz --out results
PYTHONPATH=src python src/r23_causal_firstday_gate.py --source DUKASCOPY_RAW --out results --iterations 24
PYTHONPATH=src python src/r23_causal_firstday_gate.py --source MT5_BROKER_EXPORT --out results --iterations 24
```

No failure discarded. Do not use result CSV quoteUSD amount as cash dollars; source labels only.
