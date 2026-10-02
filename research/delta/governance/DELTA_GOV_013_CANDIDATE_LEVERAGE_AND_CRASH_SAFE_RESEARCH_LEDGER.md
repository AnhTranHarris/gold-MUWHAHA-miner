# DELTA GOV-013 — Candidate Leverage Analysis, Crash-Safe Research Ledger, and Phase Separation

**Effective:** 2026-10-01  
**Branch:** `delta`  
**Status:** MANDATORY / HUMAN-REVISABLE  
**Current research phase:** ENTRY + INITIAL-HOLD

## 1. Purpose

DELTA_005 research must move quickly without losing scientific traceability during UI failures, timeouts, runtime crashes, or chat resets.

Every candidate revision therefore uses three persistent layers:
1. GitHub — canonical code/config/manifests/checkpoints;
2. Google Doc — durable chronological research ledger and decision record;
3. temporary Google Sheet — per-test mathematical analysis surface.

## 2. Current objective is strictly Entry + Initial-Hold

The active research objective is:

`ENTRY + INITIAL-HOLD`

Research may modify:
- entry qualification;
- entry timing;
- entry context;
- fast/slow confirmation;
- tick-flow confirmation;
- breakout/retest/reclaim logic;
- failed-break/sweep logic;
- session/regime ownership;
- first-seconds persistence;
- initial-hold hysteresis;
- early invalidation logic.

The following objective is explicitly deferred:

`HOLDING-TRADE + EXIT + HIGH-PROFIT`

DELTA must not optimize the mature-trade hold, exit/harvest, or high-profit objective as the primary target during the current phase.

Those later mechanisms may remain at the frozen R9 baseline when necessary for comparable scoring. They may be measured diagnostically, but they cannot become the main optimization target until the owner declares Entry + Initial-Hold requirements sufficiently achieved.

## 3. Pre-modification leverage analysis

Before materially modifying a candidate after a test, DELTA must perform a quick leverage analysis answering:

1. What exact formula/mechanism is limiting the candidate?
2. Which observed slice demonstrates the limitation?
3. Is the failure mainly:
   - opportunity generation;
   - entry direction;
   - entry timing;
   - false-break rejection;
   - initial-hold persistence;
   - initial-hold invalidation;
   - activity starvation;
   - session/regime routing;
   - interaction between specialists?
4. Which component has the highest plausible leverage on the owner-targeted metric?
5. Does the next intervention require:
   - `LOCAL_TUNE`;
   - `STRUCTURAL_CHANGE`;
   - `RECOMBINATION`;
   - `SPECIALIST_SPLIT`;
   - `NEW_SPECIALIST`;
   - `ROUTER_CHANGE`?
6. What magnitude of improvement would justify the modification?
7. What collateral metrics/opportunity density must be protected?

## 4. Creative escalation

If a child candidate remains below its goal and produces less than +10 percentage points of additional SYNTH-gap closure versus its parent, GOV-007 remains mandatory.

The leverage analysis must then avoid repeating low-leverage local tuning unless the test evidence specifically identifies a narrow high-sensitivity region.

The default response is a materially broader intervention.

## 5. Mathematical sensitivity requirement

After every completed test, DELTA creates a fresh temporary Google Sheet dedicated to that test/version.

The Sheet must support rapid analysis of:
- REAL baseline;
- SYNTH goal;
- parent candidate;
- tested candidate;
- directional improvement versus REAL;
- parent and candidate SYNTH-gap closure;
- incremental SYNTH progress in percentage points;
- 80% hard / 85% preferred / 87% lock surfaces;
- opportunity count;
- trade count;
- winning-trade count;
- activity retention;
- gross-loss magnitude;
- drawdown;
- Entry + Initial-Hold diagnostics;
- parameter/mechanism changes;
- sensitivity and leverage calculations;
- failure slices;
- candidate-next-change ranking.

The Sheet is an analysis surface, not the canonical scientific record.

## 6. Temporary Sheet lifecycle

Every test Sheet receives a unique identity containing:
- DELTA unit/test ID;
- candidate family;
- version;
- Stage-A/Stage-B window;
- execution surface.

The Sheet may be temporary/disposable after the analysis is complete.

Before deletion or replacement, all decision-relevant findings must already exist in:
- the master Google research Doc; and
- the corresponding GitHub candidate/result artifacts.

A Sheet link/ID must be recorded in the master Doc even if the Sheet is later retired.

## 7. Master Google Doc research ledger

A single DELTA_005 Entry + Initial-Hold Google Doc is the crash-recovery research ledger.

Before each compute run, append:
- test ID;
- candidate/version;
- parent;
- hypothesis;
- exact formula/mechanism change;
- reason for the change;
- expected high-leverage effect;
- active surface/window;
- protected metrics/locks.

After each compute run, append:
- result status;
- primary metrics;
- Entry + Initial-Hold diagnostics;
- opportunity/activity metrics;
- temporary Sheet link;
- pass/warning/fail labels;
- leverage-analysis conclusion;
- next proposed mutation;
- GitHub artifact/commit identities when available.

The research Doc must be updated before moving to the next materially different candidate version.

## 8. Entry + Initial-Hold diagnostic family

Where supported, test analysis should retain:
- opportunity count;
- selected-entry count;
- executed trades;
- unique opportunities;
- winning trades;
- false-break rate;
- immediate-stop / early-failure rate;
- hold-survival at 1s / 3s / 5s / 10s / 15s;
- MFE at 1s / 3s / 5s / 10s / 15s;
- MAE at 1s / 3s / 5s / 10s / 15s;
- continuation after threshold crossing;
- retest/reclaim success;
- tick-flow persistence;
- efficiency/hysteresis persistence;
- opportunity-to-entry conversion;
- entry-to-initial-hold survival;
- per-session/per-regime contribution.

Additional diagnostics may be added when a candidate's formula requires them.

## 9. Candidate formula change classification

Every material modification is tagged with one primary class:

- `PARAMETER_ONLY`
- `ENTRY_FORMULA_CHANGE`
- `INITIAL_HOLD_FORMULA_CHANGE`
- `ENTRY_AND_INITIAL_HOLD_CHANGE`
- `SPECIALIST_RECOMBINATION`
- `SPECIALIST_SPLIT`
- `ROUTER_CHANGE`
- `NEW_SPECIALIST`

Behavior-changing modifications always receive a new candidate/version ID.

## 10. Crash recovery

After any crash, timeout, or new chat:
1. read `CURRENT_STATE.json`;
2. read the DELTA_005 master Google Doc;
3. inspect the last completed candidate checkpoint;
4. use the last recorded temporary Sheet only for analysis details not already promoted to GitHub/Doc;
5. resume from the first missing durability step.

Do not infer a missing test result from memory.

## 11. No premature exit/harvest optimization

The current phase may use the frozen R9 lifecycle for downstream trade accounting so Entry + Initial-Hold candidates can be compared.

DELTA must not claim a Holding-Trade/Exit/High-Profit breakthrough from this phase.

That objective becomes a separate later campaign after owner approval.

## 12. August

August 2026 remains sealed.
