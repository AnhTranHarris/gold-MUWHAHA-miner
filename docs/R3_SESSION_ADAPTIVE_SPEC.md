# R3 Session-Adaptive Certification Specification

R3 advances from the R2 regime-gated EA without modifying R2.

## Goal

Bias new exposure toward the London/New York regimes that showed the strongest historical expectancy, while preserving the ability to trade outside those sessions when volatility is unusually favorable.

## Core geometry

Unchanged from R2:

- Lots: 0.01
- Gap: 100 Hunter pips ($1.00 total bracket)
- Stop loss: 50 Hunter pips ($0.50)
- Trail: 15 Hunter pips ($0.15)
- Trail activation: 15 Hunter pips ($0.15)

## Session-aware ATR thresholds

The session controller operates on quote timestamps using an explicit configurable UTC offset. Default offset is 0 because the exported Coinexx archive and the MT5 reports used for calibration align with UTC timestamps.

Profiles:

- London-only window: ATR(14, M5) >= $2.00
- London/New York overlap: ATR(14, M5) >= $1.75
- New York after London: ATR(14, M5) >= $1.75
- Off-session: ATR(14, M5) >= $2.50

Spread must remain <= 25 points in all profiles.

The controller does not ban off-session trading. It demands a stronger volatility regime instead.

## Session windows

The first certification implementation uses DST-aware London and New York local clocks derived from UTC:

- London active: 08:00-16:30 Europe/London local time
- New York active: 08:00-17:00 America/New_York local time
- Overlap: both session predicates true

London DST is modeled from the last Sunday in March to the last Sunday in October.
New York DST is modeled from the second Sunday in March to the first Sunday in November.

## Safety / anti-lookahead

- ATR uses `CopyBuffer(..., shift=1)` from the completed M5 bar.
- A rejected M1 minute is marked processed and is not retried later in that same minute.
- Session classification uses current quote time only.
- Existing positions continue to be managed even if the session profile changes.

## Promotion gate

R3 must compile with 0 errors / 0 warnings and then be tested on XAUUSD M1 with every tick based on real ticks for 2026-01-01 through 2026-08-31 from $100 starting capital.

R3 is not allowed to replace R2 unless it improves at least one of risk-adjusted expectancy, drawdown, or regime consistency without materially damaging profit factor.
