# GRID-001-F — Stage-A Forensic Baseline

**Unit:** `DAA_GRID_001_CAUSAL_FORENSIC_BASELINE`  
**Status:** COMPLETE / PHYSICAL SOURCE GRID REJECTED  
**Window:** frozen DELTA Stage-A, Jan 1 through Jan 18 12:00 UTC exclusive  
**Surface:** `DUKAS_COINEXX_LIKE_P75`  
**Lot:** fixed 0.01  
**Martingale:** prohibited / not used  
**Promotion eligibility:** none; forensic lane only

## Source mechanics replayed

The tutorial was reconstructed as a rolling-extreme contrarian inventory grid:
- H1 Bid bars;
- 48-bar source window;
- source-style bar cache refreshed at the first tick of each hour;
- current Ask used for both BUY/SELL signal comparisons;
- first BUY one $1.00 grid gap below cached rolling high;
- first SELL one $1.00 grid gap above cached rolling low;
- subsequent same-side entries chained from the latest still-open same-side entry;
- BUY fill at Ask, SELL fill at Bid;
- one-grid take profit;
- no stop in the forensic lane;
- $0.01 entry + $0.01 exit commission;
- all residual positions forcibly liquidated at the Stage-A boundary.

Source file SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

## Result

- Ticks: **4,205,709**
- Trades: **20,678**
- Normal TP closes: **20,444**
- Forced-liquidation closes: **234**
- Closed win rate after commission: **98.87%**
- Net: **+$3,755.85**
- Gross profit: **+$22,372.66**
- Gross loss: **-$18,616.81**
- Profit factor: **1.2017**
- Expected payoff: **+$0.1816/trade**
- Trade velocity: **2,067.8 trades/active day**
- Max balance drawdown: **$18,614.47**
- Max equity drawdown: **$20,077.56**
- Minimum equity delta from starting balance: **-$14,216.41**
- Maximum simultaneous positions: **250**
- Maximum total lots: **2.50**
- Average hold: **6,924 sec**
- Maximum hold: **725,692 sec**
- Inventory episodes: **1**
- Continuous inventory episode: **943,199 sec (~10.9 days)**
- Worst portfolio floating MAE in that episode: **-$28,261.71**

## Small-account gate

Even before applying broker margin limits, the unconstrained equity path fails all requested realistic starting balances:

- $100 start: minimum theoretical equity **-$14,116.41** — FAIL
- $200 start: minimum theoretical equity **-$14,016.41** — FAIL
- $300 start: minimum theoretical equity **-$13,916.41** — FAIL

A real broker would constrain or liquidate the system much earlier because 250 simultaneous 0.01 XAUUSD positions are not remotely compatible with these balances.

## Interpretation

The source tutorial's headline-style win rate is reproduced: virtually every normally closed trade wins because losing inventory is allowed to remain open. The end-of-window liquidation exposes the hidden economic tail. Only 1.13% of trades required forced liquidation, yet that small unresolved tail generated enough loss to reduce a gross-profit stream above $22K to only $3.76K net while producing a ~$20K equity drawdown.

Therefore **win rate is not the edge**.

The physical source grid is rejected as a specialist because its risk geometry violates the fixed-0.01 small-account survivability objective even without Martingale.

However, one component remains scientifically useful: **event density**. At ~2,068 trades/active day, the grid clock produces opportunity density above the R9 SYNTH Jan benchmark (~1,332 trades/day) and above the Jan-Jul R9 SYNTH average (~1,472/day). That supports the owner's original hypothesis that grid structure may be useful as a high-throughput specialist/event clock if physical averaging inventory is removed.

## Decision

**REJECT:** source-style physical grid inventory.  
**RETAIN:** grid crossing/event-clock mechanism for bounded specialist research.

The next experiment must preserve fixed 0.01 size, remove unlimited inventory dependence, hard-bound risk, and evaluate whether the grid event clock can harvest causal micro-reversion/continuation without requiring positions to survive indefinitely.
