# DELTA R037 — Displacement-Qualified Session Sweep Harvest — Checkpoint 17DA–17DD

**Status:** COMPLETE / NO STAGE-A SURVIVOR  
**August:** SEALED · **MQL5:** NOT AUTHORIZED

Source-default session sweeps were qualified with ATR(14), minimum candle range 1.5×ATR, and body/range ≥0.5. The Bayesian layer was not imported.

| Lane | Trades | Days | Wins | Net |
|---|---:|---:|---:|---:|
| Wick M1 | 26 | 11 | 10 | -$7.87 |
| Wick M5 | 18 | 9 | 6 | -$4.68 |
| Failed-close M1 | 20 | 10 | 11 | -$3.21 |
| Failed-close M5 | 12 | 7 | 5 | -$2.42 |

All four fail direct economics under frozen 30-second execution. The closest lane still loses, so no ATR/body/session rescue is allowed.

**Decision:** retire unchanged; harvest a genuinely different entry-confirmation family.
