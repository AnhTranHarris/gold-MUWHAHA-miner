# Gold Hunter V8 clean-room reconstruction

This repository does **not** contain decompiled or copied proprietary Gold Hunter V8 source code. The EA is a clean-room behavioral reconstruction derived from externally observable MT5 Strategy Tester behavior plus public performance evidence.

## Reference fingerprint

Reference test supplied by the owner:

- XAUUSD, M1
- 2026-01-01 through 2026-08-31
- $100 initial balance
- 1:500 leverage
- 0.01 fixed lot
- `GapPips=50`
- `StopLossPips=50`
- `TrailPips=20`
- trailing enabled
- magic `5555`
- `DailyProfitTarget=100` present in inputs, but its semantics are unresolved

Headline report behavior:

- 308,763 trades
- 617,526 deals
- 75.72% winners
- profit factor about 8.45
- average holding time about 25 seconds

Those results are a Strategy Tester fingerprint, not a claim that identical live execution is achievable.

## High-confidence order-state reconstruction

The earliest order rows in the supplied report expose the state machine directly.

### 01:00 cycle

At `2026.01.02 01:00:00` V8 placed a two-sided stop bracket:

- sell stop `4324.12`, SL `4324.62`
- buy stop `4324.62`, SL `4324.12`

The sell stop filled and the buy stop was canceled.

At `01:00:06` the short closed by stop/trailing logic (`sl 4321.82`). At that same timestamp V8 re-armed **only** the old buy boundary at `4324.62`, still using `4324.12` as its initial SL. That buy stop filled at `01:00:20`.

This proves the post-exit behavior is not "build a new bracket around current price." V8 preserves the minute's original two boundaries and re-arms the **opposite** boundary after each position closes.

### 01:01 cycle

At `01:01:00` V8 created a fresh minute bracket:

- buy stop `4329.31`, SL `4328.81`
- sell stop `4328.81`, SL `4329.31`

The buy filled at `01:01:16`; the sell was canceled. The buy closed at `01:01:42` and V8 immediately re-armed only the sell stop at the original `4328.81` boundary.

At `01:02:00` that old one-sided order was replaced by a new minute bracket:

- buy stop `4330.11`, SL `4329.61`
- sell stop `4329.61`, SL `4330.11`

The same pattern repeats in subsequent rows.

## Reconstructed state machine

1. At the start of a new M1 bar, define a center near current market price.
2. Create two stop-entry boundaries separated by approximately `$0.50` in the reference symbol specification.
3. Each order's initial stop is the opposite boundary when `GapPips == StopLossPips == 50`.
4. When one pending order triggers, cancel the other pending order.
5. Manage the open position with a tight trailing stop (`TrailPips=20`; approximately `$0.20` in the reference report).
6. When the position closes inside the same M1 bar, re-arm only the opposite original boundary.
7. If that reversal boundary triggers and later closes, re-arm the other original boundary.
8. Continue this ping-pong process for the remainder of that minute.
9. At the next M1 bar, discard the old boundary pair and generate a new pair.

This explains why trade count can exceed the number of M1 candles.

## Current implementation choices

`Experts/GoldMuwahahaMiner_V8_Baseline.mq5` implements the observed state machine while adding broker-safe normalization:

- fixed default volume 0.01
- 50-pip total band (`InpHunterPipPrice=0.01`, so 50 = `$0.50`)
- 50-pip initial SL
- 20-pip trailing distance
- 20-pip default trailing activation threshold
- M1 boundary reset
- opposite-order cancellation after fill
- same-minute opposite-boundary re-arm
- tick-size normalization
- volume-step normalization
- `SYMBOL_TRADE_STOPS_LEVEL` awareness
- symbol-derived filling mode
- synchronous `CTrade` requests
- return-code validation after every trade operation
- `OnTradeTransaction` used only as a wake-up signal; current orders and positions are re-read because MetaQuotes does not guarantee transaction arrival order

## Unknowns deliberately left testable

The following are not yet proven from the report:

- exact formula for the M1 bracket center (mid price is the baseline hypothesis)
- whether trailing activates immediately or only after +20 Hunter pips; baseline uses +20
- exact handling of spread when computing the bracket center
- exact semantics of `DailyProfitTarget=100`
- handling of unusual broker stop/freeze restrictions
- whether V8 contains any hidden session/news filter (the trade density currently argues against a strong filter)

## Public cross-check

A public Myfxbook system named **Gold Hunter V8 EA MT5** by ForexEALab reports a JustMarkets MT5 demo account at 1:500 leverage, 12,982 trades, 129.82 lots, roughly 0.01 lot per trade, 62-64% directional win rates, a -50 pip worst trade, 3-second average duration, and profit factor 2.54. These are strongly consistent with a fixed-micro-lot, very-short-duration stop/trailing architecture, although they do not prove the internal code.

Public ForexFactory searching produced much weaker V8-specific evidence than the supplied tester report and Myfxbook data. Reddit searching did not produce reliable V8-specific technical evidence, so Reddit claims were not used to invent strategy logic.

## MT5 validation protocol

The next MT5 test should use the same symbol, broker history, test period, M1 timeframe, starting capital, and 1:500 leverage as the reference report. Do not optimize parameters yet.

Compare the first 50-100 **Orders** rows before comparing profit. The clone should first reproduce the behavioral fingerprint:

1. new M1 bar produces two pending stops about `$0.50` apart;
2. SL of each pending stop is about `$0.50` beyond entry and equals the other boundary under the default inputs;
3. when one triggers, the other is canceled;
4. after a trailing/SL exit inside the same minute, only the opposite old boundary is re-armed;
5. on the next minute, that surviving boundary is canceled/replaced by a new two-sided bracket.

Only after order sequencing matches should P/L, win rate, holding time, and profit factor be used for calibration.
