# R00-054 FILTER05 — source-native ordered-quote failure audit (2026-10-19)

**Classification: EXECUTED ADDITIVE RESEARCH; NO FILTER PROMOTED; NO MT5 EA CHANGE.**

## Cumulative research lineage and authority

- Parent research branch: `carson/htf-r00-054-entry-filter-20261019`; verified parent HEAD `6d063a0ff22f3eec5bb1f1d2ebef583fb163b226`.
- Protected elected primary: R00-054 January-trained `lgb_oracle_weighted` initial BUY/SELL emitter, original quote timestamps and original fixed +30..32s first-observed midpoint signed price displacement >$0.10 definition.
- Previous source-preserved research in order: FILTER01 (FEB KEEP_ALL), FAILURE02 (Jan-trained meta-specialists not sufficiently preserving good signal supply), OVERFIT03 (user-requested June+July **deliberate in-sample** meta-correctness memory experiment), OVERFIT04 (both error-class math and January-calibrated causal category atlas), this FILTER05.
- Work uses established approved independent Coinexx and Dukascopy original raw tick tapes and Python replay; no rebuilding original replay; no holds/exits/P&L or real orders.
- Read ALL original four R9 reports, investor mandate, SRC-002, governance v1.0-v1.4 from original authority before deployment; this receipt DOES NOT replace any of them.

## Filter05 independent executed material

New helper `run_ordered_quote_audit.py` reads original SHA-pinned **eight** CSV.GZ Coinexx/Dukascopy source tapes Jan/Feb/Jun/Jul and the original immutable `FROZEN_R00_054_EVENTS_{broker}_{month}.npz` arrays. Hashes agree 8/8; all **2,574,251 event timestamps** match an original actual quote at the identical millisecond; signs/outcome vectors verified against frozen events, not refit. Coinexx normalized UTC minus 120 minutes Jan/Feb and 180 minutes Jun/Jul; Dukascopy UTC native. First source quote at event timestamp used conservatively so later same-millisecond quote cannot enter decision features (Coinexx event ties: 39 Jan, 2 Feb, 703 Jun, 578 Jul). No future quotes used as decision features. Source flags/quote changes are NOT exchange traded volume or aggressor trades.

New 64-quote-window causal inputs include bid-only, ask-only and joint quote-update rates; quote impulse aligned to original predicted side, last-eight quote impulse, quote turns, stale bid/ask age, spread changes/range, irregular tick gaps, UTC session. Every feature array is archived in its own compressed NPZ. **JAN-only broker-specific empirical quantiles** define the audit conditions. All original signals remain evaluated, none omitted/retimed. `test_source_native_no_future.py` passes future-quote mutation/same-millisecond invariance and all eight original event identity tests.

## Exact June+July research outcomes (independent source evaluations)

| June+July existing candidate events | Count |
|---|---:|
| Total original R00-054 source-event signals | 1,231,388 |
| Correct BUY/SELL signs | 548,099 (44.5107%) |
| Opposite-side moves | 530,177 |
| Neutral/missing outcomes | 153,112 |
| Jan-quantile stale-quote events | 356,281 |
| Correct signals **within** stale events | 146,581 |
| Opposite / neutral within stale | 142,416 / 67,284 |
| Accuracy within stale events | 41.142% |
| Neutral rate within stale events | 18.885% |
| Jan-quantile quote-turn-high events correct / emitted | 152,125 / 350,468 (43.406%) |
| UTC rollover condition correct / emitted | 62,771 / 148,749 (42.199%) |
| 12:00-17:00 UTC overlap correct / emitted | 131,443 / 281,861 (46.634%) |

Stale quote condition is a neutral-risk marker, not an acceptable standalone entry veto: **rejecting it would discard 146,581 previously correct directions** (26.74% of incumbent correctly directed JunJul events) and violate >=95% preservation. Bid/ask update polarity and short-impulse conditions do not alone separate wrong-direction cases at >=80% precision.

**Mathematical target, not a result**: at >=95% retained original correctness, need >=520,695 correct of 548,099 and <=130,173 wrong/neutral retained, so suppress >=553,116 of 683,289 wrong/neutral (80.949%) to reach 80% retained accuracy. Perfect neutral-only veto would max at 50.83%; perfect opposite-only veto at 78.17%. BOTH error types require separate cooperating mechanisms.

## Previous deliberate 80% overfit context, kept quarantined

OVERFIT03 memorizes *previously observed June/July fitting rows*: 99.96% apparent precision on its own one-in-seven training rows at 99.3% correct retention **within the tiny training subset only**; across full June+July 83.39% apparent precision is obtained by retaining only 13.15% of the original correct events, violating high-throughput gates. The February backward AUC was ~0.505 and cross-broker AUC ~0.528-0.537. Do not promote. This proves an overfit memory map, NOT a transferable correct failure oracle. Full FILTER05 causal categories have no 80% qualification.

## New mechanisms for separate predeclared validation, NOT YET SCORED

- N: neutral/no-opportunity **quote-gap, stale-side, source-side spread, rollover** probability, unique ARM/CONFIRM/VETO/EXPIRE/COOLDOWN/REARM lifecycle.
- O: **opposite-direction** hazard using at-decision ordered quote response + publication-safe M1/M5/M15/H1 sweep/reclaim/break/retest structural-state transitions, own independent reset clock.
- S: causal published structural pivot known-at time only (right-confirming bars must finish before pivot is available); no repaint.
- R: session, regime, tick-intensity, completed volatility and spread state, own lifecycle.
- M: 32-second matured **shadow** outcome monitor; never read current signal's own future label; independence measured by ablations.
- Arbiter: keep original R00-054 side/timestamp immutable; veto only when independent specialist evidence combines and calibrated on February; report correct lost, bad rejected and eligible R9 correct-supply per every UTC hour and day, >=95% correct signal retention *per broker-month* and >=90% reference supply; no JuneJul policy tuning.

January secondary-model training requires purged chronological crossfitting of original January predictions due to primary model in-sample bias. February is calibration; June/July historically exposed; genuine unseen blind requires another approved SHA-pinned untouched month. No extrapolation to account liquidity/fills/margin.

## Exact immutable source/result preservation

- User-download artifact: `R00_054_FILTER05_ORDERED_QUOTE_RESEARCH_20261019.zip`, **47,439,595 bytes**,
  SHA-256 `647efea54abcc26e95745d4c96cf4bf81bce8b1f049eb39bdf4c87163c6bab23`, ZIP CRC verified.
- Includes executable **original** `run_ordered_quote_audit.py` SHA `12964c8a7a7009925cf79fd4ca5f8d3c5d89d4e716482045c4d9fb215e527fa5`, all eight exact newly generated input-aligned quote-order .npz caches, `test_source_native_no_future.py`, `frozen_design.json`, `FROZEN_JAN_NATIVE_QUOTE_THRESHOLDS.json`, full 96-row by-broker-month three-class condition table, `RESULTS_READ_FIRST.json`, detailed receipt, and file-size/SHA manifest. Original source raw CSV.GZ and original models remain in existing approved locations and are NOT duplicated in this portable ZIP.
- Readable local full receipt: `R00_054_FILTER05_ORDERED_QUOTE_DISCOVERY/RESEARCH_RECEIPT_AND_NEXT_FROZEN_HYPOTHESES.md`.
- Practitioner sources are hypotheses only: MetaQuotes CopyTicks (https://www.mql5.com/en/docs/series/copyticks), MetaQuotes meta-labeling article (https://www.mql5.com/en/articles/22274), TradingView repainting (https://www.tradingview.com/pine-script-docs/concepts/repainting/), ForexFactory sweep/retest anecdotal (https://www.forexfactory.com/thread/post/15905125).

This GitHub receipt is intentionally small: source and all raw derived arrays are in exact immutable ZIP (not silently claimed committed as individual repository files). Do not claim archival synchronization to both Google Drive accounts without independently confirmed upload/readback.
