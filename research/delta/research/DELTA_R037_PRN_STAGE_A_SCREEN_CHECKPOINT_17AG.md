# DELTA R037 — Psychological Round-Number Liquidity Stage-A Screen — Checkpoint 17AG

**Status:** COMPLETE / FAMILY RETIRED / NO RETUNE  
**Unit:** R037_PSYCHOLOGICAL_ROUND_LIQUIDITY_STAGE_A_SCREEN  
**Parent durable checkpoint:** R037_PDHSR_C02_MONTH_BY_MONTH_VALIDATION_CHECKPOINT_17AF  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Question

Can strict $5/$10 XAUUSD psychological-grid sweeps followed by causal S5/S15 close reclaim create a sufficiently selective, short-horizon reversal source under the frozen 30-second DELTA lifecycle?

The family was preregistered before official compute. No threshold rescue, side/session rescue, post-hoc filtering, exit retuning, August access, or MQL5 was used.

## Producer integrity

Producer:
`research/delta/experiments/delta_r037_prn_stage_a_17ag.py`

Committed Git blob:
`800a3bf113e045b59c879735d46ba66cd95bca59`

Local pre-execution Git blob:
`800a3bf113e045b59c879735d46ba66cd95bca59`

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks:
**4,205,709**

Official raw-result SHA-256:
`8421ed2f4f349dca68160a19f2b679ac74afb3ac69bcf7b8ed46478d16a5ac59`

## Results

| Config | Trades | Wins | Direct net |
|---|---:|---:|---:|
| C01 $10 / S5 reclaim | 906 | 426 | **-$185.06** |
| C03 $10 / S15 reclaim | 1,030 | 444 | **-$253.75** |
| C02 $5 / S5 reclaim | 1,841 | 858 | **-$384.33** |
| C04 $5 / S15 reclaim | 2,123 | 946 | **-$477.98** |

All four configurations passed activity supply but failed the preregistered direct-net gate by a wide margin.

## Interpretation

Psychological-grid sweeps are abundant, but naked sweep/reclaim confirmation is too noisy for the frozen short-horizon economics. The failure is consistent with the broader public-source scan: a liquidity sweep alone is not enough; the more reconstructible community implementations require a causal displacement/market-structure-change stage before entry.

This makes 17AG a useful negative result because it removes an entire dense family without spending a refinement cycle on threshold rescue.

## Decision

**RETIRE R037-PRN-v1 WITHOUT RETUNING.**

Do not:
- rescue with session, side, weekday, or volatility filtering;
- change $5/$10 grids after seeing the result;
- tune exits;
- inspect August;
- start MQL5.

Next:
`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

Search bias:
**sparse liquidity event -> causal displacement/state shift -> optional imbalance/retest confirmation**, rather than naked level touch or naked reclaim.
