# MM-C31 — Dukascopy-Only Multi-Resolution Market Structure Research Specification

Status: QUEUED / ORTHOGONAL NEXT CAMPAIGN  
Active predecessor: MM-C30-B1-PROMOTED-STALL-RECLAIM  
Research data: XAUUSD Dukascopy ticks only. August sealed.

## Core rule

This is a multi-resolution, multi-state, multi-specialist **single-market** architecture. Ticks remain execution truth. Higher-resolution bars are causal derived state only.

Primary lattice:

`TICK -> 250ms -> 1s -> 5s -> 15s -> 30s -> M1 -> M5 -> M15 -> M30 -> H1 -> H4 -> H12 -> D1`

Only completed higher-timeframe bars may be used as completed-bar features. Partial-bar features must be explicitly named and may use only ticks observed at decision time. Bid/ask execution is never replaced by midpoint OHLC.

## Functional hierarchy

- D1/H12/H4: macro regime and structural permission.
- H1/M30/M15/M5: auction state and specialist ownership.
- M1/30s/15s/5s: setup geometry.
- 1s/250ms/tick: exact trigger and microstructure quality.
- Post-entry multiscale state: HOLD/PERSISTENCE versus HARVEST/FAILURE.

Do not majority-vote timeframe directions.

## Initial specialist families

1. Trend runner.
2. Rotation fade.
3. Failed-break/reclaim.
4. Compression-expansion.
5. MM-C30-A defensive structural owner.
6. Original R9 base owner.

Specialists must be combined through one chronological ownership state machine. Independent PnL deltas are never summed as proof.

## Frozen research sequence

1. Finish MM-C30-B1.
2. MM-C31-A: causal multiresolution builder certification.
3. MM-C31-B: structural state map and redundancy/unique-information analysis.
4. MM-C31-C: specialist ownership screen.
5. MM-C31-D: multiresolution lifecycle coupling to B1.
6. MM-C31-E: exact chronological portfolio integration.

Discovery discipline: Jan-Mar discovery, April calibration where prespecified, May-Jul frozen forward evaluation, August sealed.

No existing artifact is deleted or overwritten as a substitute. No MT5 coding until a combined causal candidate survives the promotion gates.


## Mandatory 120-second rolling tick buffer

The rolling 120-second window is infrastructure, not a strategy rule.

Every sub-minute feature/candle used by Python research and eventual MQL5 reproduction must be derivable from the same causal 120-second tick ring buffer. This buffer exists because MT5's standard chart/timeframe interface does not natively expose the required sub-minute ladder. It is not a 120-second entry condition, hold duration, exit timeout, stop rule, or profit target.

At each incoming tick, retain only ticks in `(t-120s, t]` and causally update:
`250ms / 1s / 5s / 15s / 30s / 45s / 60s / 120s` state.

Primary sub-minute bars are fixed-clock OHLC/tick-count/spread/path summaries built from those retained ticks. Event-anchored rolling features may coexist, but must be named separately from fixed-clock candles.

Python and MQL5 must share identical bucket-boundary semantics, price basis (bid/ask/mid), missing-bucket policy, UTC convention, and completed-vs-partial bar rules. Strategy logic is tested above this builder so a successful Dukascopy result can later be reproduced in the EA without depending on M1 visual bars.

The current MM-C30-B1 R120 audit found weak but real incremental context signal (Jan-Mar OOF AUC ~0.533-0.559) and rejected the 120s context as a standalone exit gate. Its intended use is therefore process-memory/state context for ownership and HOLD/HARVEST interpretation.
