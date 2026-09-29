# BETA030 Python-to-MT5 engineering contract — NOT authorized production EA

**Independent BETA only; no candidate promotion. August SEALED.** The BETA030 learned model was fitted in Python and **has NOT been compiled, converted to ONNX, imported, or numerically verified in MQL5**. This is a faithful translation specification, NOT claimed executable .mq5.

## Exact feature/input provenance

Quote source: every original ordered historical Dukascopy `timestamp_ms_utc, bid_raw, ask_raw` in price integers per 0.001 dollars, same-millisecond ties preserving original row order. Tick source is the authority for all fills; actual BUY at Ask/exit Bid and SELL at Bid/exit Ask. Roundtrip 0.01lot one-ounce fee $0.02 assumed, per-symbol broker contract and actual commissions unresolved.

**59 columns in fixed order; do not sort, rename, or retrain hidden columns:**

`X[0..25]` from BETA026: `mid_250_side, mid_1000_side, mid_5000_side, mid_15000_side, mid_30000_side, mid_60000_side, eff5, eff15, eff30, spread, spread_delta500, quote_pressure1, quote_pressure5, position_m1_5, m1_3_trend, m5_3_trend, past5_sweep_depth, past5_reclaim_margin, quote_activity, compression_m1, s1_eff, s1_disp_side, m5atr, m1_vs_m5_trend, past5_max_retrace, time_in_minute_sec`.

`R[26..51]` from BETA028: `m1_high_age, m1_low_age, m1_high_touches, m1_low_touches, m1_high_accept, m1_low_accept, m1_high_sweeps, m1_low_sweeps, m1_high_last_event_age, m1_low_last_event_age, m5_high_age, m5_low_age, m5_high_touches, m5_low_touches, m5_high_accept, m5_low_accept, m5_high_sweeps, m5_low_sweeps, m5_high_last_event_age, m5_low_last_event_age, side_level_pen_atr, side_level_dist_atr, side_touch_count, side_sweep_count, side_accept_state, side_event_age_min`.

`S[52..58]` new, computed at the actual original R9 event tick ordinal:
- S0 normalized 3-point ordinal permutation entropy from **20 observed 1s sampled midpoint changes**; six ordinal histogram counts, stable <= tie ranking; sum `-p*log(p)/log(6)`. This is NOT full ordinal transition-network Jensen-Shannon irreversibility.
- S1 two-sided **positive** truncated CUSUM `S+=max(0,S+ + return/root-mean-square(return) - 0.3)` over 20 previous 1s steps.
- S2 analogous **negative** `S-=max(0,S- - return/root-mean-square(return) - 0.3)`.
- S3 changed-sign count of 20 nonzero 1s sampled returns divided by 20.
- S4 `abs(last_mid - first_mid)/(sum(abs(20 returns)) + 1e-9)`.
- S5 5s/1s **proxy**: sum four nonoverlapping 5s squared midpoint changes divided by `5*sum(20 one-second squared changes)+1e-9`.
- S6 `log1p((number_ticks_recent_1s) / max(1,number_ticks_recent_5s/5))`.
  **Critical:** for 1s anchor at `origin_time-(20-j)*1000`, select the first already-observed raw quote at or after anchor; cap ordinal at current event, never use quote after current event. Whole-vector missing/NaN feature substitute exactly `-999.0`, +inf `999`, -inf `-999`; clamp every input to [-999,999]. Preserve real shape features which were verified causal on artificial equal-ms prefix tests.

## Structural state at original event

`ACCEPTED_EXPANSION=0`: eff5 > 0.3 and side-aligned midmove_5s > 0.08 and previous completed M1 state accepted close.
`FAILED_SWEEP=1`: `side_sweep_count >=1 AND side_accept_state <=0`.
`ROTATION_CHOP=2` overrides above: `eff15<0.16 OR eff30<0.12`.
`UNRESOLVED_TRANSITION=3` otherwise. These are research categories, not true participant order flow or latent market truths.

The original BETA028 bar registry confirms swing pivot only after **two right-hand bars CLOSED** and exposes the state only after the confirmation closing boundary becomes observable. Separate Bid, Ask, Mid and quote age. Custom 250ms, 1s, 5s, 15s, 30s, 45s OHLC must be computed in half-open time buckets from original tick tape. R9 E060 first-cycle caller uses original MT5 R9 *as research reference* but full original broker EA has different spread/position/rearm gate.

## Learned inference (research only)

Raw source train Jan–Mar 2026; April frozen selection Global, threshold $0.20; May–Jul previously-inspected diagnostics NOT pristine OOS. The study exported ten LightGBM text trees (global direct/inverse plus 4 regime-specific direct/inverse) in `BETA030_STATE_AWARE_AI_REPRODUCIBILITY_BUNDLE.zip` SHA256 `e8854e6925cbbbe2f26a28632a4ebdcffc949bbc434ad8e4e417719cc75f17d4`.

```text
on_observed_quote(tick):
   update exact tick, completed-bar state and level registry
   if first eligible R9 research-origin opportunity:
       F = all 59 causal features at actual source tick ordinal
       U_same = FrozenGlobalDirectModel(F)
       U_flip = FrozenGlobalInverseModel(F)
       chosen_side = opposite(origin_side) if U_flip - U_same > 0.20 else origin_side
       ENTER_OR_REJECT only at *current* Bid/Ask; no teacher/OVERFIT data
```

The `0.60 global + 0.40 regime-specific` multi-expert mix was tested but failed to outperform Global on the May–Jul total and was NOT selected on April calibration. Do not claim the current chosen model is a `BOCPD`, true `HSMM`, a genuine order-flow model, or a profitable AI. The +15s models are **direction models, not future decision-time predictors**; they cannot reproduce synthetic future action timestamps.

### Separate actual pending proof

In `BETA030_TWO_LANE_SCREEN.py`, selected regimes arm a bounded `WAIT` after initial event. After a newly observed quote shows the specified event-relative adverse move, a later observed quote can trigger renewed impulse. If timeout, gap >2s or no proof, `CANCEL`, never send order retroactively at origin. **BETA030 has not implemented a literal test against a recorded frozen structural level price for retest**; do not label it as one. Original source has deduped setup identity and exact one-open-position state; real MQL5 entries must wait for broker transaction/fill acknowledgement and confirm true exit before rearming.

### Hold/exit secondary

L15 fixed expiry; L30 stop $2, target $2; L45 stop $2, trail activated at favorable $0.60 then $0.35 giveback; each executed at first original observed quote after condition, with *adverse stop precedence*. Reconstruct missing quotes / live account session / broker min stops / spread / commission / margin / TickFlags / partial fills before any actual EA. Keep BETA015 mandatory for funded research: fixed 0.01 lot, $100k simulation account, daily soft $4k, daily hard $5k, $90k terminal floor, NY 17:00 reset; current BETA030 shadow replay **DID NOT** run that guard. News filter not certified.

### Model conversion / parity and human authorization

MQL5 has native ONNX model execution (`https://www.mql5.com/en/docs/onnx/onnx_mql5`) plus `OnnxCreateFromBuffer`, `OnnxRun`; LightGBM text → ONNX conversion must be independently verified with frozen 59-component fixture vectors and exact output float tolerances. **No conversion has happened here**; an absent verified converter blocks promotion. An alternative native deterministic tree walker may be created after owner approval and tested against Python float-output fixtures. `OnTick` coalesces queue events, so backfill via `CopyTicksRange` for state only; NEVER trade at a historical quote when catch-up is delayed. Preserve same-millisecond event source sequence. Source and model import compilation on local Coinexx M1 real-tick tester awaits explicit owner authorization and separate post-test approval. Standard compact Strategy Tester report is adequate for aggregate comparison, not proof of exact tick-by-tick code parity.

**BETA005 17-layer cached feature parity remains unfinished.** BETA030-specific 126 QA assertions do not certify every 17-layer feature. Do not alter `approved_beta_ea` or treat learned-model serialized weights as human-reconstructible *public* community strategy; its formulas and training algorithm are documented and reproducible using included bundle.
