# DELTA 002 — Dukascopy Ultra-Fast Tick Laboratory Report

**Status:** VERIFIED_DURABLE  
**Unit:** `DELTA_002_DUKASCOPY_TICK_LAB`  
**Parent:** `DELTA_001_R9_SOURCE_EVIDENCE_PARITY_PREFLIGHT`  
**Strategy optimization:** NONE  
**August 2026:** SEALED / NOT ACCESSED

## Result

DELTA now has a month-isolated, exact-tick XAUUSD Python research laboratory for the registered Dukascopy January–July 2026 corpus.

The execution chronology is the original ordered Bid/Ask tick stream. Derived candles are causal state only and never replace executable quotes.

## Corpus verified

| Month | Ticks | Core cache bytes | 250 ms bars | 1 s bars | QA |
|---|---:|---:|---:|---:|---|
| Jan | 9,135,062 | 146,161,376 | 4,292,059 | 1,526,214 | PASS |
| Feb | 7,538,339 | 120,613,808 | 3,587,940 | 1,360,472 | PASS |
| Mar | 9,433,179 | 150,931,248 | 4,524,761 | 1,612,599 | PASS |
| Apr | 7,470,570 | 119,529,504 | 3,897,851 | 1,493,754 | PASS |
| May | 8,333,165 | 133,331,024 | 4,094,677 | 1,517,044 | PASS |
| Jun | 8,201,406 | 131,222,880 | 4,206,410 | 1,593,269 | PASS |
| Jul | 7,415,841 | 118,653,840 | 4,093,693 | 1,593,188 | PASS |
| **Total** | **57,527,562** | **920,443,680** | **28,697,391** | **10,696,540** | **PASS** |

Every monthly compressed source byte size and SHA-256 matched the registered DELTA Dukascopy manifest.

The independently rebuilt 250 ms and 1 s bar counts match the previously validated Drive acceleration corpus for every month: 14/14 monthly count comparisons pass.

## Hot-cache architecture

The primary replay cache stores only:
- `timestamp_ms_utc : int64`
- `ask_raw : int32`
- `bid_raw : int32`

This is **16 bytes per source tick**, or 920,443,680 bytes across Jan–Jul.

Quote-volume arrays are optional sidecars and are not required for the core replay engine.

The canonical gzip sources remain immutable evidence. The memmaps are deterministic, regenerable research accelerators.

## Causality and execution invariants

PASS:
- original CSV row order retained as source ordinal;
- timestamps monotonic non-decreasing;
- Ask >= Bid on every source row;
- integer millisecond candle assignment;
- left-closed/right-open candle intervals;
- a tick exactly at a boundary belongs to the new bar;
- same-timestamp source order preserved;
- BUY market execution uses Ask;
- SELL market execution uses Bid;
- BUY mark-to-market/exit uses Bid;
- SELL mark-to-market/exit uses Ask;
- protective-stop fills use the observed executable quote after crossing rather than assuming a perfect stop-price fill;
- empty intervals are not manufactured;
- completed bars are usable only when `bar_end <= decision_time`.

Supported direct-from-tick horizons:
`250ms, 1s, 5s, 15s, 30s, 45s, M1, M2, M3, M4, M5, M6, M10, M12, M15, M20, M30, H1, H2, H3, H4, H6, H8, H12, D1`.

## Crash/time-out resilience

Every month has an independent cache directory and can be rebuilt or replayed separately.

The candidate runner uses deterministic IDs of the form:

`CANDIDATE__VERSION__2026_MM`

and atomically writes `LOCAL_COMPLETE` monthly JSON checkpoints.

A restart can therefore skip completed monthly jobs and resume from the first missing month. Candidate versions never share mutable month results.

## Performance

January contains 9,135,062 ticks.

Five warmed Numba no-op scans of the committed memmap engine measured:
- minimum: ~432.1 million ticks/sec;
- median: ~475.6 million ticks/sec;
- maximum: ~863.1 million ticks/sec.

This is a **hot-loop memory-scan benchmark only**, not a promise of end-to-end strategy throughput. Actual candidate speed depends on feature complexity, state machines, routing, accounting, and output volume.

The no-op candidate template completed the January month-runner smoke job over all 9.1M ticks and wrote the required atomic checkpoint successfully.

## Broker model v1

DELTA_002 deliberately stops short of claiming Coinexx/MT5 parity.

The lab currently preserves:
- native observed Dukascopy spread;
- executable Bid/Ask sides;
- configurable lot;
- configurable contract size;
- configurable commission;
- configurable slippage;
- configurable latency;
- observed-quote protective fills.

The next versioned calibration must freeze Coinexx/R9:
- Point/Digits/tick size;
- contract size and tick value;
- commission accounting;
- stop/freeze levels;
- filling mode;
- deviation/requotes/slippage behavior;
- latency model if used;
- margin/leverage/stop-out behavior;
- MT5 OnTick/order-event ordering;
- R9 lifecycle parity.

That calibration must not alter the underlying Dukascopy chronology.

## Engineering corrections caught before PASS

Post-commit QA found and rejected two implementation defects before DELTA_002 was accepted:

1. a SELL quote-side QA fixture used its exit Ask/Bid arguments in the wrong order;
2. pandas 2.x interpreted positional `to_numpy(False)` as a dtype argument rather than `copy=False`.

Both were corrected in the committed source, followed by a fresh January-through-July compile/QA run. No trading-science result was accepted from the defective versions.

## Canonical source

- `research/delta/lab/dukas_tick_lab.py`
- `research/delta/lab/run_candidate_month.py`
- `research/delta/lab/candidate_template.py`
- `research/delta/lab/DUKASCOPY_TICK_LAB_SOURCE_CATALOG.json`
- `research/delta/qa/DELTA_002_DUKASCOPY_TICK_LAB_QA.py`
- `research/delta/checkpoints/DELTA_002_LAB_QA.json`

## Conclusion

DELTA_002 passes as the canonical high-speed tick research environment.

It is ready for repeated month-by-month candidate development and hyper-specialized analysis on January–July while preserving exact raw quote chronology.

**Next engineering phase:** calibrate the lab's broker/execution layer against the Coinexx MT5 R9 REAL report and R9 functional specification. August remains sealed.
