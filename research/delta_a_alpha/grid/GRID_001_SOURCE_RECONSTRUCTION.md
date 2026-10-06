# GRID-001 — Source Reconstruction and Research Decision

## What the tutorial actually implements

The supplied tutorial is not merely a symmetric pending-order lattice. Its demonstrated engine is a rolling-extreme contrarian inventory strategy.

On H1 it looks back 48 bars. A fall by one grid gap from the rolling highest high opens a BUY. Further falls can add BUYs at additional grid gaps, with the most recent BUY entry becoming the next directional anchor. A rise by one grid gap from the rolling lowest low opens a SELL, with the equivalent chained-anchor behavior for later SELLs.

The source example uses a 100-point gap, 0.01 initial size, and one-grid take profit. The source initially uses no stop-loss. It later demonstrates martingale sizing of 0.01 -> 0.02 -> 0.04 at a 2x multiplier.

## Why the headline win rate is not accepted

A high closed-trade win rate is mechanically encouraged when losing positions are kept open until price returns. That moves risk into floating inventory, basket MAE, equity drawdown, tail liquidation, and terminal close behavior. Win rate alone is therefore not a promotion KPI.

The tutorial itself exposes this: its example holds losers without stops, later shows raw equity/balance behavior, and then introduces martingale as a response to growing drawdown. Delta-A-alpha will measure the hidden state directly instead of rewarding it.

## Two-lane reconstruction

### GRID-001-F — forensic source lane
Purpose: answer whether the source mechanics create a genuine XAUUSD edge under ordered ticks.

- source-faithful anchor semantics;
- fixed 0.01 sizing only;
- no martingale;
- source-style one-gap TP;
- source-style no-stop behavior only inside the forensic simulator;
- forced end-of-window liquidation;
- resource/inventory safety cap causes an explicit FAIL rather than silently changing the strategy;
- never promotion-eligible.

### GRID-001-S — bounded specialist lane
Purpose: test whether grid event logic is useful after removing hidden tail-risk machinery.

- fixed size only;
- hard maximum inventory;
- hard basket/equity loss bound;
- executable Bid/Ask accounting;
- one position/basket ownership policy explicitly defined;
- no martingale;
- no uncapped averaging;
- no assumption that a losing basket must eventually mean-revert.

## Causality corrections required

- Execute on ordered ticks, not 1-minute-OHLC paths.
- Use executable Ask for BUY fills and Bid for SELL fills.
- Do not use a completed bar's future high/low before it exists.
- Freeze whether the rolling anchor uses only completed bars or a causal running bar before replay.
- Record spread at trigger/fill and charge actual/modelled execution costs.
- Force-close residual inventory at evaluation end and include it in PnL.
- Report equity path, not only balance path.

## First decision gate

GRID-001 continues only if a fixed-size, non-martingale, causally executed version shows useful economics or clearly identifies a conditional state that could serve as a specialist without catastrophic inventory risk.
