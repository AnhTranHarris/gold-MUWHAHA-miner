# GRID-001-S — Stage-A Bounded Screen 01

**Unit:** `DAA_GRID_001_BOUNDED_STAGE_A_SCREEN_01`  
**Status:** COMPLETE / NEGATIVE  
**Surface:** `DUKAS_COINEXX_LIKE_P75`  
**Lot:** fixed 0.01 only  
**Martingale:** prohibited / not used  
**Window:** frozen DELTA Stage-A

## Question

Can the tutorial's physical grid inventory remain useful when unlimited averaging is removed and every trade has a hard loss bound?

## Frozen matrix

Inventory cap per direction: 1, 2, 4.  
Hard stop: 1.5, 2, 3, 4 grid gaps.  
Grid gap and TP: $1.00.  
Total preregistered variants: 12.

No other parameter was changed.

## Result

**All 12 variants lost money. No variant achieved PF > 1.**

Best net result:
- cap: **1 position per direction**
- stop: **4 grid gaps / $4.00**
- trades: **10,103**
- win rate: **74.78%**
- net: **-$2,301.82**
- gross profit: **$8,241.14**
- gross loss: **-$10,542.96**
- PF: **0.7817**
- expected payoff: **-$0.2278/trade**
- trade velocity: **1,010.3 trades/active day**
- max equity drawdown: **$2,301.82**
- maximum open inventory: **2 positions / 0.02 lot**
- forced boundary closes: **2**

The other variants were worse, with net losses from roughly **-$3.1K to -$7.9K** and PF values around **0.71–0.81**.

## Small-account result

Every variant failed the requested $100/$200/$300 theoretical positive-equity test. Even the least-bad configuration produced a minimum equity delta of approximately **-$2,301.82**.

This is an equity-path diagnostic. Broker margin would make the practical constraint stricter, not easier.

## Comparison with forensic source lane

The source-style no-stop forensic replay produced:
- ~98.87% closed win rate,
- +$3,755.85 net,
- but ~$20,077.56 max equity drawdown,
- 250 simultaneous positions,
- and catastrophic $100/$200/$300 survivability.

The bounded screen removes that hidden tail, but once losses are realized instead of being warehoused indefinitely, expectancy becomes negative across the entire preregistered matrix.

That is strong evidence that the tutorial's **physical averaging inventory is not the transferable edge**.

## What survives

The useful feature is still the opportunity clock:
- the source grid generated very high event density;
- bounded variants also retain substantial trade density;
- but trading every physical grid event as contrarian inventory is negative expectancy.

## Decision

**Retire physical grid inventory from Delta-A-alpha.**

Do not spend further research budget tuning inventory caps or widening source-style stops.

Advance only this component:

**GRID EVENT CLOCK → SINGLE-TRADE BOUNDED OWNERSHIP**

The next lane should treat grid crossings as high-frequency event candidates, then determine whether short-horizon causal context can decide:
- mean-reversion trade,
- continuation trade,
- or no trade.

That preserves the potential velocity contribution while eliminating the mechanism that created both the original tail risk and the bounded-screen losses.

August remains sealed. Main `delta` remains untouched. MQL5 remains unauthorized.
