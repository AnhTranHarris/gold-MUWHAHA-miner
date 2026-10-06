# DELTA-B DB001C — Minimal Executable Scalp Lifecycle Preregistration

**Status:** FROZEN BEFORE ECONOMIC REPLAY  
**Lineage:** DELTA-B only  
**Layer:** Grid Layer 1  
**Parent:** DB001B Scheduled Event Elasticity

## Primary question

Does the verified Intrinsic-Time Executable Lattice create any causal, after-cost directional value on canonical XAUUSD real ticks before Volume Profile, RSI, or later specialists are added?

This unit is diagnostic but executable. It is the first DELTA-B unit allowed to create trades.

## Data wall

Initial Stage-A replay:

- canonical Dukascopy XAUUSD January 2026
- start: 2026-01-01 00:00 UTC
- end: 2026-01-18 12:00 UTC exclusive
- expected parent DELTA Stage-A tick count: 4,205,709
- January source SHA256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- August remains SEALED

No Jan-Jul expansion is permitted merely because one January slice looks interesting.

## Economic assumptions

- one chronological position maximum per tested lane
- fixed 0.01 lot
- research cash exposure assumption: 0.01 XAUUSD lot = 1 oz
- entry uses executable Ask for BUY and Bid for SELL
- exit uses executable Bid for BUY and Ask for SELL
- quoted spread is therefore paid naturally
- additional round-trip commission: $0.02 per completed 0.01-lot trade
- slippage buffer: 0 for the first diagnostic; positive slippage sensitivity is mandatory before promotion
- no midpoint fills
- no leverage increase
- no pyramiding in DB001C
- no martingale/adverse adds

## Entry event source

Only newly emitted intrinsic Grid events may create entries.

No position is opened because price merely remains in a Grid state.

The Grid kernel is the current exact DELTA-B branch kernel after:

- conditional scheduled-event elasticity;
- prior-history tie-midrank spread percentile;
- true higher-scale reclaim semantics.

## Four nested ownership lanes

These are not four unrelated strategies. They are nested attribution slices of the same event lattice.

### G0 — MICRO_DC

Any newly emitted L0 / 1Q directional-change event may enter in the **new event direction**, except when the final Grid state is `CHURN_SHOCK`.

Purpose: measure raw directional-change value and preserve maximum Grid opportunity density.

### G1 — OWNER_ALIGNED_DC

A newly emitted L0 event is eligible only when its new direction agrees with the majority sign of at least one active higher intrinsic scale L1-L3.

Purpose: test whether higher-scale ownership improves the raw L0 event without importing another indicator.

### G2 — ESCAPE

A newly emitted Grid event is eligible when the final state is `ESCAPE`. Entry direction is the coherent active Grid direction.

Purpose: measure confirmed multi-scale expansion.

### G3 — TRUE_RECLAIM

A new event is eligible only when the final state is `FAILED_ESCAPE_RECLAIM`.

By construction, the new L0 direction must realign with the pre-existing higher-scale owner.

Purpose: measure failed micro-excursion / structural realignment.

## Deliberately untraded state

`ROTATION` does not get its own directional rule in DB001C.

Reason:

Grid can detect rotation but cannot yet answer **where price sits inside accepted value**. That is intentionally reserved for Volume Profile Layer 2.

If rotation contains large unused opportunity, that becomes a concrete justification for Layer 2 rather than permission to invent another Grid-only direction rule.

## Single frozen lifecycle

All four lanes use the same lifecycle so entry quality is not confounded with exit optimization.

At entry, freeze:

```
Qe = q_context_at_entry
```

For BUY:

```
stop   = entry_ask - 1.00 * Qe
target = entry_ask + 1.50 * Qe
```

For SELL:

```
stop   = entry_bid + 1.00 * Qe
target = entry_bid - 1.50 * Qe
```

Maximum hold:

```
30 seconds
```

No trailing stop.  
No breakeven move.  
No favorable add.  
No stop widening.

Exit priority is determined by actual ordered executable ticks. There is no bar-level simultaneous-hit assumption.

At timeout, close on the first valid executable quote at or after the deadline.

If the bounded replay ends with a position open, close it at the last observed executable quote and mark `END_OF_WINDOW`.

## One-account rule

Each ownership lane is replayed independently first for attribution.

A combined portfolio is **not** created in DB001C unless at least two lanes independently show positive after-cost expectancy and a later preregistration defines collision priority.

Standalone PnLs may not be arithmetically added and called a portfolio.

## Diagnostics recorded per trade

- lane
- entry/exit timestamp
- side
- entry/exit executable price
- Q base/context
- spread and spread percentile
- session
- scheduled event phase
- observed stress / event activation
- entry Grid state
- active direction vector L0-L3
- exit reason
- hold milliseconds
- gross price PnL
- commission
- net PnL
- MFE / MAE from executable exit side
- prior loss streak
- event scale(s) emitted on entry tick

## Stage-A metrics

For each lane:

- eligible events
- blocked because already in position
- closed trades
- winners / losers / breakeven
- win rate
- net
- gross profit
- gross loss
- profit factor
- expectancy
- max balance drawdown
- max floating-equity drawdown
- average/median hold
- stop / target / timeout counts
- trade count by session/event phase/state
- loss clustering
- directional asymmetry
- event opportunity retention

Offline diagnostic markouts at 1s/3s/5s/10s/15s/30s may be computed after entry for research interpretation, but they may not enter the causal DB001C trading rule.

## Interpretation gates

### Economically interesting Grid evidence

A lane is interesting if it has:

- positive after-cost expectancy;
- meaningful event/trade count;
- no catastrophic drawdown concentration;
- positive behavior not confined to a single hour or one release cluster.

### Null result

If all Grid-only lanes are negative after cost:

- do not rescue them with RSI;
- determine whether losses are primarily **location/auction** errors, execution friction, direction errors, or lifecycle errors;
- only begin Volume Profile if the unresolved failure is genuinely location/auction related.

### Strong Grid result

If a lane is positive and robust enough to continue:

- freeze its entry semantics;
- run a bounded lifecycle refinement as a new unit;
- later expand chronologically only under DELTA governance.

## Hard failures

Reject any result produced by:

- future MFE/MAE in inference;
- midpoint fills;
- future calendar surprise;
- changing Q after entry to widen the initial stop;
- martingale/adverse add;
- multiple simultaneous lane positions being arithmetically combined;
- tuning parameters on the same result and still calling it preregistered.

## Next-layer rule

Volume Profile does not start because DB001C is complete.

It starts only if Grid economics or diagnostics identify **auction location / accepted-value context** as a material unresolved question.
