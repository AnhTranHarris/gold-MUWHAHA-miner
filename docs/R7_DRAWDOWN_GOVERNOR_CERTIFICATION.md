# R7 Drawdown Governor Certification

## Parent

R5 (`carson/mt5-r5-tight-risk-certification`) remains the standard parent: 100-pip gap, 30-pip hard stop, 8-pip trail, 8-pip activation, fixed 0.01 lot, session-adaptive ATR gate and spread <=25 points.

## Research basis

External research was used only for design hypotheses:

- ForexFactory examples repeatedly separate equity-vs-balance drawdown, daily loss floors, pending-order blocking/deletion and cooldown periods.
- TradingView XAUUSD systems use account-level governors that block new entries during drawdown, resume after cooldown and keep hard maximum-loss floors separate from normal strategy exits.
- Reddit discussions repeatedly identify clustered losses/regime persistence as a failure mode for static exposure and recommend drawdown-contingent throttling rather than constantly rewriting entries.
- Myfxbook Gold Hunter V8 public profiles show the architecture can produce very low reported drawdown, supporting a defensive governor that preserves the core high-turnover logic rather than replacing it.

## Python campaign

The Coinexx 2020-2026 M1 archive was replayed with R5-like geometry and regime gating. Governor candidates were evaluated over the full history and then decomposed by year, month, week, day and hour.

The selected balanced candidate:

- Amber drawdown: 8R
- Red drawdown: 10R
- Recovery threshold: 6R
- Red cooldown: 45 minutes
- Same-minute re-arm while stressed: disabled
- Daily hard floor: 18R

Proxy result versus ungoverned R5:

- Net capture retained: ~99.93%
- Gross loss reduction: ~2.6%
- Maximum proxy drawdown reduction: ~34.4%
- Gross loss improved in all seven calendar years 2020-2026.
- Maximum drawdown improved in all seven calendar years.
- Net improved in 2022 and 2023 and slipped modestly in the other five years.

The Python model is a ranking/falsification environment, not MT5 tick truth. R7 must be certified in MetaTrader 5 real ticks.

## MT5 implementation

`Experts/GoldMuwahahaMiner_R7_DDGovernor.mq5`

The governor acts only on new exposure:

1. Existing positions continue to use normal R5 trailing/stop management.
2. Green: normal R5 fresh brackets and same-minute re-arms.
3. Amber (>=8R daily peak-to-closed-P/L drawdown): fresh brackets remain allowed, same-minute re-arms are suppressed.
4. Red (>=10R): a 45-minute cooldown blocks new exposure. After cooldown, fresh probe brackets may resume while same-minute re-arms remain disabled until drawdown recovers to <=6R.
5. Daily hard floor (<= -18R closed P/L): no new exposure for the remainder of the broker day.
6. R is estimated in account currency with `OrderCalcProfit` using the current symbol, normalized fixed lot and R5's 30-pip hard-stop distance.

## Certification test

Use the same comparison harness as R5:

- Symbol: XAUUSD
- Timeframe: M1
- Model: Every tick based on real ticks
- Dates: 2026-01-01 through 2026-08-31
- Initial balance: $100
- Coinexx demo / same leverage and tester environment as R5
- Leave R7 defaults unchanged

Promotion requires a material drawdown improvement while preserving R5's net profit and gross-loss advantage closely enough to justify the governor. R5 remains standard if R7 merely suppresses profitable turnover.