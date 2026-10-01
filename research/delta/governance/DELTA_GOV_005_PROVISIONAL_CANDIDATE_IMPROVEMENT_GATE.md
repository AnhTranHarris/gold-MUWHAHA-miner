# DELTA GOV-005 — Provisional Candidate Improvement Gate

**Status:** MANDATORY / HUMAN-REVISABLE
**Evidence loading:** NOT AUTHORIZED

## Scope first
Before testing, the owner defines the research scope, target area, and which primary metric(s) the candidate is intended to improve.

Primary human metrics:
- winning trade count
- net profit
- gross loss
- maximum drawdown

All four are still reported when supported by the evidence.

## Thresholds
A candidate satisfies the hard numerical gate when at least one owner-targeted primary metric improves by **80% or more versus the R9 REAL baseline**.

**Hard minimum:** 80% improvement.
**Soft preferred target:** 85% improvement.

If the owner declares only one target metric, that metric must reach 80%. If several metrics are targeted, at least one must reach 80% unless the owner explicitly requires multiple simultaneous passes.

## Direction of improvement
- Winning trade count: higher is better.
- Net profit: higher is better. For a nonzero baseline, score improvement as `100 * (candidate - baseline) / abs(baseline)`, so moving a losing baseline toward zero or into profit scores correctly.
- Gross loss: smaller absolute loss magnitude is better. Score as `100 * (abs(baseline) - abs(candidate)) / abs(baseline)`.
- Maximum drawdown: smaller magnitude is better. Score as `100 * (baseline - candidate) / baseline`.

If a baseline denominator is zero, percentage improvement is undefined and the unit must use an owner-approved absolute rule.

## Human review
The 80% rule is the hard numerical gate, but it remains subject to human review. The owner may later change thresholds, require more than one metric to pass, reject a mathematically passing candidate because another metric degraded unacceptably, or redirect the research.

Threshold changes apply prospectively unless the owner explicitly requests retrospective rescoring.

## Activity visibility
Every scorecard must also show total trade count, opportunity count when available, winning and losing trade counts, and trade-count retention. This prevents a favorable headline metric from hiding severe activity collapse.

## Stage-A labels
- 85% or more: `SOFT_PREFERRED_TARGET_MET`
- 80% to below 85%: `HARD_GATE_MET`
- below 80% on every required target metric: `HARD_GATE_NOT_MET`

The first 2.5 weeks of January remain the fast filter/development window. Passing this gate makes a candidate numerically eligible for January-through-July bounded month-by-month research, subject to all other DELTA rules.

This contract defines scoring semantics only and does not authorize loading blocked R9 evidence files.
