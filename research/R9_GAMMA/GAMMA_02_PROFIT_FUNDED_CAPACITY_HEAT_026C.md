# GAMMA-02 — Profit-Funded Capacity Heat Frontier 026C

**Status:** COMPLETE JANUARY RESEARCH HEAT FRONTIER — NOT A DEPLOYMENT SETTING  
**Parent:** GAMMA_02_PROFIT_FUNDED_CAPACITY_026.md  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Static controls on the hour-specific heartbeat opportunity engine

- cap 256: +$160,427.27 / 27,893 trades / PF 3.9088 / exp +$5.7515 / realized DD ~$4,179.75
- cap 384: +$203,190.68 / 35,075 / PF 4.1092 / exp +$5.7930 / DD ~$5,331.96
- cap 512: **+$239,248.19 / 41,147 / PF 4.18045 / exp +$5.81447 / DD ~$7,840.74**

## Profit-funded cap-512 frontiers

Strongest tested net:
- starting cap: **64**
- unlock: **+64 slots per $1,000 current realized net profit**
- hard ceiling: 512
- **+$230,080.51**
- **35,491 trades**
- **PF 4.52936**
- **+$6.48278 expectancy**
- realized balance DD **~$6,151.09**

Versus static cap 512:
- captures **~96.17% of net**
- uses **~13.75% fewer trades**
- realized balance DD is **~21.55% lower**
- PF is ~8.35% higher
- expectancy is ~11.49% higher

Another more conservative example:
- start cap 32
- +64 slots per $2,500 realized profit
- max 512
- +$206,540.36 / 28,115 trades / PF 4.6172 / +$7.346 expectancy

## Interpretation

This is exposure-efficiency evidence, not a new entry edge.

The result demonstrates that the larger January opportunity pool can be accessed progressively using already-realized profits rather than granting full research capacity from the first tick.

Cap 512 is an extreme research heat frontier and is NOT a low-capital/live recommendation.

## Exact artifact

Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/gamma02_profit_funded_capacity_026c_max512.json`

SHA-256:
`33897c0645dd986e2aeaf9819dccd0b769b7b9fd750d6bf8a470cdedf299f46a`

R9 SYNTH remains the hard target.
