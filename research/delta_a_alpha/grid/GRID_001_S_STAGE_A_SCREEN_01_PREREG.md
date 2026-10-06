# GRID-001-S — Stage-A Bounded Screen 01 Preregistration

**Unit:** `DAA_GRID_001_BOUNDED_STAGE_A_SCREEN_01`  
**Purpose:** Determine whether the source tutorial's grid event clock retains useful economics after removing unlimited inventory risk.  
**Optimization status:** BOUNDED FIXED MATRIX, NOT OPEN-ENDED OPTIMIZATION.

## Frozen environment

- Symbol: XAUUSD
- Window: DELTA frozen Stage-A — 2026-01-01 00:00 UTC through 2026-01-18 12:00 UTC exclusive
- Surface: `DUKAS_COINEXX_LIKE_P75`
- Ordered ticks with executable Bid/Ask
- Fixed lot: 0.01 only
- Martingale / loss-dependent sizing: prohibited
- Entry/exit commission: $0.01 per side
- Slippage: zero for this screen, matching DELTA P75 research surface
- Source H1 window: 48 bars
- Grid gap: 100 Coinexx points = $1.00
- TP: one grid gap = $1.00
- Source-style trigger/anchor semantics retained for this first bounded screen
- Residual positions force-closed at Stage-A boundary

## Only variables allowed to change

Inventory cap per direction:
`[1, 2, 4]`

Hard stop distance from each entry:
`[1.5, 2.0, 3.0, 4.0]` grid gaps

Total fixed variants: 12.

No other parameter changes are permitted in this unit.

## Required metrics

For every variant:
- trades;
- wins and win rate after commission;
- net/gross profit/loss;
- profit factor;
- expected payoff;
- trades per active trading day;
- maximum balance drawdown;
- maximum equity drawdown;
- minimum equity delta;
- maximum simultaneous positions and total lots;
- TP closes, stop closes, boundary liquidations;
- average/max holding time;
- spread/commission cost;
- $100/$200/$300 theoretical equity survivability;
- comparison against Stage-A source forensic lane;
- comparison against R9 SYNTH trade-velocity guiding light.

## Decision rule

This screen does not promote a specialist.

A variant is worth a second bounded study only if:
1. net profit > 0;
2. profit factor > 1;
3. no unresolved catastrophic tail is hidden in boundary liquidation;
4. equity drawdown is materially reduced from GRID-001-F;
5. trade velocity remains high enough to plausibly contribute to the REAL→SYNTH gap;
6. fixed-0.01 small-account equity diagnostics improve materially.

If no variant satisfies those conditions, physical grid inventory is retired and the next lane uses the grid only as an event clock / signal generator with single-trade bounded ownership.

August remains sealed. MQL5 remains unauthorized.
