# DELTA GOV-004 — Benchmark Roles and Human Goal Metrics Contract

**Effective:** 2026-10-01  
**Branch:** `delta`  
**Status:** MANDATORY  
**Scope:** DELTA benchmark interpretation, candidate scorecards, January filter goals, January-through-July research, and eventual MT5 comparison.

## 1. Purpose

DELTA uses four distinct evidence roles. They must not be collapsed into one benchmark because each answers a different research question.

This contract defines the roles only. It does **not** authorize loading the underlying R9 files, does not set numeric pass/fail thresholds, and does not change any sealed-data rule.

## 2. R9 REAL — starting point and baseline EA

R9 REAL is the DELTA starting point for improvement work.

Its role is:
- baseline EA behavior;
- baseline REAL ticklog behavior;
- baseline execution/path/lifecycle behavior under Coinexx MT5 real-tick testing;
- denominator/reference for measuring whether a DELTA modification actually improves the starting system.

Every candidate comparison must preserve a direct `candidate versus R9 REAL` view.

DELTA must not call a candidate an improvement merely because it looks good in isolation. It must state what changed relative to the REAL baseline.

## 3. R9 SYNTH — performance-growth reference

R9 SYNTH is the performance reference used to judge how far DELTA has improved beyond R9 REAL.

Its role is:
- aspirational performance yardstick;
- gap-to-target reference;
- benchmark for measuring growth in the human-priority metrics;
- diagnostic reference for understanding what favorable trade behavior looked like in the synthetic environment.

R9 SYNTH is not execution truth and may not become a live feature, future-informed gate, or same-sample selector.

Where mathematically meaningful, DELTA should report both:
- absolute change from R9 REAL; and
- progress/gap closure toward the corresponding R9 SYNTH metric.

No numeric promotion threshold is implied by this contract. The owner will define the required Stage-A goals separately.

## 4. Human-priority metrics

The owner-defined primary human scorecard is:

1. **Winning trade count**
   - Report absolute number of winning trades.
   - Do not substitute win rate for winning-trade count.
   - Also report total trades so activity loss is visible.

2. **Net profit**
   - Higher is favorable, subject to the other metrics and activity requirements.
   - Report the exact accounting basis used by the backtest.

3. **Gross loss**
   - Lower loss burden is favorable.
   - Preserve the source/report sign convention, but also report absolute loss magnitude when needed to avoid ambiguity.

4. **Maximum drawdown**
   - Lower is favorable.
   - Preserve the exact drawdown definition used by the source or simulator.
   - If both balance and equity drawdown are available, keep them separately rather than silently merging them.

These metrics are jointly important. DELTA must not optimize one while hiding severe degradation in another.

## 5. Activity and efficiency companion metrics

Because R9 OVERFIT is used as a trade-capacity reference, DELTA must also retain:
- total trade count;
- opportunity count when available;
- winning-trade count;
- average net profit per trade;
- gross profit per trade when useful;
- gross loss per losing trade when useful.

These are companion metrics. They help explain *how* the primary human metrics were produced.

## 6. R9 OVERFIT — trade-capacity and upper-envelope reference

R9 OVERFIT is the DELTA capacity reference for examining how trades could behave under a maximum-trade-count / high-profit-per-trade idealized surface.

Its role is:
- estimate possible trade-count capacity;
- identify what high-activity favorable trade behavior would look like;
- provide an upper-envelope reference for profit-per-trade and trade participation;
- expose how much trade activity a candidate is leaving unused.

R9 OVERFIT is **not** an execution benchmark, live selector, or permission to use future information.

It is a reference for capacity and idealized behavior only.

## 7. Dukascopy — independent cross-broker blind environment

The ordered Dukascopy tick corpus is the independent market-data environment used to test DELTA logic against the Coinexx MT5 evidence stream.

Its role is:
- rebuild the same DELTA logic from an independent tick source;
- test whether behavior depends excessively on Coinexx-specific tick paths, fills, or report construction;
- compare candidate behavior with the relevant Coinexx MT5 reports;
- reveal cross-environment fragility, robustness, or execution sensitivity.

For DELTA, “blind environment” means the Dukascopy replay is independent of the Coinexx MT5 report/tick generation process and must not import Coinexx future outcomes or synthetic labels into live inference.

This wording does **not** relabel historically inspected January-through-July data as pristine out-of-sample. Existing DELTA data-wall rules remain in force unless the owner explicitly changes them.

## 8. Required comparison surface

Once the underlying evidence is intentionally loaded in a later step, candidate scorecards should contain at minimum:

| Metric | R9 REAL baseline | Candidate | Change vs REAL | R9 SYNTH reference | Progress toward SYNTH | R9 OVERFIT capacity reference | Dukascopy replay |
|---|---:|---:|---:|---:|---:|---:|---:|
| Winning trade count | | | | | | | |
| Total trade count | | | | | | | |
| Net profit | | | | | | | |
| Gross loss | | | | | | | |
| Maximum drawdown | | | | | | | |
| Average net profit/trade | | | | | | | |

Additional metrics may be added, but these rows may not be omitted when the source supports them.

## 9. Improvement logic

DELTA evaluates candidate growth in two directions simultaneously:

`R9 REAL -> Candidate`

and

`Candidate -> R9 SYNTH / R9 OVERFIT reference surfaces`

The first answers: **Did we improve the REAL starting system?**

The second answers: **How much of the desirable performance/capacity gap have we recovered without violating causality or destroying activity?**

Dukascopy then answers: **Does the candidate behavior survive an independent tick environment rather than existing only inside the Coinexx evidence stream?**

## 10. No file-load authorization

This contract records benchmark semantics only.

Creating or reading this contract does not authorize pulling R9 REAL, R9 SYNTH, R9 OVERFIT, Coinexx report, or R9 ticklog files. Those files remain untouched until the owner explicitly authorizes the evidence-loading step.
