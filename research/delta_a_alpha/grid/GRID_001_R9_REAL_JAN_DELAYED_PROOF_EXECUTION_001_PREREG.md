# GRID-001 R9 REAL January Delayed Proof Execution 001 — Preregistration

**Unit:** `DAA_GRID_001_R9_REAL_JAN_DELAYED_PROOF_EXECUTION_001`  
**Status:** FROZEN BEFORE COMPUTE

## Purpose

Convert the 652-signal proof-admission retention breakthrough into executable counterfactual economics.

This unit uses exactly the same A15 proof decisions as Retention 001.

No signal is added or removed by a new rule.

## Frozen admitted set

Recompute the parent gate exactly:
- A15 adaptive gap;
- +0.25 gap favorable proof;
- -0.50 gap adverse failure;
- decision deadline = earlier of original R9 exit or 5 minutes.

Only PROOF signals can trade.

## Actual delayed entry

At the causal proof tick:
- BUY enters at modeled P75 Ask;
- SELL enters at modeled P75 Bid.

This is the first physical price used by this counterfactual route.

## Frozen exit

Exit at the original R9 report lifecycle endpoint:

`exit_utc = original_entry_utc + original_hold_seconds`

Map that timestamp to the nearest January Dukascopy tick.

Executable exit:
- BUY exits at Bid;
- SELL exits at Ask.

No TP, SL, trailing stop, recovery, or horizon extension is introduced.

If mapped exit is not strictly later than proof entry, the trade is rejected as non-executable and reported separately.

## Economics

For each delayed trade:

`price_pnl = side * (exit_quote - proof_entry_quote)`

At fixed 0.01 XAUUSD, $1 price movement = approximately $1 PnL under the frozen research convention.

Subtract:
- $0.02 round-trip commission.

No swap is expected over these original short R9 lifecycles.

## Required comparisons

For the same frozen PROOF set report:

1. original R9 retained cashflow proxy;
2. P75 immediate-entry / original-exit economics;
3. P75 delayed-proof-entry / original-exit economics.

Full January, discovery, validation:
- trades;
- net;
- gross profit;
- gross loss;
- PF;
- expectancy;
- win rate.

Also:
- proof-to-exit remaining lifetime;
- immediate-to-proof opportunity consumed;
- max balance drawdown;
- max equity drawdown;
- minimum equity delta;
- theoretical $100/$200/$300 positive-equity diagnostic;
- maximum concurrent delayed positions.

## Candidate gate

The delayed route becomes a January candidate mechanism only if:

- delayed net > 0;
- delayed PF > 1;
- discovery and validation both remain non-negative or qualitatively positive;
- drawdown remains compatible with the $100 diagnostic;
- no hidden multi-position inventory is required.

Velocity is expected to be sparse and must be reported honestly.

This route is allowed to be a premium channel inside the multi-specialist system; it does not need to replace R9 velocity.

## Prohibitions

- no proof-distance tuning;
- no A05/A10 comparison;
- no changed exit target;
- no state-specific rules;
- no recovery;
- no session/news filters;
- no MQL5.

August sealed. Main `delta` read-only. Fixed 0.01. No Martingale.
