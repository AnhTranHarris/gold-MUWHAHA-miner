# DELTA GOV-006 — SYNTH Metric Lock and Cumulative Ratchet Contract

**Effective:** 2026-10-01  
**Branch:** `delta`  
**Status:** MANDATORY / HUMAN-REVISABLE  
**Evidence loading:** NOT AUTHORIZED

## 1. Purpose

DELTA must improve cumulatively rather than repeatedly sacrificing already-solved primary metrics.

When a candidate brings a primary human metric sufficiently close to the corresponding R9 SYNTH performance reference, that metric and the candidate version that achieved it become a protected research anchor.

Future research then concentrates on the remaining unlocked primary metrics while preserving all previously locked performance.

## 2. Primary metrics eligible for locking

The four lockable primary metrics are:
- winning trade count;
- net profit;
- gross loss;
- maximum drawdown.

Each metric is evaluated independently.

A candidate may lock one, several, or eventually all four metrics.

## 3. The 87% SYNTH lock threshold

A primary metric becomes eligible for lock when the candidate reaches at least **87% of the directional performance journey from R9 REAL to R9 SYNTH** for that metric.

DELTA defines:

`synth_progress_pct = 100 * directional(candidate - REAL) / directional(SYNTH - REAL)`

where the direction is chosen so positive progress always means improvement.

For higher-is-better metrics:
- winning trade count;
- net profit;

use:

`synth_progress_pct = 100 * (candidate - REAL) / (SYNTH - REAL)`

when `SYNTH > REAL`.

For lower-is-better metrics:
- gross-loss magnitude;
- maximum drawdown;

use:

`synth_progress_pct = 100 * (REAL - candidate) / (REAL - SYNTH)`

when `SYNTH < REAL`.

Interpretation:
- 0% = R9 REAL level;
- 87% = lock threshold;
- 100% = R9 SYNTH level;
- above 100% = candidate has exceeded the SYNTH reference in that metric.

If the R9 SYNTH value is not directionally better than R9 REAL for a metric, or if the denominator is zero/undefined, that metric cannot automatically lock from this formula and requires an owner-approved alternate rule.

## 4. Lock event

When a candidate reaches `synth_progress_pct >= 87%` for a primary metric:

1. the metric receives status `LOCKED_AT_87_SYNTH_OR_BETTER`;
2. the exact candidate/version becomes the **lock anchor candidate**;
3. the exact metric value, REAL reference, SYNTH reference, progress percentage, data window, code commit, configuration, and result identity are preserved;
4. future research in that lineage must build from that candidate or from a descendant that preserves every existing lock.

A lock is not inferred from memory or a summary. It must be supported by a durable result artifact once evidence loading/testing is authorized.

## 5. Five-percent preservation rule

After a metric is locked, no descendant candidate may deteriorate that metric by **5% or more relative to the locked anchor value**.

For higher-is-better locked metrics:

`retention_pct = 100 * descendant / locked_value`

A descendant must retain **more than 95%** of the locked value.

For lower-is-better locked metrics, compare deterioration in magnitude:

`deterioration_pct = 100 * (descendant - locked_value) / abs(locked_value)`

A descendant must keep deterioration **below 5%**.

A deterioration of **5% or more** produces:

`HARD_FAIL_LOCKED_METRIC_PRESERVATION`

This failure applies even if another previously unlocked metric improves dramatically.

## 6. Cumulative lock inheritance

Locks accumulate.

Example sequence:

`Candidate A locks Net Profit`

then research targets the remaining metrics.

If:

`Candidate B descends from A and locks Winning Trade Count`

then Candidate B and every later descendant must preserve:
- the Net Profit lock inherited from A; and
- the Winning Trade Count lock established by B.

If a later Candidate C locks Maximum Drawdown, all three locks become simultaneous constraints.

No later research unit may silently discard an earlier lock.

## 7. Ratchet behavior

A locked metric may improve further.

If a descendant produces a directionally better value for an already locked metric and that descendant is otherwise accepted as the new lineage anchor, DELTA may ratchet the lock upward to the new better value.

A lock may:
- stay unchanged; or
- move to a better value.

A lock may never be relaxed to a worse anchor value without explicit owner authorization.

This creates a monotonic research ratchet.

## 8. Research targeting after a lock

Once one or more metrics are locked, default research priority moves to the remaining unlocked primary metrics.

Candidate manifests must identify:
- locked metrics inherited from the parent;
- their anchor values;
- their 5% preservation boundaries;
- currently targeted unlocked metrics;
- whether the experiment is expected to affect any locked metric.

The Python research process may still alter architecture, features, parameters, specialists, routing, entry, hold, exit, or other mechanisms, but every resulting candidate must satisfy all inherited lock floors.

## 9. Interaction with GOV-005

GOV-005 remains the provisional initial candidate-improvement gate.

GOV-006 adds a stricter preservation rule after a metric reaches the 87% R9 SYNTH threshold.

Therefore:
- before a metric is locked, GOV-005's 17% warning and 25% hard deterioration floor apply;
- after a metric is locked, GOV-006's **5% locked-metric deterioration hard floor** applies to that metric;
- the stricter applicable rule wins.

## 10. Human-review authority

This lock policy is human-revisable.

The owner may later change:
- the 87% SYNTH lock threshold;
- the 5% preservation tolerance;
- the method used to measure SYNTH attainment;
- whether a lock is applied automatically or only after human confirmation;
- whether a particular research scope may temporarily relax a lock.

Unless explicitly changed, the default is automatic lock eligibility at 87% and hard failure at 5% or greater deterioration.

## 11. No evidence-load authorization

This contract defines future scoring and lineage behavior only.

It does **not** authorize loading R9 REAL, R9 SYNTH, R9 OVERFIT, ticklog, or Coinexx report evidence. Existing owner evidence-loading restrictions remain active.
