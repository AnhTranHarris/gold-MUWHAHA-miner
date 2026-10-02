# DELTA Dukascopy Tick Lab v1

Purpose: ultra-fast, month-isolated XAUUSD research replay on the registered Dukascopy Jan–Jul 2026 tick corpus. August is sealed.

## Core invariants

- Raw ordered ticks are execution truth.
- Hot cache stores only `timestamp_ms:int64`, `ask_raw:int32`, `bid_raw:int32` = 16 bytes/tick.
- Source row index is the deterministic source ordinal; same-timestamp order is never sorted/reordered.
- Price math stays integer (`raw / 1000 = XAUUSD price`) until cash/P&L conversion.
- Market BUY fills at Ask; SELL fills at Bid. Exits use the opposite executable side.
- Protective stops fill at the observed executable quote when crossed (gap-safe), not magically at the requested stop.
- Spread is therefore native to the source. Commission, slippage, latency, contract size, margin/stop-out are explicit broker calibration fields and are not silently guessed.
- Every candle uses `[start,end)` integer-ms boundaries and is visible only after `bar_end <= current_tick_time`.
- 250ms, 1s, 5s, 15s, 30s, 45s, M1/M2/M3/M4/M5/M6/M10/M12/M15/M20/M30/H1/H2/H3/H4/H6/H8/H12/D1 are supported and rebuilt directly from raw ticks.
- Empty intervals remain empty.

## Why the cache is fast

The canonical gzip files remain evidence. `compile` creates deterministic NumPy `.npy` memmaps, allowing Numba candidates to scan tick arrays without reparsing CSV or loading the whole month into RAM. Jan–Jul core cache is ~0.92 GB for 57.5M ticks.

## Commands

```bash
python research/delta/lab/dukas_tick_lab.py verify --month 1 --source-dir DATA
python research/delta/lab/dukas_tick_lab.py compile --month 1 --source-dir DATA --cache-root CACHE
python research/delta/lab/dukas_tick_lab.py qa --month 1 --cache-root CACHE
python research/delta/lab/dukas_tick_lab.py benchmark --month 1 --cache-root CACHE
python research/delta/lab/dukas_tick_lab.py bars --month 1 --cache-root CACHE --timeframe M5
```

For a candidate:

```bash
python research/delta/lab/run_candidate_month.py \
  --candidate research/delta/lab/candidate_template.py \
  --candidate-id DELTA_TEST --version v001 --month 1 \
  --cache-root CACHE --results-root RESULTS --config '{}'
```

Each month writes an atomic `LOCAL_COMPLETE` JSON. Restarting skips completed jobs; behavior-changing candidate revisions use a new version ID.

## Acceleration policy

Use raw ticks whenever exact causal/executable ordering matters. Optional bar caches accelerate state features but never replace raw quote execution. The existing Drive 250ms/1s corpus is a comparison/acceleration surface only; the lab independently reproduces those bar counts from the raw ticks.

## Next calibration phase

The lab is intentionally broker-neutral in v1. The next step is Coinexx/R9 parity calibration: point/digits, contract size/tick value, commissions, stop/freeze levels, fill mode, deviation/slippage/latency assumptions, margin/stop-out, and MT5 OnTick/order-lifecycle ordering. Those changes must be versioned; they do not alter the raw market chronology.
