# GAMMA-02 — January M1 Density Recovery Checkpoint 002

**Status:** COMPLETE DISCOVERY CHECKPOINT — NOT YET INTEGRATED PORTFOLIO CERTIFIED  
**Parent prereg:** GAMMA_02_HTF_DIRECTED_M1_BOUNDARY_DENSITY_PREREG.md  
**Recovery after UI timeout:** exact runtime artifacts recovered; no orphan worker survived.

## Stage 1 — broad mechanism conclusions

The generic session-wide variants were mostly failures:
- all-session fresh M1 ladder: REJECTED / negative;
- generic pullback -> re-break: REJECTED / negative;
- generic favorable-extreme stair across London+Overlap+NY: REJECTED / negative.

Strict HTF ALIGN4 permission (completed H4=H1=M15=M5 != 0) changed the picture inside NY:
- step 0.40 / TP $8 / SL $3 / 15s: +$644.27, 8,213 trades, PF 1.07975;
- step 0.30 / TP $8 / SL $3 / 15s: +$638.35, 10,443 trades, PF 1.0677.

This established that high density is possible but broad hourly mixing dilutes the edge.

## Stage 2 — hour/session-phase decomposition

All figures are January discovery on ordered Dukascopy Bid/Ask and are standalone hour experiments.

### Strong positive hour specialists

| UTC hour | Phase | Step | TP | SL | Hold | Net | Trades | PF | Exp/trade | DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 11 | London | $0.10 | $6 | $2 | 30s | +$1,415.62 | 1,693 | 2.7763 | +$0.8362 | $337.19 |
| 13 | Overlap | $0.10 | $12 | $4 | 30s | +$3,712.37 | 2,376 | 3.4007 | +$1.5624 | $250.96 |
| 14 | Overlap | $0.05 | $12 | $3 | 30s | **+$5,518.51** | **7,579** | 1.8217 | +$0.7281 | $1,231.39 |
| 17 | New York | $0.10 | $10 | $3 | 30s | +$2,257.16 | 6,990 | 1.3772 | +$0.3229 | $919.55 |
| 18 | New York | $0.15 | $12 | $4 | 30s | +$2,269.59 | 4,860 | 1.3347 | +$0.4670 | $1,398.94 |

### Weak/diagnostic positive density

- 09 UTC London: +$117.41 / 6,463 trades / PF 1.0384 / +$0.0182 expectancy.
- 16 UTC NY: +$250.05 / 10,521 trades / PF 1.0374 / +$0.0238 expectancy.

These two are potentially useful **opportunity feeds** for later specialists but are not quality portfolio members yet because their raw expectancy is tiny and drawdown is large.

### Rejected hour phases

10, 12, 15, and 19 UTC were negative in this Stage-2 screen. Broad session averages therefore hide strong intraday heterogeneity.

## Interpretation

This is a major velocity discovery:
1. HTF alignment by itself is insufficient.
2. Fresh M1 favorable-extreme geometry becomes profitable when conditioned on the correct **session phase/hour**.
3. Several London/overlap/NY hours produce thousands of positive-expectancy trades.
4. Geometry/lifecycle is hour-specific; one universal fast setting is rejected.
5. High concurrency/cap materially affects some frontiers, so aggregate exposure must be measured honestly.

The standalone hour nets MUST NOT be arithmetically promoted as a portfolio result. The next required unit is one integrated ordered-tick replay with:
- one global position ledger,
- one balance/equity path,
- hour-specific geometry chosen only from this completed screen,
- explicit global concurrency caps,
- comparison of a quality portfolio versus a higher-volume portfolio.

## Durability

Exact artifacts are persisted in Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/`

Important files:
- gamma02_m1_density.py
- gamma02_m1_density_stage1_summary.json
- gamma02_hourly_geometry_stage2.json
- gamma02_hourly_geometry_stage2_summary.json
- gamma02_ny_density_aggressive.json
- gamma02_ny_rebreak_refine.json
- gamma02_ny_hour18_tight.json
- gamma02_ny_hour18_cap_frontier.json

## Next atomic unit

`GAMMA_02_M1_DENSITY_INTEGRATED_PORTFOLIO_001`

No MQL5 build. August remains sealed. R9 SYNTH remains the hard target.
