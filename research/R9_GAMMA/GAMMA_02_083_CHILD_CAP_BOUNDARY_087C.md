# GAMMA-02 — Exact Child-Cap Boundary 087C

**Status:** MAJOR JANUARY ALL-METRIC CROSSOVER / FULL-TICK EQUITY CERTIFIED  
**Parent:** GAMMA_02_083_GLOBAL_CHILD_CAP_087.md  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

The 640-704 child-cap region was refined to single-slot resolution.

## Exact minimum crossover

| Child cap | Net | Trades | PF | Win | Expectancy | Avg hold | All six metrics? |
|---:|---:|---:|---:|---:|---:|---:|---|
| 701 | +$48,665.98 | 32,810 | 19,545.57 | 99.9025% | +$1.483267 | 14.6036s | NO |
| 702 | +$48,716.20 | 32,836 | 19,565.74 | 99.9025% | +$1.483622 | 14.6028s | NO |
| **703** | **+$48,766.62** | **32,862** | **19,585.99** | **99.9026%** | **+$1.483982** | **14.6021s** | **YES** |
| 704 | +$48,817.85 | 32,889 | 19,606.56 | 99.9027% | +$1.484322 | 14.6009s | YES |

Exact January R9 SYNTH comparator:
- net +$41,520.82
- trades 27,980
- PF 23.7154
- win 87.0908%
- expectancy +$1.483946
- average hold 16.4627s

## Full ordered-tick equity certification — cap 703

- net: **+$48,766.62**
- trades: **32,862**
- PF: **19,585.98795**
- win: **99.902623%**
- expectancy: **+$1.483982107**
- average hold: **14.602091s**
- full-tick equity DD: **$10,348.16**
- peak-relative equity DD: **6.95597%**
- minimum total equity from $100K start: **$99,043.55**
- max open child positions: **703**

Cap 702 misses only the expectancy target. Therefore **703 is the exact minimum global child cap preserving all six January R9 SYNTH headline metrics in this architecture**.

## Scientific caveat

The 083 child population still contains heavy same-market-tick multiplicity across overlapping parent campaigns. This architecture is therefore a child-ticket scaling/pyramiding system, not 32,862 independent unique-tick market opportunities. That distinction remains mandatory in all later reporting.

## Next required units

1. exact $100K / 1:500 XAUUSD margin utilization model for cap 703;
2. freeze January architecture if margin is operationally feasible;
3. chronological February validation with all January parameters frozen;
4. no January retuning after February is opened.

R9 SYNTH remains the hard benchmark.
