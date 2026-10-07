# R9 STMR_XMONTH_SUBPHASE_001 — Coinexx MT5 Certification

**Branch:** `r9-stmr-xmonth-subphase-001-mt5-r9base-20261006`  
**Candidate EA:** `Experts/GoldMuwahahaMiner_R9_STMR_XMonth_001.mq5`  
**Candidate version:** 9.32  
**R9 executable base:** `carson/r9-tick-logger` @ `23b85ca774efa43acbcb2006fc5e88ce5ac08bf0`

## Why this branch exists

This branch is descended directly from the verified R9 MT5 lineage. It preserves both R9 controls byte-for-byte:

- `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5` — Git blob `7eecb5f1947017a01ce85b2520725de54749e523`
- `Experts/GoldMuwahahaMiner_R9_TickLogger.mq5` — Git blob `5c7655cd3357f9126e8bffd97c34374dfb29f83e`

The STMR grid candidate is added beside them so the same branch contains both the historical R9 control and the new grid build.

## Scientific boundary

The candidate ports the durable clean-room `STMR_XMONTH_SUBPHASE_001` session/timeframe grid mechanics. It intentionally does **not** activate the old R9 minute bracket, S1 quality gate, M5 ATR gate, trailing stop, same-minute rearm, or DST session router. Adding those mechanisms would create a new hybrid strategy and would no longer test whether the Dukascopy STMR result translates to Coinexx.

The R9 base still matters: the candidate uses the same MT5/XAUUSD trade plumbing lineage, fixed-lot discipline, broker-native Bid/Ask execution, trade-retcode handling, tick-size normalization, hedging account assumptions, and an untouched R9 control in the same branch.

## Frozen candidate mechanics

- XAUUSD only.
- Fixed 0.01 lot.
- Hedging account required.
- Maximum 3 candidate positions.
- No Martingale or loss-dependent sizing.
- Fixed UTC session windows.
- Custom completed tick bars for H4/H1/M15/M5.
- EMA(8/21) ownership state on completed bars only.
- Session-local lattice reset.
- Semantic sleeve-local first-touch genealogy.
- One landing-cell crossing decision per ordered tick.
- No timer rearm.
- Hard 300-second maximum hold.
- Broker-native SL/TP execution.
- Opening trade is bound through `CTrade::ResultDeal()` -> `DEAL_POSITION_ID` -> `POSITION_IDENTIFIER` before fill-relative lifecycle adjustment.

Funded sleeves:

| Sleeve | Allowed UTC subphase | TP | SL |
|---|---|---:|---:|
| ASIA_LOWER_TAKEOVER | 23:00-00:00 | $4.00 | $1.00 |
| LONDON_M5_TAKEOVER | 11:00-12:00 | $4.00 | $0.75 |
| OVERLAP_LOWER_TAKEOVER | 15:00-16:00 | $4.00 | $1.50 |
| LATE_ALIGNED_MOMENTUM | 20:00-22:00 | $4.00 | $1.50 |
| LATE_MACRO_SPLIT_TRANSFER | 20:00-22:00 | $4.00 | $1.50 |
| LATE_LOWER_TAKEOVER | 21:00-22:00 | $2.50 | $1.25 |

## Python comparator

Clean-room Jan-Jul Dukascopy stress result:

- net: **+$829.71**
- gross profit: **$3,625.77**
- gross loss: **-$2,796.06**
- PF: **1.2967426**
- trades: **2,675**
- expected payoff: **+$0.310172**
- max open: **3**
- forced final liquidations: **0**

Monthly net:

`+$641.58 / +$43.95 / +$4.55 / -$34.51 / -$19.89 / +$213.13 / -$19.10`

The authoritative January research floor remains `STMR_SLEEVE_PHASE_001` at +$877.78. The exact portable January helper was not recovered, so this MT5 candidate certifies the durable clean-room Jan-Jul child rather than silently claiming journal-0024 parity.

## Compile gate

Compile `GoldMuwahahaMiner_R9_STMR_XMonth_001.mq5` in the Coinexx MetaEditor before testing.

**Required gate: 0 errors, 0 warnings.**

A helper is included at `tools/compile_r9_stmr.cmd`. Set `METAEDITOR_EXE` if MetaEditor is installed somewhere other than the common locations checked by that script.

## Primary Coinexx test

- Expert: `GoldMuwahahaMiner_R9_STMR_XMonth_001`
- Symbol: `XAUUSD`
- Host timeframe: M1
- Modeling: **Every tick based on real ticks**
- From: 2026-01-01
- Through: 2026-07-31 / test end 2026-08-01
- Deposit: $100,000 for direct comparison with the historical R9 reports
- Leverage: 1:500 where available in the same Coinexx environment
- `InpQuoteUtcOffsetMinutes = 0` under the existing Coinexx research convention
- `InpDecisionLoggerEnabled = true`

Defaults already encode the Jan-Jul envelope.

Run the untouched `GoldMuwahahaMiner_R9_HybridGate` over the same Coinexx environment as the control.

## Exact month-comparison mode

The Python cross-month stress was executed month-by-month with a 10-day prior warmup. For the closest MT5 structural comparison, use these tester/input windows:

| Month | Tester/warmup start | Entry start | Entry end |
|---|---|---|---|
| Jan | 2026-01-01 | 2026-01-05 | 2026-02-01 |
| Feb | 2026-01-22 | 2026-02-01 | 2026-03-01 |
| Mar | 2026-02-19 | 2026-03-01 | 2026-04-01 |
| Apr | 2026-03-22 | 2026-04-01 | 2026-05-01 |
| May | 2026-04-21 | 2026-05-01 | 2026-06-01 |
| Jun | 2026-05-22 | 2026-06-01 | 2026-07-01 |
| Jul | 2026-06-21 | 2026-07-01 | 2026-08-01 |

Set the EA's three datetime inputs to the same values. This avoids confusing a continuous Jan-Jul EMA history with the month-local Python warmup protocol.

## Certification invariants

Before judging profit, verify:

1. only six funded sleeves open positions;
2. no London Open or rollover entries;
3. overlap takeover only 15:00-16:00 UTC;
4. late lower takeover only 21:00-22:00 UTC;
5. every volume is 0.01;
6. no more than three candidate positions coexist;
7. `bindFail=0` and `volumeMismatch=0` in the final EA summary;
8. positions close through broker TP/SL or 300-second age exit;
9. no timer same-cell rearm;
10. no entries outside the configured entry interval.

The decision CSV is written under MT5 Common Files with a filename beginning `GoldMuwahaha_R9_STMR_XM01_TESTER_`.

## If MT5 diverges from Python

Diagnose in this order before changing any scientific rule:

1. tester time / quote UTC offset;
2. completed H4/H1/M15/M5 ownership states;
3. session transition and lattice anchor;
4. landing-cell/key genealogy;
5. sleeve classification and subphase;
6. exact opening deal/position binding;
7. Coinexx spread, commission, stops level, fill and slippage.

Only after those are reconciled should session/timeframe research be reopened.
