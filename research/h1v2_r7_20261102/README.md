# H1V2 R7 — 15,401,392 full-candidate four-month nested risk grid

**Status: offline hindsight research / demonstrably failed 80% selectivity / not a live strategy.**

Source-exact R9 V2 audit read, R6 branch ancestor `265aae380b2ddde2c3db0fa97b06a2a0aca722d6` preserved. Model parent remains repaired V2 `997dfdbd06157faa426c143874ad84277971570e`. No original R9 trading engine code changed. This experimental source receives raw chronological Bid/Ask, no future features; ONLY original exact 30s BUY/SELL quote-ordinal labels are future-privileged targets.

## Sources and dependency

Restore the original H1V2 four-month source-exact kit and the four original SHA-pinned Dukascopy raw gzip files from Primary Drive folder: https://drive.google.com/drive/folders/1lSCfO_awUKkbR4I6xDTy9orjIl0SrgIV . Data must remain at `/mnt/data/{h1v2/results,XAUUSD_DUKAS_2026_01_ticks.csv.gz,...}` or update code paths explicitly.

## Commands (chunked by month)

```bash
PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r7/src pytest -q /mnt/data/h1v2_r7/tests
for mon in 01 02 06 07; do
  PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r7/src python /mnt/data/h1v2_r7/src/full_population_nested_regime.py --month "$mon"
  PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r7/src python /mnt/data/h1v2_r7/src/r7_fine_session_multigrid.py --month "$mon"
done
PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r7/src python /mnt/data/h1v2_r7/src/full_population_nested_regime.py --audit
PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r7/src python /mnt/data/h1v2_r7/src/r7_ranked_tick_replay.py
PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r7/src python /mnt/data/h1v2_r7/src/r7_fine_session_multigrid.py --audit
```

Per month, decompress original R9 H1V2 labels, reconcile original raw Sha, all raw quote indices, build full historical feature grid, independent BUY/SELL success/neutral/wrong count. Parent 99-feature, R2-R6 checkpoint history NOT modified.

Recreate both grid experiments, compare six-hour and 24-hour UTC grid variants, train all-four deliberately in-sample and four leave-one-month-out falsifications, then one-position original quote-ordinal R9 exits without skipping losing selections. Do NOT claim the 513,262 oracle wins were predicted, or the top-0.01%-ranked cohorts were independent validation, or the $0.02 flat fee matches Coinexx actual commissions. Missing original month-end exit quotes => unscorable, not wins/losses.

Verifications: `H1V2_R7_FULL_POPULATION_VERIFICATION_20261102.md`, `results/R7_ALL_FOUR_EXHAUSTIVE_NESTED_REGIME_AUDIT.json`, `results/R7_EXHAUSTIVE_RANKED_TICK_REPLAY.json`, `results/R7_FINE_UTC24_EXHAUSTIVE_TRAIN_AUDIT.json`, four monthly complete receipts and full arrays/histograms.

Research method reference for eventual MQL5 implementation: https://www.mql5.com/en/docs/series/copyticksrange (quote time/flags and chronology). Motivation for future marked quote excitation: Bacry & Muzy *Hawkes model for price and trades high-frequency dynamics*, Quantitative Finance 2014, doi 10.1080/14697688.2014.897000. This R7 model is **not** a fitted Hawkes process.
