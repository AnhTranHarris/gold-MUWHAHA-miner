# R9 V12: exact-ms micro180 research + standalone MT5 DEMO telemetry

**Research-only source fork. Original R9/V8/V9/V10/V11 and all order policies unchanged.**

## Why the micro180 clock matters

Original V9 held positions an average **6.692 seconds**, median **3.475 seconds** in the full Jan–Sep 2026 original Coinexx research replay. One-second OHLC approximations miss quote ordering and can contaminate the entry second. R9 V12 works from original ordered `Tick.ordinal` and `time_msc`, preserving different quotes within a common millisecond.

### Exact-ms audit — existing Coinexx files only

`micro180_20261114/micro180_exactms_v12.py` subclasses **unchanged** `VolumePreservingMicroV9` and records entry/exit ordinal, current executable Bid/Ask, lane signature, pre-entry 250/1000ms quote counts and mid-displacement, within-actual-hold MFE/MAE and stop/harvest reason. The counterfactual quote path follows the next source rows up to 60 sec. This is a separate **observation**, not hypothetical executable fills. Quote gaps above 2.5 seconds censor later observations. First-passage tests for signed liquidation-price drift of 10/25/50/100 cents begin at the **next source row**, including later rows with the same source millisecond. Equal-ms hits are ordered by ordinal, not assigned to the same artificial second candle.

`micro180_20261114/summarize_micro180_v12.py` aggregates the nine **derived trade-event ledgers**; it does not load the 72-million-quote source files or regenerate tick history. Every full month has an exact compressed source SHA-256 check, and entry and completed-trade **counts** must match the frozen V9 monthly receipt. The full 338k entries are not independently pairwise compared with another separately re-run model, so count parity must not be described as complete per-trade external parity.

Each month resets original V9 strategy state as in earlier source-verified baseline. All Jan–Sep 2026 observations are repeatedly used development data, **not untouched OOS proof**.

### DEMO broker telemetry — no execution methods

`Experts/GoldMuwahahaR9V12DemoTelemetryObserver.mq5` is a new **standalone** observer EA (not included in the original trading EA):

- `InpEnableObserver=false` by default; it does nothing unless the owner opts in.
- Checks `ACCOUNT_TRADE_MODE_DEMO`; refuses live/contest account.
- Filters by exact XAUUSD symbol and `InpExactMagic` (defaults **0**, manual demo trades, not an EA strategy trade).
- Uses `OnTradeTransaction` to queue REQUEST notifications and DEAL_ADD ticket IDs. Does not call `OrderSend`, `OrderSendAsync`, `CTrade`, `PositionClose`, etc.
- Uses bounded 512-row and 256-deal queues; OnTimer looks up `HistoryDealSelect` and writes a CSV in **Terminal Common Files**, with diagnostics when rows/deals are dropped.
- For DEAL, preserves original `OnTradeTransaction` **callback** monotonic time, server-time seconds and quote snapshot, even though history selection/file flush happens later.
- Separately stores `DEAL_TIME_MSC`, actual `DEAL_PRICE`, `DEAL_VOLUME`, `DEAL_COMMISSION`, `DEAL_FEE`, `DEAL_SWAP`, `DEAL_PROFIT`, `DEAL_ENTRY` and `DEAL_REASON`. Deal time is a server-side execution timestamp; callback time is only receipt time. The accompanying callback Bid/Ask snapshot is **NOT** a quote observed at fill time.
- REQUEST callbacks reflect server-side processing results; their callback time is **NOT** the initial request submission time. No true submission-to-fill latency can be calculated from this observer alone.

Python `telemetry_v12/broker_telemetry_v12.py` validates the CSV schema, refuses non-DEMO labels, de-duplicates deals, joins uniquely matched order-request and deal prices, and treats partial fills and ambiguous/missing matches explicitly. The limited conditional price difference reported is **deal price versus requested price**, not execution PnL and not authoritative broker slippage relative to a contemporaneous quote.

### Safe owner-operated DEMO procedure

1. **Do not attach this EA to live MT5.** Research code is not native-compiled or broker-certified in this environment.
2. Compile this separate observer in **MetaEditor**. Stop on any compiler diagnostics. Test offline without order permissions first.
3. On an isolated **DEMO** XAUUSD chart set `InpEnableObserver=true`. Keep all R9/V9 demo-orders disabled. For manual demo transactions leave `InpExactMagic=0`; for any separately authorized demo strategy test specify its verified magic number.
4. After a small **manually authorized** DEMO transaction, check Common Files CSV header, rows, stable session IDs and timer/loss counters; **never place trades just to feed the telemetry study without owner approval**.
5. Validate the existing recorded CSV with:
   ```bash
   python research/coinexx_r9_chronological/telemetry_v12/broker_telemetry_v12.py \
      --input R9_V12_DEMO_EXECUTION_EVENTS.csv \
      --out /tmp/v12_demo_telemetry_audit.json
   ```
6. Treat any loss diagnostics, duplicate deals, missing request callbacks, partial-fill ambiguity, unsynchronized quote clocks or source/broker mismatch as **uncertified execution evidence**. Do not use for real orders.

The collector has **not** been compiled in MetaEditor, attached to MT5, or run against actual DEMO history during this research run. No fills, slippage distributions, rejection rates or latency figures are claimed.

### Needed next broker-telemetry addition

A true **submit-to-fill latency** study requires timestamps immediately **before the trading EA actually submits a request** and explicit correlation identifiers through order/deal events, plus server-to-terminal clock reconciliation. That would touch the real EA trade path and is **out of scope** here until explicitly approved. The current zero-order read-only observer cannot reconstruct an absent submission timestamp.

### Quality and release gate

The CI workflow `r9_v12_exactms_demo_telemetry_ci.yml` runs 71 inherited V9/micro180 and exact-ms tests, 40 V10/V11 structural tests, 7 new telemetry tests, and immutable SHA guards for the original systems. It tests source only (not MetaEditor compile, broker execution, native parity, or OOS forecasting).

Owner may inspect the full nine-month analysis and all nine *derived* ledgers with no market-data imports. **The requested trade-policy change is zero; PR must remain DRAFT.**

## Primary official sources

- `OnTradeTransaction`, transaction order / response semantics: https://www.mql5.com/en/docs/event_handlers/ontradetransaction
- History deal millisecond time, price, fees and position link: https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties
- The `MqlTick` Bid/Ask and trade-volume distinction: https://www.mql5.com/en/docs/constants/structures/mqltick
- Coalescing and NewTick handler: https://www.mql5.com/en/docs/event_handlers/ontick
- Shared common files: https://www.mql5.com/en/docs/files/fileopen
- Demo-only mode account property: https://www.mql5.com/en/docs/constants/environment_state/accountinformation#enum_account_trade_mode
