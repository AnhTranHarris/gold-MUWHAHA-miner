# BETA064 CHECKPOINT 02B — SYNTH Condition-Matched Session × Specialist Coverage Diagnostic

**Date:** 2026-09-30  
**Branch:** `beta`  
**Parent control:** BETA064 Major Checkpoint 02 — FROZEN  
**Scope:** ENTRY→HOLD diagnostics only  
**Hold→Exit:** deferred  
**August:** sealed and not read  
**Status:** DIAGNOSTIC / NO CHECKPOINT MUTATION

## Question

Using the frozen 5,070-trade session-aware BETA Major Checkpoint 02 architecture, how much of the previously established **71,810 R9 SYNTH Entry→Hold-surviving opportunity pool** is covered under comparable session × specialist conditions, and where does the remaining deficit reside?

No checkpoint thresholds, learned models, specialist definitions, session definitions, or ownership rules were changed for this diagnostic.

## Denominator

The frozen R9 SYNTH Entry→Hold pool remains:

| Month | SYNTH Entry→Hold survivors |
|---|---:|
| Jan | 9,156 |
| Feb | 10,496 |
| Mar | 13,196 |
| Apr | 10,225 |
| May | 9,826 |
| Jun | 10,410 |
| Jul | 8,501 |
| **Total** | **71,810** |

## Three different coverage measures

### 1. Gross trade-count ratio

Checkpoint 02 trades / SYNTH Entry→Hold pool:

`5,070 / 71,810 = 7.06%`

This is useful only as a headline density ratio.

It overstates condition-matched recovery because BETA now produces far more Kinetic Ignition trades than the SYNTH pool contains.

### 2. Session × specialist capacity-matched coverage

Within each session-authority × specialist cell, cap BETA recovery at the number of SYNTH Entry→Hold survivors in that same cell.

Recovered condition-matched capacity:

`3,044 / 71,810 = 4.24%`

Approximately **2,026 of the 5,070 BETA trades are excess capacity in cells already saturated relative to the SYNTH denominator**, dominated by E11 Kinetic Ignition.

Therefore **4.24%** is the more useful current condition-cell coverage metric.

### 3. Direct application of frozen BETA model gates to SYNTH

This is intentionally rejected as the principal coverage definition.

The frozen BETA survival models show severe feed covariate shift when applied directly to SYNTH:

- mean BETA candidate `P_survive`: ~0.871
- mean SYNTH candidate `P_survive`: ~0.198
- KS distance: ~0.999

The synthetic path has radically different spread/state geometry. Requiring SYNTH to pass the BETA probability gates would make the comparison circular and would not measure the owner's intended question.

The SYNTH successful path therefore defines the opportunity denominator; real Dukascopy evidence determines whether a corresponding BETA opportunity family is safe enough to recover.

## Month-by-month coverage

| Month | SYNTH Entry→Hold | BETA Ckpt-02 trades | Gross ratio | Session×specialist recovered | Condition-cell coverage |
|---|---:|---:|---:|---:|---:|
| Jan | 9,156 | 726 | 7.93% | 491 | 5.36% |
| Feb | 10,496 | 910 | 8.67% | 546 | 5.20% |
| Mar | 13,196 | 1,463 | 11.09% | 914 | 6.93% |
| Apr | 10,225 | 589 | 5.76% | 319 | 3.12% |
| May | 9,826 | 509 | 5.18% | 269 | 2.74% |
| Jun | 10,410 | 585 | 5.62% | 311 | 2.99% |
| Jul | 8,501 | 288 | 3.39% | 194 | 2.28% |
| **Total** | **71,810** | **5,070** | **7.06%** | **3,044** | **4.24%** |

The new session architecture clearly expands real trade density, but it is still far from the owner's 85% condition-matched coverage objective.

## Session attribution

| Session authority | SYNTH Entry→Hold | BETA trades | BETA survivability | Condition-cell coverage |
|---|---:|---:|---:|---:|
| UK | 7,655 | 1,722 | 90.30% | **22.50%** |
| Asia | 4,492 | 620 | 85.16% | **13.80%** |
| Australia | 12,996 | 732 | 89.21% | 5.63% |
| New York | 25,082 | 1,187 | 88.54% | 4.73% |
| Middle East | 10,475 | 468 | 86.54% | 4.47% |
| Europe | 9,683 | 341 | 85.63% | 3.52% |
| Base / unassigned | 1,393 | 0 | — | 0.00% |

The **largest absolute remaining session deficit is New York**: 23,895 condition-cell opportunities remain uncovered.

The strongest current relative recovery is UK/London.

## Specialist attribution

| Specialist | SYNTH Entry→Hold | BETA trades | BETA survivability | Condition-cell coverage | Remaining gap |
|---|---:|---:|---:|---:|---:|
| E11 Kinetic Ignition | 246 | 2,114 | 93.95% | **100.0%** | 0 |
| E9 Level Break | 1,254 | 714 | 81.79% | 56.94% | 540 |
| E5 VWAP Reclaim | 1,829 | 231 | 90.48% | 12.63% | 1,598 |
| E12 Failed Expansion | 5,403 | 316 | 90.51% | 5.85% | 5,087 |
| E7 Sweep/Reclaim | 7,295 | 255 | 87.45% | 3.50% | 7,040 |
| E4 VWAP Pullback | 66 | 2 | 100% | 3.03% | 64 |
| E6 Value Reversion | 46,648 | 1,315 | 82.05% | **2.82%** | **45,333** |
| E10 Compression Release | 5,126 | 107 | 96.26% | 2.09% | 5,019 |
| E3 ORB | 287 | 2 | 50% | 0.70% | 285 |
| E8 Level Bounce | 3,331 | 14 | 78.57% | 0.42% | 3,317 |
| E1 Macro Trend | 36 | 0 | — | 0% | 36 |
| E2 Pullback/Reaccel | 289 | 0 | — | 0% | 289 |

### Central finding

**E6 Value Reversion alone represents 45,333 uncovered SYNTH Entry→Hold opportunities — about 63.1% of the entire 71,810 denominator.**

Checkpoint 02 is therefore no longer primarily a general “more specialists” problem.

It is predominantly a **real-market reversion-state discrimination problem**.

## Session × specialist priority

Largest uncovered cells:

| Session × specialist | SYNTH pool | Current matched | Gap | Current broader admissible survivability |
|---|---:|---:|---:|---:|
| NY × E6 Value Reversion | 17,186 | 446 | **16,740** | 83.40% |
| Middle East × E6 | 8,153 | 89 | **8,064** | 75.42% |
| Australia × E6 | 7,035 | 50 | **6,985** | 84.38% |
| Europe × E6 | 6,570 | 129 | **6,441** | 79.77% |
| UK × E6 | 4,953 | 496 | **4,457** | 84.32% |
| NY × E7 Sweep/Reclaim | 2,587 | 59 | 2,528 | **86.16%** |
| NY × E12 Failed Expansion | 1,814 | 67 | 1,747 | 84.46% |
| Asia × E6 | 1,759 | 105 | 1,654 | 73.02% |
| Australia × E7 | 1,525 | 19 | 1,506 | **85.19%** |
| Australia × E10 Compression Release | 1,393 | 16 | 1,377 | **90.00%** |
| NY × E10 | 1,225 | 21 | 1,204 | **92.31%** |
| Australia × E12 | 1,098 | 55 | 1,043 | **93.00%** |
| Europe × E7 | 1,007 | 14 | 993 | **91.11%** |
| UK × E10 | 711 | 43 | 668 | **93.00%** |
| UK × E7 | 726 | 86 | 640 | **88.48%** |
| Asia × E12 | 666 | 37 | 629 | **90.59%** |
| Europe × E12 | 645 | 27 | 618 | **91.94%** |
| UK × E12 | 573 | 89 | 484 | **90.28%** |
| NY × E5 VWAP Reclaim | 492 | 31 | 461 | **92.16%** |
| Australia × E5 | 522 | 63 | 459 | **94.57%** |

This table separates **quality problems** from **capacity problems**.

## Remaining deficit classes

The 68,766 condition-cell gap decomposes as follows:

### A. Real analog exists, but real survivability is below 85%

- SYNTH pool in these cells: 48,201
- currently matched: 1,621
- remaining gap: **46,580**
- share of total 71,810 denominator: **64.9%**

This is the dominant problem.

Most of it is E6.

These opportunities must not be recovered by loosening the 85% requirement.

They require better causal substate discrimination.

### B. Real quality already passes, but capacity / ownership is limited

- SYNTH pool: 15,052
- currently matched: 1,068
- remaining gap: **13,984**
- currently admissible but unused real candidates: **1,951**

This is the safest near-term recovery pool.

Examples include NY E7, Australia/NY/UK E10, Australia/Europe/UK/Asia E12, and Australia/NY E5.

### C. Broader real pool passes, but the actually selected ownership sample is weak

- remaining gap: **3,751**

These require scheduling/ownership diagnostics before promotion.

### D. No selected real analog

- remaining gap: **2,568**

These are mainly low-volume E1/E2/E3/E4/E8/base states.

### E. Selected sample passes, broader real pool fails

- remaining gap: **1,883**

Do not expand these blindly; present success may depend on a narrow selected slice.

## Current architecture ceiling without new state discrimination

If every currently unused candidate in the clearly **QUALITY_PASS_CAPACITY_LIMITED** cells could be admitted with no one-position conflicts, condition-cell matched capacity would rise only from:

`3,044 → 4,995`

or:

`4.24% → 6.96%`

of the 71,810 SYNTH Entry→Hold denominator.

This is an optimistic upper bound because the 1,951 candidates cannot all necessarily fit chronological one-position ownership.

Therefore **routing/ownership optimization alone cannot solve the 85% coverage objective**.

A new causal discrimination layer is required.

## Diagnostic conclusion

Major Checkpoint 02 remains a valid frozen survivability baseline and should not be loosened.

The next research hierarchy should be:

1. **E6 Value Reversion sub-specialization by session**, beginning with UK, Australia and NY because their broader admissible E6 pools are closest to the 85% survival boundary.
2. Build separate reversion-state descriptors for:
   - session value / VWAP displacement;
   - sweep-before-reversion vs passive excursion;
   - excursion age;
   - exhaustion / failed continuation;
   - range rotation vs directional trend contamination;
   - spread/ATR burden;
   - return-to-value velocity;
   - M5/M15 structural ownership;
   - session age / overlap.
3. Do not use one universal E6 rule across Australia, Asia, Middle East, Europe, UK and NY.
4. In parallel, harvest the already-quality-passing capacity cells for E7/E10/E12/E5 through ownership-aware scheduling research.
5. Keep E11 frozen as a control; it is already over-covered relative to SYNTH and should not be expanded.
6. Keep Hold→Exit deferred.
7. Keep August sealed.

## Quant decision

**Checkpoint 02 survives this diagnostic unchanged.**

The 85% condition-matched coverage target is **not met**.

Current useful coverage:
- gross trade-count ratio: **7.06%**
- session×specialist condition-cell coverage: **4.24%**
- optimistic current-definition quality-capacity ceiling before ownership conflicts: **~6.96%**

The next material research problem is **session-conditioned E6 Value Reversion discrimination**, with a secondary ownership/capacity program for already-passing E7/E10/E12/E5 cells.

No MQL5 change.
No Hold→Exit change.
No August read.
