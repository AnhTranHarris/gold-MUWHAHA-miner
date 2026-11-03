# R12C-Q v2 — exact original R9 15-minute source quotas under frozen-signal execution stress

Experiment 2026-11-03 America/Chicago, separate append-only V2. Original R12C V1 source+data ZIP and original R11/R12/R12D/R12BN always immutable. No causal entry model trained or deployed. V1 archive MT5_EXPAND https://drive.google.com/file/d/1r4qJAPnh215Aj5bMrezH55SpkaTVR_xj/view ; previous R12 original ledger https://docs.google.com/document/d/1v0X5Vkif81qV784Ja6FVe5DfyQLx7RoEw-yjC4m7D1Y/edit . V2 runs the same original pinned three source GZIPs Feb2 2026 (two independent MT5 strategy tester modes, Dukascopy raw) and retains exact same source 54 scenarios. Full 54 per-signal NPZ tracks are newly captured without replacing any original V1 file.

**Original source-verified 06:00 UTC quote logger reference** is not hour divided by four. The 4 native original 15-minute R9 SYNTH logged ENTRY counts were exactly 28 at 06:00, 27 at 06:15, 25 at 06:30, and 24 at 06:45 =104. Reference comes from frozen original `R12_02_ALL_UTC_QUARTERS_WITH_R9_SYNTH_VERIFIED.csv` reconstructed from R9 SYNTH Strategy Tester ENTRY events. The complete original R12 month-specific 11,520 quarter source reference is retained upstream. Source server February UTC offset -2 hours. Exact signal and fill ordinals and times in 54 NPZ files. Every successfully delayed filled trade assigned to its **actual fill UTC 15m quarter**, never the theoretical signal quarter if a fill crosses the boundary. Quote-rejected and busy signals assigned to the source SIGNAL quarter separately. Strict precision denominator is completed GOOD+BAD, while censored/not executed separately reported. Missing denominator is undefined/blank and does not become 100% precision or a pass.

For every unique (source, delay 0/50/100/250/500/1000ms, extra per-side slip 0/.02/.05 USD), 4 distinct exact quarter rows. **216 total rows** in `R12C_Q_ALL_216_QUARTER_SOURCE_EXACT_LATENCY_AND_PRECISION.csv` with all 4 exact source targets, frozen nominal signals, good delayed accepted fills, bad executed fills, censored, busy, rejected, strict quality fraction, exact count-parity flag, 80% accuracy and joint flag. **54 separately validated hour rows** in `R12C_Q_ALL_54_HOURLY_FULL_STRESS_RECONCILED.csv`; assert complete 54 scenario matrix matches V1 raw count receipts exactly. Full 54 scenario quote-ordinal trace NPZ, original complete source SHA receipts, manifest and logs preserved. V2 creates no new executable BUY/SELL/WAIT predictor and cannot claim broker order-fill or actual realized net on failed positions.

At 100ms delay and zero extra slippage, results for MT5 REAL tester (not live Coinexx): strict good fills per UTC quarter 43/41/34/17 vs native source exact goals 28/27/25/24; completed-fill correctness 43/61=70.49%, 41/61=67.21%, 34/49=69.39%, 17/37=45.95%. Hence 135 strict good fills >=104 whole-hour quota but **zero of 4 fifteen-minute joint count+80% precision passes**, and only 3/4 quarter *count* pass. At the same stress MT5 SYNTH 273/300/305/250 strict good vs native 28/27/25/24, completed-fill correctness 98.20%,98.04%,97.13%,96.90%; four joint passes. Dukas only 0/1/0/0 good and zero of four joint passes. This is a **deliberately chosen, previously observed Feb2 problem hour**, not independent validation. Repeated future-chosen original signal hindsight remains noncausal; results do not imply a deployable edge. Two MT5 tester modes are NOT two independent live broker feeds.

**Mathematical severe mismatch:** R12D-Q original four-month Dukas future-known firstTP oracle hits 7,313 /7,521 active source 15m quotas (208 impossible under its frozen safety/execution quote domain). R12BN SYNTH native future-known hits 7,520 /7,521 source quarters but synthetic source spread and fill optimism can create false safety if treated as live Coinexx. These contracts cannot be merged into a single executable multi-broker portfolio. Spread and lot sizing are broker-specific; default WAIT on unsupported spread, depth, margin, stale feed, or cost.

R12C-Q v2 local reproducibility:

```
PYTHONPATH=src:<EXACT_R12_ENGINE_DIR>:<EXACT_R11S1_UPSTREAM_DIR> \
 python src/r12c_quarter_latency_v2.py \
 --real R9_REAL_2026-02-02_ticks.csv.gz \
 --synth R9_SYNTH_2026-02-02_ticks.csv.gz \
 --dukas XAUUSD_DUKAS_2026_02_ticks.csv.gz \
 --quarter-reference <ORIGINAL_R12_FEB_QUARTER_SOURCE_CSV> \
 --engine-dir <EXACT_R12_ENGINE_DIR> \
 --prior-scenarios <IMMUTABLE_R12C_V1_54_ROW_CSV> \
 --out <NEW_V2_OUTPUT_DIR>
PYTHONPATH=src pytest -q tests
```

All 15 local tests passed, including 5 independent V2 full 216-row/54-trace/strict denominator/original source 104-count and V1 exact count regressions. Non-source local CI only executes V1 10 unit tests and skips 5 large source-dependent V2 tests; no CI success is called actual four-month model validation. ZIP member hashes and CRC independently checked on the local output, and the exact raw ZIP uploaded to MT5_EXPAND. Previous negatives, source blobs, original 251k R11 ledger and R12 full research log are not overwritten.

Next falsifiable studies (do not claim completed): fill-quote latency and spread distribution over all 88 original daily MT5 SYNTH files AND MT5 REAL tick log days, real broker transactions/quotes with verified symbol trading conditions, five-minute quote-event risk history, calibrated BUY/SELL/WAIT hazard model with source-domain invariant crossed quote features, embargoed prospective train/test and full 15min/h/month risk+profit. No live deployment/MT5 EA modification is authorized.
