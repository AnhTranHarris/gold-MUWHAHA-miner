# 04 — P5 H1/H4 Structural Trend Core

**Status:** independently robust structural sleeve.

## Purpose

P5 provides a low-frequency, high-expectancy return stream with a failure distribution different from the HFT auction engines.

## Reconstructible family

Use only completed higher-timeframe bars.

Representative H1 family:
- 5-bar or 8-bar Donchian breakout;
- ATR / rolling-volatility ratio filter;
- large structural stop room;
- early trailing lifecycle;
- up to ~12 h holding window.

Representative H4 configuration:
- 6-bar structural breakout;
- relative-volatility ratio < ~2;
- ~1.5 ATR catastrophic stop;
- ~1 ATR trailing management;
- ~24 h lifecycle.

Representative H4 result:
- 87 trades
- +$1,684 net
- -$1,619 gross loss
- PF ≈ 2.04
- 7/7 positive months.

## Portfolio role

P5 should remain an independent sleeve. Do not force it through every HFT gate. Its value is different cadence and tail-state behavior, not high trade count.

No future bar may be used to confirm a breakout.
