# DELTA-A GRID-HF R1 — Research Checkpoint

## Research question

Can grid geometry preserve R9-SYNTH-like opportunity volume while avoiding the low-frequency choke and uncontrolled inventory risk of a conventional grid EA?

## Source provenance

The initial control was reconstructed from MegaJoctan / OmegaFX's public Python Grid Bot example and accompanying YouTube tutorial. The published source establishes:

- rolling high/low grid anchoring,
- fixed grid spacing,
- sequential same-side entries,
- per-position take profit,
- optional Martingale extension,
- finite maximum-order control in the backtest variant.

DELTA-A rejected Martingale as a candidate mechanism after tick-level stress testing.

## Data and causal requirements

- Instrument: XAUUSD.
- Source: ordered Dukascopy Bid/Ask ticks.
- January is the harvest/research month.
- August remains sealed.
- No future ticks may influence entry decisions.
- Bar/context features must be completed/as-of when used.
- The research comparator execution surface is `DUKAS_COINEXX_LIKE_P75`.
- Live MT5 must execute on actual broker Bid/Ask.

## Evolution of the architecture

### Phase 1 — physical basket control

The original grid generated apparently extreme closed-trade win rates because losers could remain open. Forced liquidation exposed the hidden inventory loss.

### Phase 2 — basket recovery

Replacing independent full-grid take profits with basket-level recovery near VWAP materially improved retained PnL and removed large end-period stranded inventory in the leading controls.

### Phase 3 — low-drawdown mechanics

The strongest causal risk improvements came from:

- finite inventory,
- single-basket ownership,
- reclaim-confirmed add-ons,
- earlier basket-level recovery.

Hard loss caps and simple generic volatility/momentum vetoes were not robust enough and were rejected.

### Phase 4 — high-frequency virtual grid engine

The research then decoupled **grid sensing** from **physical grid inventory**.

A virtual grid can generate many candidate event clocks without opening a basket for every level crossing. This allows separate specialists to own continuation, reversion, failed-reclaim, exhaustion, or pullback states.

## R9 SYNTH reference

Historical R9 SYNTH comparator:

- 219,342 trades Jan-Jul
- 87.14% winning trades
- +$309,122.85 net
- PF approximately 20.04
- expected payoff approximately +$1.409/trade

R9 SYNTH is an aspirational/teacher comparator, not causal proof for DELTA-A.

## Current GRID-HF R1 result

Current January checkpoint summary after the present multi-scale regime bank and current de-duplication checkpoint:

- 29,540 unique candidate trades
- approximately 1,019 candidate trades/day
- +$5,486.71 net
- +$0.1857 average/event
- PF 1.0424
- approximately 49.2% positive outcomes
- approximately $2,195 closed-event-sequence DD
- 26,090 continuation events
- 3,450 reversion events

### Interpretation

**Volume objective:** experimentally achieved at approximately R9-SYNTH January scale.

**Entry quality objective:** not yet achieved. Expected payoff and PF remain far below R9 SYNTH.

**Durability objective:** not yet achieved. The current HF version is January-only.

## Regime-bank mechanics at this checkpoint

### Volatile/persistent specialist

Current leading continuation profile:

- virtual grid spacing: approximately $2.375
- direction: continuation of the crossing
- lifecycle: 120 seconds
- causal event generation on native Dukascopy signal quotes
- fill/economic evaluation on P75 execution quotes

The positive neighborhood around this profile includes roughly $2.125-$2.50 spacing, with 120 seconds strongest in the latest bounded January sweep.

### Quiet/rotational bank

The quiet-state research bank uses wider reversion scales:

- $4
- $5
- $6
- $8
- $10

The bank exists because no single quiet reversion scale supplied both adequate quality and R9-scale density. Combined independent scales supply a denser candidate population.

### Regime proxy

The first causal regime bank used a native Dukascopy spread/volatility proxy near **0.60** as the bounded switching threshold.

This threshold is a research checkpoint, not a production constant. It requires neighborhood and Jan-Jul validation before translation lock.

## Key scientific finding

Grid geometry is currently much better at identifying **when something is happening** than **which direction ultimately owns it**.

The multi-scale grid clock covered a large fraction of R9 SYNTH January timing, while raw grid-crossing direction was approximately chance-level versus R9 BUY/SELL labels.

Therefore the next scientific task is **directional ownership and specialist routing**, not signal-count expansion.

## Frozen pause conditions

Refinement is paused at this checkpoint by owner request.

Do not claim:

- MT5 certification,
- Jan-Jul durability for GRID-HF R1,
- live profitability,
- R9 parity,
- production readiness.

Do preserve:

- the high-volume event architecture,
- P75 research execution semantics,
- January benchmark metrics,
- rejected Martingale/naive-basket lessons,
- current regime-bank mechanics.

## Next research unit after pause

**GRID-HF R2 — High-Volume Directional Ownership and Specialist Routing**

Hard design constraint: do not improve PF by choking opportunity supply far below the approximately 1,000 unique candidate/day floor.
