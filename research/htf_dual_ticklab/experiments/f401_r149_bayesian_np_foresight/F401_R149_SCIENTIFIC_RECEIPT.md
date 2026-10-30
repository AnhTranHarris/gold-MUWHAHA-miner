# F401-R149 — Bayesian–Neyman–Pearson causal foresight / privileged-student development

**Date:** 2026-10-30 (America/Chicago). **Status:** RESEARCH UNAPPROVED; TELEMETRY-ONLY. **Current checklist M-DK-01 remains OPEN.** No original source, accepted component, `/02`, or main branch was modified. No live order was placed. This is an additive successor to frozen R148B, not a replay-engine rebuild.

## Executive decision
The R149 causal Bayesian/technical array and repeated teacher-student research fit are COMPLETE. Two chronological Jan/Feb-fit → June-calibrated → July-heldout **R149-only** cycles produce small favorable incremental diagnostic results on their own broker. Cross-broker transfer is not sufficiently robust: one direction reduces bad veto capacity, the other violates correct preservation. Therefore R149 overrides are disabled and the previously strongest frozen R148B remains the active Python foresight-shadow decision. R149 models are trained and ready to score as shadow telemetry, not native MT5 or G08 certified.

## Source-exact initialization and causal contract
- Eight original XAUUSD Coinexx/Dukascopy January, February, June, July 2026 registered raw gzip tapes authenticated against immutable SHA-256 pins. Exact R148B original event/time/side/truth and R24/R148 masks reconciled. Total original events: **2,574,251**, native valid R149 decision events: **2,342,805**; remainder **231,446** fall back to the parent.
- No reindexing, relabeling, synthetic quote bars, future +30–32s outcome, teacher mask or teacher score in inference features. Coinexx server time corrected by -120m Jan/Feb, -180m June/July; Dukascopy UTC.
- Decision state is evaluated at first genuine native source quote within [t0+15, t0+16) seconds. The decision quote itself is excluded from all derived candle features; only **completed** real quote-populated candles with end <= decision appear. Missing quote window: parent-only fallback.
- Existing frozen R24/R148 + mandatory R120 six-clock, UTC session and completed M1/M5/M15/H1 state is preserved. R149 adds 10 native completed quote-candle clocks (250ms, 500ms, 1s, 5s, 15s, 30s, 1m, 5m, 15m, 1h).
- New **159D** completed-candle/technical/Bayesian approximate state: completed age, quote counts, true-range ATR proxy (not a Wilder exact ATR), 14-return RSI proxy, Bollinger z/width, variance-normalized trend and curvature, causal swing/Fibonacci basis distance, shrinkage Gaussian direction posterior and stable-vs-shock posterior, multi-clock interactions. No true traded-volume VWAP is asserted.
- Additional **20D genuinely recursive** two-state stable/shock HMM plus scalar Kalman drift, computed solely across earlier published quote-populated bars, with gap reset. These are **not** claimed to be exact full BOCPD run-length inference, nor physical order-book/microstructure volume.
- Learner sees 179D incremental features + 3 frozen R148B causal score fields + side/UTC clock = **185D**. The teacher student produces one causal latent; two independent guardian/hunter heads each see **186D**. Frozen historical FILTER08 own-month score is a **training target only**, never a runtime feature.

## Training and frozen evaluation design
Two LightGBM teacher students per cycle (seeds 14911/14912, 140/180 estimators), 22k teacher-stratified source rows per fitting month. Two correct-rescue and two residual-bad-hunter LightGBM models (seeds 14921/14922, 140/180 estimators), each trained on actual original CORRECT versus OPPOSITE+NEUTRAL as asymmetric heads. Each cycle selects exactly one NP-style rescue/hunter pair on the **designated donor calibration month**, maximizing incremental bad vetoes subject to **no increase in that calibration month’s original-correct losses**. Test labels are used for recount only, after the thresholds are frozen.

| Cycle | R149 train / calibration | Test cell | Parent bad / right | R149 bad / right | Bad delta | Right-loss delta |
|---|---|---|---:|---:|---:|---:|
| C1_CX_JANFEB_TO_JUL | coinexx-01, coinexx-02; cal coinexx-06 | coinexx-07 | 116,814 / 2,724 | 117,456 / 2,653 | +642 | -71 |
| C2_DK_JANFEB_TO_JUL | dukascopy-01, dukascopy-02; cal dukascopy-06 | dukascopy-07 | 127,820 / 2,495 | 128,307 / 2,424 | +487 | -71 |
| C3_CX_DONOR_TO_DK | coinexx-01, coinexx-02, coinexx-06; cal coinexx-07 | dukascopy-07 | 127,820 / 2,495 | 127,729 / 2,468 | -91 | -27 |
| C4_DK_DONOR_TO_CX | dukascopy-01, dukascopy-02, dukascopy-06; cal dukascopy-07 | coinexx-07 | 116,814 / 2,724 | 127,782 / 4,891 | +10,968 | +2,167 |

**Interpretation:** The Jan/Feb→June→July same-broker transfers both improve the R148B point (fewer correct losses and more wrong vetoes), but gains are modest. Coinexx→Dukascopy transfers fewer bad vetoes (not incremental capacity). Dukascopy→Coinexx gains more bad vetoes but sacrifices 2,167 additional correct events in one month and is disallowed by preservation constraints. No universal broker override. The R149 thresholds were never chosen from test-label information.

**Critical exposure caveat:** R148B parent parameters and the original privileged FILTER08 teacher were previously fitted or selected on these exposed eight historical cells. Thus this is **heldout only with respect to new R149 weights/calibration**, not full-stack OOS, untouched-month G08, or certified live foresight. Neither this test nor the target original +30–32s midpoint label proves t0+15 executable economics.

## Teacher learning, separate from live correctness
| Frozen student test | Teacher score MAE (student / constant) | Pearson | Student bad-vs-good AUC | Original same-month teacher AUC |
|---|---:|---:|---:|---:|
| C1_CX_JANFEB_TO_JUL | 0.127 / 0.233 | 0.786 | 0.959 | 0.998 |
| C2_DK_JANFEB_TO_JUL | 0.112 / 0.244 | 0.852 | 0.981 | 0.998 |
| C3_CX_DONOR_TO_DK | 0.118 / 0.244 | 0.842 | 0.977 | 0.998 |
| C4_DK_DONOR_TO_CX | 0.128 / 0.233 | 0.751 | 0.937 | 0.998 |

Teacher distillation does transfer substantial *predictive ordering* to causal inputs, but does not reproduce the nearly oracle-perfect same-month teacher. Gain-importance attribution (not a causal effect measure) places most learned mass on preexisting frozen R148B parent score channels; the 20D recursive feature fraction is small. The experiment does not demonstrate a genuinely new independent market information source.

## Bayesian recursive-family ablation — verdict MIXED
| Source / July test | Full 179D bad / right | 20D HMM/Kalman zeroed bad / right |
|---|---:|---:|
| coinexx | 117,456 / 2,653 | 117,606 / 2,681 |
| dukascopy | 128,307 / 2,424 | 128,249 / 2,395 |

The recursive filter adds some differentiation but is not uniformly beneficial: Coinexx full model protects 28 more correct events at the expense of 150 bad vetoes; Dukascopy full model rejects 58 more bad events at the expense of 29 additional correct losses. No positive universal ablation result is claimed. Short-run calibration and parent exposure prohibit inference of a stable improvement.

## Full four-month broker-native research fit
After frozen comparative experiments, new **all Jan/Feb/Jun/Jul teacher students and class-specific heads** were trained separately for Coinexx and Dukascopy at 88k teacher-student fit rows per broker and multiple seeded estimators. These are **final source-only research fits**, not forward-certified. No thresholds from other fitted model weights are transplanted. Their only authorized runtime role is telemetry, with `r149_override_active=False` hard-coded. The already-filled t0 order and unknown/missing/OOD-source fallback are preserved.

## QA and scope
- **9/9** R149 targeted unit tests pass: future-tick mutation invariance on all 10 clocks, recursive prefix invariance, no fabricated bars, predictor signatures with no truth/teacher/outcome, bounds, parent action immutability, broker fallback, and score missingness. Both broker final-model ensembles loaded and produced finite shadow scores without changing parent action.
- Full eight-cell SHA receipts, event alignment and 4 test-mask counts reverified, 2,574,251 source events in exact original ordinal. Each heldout mask is frozen in evidence.
- Absent from training/inference: market depth/true aggressor flow, actual executed fills, spread/latency from broker execution, true traded-volume VWAP. Fibonacci levels used only as relative geometric basis, not supernatural forecasts.
- Current function **M-DK-01 OPEN**, historical research-stage acceptance **21/39**, **G01–G09 OPEN**. G06 applies to entire cooperative filter per broker-month, not this standalone replacement. No owner self-approval, no /02 promotion or PRIMARY write.
- Native MQL5 compilation/parity G07, a genuinely untouched future broker/month G08, actual fill/cost/shared-capital G09 are not passed. This model is not funded profitability evidence.

## Exact next action
Freeze R148B decision and R149 shadow ensembles. In a genuinely new, chronological, label-blind broker/demo stream, publish a new t0+15 native quote event and both state banks strictly as-of; log R24, R148B and R149 proposed actions without R149 override; mature original truth only afterward. Compare incremental unique bad veto and correct losses by broker/side/session/micro-regime/HTF and 4,178 R9 supply bins. Reject promotion on correct-budget breach, unstable cross-broker tail or no benefit over frozen R148B. Native terminal integration remains a separate gated workstream.

## References (research inspiration, not source inputs)
- Adams & MacKay, 2007, *Bayesian Online Changepoint Detection* (a distinct full run-length algorithm; R149 does not claim to implement it): https://arxiv.org/abs/0710.3742
- Prior MT5_EXPAND `/00`: R148B scientific report https://drive.google.com/file/d/13uWpxbR5hCKuVm4VKpwArUg-vyrL89FV/view
- Prior MT5_EXPAND `/01`: R148B frozen source https://drive.google.com/file/d/1L8vNYAw3AvEaZYLEVR4W3vhrWVio4KLB/view

