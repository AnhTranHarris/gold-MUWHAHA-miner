# BETA064 CHECKPOINT 02 — Dual Tick Replay SYNTH vs Dukascopy Entry→Hold Diagnostic

**Date:** 2026-09-30  
**Branch:** `beta`  
**Status:** DIAGNOSTIC ONLY — CHECKPOINT 01 FROZEN — HOLD+EXIT DEFERRED — AUGUST SEALED

## Objective

Run month-by-month parallel tick-level diagnostics between:

1. frozen BETA064 Major Checkpoint 01 on Dukascopy XAUUSD raw ticks; and
2. R9 SYNTH ticklog chronology,

to identify which SYNTH Entry→Hold opportunities have comparable BETA market states, which transfer to real Dukascopy path behavior, and which are lost by the frozen router / one-position ownership.

Checkpoint 01 is not retuned during this diagnostic.

## Execution / labeling contract

- January through July 2026 only.
- August is not read.
- BUY entry at observed Ask, valued on observed Bid.
- SELL entry at observed Bid, valued on observed Ask.
- $0.02 research lifecycle charge.
- same causal specialist definitions E1–E12.
- same specialist-specific horizon and Hold checkpoint.
- path label: favorable first passage vs adverse/thesis-failure first passage.
- future path is used only for offline labels.
- Hold+Exit optimization is out of scope.

## Authoritative R9 SYNTH entry counts

| Month | R9 SYNTH entries |
|---|---:|
| Jan | 27,980 |
| Feb | 33,523 |
| Mar | 40,985 |
| Apr | 31,758 |
| May | 28,913 |
| Jun | 31,801 |
| Jul | 24,382 |
| **Total** | **219,342** |

## Strict same-time / same-specialist replay

For every SYNTH entry, reconstruct the causal specialist state and then inspect the corresponding Dukascopy market time.

Definitions:

- `mapped_to_E1_E12`: SYNTH entry maps into at least one frozen specialist state.
- `synth_entryhold_survive`: mapped SYNTH entry survives its specialist-specific Entry→Hold checkpoint.
- `beta_same_state`: at the same calendar time, Dukascopy exhibits the comparable frozen specialist state.
- `transferable_real_survive`: the same-state Dukascopy opportunity also survives the real Entry→Hold path.

| Month | SYNTH | SYNTH E1–E12 mapped | SYNTH Entry→Hold survive | Same BETA state | Real-path transferable |
|---|---:|---:|---:|---:|---:|
| Jan | 27,980 | 11,139 | 9,156 | 3,139 | 350 |
| Feb | 33,523 | 12,609 | 10,496 | 3,507 | 489 |
| Mar | 40,985 | 15,766 | 13,196 | 4,345 | 623 |
| Apr | 31,758 | 12,539 | 10,225 | 3,547 | 444 |
| May | 28,913 | 12,156 | 9,826 | 3,457 | 384 |
| Jun | 31,801 | 12,931 | 10,410 | 3,425 | 407 |
| Jul | 24,382 | 10,601 | 8,501 | 2,963 | 268 |
| **Total** | **219,342** | **87,741** | **71,810** | **24,383** | **2,965** |

Aggregate interpretation:

- 40.00% of all SYNTH entries map into the frozen E1–E12 state taxonomy.
- 32.74% of all SYNTH entries both map and survive the SYNTH Entry→Hold checkpoint.
- only 33.95% of those SYNTH Entry→Hold survivors have the same BETA state at the corresponding Dukascopy time.
- only 12.16% of the same-state opportunities also survive the real Dukascopy Entry→Hold path.
- therefore only 4.13% of SYNTH Entry→Hold survivors are directly transferable under this strict same-time definition.

This is the central Checkpoint-02 finding.

## Coverage deficit decomposition

Compared with 71,810 SYNTH Entry→Hold-surviving opportunities:

- **47,427** are lost because the comparable BETA specialist state is absent at the same real-market time;
- **21,418** form a comparable BETA state but fail the real Dukascopy Entry→Hold path;
- **2,965** survive both state and real path and are candidate transferable opportunities.

Checkpoint 01 executes 2,097 one-position trades. Relative to the 2,965 transferable candidates, the frozen router / one-position ownership captures about **70.7%**.

Thus the deficit hierarchy is:

`state/path transfer >> router/ownership`

The 0.88 survivability gate is not the primary explanation for the giant SYNTH coverage gap.

## Month-by-month deficit decomposition

| Month | SYNTH Entry→Hold | State absent | Real path fails after state match | Transferable | Checkpoint-01 trades |
|---|---:|---:|---:|---:|---:|
| Jan | 9,156 | 6,017 | 2,789 | 350 | 278 |
| Feb | 10,496 | 6,989 | 3,018 | 489 | 337 |
| Mar | 13,196 | 8,851 | 3,722 | 623 | 568 |
| Apr | 10,225 | 6,678 | 3,103 | 444 | 274 |
| May | 9,826 | 6,369 | 3,073 | 384 | 249 |
| Jun | 10,410 | 6,985 | 3,018 | 407 | 261 |
| Jul | 8,501 | 5,538 | 2,695 | 268 | 130 |

## Independent feature-analog diagnostic

A second diagnostic does not require exact same-time state identity.

SYNTH candidates were grouped by frozen specialist and BETA predicted-survivability bin, then compared with Dukascopy candidates in the same specialist/bin.

Across Jan-Jul:

- 72,184 SYNTH entries were condition-matched by specialist/state bin;
- 57,645 (79.86%) survived their SYNTH Hold checkpoint;
- only 5,760 belonged to real-state bins with at least 30% observed Dukascopy survivability;
- only 520 belonged to bins with at least 50% observed Dukascopy survivability.

Monthly raw candidate survivability was consistently much higher in SYNTH than Dukascopy:

| Month | Dukascopy candidate survival | SYNTH candidate survival |
|---|---:|---:|
| Jan | 14.60% | 66.42% |
| Feb | 16.89% | 68.34% |
| Mar | 18.75% | 69.88% |
| Apr | 13.73% | 66.83% |
| May | 13.70% | 66.20% |
| Jun | 14.30% | 66.36% |
| Jul | 11.23% | 65.59% |

This independently confirms that the main problem is not only exact timestamp/state matching. The SYNTH path itself grants far more Entry→Hold persistence.

## Specialist attribution

Strict replay totals:

| Specialist | SYNTH Entry→Hold | Same BETA state | Real-path transferable |
|---|---:|---:|---:|
| E6 Value Reversion | 46,648 | 23,219 | 2,728 |
| E7 Sweep/Reclaim | 7,295 | 477 | 101 |
| E12 Failed Expansion | 5,403 | 208 | 55 |
| E10 Compression Release | 5,126 | 247 | 42 |
| E8 Level Bounce | 3,331 | 142 | 24 |
| E5 VWAP Reclaim | 1,829 | 36 | 12 |
| E9 Level Break | 1,254 | 46 | 2 |
| E2 Pullback/Reaccel | 289 | 0 | 0 |
| E3 ORB | 287 | 4 | 1 |
| E11 Kinetic Ignition | 246 | 4 | 0 |
| E4 VWAP Pullback | 66 | 0 | 0 |
| E1 Macro Trend | 36 | 0 | 0 |

E6 currently supplies about 92% of all strict transferable opportunities.

This concentration is undesirable for a supposedly broad specialist firm and identifies a major Checkpoint-02 research target: improve genuinely orthogonal real-market opportunity recognition rather than adding more E6-like variants.

## Most important missed-opportunity mechanisms

### 1. State non-transfer

The largest numerical loss is that a SYNTH specialist state frequently does not exist on the real Dukascopy path at the same moment.

This is extreme for E7, E12, E10, E8, E5 and E9, where roughly 93–98% of SYNTH Entry→Hold opportunities lack an exact same-time real-state counterpart.

This is consistent with SYNTH generating cleaner sequential structures that satisfy frozen specialist conditions more often.

### 2. Real-path failure after state transfer

Even when the comparable state exists, most opportunities fail the real Hold checkpoint.

Examples:

- E6: 23,219 same-state → 2,728 real survivors.
- E7: 477 → 101.
- E10: 247 → 42.
- E9: 46 → 2.

The real path is substantially less persistent than the SYNTH path.

### 3. Specialist concentration / missing orthogonal coverage

E1/E2/E4 have effectively no strict same-time transferable opportunities in this comparison. E3/E11 are nearly absent.

This does not prove those economic mechanisms do not exist in real Gold. It says the current frozen definitions do not reproduce the SYNTH Entry→Hold opportunities at the same times.

They require diagnostic redesign / broader causal state recognition before any gate loosening.

### 4. Router / one-position loss is secondary

2,965 opportunities survive state + real path; Checkpoint 01 executes 2,097.

Recovering some of the remaining 868 may be useful later, but even recovering all 868 cannot approach the requested 85% SYNTH coverage.

Therefore Checkpoint 02 must focus first on missing real-market states and real-path survivability.

## Session / hour attribution

Strict same-time transfer is weakest in Asian/early hours and somewhat less poor later in the day.

Session transfer rates:

- Asia/Other: 2.78%
- London AM: 4.25%
- NY overlap: 4.68%
- NY PM: 4.94%

The state-absence rate falls materially into later NY hours. This suggests session-specific specialist definitions may recover legitimate real opportunities without weakening the universal survivability floor.

## Quant decision

Checkpoint 01 remains frozen.

Checkpoint 02 has established that the path to 85% condition-matched coverage is **not**:

- lower the 0.88 survivability threshold;
- copy more SYNTH entries;
- optimize Hold+Exit;
- simply increase one-position capacity.

The next Entry→Hold research loop should instead:

1. preserve Checkpoint-01 as control;
2. create diagnostic children for underrepresented specialists;
3. target real-market causal equivalents of SYNTH E7/E12/E10/E8/E5/E9 states;
4. treat E6 as the current control specialist rather than expanding it first;
5. use session-aware and cross-scale state descriptors to find real equivalents;
6. require each recovered opportunity family to pass >=85% Entry→Hold survivability on its own or in the routed portfolio;
7. report incremental coverage vs the 71,810 SYNTH Entry→Hold denominator;
8. keep Hold+Exit deferred;
9. keep August sealed.

## Current status

Checkpoint-01 survivability target: **PASS**.

Checkpoint-02 85% condition-matched trade-coverage target: **NOT YET MET**.

Primary deficit: **SYNTH-to-real state/path transfer**, not router strictness.

No MQL5 promotion.
