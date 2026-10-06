# GRID-001 January Phase Sandwich Stack 001

**Status:** COMPLETE / POSITIVE STABLE FLOOR / 50% BREAKTHROUGH GATE NOT MET

## Purpose

This is the first honest vertical sandwich assembly of the multi-timeframe / market-phase category.

It combines only mechanisms that had already survived their own frozen January tests:

- A05 volatility-expansion continuation route at ATR14/ATR240 >= 2.00;
- A05 15m opposed + extended -> child continuation;
- A10 15m aligned + extended -> child continuation;
- A10 5m opposed + mature -> parent reclaim;
- A15 15m aligned + extended -> child continuation;
- A15 15m opposed + mature -> parent reclaim.

No new thresholds were introduced in this stack.

A single grid-system owner was enforced:
- one physical 0.01 position maximum;
- overlapping candidates suppressed;
- volatility-expansion route gets first priority, then A15, A10, A05.

## Combined January result

Pre-owner candidates: **1,836**

Suppressed by system ownership: **608**

Accepted trades: **1,228**

Trade velocity: **64.63 trades / active day**

Economics:
- net: **+$315.39**
- gross profit: **+$2,865.84**
- gross loss: **-$2,550.45**
- PF: **1.1237**
- expected payoff: **+$0.2568**
- win rate: **51.06%**

Chronology:

Discovery:
- 444 trades
- **+$57.62**
- PF **1.1231**
- expected payoff **+$0.1298**

Validation:
- 784 trades
- **+$257.77**
- PF **1.1238**
- expected payoff **+$0.3288**

Risk:
- max balance drawdown: **$125.65**
- max equity drawdown: **$135.63**
- minimum equity delta: **-$12.34**

Theoretical small-account diagnostic:
- $100 start minimum equity: **$87.66**
- $200 start: **$187.66**
- $300 start: **$287.66**

All remain positive on the frozen research surface.

## Route contribution after ownership collisions

- Volatility expansion: **+$170.15**
- A05 15m opposed extended child route: **+$54.88**
- A10 15m aligned extended child route: **+$3.68**
- A10 5m opposed mature reclaim: **+$7.77**
- A15 15m aligned extended child route: **+$49.18**
- A15 15m opposed mature reclaim: **+$29.73**

This confirms that the routes can coexist under one owner without destroying the combined economics.

## R9 REAL January breakthrough check

Canonical R9 REAL January net loss:
**-$6,651.62**

Requested halfway recovery target:
**+$3,325.81**

This sandwich contributes:
**+$315.39**

Additive overlay contribution proxy:
**4.74% of the full R9 REAL January net loss**

Progress toward the requested 50%-recovery target:
**9.48%**

Additive proxy remaining R9 REAL January net:
**-$6,336.23**

This is explicitly a contribution proxy. The standalone grid stack has not yet been mapped onto the actual R9 REAL trade entries, so it cannot honestly claim to have directly removed R9 REAL gross loss or drawdown.

## Verdict

This category is **useful but insufficient**.

What it accomplished:
- converted the original physical grid into a positive, bounded, single-owner opportunity layer;
- preserved positive economics in both chronological January partitions;
- produced low drawdown and positive $100-equity diagnostics;
- established that direction × timeframe × phase changes opportunity ownership;
- created several reusable routes for the future 6–16 specialist architecture.

What it did **not** accomplish:
- anything close to the requested 50%-ish R9 REAL January bridge;
- enough velocity or profit contribution to justify further micro-tuning of these leaves.

Therefore this category should now be frozen as the new sandwich floor.

## Next high-leverage category

The next attack should use the new grid state engine **on the actual R9 REAL January trade stream**.

Why:

R9 REAL January already contains **31,915 trades** and **-$10,436.90 gross loss**. A standalone sparse overlay can only add modest profit. To move a 50%-ish weakness metric, the grid needs to become a system-wide context/routing layer that can:

- tag each R9 REAL entry with nested timeframe state and phase;
- identify parent-opposed / hostile / transition trade families;
- veto or defer demonstrably bad entries;
- reroute recoverable wrong-direction events;
- preserve good R9 REAL opportunities.

That would let us measure a **true direct gross-loss reduction** rather than an additive proxy.

No retuning of the current phase sandwich is recommended before that mapping.

August remains sealed. Main `delta` remains read-only. MQL5 remains unauthorized.
