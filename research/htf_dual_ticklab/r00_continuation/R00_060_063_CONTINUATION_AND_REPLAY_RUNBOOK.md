# R00 entry-direction research — exact preservation and continuation receipt

**Date:** 2026-10-18. **Status:** research-only, no exits/P&L or EA deployment. This file indexes originals, not substitutes for four complete reports or any governing law.

## Original user-approved controlling materials (read originals in full)

- Report 1: https://drive.google.com/file/d/19IS6aelL4Sj9m2hnevkGWqlNkcMhqaCp/view
- Report 2: https://drive.google.com/file/d/1JJitSmvENPubAKD_f_HBxVKezgma8oDx/view
- Report 3: https://drive.google.com/file/d/1nPlaRXsQctmw5TP3lMvl9-pqHEXwCM9c/view
- Report 4: https://drive.google.com/file/d/1D5JxeJJTOaZPCkcqwlQ9jhJkh6hzRt9e/view
- Investor mandate: https://drive.google.com/file/d/1rSWeGBht_IvEWzS9gf5qIZprPIotuxvb/view
- Source authorization supersession: https://drive.google.com/file/d/1qElhwjYLxunB1D_whIC6EJOSY8cHZ3qa/view
- Anti-drift governance: https://drive.google.com/file/d/1kS11NY0RRFaL0NQ-BxUc21u85Dej5VFq/view
- Whole-system governance: https://docs.google.com/document/d/1f65dWnWa9AGGTKYoqQ_7rr28lQbx4EppQEGUUAMWW9U/edit
- Cross-cutting continuation v1.2: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/f9ca199d5c7627678b725c915e4c6eab279029da/research/htf_dual_ticklab/governance/CROSS_CUTTING_CONTINUITY_LAW_v1.2.md
- Handoff and emergency v1.3 originals: https://docs.google.com/document/d/1u1ClV5rT4M31aS2LxfgN1CBFFZkSH70_kYjmOwC1fmE/edit and https://docs.google.com/document/d/1OQ7Kr717hMf3RYgK1Tl6naGfZNwb0vg0auj0M767X_c/edit

## Approved sources and branch lineage

- Original Dukascopy Jan–Jul approved: https://drive.google.com/drive/folders/1lSCfO_awUKkbR4I6xDTy9orjIl0SrgIV
- Original Coinexx Jan–Sep approved: https://drive.google.com/drive/folders/1XzHug6HYQdSKIbKuGhBTOUHawAXynIb4
- Historical R9 SYNTH/REAL and tester reports only from explicitly approved paths in canonical handoff.
- R9 read-only source commit `8729a6345655a7b4ea31facc81982004ee2b8921`.
- Python infrastructure parent `ca4b58aec597174b6f6d18ab2f36cba6836e4f4c`; newest approved governance parent `f9ca199d5c7627678b725c915e4c6eab279029da`.
- New research GitHub descendant branch: `carson/htf-r00-060-061-entry-research-20261018` created from `f9ca199d...` (verify live HEAD before use). Do not reset from main.
- Raw Coinexx source clock shift to UTC: -120 minutes January/February, -180 minutes June/July; Dukascopy original UTC. Both brokers analyzed independently; no merged dealer tape.

## Last independently run and checked experiments

- R00-054 is retained as **best February-frozen volume-complete forecast control** among this lineage, per its original model artifact.
- R00-060: 20 predeclared candidate conditional multi-oracles; January training, February frozen selection, June/July transfer. Scored 547,931 correct / 1,231,388 emitted; 2,002/2,006 reference hours and 108/110 dates reach new 90%-of-R9 correct-count floor. Below 80% direction target.
- R00-061: 60 predeclared confidence/HTF/expert-gate families, selected FEB-only. 89,630 correct / 191,886 emitted (46.71%); 669/2,006 hours and 16/110 dates meet R9 quota. Higher precision cannot be presented as complete success when hour/day coverage collapses.
- R00-062: 24 predeclared time-causal quota/expert modes; selected FEB-only. 130,799 correct / 288,233 emitted (45.38%); 1,462/2,006 hours and 102/110 dates reach R9 floor. Better coverage than R00-061, still not eligible for promotion.
- All three fixed 30-second entry-direction diagnostic labels: side * (future ORIGINAL observed midpoint - decision midpoint) STRICTLY > $0.10; future neutral and missing count as failures on every emitted signal.
- No true prospective untouched future month. June/July used before in project; their transfer results are historical/exploratory. No broker executable fills or returns are implied.
- Missing two Dukascopy source-boundary hours per June and July remain counted as FAIL for every full-volume comparison; no hindsight exclusion.

## Full exact source-code and result locations inside ZIP

- `R00_060_COOPERATIVE_ROUTER/` contains frozen plan, verified source hash log, January model joblib, complete Python, February selection, ALL 80 broker-month tests, all-hour/day/week/month matrix, original-event arrays and tool logs.
- `R00_061_PRECISION_CAPACITY/` contains complete source, frozen plan, all 240 broker-month tests, full selected event arrays, R9 per-window results, January-trained model provenance and full tool logs.
- `R00_062_CAPACITY_SCHEDULER/` contains original script, frozen plan, Numba causal tick lifecycle, 96 broker-month tests, exact interval ledgers, per-event selected decisions and logs.
- `R00_060_063_AUDIT/` contains exact numeric cross-version audit and the next new mechanism R00-063 **DESIGN_ONLY** JSON.
- New source uses original R00-054 native feature caches at `r00_054_native_tick_research/cache/native_{broker}_{month}.npz`. Those eight caches are reproducible from the original registered gzip ticks by `r00_054_native_tick_research/build_native_features.py`, preserved in the predecessor archival ZIP. SHA-256 registered source checks all passed freshly in R00-060, and the exact eight original gzip file names/digests reside in `ORIGINAL_SOURCE_SHA256_VERIFIED.json`.
- The R00-058A/059A original causal-repair portable code/results ZIP is embedded inside this archive for predecessor engine recovery, without any silent replacement of invalid earlier scores.

## Exact safe continuation

1. Validate ZIP CRC and `SHA256_OF_ALL_MEMBERS.json`, recover code and model joblib. Read every original report/law rather than this index as authority. Verify GitHub live HEAD/parent and approved source registry.
2. Recheck SHA-256 against eight source gz files. Inspect the prior R00-058/059A causal future-availability error and its supersession file: a future quote's existence is NEVER an emission gate.
3. Reproduce R00-060, 061 and 062 if needed with the untouched Python and recorded plan/model SHA; do not create a fake Jan/Feb calibration winner by inspecting June/July.
4. **NEXT BUILD ACTION:** freeze a prospective `R00-ENTRY-063` source-native tick event-generating experiment that adds quote-side bid/ask innovation and spread-recovery sequence features rather than postfiltering the current 5-second grid; four experts remain independently armed/expired/confirmed with episode IDs. Retain fixed 30s diagnostic and 90%-of-R9 hour/day floors.
5. Only after a genuine entry-direction improvement from the approved quote data and proper candidate validity gates can the larger MT5 EA portfolio/execution research begin. This receipt does not grant live trading approval.

## Unverified / known blockers

- Full historical verbatim conversation export is unavailable; do not fabricate completeness.
- Not all source-native intermediate feature caches are duplicated inside THIS smaller transfer ZIP; original raw source files are approved and pinned, and previous original parent research archive is needed for reproduction. Historical 046–050 archive may still be unavailable separately. Exact missing dependencies must be disclosed, not silently substituted.
- February matched R9 per-hour/day ORIGINAL ledger was not independently recovered; February selection uses documented 33,523 closed trades/month only. June/July hour/day/week/month floor is strict and based on original archived R9 ledger.
- Current R00-060/061/062 source is preserved here, but any GitHub/Drive upload must be separately verified with exact SHA-256. Never label a local file as cloud synced.
- Historical external hash-chain head/count is not verified in this conversation, so no previous journal chain is rewritten.