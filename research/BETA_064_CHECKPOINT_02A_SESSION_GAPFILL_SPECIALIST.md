# BETA064 CHECKPOINT 02A — Session-Conditioned Gap-Fill Specialist

**Date:** 2026-09-30  
**Branch:** `beta`  
**Parent:** Major Checkpoint 01 — frozen  
**Status:** PROMISING RESEARCH CHILD — NO EA PROMOTION — HOLD+EXIT DEFERRED — AUGUST SEALED

## Purpose

Checkpoint-02 diagnostics showed that the largest Entry→Hold deficit versus R9 SYNTH is state/path transfer, not simply router strictness.

This bounded child experiment tests whether global trading-session context can recover additional real Dukascopy Entry→Hold opportunities without weakening the frozen Checkpoint-01 trades.

The requested session authorities are implemented explicitly:

- Australia
- Asia
- Middle East
- continental Europe
- UK / London
- New York

The session layer is **not** a six-way directional voting system.

It is a contextual authority layer that modifies eligibility and required survival confidence for selected Entry specialists.

## Session definitions

Each timestamp is converted from UTC into the session's own IANA timezone so daylight-saving transitions are handled causally.

| Authority | Timezone | Primary local window |
|---|---|---|
| Australia | Australia/Sydney | 08:00–17:00 |
| Asia | Asia/Tokyo | 09:00–18:00 |
| Middle East | Asia/Dubai | 08:00–17:00 |
| Europe | Europe/Berlin | 08:00–17:00 |
| UK | Europe/London | 08:00–17:00 |
| New York | America/New_York | 08:00–17:00 |

Overlaps are preserved as information rather than forcibly assigning each tick to only one geographical session.

## Diagnostic discovery

The raw session diagnostic established clear differences in Entry→Hold behavior.

Examples:

- Asian opening windows repeatedly exhibit higher survival than the surrounding Asian session.
- European/UK/NY conditions improve several continuation / break specialists.
- E11 Kinetic Ignition improves strongly during Europe/UK/NY relative to Australia.
- E9 Level Break is materially stronger in Europe/UK/NY.
- E10 Compression Release becomes approximately breakeven-to-positive in UK/NY before routing, while remaining negative earlier.
- E1 Macro Trend has its best gross economics during Europe/UK/NY, but its sample remains too sparse for session gap-fill admission.

This justified session-conditioned thresholds rather than one global threshold for every region.

## Rejected design — full session router replacement

A first session router was allowed to replace the frozen gate broadly.

Trade counts increased substantially, but Entry→Hold survivability fell below 85% in January–March:

| Month | Trades | Survivability |
|---|---:|---:|
| Jan | 1,475 | 81.90% |
| Feb | 2,088 | 77.16% |
| Mar | 2,876 | 81.19% |

This design is rejected.

It demonstrates that session context is useful but must not override the quality discipline of Major Checkpoint 01.

## Accepted design — session gap filling

The refined architecture preserves every frozen Checkpoint-01 trade and reserves its entire position-ownership interval.

Session specialists may add a trade only when:

1. Checkpoint 01 has no active/reserved position;
2. the candidate is not already a Checkpoint-01 trade;
3. the specialist is approved for session gap filling;
4. its broader causal precheck is satisfied;
5. its session-specific survival authority is satisfied;
6. one-position chronological ownership remains intact.

Eligible session-gap specialists:

- E5 VWAP Reclaim
- E6 Value Reversion
- E7 Sweep/Reclaim
- E9 Level Break
- E10 Compression Release
- E11 Kinetic Ignition
- E12 Failed Expansion

E1/E2/E3/E4/E8 remain observational or frozen-only until they show enough robust session-conditioned evidence.

## Frozen session survival authorities

Final conservative thresholds:

| Session | Required session survival score |
|---|---:|
| Australia | 0.920 |
| Asia | 0.900 |
| Middle East | 0.915 |
| Europe | 0.910 |
| UK | 0.925 |
| New York | 0.925 |

Additional precheck:

- broad session survival signal >= 0.89;
- broad session economic score >= 0.08.

The original Checkpoint-01 gates remain unchanged:

- `p_survive >= 0.88`;
- `entry_score >= 0.30`.

## Month-by-month result

| Month | Ckpt-01 trades | Session-gap trades | Total trades | Survivability | First-passage success | Diagnostic value |
|---|---:|---:|---:|---:|---:|---:|
| Jan | 278 | 448 | **726** | **87.60%** | 62.40% | +$894.48 |
| Feb | 337 | 573 | **910** | **87.36%** | 58.24% | +$1,081.53 |
| Mar | 568 | 895 | **1,463** | **87.29%** | 58.92% | +$1,640.56 |
| Apr | 274 | 315 | **589** | **90.15%** | 61.46% | +$711.29 |
| May | 249 | 260 | **509** | **91.94%** | 63.85% | +$576.06 |
| Jun | 261 | 324 | **585** | **88.21%** | 61.88% | +$623.69 |
| Jul | 130 | 158 | **288** | **90.63%** | 60.76% | +$254.46 |
| **Total** | **2,097** | **2,973** | **5,070** | **88.44% weighted** | **60.53% weighted** | **+$5,782.07** |

Relative to Major Checkpoint 01:

- Entry→Hold trade count: **2,097 → 5,070**
- opportunity count multiplier: **2.42×**
- incremental accepted opportunities: **+2,973**
- weighted survivability: 90.56% → **88.44%**
- remains above the required 85% floor in every month
- diagnostic path-resolution value: +$2,781.99 → **+$5,782.07**

This is the first large coverage expansion that preserves the Entry→Hold survivability requirement across all seven observed months.

## Leave-one-month-out robustness

Session thresholds were reselected while withholding each month.

Held-out survivability:

| Held-out month | Trades | Survivability |
|---|---:|---:|
| Jan | 726 | 87.60% |
| Feb | 975 | **86.36%** |
| Mar | 1,463 | 87.29% |
| Apr | 589 | 90.15% |
| May | 509 | 91.94% |
| Jun | 585 | 88.21% |
| Jul | 288 | 90.63% |

All seven held-out months remain above 85%.

Therefore the session effect is not dependent on observing the held-out month to preserve the research survivability gate.

## Attribution of added opportunities

Added-trade session authorities:

- UK: 1,032 additions, 89.24% survival
- New York: 759, 87.35%
- Asia: 505, 83.96%
- Europe: 236, 82.20%
- Middle East: 235, 85.96%
- Australia: 206, 87.86%

Some individual session additions are below 85% in isolation, especially Asia/Europe, but they are admitted only inside the month-level portfolio geometry that preserves every month's >=85% total survivability. Future refinement should raise those isolated session qualities rather than loosen them.

Largest added specialist families:

- E6 Value Reversion: 1,083 additions
- E11 Kinetic Ignition: 967
- E9 Level Break: 301
- E7 Sweep/Reclaim: 210
- E12 Failed Expansion: 210
- E5 VWAP Reclaim: 124
- E10 Compression Release: 78

This is materially healthier than Checkpoint-02's prior strict-transfer result because E11, E9, E7, E12 and E10 now contribute nontrivial real opportunities rather than leaving E6 as almost the entire transferable universe.

## Architectural integration

The Entry hierarchy becomes:

`global causal market state`

→ `geographical/session authority surface`

→ `eligible E1–E12 Entry desks`

→ `Checkpoint-01 frozen router OR session gap-fill authority`

→ `one-position ownership`

→ `fill + origin/thesis packet`

→ `H1–H8 Hold floor`

The session authority is metadata on the thesis packet so the Hold layer can later learn whether a pullback, stall, or extension means something different in Australia, Asia, Europe, UK or New York.

That metadata is recorded now, but Hold+Exit behavior is not changed in this unit.

## Quant decision

**Promising research child: retain.**

The session specialist layer recovers substantial additional Entry→Hold coverage while keeping every observed month and every leave-one-month-out month above the 85% survivability requirement.

It does not replace Major Checkpoint 01.

Major Checkpoint 01 remains immutable control.

Next diagnostics should:

1. compare these 5,070 Entry→Hold trades against the SYNTH condition-matched denominator;
2. identify remaining coverage deficit by session + specialist;
3. raise isolated Asia/Europe session-add survivability;
4. investigate E7/E12/E10/E9 state equivalents further;
5. preserve Hold+Exit deferral;
6. keep August sealed.

No official EA or MQL5 promotion is authorized.
