# GAMMA-02 — Exact January R9 SYNTH Benchmark 029

**Status:** COMPLETE / AUTHORITATIVE MONTHLY BENCHMARK EXTRACTED FROM MT5 DEALS  
**Source:** `ReportTester-871471_jan2026_jul2026_R9_ticklog_synth(4).xlsx`  
**Source SHA-256:** `e5fcf4d6879193fac88e7a8e101db1111d59e1a7f5abfb793c970b06cfce7cc7`

## January R9 SYNTH

- **+$41,520.82 net**
- 27,980 trades
- PF **23.71541**
- 24,368 strictly positive trades = **87.09%**
- +$1.48395 expectancy/trade
- average winner +$1.77892
- average loser -$0.50690
- average hold **16.46 s**
- median hold 18 s
- P90 hold 29 s
- P95/P99 hold 30 s
- closed-trade balance DD ~$3.40

The deal ledger includes the two -$0.01 commissions per complete 0.01 trade.

## Current GAMMA-02 funded-cap primary vs exact January SYNTH

| Metric | R9 SYNTH Jan | GAMMA-02 Jan | GAMMA/SYNTH |
|---|---:|---:|---:|
| Net | +$41,520.82 | **+$154,538.37** | **3.72x** |
| Trades | 27,980 | 24,646 | **88.08%** |
| PF | **23.715** | 4.091 | 17.25% |
| Expectancy/trade | +$1.484 | **+$6.270** | **4.23x** |
| Win rate | **87.09%** | 67.93% | -19.16 pp |
| Avg hold | **16.46 s** | ~1,164.48 s | ~70.7x longer |

## Interpretation

The hard target is now more precise.

GAMMA-02 has already exceeded the January R9 SYNTH **raw net** and **per-ticket expectancy**, and has recovered most of the monthly trade count.

It has NOT reproduced the SYNTH architecture:
- PF is far lower;
- win rate is far lower;
- average holding time is roughly 19.4 minutes rather than 16 seconds;
- simultaneous inventory/heat is radically higher;
- exact January funded-cap equity DD is ~$17.55K versus R9 SYNTH's near-frictionless modeled equity curve.

Therefore the next goal is **not simply more gross profit**. The research must preserve GAMMA-02 capture while compressing lifecycle and exposure, improving PF/win conversion, and freeing slots faster.

This avoids the false claim that a heavily concurrent inventory engine has already “beaten” R9 SYNTH in system quality.

## Next unit

`GAMMA_02_SLOT_EFFICIENCY_QUALITY_030`

Start with source/hour attribution under the exact funded-cap replay. Remove or restructure negative/low-efficiency capacity consumers only when total one-ledger economics improve. Then test campaign profit-lock / slot-release mechanisms using exact tick-marked equity.

August remains SEALED. No MQL5 build yet.
