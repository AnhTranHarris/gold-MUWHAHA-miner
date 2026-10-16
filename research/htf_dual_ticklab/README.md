# XAUUSD HTF Dual-Broker Tick Replay v0.1.0

**Status: RESEARCH ENGINE — not live-trading approved; no R9 trading logic imported.**

Two independent input environments using one causal replay core:
- **Coinexx MT5 native**: `XAUUSD_MT5_BROKER_2026_MM_ticks_ALL.csv.gz`, Jan–Sep 2026; uses `time_msc`, bid, ask, flags.
- **Dukascopy**: `XAUUSD_DUKAS_2026_MM_ticks.csv.gz`, Jan–Jul 2026; uses `timestamp_ms_utc`, `ask_raw/1000`, `bid_raw/1000`, ask/bid quoted volume. The scale is explicitly configurable.

Both inputs were personally supplied for this project in Google Drive. Raw datasets, backtest outputs, credentials and broker secrets **must not** be committed to GitHub. No unrelated GitHub branches, prior strategy code or external market datasets are imported. Source history is the pinned user-approved R9 reference snapshot; this package is self-contained.

## First use

Python 3.11+; no dependencies for runtime. From this directory:

```sh
python -m htf_ticklab.cli --broker coinexx \
  --input '/path/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz' \
  --output './results/coinexx/2026-01.json' --strategy none
python -m htf_ticklab.cli --broker dukascopy \
  --input '/path/XAUUSD_DUKAS_2026_01_ticks.csv.gz' \
  --output './results/dukascopy/2026-01.json' --strategy none
```

`--strategy none` is the safe default. `--strategy impulse-demo` merely exercises signal/fill plumbing using **completed S15** bars and is neither optimized nor a recommendation. Use `python -m htf_ticklab.cli --help` for configuration. `python -m pytest -q` runs tests (install `requirements-dev.txt`).

## Recovery update v0.2 (isolated repair branch)

The original v0.1 commit remains immutable. This recovery build adds a continuous
multi-month mode and bounded entry-intent handling. An interrupted replay must
be restarted from the first source file; incremental JSON checkpoints are
**audit receipts, not state-restoration binaries**. They never authorize a
skip directly to the next month without reconstructing the engine state.

```sh
python -m htf_ticklab.cli --broker coinexx \
  --input /authorized/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz \
          /authorized/XAUUSD_MT5_BROKER_2026_02_ticks_ALL.csv.gz \
  --output ./results/coinexx/jan_feb_continuous.json \
  --checkpoint-each-input --strategy none
```

All requested files are hash-verified before replay, and registered monthly
files must be passed in chronological order. Positions, equity, completed
bars, pending requests, and strategy state are carried across file boundaries
without account resets or artificial market gaps. The CLI continues to accept
one monthly file as before. The optional `--checkpoint-each-input` writes
atomic cumulative summaries after each input but does **not** yet support
instant restore of Python execution state. Each source is read as a streaming
`.csv.gz`; the system does not use filenames from neighboring projects.

Entry requests cannot stack up while a position or entry request is pending:
rejected intents are counted under `entry_while_position_open` and
`duplicate_pending_entry`. This prevents a stale burst of orders from later
executing after the original signal disappears. It is a research safety
constraint; no claim is made that it reproduces arbitrary MT5 broker queues.

## Execution and causality

- Quote-time monotonicity, crossed/invalid quotes, timestamp consistency and source-column verification are enforced; equal millisecond timestamps remain ordered. No sorting, candle interpolation, tick fabrication or use of full-minute future OHLC.
- M1/M5/H1 and S5/S15/S30/S45 candles are built on UTC millisecond boundaries; strategy callbacks receive **only completed bars** on the first subsequent quote. Gaps are never filled with synthetic bars.
- A market-order request generated at a tick becomes eligible after configured latency and **only on a later observed tick**. Buy at ask and sell at bid (plus any adverse simulated slippage). Exit a long at bid, exit a short at ask.
- Protective stop/target triggers are server-side quote checks with gap execution at the available quote; no perfect fills at crossed price. Optional constant adverse deviation, two-sided commissions, strict volume/stop/margin/spread gates, tick-level mark-to-market equity and simulated stop-out support.
- Net/gross P&L, PF, win rate, win/loss counts, max observed intratick equity drawdown and hourly/daily/weekly/monthly UTC close-time buckets are generated in JSON. A monthly checkpoint is written atomically and source SHA-256 recorded; existing outputs require explicit `--force` to overwrite.

## Critical limitations to address before investor certification

1. **Contract size (100 oz/lot), leverage (500), stop-out margin fraction, fees, latency, fill deviation and spread ceiling are editable illustrative assumptions**, not asserted historical Coinexx/Dukascopy broker settings. Tick CSV alone does not document historic trade specifications. The Dukascopy tick feed is **not an MT5 execution venue** or proof of tradable account access.
2. Data contains only top-of-book quotes, not market depth, fill confirmations, actual order timestamps, rejects, partial fills, broker freeze levels, funding and historical commissions. The simulator cannot claim exact live-broker fidelity. Order book / network delay modeling can be added after separate permitted evidence.
3. The baseline supports **one position at a time**, simple entry/close orders, and server-side protective exits. No pending-order queue priority or hedged multi-position accounting is claimed. A multi-input continuous run preserves open positions across monthly files. Do not call a single-month result with an open position a settled return.
4. Replay treats every serialized broker quote as available to a local process; real MT5 `OnTick()` event coalescing under handler load is not simulated yet.
5. Bid/ask mismatches between the two brokers are **environment differences**, not automatic strategy failures. Compare matching UTC coverage and identical research policy, with broker-specific execution settings.

## Investor governance

Acceptance gates are governed by `XAU-HTF-INV-001 v1.0` in the user-designated TRADING_RESEARCH Drive folder. This engine does not assert daily/weekly profitability or $100 account survivability. Inspect zeros, rejected orders, margin stopouts, drawdown, and real quote path before optimizing any strategy. Historical fills are not guaranteed future trades.

## Exact file integrity and source isolation

`htf_ticklab/source_registry.py` pins the **16 user-supplied monthly files** to their compressed-file SHA-256 hashes (private Drive IDs are deliberately not published). The CLI checks the hash *before* processing a file and aborts if it does not match; it does not fetch other repositories or remote data. Only tests use `--allow-unregistered-input`, in which case the output clearly records `source_verified=false`. The January source files were exercised end-to-end; February and later have checksum/header checks but have not all undergone complete replay validation at this baseline version.

### Reporting detail

Each run produces both an atomic JSON summary (`--output`) and a SHA-256-pinned **per-trade CSV ledger** unless `--no-trade-ledger` is specified. Period summaries (UTC hour/day/ISO week/month) include net and gross loss/profit, PF, win accuracy, win/loss count ratio, and **closed-trade-path drawdown**. The top-level `max_equity_drawdown_*` is the distinct tick-marked floating-equity drawdown across the full replay. `positive_hour_coverage_trade_active_only` uses **hours that contain exits** as denominator; a market-hour denominator requires an explicitly agreed market calendar and must not be silently conflated with this diagnostic.
