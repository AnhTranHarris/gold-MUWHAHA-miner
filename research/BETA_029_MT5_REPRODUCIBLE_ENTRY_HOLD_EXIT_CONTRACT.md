# BETA029 — MT5-portable mechanics and test contracts (NOT a production MQL5 EA)

Scope: `beta` independent, 2026-09-29. Owner authorizes research/reconstruction and HOLD/EXIT hypothesis unfreezing, **not automatically a new MQL5 EA**. Original Dukascopy January–July original ordered tick feed for research. August SEALED. Gold Hunter V8 is owner-stated genealogy, secondary clue only; internal logic and web review claims NOT established.

## Core deterministic data types

`Tick {time_msc, source_ordinal, bid, ask, flags}` (preserve same-ms source ordering); `ClosedBar {tf_ms,start_ms,end_ms,first_tick,last_tick,O,H,L,C,quote_count,is_complete}`; `Level {level_id,tf,pivot_time,confirmed_at,level_px,high_or_low,first_touch,number_touches,sweep_count,accepted_close_at,reclaim_at,last_event_at,consumed}`; `Opportunity {setup_id,r9_origin_tick,origin_msc,origin_side,regime_snapshot,level_id,eligible_msc,deadline_msc}`; `Position {broker_ticket,fill_price,filled_at,live_mfe,live_mae,trailing_stop,expiry_ms,exit_ack}`.

Custom 250ms, S1, S5, S15, S30, S45 bars are built from original tick chronology as half-open UTC buckets; no synthetic tick path. All M1/M5/M15/H1 pivots require **two CLOSED right-side bars**, first visible only at later quote after right bar end. Full body break differs from intrabar wick. Higher timeframes describe regime/level ownership; not majority vote BUY/SELL. M1/M5 describes acceptance, sweep, reclaim and first/repeated touch. 250ms/1s exact observations describe execution proof and quote-side spread. Position and account state is separate from signal state.

## Screened BETA029 transitions

```text
OPPORTUNITY / R9 E060 coherent-midpoint first-cycle parent:
  CONTINUE_FAST -> if pre-event weak completed-S1 and adverse 250ms quote,
                   reverse on current observed quote (a tested specialist,
                   not a promotion); otherwise parent current quote.
  CONTINUE_RETEST_PROOF -> only when prior completed M1/M5 registry
                   accepted break and fresh touches <=2 and event age <=2 M1;
                   set origin mid; WAIT <= 5000ms for side-adverse >=$0.10,
                   then observed side-aligned cross to >= origin mid+$0.05;
                   execute at actual proof-tick Ask/Bid, otherwise CANCEL.
  FADE_SWEEP_SHIFT_PROOF -> only prior completed registered sweep,
                   accepted-state <=0, event age <=2 M1;
                   WAIT <= 5000ms for price to move origin-side adverse >=$0.10
                   then >=$0.15 with immediate adverse momentum;
                   execute opposite original side on observed current quote,
                   otherwise CANCEL.
  BROAD_SWEEP -> analogous with event-age<=3 and TTL 2500ms.
  STRUCTURE_IGNITION -> specified latest registered event; require actual
                   renewed same-side movement >=$0.05 within 2500ms.
  ALL pending -> CANCEL if quote gap >2000ms, expiration or level invalid;
                   NEVER fill earlier origin in absence of future proof.
```

The screened retest prices are relative to original event quote, **not yet a literal retest of level price**; these labels are provisional mechanical names. Literal level-retest FSM, Quasimodo and post-sweep FVG remain UNTESTED. Do not claim exact public-script or old Gamma-source equivalence.

## Parallel entry/hold/exit work

ENTRY lane: R9 parent vs micro250 vs actual future-confirmed tick entry, report origin cohort, filled count, expired count, true after-spread positive 3/5/15s count, teacher time/side recall and missed original events. HOLD lane: event-specific accepted continuation vs fading/failed ignition, live observed MFE/MAE renewal rate and structure age; no retrospective optimum stop. EXIT lane: frozen 15s timeout, 30s $2 stop/$2 target, 45s $2 stop and activate .60/ trail .35; independently screen earlier failed-ignition exit / runner extension only after current evidence. PROFIT: one-position same account timeline; no arithmetic sum of independent sleeves and no same-time multiple fills.

OnTick may coalesce NewTick events; official source https://www.mql5.com/en/docs/event_handlers/ontick . Use CopyTicksRange https://www.mql5.com/en/docs/series/copyticksrange plus stable source ordinal, dedupe actual duplicate payloads only, reconcile gaps; never submit trade against stale quote. OnTradeTransaction (or verified broker deal/position audit) must confirm real fill and exit before rearming. Broker independent: points/digits/contract size, quote freshness, commission/spread, execution type, lot step, min stops, margin, session/DST.

BETA015 owner-prop simulation guard (for any *funded* replay): 0.01-lot, initial $100,000, one open position, 4k daily soft loss, 5k daily hard loss, 90k equity floor, New York 17:00 reset. Those are separate from owner's eventual small-account deployment profile. No BETA015 test occurred in BETA029. BETA005 materialized 17-layer feature parity remains first incomplete science audit.

Separate next untested source-families: Chinese ORB two-stage rebreak https://www.mql5.com/zh/articles/18486 , public BOS https://www.mql5.com/zh/articles/15017 , Quasimodo shoulder-leg-head-BOS-left-shoulder retest https://www.mql5.com/en/articles/23141 , open-source sweep/CHoCH https://www.tradingview.com/script/HCXJM3dW-CHOCH-Liquidity-Sweep-Detector/ , event-driven modular structure https://www.mql5.com/en/articles/23049 . None of these vendor publications verifies gold profit.

**Promotion rule:** independent causality + incremental absolute correct entries AND source teacher separation + chronological one-account positive after cost under BETA015 + maintained velocity and gross loss + genuine forward later + owner approval BEFORE MQL5 coding, owner executes Coinexx M1 `Every tick based on real ticks` report when authorized. August remains SEALED; `approved_beta_ea=null`.
