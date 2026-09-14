# R5 Tight Risk Certification

Parent: R4 Harvester

Python-screened candidate promoted for MT5 real-tick certification:

- GapPips = 100
- StopLossPips = 30
- TrailPips = 8
- TrailActivationPips = 8
- Lots = 0.01
- M5 ATR/session regime logic unchanged from R4
- Spread gate unchanged at 25 points
- No Asian hard filter
- No blanket news blackout
- No lot compounding

## Why this candidate

Across the 2020-2026 Coinexx bar-screening environment, 8/8/30 improved proxy net capture in every tested calendar year and materially reduced gross loss versus the R4 10/10/50 structure. It also improved the Apr-Aug 2026 proxy slice and remained stronger across all Asian-range quintiles and adverse-execution stress levels.

These are screening results only. M1 OHLC cannot certify sub-minute trailing and stop sequencing. MT5 Strategy Tester with every tick based on real ticks is authoritative.

## Certification test

- Symbol: XAUUSD
- Timeframe: M1
- Model: Every tick based on real ticks
- Date range: 2026-01-01 through 2026-08-31
- Initial deposit: USD 100
- Leverage: same Coinexx tester environment used for R1-R4
- Inputs: defaults from GoldMuwahahaMiner_R5_TightRisk.mq5

## Promotion gate

Compare directly with R4:

- Net profit target: >= R4 $355,138.26 preferred
- Gross loss target: < R4 $31,220.87
- PF target: > R4 12.38 preferred
- Win rate: preserve or improve R4 82.13% if possible
- Relative equity DD: stay near or below ~1%

Do not merge into the parent architecture until the compile result and MT5 report are reviewed.
