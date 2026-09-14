# R3 MT5 Certification Protocol

1. Compile `Experts/GoldMuwahahaMiner_R3_SessionAdaptive.mq5` in current MetaEditor.
2. Require 0 errors and 0 warnings before testing.
3. Strategy Tester:
   - Symbol: XAUUSD
   - Period: M1
   - Model: Every tick based on real ticks
   - Range: 2026-01-01 through 2026-08-31
   - Initial deposit: $100
   - Leverage: 1:500
   - Defaults unchanged
4. Export the XLSX report.
5. Compare against certified R2:
   - Net profit: $344,236.79
   - PF: 10.53824
   - Expected payoff: $1.099145
   - Win rate: 78.45%
   - Relative equity DD: 1.17%
   - Trades: 313,186
6. Reject R3 if session adaptation materially degrades PF or causes a large opportunity collapse without a compensating drawdown improvement.
