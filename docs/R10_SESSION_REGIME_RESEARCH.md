# R10 Session-Regime Research Evidence

## Status
Research / MT5 certification candidate. R9 remains the validated control until MT5 Every Tick Based on Real Ticks evidence exists for R10.

## Objective
Preserve R9's superior loss profile while recovering enough profitable participation to meet or exceed the R5 Jan-Aug 2026 net-profit benchmark.

Historical MT5 controls:
- R5 net: 366,320.15; gross loss: -21,861.68
- R9 net: 333,979.46; gross loss: -18,339.05

R9 therefore needs roughly +9.68% net while keeping loss around or below its current envelope.

## Method
- 12 random paired Dukascopy S1 BID/ASK dates were replayed with Coinexx-like spread assumptions.
- 9 Apr-Aug dates overlap the Coinexx M1 master and were used for profile development / cross-resolution comparison.
- Sep 1, Sep 8 and Sep 15 remained external random holdouts.
- The S1 simulator uses only completed one-second information before entry.
- Candidate robustness was tested across three plausible intra-second OHLC orderings and friction from 0.04 through 0.10.
- Five Coinexx server-time blocks were searched independently, then replayed together as one monolithic causal strategy.
- Leave-one-development-day-out reselection was used as an additional robustness check.

## Selected internal profiles

### 00:00-06:59 Coinexx server time
- gap 20
- stop 35
- trail 5
- activation 6
- max rearms 4
- max hold 20 sec
- 10 sec velocity/range lookback
- min velocity 2
- directional efficiency >= 0.65
- min range 75
- max turns 99

### 07:00-11:59
- gap 15
- stop 35
- trail 5
- activation 25
- max rearms 7
- max hold 20 sec
- min velocity 0
- efficiency >= 0.70
- min range 75
- max turns 99

### 12:00-15:59
- gap 15
- stop 35
- trail 10
- activation 6
- max rearms 3
- max hold 35 sec
- min velocity 2
- efficiency >= 0.65
- min range 75
- max turns 7

### 16:00-20:59
Same profile as 07:00-11:59.

### 21:00-23:59
- gap 15
- stop 28
- trail 8
- activation 25
- max rearms 2
- max hold 15 sec
- min velocity 18
- efficiency >= 0.65
- min range 60
- max turns 12

## Direct S1 results
R9 control over the 9 Coinexx-overlap dates:
- net 7,394.889
- gross profit 8,020.509
- gross loss -625.620
- trades 13,026

R10 candidate over the same 9 dates:
- net 8,431.849
- gross profit 9,017.974
- gross loss -586.125
- trades 12,599

Change vs R9 S1 control:
- net +14.02%
- gross profit +12.44%
- absolute gross loss -6.31%
- fewer trades, indicating quality/geometry improvement rather than indiscriminate participation growth

All 9 development days improved.

External September holdouts also improved:
- Sep 1: 868.561 -> 956.156
- Sep 8: 782.475 -> 857.095
- Sep 15: 569.814 -> 686.130

All 12 random dates remained positive.

## Stress results
Across 3 intra-second path assumptions x friction 0.04/0.06/0.08/0.10:
- all 12 random dates remained profitable in every tested combination
- normal path / 0.04 friction: dev9 net 8,431.849, GP 9,017.974, GL -586.125; Sep3 net 2,499.381
- harsh high-first / 0.10 friction: dev9 net 7,423.778; Sep3 net 2,206.557; worst individual day 566.513
- harsh low-first / 0.10 friction: dev9 net 7,415.855; Sep3 net 2,207.891; worst individual day 566.392

## Leave-one-day-out
For each of the 9 Apr-Aug development dates, profiles were reselected using the other eight dates and then tested on the omitted date. Every omitted day outperformed the R9 S1 control. Aggregate held-out uplift was about +12.9%. Sep 1/8/15 remained positive under every leave-one-day-out selected profile set.

## Cross-resolution relationship
R10 S1 daily net versus R5 M1 same-day proxy:
- Pearson approximately 0.986
- Spearman approximately 0.983

This is slightly below R9's approximately 0.994 Pearson correlation, but remains extremely strong while adding materially more net and less modeled loss.

The S1 layer is used as a market-state / parameter-selection laboratory, not an exact tick-level P&L emulator. One-second OHLC cannot reproduce MT5's true intra-second tick sequence.

## Full Jan-Aug M1 structural capacity check
The deterministic full Jan-Aug Coinexx M1 R5 proxy remains approximately:
- net 382,944
- GP 401,665
- GL -18,721

The S1 gate cannot be literally replayed on M1 bars without inventing sub-minute ordering. The correct cross-resolution use is to verify that the R10 candidate remains inside the M1 opportunity envelope and retains same-date correlation.

## MT5 translation estimate — NOT certification
Using observed R9 S1-to-MT5 scaling only as a translation estimate:
- projected R10 net: approximately 380,812
- projected GP: approximately 396,134
- projected GL: approximately -17,181

This would exceed the R5 net benchmark and improve on R9 gross loss, but it is explicitly a projection. MT5 Every Tick Based on Real Ticks is the final authority.

## Engineering changes in R10
- R9 M5 ATR/session/spread gate retained.
- S1 bars still built internally from live/tester ticks; no S1 chart period required.
- Execution geometry and S1 gate thresholds are selected internally by Coinexx server-time block.
- Profiles are hard-coded rather than exposed as external tester inputs, preventing accidental preset corruption such as the R9_1 test.
- Trade-open profile is frozen for that position so a time-block change cannot mutate its stop/trailing/hold behavior mid-trade.
- Minute-cycle handling is hardened: if a position survives into a new minute, its old boundary is not incorrectly rearmed after exit.

## Promotion gate
Do not merge or demo-forward R10 until:
1. it compiles with zero errors;
2. Jan-Aug 2026 XAUUSD M1 / Every Tick Based on Real Ticks materially exceeds R9;
3. preferred target: net > R5 366,320 while GL <= R9 18,339 in magnitude;
4. if only one major target is met, evaluate PF/DD/Sharpe and random-date evidence before proceeding;
5. exact random S1 dates may be rerun in MT5 for cross-resolution diagnostics if the full test behaves unexpectedly.
