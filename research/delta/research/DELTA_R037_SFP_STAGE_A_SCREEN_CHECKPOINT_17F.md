# DELTA R037 — Local Swing Failure Pattern Stage-A Screen — Checkpoint 17F

**Status:** COMPLETE / NO SCREEN SURVIVOR / FAMILY RETIRED  
**Family:** R037-SFP-v1  
**Parent:** R037_MSF_STAGE_A_SCREEN_CHECKPOINT_17E  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Frozen hypothesis

A valid bearish SFP requires a completed bar to wick above a causally confirmed local swing high and close back below it. A bullish SFP requires a wick below a confirmed swing low and a close back above it. Swings use a symmetric two-bar confirmed fractal and are not visible until two right-side bars complete.

The strong-rejection variants additionally require the close to finish in the reversal half of the sweep candle. Each swing identity is consumed on the first beyond-level interaction. Ambiguous same-bar two-sided failures emit no proposal.

Public reconstructible basis:
- MetaQuotes Code Base 76586 — Liquidity Sweep Detector;
- MetaQuotes MQL5 article 24184 — wick-only violation of active swing = sweep while close-through = true break;
- open-source TradingView SFP implementations documenting wick-through + close-back mechanics.

## Crash safety

Prereg commit: `83861bf58aaff8e393950d1fd771fe24dfc0ec54`  
Producer commit: `d05a78fa8384906f2da14a3a1eaba7e29718c205`  
Producer Git blob: `8aaedf366dce60f52e83b21dba6de264f94dc1e2`  
Producer SHA-256: `2d164150f7d604283ef52f9b665c82c172b1a9ffb9dcc1149c4cf51fa45c04e5`  
Recovery run: **37177568521 PASS**  
Precompute pointer gate: **37177616703 PASS**

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**  
Official bounded runtime: approximately **20.172 seconds**, exit 0.  
Official raw result SHA-256:
`23deec8f7c1f3250b880b9b510ee25effb1c5de4fc271305950ba5453bab7b5f`

## Results

Parent control: **14,034 trades / 6,349 official wins / -$2,944.94 net / $2,946.43 max equity DD**.

- **C01 M1 BASIC:** 911 proposals / 877 accepted; +864 trades / +371 official wins / **-$195.85 net delta**; direct SFP -$202.89; equity-DD +6.64%. FAIL.
- **C02 M1 HALF_REJECTION:** 501 / 485; +479 / +201 / **-$115.64**; direct -$119.48; equity-DD +3.92%. FAIL.
- **C03 M5 BASIC:** 196 / 185; +177 / +72 / **-$40.69**; direct -$43.74; equity-DD +1.38%. FAIL.
- **C04 M5 HALF_REJECTION:** 107 / 102; +97 / +44 / **-$18.85**; direct -$22.03; equity-DD +0.64%. FAIL.

## Interpretation

Higher timeframe and stronger rejection monotonically improve the family, but even the strongest preregistered variant is far outside the frozen -$2 screen gate.

The causal lesson is useful and negative: **local wick-sweep + close-back rejection alone is too permissive for the frozen 30-second hold.** The result does not justify retuning swing width, rejection depth, sessions, sides, or exits.

This also sharpens the 17E clue: the near-neutral MSF C04 result cannot be explained merely by “liquidity rejection.” The successful ingredient appears more specific to **completed M5 continuation structure + FVG retest**, not generic SFP reversal.

## Decision

**Checkpoint 17F = RETIRE R037-SFP-v1 / NO RETUNE.**

No promotion. Continue:
`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

August remains SEALED. MQL5 remains unauthorized.
