# DELTA GOV-007 — Creative Refinement Escalation and Dukascopy Optimization Playground

**Effective:** 2026-10-01  
**Branch:** `delta`  
**Status:** MANDATORY / HUMAN-REVISABLE  
**Evidence loading:** NOT AUTHORIZED

## 1. Purpose

DELTA research is allowed to be highly creative when a candidate is not progressing fast enough toward the owner's goals.

The Python tick-level research environment, especially the Dukascopy replay environment once evidence loading is authorized, is the primary experimental playground for repeated causal testing, restructuring, recombination, refinement, and optimization.

The objective is not to preserve the shape of a weak candidate. The objective is to preserve what works, replace what does not, and search broadly enough to reach or exceed the active DELTA goals.

## 2. Creative authority

For any candidate, DELTA may perform aggressive research changes including:
- parameter modification and broader parameter search;
- feature addition, removal, replacement, or redefinition;
- timeframe reassignment or multi-timeframe recombination;
- entry logic redesign;
- hold/persistence logic redesign;
- exit/harvest logic redesign;
- specialist decomposition or recombination;
- state-machine restructuring;
- routing/ownership redesign;
- execution-rule correction;
- volatility/regime logic changes;
- architecture simplification;
- architecture expansion when justified;
- combination of multiple independently reconstructible mechanisms;
- replacement of a weak mechanism rather than endlessly tuning it.

No candidate structure is protected merely because it existed earlier.

The protected objects are the causal rules, evidence integrity, active metric locks, and owner-defined gates.

## 3. Ten-percentage-point creative escalation trigger

For a target primary metric, measure the candidate's directional progress toward R9 SYNTH using the same SYNTH-progress definition as GOV-006.

For a child/refinement candidate:

`incremental_synth_progress_pp = child_synth_progress_pct - parent_synth_progress_pct`

If:
- the target metric remains below its active goal; and
- the child produces **less than +10 percentage points** of additional SYNTH-gap closure versus its parent;

then DELTA marks the refinement:

`CREATIVE_ESCALATION_REQUIRED`

This trigger means the current refinement path is producing insufficient incremental progress.

It does **not** mean the candidate is automatically discarded.

## 4. Required response to sub-10-point progress

When `CREATIVE_ESCALATION_REQUIRED` is triggered, DELTA should broaden the search rather than continue only with minor local tuning.

At least one subsequent research branch should test a materially different intervention, such as:
- structural logic change rather than parameter-only change;
- different timeframe interaction;
- different entry/hold/exit decomposition;
- specialist split or recombination;
- alternate state representation;
- removal of a mechanism that is suppressing progress;
- addition of a new reconstructible mechanism;
- redesigned gating/routing;
- broader but bounded configuration search.

The research record must identify what was changed and why the prior path was considered insufficient.

## 5. Dukascopy tick-level Python playground

Once evidence loading is explicitly authorized, Dukascopy tick-level Python replay is DELTA's primary experimental playground for candidate discovery and refinement.

It may be run repeatedly to:
- test hypotheses;
- compare configurations;
- search parameter neighborhoods;
- compare architectures;
- identify interaction effects;
- optimize candidate settings;
- test alternate specialists;
- evaluate combinations;
- diagnose failures;
- retest corrected versions;
- search for configurations that meet or exceed the active goals.

Repeated runs are allowed and expected.

The requirement is not “fewest experiments.” The requirement is disciplined, causal, versioned experimentation.

## 6. Multiple-run best-configuration search

DELTA may run multiple bounded experiments for the same candidate family to determine the best available settings/configuration.

Every materially different behavior/configuration receives a distinct candidate/version or deterministic experiment ID.

The search process must preserve:
- parent candidate/version;
- parameter/configuration set;
- code commit;
- data window;
- metric results;
- locked-metric preservation status;
- failure/warning labels;
- selected-best rationale.

A “best” configuration must be best under the active DELTA goals and constraints, not merely the single highest profit result.

## 7. Interaction with metric locks

Creative freedom does not override GOV-006.

If a primary metric is locked:
- every experimental descendant must preserve the active lock;
- a 5% or greater deterioration of a locked metric is a hard failure;
- the experiment may still be retained as diagnostic evidence, but it cannot become the accepted lineage parent unless the owner explicitly relaxes the lock.

This prevents creative restructuring from destroying already-secured performance.

## 8. Interaction with GOV-005

Creative refinement is evaluated under the existing provisional human gate:
- 80% hard targeted improvement threshold;
- 85% soft preferred target;
- 17% degradation warning;
- 25% primary-metric hard fail;
- any stricter inherited lock floor.

The 10-point creative-escalation trigger is a research-process rule, not a replacement for those pass/fail thresholds.

## 9. Search discipline

Creativity does not authorize:
- future leakage;
- using SYNTH/OVERFIT outcomes as live inference;
- violating right-edge timing;
- changing evaluation rules after seeing a protected result without versioning;
- hiding failed experiments;
- silently changing data boundaries;
- erasing candidate lineage;
- breaking locked metrics;
- opening sealed data.

Any such violation invalidates the affected result.

## 10. Human review

This rule is human-revisable.

The owner may later change:
- the 10-percentage-point escalation threshold;
- which interventions count as sufficiently creative;
- the search breadth;
- the number of configuration trials;
- the definition of “best” for a particular research scope.

Unless changed, DELTA should treat sub-10-point incremental SYNTH progress as a signal to broaden the search materially.

## 11. No evidence-load authorization

This contract defines research behavior only.

It does **not** authorize loading R9 REAL, R9 SYNTH, R9 OVERFIT, Coinexx reports, R9 ticklogs, or Dukascopy tick files. Existing owner evidence-loading restrictions remain active.
