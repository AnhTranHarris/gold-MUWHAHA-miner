# XAUUSD HTF Research Guard — Installation and Operating Guide

**Version:** `XAU-HTF-GOV-001/1.0` · **Status:** Governance control, not a trading strategy. The runtime backtest engine is unchanged.

## Read this before working

1. `SOURCE_AUTHORIZATION_SUPERSESSION_v1.0.md`: current approved sources and the specific supersession of the obsolete Dukascopy exclusion.
2. `ANTI_DRIFT_RESEARCH_CHARTER_v1.0.md`: source lock, research objective, investor priorities, bounded R9 research and constructive experiment requirements.
3. `EXPERIMENT_PLAN_EXAMPLE.json`: valid **mock metadata example only**. Edit/copy for a real plan; contains no approved trading results. Existing R9 and model outcomes are not imported into the new experiment.
4. Existing `htf_ticklab/source_registry.py`: the 16 approved monthly broker tick files; source hashes are validated against this registry. The older authorized MT5 reports and tester logs are subject to their separate Drive manifest and specific scope.
5. `RESEARCH_RESULT_TEMPLATE.md`: the reporting contract and supporting-artifact checklist.

## Running the mechanical guard

From `research/htf_dual_ticklab` on this branch:

```bash
python -m htf_ticklab.research_guard check-plan governance/EXPERIMENT_PLAN_EXAMPLE.json
python -m pytest -q
```

Before *any scored experiment*: copy the example to a new immutable `experiment_id` file, replace all demonstration statements, specify the actual source subset and research features/controls/latency schedule, and run `check-plan`. Save the output SHA-256 in the result receipt. Do not edit that plan after seeing results; changing parameters produces a new versioned plan.

After testing, construct a `result.json` with the frozen plan SHA-256, all broker and interval metrics, all positive and negative observations, source/code references, artifact hashes, findings, and the concrete next experiment:

```bash
python -m htf_ticklab.research_guard check-result path/to/plan.json path/to/result.json
```

This metadata gate runs separately from `python -m htf_ticklab.cli` and **cannot prevent** a user from invoking that low-level CLI directly. For science-grade scorecards, the plan gate is a mandatory procedural precondition, and a review must compare its SHA with the backtest report and recompute source hashes. The engine's existing source registry independently rejects unapproved production inputs without a test-only override. Do not label unguarded output investor-grade.

## Required experiment workflow

- Primary source choice: approved Coinexx and Dukascopy Jan–Jul for comparable brokers; Coinexx Aug–Sep exploratory only.
- Single broker exploratory engineering may use one authorized feed, with no cross-broker claims.
- Freeze code commit, clock profile, costs and order latency scenarios; choose chronological train/evaluation windows; all supplied 2026 data is historically exposed and cannot be honestly called untouched holdout.
- Test a new causal mechanism and its ablation and negative control; pursue at least two orthogonal improvements during a bounded cycle (indicators/state filters, execution survivability, regime routing, latency-aware expiry, etc.).
- Run at $100 and $200 if making pre-$5,000 capital-survivability claims; report full-hour/day/week/month distributions and equity intratick drawdown. All investor metrics required; gates not formally approved remain TBD.
- If negative, document root cause + smallest safe remedy + next test. If promising, stress costs, clock alignment, causal cutoffs and weak months. Do not alter or delete failed results.
- Audit R9 only to answer a concrete implementation question; `r9_diagnostic_budget` per plan <=3.
- Save artifacts atomically, upload to approved research Drive, verify hash/readback, and add recovery references. A chat timeout is not automatic proof of lost output.

## Review requirements and limitations

Source/file validation + unit tests + SHA-256 result receipts are necessary but insufficient. Automated code cannot promise valid economics or successful results; human review must confirm no unseen out-of-policy imports and no future-leaking indicator/calibration. This guard does not solve market-alignment ambiguity in unvalidated dates or calibrate real fills. Positive results are *candidates*, not guarantees or deployment authorization.
