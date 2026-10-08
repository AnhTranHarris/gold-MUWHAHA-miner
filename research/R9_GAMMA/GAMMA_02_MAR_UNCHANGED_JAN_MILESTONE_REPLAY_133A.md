# GAMMA-02 — March Unchanged January-Milestone Replay 133A

**Status:** COMPLETE / BASELINE ONLY / NO MARCH TUNING  
**January fallback:** `carson/r9-gamma-02-jan-grid-milestone` remains untouched  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Objective
Replay the frozen January milestone unchanged on March 2026 Dukascopy ticks and judge it against exact March R9 SYNTH daily, weekly, and monthly performance. No March-specific parameter search, rule selection, or calendar-date logic is permitted.

## Exact March R9 SYNTH benchmark

- net: **75698.63**
- trades: **40985**
- gross loss: **-2024.8600000000001**
- PF: **38.38462412216153**
- win rate: **0.9001097962669269**
- expectancy: **1.8469837745516653**
- average hold: **15.861754300353788**
- closed-trade balance DD: **2.6199999999953434**

## Primary unchanged transfer — L35/C703

- net: **13470.65**
- trades: **17501**
- gross_loss: **-21417.16**
- pf: **1.6289652783095423**
- win: **0.8662362150734244**
- expectancy: **0.7697074452888406**
- balance_dd: **5192.829999999994**
- equity_dd: **10483.500000000131**
- maxopen: **512**
- positive_days: **6**
- beat_days: **3**
- positive_weeks: **3**
- beat_weeks: **0**
- net capture vs R9 SYNTH: **17.80%**
- trade capture vs R9 SYNTH: **42.70%**
- expectancy capture vs R9 SYNTH: **41.67%**
- gross-loss multiple vs R9 SYNTH: **10.58x**

## Week-by-week
| Week | R9 SYNTH | Candidate | Capture |
|---|---:|---:|---:|
| 2026-W10 | $18,489.39 | $-4,466.67 | -24.2% |
| 2026-W11 | $11,485.84 | $9,761.34 | 85.0% |
| 2026-W12 | $14,990.78 | $-2,450.99 | -16.3% |
| 2026-W13 | $24,526.28 | $8,011.79 | 32.7% |
| 2026-W14 | $6,206.34 | $2,615.18 | 42.1% |

## Component attribution
| Sleeve | Net | Trades | Gross loss | PF | Win |
|---|---:|---:|---:|---:|---:|
| WATCHDOG | $3,517.95 | 15,096 | $-17,204.64 | 1.204 | 90.43% |
| COVERAGE | $9,558.58 | 1,988 | $-3,028.19 | 4.157 | 65.79% |
| COLD64 | $808.05 | 64 | $0.00 | 999.000 | 100.00% |
| ASIA02_CONT | $0.00 | 0 | $0.00 | 999.000 | 0.00% |
| LONDON10_ROTATE_LONG | $-401.46 | 354 | $-1,184.33 | 0.661 | 38.70% |
| OVERLAP13_SHORT | $0.00 | 0 | $0.00 | 999.000 | 0.00% |
| LATE21_LONG | $0.00 | 0 | $0.00 | 999.000 | 0.00% |

## Interpretation
March is the first clear evidence that the January milestone is not yet an unknown-state universal architecture. It remains net positive, but captures only ~17.8% of March R9 SYNTH net and ~42.7% of its trade velocity. Only 6/22 R9-SYNTH trading days are positive and 3/5 weeks are positive.

Watchdog itself remains positive but weak (~+$3.5K, PF ~1.20). The earlier-session causal coverage sleeve remains the strongest transferable component (~+$9.6K, PF ~4.16). London10 becomes negative, while the frozen Asia02, overlap13, and late21 January cells are dormant.

This makes February + March highly informative: the missing layer is not a month switch. It is a causal online learner/meta-router that can shadow candidate specialists, update evidence only after outcomes are realized, promote/demote physical execution with hysteresis, and keep bounded exploration so unseen regimes can be discovered without risking the funded account.

## Next scientific question
Use February as the first unseen learning month and March as an out-of-sample validation month for a bounded online specialist-learning/meta-router. The learner must not use month/day labels, future P/L, unfinished bars, or retrospective schedule selection. January fallback remains frozen.
