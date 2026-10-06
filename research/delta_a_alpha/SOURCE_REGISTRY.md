# Delta-A-alpha Source Registry

## Parent scientific state

- Repository: `AnhTranHarris/gold-MUWHAHA-miner`
- Parent branch: `delta`
- Parent commit: `ac91fc43389a34f8ba380b58143f8e185589b106`
- Parent durable checkpoint: `R037_SPECIALIST_DOCUMENTATION_FINALIZATION_CHECKPOINT_18B`
- Canonical Stage-A January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Default research surface: `DUKAS_COINEXX_LIKE_P75`
- Main `delta`: READ ONLY
- August 2026: SEALED

## GRID-001 primary source

Video: https://www.youtube.com/watch?v=4WQEoQxsJMc

Creator repository: `MegaJoctan/StrategyTester5`

Creator repository main commit inspected: `45e2a23d11716f204cf66f9695124980aceae1bc`

User-supplied transcript: `NoteGPT_Transcript_Coding A Grid Trading Bot In Python... 95%+ WINS(1).txt`

Durable Drive transcript document ID: `1d0IQ7F5JAIJT5HC02YuYkjLGdt4LVR4QyBQgPd2qbew`

Repository audit result:
- README documents StrategyTester5 as a Python/MetaTrader 5 backtesting and optimization framework.
- `docs/tutorials.md` explicitly embeds the supplied grid-trading video.
- The public default branch does not expose the exact tutorial `grid_bot.py` implementation as a searchable source file.
- Therefore the transcript/video is the source for the specific grid mechanics; the repository is authoritative for the framework/API context, not a substitute for missing tutorial code.

Reconstructed source logic:
- tutorial timeframe: H1;
- rolling grid window: 48 bars;
- first BUY when price is one grid gap below rolling highest high;
- subsequent BUY anchors use the previous BUY entry;
- first SELL when price is one grid gap above rolling lowest low;
- subsequent SELL anchors use the previous SELL entry;
- source example grid gap: 100 symbol points;
- source initial lot: 0.01;
- take profit: one grid gap from entry;
- source default: no stop-loss;
- later tutorial demonstration introduces 2x martingale lot multiplication;
- example backtest uses 1-minute-OHLC modelling rather than ordered real ticks.

Source claims are hypotheses only. The headline win rate is not evidence of positive expectancy because unresolved losing inventory can remain open.

## Owner research constraints

- XAUUSD only for Delta-A-alpha grid work.
- Every physical trade is fixed at 0.01 lot.
- Martingale and any loss-dependent lot escalation are prohibited.
- Small-account survivability must be explicitly measured for $100, $200, and $300 starting balances.
- The grid specialist is intended to help close the R9 REAL-to-SYNTH gap before later 6-16 specialist portfolio stacking.

## Canonical R9 benchmark sources

SYNTH MT5 report:
- `ReportTester-871471_jan2026_jul2026_R9_ticklog_synth(4).xlsx`
- SHA-256 `e5fcf4d6879193fac88e7a8e101db1111d59e1a7f5abfb793c970b06cfce7cc7`

REAL MT5 report:
- `ReportTester-871471_jan2026_jul2026_R9_ticklog_real(4).xlsx`
- SHA-256 `19d5ffd785beaae2a9d0baa5efb50efcd36a7db635c7ef82957be442429c1064`

The uploaded `(3)` and `(4)` copies for both reports were hash-verified byte-identical.

Canonical extracted benchmark:
`research/delta_a_alpha/benchmarks/R9_REAL_SYNTH_JAN_JUL_2026.json`

Extractor:
`research/delta_a_alpha/helpers/mt5_report_benchmark_extract.py`

## Scientific separation

The MT5 tester benchmark is the account-level guiding-light ledger including commission and swap. Older ticklogger teacher figures that exclude some account cashflows may remain useful for microstructure diagnostics, but must not silently replace the canonical account-level benchmark.
