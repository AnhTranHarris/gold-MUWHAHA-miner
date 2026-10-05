# DELTA-A R9 Grid — $100 Profit-Ramp Research 01

Status: EXPERIMENTAL / NOT A MILESTONE / AUGUST SEALED / NOT MT5 AUTHORIZED

## Objective
Emulate the useful part of R9 SYNTH's $100 / 0.01-lot behavior without pretending a $100 account can safely carry the research portfolio's hundreds of simultaneous physical positions.

## Core hypothesis
Keep lot size fixed at 0.01 and compound by **unlocking physical position slots and specialist ownership as realized capital grows**. The complete grid engine continues virtually at all times.

## Current staged ignition prototype
The strongest current seed lane uses CORE_H4 virtual opportunities plus causal quality gates and balance-dependent risk:

- balance < $80: require London/NY-overlap AND prior same-side specialist agreement; max loss target ~ $3; 1 slot
- $80 to < $125: London/NY-overlap entries; max loss target ~ $5; 1 slot
- $125 to < $175: prior 10-second same-side specialist confirmation; max loss target ~ $7.50; 1 slot
- $175 to < $200: all eligible CORE_H4; max loss target ~ $10; 1 slot
- $200 to < $250: max loss target ~ $10; up to 2 slots
- $250 to < $350: max loss target ~ $15; up to 2 slots
- $350 to < $500: max loss target ~ $20; up to 3 slots
- at $500: hand off to the preserved $500 capital adapter

Scheduled trading-gap protection remains active.

## Measured research behavior
On the historical February-start path, the staged seed reached about $530 from $100 after 97 physical trades in approximately 10.7 calendar days, while keeping realized balance at or above the starting $100 during that particular path.

Across rolling active-day starts rather than choosing the favorable February start:
- about 78% reached $500 within a 90-day window
- about 14% dipped below $60 before reaching $500
- about 1.9% fell below $30
- median successful time to $500 was about 13.1 days

This is promising but not robust enough for a $100 milestone.

## Findings
1. Fixed 0.01 lot is not the principal constraint. Physical concurrency and tail-loss control are.
2. Tight universal stops damage expectancy; balance-dependent stops behave better.
3. Consensus/session gating improves survival but can starve the account if used permanently.
4. The likely R9-like compounding mechanism is **slot compounding**: 1 physical 0.01 slot at seed capital, then more 0.01 slots as realized balance grows.
5. A fresh live EA should pre-warm its virtual state from prior broker history so the account can use mature specialist logic without waiting weeks in real time.

## Next research
Improve the seed lane's rolling-start survival toward >=95% before promotion. Candidate mechanisms:
- capital-floor ratchet with defensive/rescue mode,
- specialist priority queue when a slot becomes free,
- selective rejected-trade recovery specialist,
- conservative slot unlock based on both balance and free-margin reserve,
- state pre-warm parity on MT5.
