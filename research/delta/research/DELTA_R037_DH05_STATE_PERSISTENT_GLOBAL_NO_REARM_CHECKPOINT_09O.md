# DELTA R037 — DH05 State-Persistent Execution + GLOBAL NO_REARM — Checkpoint 09O

**Status:** COMPLETE NEGATIVE QA / GLOBAL NO_REARM SUPPRESSES DENSE REENTRY / SPARSE DENSITY STILL UNRESOLVED  
**Unit:** R037_DH05_STATE_PERSISTENT_EXECUTION_WITH_GLOBAL_NO_REARM_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_REVERSAL_STATE_PERSISTENT_EXECUTION_MANDATE_CHECKPOINT_09N  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Timeout / crash audit

The recent chat timeout did not corrupt durable DELTA science. The missing 09N persistence step was recovered from an already-completed official result and its final rebuild gate passed.

During the first 09O local execution attempt, Numba failed before any output was created because a cached compiled dependency referenced a prior dynamically-imported module environment named `<dynamic>`. This was a runtime cache-contamination issue, not a research or model defect.

The fix did not alter scientific source:
- exact committed 09O Git blob: `8d6968ad12a71951604c30067b4df61fe95b894e`
- producer commit: `6b808fa738f6b07368ffd6f86b916a69fd3bb889`
- producer SHA-256: `361c29ed5c72735b560b951c7f10aae8cec2afbe6112ab6c73bb76448b51e87c`
- exact 09N dependency blob: `2c37baf5c1ac3cc94de131c16185bdc8a4fcaa98`
- exact 09L dependency blob: `4b7bf08ebb0437ee02cf8c8aa48ed6987db10f9c`

The official rerun used a fresh per-unit `NUMBA_CACHE_DIR`.
Result:
- exit status: **0**
- runtime: **10.95 s**
- max RSS: **698,756 KB**
- result SHA-256: `ead3a618e7e6caaada2862f4d6784660d265b23618f8e85df14e67e3233d3b95`

No partial result from the failed attempt was promoted.

## Bounded question

Does the exact frozen R032 **GLOBAL NO_REARM** rule repair the 09N state-persistent execution mandate by preventing ordinary downstream re-entry during the same UTC minute as the prior exit?

Generator counts, reversal thresholds, failure-age semantics, and all DH05 numeric vectors remained frozen.

Two causal dispositions were tested when a confirming state transition occurred inside the same UTC minute:
- **DROP:** discard that re-entry opportunity; require a later fresh reconfirmation.
- **DEFER:** retain it until the first tick of a later UTC minute if the mandate remains valid.

## Result

The one-shot control remains aggregate six-vector trade-count absolute error **336**.
The best prior 09L clue remains **304**.

The best 09O profile is:

`REV_DISP_CHAIN__NO_REARM_DROP`

with aggregate error **338**.

Therefore 09O does **not** meet the carry-forward criterion.

### Best profile fingerprint

| Vector | Trades | Target | Reentries | Same-minute blocks |
|---|---:|---:|---:|---:|
| A03 | 194 | 306 | 2 | 32 |
| S05 | 9 | 51 | 0 | 0 |
| S06 | 650 | 615 | 1 | 64 |
| S09 | 11 | 119 | 0 | 1 |
| S10 | 230 | 206 | 3 | 53 |
| S16 | 7 | 24 | 0 | 1 |

S06 under the leading profile:
- **651 generator signals**
- **650 trades**
- **274 wins**
- **-$151.05**
- only **1** downstream state re-entry after **64** same-minute candidate reentries were suppressed.

BODY_SIGN with GLOBAL NO_REARM similarly collapses S06 reentries from 132 in 09N to **4**, while aggregate error remains **341**.

## Interpretation

GLOBAL NO_REARM is doing exactly what its parent invariant says: it prevents dense same-minute execution recycling. This substantially eliminates the state-persistence overproduction discovered in 09N.

But the historical sparse-vector density does not return:
- A03 remains **194 / 306**
- S05 remains **9 / 51**
- S09 remains **11 / 119**
- S16 remains **7 / 24**

So the missing historical mechanism is not ordinary same-minute downstream rearming.

The next causal hypothesis is now more specific and does not require a new number:

1. preserve GLOBAL NO_REARM;
2. treat the existing frozen reversal-displacement threshold as a **symmetric state band**;
3. positive displacement above the threshold confirms/reconfirms;
4. an explicit opposite displacement beyond the same threshold invalidates;
5. weak/neutral completed reversal bars do **not** automatically destroy the mandate;
6. a new executable re-entry still requires a later causal reconfirmation and cannot occur in the same UTC minute as the prior exit.

This tests whether the previous 09N state chain died too aggressively on neutral bars while retaining the execution suppression that 09O validated.

## Decision

**Checkpoint 09O = QA PASS / NEGATIVE RESULT / NO NEW SEMANTIC FREEZE.**

Preserve as validated parent constraint:
- GLOBAL NO_REARM suppresses ordinary same-minute downstream execution re-entry.

Reject as parity solution:
- first-nonconfirming-bar invalidation + GLOBAL NO_REARM;
- deferring a same-minute reconfirmation to the next minute without a new state transition.

Do not retune vectors, extend failure lifetime, access August, integrate SORB, optimize mature exits, or begin MQL5.

## Next bounded unit

`R037_DH05_GLOBAL_NO_REARM_REVERSAL_HYSTERESIS_PARITY_RECONSTRUCTION`

Test only symmetric reversal-state hysteresis using the existing frozen `revdisp_atr` quantity plus the exact GLOBAL NO_REARM rule. No new numeric threshold.
