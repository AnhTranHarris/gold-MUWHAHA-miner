# 08 — State-Stability Gross-Loss Filter

**Status:** validated research filter; not yet integrated into the authoritative EA.

## Breakthrough

Ranking auction states by headline total profit was inferior to ranking them by **worst monthly profit factor during Jan-Apr**.

Keeping the two most stable states at each temporal scale produced on untouched May-Jul:

All states:
- net ≈ +$9,846
- gross loss ≈ -$176,552
- July ≈ -$2,102

Stability-ranked:
- net ≈ +$6,764
- gross loss ≈ -$69,489
- July ≈ +$193

This retained about 69% of forward profit while eliminating roughly **60.6% of gross loss** and changed July from negative to positive.

## Rule

For each scale/state combination:
1. compute monthly PF on development months;
2. take the **minimum monthly PF** as the stability score;
3. rank states by this floor, not total P&L;
4. allocate only to the most stable states or reduce capital priority to weak states.

## Principle

Optimize the **monthly floor of the state**, not the headline backtest total.

This is a capital-priority mechanism, not a global trade/no-trade regime switch.
