# DELTA GOV-003 — Research-Speed Stage-Gate Contract

**Effective:** 2026-10-01  
**Branch:** `delta`  
**Status:** MANDATORY  
**Scope:** DELTA strategy, specialist, system, mechanism, feature, model, routing, entry, hold, exit, and composite research.

## 1. Purpose

DELTA research must move quickly without sacrificing causal integrity, reproducibility, trade-activity visibility, or crash recovery.

The default research pipeline is therefore a staged funnel:

`IDEA -> JANUARY FILTER WINDOW -> JANUARY-JULY MONTH-BY-MONTH RESEARCH -> PROMOTION REVIEW`

The January filter exists to reject weak ideas cheaply and to permit bounded refinement of promising ideas before expensive seven-month research.

## 2. Stage A — January filter window

Every new strategy, specialist, idea, system, concept, feature family, state model, execution rule, or combination begins on the owner's **first 2.5 weeks of January** filter window.

The exact tick boundary for this filter window must be frozen in the candidate/unit manifest before the first compute run. Until the owner supplies the final acceptance requirements and goals, DELTA records the interval as:

`JAN_FILTER_FIRST_2P5_WEEKS — EXACT_END_BOUNDARY_PENDING_OWNER_GOALS`

No unit may silently choose a different January screening interval.

## 3. What Stage A is allowed to do

Within the January filter stage, DELTA may perform bounded:
- modification;
- correction;
- repair;
- parameter adjustment;
- optimization;
- feature removal/addition;
- state-machine repair;
- execution correction;
- specialist redesign;
- candidate combination;
- simplification;
- complexity expansion when justified;
- robustness checks.

The purpose is to determine whether the idea can satisfy the owner-defined acceptance goals efficiently enough to justify wider testing.

Every materially different trading behavior must receive a new candidate/version identifier. Earlier results remain durable and are never overwritten.

## 4. Stage A promotion gate

A candidate advances only if it passes the owner-defined requirements/goals that will be frozen separately.

Until those requirements are supplied, the promotion state is:

`THRESHOLDS_PENDING_OWNER_DEFINITION`

No profit, PF, win rate, activity level, drawdown, entry-quality, hold-quality, or other threshold may be invented by the research system.

Failed candidates remain recorded as durable negative evidence.

## 5. Stage B — January through July month-by-month research

A Stage-A survivor is tested across the complete January-through-July research period as **separate bounded monthly jobs**:

- January
- February
- March
- April
- May
- June
- July

Each month is executed independently to reduce memory/runtime pressure and prevent one long replay failure from invalidating the entire campaign.

The monthly runner must support resume-from-first-incomplete-month behavior.

## 6. Monthly durability rule

For every month, DELTA must persist before advancing:
- candidate/version ID;
- producing code commit;
- source-data identity/hash;
- exact monthly time boundary;
- config/parameters;
- metrics required by the active acceptance contract;
- opportunity count;
- selected trade count;
- trade-count retention;
- winning/losing trade counts;
- entry-quality measures;
- hold/persistence measures;
- net/PF/expectancy;
- gross profit/loss;
- drawdown;
- execution/friction measures when applicable;
- QA result;
- checkpoint status.

A completed month is never rerun merely because a later month or chat/runtime fails.

## 7. Refinement between months

January-through-July is a research/development campaign, not pristine out-of-sample validation.

After inspecting a completed month, DELTA may refine, modify, repair, optimize, or combine the candidate for subsequent research.

However:
- any behavior-changing change creates a new candidate/version;
- prior monthly results remain attached to the version that produced them;
- a revised candidate does not inherit prior-month performance as if it had produced it;
- if cross-month comparability is required, the revised version must be replayed on the relevant earlier months as separate bounded jobs;
- no monthly result may be silently rewritten.

## 8. Frozen-candidate full-window comparison

When a candidate becomes sufficiently stable for promotion review, DELTA should run that frozen candidate version across each January-through-July month without behavior changes between months.

This produces one comparable seven-month research surface while still preserving bounded monthly execution and crash recovery.

## 9. Parallel research

DELTA may evaluate multiple candidates or candidate families in parallel when runtime permits.

Parallelism must not mix:
- candidate state;
- caches;
- model artifacts;
- trade ledgers;
- result files;
- month checkpoints.

Each job receives a unique deterministic job ID.

## 10. Interaction with tick-rooted timeframe governance

All Stage-A and Stage-B tests obey `DELTA_GOV_002_TICK_ROOTED_NESTED_TIMEFRAME_CONTRACT.md`.

Ticks remain the authoritative chronology. Every requested candle is reconstructed from ticks under the frozen boundary rules.

No research-speed optimization may reduce timing fidelity or bypass right-edge causality.

## 11. Interaction with sealed data

This contract does not authorize access to sealed holdout data.

January through July remain the active development/research corpus under existing DELTA governance. Any sealed period remains sealed until separately authorized.

## 12. Default research-speed principle

Use the smallest sufficient data window and cheapest sufficient computation capable of falsifying the current idea.

Do not spend seven months of tick replay on a candidate that cannot survive the January filter.

Do not discard a January survivor merely because a later month exposes a repairable mechanism failure; preserve the failure, version the correction, and continue bounded research.

The goal is fast falsification, durable learning, controlled refinement, and eventual multi-month robustness.
