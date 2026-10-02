# DELTA 005J-001 — State-Conditioned Initial Protection

**Status:** COMPLETE — NOT PROMOTED  
**Mode:** historical Python simulation  
**Focus:** Entry + Initial-Hold  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Stage-A ticks:** 4,205,709  
**Variants:** 54  
**August:** not accessed

## Purpose

005J combined the two strongest earlier findings:
- 005E: accepted post-break consolidation predicts short-horizon survival;
- 005H: looser early trailing materially improves first-seconds survival.

Every trade received a 1-second observation grace. Trades classified as accepted-consolidation then received temporarily looser trail activation; all other trades immediately reverted to baseline R9 protection.

## Best net cell

Range ceiling $1.00, minimum boundary acceptance $0.00, accepted-state activation $0.30, protection end 10 seconds:

- 16,736 trades
- 7,031 winners
- 5,601 accepted classifications
- accepted-state final win rate 42.69%
- nonaccepted final win rate 49.61%
- gross profit $1,817.69
- gross loss -$5,560.58
- net -$3,742.89
- max balance drawdown $3,743.87
- average hold 7.41 seconds
- winner retention 95.65%
- net-loss improvement 0.67%
- gross-loss deterioration 4.07%
- +4.54pp 5s survival
- +5.01pp 10s survival
- +1.63pp 15s survival

## Precision improvement versus global loosening

State conditioning is materially less destructive than applying loose protection to all trades.

For comparison, DELTA_005H's global $0.30 activation produced roughly +11pp 5s/+10.7pp 10s survival but retained only 83.4% of winners.

005J obtains a smaller but cleaner persistence gain while retaining ~95.6% of winners.

Therefore conditioning protection on causal state has value.

## Critical limitation

The best net improvement is only 0.67%, far below the project's +10 percentage-point creative-escalation threshold.

Across the matrices, accepted-consolidation positions end with final win rates around 41–46%, while nonaccepted positions remain around 49–50%.

This means accepted consolidation is strongly associated with **survival**, but under the unchanged downstream lifecycle it is not synonymous with final profitability.

## Formula-level diagnosis

High leverage:
- broad $1.00 state ceiling;
- longer 10-second conditional protection.

Low leverage:
- $0 vs $0.05 boundary-acceptance buffer.

Trade-off:
- higher accepted-state activation increases survival but lowers accepted-state final win rate.

The next research question should not be "which 005J threshold is best?"

It should be:

**Which causal states specifically benefit from looser protection relative to baseline protection, on the same original entry?**

## Next unit

DELTA_005K — Protection-Benefit Forensic Differential.

005K will pair each original entry under:
1. baseline R9 early protection; and
2. a fixed looser-protection treatment.

It will then analyze causal entry/early-horizon state against the paired treatment effect, using treatment benefit only as a retrospective label.

No future treatment outcome may enter candidate features.

Temporary matrix workbook:
https://docs.google.com/spreadsheets/d/1-JbrciPz3J0yeZhZwo9ZPdMOQMPAAuNtKm4Q8doNi8c/edit?usp=drivesdk

Holding-Trade + Exit + High-Profit remains deferred.
