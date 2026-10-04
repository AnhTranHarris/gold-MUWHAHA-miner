# DELTA R037 — Volatility Squeeze Breakout/Release Stage-A — Checkpoint 17AN

**Status:** COMPLETE / NO SCREEN SURVIVOR / FAMILY RETIRED WITHOUT RETUNING  
**Family:** R037-VSBR-v1  
**Parent:** R037_ASRB_C02_LATER_JAN_CHECKPOINT_17AM  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Question

Can a reconstructible Bollinger-inside-Keltner volatility compression, followed by the first completed-bar squeeze release and release close direction relative to the SMA20 basis, produce a viable high-supply XAUUSD Stage-A entry source?

No trend, RSI, volume, session, or exit filter was added after seeing results.

## Integrity

Preregistration commit: `7c323efa14fc6bcdcfdb38402e7f4c478cdf8996`

Producer:
`research/delta/experiments/delta_r037_vsbr_stage_a_17an.py`

Producer commit:
`57979c3ecd0f1f17d3785eccb1e7c8c183151a5b`

Producer blob:
`4a99f047426c8619eec11b5b41868d4c9dfbecdb`

Producer file SHA-256:
`f929f86bca9b1df694d629ca722bee98de7865839e44c8892f7e416614da3081`

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**

Official result SHA-256:
`e01b1b7447642709f907efb724196d5c2f52fa931ebdc7f1b0c2d412365019dc`

The executable source was required to match the committed Git blob exactly before official compute. A transport-copy mismatch was rejected and never executed officially. The corrected executable matched the Git blob and compiled before the bounded replay.

## Frozen profiles

- **C01_M1** — 20-bar M1 squeeze/release
- **C02_M5** — 20-bar M5 squeeze/release

For both:
- Bollinger half-width = 2.0 × population standard deviation
- Keltner half-width = 1.5 × ATR20
- squeeze when Bollinger half-width < Keltner half-width
- release on completed-bar squeeze true → false
- long when release close > SMA20 basis; short when below
- first executable P75 tick at/after bar right edge
- 25-point spread ceiling
- 300 raw stop
- 100 raw trail activation / 30 raw trail distance
- 30-second maximum hold

## Stage-A results

| Profile | Trades | Days | Wins | Net |
|---|---:|---:|---:|---:|
| C01_M1 | 446 | 13 | 200 | **-$93.95** |
| C02_M5 | 92 | 12 | 48 | **-$15.47** |

C01 produced 446 release events; 423 trades exited by stop.  
C02 produced 92 release events; 90 trades exited by stop.

Both profiles easily satisfy the supply gates but fail the preregistered economic floor of -$1.

## Interpretation

This is a high-information negative result. The family has abundant opportunity density, so failure cannot be blamed on insufficient signals. The simple volatility-compression release direction does not survive the frozen 30-second XAUUSD lifecycle.

Because both preregistered timeframes fail materially, adding post-hoc trend, RSI, volume, session, or exit filters would be rescue tuning rather than validation.

## Decision

**RETIRE R037-VSBR-v1 WITHOUT RETUNING.**

Do not:
- sweep Bollinger/Keltner multipliers;
- add trend/RSI/volume/session rescue filters;
- change M1/M5 after results;
- change stop/trail/hold logic;
- access August;
- begin MQL5.

Next:
`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`
