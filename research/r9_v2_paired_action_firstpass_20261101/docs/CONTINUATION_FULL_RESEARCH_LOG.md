# R9 v2 — Source-exact paired-action foresight training research log
**Research continuation: 2026-11-01**
**No source deletion, no overwrite of prior branches, no MT5 compilation, no trading authorization.**

## Governing primary sources — ORIGINAL FULL DOCUMENTS, NOT SUMMARIES
- baseline: https://docs.google.com/document/d/1YZZ8imbGfYUXdtKICasFFw3QPxpcUB2QLiBQANuR44Q/edit
- original_teacher_training: https://docs.google.com/document/d/10W8PTGCXAi1wRPoIP44_1OwEozH97h0ouL2ejsXxrv8/edit
- ordered_teacher_training: https://docs.google.com/document/d/1moZNDhkf-oBjYBzh6dEHQiGMbq-FAh52jke7TcmJmoM/edit
- architectural_contract: https://docs.google.com/document/d/1vJPgj_nWadWVALQC0UWB68evqSkKuKwz7KIF_LhXqkA/edit
- previous_ordered_recovery: https://drive.google.com/file/d/1Z5_2vHZ2NUMSfLDzNKbJHBbCYuSH7G-i/view
- previous_fast_lane_recovery: https://drive.google.com/file/d/1A7F-l0NhdgtYYlmhLABGP1zt-0pyf-_4/view

## Precise decision to avoid duplicate experiments
The original source-exact eight-source-month run and ordered post-entry quote-event label study had ALREADY completed. Both fitted a veto-only LightGBM student using the baseline fast lane direction. Their native Google Docs above remain intact; their complete Python source and frozen model weights reside on branch `carson/r9-v2-hindsight-teacher-eight-source-training-20261101`, with a separate experimental branch `carson/r9-v2-30s-hindsight-teacher-foresight-student-20261101`. The research logs reject all variants and do not authorize promoting any strategy.

## Distinct additional hypothesis — same-quote opposing executable actions
The old veto study had no reliable answer for whether a losing SELL should have been BUY, or vice versa. Rather than rerun those filters, at each recorded v2 single-position entry time, match the exact original raw quote tick and replay BOTH sides (baseline direction and opposing direction) on the exact later chronological quotes using the identical initial R9 stop, trailing activation/geometry, and first 30s timeout. The original direction must match *both* the recorded exit timestamp and net result byte-exact at the 1e-5 price/fee tolerance.
First favorable: executable liquidation-side net excursion >= +$0.10 (inclusive of a fixed $0.02 fee). First adverse: liquidation-side quote displacement <= -$0.10 from the liquidation-side quote at the same entry tick, excluding spread. Strict positive label requires the earliest favorable event before adverse and a net-positive actual R9-style exit no more than 30,000 elapsed ms after entry. No net-positive but adverse-first or neutral is a successful label. The 0.10 adverse frontier is a forensic diagnostic, not the broker SL value.
Within-source quote order is preserved at identical millisecond timestamps via source tick index. Hindsight labels are derived exclusively from later quotes, never inserted as runtime features. BUY/SELL counterfactuals are mutually exclusive actions at the same quote event. The best-of-two oracle is impossible to trade live and only probes hindsight opportunity supply.

## Full eight source-month paired label reproduction — exact original lifecycle reconciliation
| Broker | Source month | Original complete entries | Exactly reproduced | Either-side strict good | Either-side supply rate | Monthly SYNTH 85% trade floor |
|---|---|---:|---:|---:|---:|---:|
| coinexx | 2026-01 | 414,938 | 414,938 | 223,200 | 53.791% | 23,783 |
| coinexx | 2026-02 | 477,916 | 477,916 | 273,671 | 57.263% | 28,495 |
| coinexx | 2026-06 | 387,283 | 387,283 | 201,750 | 52.094% | 27,031 |
| coinexx | 2026-07 | 312,856 | 312,856 | 155,615 | 49.740% | 20,725 |
| dukascopy | 2026-01 | 238,644 | 238,644 | 66,741 | 27.967% | 23,783 |
| dukascopy | 2026-02 | 236,293 | 236,293 | 67,854 | 28.716% | 28,495 |
| dukascopy | 2026-06 | 235,139 | 235,139 | 69,864 | 29.712% | 27,031 |
| dukascopy | 2026-07 | 177,943 | 177,943 | 41,058 | 23.074% | 20,725 |

## Additional forward model architecture and chronological leakage controls
Exact source code (never reconstituted from prose): src/paired_action_labels.py; src/causal_dual_features.py; src/train_paired_action.py; src/freeze_source_exact.py. These are preserved in all eight checkpoint binaries and in a new descendant GitHub branch. Every checkpoint includes all six complete source-month artifacts: paired labels NPZ, causal as-of feature NPZ, two SHA-256 receipts, fitted LightGBM text weights, and complete forward-check/calibration JSON. The unabridged 102 feature names and source file hashes are in per-source feature receipts.
Runtime as-of features include Bid/Ask and spread revision, source-specific quote impulse, tick event counts, spread compression, realized variance, causal displacement, path efficiency, quote event rate at 250ms, 500ms, 1s, 5s, 15s, 45s, 5m, 15m, 1h and 4h. Include time-of-day/week sinusoidal context, original lane observation, and side-relative signs. No teacher mark, label, or future price is a feature. H1/H4 short history remains tagged as a research limitation.
Two exclusive action views at identical ticks are scored with a binary LightGBM. Historical months before the target month are eligible training; current month uses earliest 50% of active UTC days for training, a disjoint next ~22% for Neyman–Pearson calibration, remaining dates for unchanged evaluation, with 30s purge at training and calibration boundaries. No later month enters an earlier fit. Predeclared NP bad-score rejection quantiles .50, .75, .90, .95, .975, .99 are assessed on calibration only. A model policy is APPROVED for shadow-scoring only if calibration selects both >=80% strict favorable-first and positive net; otherwise a fixed 0.90 NP diagnostic is recorded as failure and never promoted.
The held-out diagnostic uses the frozen baseline decision-event universe; it greedily removes overlapping replayed positions from scored candidates but does not re-admit opportunities created when old positions are skipped. Therefore it is off-policy, and MUST NOT be used as an actual EA equity curve or full-month acceptance. Monthly 85% SYNTH trade floor and daily/weekly/monthly 80% checks require new full chronological stream using the frozen fitted router; absent that, full-system approval is NOT EVALUATED.

## Eight chronological student training results — raw frozen research outputs
| Broker | Month | Held-out selected nonoverlap | Strict successful % | Net idealized | Calibration satisfied? | Days 80% | Weeks 80% |
|---|---|---:|---:|---:|---|---|---|
| coinexx | 2026-01 | 35,768 | 27.740% | $-13,662.75 | NO | 0/8 | 0/2 |
| coinexx | 2026-02 | 10,420 | 31.545% | $-2,007.03 | NO | 0/7 | 0/2 |
| coinexx | 2026-06 | 13,989 | 30.974% | $-2,815.72 | NO | 0/8 | 0/2 |
| coinexx | 2026-07 | 11,522 | 27.860% | $-2,427.08 | NO | 0/8 | 0/2 |
| dukascopy | 2026-01 | 20,335 | 18.407% | $-13,211.96 | NO | 0/8 | 0/2 |
| dukascopy | 2026-02 | 5,119 | 18.539% | $-3,729.40 | NO | 0/7 | 0/2 |
| dukascopy | 2026-06 | 4,971 | 19.272% | $-2,656.67 | NO | 0/8 | 0/2 |
| dukascopy | 2026-07 | 11,228 | 14.802% | $-6,513.83 | NO | 0/8 | 0/2 |

## Complete original source and fixed entry scientific boundaries
* Per-source exact input tick SHA256 is stored inside the paired receipt and feature receipt, not substituted by filename. 8 original full ledger ZIPs remain untouched in Google Drive. No new raw tick files are synthesized.
* Same-millisecond bid/ask source index order retained. R9 stop rounding uses `round(floor(x/.01 + .5)*.01,2)`; using `floor(x*100+.5)/100` caused Dukascopy mismatches and was corrected *before* the final complete rerun.
* Original-side net and exit timestamp match recorded baseline on ALL 2,481,012 trades, 0 discrepancies across all 8 source-months. Six new tests pass, including source-event ordering, fractional stop rounding, causal prefix invariance, future-label exclusion.
* No teacher OR runtime model is approved. A zero-activity or a source-week with no trades never passes 80% survival. Any 80% or 85% claimed from an ex-post quota ranking is invalid.
* Economic model assumes 0.01 lot XAUUSD with $0.02 fee, idealized fill at executable bid/ask, no slippage, broker rejection, margin, capacity, or spread market-impact adjustment. Negative results cannot be called realized account losses.
* Limitations of this next-distinct hypothesis: the source event universe contains only timestamps where the baseline fast lane was already in a flat/eligible position and entered a trade. It omits alternative action/timing at suppressed ticks and cannot certify an online 80%/85% policy. Another mechanism must learn when to WAIT/DELAY and what action to choose at ALL eligible event times before an on-policy replay.

## Next independent architecture experiment, after preserving these failed models
Implement action-timing evaluation on every eligible 250ms quote event while flat, including (BUY NOW, SELL NOW, WAIT 250ms, WAIT 1s, WAIT 3s). Train a first-passage competing-action model on future-path labels in research only. Include source-specific executable spread/cost tails and price delay. Train on chronological dates only, release as a separate additive branch. Compute portfolio-realistic exits and daily/weekly/monthly survival from the selected action stream, never from a fixed baseline ledger. Require >=85% R9 SYNTH trades EACH month, >=80% strict survivors EACH active day/week/month, positive net on EACH broker and no overfit leakage before any promotion.

## This document is a scientific log, not a substitute for the COMPLETE primary datasets and executable code
The eight complete binary checkpoints with their full SHA-256 manifests and raw research weights form the executable source of truth. The original full Google Docs and GitHub artifacts linked above remain unmodified. Resume by verifying all eight checkpoint checksums, then loading the original code and model data; do not use this document as a condensed working substitute for their actual content.
