# R9 v1.94 — Exact archived Coinexx M60 155-feature LightGBM model bridge

2026-11-13. **SHADOW-FIRST RESEARCH. NOT COMPILED OR DEPLOYED.**

## Preservation and what is genuinely connected
- New branch: carson/r9-v194-m60-155-model-integration-20261113, forked from isolated R9 v1.93 at commit d5bde60f55992cd8799bed85bba68efedbf9aff2.
- The critical rollback R9 v1.90 stays at 8729a6345655a7b4ea31facc81982004ee2b8921.
- Inputs are ONLY archived Coinexx XAUUSD Bid/Ask source-ordinal research features; no Dukascopy, external indices, L2, reconstructed market volume or false order flow.
- Genuine, already trained LightGBM model weights are read from the ORIGINAL Drive archive R9_M60_JanSep_FullTraining_155Features_20261113.zip. Python verifies their immutable SHA256 BEFORE the trusted archive's joblib pickle is deserialized. No retraining or original raw data reconstruction.
- frozen_snapshot.py assembles exactly ONE 155-element historical as-of vector from existing full_month, event, priority and candidate_closes month files. The analytic 11-feature Brownian calculation is imported from the original SHA-pinned source inside the same ZIP.
- score_snapshot.py loads the actual model ONCE in a persistent Python process, returns a real predicted probability and can publish one small atomic score packet (file replaced, not appended). It accepts exact 155-feature vectors; it never substitutes M1 ADX/EMA for missing trained inputs.
- GoldMuwahahaR9M60ModelBridge.mqh strictly matches model SHA, full 155-column contract, timestamp, quote Bid/Ask cents, account, symbol, magic, side, source ordinal and feature end time. The v1.94 EA invokes the model bridge AFTER a normal R9 original S1-qualified candidate and BEFORE OpenTrade. The original 1.93 account risk governor always remains enforced.

## Trading modes and protection
InpR9M60Mode=0 disables model bridge. Default = 1 SHADOW: an exact score is read when available but NEVER changes trade decisions or volume. Experimental 2 FILTER: requires exact current-tick packet or fails closed and compares score to InpR9M60MinProbability (currently 0.0 = no score threshold selection). Do not switch to mode 2 until genuine live feature production, latency parity, and executable after-cost tests succeed; absent packets would block trading, not enhance it.
The trained model scored only the ORIGINAL R9 candidate universe. Model-based filter mode does not promote experimental M1 rescue entries outside that trained universe. R9 v1.93 exit and gross-loss logic are unchanged.

**MISSING LIVE COMPONENT:** Existing cache snapshots work at frozen historical decisions, but are NOT a realtime producer for a new MT5 tick. A low-latency exact as-of 155-feature online producer, with confirmed source-ordinal and same-quote parity, is still needed. The single latest-score packet file also does not synchronize an entire historical Strategy Tester run. This bridge must not be described as a fully operational live AI filter, and its presence is NOT a demonstrated profitability improvement.

MQL5 OnTick may coalesce incoming quotes. Busy polling or blocking for a Python response on each tick could destroy the owner's high-volume requirement. No such blocking is added in v1.94.

## The actual selected model and ROC-AUC
The direct 5-second binary LightGBM trained with 155 real as-of features is selected rather than the unpromoted 237-feature interactions.
Five retrospective chronological models, trained through the month before the evaluation month:
- fold05 (Jan-Apr -> May): SHA256 48c3e3898aab1a78cc5f3b0fec45137af23f2267a4ef665a73eb1e1c431ed661; pooled AUC .719757, original R9 side AUC .705085.
- fold06 (Jan-May -> Jun): bdeb8c4ccc8b6523c3c2cf1185104162c5bf2e3f45271c42c521e50e660ec121; pooled .730416, R9-side .714114.
- fold07 (Jan-Jun -> Jul): bd4c886a470cecac663f5cb71889f195148fa2ef3da932cfce02c361c873e1c5; pooled .756060, R9-side .738934.
- fold08 (Jan-Jul -> Aug): b23e84ed6d9d34b68e5496c71304b76c5db8be8b81be85975ea5dcd1f4df830f; pooled .750072, R9-side .734531.
- fold09 (Jan-Aug -> Sep): 8d6bb3c41741a2223494a8ec87314e9e8d7ea93634ab83498dd133fe7a187d06; pooled .736258, R9-side .723210.
- final_is (all Jan-Sep training, NO held-out metric): 09e1f1b9514dd18bbf6966055e2c277da3695d43cd4c861f997f5ad2c5d75b2f. Source labels this IN-SAMPLE_ONLY; scorer refuses Jan-Sep timestamps with it.
Mean pooled May-Sep ROC-AUC .738513. Mean original-side ROC-AUC .723175. All five test months have been previously explored; no prospective OOS certification. ROC-AUC is for a frozen hypothetical 5-second first-passage label, NOT net USD P&L, actual stop/trailing outcomes, or profit per hour. Do not choose a live threshold from this metric alone.

## Exact 155-feature contract
The 155 columns in original run_train.read_month order, with np.float32 boundary:
1. 14 frozen original R9 decision context features in cached order.
2. 25 HFT features from original 145-col full cache at indices range(14,117,6) followed by range(117,145,4).
3. All 77 event_engine event-time trend/quote-flow features, in their frozen order.
4. All 23 priority-screen source-ordered CUSUM and quote-intensity features.
5. All 11 action_barrier_features analytical Brownian outputs from original archived source.
6. Five action metadata: action side, original-side indicator=1, frozen adaptive stop cents, target cents, spread cents.
14+25+77+23+11+5=155. Missing state remains NaN and is represented as JSON null. No future label is an input. A path that supplies only the 3 MT5 indicators is NOT equivalent to this model.

## One-decision reproduction
Use preexisting source-derived caches already retained; these are not instructions to rebuild them.

Step A: run frozen_snapshot.py with:
--archive ORIGINAL_ZIP
--old-npz EXISTING/full_derived/full_month_2026_09.npz
--event-npz EXISTING/event/event_2026_09.npz
--priority-npz EXISTING/derived/priority_2026_09.npz
--candidate-csv EXISTING/candidate_closes_2026_09.csv.gz
--index 0
--account-login COINEXX_ACCOUNT_LOGIN

Step B: pipe its stdout JSON to score_snapshot.py with:
--archive ORIGINAL_ZIP
--model-id fold09
--packet-dir YOUR_MT5_TERMINAL_COMMON_FILES

This produces ONE historical candidate score; it is not a synchronized full backtest. On an MT5 fold test, set InpR9M60ExpectedModelSha to fold09 SHA256. Default EA SHA points at final_is, appropriate ONLY as a post-September, unvalidated shadow scorer.

## Tiny packet protocol, fully match or discard
16 comma-delimited ASCII CSV fields:
R9M60_155_V1,account_login,symbol,magic,time_msc,bid_cents,ask_cents,side,155,model_sha256,model_id,feature_end_time_msc,source_ordinal,probability,ASOF_PINNED,R9_M60_155_20261113_V1

Packet filename: R9_M60_155_SYMBOL_ACCOUNT_MAGIC.csv in MetaQuotes Terminal Common/Files.
The Python producer atomically replaces a tiny packet. The EA rejects stale timestamps, mismatched Bid/Ask, wrong side, wrong account or model hash and nonfinite probabilities. The file does not prove causal origin without a trusted, verified snapshot producer.

## Pre-activation gates
1. Compile v1.94 in intended MT5 MetaEditor; no MQL5 compiler available in current environment.
2. Compare all 155 per-feature values with frozen source at a representative source-ordinal sample, including duplicates in the same millisecond. Verify Python saved-model score parity to numerical tolerance.
3. Test packet reader and model absence/mismatch/late packet on MT5; ensure shadow mode's orders match v1.93 except accounted execution overhead.
4. Engineer and validate live causal 155-feature producer with acceptable latency; never fake missing inputs, never block critical OnTick indefinitely.
5. Do a COMPLETE existing Coinexx ticklogger chronology & account risk, trailing-stop, fee and position-occupancy replay. Measure trade retention, net USD/trade, hourly profit, hold <=30s, gross loss, drawdown and error rates with model ON and OFF.
6. Freeze the policy before new truly unseen post-Sep Coinexx periods; historical months Jan-Sep are exposed development data.

Sources: https://www.mql5.com/en/docs/files/fileopen ; https://www.mql5.com/en/docs/event_handlers/ontick.
