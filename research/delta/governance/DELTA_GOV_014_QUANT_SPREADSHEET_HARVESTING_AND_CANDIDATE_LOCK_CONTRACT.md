# DELTA GOV-014 — Quant Spreadsheet Harvesting, Speculative Hypothesis Generation, Candidate Lock, and Cleanup Contract

**Effective:** 2026-10-02  
**Branch:** `delta`  
**Status:** MANDATORY / HUMAN-REVISABLE  
**Active phase:** ENTRY + INITIAL-HOLD  
**Active science parent:** `DELTA_004_COINEXX_LIKE_DUKASCOPY_RESEARCH_SURFACE`

## 1. Purpose

DELTA must avoid endless low-leverage micro-testing.

Before expensive tick-level replay, each candidate family is analyzed through a bounded spreadsheet-first quant harvesting cycle that uses the relationship between R9 REAL and R9 SYNTH to identify higher-leverage conditions, interactions, and adjustment packages.

The spreadsheet is an analysis surface. Ordered Dukascopy ticks remain the economic execution authority.

## 2. R9 REAL ↔ R9 SYNTH normalization

For a higher-is-better metric:

`synth_gap_closure_pct = 100 * (candidate - REAL) / (SYNTH - REAL)`

For a lower-is-better metric:

`synth_gap_closure_pct = 100 * (REAL - candidate) / (REAL - SYNTH)`

The primary protected metrics remain:

- winning trade count;
- net profit;
- gross-loss magnitude;
- maximum drawdown.

Total trades, opportunity count, activity retention, and average net/trade remain required companion metrics.

A spreadsheet may calculate a scoped composite SYNTH-gap score across the candidate's declared target metrics, but it may not hide individual primary-metric deterioration.

## 3. Spreadsheet harvesting threshold

The spreadsheet cycle is intended to identify changes with materially higher leverage before expensive replay.

Preferred rule:

- an adjustment package should add at least **+10 percentage points** of scoped SYNTH-gap closure versus its parent before it receives high-priority tick-level testing;
- below +10pp, GOV-007 creative escalation applies unless the spreadsheet exposes a narrow, high-sensitivity region that justifies a targeted test;
- a candidate reaching at least **30% scoped REAL→SYNTH gap closure** is classified `HIGH_VALUE_CANDIDATE_TARGET_MET` for research prioritization.

These are research-selection rules. They do not silently replace or weaken GOV-005 or GOV-006 promotion and lock rules.

## 4. Multi-sheet candidate workbook

Each candidate workbook may use multiple sheets/tabs, including:

1. control / preregistration;
2. R9 REAL and R9 SYNTH baselines;
3. candidate scorecard;
4. bounded event/trade harvest;
5. session/regime/condition slices;
6. two-dimensional interaction matrices;
7. Entry + Initial-Hold timing surface;
8. speculative hypothesis lab;
9. Dukascopy tick-replay queue/results;
10. final variable/logic lock;
11. cleanup manifest.

The workbook may add task-specific tabs when required by the candidate formula.

## 5. Bounded data rule

Raw tick streams must not be dumped into Google Sheets.

Default spreadsheet data is:

- event-level;
- trade-level;
- condition-slice level;
- binned/aggregated interaction level;
- bounded diagnostic samples.

Default resource envelope:

- approximately 10,000–50,000 harvested event/trade rows per analysis batch;
- soft cap of approximately 100,000 event/trade rows in one candidate workbook;
- default 2D interaction grids no larger than about 20×20;
- expand toward about 50×50 only when lower-resolution analysis cannot distinguish the high-leverage region.

If a workbook becomes too large, DELTA shards by candidate condition family, stage, month, or diagnostic purpose rather than creating one monolithic spreadsheet.

Raw Dukascopy ticks remain in the registered Python research environment.

## 6. Controlled speculative / “hallucination-style” hypothesis generation

DELTA may deliberately use speculative AI ideation to expand the hypothesis space.

Permitted tactics include:

- contrastive winner-versus-loser slicing;
- regime inversion;
- symbolic formula/rule mutation;
- counterfactual threshold changes;
- random-subspace feature interactions;
- adversarial parameter jitter;
- failure-cluster mining;
- boundary-condition inversion;
- omitted-variable brainstorming;
- causal-timing challenge tests;
- specialist split/recombination ideas.

Every such proposal is labeled:

`HYPOTHESIS_ONLY`

until it is supported by spreadsheet evidence and then confirmed by causal Dukascopy replay.

Speculation is never reported as observed market fact or performance evidence.

## 7. Spreadsheet → tick replay loop

The default loop is:

`HARVEST -> SLICE -> INTERACTION -> SPECULATE -> RANK -> PREREGISTER -> TICK REPLAY -> WRITE BACK -> REPEAT`

For each cycle:

1. harvest bounded candidate diagnostics;
2. compare candidate behavior to R9 REAL and R9 SYNTH;
3. build condition and 2D interaction surfaces;
4. generate multiple causal, reconstructible adjustment hypotheses;
5. rank packages by expected leverage, activity preservation, compute cost, and collateral-risk exposure;
6. preregister only the highest-value packages;
7. test them in the established Dukascopy tick-level Python cycle;
8. write confirmed results back into the candidate workbook;
9. repeat the spreadsheet cycle as necessary.

The purpose is to use spreadsheet mathematics to improve test selection, not to substitute spreadsheet correlation for causal replay.

## 8. High-probability candidate search

A candidate should not receive endless parameter micro-tuning.

If repeated spreadsheet cycles cannot identify a plausible >=10pp incremental region, the next action should normally be one of:

- STRUCTURAL_CHANGE;
- SPECIALIST_SPLIT;
- NEW_SPECIALIST;
- RECOMBINATION;
- ROUTER_CHANGE.

The preferred research target is a candidate that reaches or exceeds 30% scoped SYNTH-gap closure while preserving activity and avoiding protected-metric hard failures.

## 9. Final lock

Once a candidate is accepted as successful, DELTA freezes:

- candidate ID/version;
- parent;
- exact formulas;
- all variable values;
- timeframe dependencies;
- execution surface;
- state-machine ordering;
- entry logic;
- initial-hold logic;
- session/regime ownership;
- Stage-A result;
- final frozen Jan–Jul replay;
- P50/P90/native sensitivity;
- code commit SHA;
- config/result hashes;
- MT5 reconstruction mapping.

After freeze, later reconstruction must use the locked specification rather than reconstructing from discarded exploratory sheets.

## 10. MT5 reconstruction handoff

A successful candidate's handoff package must contain enough information to reproduce the Python behavior in MQL5 without relying on deleted exploratory artifacts.

At minimum preserve:

- final equations and thresholds;
- exact state order;
- quote-side execution rules;
- timing/bar-visibility rules;
- source commit;
- frozen config;
- final results;
- hashes;
- parity fixture requirements;
- explicit MT5 implementation mapping.

MQL5 coding still requires owner authorization under existing DELTA governance.

## 11. Post-lock cleanup and space preservation

After status reaches:

`FINAL_LOCKED_MT5_HANDOFF_READY`

DELTA performs a cleanup pass.

Delete or retire when no longer required for final reproducibility:

- intermediate candidate Google Sheets;
- scratch CSV exports;
- superseded parameter grids/matrices;
- temporary diagnostic extracts;
- duplicate reports;
- bulky intermediate result blobs;
- obsolete working branches/artifacts where safe.

Preserve:

- canonical R9 REAL/SYNTH references;
- canonical Dukascopy source corpus and manifests;
- final candidate source/config;
- final frozen replay result;
- final compact scorecard / locked-variable record;
- exact hashes;
- final MT5 handoff specification;
- a compact rejected-hypothesis summary sufficient to prevent accidental repetition of known dead ends.

GitHub must not be used as a raw-data warehouse. Large exploratory outputs should be avoided in Git history from the beginning.

Deleting a tracked GitHub file does not necessarily remove its historical storage. DELTA therefore prioritizes **not committing bulky transient artifacts** rather than rewriting repository history.

## 12. Cleanup safety

No artifact may be deleted merely because a candidate looks promising.

Cleanup occurs only after:

1. final candidate lock is complete;
2. final results and hashes are verified;
3. the MT5 reconstruction handoff is self-contained;
4. the cleanup manifest marks the artifact disposable;
5. canonical baselines and source data remain intact.

The goal is aggressive cleanup of disposable research history without destroying the evidence required to reproduce the accepted candidate.

## 13. August

August 2026 remains sealed.

This contract does not authorize August access.
