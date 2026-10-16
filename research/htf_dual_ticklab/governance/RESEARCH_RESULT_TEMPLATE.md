# Research result / constructive learning receipt template

**No result is certified merely because the JSON schema passes.** Fill in results only after re-running against approved source hashes with an immutable plan.

Record:

- `schema_version` = `XAU-HTF-GOV-001/1.0`
- `experiment_id`, `frozen_plan_sha256`, `classification` = `promising|negative|inconclusive|blocked`, and `decision` = `explore|revise|hold|retire_mechanism`
- `evidence_summary` includes same-period baseline comparison, as-tested costs, slippage, execution delays, code version, clock/UTC, starting balance, *all* reported periods and exact dataset window
- `falsification_summary` describes evidence against the hypothesis, with ablation and negative control, including all underperforming sessions/months
- `broker_metrics` keyed to each planned broker: after-cost `net_profit`, positive `gross_loss` magnitude, `max_equity_drawdown_pct`, `profit_factor` (null when undefined), `completed_trades`, `win_rate`, `win_loss_ratio` (null when undefined), `margin_calls`, `stop_outs`
- `artifacts`: list of name and SHA-256 of actual outputs, retained in Drive plus GitHub code commit references in accompanying receipt
- `includes_all_periods = true` only when no interval selected away; attach actual hour/day/week/month reports outside this short metadata receipt
- `trade_survivability_claim = research_only|not_certified`, `investor_approved = false`
- `limits_and_unknowns` (unverified live fill calibration, imperfect UTC months, selection risk and model uncertainty)
- `next_experiment`: the next **constructive** new-EA test with a falsifiable prediction
- `next_milestone`: how results feed an implementable independent EA, not another endless R9 audit
- On negative tests: `identified_failure_mode`, `safe_remediation`; on retirement: `retirement_evidence`, `alternative_mechanism`

**Experiment outcome rubric:**

| Stage | What to preserve | Response |
|---|---|---|
| Promising | positive and negative periods, source/code/output hashes, sensitivity and control results | Stress on paired broker + latency, no cherry-picking |
| Negative | identifiable bottleneck, rejected invalidity vs causal failure, error category and failed counterfactual | Implement limited viable repair OR choose orthogonal path |
| Inconclusive | data limits, insufficient fills/quote coverage, difference between opportunity and execution | Smaller measurable experiment, no claim of success or impossibility |
| Blocked | missing authorization, bad hashes, ambiguous UTC, run failures | Fix reproducibility first; do not make market inference |
