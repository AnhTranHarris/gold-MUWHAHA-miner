# F401-R118 — sequence-liquidity / regime-state foresight portfolio — PREDECLARED

Date: 2026-10-28. UNAPPROVED RESEARCH. This plan is frozen before R118 model fitting or scoring.

## Objective and predecessor

Continue active M-DK replacement research from F401-R117. Primary objective is absolute original incorrect-signal veto capacity, with correct-signal loss as a strict risk constraint rather than a symmetric penalty. Individual M-DK-01 comparison is against the original Dukascopy January fitted teacher reference: 94,603 incorrect veto / 7 correct lost on 344,037 immutable Jan signals. Portfolio research target is >400,000 incorrect vetoes across the four registered DK months. That target is not an achieved result or an owner approval criterion.

R117 is parked: 8,656 incorrect veto / 726 correct lost; raw lifecycle states covered 578,263 incorrect / 503,852 correct. This establishes scale but insufficient discrimination. R118 changes source information and representation; no R117 cut/leaf sweep.

## Exact source lock

Original R117 event arrays preserve original t, side, truth_class and fitted historical teacher decision. Four registered Dukascopy L1 quote tapes are immutable:
- 2026-01 SHA256 d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5
- 2026-02 SHA256 ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d
- 2026-06 SHA256 34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2
- 2026-07 SHA256 e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7

Source columns include timestamp_ms_utc, ask_raw, bid_raw, ask_volume, bid_volume. `ask_volume`/`bid_volume` are treated only as timestamped L1 quoted size/liquidity. They are NOT executed volume, aggressor trades, queue depth or L2.

## Hindsight map and three materially distinct causal families

A. DENSE QUOTE-PATH + L1 LIQUIDITY STATE. At every original t0, consume only quotes with timestamp strictly < t0. Build multihorizon (0.25/0.5/1/2/3/5/8/10/15/30/60/120/300/900/3600s) price path, spread, quote-arrival, bid/ask-only/joint update, L1 quoted-size imbalance/persistence, path-efficiency, volatility and price/liquidity interaction summaries, plus fixed-quote-count 2/4/8/16/32/64/128 event motifs. This directly exploits a source channel unused by R117.

B. MATURED EVENT / HIDDEN-STATE FORESIGHT. For each event use only earlier original event outcomes whose labels are fully mature before t0 (previous event time + 33.001s <= t0). Build side-specific and all-side 1/2/5/10/30/60 minute wrong/opposite/neutral rates, run lengths, event intensity, time-since-regime-transition and streaming change-state coordinates. No current/future label is available to runtime features.

C. MULTI-TF GEOMETRY / SUPPORT-RESISTANCE / GRID. Publish completed M1/M5/M15/H1/H8 bars only. Derive current completed body/range/location, 3/5/9-bar direction/efficiency/range compression, distance/penetration relative to rolling published extrema, and distance to fixed price grids (0.1/0.25/0.5/1/2/5/10 USD) normalized by current spread and causal recent volatility. These contexts can score every original signal and impose no bar-close-only trade frequency limit.

All three families are joined by original side/session/time context. No absent FILTER05 QUOTE_ORDER column is synthesized. No F400 reconstruction. Healthy tick engine remains untouched.

## Models and targets

Build five high-capacity tree heads from the same causal feature bank:
1. direct incorrect-vs-correct risk;
2. opposite-vs-correct specialist;
3. neutral-vs-correct specialist;
4. historical teacher-selected-wrong phenotype distillation head (teacher decision target allowed only in FIT/diagnostic training; fitted teacher output is never a runtime feature);
5. independent correct-signal guardian.

Also build one session/side/regime mixture using separately fitted direct-risk experts for high-volume context rather than a universal threshold. Model family: deterministic LightGBM, interaction-rich leaves; exact settings persisted. The same feature matrix is used for ablations so improvements cannot come from different event populations.

## Chronology and evaluation

Primary foresight study: Jan chronological FIT 0-60%, CAL 60-80%, VAL 80-100% with >=40s split separation. Freeze router form/cuts on Jan CAL only. Score Feb/Jun/Jul unchanged as historically exposed transfer, not prospective OOS. A second four-month FITTED_DIAGNOSTIC can fit teacher phenotype across all months solely to measure whether the new causal states contain enough information to reconstruct the hindsight teacher's large veto regions; it cannot certify forward edge.

No June/July outcome or teacher mask may alter primary model settings/cuts. Do not call own-month teacher-assisted diagnostics validation.

Predeclared correct-loss frontiers for reporting are 0.10%, 0.25%, 0.50%, 1.0%, 2.0%, 5.0% of correct events, with strict-greater cuts derived on CAL and fixed. Selection objective among predeclared router formulas: maximize CAL incorrect veto at each loss budget. Report every frontier, not only the best-looking point.

## Required outputs

For Jan FIT/CAL/VAL and each full month: original N/correct/opposite/neutral; incorrect veto; correct lost; opposite/neutral veto; wrong:good; teacher-veto overlap; teacher-missed wrong veto; side/session/regime counts. Report total four-month unique incorrect veto. Report raw capacity eligibility separately from protected veto. Add feature-family ablation, permutation/placebo of temporal association on CAL, causal future-mutation unit tests and inference throughput.

## Fast-fail / pivot law

If family A+B+C cannot provide large selective transfer, preserve it once and immediately test an orthogonal successor within R118: (D) error-phenotype routing from high-order teacher leaf/co-occurrence states reconstructed only from available FIT targets and causal sequence features, or (E) causal sequence representation pretraining on dense next-event/multihorizon future-path targets followed by frozen small veto readout. Do not retune nearby thresholds/leaves and call it new science.

No owner checkmark, /02 promotion, G-gate, MQL5/live authorization or complete-EA performance claim is created by R118.
