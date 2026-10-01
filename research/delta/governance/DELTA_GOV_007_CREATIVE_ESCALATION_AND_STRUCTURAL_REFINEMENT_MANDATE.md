# DELTA GOV-007 — Creative Escalation and Structural Refinement Mandate

**Effective:** 2026-10-01  
**Branch:** `delta`  
**Status:** MANDATORY / HUMAN-REVISABLE  
**Evidence loading:** NOT AUTHORIZED

## 1. Purpose

DELTA research is not restricted to conservative parameter tuning.

Carson is explicitly authorized to creatively modify, adjust, repair, combine, decompose, restructure, simplify, expand, replace, or recombine candidate logic when doing so is needed to achieve the owner-defined goals.

The objective is not to preserve a weak candidate's original architecture. The objective is to preserve useful causal mechanisms while aggressively improving the system within DELTA governance.

## 2. Creative authority

Within the owner's declared research scope, Carson may change or recombine any non-locked part of a candidate, including:
- parameters and thresholds;
- feature definitions;
- feature ordering;
- timeframe usage;
- cross-timeframe state logic;
- specialist composition;
- regime/state classification;
- candidate routing;
- entry logic;
- directional selection;
- hold/persistence logic;
- exit/harvest logic;
- stop/trailing behavior;
- execution filters;
- debounce, expiry, rearm, ownership and concurrency rules;
- state-machine structure;
- signal weighting or voting;
- module boundaries;
- combination of multiple reconstructible strategies or specialists;
- simplification of unnecessary complexity;
- addition of complexity where evidence justifies it;
- replacement of a weak subsystem while retaining stronger mechanisms.

A materially behavior-changing modification creates a new candidate/version and preserves the parent result.

## 3. Sub-10% progress trigger

For a targeted primary metric, define the candidate's progress on the R9 REAL -> R9 SYNTH scale using the same directional SYNTH-progress convention in GOV-006.

For a child candidate compared with its parent or current accepted anchor:

`incremental_synth_progress_pp = child_synth_progress_pct - parent_synth_progress_pct`

If the incremental gain is **less than 10 percentage points** on the targeted R9 SYNTH progress scale, the result triggers:

`CREATIVE_REFINEMENT_REQUIRED`

This is **not** an automatic candidate failure.

It means local tuning has not produced enough movement toward the target and Carson should increase the degree of creative refinement before spending excessive compute repeating near-identical variants.

## 4. Escalation behavior

After `CREATIVE_REFINEMENT_REQUIRED`, Carson should prefer increasingly structural changes over repeated tiny parameter nudges.

Permitted escalation includes:
1. diagnose which mechanism limits the targeted metric;
2. remove or replace the limiting mechanism;
3. redesign the candidate around stronger surviving mechanisms;
4. combine complementary specialists or state models;
5. alter the timeframe/state architecture;
6. separate entry, hold, and exit responsibilities into distinct specialists;
7. introduce causal routing between specialists or regimes;
8. test materially different state-machine behavior;
9. simplify an overcomplicated candidate if complexity is reducing performance;
10. introduce additional reconstructible complexity when simple mechanisms are insufficient;
11. recombine previously successful DELTA-created mechanisms in new causal structures;
12. test alternative execution/lifecycle logic where path sensitivity is the bottleneck.

The research system should not become trapped indefinitely in a narrow parameter neighborhood after the sub-10% trigger fires.

## 5. Creative work must remain disciplined

Creative freedom does not override DELTA scientific controls.

Every experiment must still obey:
- clean-room scope;
- tick-rooted chronology;
- right-edge causality;
- deterministic reconstruction;
- candidate/version traceability;
- January filter and month-by-month durability;
- GOV-005 primary-metric floors;
- GOV-006 locked-metric preservation;
- activity/trade-count visibility;
- no future-informed inference;
- reconstructibility of public/community mechanisms;
- owner approval gates for MT5 translation and sealed data.

Creativity changes *what may be tried*, not the evidence standard required to accept it.

## 6. Locked metrics constrain creativity

When a primary metric has been locked under GOV-006, creative refinement must treat the lock as a hard design constraint.

Carson may redesign the rest of the candidate aggressively, but any descendant that deteriorates a locked metric by 5% or more from its lock anchor receives:

`HARD_FAIL_LOCKED_METRIC_PRESERVATION`

Creative escalation therefore targets the remaining unlocked weaknesses while protecting cumulative gains.

## 7. Interpretation of the 10% trigger

The 10% threshold is measured as **incremental percentage-point progress toward R9 SYNTH**, not as:
- 10% of account balance;
- 10% absolute profit;
- 10% of trade count;
- 10% degradation;
- or 10% relative change in the raw metric unless those happen to coincide.

Example:

If a parent is at 42% SYNTH progress on Net Profit and a child reaches 49%, the incremental gain is 7 percentage points. That triggers `CREATIVE_REFINEMENT_REQUIRED`.

If a child reaches 55%, the incremental gain is 13 percentage points and does not trigger this rule.

## 8. Interaction with candidate progression

A sub-10% incremental gain can still be useful evidence and remains durable.

Carson should:
- record the result;
- identify what improved and what did not;
- preserve any transferable mechanism;
- avoid discarding a useful mechanism merely because the total gain was small;
- use the result to design a more substantial next variant.

If a small-gain candidate also creates or improves a locked metric, GOV-006 remains authoritative for the lock.

## 9. Human-review authority

This mandate is human-revisable.

The owner may later change:
- the 10 percentage-point escalation trigger;
- the kinds of restructuring allowed for a particular research scope;
- whether certain candidate families should be abandoned rather than restructured;
- the amount of experimentation permitted before a structural pivot;
- any lock or preservation constraint through the appropriate governance change.

## 10. No evidence-load authorization

This contract defines Carson's future research behavior only.

It does **not** authorize loading R9 REAL, R9 SYNTH, R9 OVERFIT, ticklog, or Coinexx report evidence. Existing owner evidence-loading restrictions remain active.
