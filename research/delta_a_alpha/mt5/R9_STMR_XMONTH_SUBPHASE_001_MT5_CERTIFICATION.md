# R9 STMR_XMONTH_SUBPHASE_001 — MT5 Certification Build

**EA:** `Experts/GoldMuwahahaMiner_R9_STMR_XMonth_001.mq5`  
**Research source:** `STMR_XMONTH_SUBPHASE_001`  
**Purpose:** determine whether the Jan–Jul Dukascopy ordered-tick session/timeframe mechanics survive Coinexx MT5 native execution.

## 1. Scientific boundary

This is a **broker-certification port**, not a new optimization pass. It does not modify the authoritative January research floor `STMR_SLEEVE_PHASE_001` (+$877.78). It ports the strongest durable clean-room Jan–Jul child so Coinexx can falsify or confirm it.

The EA intentionally does **not** inherit R9 HybridGate's minute bracket, S1 quality gate, ATR gate, trailing stop, same-minute rearm, or DST session logic. Those mechanisms are a different R9 lineage and would contaminate the STMR test.

## 2. Frozen STMR mechanics

- XAUUSD only.
- Fixed 0.01 lot.
- Hedging account required.
- Maximum 3 STMR positions.
- No Martingale or loss-dependent sizing.
- Tick-native Bid/Ask execution.
- H4/H1/M15/M5 EMA(8/21) states are reconstructed internally from **UTC-aligned completed tick bars** instead of broker chart indicators.
- H4 = environment; H1 = structure; M15 = phase; M5 = transfer/reclaim state.
- Session-local lattice anchor and spatial memory reset at every fixed UTC session transition.
- Sleeve-local first-touch genealogy; no timer rearm.
- One landing-cell crossing decision per tick; large tick jumps do not synthesize intermediate crossing events.
- Hard 300-second maximum hold.
- No trailing stop.

### Fixed UTC sessions and lattice gaps

| Session | UTC | Gap |
|---|---|---:|
| Asia | 23:00–07:00 | $0.75 |
| London Open | 07:00–09:00 | observe-only |
| London | 09:00–13:30 | $1.00 |
| Overlap | 13:30–16:00 | $0.75 |
| New York | 16:00–20:00 | $1.50, but all current NY sleeves observe-only |
| Late NY | 20:00–22:00 | $0.50 |
| Rollover | 22:00–23:00 | observe-only |

### Funded sleeves

| Sleeve | Subphase | TP | SL |
|---|---|---:|---:|
| ASIA_LOWER_TAKEOVER | 23:00–00:00 UTC | $4.00 | $1.00 |
| LONDON_M5_TAKEOVER | 11:00–12:00 UTC | $4.00 | $0.75 |
| OVERLAP_LOWER_TAKEOVER | 15:00–16:00 UTC | $4.00 | $1.50 |
| LATE_ALIGNED_MOMENTUM | 20:00–22:00 UTC | $4.00 | $1.50 |
| LATE_MACRO_SPLIT_TRANSFER | 20:00–22:00 UTC | $4.00 | $1.50 |
| LATE_LOWER_TAKEOVER | 21:00–22:00 UTC | $2.50 | $1.25 |

All other STMR semantic sleeves are classified but **observe-only**.

## 3. Python clean-room comparator

Jan–Jul 2026:

- net: **+$829.71**
- gross profit: **$3,625.77**
- gross loss: **-$2,796.06**
- PF: **1.29674**
- trades: **2,675**
- expected payoff: **+$0.31017/trade**
- max open positions: **3**
- forced final liquidations: **0**

Monthly net:

`+$641.58 / +$43.95 / +$4.55 / -$34.51 / -$19.89 / +$213.13 / -$19.10`

Do **not** expect exact dollar identity in MT5. The Python run used Dukascopy ticks materialized to a research Coinexx-like spread surface and explicit $0.02 round-trip research cost. MT5 uses actual Coinexx Bid/Ask, fills, spread, commission, stop processing, slippage, tick-size rules, and margin.

## 4. Required MetaTrader 5 test

For the first certification run:

- Expert: `GoldMuwahahaMiner_R9_STMR_XMonth_001`
- Symbol: `XAUUSD`
- Timeframe: `M1` (host chart only; strategy builds its own H4/H1/M15/M5 states)
- Modeling: **Every tick based on real ticks**
- From: **2026-01-01**
- To: **2026-08-01** / end of 2026-07-31
- Deposit: **$100,000** for clean comparison with the historical R9 reports
- Leverage: **1:500** if available in the same Coinexx test environment
- `InpQuoteUtcOffsetMinutes = 0` for the existing Coinexx research convention
- `InpDecisionLoggerEnabled = true`
- Do not load an old R9 `.set` file. Scientific geometry is compiled into the EA.

Then optionally repeat with **Every tick** as a secondary synthetic comparison. Real-tick certification is the primary result.

## 5. Fast parity checks before judging P/L

A structurally valid run should show:

1. no entries before 2026-01-05 00:00 UTC;
2. no entries during London Open 07:00–09:00 UTC;
3. no entries during rollover 22:00–23:00 UTC;
4. only the six funded sleeves open trades;
5. overlap takeover only during 15:00–16:00 UTC;
6. late lower takeover only during 21:00–22:00 UTC;
7. position volume always 0.01;
8. no more than three STMR positions at once;
9. no timer-based same-cell rearm;
10. positions close by native TP/SL or the 300-second age limit.

The decision logger is written to MT5 `Common\Files` with a name beginning:

`GoldMuwahaha_R9_STMR_XM01_TESTER_...csv`

It records the session, H4/H1/M15/M5 ownership states, sleeve, direction, lattice cell/key, phase gate, current position count, and decision action. If Coinexx diverges sharply from Python, use that file before changing strategy logic.

## 6. Debug order if Coinexx differs materially

Do not optimize immediately. Diagnose in this order:

1. **Clock:** verify Coinexx tester timestamps and `InpQuoteUtcOffsetMinutes`.
2. **Completed-bar states:** compare H4/H1/M15/M5 states around sample entries.
3. **Session reset/anchor:** confirm lattice anchor on the first tick of each session.
4. **Cell genealogy:** confirm one semantic first touch and no timer rearm.
5. **Sleeve classifier/subphase:** verify sleeve ownership and allowed hours.
6. **Broker execution:** fill price, spread, commission, stops-level, slippage.
7. Only after steps 1–6 should TP/SL/session/timeframe research be reopened.

## 7. Carson edit map

Inside the EA, search these markers before changing code:

- `[EDIT-01]` clock/session translation
- `[EDIT-02]` custom timeframe/EMA state
- `[EDIT-03]` lattice/genealogy
- `[EDIT-04]` sleeve classification/admission
- `[EDIT-05]` lifecycle
- `[EDIT-06]` execution/tickets
- `[EDIT-07]` diagnostics

These tags are intended to keep future edits local and auditable instead of allowing a later repair to mutate unrelated behavior.
