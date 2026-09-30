# BETA064 MAJOR CHECKPOINT 01 — ENTRY→HOLD SURVIVABILITY FREEZE

**Freeze date:** 2026-09-30  
**Branch:** `beta`  
**Status:** MAJOR CHECKPOINT 01 — FROZEN RESEARCH BASELINE  
**EA promotion:** NO  
**MQL5 authorization:** NO  
**August:** SEALED

## Frozen architecture

This checkpoint freezes the complete BETA064-R1B2 two-floor Entry→Hold architecture without modification:

`market state → eligible ENTRY specialists → survivability/economic router → fill/thesis packet → HOLD specialists → shared continuation-value arbiter`

ENTRY floor:
- E1 Macro Structural Trend
- E2 Structural Pullback / Reacceleration
- E3 Opening Range Break
- E4 VWAP / Value Trend Pullback
- E5 VWAP / Value Reclaim
- E6 Statistical Value Reversion
- E7 Liquidity Sweep / Reclaim
- E8 Key-Level Bounce / Rejection
- E9 Key-Level Break / Acceptance
- E10 Compression → Expansion
- E11 Kinetic Ignition
- E12 Failed Expansion / Contradiction

HOLD floor:
- H1 Ignition Confirmation
- H2 Extension / Runner Persistence
- H3 Healthy Pullback
- H4 Reacceleration
- H5 Transient Scalp / Fragile Continuation
- H6 Stall / Chop
- H7 Failed Acceptance / Thesis Failure
- H8 Exhaustion / Climax

Frozen gates:
- `P_survive >= 0.88`
- `Entry economic score >= 0.30`
- one-position chronological ownership
- BUY at observed Ask / value at observed Bid
- SELL at observed Bid / value at observed Ask
- fee assumption $0.02
- August sealed

## Checkpoint-01 observed Jan-Jul panel

| Month | Entry→Hold trades | Survivability |
|---|---:|---:|
| Jan | 278 | 92.45% |
| Feb | 337 | 87.83% |
| Mar | 568 | 88.91% |
| Apr | 274 | 90.15% |
| May | 249 | 92.77% |
| Jun | 261 | 91.95% |
| Jul | 130 | 94.62% |
| **Total** | **2,097** | **90.56% weighted** |

This is now the immutable comparison baseline for subsequent coverage research. Any future experiment must be reported as a delta versus this checkpoint and must not silently retune or overwrite it.

## Authoritative supporting commits

- specialist registry / gates: `1a7a46bd3fc3c9139881c861cda825a0881be5b6`
- full R1B2 survivability record: `6734cb20906a9c27227fdffdc5039ab70cf9a2f1`
- R1B architecture/source audit: `a213944a354981762763c33bdf8cbc84fe7caabe`

## Next research question — SYNTH condition-matched coverage

The next question is explicitly:

> Does Checkpoint-01 Entry→Hold trade count achieve **>=85%** of the monthly R9 SYNTH opportunity/trade count under **comparable market conditions**?

This is NOT the same as comparing 2,097 trades directly to all 219,342 R9 SYNTH trades.

The authoritative R9 SYNTH MT5 report contains 219,342 total trades. Direct extraction of monthly entry counts gives:

| Month | All R9 SYNTH trades |
|---|---:|
| Jan | 27,980 |
| Feb | 33,523 |
| Mar | 40,985 |
| Apr | 31,758 |
| May | 28,913 |
| Jun | 31,801 |
| Jul | 24,382 |
| **Total** | **219,342** |

Therefore raw all-trade coverage is only:

| Month | BETA Ckpt-01 | All SYNTH | Raw coverage |
|---|---:|---:|---:|
| Jan | 278 | 27,980 | 0.99% |
| Feb | 337 | 33,523 | 1.01% |
| Mar | 568 | 40,985 | 1.39% |
| Apr | 274 | 31,758 | 0.86% |
| May | 249 | 28,913 | 0.86% |
| Jun | 261 | 31,801 | 0.82% |
| Jul | 130 | 24,382 | 0.53% |
| **Total** | **2,097** | **219,342** | **0.96%** |

This raw comparison is a diagnostic only and is **not** the requested condition-matched coverage metric.

## Condition-matched denominator required

For each month, reconstruct the SYNTH market state using the same causal state definitions used by Checkpoint-01 and count only opportunities that fall into a comparable Entry specialist family/state.

Required denominator:

`Comparable_SYNTH_m = count(SYNTH opportunities eligible for E1..E12 under frozen causal definitions)`

Primary coverage metric:

`Coverage_m = Checkpoint01_EntryHoldTrades_m / Comparable_SYNTH_m`

Pass gate:
- each month >=85%, and
- Jan-Jul aggregate >=85%.

Also report:
- coverage by Entry specialist;
- coverage by timeframe family;
- coverage by session/regime;
- opportunity-normalized trades per active hour/day;
- whether any apparent shortfall is caused by BETA abstention, one-position ownership, spread/friction feasibility, or missing specialist coverage.

The Checkpoint-01 architecture and thresholds are frozen during this measurement. No tuning is allowed until the coverage deficit is measured and attributed.

## Scientific interpretation

If condition-matched coverage is >=85% while survivability remains >=85%, the Entry→Hold architecture has simultaneously achieved high quality and high coverage relative to SYNTH-like opportunity states.

If coverage is <85%, the next optimization target becomes **orthogonal opportunity recovery**, not loosening the survivability gate indiscriminately.

August remains sealed throughout this comparison.
