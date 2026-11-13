# R9 / CCITP — Alpaca IEX ETF evidence and source-availability audit

**Status:** verified quote access + three source-exact gold-entry as-of snapshots + causality implementation; **NOT TRAINED, ROC-AUC UNMEASURED, NO EA PERMISSION**.

## Data identity and limits

- Historical source: connected Alpaca Paper Trading, `get_stock_quotes`, `feed="iex"`, explicit RFC3339 UTC ranges, per-symbol requests. Source timestamps are exchange timestamps, NOT verified delivery timestamps to our Coinexx terminal.
- Six vetted proxies: QQQ (Nasdaq 100), SPY (S&P 500), DIA (Dow 30), EWJ (broad Japan equity ETF, **NOT Nikkei 225**), FEZ (Euro Stoxx 50), VGK (broad European equity ETF). ETF quotes measure their own displayed bid/ask and size at **IEX**, not index-futures liquidity and not XAUUSD liquidity.
- Every one of the six proxies returned at least one historical quote on all nine sampled 2026 dates, January–September. A point sample is not an all-session coverage guarantee. This first exploratory audit did not download full nine-month ETF history.
- Alpaca wrapper accepts at most 10,000 records/request and does not expose `page_token`, although the underlying provider API does. Do **not** silently discard `next_page_token`. For complete extraction, use per-symbol bounded time slices that fully consume results or authenticated Alpaca API pagination via a separate controlled worker. Never claim complete data when any page remains.
- A precommitted 500ms assumed feed latency was used in the exploratory join. This is a stress assumption, not independently measured gold-side receipt latency. Require strict availability BEFORE each Coinexx gold decision.

## Nine-month point-in-time source coverage

Each date was sampled at 15:00 UTC. February, March, April, June, July, August use a 2-second window. January, May, September had separate 10-second probes and longer as-of-gold probes. All six symbols returned data:

| Month | Date | QQQ | SPY | DIA | EWJ | FEZ | VGK | Duration |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Jan | 2026-01-15 | 1519 | 1863 | 41 | 159 | 106 | 135 | 10 sec |
| Feb | 2026-02-17 | 244 | 216 | 60 | 182 | 15 | 23 | 2 sec |
| Mar | 2026-03-17 | 609 | 222 | 136 | 31 | 29 | 72 | 2 sec |
| Apr | 2026-04-15 | 538 | 197 | 128 | 20 | 47 | 32 | 2 sec |
| May | 2026-05-15 | 1606 | 2078 | 1388 | 196 | 215 | 346 | 10 sec |
| Jun | 2026-06-15 | 371 | 562 | 262 | 45 | 45 | 35 | 2 sec |
| Jul | 2026-07-15 | 887 | 835 | 321 | 130 | 61 | 98 | 2 sec |
| Aug | 2026-08-17 | 273 | 253 | 123 | 53 | 13 | 41 | 2 sec |
| Sep | 2026-09-15 | 2404 | 1361 | 346 | 696 | 286 | 282 | 10 sec |

No sampled request reported a next page token; these exact bounded samples were complete. These windows were selected ex ante by calendar date/clock, not by realized gold profitability.

## Direct R9 execution-entry alignment (proof of timestamp join, NOT statistical test)

Three complete Coinexx R9 source-ordinal candidate records in the existing nine-month as-of cache were joined to prior Alpaca IEX quote windows; 500ms minimum source-time delay, <=25 basis-point spread for accepted ETF quotes. All six ETFs had valid, recent quotes in the snapshots. The gold return below is source-replay quoted-price units (cent per ounce), before modeled cost, NOT server-filled account USD:

| Coinexx decision (UTC) | Side | Source entry ordinal | Original R9 quoted-price movement | 5-second QQQ midpoint return (bp) | 5-second SPY midpoint return (bp) |
|---|---|---:|---:|---:|---:|
| 2026-01-15 15:00:40.200 | BUY | 3,157,231 | +26 units | -5.356 | -1.513 |
| 2026-05-15 15:00:59.019 | SELL | 35,414,063 | +96 units | -2.816 | -1.552 |
| 2026-09-15 15:00:03.060 | SELL | 68,163,278 | -52 units | +0.781 | +1.190 |

For Jan 15 15:00:40.200, DIA had 2,162 source quote updates across the 12-second retrieval, of which 1,438 were rejected for spread >25 bps (or other configured invalidity). **Do not silently carry forward the last valid DIA midpoint across one of these invalid events.** May DIA 6/1,035, FEZ 2/100, VGK 26/328; September FEZ 19/169 rejected in their separately sampled entry-aligned windows. These are event-level quality results, not full-month quality rates.

## Validation and thresholds

- Added `alpaca_iex.py` with the source-specific adapter, ETF-vs-index provenance, strict cross-feed causal ordering, invalid-event reset, fixed 500ms latency assumption, 2s max quote age, 25bp max spread and past-only 1/3/5/10s returns; IEX displayed size imbalance explicitly stays an ETF-only feature.
- Existing `crossindex.py` was not changed. Separate `tests/test_alpaca_iex.py` verifies source-time parsing, missing instruments, strict same-time and future rejection, rejection resets, stale data, causal returns, invalid quote sizes, and non-Nikkei labeling.
- **21 combined local tests PASS** and source compiles. No new R9 EA code or previous P1 research changed.
- Owner acceptance: external gold first-passage label prediction ROC-AUC <0.75 FAIL; 0.75–0.80 research; >0.80 target reached but not economic/deployment approval. No ROC-AUC is computed from three examples. Expanding to all trading hours requires a genuinely complete nine-month ETF source-month corpus and later out-of-sample periods.
- **Data availability caution:** ETFs trade US-listed hours; Japanese/European native exchange discovery is not represented overnight. The source clock alone does not establish feed receipt timestamps or obtainable real-time lead/lag at 250ms.

## Next technical gate: data ingestion without exhaustive manual MT5 exports

The connected Alpaca plugin is confirmed for historical query samples, but its exposed schema does not pass through Alpaca's underlying `page_token`. For full-year scale without many manual timestamp chunks, use a controlled, rate-limited, paginated Alpaca historical-quotes ingestion worker operating with the user's Alpaca API authorization. Keep provider raw data in PRIVATE storage (not in public GitHub), log exact symbol/feed/time boundaries/hashes, detect missing and invalid quote segments, and train on as-of feature snapshots with strict expired-label purging. *No API credentials are stored in GitHub or Google Drive*. Do not substitute single-minute OHLC for 1–30-second quote-based lead–lag.

## Source pointers

- Frozen Coinexx R9 nine-month candidate source, `source_receipt.json` in `carson/coinexx-r9-path-signature-shadow-p1-20261113` branch, 303,934 candidates, hashes for all nine raw XAUUSD months; existing derived cache in primary data Drive.
- Alpaca historical quotes API: https://docs.alpaca.markets/us/reference/stockquotes-1 (symbol-major paging and next_page_token), https://docs.alpaca.markets/us/v1.4.2/docs/historical-stock-data-1 (IEX is one venue, not consolidated), https://docs.alpaca.markets/us/reference/stockquotesingle-1 (quote schemas and nanosecond time).

## 2026-11-13 executable ingestion-worker extension

`ingest_alpaca.py` is now added to this GitHub research branch, with accompanying `tests/test_ingest_alpaca.py`. It implements provider-authorized, **complete page-token pagination**; one-symbol partitions; private gzip CSV archives; complete-source SHA-256 receipts; checkpoint/resume validation; date-scope conflict rejection; exact nanosecond timestamp-order guards; and exclusive partition boundaries over Alpaca's inclusive API end. It supports cheaper full-month `1Min` bar ingestion for high-level regime screening, and UTC-hour full quote ingestion for later microsecond/horizon-specific research. Bars are never to be interpreted as 1–30-second quotes. No credentials are stored in source or pushed to GitHub.

**Execution status: the ingestion worker's network path has NOT been executed**; local tests substitute deterministic API fixtures because Alpaca OAuth access through ChatGPT plugins does not supply API-key secrets to the Python runtime. A private authorized Alpaca environment is needed for unattended bulk pagination. The worker is ready for such an environment but the user's credentials are neither known nor requested in chat. At the current checkpoint there are only nine-month provider spot checks and three true quote-to-gold matching examples, **not** a full historical index dataset, AUC estimate or fitted trading policy.

Twenty-seven combined Python unit tests now pass locally, covering original cross-index invariants, new quote-quality and latency invariants, and ingestion pagination / checkpoint failures. CI source is unchanged because existing cross-index test discovery already covers these new tests.
