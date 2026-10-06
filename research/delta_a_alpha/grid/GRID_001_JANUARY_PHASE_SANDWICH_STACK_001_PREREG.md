# GRID-001 January Phase Sandwich Stack 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_PHASE_SANDWICH_STACK_001`  
**Status:** FROZEN BEFORE COMPUTE  
**Purpose:** first vertical sandwich assembly for the multi-timeframe / market-phase category

## Frozen components

### R0 — Volatility Expansion Route

Use the already-frozen A05 expansion route at:

`ATR14 / ATR240 >= 2.00`

Unchanged:
- 1-gap proof within 3 seconds;
- 1.5-gap target;
- original-event-midpoint stop;
- original five-minute horizon;
- fixed 0.01.

This is the highest-confidence January expansion variant and is not retuned.

### R1 — A05 15m opposed + extended

Ownership:
- parent owner = 15m;
- parent direction opposes child event;
- parent age >= 7 strong 15m bars.

Action:
- child continuation proof-before-entry trade.

Interpretation:
- extended parent may be exhausting and losing authority.

### R2 — A10 15m aligned + extended

Action:
- child continuation proof-before-entry trade.

### R3 — A10 5m opposed + mature

Ownership:
- parent owner = 5m;
- parent opposes child;
- age 3–6 strong 5m bars.

Action:
- frozen parent-reclaim route.

### R4 — A15 15m aligned + extended

Action:
- child continuation proof-before-entry trade.

### R5 — A15 15m opposed + mature

Action:
- frozen parent-reclaim route.

These phase routes were selected because they were positive in both the chronological January discovery and validation partitions during Trend Phase 001.

No other phase leaf is allowed in this unit.

## Single grid-system owner

The combined grid layer may hold at most **one physical 0.01 trade at a time**.

Candidate priority when entry timestamps collide:

1. R0 volatility expansion
2. A15 phase routes
3. A10 phase routes
4. A05 phase route

Otherwise candidates are processed chronologically.

Any candidate born while the grid-system owner is active is suppressed.

## Required metrics

### Component level

For every route:
- pre-owner candidates;
- accepted trades;
- suppressed trades;
- net contribution after system ownership.

### Combined sandwich

- trades;
- trades/active day;
- net;
- gross profit;
- gross loss;
- PF;
- expectancy;
- win rate;
- discovery / validation;
- max balance drawdown;
- max equity drawdown;
- minimum equity delta;
- $100 / $200 / $300 positive-equity diagnostic.

## R9 REAL January bridge accounting

Canonical R9 REAL January:
- net = -$6,651.62
- gross loss = -$10,436.90
- balance DD = $6,659.15

For this overlay-style grid research, report:

`net_loss_recovery_pct = sandwich_net / 6651.62 * 100`

and:

`remaining_R9_real_net_if_additive = -6651.62 + sandwich_net`

This is explicitly a **contribution proxy**, not a historical rewrite of R9 REAL trades.

The category meets the requested 50%-ish net breakthrough only if:

`sandwich_net >= $3,325.81`

No claim of direct R9 gross-loss reduction is allowed until the grid context is actually mapped onto R9 REAL trade entries.

## Advancement

If the stack is positive in discovery and validation but remains far below the 50% R9 bridge target:
- preserve it as the new sandwich floor;
- declare this category useful but insufficient;
- move to the next structural category in a later unit rather than micro-tuning these leaves.

If it fails when combined:
- preserve the individual candidates;
- diagnose ownership collisions before changing routes.

August sealed. Main `delta` read-only. MQL5 unauthorized.
