# Gold MUWHAHA R2 MT5 Certification

## Parent

R2 is based on the certified R1 geometry candidate.

R1 reference result, XAUUSD M1, 2026-01-01 through 2026-08-31, $100 initial deposit:

- Net profit: $353,494.57
- Profit factor: 10.603
- Expected payoff: $1.116/trade
- Total trades: 316,751
- Win rate: 78.40%
- Relative equity drawdown: 2.84%
- Average holding time: 22 seconds

## R2 hypothesis

Keep the complete R1 state machine and geometry, but only create or re-arm exposure when:

1. The last completed M5 ATR(14) is at least $2.00 in XAUUSD price units.
2. Current live spread is no more than 25 symbol points ($0.25 for the Coinexx two-decimal XAUUSD specification).

Existing positions continue to be trailed and managed even if the gate subsequently closes.

The ATR check uses CopyBuffer start position 1, intentionally reading the completed M5 candle rather than the forming candle. A rejected M1 minute is marked processed, so the EA does not retry later in that same minute if volatility rises. This prevents intrabar look-ahead contamination.

## Defaults

- Lots: 0.01
- GapPips: 100
- StopLossPips: 50
- TrailPips: 15
- TrailActivationPips: 15
- ATR timeframe: M5
- ATR period: 14
- Minimum ATR: 2.00
- Maximum spread: 25 points
- Fail closed if ATR is unavailable: true
- Daily profit target: disabled

## First certification run

Compile `Experts/GoldMuwahahaMiner_R2_RegimeGate.mq5` in MetaEditor.

Required compile gate:

- 0 errors
- 0 warnings

Then Strategy Tester:

- Symbol: XAUUSD
- Period: M1
- Model: Every tick based on real ticks
- Dates: 2026-01-01 through 2026-08-31
- Initial deposit: $100
- Leverage: same Coinexx test environment as R1
- Leave all EA inputs at defaults

Export the complete XLSX report.

## Promotion criteria

R2 does not need to beat R1 on raw profit to survive. It advances if it materially improves execution robustness/selectivity without destroying the edge. Review:

- net profit
- profit factor
- expected payoff
- relative equity drawdown
- trade count
- win rate
- largest loss
- consecutive-loss clusters
- month-by-month profit slope, especially April-August

If R2 passes, the next controlled candidate adds session-aware adaptation (London / overlap / New York) without changing R2's core risk geometry.