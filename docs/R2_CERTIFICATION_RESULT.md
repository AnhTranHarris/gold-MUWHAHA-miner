# R2 MT5 Certification Result

## Source report

`ReportTester-871471_GoldMuwahahaMiner_jan2026_aug2026_brg1.xlsx`

## Test configuration

- Expert: `GoldMuwahahaMiner_R2_RegimeGate`
- Symbol: XAUUSD
- Period: M1, 2026-01-01 through 2026-08-31
- Initial deposit: $100
- Leverage: 1:500
- History quality: 100%
- Geometry: 100 / 50 / 15 / 15
- Completed M5 ATR(14) minimum: $2.00
- Maximum spread: 25 points

## Results

- Net profit: $344,236.79
- Gross profit: $380,326.97
- Gross loss: -$36,090.18
- Profit factor: 10.53824
- Expected payoff: $1.099145
- Total trades: 313,186
- Winning trades: 245,683 (78.45%)
- Short win rate: 78.55%
- Long win rate: 78.34%
- Average winning trade: $1.548039
- Average losing trade: -$0.488250
- Largest winner: $130.10
- Largest loser: -$37.68
- Equity drawdown relative: 1.17% ($2.49)
- Equity drawdown maximal: $39.84 (0.01%)
- Sharpe ratio: 56.026843
- Average holding time: 22 seconds
- Minimum holding time: 1 second
- Maximum holding time: 5:00:21

## Decision

R2 passes the certification gate and advances as the parent for R3 research.

Relative to R1, R2 gives up a small amount of net profit while materially reducing relative equity drawdown. This is considered a favorable robustness trade for forward testing.

R2 remains immutable. R3 will add session-aware volatility thresholds without changing the R2 core state machine or 100/50/15/15 geometry.
