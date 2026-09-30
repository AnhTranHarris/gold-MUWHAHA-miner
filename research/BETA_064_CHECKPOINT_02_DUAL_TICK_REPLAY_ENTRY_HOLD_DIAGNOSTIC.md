# BETA064 Checkpoint 02 — Dual Tick Replay Entry→Hold Diagnostic, Jan-Jul 2026

**Date:** 2026-09-30  
**Branch:** `beta`  
**Status:** DIAGNOSTIC COMPLETE — ENTRY→HOLD ONLY  
**Feeds:** Dukascopy XAUUSD raw ticks + R9 MT5 SYNTH ticklog  
**August:** SEALED  
**Hold+Exit:** DEFERRED

## Objective

Compare the causal BETA specialist universe against R9 SYNTH month by month without trying to reproduce SYNTH mechanically.

The diagnostic asks:

1. Which R9 SYNTH entries occur under conditions recognized by E1-E12?
2. Of those, which survive the same specialist-specific early Hold checkpoint?
3. Which apparent SYNTH opportunities have a comparable real-tick analogue in Dukascopy?
4. Which families are mostly synthetic path persistence?
5. Where is BETA genuinely missing recoverable Entry→Hold opportunity?

## Replay methodology

Feature/state layer:

- one-second causal state cache;
- completed five-second bars timestamped at their **right edge**;
- frozen E1-E12 specialist definitions;
- January FIT-trained BETA router used only as a diagnostic score;
- no Hold+Exit policy optimization.

Path layer:

- raw tick chronology;
- exact first observed tick at/after decision/entry;
- BUY enters Ask and marks/exits on Bid;
- SELL enters Bid and marks/exits on Ask;
- specialist-specific horizon and early Hold checkpoint;
- favorable/adverse executable first-passage barriers;
- $0.02 research lifecycle fee where P/L is reported.

Two comparison lenses were kept separately.

### Lens A — strict causal-boundary feature analogue

An actual R9 SYNTH entry is condition-matched only when a same-direction E1-E12 specialist is active at the last completed five-second decision boundary.

This is the primary conservative denominator.

### Lens B — permissive same-family / same-time sensitivity

A SYNTH Entry→Hold survivor is matched to a Dukascopy state of the same specialist/side within a ±15-second neighborhood.

This is deliberately more permissive and is reported as a sensitivity bound, not the primary denominator.

## Strict feature-analogue monthly results

| Month | R9 SYNTH entries | Condition-matched | SYNTH Entry→Hold survivors | Survivor rate within matched | Moderate real-analogue pool | Strong real-analogue pool |
|---|---:|---:|---:|---:|---:|---:|
| Jan | 27,980 | 9,180 | 7,348 | 80.04% | 595 | 31 |
| Feb | 33,523 | 10,104 | 8,197 | 81.13% | 935 | 23 |
| Mar | 40,985 | 12,803 | 10,495 | 81.97% | 1,788 | 296 |
| Apr | 31,758 | 10,344 | 8,217 | 79.44% | 695 | 25 |
| May | 28,913 | 10,125 | 7,995 | 78.96% | 662 | 97 |
| Jun | 31,801 | 10,742 | 8,422 | 78.40% | 736 | 28 |
| Jul | 24,382 | 8,886 | 6,971 | 78.45% | 349 | 20 |
| **Total** | **219,342** | **72,184** | **57,645** | **79.86%** | **5,760** | **520** |

Definitions:

- **Moderate real analogue:** SYNTH Entry→Hold survivor with at least one comparable BETA specialist score/state region where Dukascopy survival is >=30%.
- **Strong real analogue:** same, but Dukascopy survival >=50%.

The thresholds are diagnostics, not production gates.

Only about:

- **9.99%** of strict SYNTH Entry→Hold survivors fall in the moderate real-analogue pool;
- **0.90%** fall in the strong real-analogue pool.

This is the central diagnostic result.

## Candidate-level path divergence

Weighted across Jan-Jul:

- Dukascopy E1-E12 candidate survival: approximately **15.1%**
- SYNTH E1-E12 candidate survival: approximately **67.3%**

The same broad specialist state therefore survives roughly 4.5× as often in the generated SYNTH path.

January raw executable markouts show the mechanism directly:

- 250 ms: SYNTH about -$0.16 vs Dukascopy about -$0.83
- 1 s: SYNTH about -$0.09 vs Dukascopy about -$0.80
- 2 s: SYNTH about -$0.02 vs Dukascopy about -$0.79
- 5 s: SYNTH about +$0.14 vs Dukascopy about -$0.78
- 10 s: SYNTH about +$0.61 vs Dukascopy about -$0.79
- 15 s: SYNTH about +$0.76 vs Dukascopy about -$0.78

This confirms that much of the SYNTH Entry→Hold inventory is created by path persistence after entry, not by a pre-entry state that transfers to real ticks.

## Permissive same-time / same-family sensitivity

Across Jan-Jul:

- E1-E12-mapped SYNTH entries: **87,741**
- SYNTH Entry→Hold survivors: **71,810**
- a same-specialist Dukascopy state exists within the ±15-second sensitivity window for **24,383**
- only **2,965** also survive Hold on Dukascopy

Therefore:

- same-state presence among SYNTH Entry→Hold survivors: **33.95%**
- real-tick Hold survival among SYNTH Entry→Hold survivors: **4.13%**
- real-tick Hold survival conditional on a nearby same-specialist state: **12.16%**

This is a sensitivity result only. It is more permissive than the strict causal-boundary match.

## New Checkpoint-2 trade-count target

The correct future coverage target is no longer 85% of all 219,342 SYNTH trades.

Two useful bounds now exist:

### Strict causal-boundary denominator

57,645 comparable SYNTH Entry→Hold survivors.

85% coverage target:

**48,999 causal BETA Entry→Hold trades Jan-Jul**

Monthly targets:

- Jan 6,246
- Feb 6,968
- Mar 8,921
- Apr 6,985
- May 6,796
- Jun 7,159
- Jul 5,926

### Permissive sensitivity denominator

71,810 comparable SYNTH Entry→Hold survivors.

85% sensitivity target:

**61,039 trades Jan-Jul**

This is not the primary certification target.

## Specialist diagnostics

### E6 Value Reversion

Largest apparent opportunity inventory.

Feature-analogue population:
- ~50,019 mapped entries
- SYNTH survival ~81.6%
- comparable Dukascopy survival ~13.4%

Strict same-time sensitivity:
- 46,648 SYNTH Entry→Hold events
- 23,219 nearby BETA states
- 2,728 real Hold survivors
- 11.75% real survival conditional on a same-time state

Interpretation:
very large coverage opportunity, but mostly synthetic persistence. Do not simply increase E6 frequency.

Research need:
split E6 into multiple rotational subtypes and identify real-tick precursors of the small surviving subset.

### E7 Sweep / Reclaim

Feature analogue:
- 4,775 entries
- SYNTH survival ~97.6%
- Dukascopy analogue survival ~18.7%

Same-time sensitivity:
- 7,295 SYNTH Entry→Hold events
- 477 same-time states
- 101 real survivors
- 21.17% conditional real survival

Interpretation:
one of the better real-transfer families and a priority for refinement.

### E12 Failed Expansion

Feature analogue:
- 1,254 entries
- SYNTH survival ~89.8%
- Dukascopy analogue survival ~20.3%

Same-time sensitivity:
- 5,403 SYNTH Entry→Hold events
- 208 same-time states
- 55 real survivors
- 26.44% conditional real survival

Interpretation:
strong candidate for a more detailed failure-transition specialist.

### E5 VWAP Reclaim

Feature analogue:
- 1,615 entries
- SYNTH survival ~88.2%
- Dukascopy analogue survival ~14.5%

Same-time sensitivity:
- 1,829 SYNTH Entry→Hold events
- only 36 same-time states
- 12 real survivors
- **33.3% conditional real survival**

Interpretation:
small sample, but the highest same-time conditional survival among populated specialists. This should receive targeted research, not immediate promotion.

### E4 VWAP Pullback

Only 103 feature-analogue entries but ~21.2% Dukascopy analogue survival and strong diagnostic P/L in some months.

Same-time overlap is essentially absent.

Interpretation:
possible under-covered specialist family; needs more opportunity generation before conclusion.

### E10 Compression Release

Large SYNTH effect but weak real analogue:
- SYNTH survival ~81.3%
- Dukascopy analogue survival ~11.6%
- same-time conditional survival ~17.0%

Do not chase SYNTH frequency broadly.

### E8 Level Bounce

Dukascopy analogue survival ~19.3% but SYNTH economic quality is weak/negative in several months.

Not a priority until its entry economics improve.

### E9 Level Break

Weak transfer:
- Dukascopy analogue survival ~11.1%
- same-time conditional survival ~4.35%

Current E9 formulation is not a good coverage-expansion route.

### E11 Kinetic Ignition

Dukascopy analogue survival is relatively high (~21.4%) but favorable-first-passage quality is poor and average diagnostic P/L is negative.

The current kinetic definition confuses survivability with monetizable continuation.

### E1 / E2 / E3

Current formulations do not explain meaningful real-tick coverage.

Do not add frequency by loosening them.

## Session/time diagnostic

Strict same-time transfer is not uniform through the day.

Approximate transfer rates among SYNTH Entry→Hold events:

- Asia/other: 2.78%
- London AM: 4.25%
- NY overlap: 4.68%
- NY PM: 4.94%

Highest hourly transfer pockets in the diagnostic are approximately:

- 20 UTC: 6.04%
- 18 UTC: 5.56%
- 13 UTC: 5.34%
- 19 UTC: 5.12%
- 11 UTC: 5.04%
- 15 UTC: 5.03%
- 17 UTC: 4.95%

This supports session-conditioned specialist sub-routing rather than a single global threshold.

## What BETA is actually missing

The diagnostic does **not** support the idea that BETA merely needs to recover tens of thousands of currently filtered SYNTH trades.

Most SYNTH Entry→Hold winners are not transferable.

The legitimate missing opportunity is concentrated in smaller real-tick subsets:

1. **Sweep/Reclaim quality subtypes**
2. **Failed-Expansion / contradiction transitions**
3. **VWAP Reclaim**
4. **under-covered VWAP Pullback**
5. **session-conditioned Value Reversion subsets**
6. selected Level-Bounce / Kinetic states only after stronger economic qualification

The next research loop should focus on explaining the approximately **5,760 moderate real-analogue opportunities** first.

It should not target all 57,645 SYNTH Entry→Hold survivors.

## Next bounded unit

Proposed next unit:

`BETA064-C03 REAL-TRANSFER SPECIALIST DECOMPOSITION`

Goals:

- decompose E6/E7/E12/E5/E4 into causal sub-specialists;
- use raw-tick pre-entry / immediate post-fill microstructure to explain why the real-surviving subset differs;
- session-condition the router;
- retain exact right-edge timestamping;
- rebuild a causal Entry→Hold checkpoint;
- only after a new causal >=85% survivability checkpoint exists, measure progress toward the 48,999 strict 85%-coverage target.

Hold+Exit remains deferred.
