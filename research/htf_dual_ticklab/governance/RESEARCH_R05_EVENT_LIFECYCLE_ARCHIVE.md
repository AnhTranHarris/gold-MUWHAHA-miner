# R05 — Event-Time Opportunity Search, Executable Research Evidence

**Study**: XAU-HTF-20261016-R05-EXECUTION-PATH  
**Status**: RESEARCH_IN_PROGRESS; NO PROMOTION; TRADING OFF  
**Direct ancestor**: R04 at `0094e76b0cbeedea6f8dd95023c71c1afc811d2b`.

## Exact source artifact

The complete original reproducible Python scripts, causal two-stage impulse/retracement/reacceleration source, smoke tests, frozen LightGBM models, all configuration grids and paired broker trade ledgers were saved under the authorized MT5_EXPAND 04_EXPERIMENT_RESULTS_AND_VALIDATION folder:

- **Original research ZIP**: https://drive.google.com/file/d/1-1d8_BnjEdmjkfkU6f72rdjLN91cnFAm/view
- Exact ZIP SHA-256: `716ad072541818bc067f8d5e3952c0f11d45a311b8f811d7a29def85d7fc487a`
- ZIP size: 2,252,641 bytes, 112 members; member hashes stored in ZIP. Original market tapes are not duplicated.
- Standalone tick-entry state machine source SHA-256: `e25e81d10be092c4399e719d208a006e7f52a8a5e84e71badf31a2726942d650`; `research/r05_event_reaccel.py` inside ZIP.
- Original-tick Numba research code: `research/r05_impulse_pullback_tick.py`; separate from production replay. **No native-engine parity is asserted.**
- Frozen payoff model research: `research/r05_path_quality_search.py` with 5/15/30-second payoff-model artifacts.

## Original authorized market source pins

- Coinexx Jan `1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8`
- Coinexx Feb `5de772aab4d15ebf18aa48850e847c98e2bcb639064790bbed9d87a598c3bf05`
- Dukascopy Jan `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Dukascopy Feb `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`

All four original compressed file digests were independently reverified for R05. Coinexx Jan/Feb raw millisecond clock corrected -120 minutes; Dukascopy unchanged. Two independent accounts and quote tapes; never merge them.

## Constructive experiment, not strategy release

- 320 original-tick trade lifecycle configurations in initial January training, testing impulse detection, Fibonacci-retracement depth, tick-confirmed reacceleration, ATR, RSI/anchored-price regime, stops, targets, trailing, expiry and rearm.
- 26/320 generated 710+ trades per *calendar* day under a $10,000 **capacity-only** seed, with peak 1,654.6/day. None certified for $100/$200 survival or positive after-cost net; do not confuse structural trade capacity with executable economic alpha.
- 96 follow-on chronological broker/month/$100-$200 exact tick trade-ledger scenarios.
- A pooled cross-broker January-frozen 5/15/30-second expected-executable-payoff model, with completed quote-sided January/February evaluation and explicit nonoverlap spacing; model outcome predictions are not broker fills.
- No investor-compliant whole-EA positive/high-velocity solution established. No production CLI change or MQL5 conversion on this branch.

## Practical new mechanism / next engineering operation

Integrate a causal **two-stage event entry** into the R04 multi-signal account arbiter. Use the prior completed-second impulse to arm an opportunity; require a Fibonacci-coordinate retracement and subsequent positive quote acceleration before submitting the marketable entry, with a rolling adaptive spread distribution and joint specialist-specific economic exits, rearm and shared-account margin. Maintain state-sensitive H1, M5 ATR and RSI as conditional context, not universal slow filter vetoes. Inspect full original source in Drive, implement and test against actual package **before** treating any source as production parity. Then run a frozen simultaneous **volume + after-cost net + accuracy + survival** optimization on the 12 broker/capital/latency scenario slots, continuous across months, with complete S/S' counterfactuals.

Community references are hypotheses only: https://www.mql5.com/en/articles/23355 (adaptive spread), https://www.mql5.com/en/articles/19290 (quote-flow proxy), https://www.mql5.com/en/articles/23571 (inventory-aware quoting: not an assumption of retail DMA). The approved R9 specimen remains read-only.

**Anti-drift:** R04 HEAD above is the rollback. The GitHub research pointer records exact original Drive evidence; until full source is committed and re-tested, `GITHUB_DRIVE_FULL_SOURCE_PARITY=NOT_YET_VERIFIED`.