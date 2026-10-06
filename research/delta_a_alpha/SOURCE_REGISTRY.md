# Delta-A-alpha Source Registry

## Parent scientific state

- Repository: `AnhTranHarris/gold-MUWHAHA-miner`
- Parent branch: `delta`
- Parent commit: `ac91fc43389a34f8ba380b58143f8e185589b106`
- Parent durable checkpoint: `R037_SPECIALIST_DOCUMENTATION_FINALIZATION_CHECKPOINT_18B`
- Canonical Stage-A January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Default research surface: `DUKAS_COINEXX_LIKE_P75`
- August: SEALED

## GRID-001 source

Video: https://www.youtube.com/watch?v=4WQEoQxsJMc

User-supplied transcript: `NoteGPT_Transcript_Coding A Grid Trading Bot In Python... 95%+ WINS(1).txt`\n\nDurable Drive transcript document ID: `1d0IQ7F5JAIJT5HC02YuYkjLGdt4LVR4QyBQgPd2qbew`

Reconstructed source logic:
- tutorial timeframe: H1;
- rolling grid window: 48 bars;
- first BUY when price is one grid gap below rolling highest high;
- subsequent BUY anchors use the previous BUY entry;
- first SELL when price is one grid gap above rolling lowest low;
- subsequent SELL anchors use the previous SELL entry;
- source example grid gap: 100 symbol points;
- source example fixed lot: 0.01;
- take profit: one grid gap from entry;
- source default: no stop-loss;
- later tutorial variant introduces 2x martingale lot multiplication;
- example backtest uses 1-minute-OHLC modelling rather than ordered real ticks.

Source claims are hypotheses only. The headline win rate is not evidence of positive expectancy because losing inventory is intentionally held open.

## External cross-checks

Current MetaTrader community products show common grid adaptations such as ATR-based dynamic spacing, capped total exposure, volatility filters, and account-level drawdown protection. These are research leads only; commercial claims are not evidence.

Community discussion consistently flags uncapped martingale/averaging as tail-risk exposure. Delta-A-alpha therefore separates grid event logic from martingale sizing.
