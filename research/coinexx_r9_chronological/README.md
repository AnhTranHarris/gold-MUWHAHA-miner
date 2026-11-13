# Coinexx R9 Chronological Backtest Environment

This directory is the durable **Coinexx-only** Python research environment for Gold MUWHAHAHA Miner R9.

## Governing data rule

The raw Coinexx tick stream is authoritative. The engine never replaces ticks with summaries, never sorts them, never deduplicates equal millisecond timestamps, and never fabricates missing ticks or missing one-second bars.

Full one-second candles are available as a *parallel derived stream* for R9's causal second-state calculations. They do not replace the raw ticks. Minute/hour summaries are not research inputs in this environment.

## Exact accepted Coinexx schemas

Broker export:

`time,time_msc,bid,ask,last,volume,volume_real,flags`

R9 TickLogger:

`run_label,time_msc,time,bid,ask,last,tick_volume,volume_real,flags,spread,minute_start,minute_second,cycle_buy,cycle_sell,pending_mode,rearm_number,s1_disp,s1_eff,s1_range,s1_turns,atr,session,gate_open,position_open,position_side,entry_price,mfe,mae,current_sl,trail_armed,event`

Only the market columns are fed to a replay strategy. TickLogger state columns are optional parity telemetry and are never silently reused as predictive inputs.

## Chronology contract

For source rows `i=1..N`:

- `time_msc[i] >= time_msc[i-1]` is required.
- Equal millisecond timestamps remain in source-row order.
- `time == floor(time_msc / 1000)` is required.
- `bid > 0`, `ask > 0`, and `ask >= bid` are required in strict mode.
- Violations stop the run; invalid ticks are not silently discarded.

The event loop calls the strategy exactly once per accepted source row.

## Price representation

Coinexx XAUUSD is represented internally in exact 0.01 price units:

`P_units = price / 0.01`

For the pinned R9 inputs, one Hunter pip is also 0.01, so `30 pips = 30 price units = $0.30`.

This removes avoidable binary-float drift from bracket, stop, and trailing calculations.

## R9 v1.90 formulas

At the first observed tick of each source-native minute:

`mid = (bid + ask) / 2`

`cycle_buy  = RoundToTick(mid + gap/2)`

`cycle_sell = RoundToTick(mid - gap/2)`

with `gap = 30 * 0.01 = $0.30`.

For the most recent `L=10` **completed observed seconds**, using bid closes `C`:

`disp = C_last - C_first`

`travel = Σ |C_i - C_(i-1)|`

`efficiency = |disp| / (travel + 1e-9)`

For the most recent 10 completed observed seconds:

`range = max(second_high) - min(second_low)`

A side must satisfy the pinned directional displacement, efficiency, range, and turn-count tests before entry.

### Completed M5 ATR(14)

Only completed source-native M5 bid bars are used.

`TR_t = max(H_t-L_t, |H_t-C_(t-1)|, |L_t-C_(t-1)|)`

Seed:

`ATR_14 = mean(TR_1..TR_14)`

Wilder recursion:

`ATR_t = (ATR_(t-1)*13 + TR_t)/14`

The gate uses the previous completed M5 ATR state; the current incomplete M5 bar never contributes to the value used to authorize an entry.

### Execution geometry

BUY market entry uses Ask; SELL market entry uses Bid.

Initial stop distance:

`stop_distance = max(30*0.01, broker_stop_distance + tick_size)`

BUY:

`SL = Bid - stop_distance`

SELL:

`SL = Ask + stop_distance`

Trailing activates after a favorable `$0.10` move and targets `$0.03` behind the executable liquidation side, subject to the broker-stop/tick-size constraint.

Max hold is 30 source-native seconds.

## Important source-exact lifecycle detail

The MQL5 EA does **not** set `g_hadPosition=true` on the entry tick. It becomes true only when a later `OnTick` sees the position. The Python baseline mirrors this. A position that opens and is stopped by the trade server before the next EA-observed tick is therefore not treated as an observed-position exit for opposite-side rearm.

## MT5 report handling

`mt5_report.py` streams the actual XLSX worksheet XML and writes **every Orders/Deals row in source order**. It does not load the 1+ GB uncompressed worksheet into memory and does not replace the ledger with a summary.

## Commands

```bash
python -m coinexx_r9.cli verify-ticks XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz

python -m coinexx_r9.cli emit-seconds XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz \
  --out january_seconds.csv.gz

python -m coinexx_r9.cli replay-r9 XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz \
  --config config/r9_hybridgate_v1_90.json \
  --trades-out january_r9_trades.csv \
  --receipt-out january_r9_receipt.json

python -m coinexx_r9.cli extract-mt5 MT5_REPORT.xlsx \
  --orders-out mt5_orders.csv \
  --deals-out mt5_deals.csv
```

## Scope boundary

This v1 environment certifies **market-data chronology and the R9 v1.90 price/lifecycle formulas**. It does not invent an account model. Broker commission, margin, stop-out, rejected trade requests, fill slippage, freeze levels, and server-side execution behavior require exact Coinexx/MT5 evidence before they may affect monetary P&L. Until those are pinned, the trade ledger is an execution-price/lifecycle ledger, not a funded-account equity curve.

## Bootstrap validation

The recovered January Coinexx broker export was read end-to-end in strict mode: 7,699,274 rows passed chronology/schema checks, including 413 adjacent rows sharing the same `time_msc`; those rows were preserved, not deduplicated.

A complete R9 v1.90 replay was also executed over all 7,699,274 rows. Because this sandbox throttles long CPU-bound processes, validation used three exact row partitions (3,000,000 / 3,000,000 / 1,699,274) with the complete Python strategy state carried across boundaries. No market state was reset and no source row was summarized or omitted. The compact receipts under `validation/` are integrity evidence only; the raw ticks remain authoritative.

## Storage policy

Raw ticks and large MT5 reports stay in Google Drive. GitHub stores only code, tests, formulas, exact source identities, and small verification receipts. Large derived tick/candle/trade corpora are not committed.

## Source pins

See `SOURCE_PIN.json`. The current canonical Drive folder is `1VoMTDxRl4txMUIQeZt3aszlZHUQIWv_w`.

The January raw Coinexx broker export used for bootstrap validation is still in a legacy Drive location and is explicitly marked as such; this code does not silently treat that legacy location as the new canonical folder.
