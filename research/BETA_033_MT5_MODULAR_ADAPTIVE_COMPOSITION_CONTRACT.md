# BETA033 — MT5-reconstructible modular stateful entry / hold / exit specification

**Date:** 2026-09-29. **Evidence:** January 1 00:00–January 18 12:00 UTC bounded historical research, 4,205,709 original Dukascopy quote ticks, 14,174 parent source events. This file is a **Python-to-MT5 translation contract** — not an authorized MQL5 EA source file, not Coinexx execution parity, not a verified profitable system. Full runnable Python and QA: `BETA033_MODULAR_ADAPTIVE_REPRO_BUNDLE.zip`, SHA256 `c5ea48da853b130fcc27c40145cd12eeeb996afc501b72e1d2e9116e8a0c3173`. Raw source January gzip SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`.

## Four independent types, one account

```text
Tick {ms, source_ordinal, bid, ask, bidask_flags}
ClosedMicrobar {tf_ms, start_ms, end_ms, bid_OHLC, tick_count, completed}
MarketState {regime_id, eff5, eff15, S1_eff, quote_pressure1, M5_closed_trend,
             verified_asof_tick}
StructureState {M1/M5 two-right-bar CONFIRMED pivot, level_id, confirmed_time,
                event_age, first/repeated_touches, sweep_count, accepted_body_close}
Opportunity {setup_id, parent_source_tick_ordinal, orig_side, asof_market,
             asof_structure, originating_server_time}
Intent {setup_id, pending_mode, expiry_msc, entry_tick_ordinal|CANCEL,
        entry_side, real_Bid_or_Ask_quote, specialist_id}
Position {broker_fill_ticket, current_size, entry_price, max_favorable_sofar,
          max_adverse_sofar, state_time, stop, target, armed_trail, deadline}
Account {single_position_ownership, actual_deal_ledger, margin/risk status,
         permanent_protection_lock, NY17_daily_reset}
```

`entry_specialist(state,opportunity,tick)` changes or delays executable entry **only on/after a genuinely observed tick**. If a selected pending proof expires, CANCEL the setup; never retroactively fill its origination clock or use its future 15s markout as proof.

`lifecycle_specialist(family,strength,entry_state)` chooses stop/target/timeout/fail-ignition/trailing parameters from ONLY as-of-entry market and structure. Independently `position_policy.update(current_observed_tick,current_bidask,current_MFE,current_MAE)` applies after-fill ACTIVE state and exits on the current opposite-side quote. It is not an optimizer's hindsight high/low path. `portfolio_arbiter` sorts all completed qualified entry signals by actual original source tick order and allows only ONE open 0.01-lot position. Re-arm only after actual broker exit acknowledgement.

The owner-directed research weighting for ENTRY, HOLD, EXIT is EQUAL initially, without fabricating an arbitrary scalar sum that replaces **realized net P&L**; module-specific inputs/time horizons can vary with state. Audit entry-only, lifecycle-only and combined specialists against the SAME one-position base source and costs.

## Exactly tested BETA033 families

1. **FAST_ACCEPT:** confirmed prior M1-side acceptance with bounded touch/age plus S1 efficiency and quote-pressure gate. Wait up to 1.3s/2.5s for future actual same-side quote extension; then enter with 36s–48s as-of selected hold, ~$1.4 stop, ~$2.6 target, .85/.55 armed trail. Actual entry is observed confirmation quote. No claim of literal pivot fill.
2. **ORIGIN_RETRACE_CONTINUE:** confirmed prior accepted structural context; wait 2.6s/4.5s for adverse origin-relative move ≥ $0.10 (stronger setting $0.18) then favorable recross +$0.04 in original side. A delayed 45s hold, $1.25 stop, $2.80 target and .80/.52 trail is only used on that selected context. **This is origin-relative RETREAT/RECROSS, not literal level-price retest; no source-equivalence claim.**
3. **SWEEP_CONTEXT_COUNTER_MOMENTUM:** previous completed structural sweep count≥1 with no prior accepted directional close; then wait actual adverse continuation and reverse original side on observed counter-momentum. 25s hold, $1.10 stop, $1.60 target, .50/.35 trail in selected context. **This is not an independently observed stop-hunt/reclaim and is not actual institutional order flow.**
4. **REGIME_HARVEST:** original parent entry; as-of M5 trend agreement and current quote pressure +15s path efficiency assign TREND / CHOP / NEUTRAL to independent 15s–50s timed exit, $0.95–1.5 stop, $1–4 target and .50/.37–.90/.60 trail. Compares whole chronology, not summed specialist P&L.
5. **EARLY_FAILURE:** parent entry; actual observed adverse P&L after 2s/4s/6s thresholds allows early close, with longer/tolerant observed persistence in strong aligned states; no retrospective perfect stop. Earlier release of capital is valued ONLY when actual net/trade, after-cost GP/GL/DD and missed opportunities improve.

**Production-size units**: source `bid_raw,ask_raw` are integer price×1000, output dollars-per-ounce with contract assumption 0.01 lot ≈ 1oz of XAUUSD (verify on Coinexx). BUY enters real Ask, exits Bid; SELL enters Bid, exits Ask; $0.02 per 0.01-lot roundtrip is a **research assumption**, not confirmed broker actual commission. Quote gap >3s is counted but no fake liquidation on a missing tick; next observed tick handles any stop/timeout. Slippage, real broker stop mechanics, staleness and partial-fill realism remain unresolved. End cutoff Jan 18 noon exclusive, initial origin buffer 61sec, last actually recorded market quote may occur earlier during closure.

## State/portfolio computation map

```text
OnTick():
  reconcile_tick_sequence_from_CopyTicksRange()
  update quote-side 250ms/1s/.../M1/M5 completely observable buffers
  refresh confirmed pivot + acceptance/sweep, state age and regime
  if already filled: update live hold policy, protective stop and exit intent
  else if setup pending: test observed proof / TTL; cancel or admit
  else: parent first-cycle opportunity -> select one eligible entry specialist
  if approved signal and risk+spread+sizing permit: submit real quote order

OnTradeTransaction():
  reconcile actual deal, volume and position before updating fill/exit state
  do not assume one request == one deal or chronological transaction callback priority
  only then permit new setup ownership/rearm.
```

MetaQuotes primary docs: [OnTick](https://www.mql5.com/en/docs/event_handlers/ontick) (NewTick coalescing), [CopyTicksRange](https://www.mql5.com/en/docs/series/copyticksrange) (historical tick-by-time_msc sequence), [OnTradeTransaction](https://www.mql5.com/en/docs/event_handlers/ontradetransaction) (order vs fill events). Need explicit source-order tie breaks for same millisecond timestamps; broker _Digits/_Point/contract/lot/commission/session NY DST mapping.

## Results and restrictions

Python first-stage common BASE: 13,395 closed/2,478 winners/net **-$10,375.74**, PF **0.1482**, max modeled floating DD **$10,375.84**. Best combined origin-retrace: 12,785/2,382/net **-$9,833.39**, **+5.227% absolute-loss reduction**, $615.04 lower gross loss; historical initial Jan 1–11 +$285.65 net delta, Jan 11–Jan 18 +$256.70. Entry-only +4.944%; lifecycle-only +0.738%; full +5.227%. All remain negative. Other families ≤3.419% (except fast 1.647). Zero of 15 pass >10%; therefore **NO JAN–JUL expansion and NO EA promotion**. No fitted AI performance claim in this unit.

**Reproducibility:** actual full Python `BETA033_MODULAR_4PLUS1_ADAPTIVE_STAGE1.py` SHA256 `1223cb684f4a1f57ea6a7269e9da22ca11869e4446c5edad1b692839696d9a67`, JSON results SHA `a2016b8a3706b420535638912845a8063c98368a39e7b96d9b91aec0e2da1744` (verify precise hash against manifest if changed), QA 225/225 PASS. Bundle contains 17 code, result, cached feature and manifest files, but NOT large raw market ticks. The registry and BETA030 59-variable event cache are source-derived research assets; **BETA005 17-layer materialized cache parity remains first incomplete infrastructure**.

**Owner and data gates**: August SEALED, BETA015 $100k funded risk mandatory before funded certification, no claim of Coinexx real-tick order equivalence, no EA code before owner explicit authorization; original historical R9 SYNTH/REAL/OVERFIT teacher vs Dukascopy independent source separation enforced.
