# GAMMA-02 — NY17 Subphase Lifecycle 001

**Status:** MAJOR JANUARY DISCOVERY FRONTIER — CONTINUOUS CHRONOLOGY  
**Predecessor:** GAMMA_02_NY_CAMPAIGN_INVENTORY_PORTFOLIO_001.md  
**August:** SEALED

## Why this mutation exists

The 17:00 UTC campaign contained 12,459 causal exact-signature extension opportunities, but one universal TP/SL/hold geometry was suppressing large parts of the payoff distribution.

The hour was decomposed into six causal 10-minute subphases and each subphase was allowed its own fixed lifecycle. No future feature is used at entry; the subphase is known from current UTC time.

## 17:00 subphase map

| UTC subphase | TP | SL | Max hold |
|---|---:|---:|---:|
| 17:00-17:09 | $80 | $40 | 30m |
| 17:10-17:19 | $80 | $40 | 30m |
| 17:20-17:29 | $120 | $60 | 30m |
| 17:30-17:39 | $80 | $40 | 30m |
| 17:40-17:49 | no fixed TP | $60 | 30m |
| 17:50-17:59 | $120 | $120 | 30m |

16 UTC remains the existing 10-minute runner; 18 UTC remains the existing 15-second fast harvester.

## Continuous one-ledger frontier

| Global cap | Net | Trades | PF | Expectancy | Realized balance DD |
|---:|---:|---:|---:|---:|---:|
| 16 | +$6,473.55 | 1,737 | 2.789 | +$3.727 | $442.54 |
| 32 | +$12,965.70 | 3,219 | 2.921 | +$4.028 | $817.62 |
| 64 | **+$24,958.35** | **5,711** | **3.090** | **+$4.370** | $1,435.12 |
| 96 | +$36,199.96 | 7,498 | 3.351 | +$4.828 | $1,712.17 |
| 128 | **+$46,575.11** | **9,202** | **3.450** | **+$5.061** | $2,223.86 |
| 160 | +$55,768.89 | 10,772 | 3.453 | +$5.177 | $2,698.97 |
| 192 | +$64,104.96 | 11,929 | 3.407 | +$5.374 | $3,226.72 |
| 256 | +$79,316.01 | 13,567 | 3.383 | +$5.846 | $4,209.41 |
| 384 | +$114,596.30 | 16,058 | 3.732 | +$7.136 | $6,630.76 |
| 512 | **+$151,655.44** | **17,968** | **4.189** | **+$8.440** | $10,857.54 |

High-cap rows are research heat frontiers only, not low-capital recommendations.

At cap 128, the 17 UTC specialist itself contributes:
- +$27,085.39
- 879 admitted trades
- PF ~10.256
- +$30.81 expectancy/trade

## Interpretation

This is a material improvement over the prior campaign frontier at the same exposure cap.

Prior cap-128 campaign:
- +$36,375.97
- 12,617 trades
- PF ~2.257
- +$2.883 expectancy

Subphase-lifecycle cap-128:
- **+$46,575.11**
- 9,202 trades
- **PF 3.450**
- **+$5.061 expectancy**

The improvement comes from preserving scarce inventory for much higher-quality 17 UTC trades and matching emergency room/target geometry to the subphase rather than imposing one universal lifecycle.

January also shows that late 17 UTC entries require much wider catastrophic room before their 30-minute trend resolves. This is a discovery fact, not yet a cross-month rule.

## Exact artifacts

Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/`

- `gamma02_ny17_subphase_lifecycle_001.py`
  SHA-256 `7c4150d82159f67a2ebb47a088bb685ddd7b8f71dc3aa05b5b6bbe93d5ec269c`
- `gamma02_ny17_subphase_lifecycle_001.json`
  SHA-256 `ecc2c554304c6f2afd105f872f6ba057ddb40de99c1f09efb81b92d0b473814b`
- `gamma02_ny17_subphase_lifecycle_001_replay128.json`
  SHA-256 `4a162de6e4718e7985ce8738582ebd210ddda12b2e3a4cc28819f4ccb75a88bd`

Standalone replay reproduced cap 128 exactly.

## Next research

1. Refine 16 UTC and 18 UTC with the same causal subphase discipline.
2. Test profit-lock / unified-stop logic on the new 17 UTC lifecycle map.
3. Search for a separate high-volume harvester that can coexist with the extremely high-expectancy 17 UTC inventory.
4. Integrate with the previously earned STMR parent and shadow layer.
5. Exact tick-level equity-DD certification for finalists.
6. Jan-Jul only after January architecture stabilizes.

R9 SYNTH remains the hard target.
