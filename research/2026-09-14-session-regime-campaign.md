# Gold MUWHAHA Miner — session/regime research campaign

Date: 2026-09-14

This branch is deliberately based on `carson/v8-cleanroom-baseline`. The baseline EA is not modified here. Research candidates must earn promotion through Python screening and then MT5 Strategy Tester / forward validation.

## Dataset

Coinexx XAUUSD native M1 archive, 2020-01-02 through 2026-08-31.

- 2,359,684 M1 bars
- point/tick size: 0.01
- contract size: 100
- no duplicate timestamps in the supplied M1 archive
- native M5/M15 cross-checks matched M1 resampling exactly in prior QC

## Python laboratory limitation

The research simulator uses M1 OHLC plus spread and a conservative deterministic intrabar path. It cannot know true tick ordering inside a minute. It is therefore a ranking and falsification laboratory, not a substitute for MT5 real-tick certification.

A useful calibration result is that the bar model reproduces the 2026 forward regime closely enough for ranking: about 322.5k proxy trades and PF about 9.07 versus the MT5 forward report at about 322.6k trades and PF about 9.07.

## Baseline regime result

Fixed 50-pip total bracket / 50-pip SL / 20-pip trail proxy by year:

| Year | Proxy PF | Proxy expectancy |
|---|---:|---:|
| 2020 | 0.714 | -0.077 |
| 2021 | 0.521 | -0.100 |
| 2022 | 0.355 | -0.171 |
| 2023 | 0.570 | -0.081 |
| 2024 | 0.622 | -0.089 |
| 2025 | 2.990 | +0.313 |
| 2026 | 9.070 | +1.003 |

Interpretation: the fixed V8 settings are highly regime-sensitive in the conservative M1 model. The architecture became dramatically better as XAUUSD minute volatility expanded in 2025-2026.

## London / New York result

The strongest broad session was New York. London remains useful, but the raw London open is materially weaker than later New York activity in the long-history proxy.

Baseline proxy:

- London all: PF 1.38, expectancy +0.078
- London open: PF 1.06, expectancy +0.013
- London/NY overlap: PF 1.65, expectancy +0.127
- New York all: PF 2.10, expectancy +0.208
- New York-only after London: PF 2.39, expectancy +0.258

A wider $1.00 total bracket with a tighter $0.15 trail improved all of those slices:

- London all: PF 2.20
- London open: PF 1.76
- London/NY overlap: PF 2.63
- New York all: PF 3.33
- New York-only: PF 3.76

This is why session logic should be adaptive rather than simply 'London/NY only'.

## Candidate R1 — adaptive-quality gate

The first candidate to clear the long-history promotion screen combines:

- M5 ATR(14) >= $2.00
- current spread <= 25 XAUUSD points ($0.25 on this Coinexx symbol)
- total breakout bracket = $1.00 (100 Hunter pips)
- initial SL remains $0.50 (50 Hunter pips)
- trail / activation = $0.15 (15 Hunter pips)
- fixed 0.01 lot remains unchanged

Proxy PF by year:

| Year | PF | Expectancy |
|---|---:|---:|
| 2020 | 4.22 | +0.386 |
| 2021 | 2.25 | +0.175 |
| 2022 | 1.98 | +0.153 |
| 2023 | 2.01 | +0.146 |
| 2024 | 2.48 | +0.214 |
| 2025 | 5.80 | +0.520 |
| 2026 | 13.08 | +1.116 |

This is not a claim that MT5 will achieve these PF values. It is evidence that the candidate ranks above the fixed baseline across all seven calendar years in the conservative bar model.

### NY-focused version

Adding a New York-session requirement to R1 raises quality further in the proxy:

- 2020 PF 4.03
- 2021 PF 2.31
- 2022 PF 1.97
- 2023 PF 1.97
- 2024 PF 2.66
- 2025 PF 6.41
- 2026 PF 16.12

The trade-off is fewer opportunities. Therefore this should be tested as a selectable mode rather than hard-coded as the only operating session.

## Slippage stress

This is a critical forward/live gate because community reports about Gold Hunter V8 specifically identify real-account slippage as a failure mode.

Proxy expectancy under adverse execution per entry/exit:

- original baseline, $0.05 slippage: approximately +0.012 per trade
- original baseline, $0.10 slippage: approximately -0.101 per trade
- R1, $0.05 slippage: approximately +0.558 per trade
- R1, $0.10 slippage: approximately +0.446 per trade
- NY R1, $0.10 slippage: approximately +0.411 per trade

This makes execution robustness a stronger justification for R1 than its headline PF.

## Scheduled news overlay (2026)

Exact scheduled release windows were tested for 2026 CPI and Employment Situation releases at 08:30 ET plus FOMC decision windows at 14:00 ET.

A blanket news blackout is not supported by the current bar study:

- event windows remained profitable
- FOMC windows were particularly strong in the proxy
- removing +/- 15, 30, or 60 minutes around every tested event did not materially improve baseline expectancy

Therefore the research direction is **not** 'disable trading around all high-impact news'. Instead use spread / realized-volatility / slippage protection and allow momentum events when execution remains acceptable.

Unscheduled geopolitical / gold-specific shocks cannot be reliably covered by a calendar, so the same execution/regime gate is intended to handle them.

## Community cross-reference

Public Gold Hunter V8 evidence remains consistent with an ultra-short-duration XAUUSD scalper. Myfxbook's public demo instance reports roughly 13k trades, 0.01-lot behavior, ~3 second average duration, PF ~2.54 and a worst trade around -50 pips. A separate community discussion warns that the EA may work in demo but fail on real accounts because of slippage. These are treated as hypotheses / warnings, not proof of source-code behavior.

Community XAUUSD discussions also repeatedly emphasize London / early New York volatility, NY-open fakeouts, spread widening and ATR/momentum filtering. Those ideas are useful only after they survive this repository's own data.

## Promotion gates

1. Keep `GoldMuwahahaMiner_V8_Baseline.mq5` immutable.
2. Test fixed 100-gap / 15-trail settings in MT5 first because they require no structural rewrite.
3. Add M5 ATR and spread gating only in a separate experimental EA.
4. Compare January-August 2026 against the exact baseline report.
5. Require forward split validation.
6. Stress with realistic spread/slippage and then demo-forward test.
7. Do not merge a candidate into the baseline branch unless it improves robustness, not just profit.

## Primary external references

- MetaQuotes iATR: https://www.mql5.com/en/docs/indicators/IATR
- MetaQuotes CopyBuffer: https://www.mql5.com/en/docs/series/copybuffer
- MetaQuotes SymbolInfoTick: https://www.mql5.com/en/docs/marketinformation/symbolinfotick
- BLS Employment Situation schedule: https://www.bls.gov/schedule/news_release/empsit.htm
- BLS CPI schedule: https://www.bls.gov/schedule/news_release/cpi.htm
- Federal Reserve FOMC calendar: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
- Myfxbook Gold Hunter V8 public system: https://www.myfxbook.com/members/ForexEALab/gold-hunter-v8-ea-mt5/11981314
