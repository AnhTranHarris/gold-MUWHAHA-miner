# DELTA GOV-005 — Provisional Candidate Improvement Gate

**Effective:** 2026-10-01  
**Branch:** `delta`  
**Status:** MANDATORY / HUMAN-REVISABLE  
**Evidence loading:** NOT AUTHORIZED

## 1. Scope first

Before testing, the owner defines:
- research scope;
- target area;
- candidate hypothesis/system/specialist/idea being evaluated;
- which primary metric or metrics the candidate is intended to improve.

Primary human metrics:
- winning trade count;
- net profit;
- gross loss;
- maximum drawdown.

All four primary metrics must still be reported whenever the evidence supports them, even if only one is the declared target.

## 2. Hard improvement gate

A candidate satisfies the initial hard numerical improvement requirement when **at least one owner-targeted primary metric improves by 80% or more versus the R9 REAL baseline**.

- **Hard minimum improvement target:** 80%.
- **Soft preferred improvement target:** 85%.

If the owner declares one target metric, that metric must reach at least 80% improvement.
If the owner declares several target metrics, at least one must reach 80% unless the owner explicitly requires simultaneous passes across multiple metrics.

Reaching 85% or more is preferred but is not, by itself, a separate mandatory pass condition.

## 3. Direction of improvement

All percentage comparisons are directional so that “improvement” and “deterioration” mean the same thing across metrics.

### Winning trade count
Higher is better.

`improvement_pct = 100 * (candidate - baseline) / abs(baseline)`

### Net profit
Higher is better.

For a nonzero baseline:

`improvement_pct = 100 * (candidate - baseline) / abs(baseline)`

This correctly scores movement from a losing baseline toward zero or into profit as improvement.

### Gross loss
Lower absolute loss magnitude is better.

`improvement_pct = 100 * (abs(baseline) - abs(candidate)) / abs(baseline)`

### Maximum drawdown
Lower drawdown magnitude is better.

`improvement_pct = 100 * (baseline - candidate) / abs(baseline)`

If a baseline denominator is zero, percentage comparison is undefined and the unit must use a separately owner-approved absolute rule.

## 4. Cross-metric protection floor

A candidate may not buy a large gain in one primary metric by catastrophically damaging another primary metric.

For every supported primary metric, calculate its directional percentage change versus R9 REAL.

### Investigation warning

If **any primary metric deteriorates by 17% or more but less than 25%**, the candidate receives:

`WARNING_INVESTIGATE_METRIC_DEGRADATION`

The candidate is not automatically failed at this warning level, but the degraded metric must be flagged for diagnosis and attempted improvement during refinement.

### Hard floor failure

If **any primary metric deteriorates by 25% or more**, the candidate receives:

`HARD_FAIL_PRIMARY_METRIC_FLOOR`

This hard failure overrides an 80% or 85% improvement achieved in another metric.

In normalized directional-score terms:
- improvement score `<= -25%` = hard fail;
- improvement score from `-25%` exclusive through `-17%` inclusive = warning/investigation;
- improvement score better than `-17%` = no degradation warning from this rule.

## 5. Stage-A decision logic

The default provisional Stage-A evaluation order is:

1. Verify all supported primary metrics are calculated correctly.
2. Apply the 25% cross-metric hard floor.
3. Apply the 17% degradation warning.
4. Check whether at least one owner-targeted metric reaches the 80% hard improvement target.
5. Mark 85% or greater on a targeted metric as the soft preferred target.
6. Retain all warnings and companion activity metrics in the promotion record.

Default labels:
- any primary metric deteriorates by 25% or more -> `HARD_FAIL_PRIMARY_METRIC_FLOOR`;
- no hard-floor breach, but a primary metric deteriorates by 17% to under 25% -> add `WARNING_INVESTIGATE_METRIC_DEGRADATION`;
- targeted metric reaches 85% or more -> `SOFT_PREFERRED_TARGET_MET`;
- targeted metric reaches 80% to below 85% -> `HARD_GATE_MET`;
- no targeted metric reaches 80% -> `HARD_GATE_NOT_MET`.

A warning may coexist with `HARD_GATE_MET` or `SOFT_PREFERRED_TARGET_MET`; it requires investigation but does not automatically prevent Stage-B eligibility unless another owner rule says otherwise.

## 6. Activity visibility

Every scorecard must also show:
- total trade count;
- opportunity count when available;
- winning trade count;
- losing trade count;
- trade-count retention;
- average net profit per trade when supported.

This prevents favorable headline metrics from hiding severe activity collapse.

## 7. Human-review authority

This contract is intentionally provisional and human-revisable.

After reviewing actual data, the owner may:
- change the 80% hard target;
- change the 85% preferred target;
- change the 17% warning threshold;
- change the 25% hard deterioration floor;
- require multiple primary metrics to pass simultaneously;
- add or remove target metrics;
- reject a mathematically passing candidate;
- continue investigating a numerically failing candidate;
- redefine the research target area.

Threshold changes apply prospectively unless the owner explicitly requests retrospective rescoring.

## 7A. Escalation to cumulative lock

If a primary metric reaches at least 87% of its directional progress from R9 REAL toward R9 SYNTH, `DELTA_GOV_006_SYNTH_METRIC_LOCK_AND_CUMULATIVE_RATCHET_CONTRACT.md` activates for that metric.

Once locked, the metric is no longer governed only by this contract's general 17% warning / 25% hard floor. The stricter 5% locked-metric preservation floor applies.

## 7B. Specialist versus composite interpretation

Under GOV-008, a narrow specialist is evaluated against its declared scoped baseline population. It is not required to independently solve all four system-wide primary metrics.

The assembled composite system is the canonical object for whole-system promotion and aggregate primary-category progress. The 17% warning and 25% hard floor must use the same declared scope as the numerator/denominator comparison; DELTA may not switch between specialist-scope and whole-system baselines after observing results.

## 8. Research-speed interaction

The first 2.5 weeks of January remain the fast filter/development window.

Passing this provisional gate makes a candidate numerically eligible for January-through-July bounded month-by-month research, subject to all other DELTA governance.

This contract defines scoring semantics only and does **not** authorize loading blocked R9 REAL, R9 SYNTH, R9 OVERFIT, ticklog, or Coinexx report evidence.
