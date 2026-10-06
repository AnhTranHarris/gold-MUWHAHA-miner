# Delta-A-alpha — Session + Timeframe Awareness Campaign 001 — Preregistration

**Unit:** `DAA_GRID_SYSTEM_SESSION_TIMEFRAME_CAMPAIGN_001_PREREG`  
**Status:** PREREGISTERED — OWNER-DIRECTED ORDER OVERRIDE  
**Accepted parent floor:** `DAA_GRID_SYSTEM_BUILD_01_STATE_SKELETON`

## Owner-directed objective

Aggressively develop **session awareness** and **timeframe awareness** before the remaining whole-grid dimensions.

The objective is not merely to add session/timeframe filters. It is to make the grid morph intelligently across:
- Asia;
- London open / London;
- London–New York overlap;
- New York;
- late New York / rollover / transitions;

while assigning different jobs to different horizons so higher-timeframe context can support high-velocity tick/M1-style scalping without destroying opportunity density.

The grid remains support infrastructure for R9 REAL and a future 6–16 specialist portfolio.

## Immutable constraints

- XAUUSD only.
- Fixed 0.01 lot only.
- Martingale prohibited.
- Loss-dependent sizing prohibited.
- Main `delta` branch read-only.
- August 2026 sealed.
- MQL5 unauthorized.
- Ordered executable Bid/Ask accounting mandatory.
- No future-bar leakage.
- No majority-vote MTF confluence.
- Session/timeframe mechanics must have distinct roles.

## Research surface

Canonical source:
`XAUUSD_DUKAS_2026_01_ticks.csv.gz`
SHA-256 must match the retained January manifest.

Primary friction surface:
`DUKAS_COINEXX_LIKE_P75`.

January is split before mechanism refinement:
- **Discovery:** 2026-01-01 00:00 UTC through 2026-01-18 12:00 UTC exclusive.
- **Validation:** 2026-01-18 12:00 UTC through 2026-02-01 00:00 UTC exclusive.

Full-January metrics are reported only after a mechanism survives the discovery/validation split.

## Benchmark references

January R9 REAL:
- net: -$6,651.62
- trades: 31,915

January R9 SYNTH:
- net: +$41,520.82
- trades: 27,980

The 30% global milestone is **not** a hard gate for this dimension. Session/timeframe work should seek the strongest robust January improvement first. Global 30/60/90/100% attainment is judged later after multiple system dimensions are integrated.

## Research policy

Public GitHub is a first-class community source.

Promote only reconstructible mechanics. Missing-license repositories are conceptual evidence only unless clean-room reimplemented.

The research sequence is:

1. inspect public session-aware and MTF/scalping mechanisms;
2. inspect retained main-`delta` session/MTF research only as comparative evidence, never as active code authority;
3. freeze a small high-impact mechanism shortlist;
4. build a portable January tick-level research harness;
5. test mechanics individually on discovery;
6. combine only complementary survivors;
7. generate original high-performance mutations from observed failure modes;
8. retest on discovery;
9. validate the strongest frozen candidates on the untouched January validation partition;
10. persist every accepted child as the new floor for this dimension.

## Required session/timeframe categories

### Session state

At minimum:
- ASIA;
- LONDON_OPEN;
- LONDON;
- OVERLAP;
- NEW_YORK;
- LATE_NY;
- ROLLOVER_TRANSITION.

DST-safe UTC rules are mandatory.

### Timeframe roles

No timeframe voting.

Candidate role separation:
- H4/H1: parent trend/volatility environment;
- M15/M5: structural phase and pullback/expansion state;
- M1/ticks: event timing and executable path.

Alternative role families are allowed if public evidence or January diagnostics support them.

## Mandatory metrics

Per candidate:
- discovery and validation net;
- gross profit/loss;
- PF;
- expected payoff;
- trades and trades/day;
- win rate;
- max balance and equity drawdown;
- holding-time distribution;
- session contribution ledger;
- timeframe-state contribution ledger;
- long/short contribution;
- forced-boundary liquidations;
- $100/$200/$300 theoretical equity-path survivability;
- comparison with current grid floor and January R9 REAL/SYNTH references.

## Anti-overfit rule

No candidate becomes accepted because it wins only in one session, one week, or one side of the discovery partition.

Threshold polishing after observing validation is prohibited.

## Current research-order override

The previous next unit `DAA_GRID_SYSTEM_BUILD_02_ELASTIC_GEOMETRY_PREREG` is **PAUSED**, not deleted.

Current next unit after this preregistration:
`DAA_GRID_SESSION_TIMEFRAME_SOURCE_HUNT_001`.
