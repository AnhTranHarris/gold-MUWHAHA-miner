# GRID-001 R9 REAL January Gross-Loss Concentration 001 — Preregistration

**Unit:** `DAA_GRID_001_R9_REAL_JAN_GROSS_LOSS_CONCENTRATION_001`  
**Status:** FROZEN BEFORE ANALYSIS

## Question

Do the already-frozen Delta-A-alpha multi-timeframe/grid states concentrate enough of the **actual R9 REAL January gross loss** to justify a later causal veto/defer/reroute experiment?

## Canonical denominator

R9 REAL January:
- 31,915 trades
- net: -$6,651.62
- gross profit: +$3,785.28
- gross loss: -$10,436.90
- PF: 0.362682

Soft preferred breakthrough scale:
- 20% gross-loss share = **$2,087.38**
- 20% net-loss improvement = **$1,330.32**

## Important accounting rule

Family accounting uses MT5 deal cashflows exactly.

If a hypothetical family were vetoed:
- its entry commission disappears;
- its exit commission/swap/profit disappears;
- family gross-profit loss and gross-loss reduction must both be reported.

A family is not useful merely because it contains many losers.

## Frozen families to inspect

No learned model and no threshold optimization.

### F1 — nested owner relation
- ALIGNED
- OPPOSED
- CONFLICT
- NEUTRAL

### F2 — owner timeframe × relation
- 5m/15m × ALIGNED/OPPOSED
- conflict and neutral remain separate.

### F3 — owner timeframe × relation × phase
Phase bins already frozen:
- EARLY = 1–2 strong completed bars
- MATURE = 3–6
- EXTENDED = 7+

### F4 — volatility-expansion state
Using completed-M1 ATR14/ATR240:
- <1.00
- 1.00–1.75
- 1.75–2.00
- >=2.00

### F5 — latest adaptive-grid event relation
For A05, A10, A15 independently:
- latest virtual event ALIGNED with R9 trade
- latest virtual event OPPOSED to R9 trade

Event-age bins are frozen:
- <5 sec
- 5–30 sec
- 30–120 sec
- >=120 sec

### F6 — lattice consensus
Across A05/A10/A15 latest-event relation:
- all aligned
- all opposed
- mixed

### F7 — preregistered nested combinations
Only:
- owner OPPOSED × phase
- owner OPPOSED × volatility state
- owner OPPOSED × lattice consensus
- owner ALIGNED × phase
- owner ALIGNED × volatility state

No post-hoc arbitrary conjunctions are allowed in this unit.

## Metrics for every family

- trades and trade share
- net cashflow
- MT5 deal-level gross profit
- MT5 deal-level gross loss
- PF
- gross-loss share of canonical January
- gross-profit share of canonical January
- net-loss share
- hypothetical full-veto net improvement
- trades removed
- discovery and validation versions

## Candidate gate

A family is **large enough to matter** if:
- it contains at least 20% of canonical gross loss, OR
- its hypothetical veto improves net by at least 20% of canonical January net loss,

AND:
- it is net-negative in both discovery and validation;
- gross-loss share materially exceeds gross-profit share;
- it is causally knowable at entry.

A family below the 20% scale may still be retained as a sandwich layer, but it is not the requested hard-category breakthrough.

## Anti-cheating rule

This unit measures concentration only.

It does **not** claim a real improvement from perfect vetoing. Any family that passes must face a separate intervention test:
- VETO,
- DEFER,
- or REROUTE,
with preserved opportunity/recovery behavior.

No session/news/macroeconomic categories yet.
No new indicators.
No MQL5.

August sealed. Main `delta` read-only. Fixed 0.01. No Martingale.
