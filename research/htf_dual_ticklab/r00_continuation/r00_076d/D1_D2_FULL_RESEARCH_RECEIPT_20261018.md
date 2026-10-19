# R00-076D1 and R00-076D2 — original-event directional correction continuation

**Experiment state:** Two completed historically exposed research cycles; neither meets the target and neither is promoted. This record indexes byte-preserved originals, not a substitute for original reports or experiment code.

**Exact repository ancestry:** R00-076D1 isolated branch created from `5c50fab95a1311fda86ddb5ab2d8d640558e6b4d` (verified R00-076C portable dual-Drive receipt), itself descendant of `7b77c146dae946288856a2e2d2d54d42e557b16e`. Existing R00-068, 070, 072, 076A/B/C broker readers, frozen models and event generator remain unmodified.

## Frozen before first fitting
- D1 plan SHA-256: `a53eb78c9f190d615b5018788674006e2a3e7ac8ca25c2c2a6ee3d815e9ed1d1`.
- D2 plan SHA-256: `842f1f31c65828b3a87d7a23d9e7cf258c78b928994bc59a8b54107a039027be`.
- Inputs: exactly eight independently approved SHA-registered Coinexx/Dukascopy Jan/Feb/Jun/Jul 2026 native bid/ask gzip sources, unchanged R00-067 reader and Coinexx UTC shift (-120 min Jan/Feb, -180 min June/July), Dukascopy native UTC.
- Protected event universe: 814,244 June/July same original quote indices/timestamps; every policy outputs exactly one BUY/SELL per input event, no skip/delay/filter.
- Label: first original midpoint quote in [t+30s,t+32s), signed change strictly exceeding $0.10; neutral/missing wrong. January fit, February froze one policy, June/July historically exposed transfer; not blind.
- Original R9 SYNTH per hour/day/week/month event and correct-direction count floors applied; no exit, P&L, account execution or margin simulation.

## D1: new source-native interarrival duration and four independent tick-updated states
Forty-two predeclared as-of-event features (bilateral quote arrival shocks, response time, completed confirmed M15/H1 public pivot sweep/reclaim/retest, independent impulse/exhaustion/pullback stage/age); original 070 pivot confirmation source reused byte-exact. Four deterministic fixture tests passed, including full prefix invariance. One early local synthetic-fixture defect in NEW D1 wrapper corrected before scoring; no original broker reader touched.

February frozen `FULL_flip_005` at 175,721 correct vs 175,397 protected reference, both brokers. June/July 366,591 / 814,244 correct (45.0223%) vs 367,207 / 814,244 (45.0979%) protected. Frozen rescue 19,731, damage 20,347, neutral flips 4,977; **net -616**, all events retained.

For context only, `FULL_flip_010` (not February-selected) recorded 367,257 correct, +50 over baseline on exposed transfer. **PROHIBITED to retrospectively promote/tune based on that value.** All failed candidates retained.

## D2: separate stage-eligible four-expert direction forecast
Jan-specific impulse, exhaustion, confirmed HTF reclaim and structural-pullback classifiers fitted per broker only where the ORIGINAL tick-updated stage was active; inactive experts keep original side rather than dropping signals. Feb froze `I_alone_005` 175,619 correct vs 175,397 baseline. June/July 366,817 / 814,244 correct (45.0500%), rescued 10,877, damaged 11,267, neutral flips 2,024, **net -390**. Never promoted.

## Interval comparison
Both frozen policies produce full 814,244 original June/July candidate events. Exact preserved R9 SYNTH reference rows: 1998/2006 UTC reference hours and 108/110 days meet >=90% per-window emitted-and-correct-count floors. The R9 reference hours cover 804,611 candidate events, not 814,244; unmatched month-boundary periods are preserved and not silently marked passing. D1/D2 also preserve ISO-week and UTC-month complete rows; 19/20 weeks and 5/6 months meet original interval threshold when using the exact prior R9 reference ledger. No opportunity set has been reduced to raise accuracy.

## Complete source/evidence package created and verified LOCALLY
Filename: `XAUUSD_R00_076D1_D2_COMPLETE_DIRECTION_CORRECTION_20261018.zip`
- **161,409,309 bytes**.
- SHA-256: **`f3a368f4167a0073da0eef4ad445acba325b9a49ab1bef1d9671295420140d51`**.
- **110 original registered ZIP members**, ZIP CRC and all archived per-member SHA-256 verified.
- Contains EXACT Python scripts for both D1/D2 runners and feature extractor, original R00-070 pivot dependency, source-gzip hash receipts, eight new per-event 42-feature caches, Jan specialist model joblibs, all Feb-frozen decision records, every original-event alternative BUY/SELL/probability array for every scored month, per-policy scorecards, exact R9 hour/day/week/month ledgers, synthetic tests, all local logs and original four report texts/investor/governance law copies from the previously verified R00-076C archive.
- The 161MB archive is **locally verified**, NOT verified uploaded to either Google Drive account at this moment. Do not assert cloud copies exist. It must be preserved by direct archive download and/or subsequent authenticated upload. Original prior full R00-076C ZIP remains separate and SHA-registered.
- User-facing local artifact location is /mnt/data/XAUUSD_R00_076D1_D2_COMPLETE_DIRECTION_CORRECTION_20261018.zip (container snapshot is not by itself permanent cloud storage).

## Precise next engineering action
**R00-076D3: purged chronological January out-of-fold counterfactual direction-rescue classification, separating rescued/wrong, damaged/right, and neutral/missing outcomes.** Fit a truly OOF reference model without January in-sample original protected side leakage; keep both quote duration and independent structural episode evidence as separate causal channels. Freeze only on February and evaluate one June/July historically exposed transfer at exactly original events. Do not fit a new static threshold from the June/July `FULL_flip_010` observation. Preserve and compare both broker and original R9 interval evidence.

No prospectively unseen source month has been authorized. No 80%-accuracy, profit, margin survivability, fill or MT5 deployment claims.
