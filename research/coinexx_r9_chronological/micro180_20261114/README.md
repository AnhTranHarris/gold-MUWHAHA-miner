# R9 Micro180 asymmetric-entry + cash-exit research fork — 2026-11-14

**Research only. Not validated as profitable. No live EA release.** Original compiled EA `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5` and old nine-month dual-OR baseline remain untouched.

## What changed

- **Actual millisecond timestamps**: source `time_msc`, original source order, same-ms quote rows retained. Bounded 180-second rolling **real observed** 1-second Bid/Ask close records, plus completed/active 5s, 15s, 30s Bid/Ask OHLC candles. Empty intervals are not fabricated.
- **5s basket**: recognizes immediate midquote displacement >= 10 cents, **candidate only**. Its reset alone does not give new trade permission.
- **15s basket**: preceding completed real 15-second candle must confirm side-directed minimum 6-cent displacement. S1 10-second actual elapsed-time freshness and bid-based directional efficiency remain required.
- **15s and 30s executable breakouts**: **BUY** must exceed previous *completed Bid-second closes* in both windows; **SELL** must be below previous *completed Ask-second closes* in both windows, by at least one price point. Every window has observed-coverage and freshness checks. Basket or spread-only displacements never by themselves authorize an order.
- **Micro quant filters**: efficiency of completed 15-second midpoint closes, normalized 30-second executable-side breakout (RMS 1-second return scale), past-second spread-shock ratio, and bounded quote arrival count. All causal and deterministic, *not* fitted win probabilities.
- **Indicators integrated**: completed-price M1 EMA20, Wilder-derived +/-DI14 and ATR14 in Python; native `iADXWilder`, `iMA` EMA and M1/M5 `iATR` in MQL5. Quote-only rolling structure remains an explicitly labeled fallback when the first set is unavailable. MQL5-native vs Python indicator parity NOT yet verified; MT5 fallback is **not** synthetic trade volume.
- **Cash exit lifecycle**: on-modeled-net +$0.10 close/harvest, +$1.75 preferred cap, default up-to-30s timeout, first-available adverse quote >$2 loss cutoff, and original initial broker-side SL. Optional research runner is **OFF**: it requires strict observed trend plus an actually legal tighter stop protecting >=$0.10 modeled net, never widens a stop. No guarantee of realized cash floor or risk ceiling under slippage/gaps.
- **Risk**: Python prototype uses prior `CashAccount` with governor **ON by default** in runner, including 25% initial-equity floor, stricter 10% peak and daily gross-loss budget. The standalone MQL5 fork has persistent 25%-from-start, 10%-from-peak, daily 4%-to-12% gross governor and $2 broker-verified OrderCalcProfit admission. Multi-terminal account-state parity is **not** certified.
- **Capacity**: at most 4 fills per source-native minute, one open position, deliberate 5s+15s rearm boundaries and 3s post-exit cooldown. This is opportunity throughput, **not a high-profit guarantee**.

## Research procedure

```bash
PYTHONPATH=research/coinexx_r9_chronological/src:research/coinexx_r9_chronological/variable_cash_horizon_20261114 \
python research/coinexx_r9_chronological/micro180_20261114/run_micro180.py \
  --ticks /EXISTING_READONLY_PATH/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz \
  --limit 200000 --output /tmp/micro180_smoke.json
```

Use `--limit 0` only for an intentionally authorized **whole monthly** source pass. No raw tick data are reconstructed or written. The script uses the existing exact Coinexx reader from the verified source project. It **does not validate** the source SHA-256 by itself; source fingerprints must match the frozen receipt before result promotion.

For local deterministic invariants:

```bash
python -m unittest discover -s research/coinexx_r9_chronological/micro180_20261114 -p 'test_micro180.py' -v
```

The MQL5 code is **a separate demo-disabled fork** `Experts/GoldMuwahahaMiner_R9_Micro180_Research.mq5`: default `InpEnableDemoOrders=false`; even if enabled it will refuse a non-DEMO account. It requests batches from the terminal with `CopyTicks` using an equal-millisecond offset cursor, and fails closed if quotes cannot be caught up. Native MetaEditor compilation has **not** yet occurred. It does not inherit R9 session-adaptive ATR or source-identical Python EMA/ADX math; those are explicit parity blockers before demo or release. Any benchmark should report these differences.

## Important experiment controls

- New parameters are **engineering hypotheses**, not selected for nine-month profitability. Prior nine-month dual-OR baseline: 419,389 trades and -$162,656.05 modeled cash after historical spread plus illustrative $0.20 extra fee; this micro180 candidate has **not** undergone an equivalent nine-month source-exact evaluation.
- Source January first 200,000 quote smoke test: 81 completed experimental trades, -$30.43 modeled net, 200,000 source records, ~98 MB peak runtime memory in the first build. The first sample has zero historical `last` and executed-volume records. No profitable claim or comparative inference from a 200k slice.
- All cash values depend on broker `OrderCalcProfit`, commission and slippage; Python K=1 and C=0.20 are illustrative. The $0.10 positive target is a *close request threshold*, not a guarantee of realized minimum; $1.75 cannot be guaranteed as a hard realized upper maximum.
- A $2 stop order and 25% account equity boundary can be overrun in gaps. The governors target risk containment, not guaranteed liquidation prices.

## Release gates

1. Add MQL5 MetaEditor compiler in a real installed terminal, fix warnings, and run read-only shadow mode before any demo trade.
2. Compare same Coinexx input between Python and MQL5 on **all** 5/15/30 candles, exact-ms ordering, both-side breakpoint exits, native M1/M5 indicator values, broker conversions and rearm behavior. MQL5 `OnTick` queue coalescence requires validation of `CopyTicks` catch-up and equal-ms duplicates.
3. Run unmodified original R9 and frozen dual-OR controls beside micro180 on January–September original source (all months, source hashes, no lookahead) and frozen later OOS before interpreting performance. Validate both $0.10 harvest and conditional runner as **separate experimental arms**, and never use old AUC at new entry timestamps.
4. Produce compact per-trade MFE/MAE, first-passage cash, slippage sensitivity, and session BUY/SELL breakdown. A positive net full-system result under conservative costs and emergency governor scenarios is necessary before promotion.

**No downloader rebuild, no duplicate tick library, no raw tick export, no old model transfer, no automatic live trade.**
