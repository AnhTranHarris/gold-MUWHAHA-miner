# GAMMA-02 — Meta Router 122 Stream Cache Checkpoint A

**Status:** DURABLE INPUT CACHE COMPLETE / ROUTER SCORING IN PROGRESS  
**Date:** 2026-10-07  
**August:** SEALED

## Purpose

Persist the expensive month-by-month causal shadow-expert streams before the no-month-label meta-router parameter search.

## Experts

Each month has shadow trade streams for:
- 103 — high-activity rolling renewal;
- 119 — dynamic renewal watchdog;
- 109 — failed-ignition reverse;
- 114 — frozen April-derived late-NY continuation rules (hour 17 only);
- 115 — frozen June-derived 16-UTC rules (hour 16 only).

Each stream contains chronological entry index, exit index, entry raw price, direction, realized P/L, realized hold, and expert ID.

## January-May diagnostic pattern

The raw shadow streams confirm strong causal regime separation without using month labels at entry:

- Jan: 103/119/114/115 are positive; 119 strongest.
- Feb: 103/119/114 positive; 103 strongest quality.
- Mar: 119 +109 positive; 103 has no selected trades; 114/115 negative.
- Apr: 114 positive; 119 nearly flat negative; 115 negative.
- May: 114 positive; 119/115 toxic; 109 tiny positive.
- Jun: 114 and 115 positive; 119 negative.
- Jul: 115 positive; 114/119 negative; 103 only 28 tiny positive trades.

This is the exact pattern router 122 must learn causally from realized shadow performance.

## Persistence

Library root:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/meta-router-122/`

Files:
- `gamma02_router122_streams_m1.npz` + JSON summary
- `gamma02_router122_streams_m2.npz` + JSON summary
- `gamma02_router122_streams_m3.npz` + JSON summary
- `gamma02_router122_streams_m4.npz` + JSON summary
- `gamma02_router122_streams_m5.npz` + JSON summary
- `gamma02_router122_streams_m6.npz` + JSON summary
- month 7 cache is also persisted; Library may have duplicate-safe filename suffix from a repeated upload.

The local exact builder is:
`/mnt/data/gamma02_causal_meta_router_122.py`

## Router trial design

One continuous Jan-Jul chronology.

For every expert:
- all its signals are observed in shadow mode;
- expert quality changes only when its shadow exits have actually realized;
- current entry admission cannot use its own future outcome.

At each live candidate entry:
- recent shadow expectancy/PF determines whether the expert is active;
- simultaneous candidates are ranked by current realized shadow score;
- all experts share one global chronological position cap.

This is causal and does not use calendar-month labels.

## First trial

- global cap 703
- rolling shadow window 64 exits
- minimum 8 realized shadow samples
- minimum expectancy 0
- minimum PF 1.0
- cold start: deny until sample minimum
- simultaneous ranking: current realized shadow expectancy

If a timeout occurs, inspect the final result:
`/mnt/data/router122_all_w64_s8_e0_pf1.json`

No final JSON = incomplete trial; rerun only this trial, not the expert-stream builds.
