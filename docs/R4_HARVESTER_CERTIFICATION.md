# R4 Harvester Certification

## Parent

R3 Session Adaptive (`carson/mt5-r3-session-adaptive-certification`).

## Research reason

The 2020-2026 Coinexx M1 Python screening found that tightening the trailing stop and activation from 15/15 Hunter pips to 10/10 improved proxy expectancy and reduced gross loss in every tested calendar year. Because M1 OHLC cannot certify intra-minute stop movement, MT5 real-tick Strategy Tester remains authoritative.

## Intentional R4 change

Only profit-harvesting defaults change:

- `InpTrailPips`: 15 -> 10
- `InpTrailActivationPips`: 15 -> 10

Preserved from R3:

- Lots 0.01
- Gap 100
- Stop loss 50
- M5 ATR(14) regime gate
- Spread maximum 25 points
- London ATR minimum 2.00
- London/New York overlap ATR minimum 1.75
- New York ATR minimum 1.75
- Off-session ATR minimum 2.50
- DST-aware session classification
- No same-minute retry after a rejected minute
- V8 OCO / opposite-boundary re-arm state machine

No news blackout, Asian-session hard filter, lot compounding, or predictive indicator stack is introduced in R4.

## Certification run

Use:

- Expert: `GoldMuwahahaMiner_R4_Harvester`
- Symbol: XAUUSD
- Period: M1
- Model: Every tick based on real ticks
- Date: 2026-01-01 through 2026-08-31
- Initial deposit: USD 100
- Leverage: 1:500 where available
- Default EA inputs

## Promotion objective

R4 should beat R1/R2/R3 on net profit while preserving the gross-loss and drawdown improvements established by R2/R3.

Reference targets from prior MT5 certification:

- R1 net profit: about 353,494.57
- R2 net profit: about 344,236.79
- R3 net profit: about 343,378.35
- R2/R3 relative equity drawdown: about 1.17%

R4 is not approved for merge unless the MT5 report is reviewed.