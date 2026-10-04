# DELTA R037 — Sweep → IFVG → Retest Stage-A Screen — Checkpoint 17BX–17BY

**Status:** COMPLETE / M5 STAGE-A SURVIVOR  
**Parent:** R037_FIB_GOLDEN_POCKET_IMPULSE_RETRACE_STAGE_A_SCREEN_CHECKPOINT_17BW  
**Family:** R037-SIFVG-v1  
**Surface:** native completed-bar M1/M5 signal logic → DUKAS_COINEXX_LIKE_P75 execution  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Research question

Can a source-grounded, closed-bar causal sequence of liquidity sweep → directional FVG displacement → body-close inversion → first confirmed IFVG retest create positive frozen 30-second XAUUSD persistence?

This is not a rescue of BOSLS 17AY. BOSLS entered immediately on wick sweep/reclaim. This family requires a later displacement gap, later body-close inversion, and then a later retest.

## Source-grounded fixed semantics

Primary public logic was reconstructed from the open-source TradingView Sweep IFVG implementation, with independent IFVG-state support from MetaQuotes/MQL5 materials:

- 3-candle confirmed swing; one right bar required before swing is knowable.
- eligible liquidity swing must be the extreme of the preceding 50 bars.
- sweep = wick beyond eligible swing + completed close back inside.
- sweep validity = 50 bars.
- FVG = three-bar wick-to-wick gap in sweep-implied reaction direction.
- minimum FVG = 30 ticks.
- inversion requires a completed candle body to close through the far gap edge; wick probe alone does not invert.
- first later retest must overlap the inverted gap and close back on the inversion side with matching directional body.
- consecutive chart bars are required for FVG construction to prevent weekend/session-gap artifacts.
- first P75 executable tick after the retest bar is the entry.

The public prose exposes inversion/retest lifecycles as configurable but does not publish the exact current grace defaults. Clean-room approximation was fixed **before compute** at 50 bars for inversion grace and retest validity, matching the published 50-bar sweep lifecycle. No post-result tuning is permitted.

## Durability / crash containment

Preregistration commit: `8ce37fe1d54fddf62145e4edfa699deab4d1b79f`

Producer:
`research/delta/experiments/delta_r037_sweep_ifvg_retest_17bx_17by.py`

Producer commit:
`6a2d4c7207b28af088b082c2d9492306a8ebe74c`

Producer blob:
`9a53dce8bba3579787270eb8376d2515abcf6b36`

Producer SHA-256:
`835e21edced8e053466e267e341151ee482e9f63e833b67aa94064826d73761d`

The local official producer Git blob exactly matched GitHub before execution. The official compute ran through `delta_bounded_python_runner.py` with a 120-second wall timeout, isolated Numba cache, child process-group containment and producer atomic JSON replacement. It completed normally in approximately 5.8 seconds.

Canonical January SHA:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**

Official result SHA-256:
`2aa333df3e79573a521989afcaeb9b20b975db235ba31f667e4c7007bb6d6d54`

## Stage-A result

| Lane | Trades | Days | Wins | Net | Gate |
|---|---:|---:|---:|---:|---|
| 17BX M1 | 152 | 11 | 73 | **-$26.86** | FAIL |
| 17BY M5 | 24 | 10 | 17 | **+$1.35** | **PASS** |

### 17BY M5 funnel

- confirmed extreme highs: 131
- confirmed extreme lows: 69
- buyside sweeps: 72
- sellside sweeps: 31
- candidate bullish FVGs: 20
- candidate bearish FVGs: 39
- bullish inversions: 27
- bearish inversions: 13
- bullish retests/signals: 17
- bearish retests/signals: 7

The M1 failure beside the M5 survival is important: this is not evidence that generic IFVGs are profitable. The only surviving evidence is the **M5 source-anchored sequence** under the frozen lifecycle.

## Decision

**17BY M5 advances to independent later-January validation unchanged.**

Do not:
- retune the 50-bar windows;
- alter 30-tick gap minimum;
- add sessions or directional filters;
- optimize stops/exits;
- use August;
- start MQL5.

Next bounded unit:
`R037_SWEEP_IFVG_INDEPENDENT_LATER_JAN_VALIDATION`

The survivor must reproduce on the untouched remainder of January before any broader refinement or integration is earned.
