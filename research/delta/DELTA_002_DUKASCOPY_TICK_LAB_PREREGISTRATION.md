# DELTA 002 — Dukascopy Ultra-Fast Tick Laboratory

**Status:** PREREGISTERED  
**Parent:** DELTA_001_R9_SOURCE_EVIDENCE_PARITY_PREFLIGHT  
**Strategy optimization:** PROHIBITED IN THIS UNIT  
**August 2026:** SEALED

## Purpose

Build the canonical DELTA Python research laboratory for exact XAUUSD tick replay on the registered Dukascopy January–July 2026 corpus.

The lab must be fast enough for repeated candidate refinement while retaining the raw ordered Bid/Ask stream as execution truth.

## Registered design

1. Canonical monthly CSV.GZ remains immutable evidence.
2. Each month is compiled independently into NumPy memory-mapped hot arrays:
   - timestamp_ms_utc: int64
   - ask_raw: int32
   - bid_raw: int32
3. Core cache footprint target: 16 bytes/tick. Quote-volume arrays are optional sidecars.
4. Source row index is the deterministic source ordinal; rows are never resorted.
5. Price math remains integer raw units in the hot path. Registered dataset scale: 1000 raw units per $1.00 XAUUSD.
6. Candidate execution uses observed Bid/Ask, never midpoint fills.
7. Candles are reconstructed directly from ticks using integer millisecond [start,end) boundaries and right-edge visibility.
8. Supported timeframes: 250ms, 1s, 5s, 15s, 30s, 45s, M1, M2, M3, M4, M5, M6, M10, M12, M15, M20, M30, H1, H2, H3, H4, H6, H8, H12, D1.
9. Month jobs are isolated and atomically checkpointed so restart begins at the first incomplete month.
10. The initial broker layer is deliberately broker-neutral but real-quote aware: native spread, executable-side mark-to-market, configurable commission/slippage/latency/contract size. Coinexx/R9 parity is a later versioned calibration task.

## Falsification / hard fail

DELTA_002 fails if any of the following occurs:
- a Jan–Jul monthly source byte size or SHA-256 differs from the registered manifest;
- parsed tick row count differs from the validated monthly count;
- source timestamps decrease;
- any Ask is below Bid;
- source order is changed;
- a tick exactly on a bar boundary is assigned to the previous bar;
- same-timestamp source ordering is lost;
- reconstructed 250ms or 1s monthly bar counts differ from the independently validated Drive acceleration corpus;
- market BUY/Sell execution tests do not use Ask/Bid respectively;
- August is accessed.

## QA surface

For every month report:
- canonical source hash and size;
- tick row count;
- first/last timestamp and quote;
- timestamp monotonicity;
- Ask>=Bid;
- hot-cache bytes;
- 250ms and 1s bar-count parity.

January additionally records a hot-loop benchmark and a candidate month-runner smoke checkpoint.

## Scientific boundary

DELTA_002 produces no accepted trading candidate and does not tune entry/hold/exit logic. Its purpose is to create the deterministic environment that later DELTA candidates will use.
