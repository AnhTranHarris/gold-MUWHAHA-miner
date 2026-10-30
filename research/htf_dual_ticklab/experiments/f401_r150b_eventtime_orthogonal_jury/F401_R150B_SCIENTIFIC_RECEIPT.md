# F401-R150B — Orthogonal residual + 32-quote event-time class-jury source-exact research receipt

**Date:** 2026-10-30 America/Chicago. **Status:** UNAPPROVED SCIENTIFIC NEGATIVE / MECHANISTIC DISCOVERY. **Current objective:** M-DK-01 OPEN; owner 21/39 historical approvals; G01–G09 OPEN. **Baseline:** F401-R148B frozen active Python decision. **R149:** shadow only. **Predecessor:** F401-R150A design audit, distinct from automated R150 first-passage engine. PRIMARY READ-ONLY; MT5_EXPAND /02 not touched. No live order, MT5 parity or profit claim.

## Source-exact bootstrap, scope and build

R150A forensic findings were used as the hypothesis before experiments. The same eight registered original Coinexx/Dukascopy Jan, Feb, Jun, Jul gzip bid/ask tapes were independently SHA-checked in the existing R149 native reader. No replay engine was recreated or historical event ordinals/labels rewritten. This **scored R150B experiment is only the 21:00–23:59 UTC pocket**, not a full four-month active replacement. The reference dataset still contains 2,574,251 original events. R150B extracted genuine pre-decision quote ordering for 205,572 late-session events; 160,835 have verified first native t0+[15,16) decision quote plus usable existing state. The other 44,737 cannot receive R150B inference, and must remain on the frozen parent.

New 32D source-native bid/ask mark/sequence features were built using only the final 32 genuine quote revisions **strictly earlier than** the first genuine native quote in [t0+15s,t0+16s). Same-millisecond source quotes are all excluded. Explicit bid-only/ask-only/simultaneous quote marks; widening/closing spread hazards; signed revision imbalance; side-mid signed path efficiency; interarrival burstiness; decayed mark excitation; update entropy; event-time lead-lag and depth-2 area proxies; contiguous signed run-length. These are *Hawkes-inspired decayed mark statistics*, NOT a fitted Hawkes likelihood; and *low-order path interactions*, NOT a mathematical signature theorem or a fully implemented BOCPD. No invented Coinexx true traded volume, L2 or executed fill.

The frozen R149 published 159D technical/Bayesian geometry +20D recursive HMM/Kalman state was reused. The complete incremental challenger state is 211D = 179D frozen R149 source-state +32D new event-time state. The pre-existing R148/R120/R147 structural publishers remain available to the parent but are **not directly injected as a 153D vector in this R150B challenger**; this is an acknowledged unresolved part of R150A, not falsely described as completed.

## Three predeclared mechanism comparisons

All learner weights FIT Coinexx/Dukascopy January+February only, per broker; June alone selected any thresholds; July alone was evaluation. The frozen R148B parent, however, had already been fitted on the exposed eight months: thus July is **held from new R150B fitting/calibration only**, NOT full-stack OOS G08.

- **E0_T0:** 179D existing source state only, teacher-free CORRECT rescue / NEUTRAL / OPPOSITE heads.
- **E1_T0:** same class heads with 32 genuine quote-order features, teacher-free training targets (original class only).
- **E1_T1:** same 211D + cross-fitted *privileged-teacher residual prediction* (not actual teacher). A parent-only nuisance predicts teacher logit from frozen parent outputs. Its out-of-month residual is learned from **source-only 211D** state. Training uses out-of-month residual latents; evaluation uses all-Jan/Feb-fitted causal residual model. No teacher target/score or current event truth enters runtime.

The learner uses one LightGBM binary head each for CORRECT rescue on parent vetoes and NEUTRAL/OPPOSITE on released events, regularized with 95 trees/31 leaves/min child65 and deterministic seeds. The jury veto is a parallel OR between high-confidence NEUTRAL and OPPOSITE specialists; high-confidence CORRECT guardian rescues selected parent vetoes. The cut search explicitly permits abstention to R148B (`infinity`) and selects only June-calibrated policies with correct losses no greater than the June R148B baseline. All three configurations failed to earn any nontrivial override. Consequently every July scored mask equals the parent mask exactly.

| JULY 21–23 UTC late-session diagnostic | Opposite veto | Neutral veto | Total bad veto | Correct lost | R150B change vs R148B |
|---|---:|---:|---:|---:|---|
| Coinexx parent and all three R150B policies | 6,736 | 2,388 | **9,124** | **224** | **0 bad / 0 correct** |
| Dukascopy parent and all three R150B policies | 4,416 | 2,832 | **7,248** | **198** | **0 bad / 0 correct** |

**This is NOT a breakthrough and NOT 90% monthly capacity.** Correct-loss budget conservatism prevented unproven veto changes. No hindsight-derived override is activated. The class heads were trained repeatedly across the two brokers and the three mechanism configurations, but not tuned against July.

## Direct source forensics: eligibility changes the R150A treasure-map interpretation

| UTC 21–23 four-month source pocket | Late original events | Causal 32-quote/decision-eligible | Parent veto OPP/NEUTRAL/CORRECT | Teacher residual *all* events | Teacher residual *eligible* events |
|---|---:|---:|---|---|---|
| Coinexx | 108,685 | 94,721 | 28,923/7,704/759 | 17,940 bad / 2 correct | **10,704 bad / 2 correct (59.7% of residual bad)** |
| Dukascopy | 96,887 | 66,114 | 24,191/10,586/873 | 20,092 bad / 5 correct | **3,952 bad / 2 correct (19.7% of residual bad)** |

The teacher residual counts for all late-session events reproduce the R150A audit. But the **available** teacher-residual pocket collapses sharply under exact first-quote t0+15 eligibility, especially Dukascopy. An absent genuine decision quote is **not** a valid filter opportunity and cannot be scored as a veto. Trying a later quote would create a NEW timed intent/outcome and cannot inherit the original t0+30–32 midpoint truth. This is an important physical/action-clock limitation and motivates cooperation with the separate R150 first-passage engine rather than blindly training another classifier.

## July head-rank and teacher-fade evidence

The following July AUC values are conditional on source-eligible late-session events. They measure class ranking and do **not** imply a usable veto at the owner's false-veto budget.

| Broker | Mechanism | CORRECT guardian AUC | NEUTRAL specialist AUC | OPPOSITE specialist AUC |
|---|---|---:|---:|---:|
| Coinexx | E0_T0 | 0.6700 | 0.6808 | 0.7058 |
| Coinexx | E1_T0 | 0.6679 | 0.6814 | 0.7077 |
| Coinexx | E1_T1 | 0.6688 | 0.6809 | 0.7091 |
| Dukascopy | E0_T0 | 0.5788 | 0.6479 | 0.6665 |
| Dukascopy | E1_T0 | 0.5810 | 0.6496 | 0.6731 |
| Dukascopy | E1_T1 | 0.5812 | 0.6579 | 0.6750 |

The incremental quote-order state improves SOME class rankings (not uniformly); the teacher-auxiliary residual changes ordering modestly. Critically the CORRECT guardian is weak in the relevant high-precision tail, preventing safe recycling of R148B false vetoes. This is the mechanistic reason the June NP budget search selected parent-only for all three options.

Parent-only versus parent-plus-source orthogonal historical teacher-score mean absolute error (MAE), held from new R150B fit:

| Broker | June parent MAE → augmented MAE | July parent MAE → augmented MAE |
|---|---|---|
| Coinexx | 0.126171 → 0.126902 | 0.136965 → 0.136117 |
| Dukascopy | 0.116893 → 0.116891 | 0.121525 → 0.119958 |

Thus teacher-residual training has some July score-fidelity signal but fails to establish a robust independent economic/filtering advantage. Because the historical teacher itself is fitted on all these months, none of this is untouched-label proof. In inference the teacher is absent; full teacher independence at TRAINING is achieved only by E1_T0 and it too fails the cutoff test. The user goal of a teacher-retired mechanism remains OPEN.

## QA / realized limitations

- SHA-authenticated exact eight raw tapes and aligned original event ordinals.
- All eight 211D derived caches included in portable archive; source feature file hashes registered in eight receipts. Missing first 15–16 sec quote is handled as INELIGIBLE, never invented.
- Native first quote source timestamp parity checked against existing frozen R149 published decisions for all eight late-session cells.
- **6/6 targeted deterministic tests PASS**: future quote mutation, same-ms exclusion, missing quote handling, no teacher/truth input in runtime, unknown broker fallback, filled t0 immutability. Additional native Coinexx July runtime smoke verifies original-event-ordinal, 32D exact feature parity and parent action immutability.
- A real code defect in signed run-length calculation was identified, corrected to stop on first prior sign mismatch, and **all eight caches and scored models rebuilt**. Old pre-fix experimental outputs are invalidated and excluded from the final package.
- No original event label or teacher prediction enters causal feature publisher, class runtime or parent R148B. The teacher remains an offline auxiliary regression target; its privileged historical masks are for post-hoc audit only.
- No MQL5 compiled parity, true untouched future month, executable fill economics or shared-capital pass. No G01–G09 gate or M-DK-01 objective approval.

## Mechanistic next move under governor fast-fail

**Do not rerun nearby 211D class heads or threshold micro-grids.** The low precision of CORRECT rescue is the blocker; late-session labels and a strong teacher oracle alone do not make a safe change under an almost exhausted false-veto budget. The next materially different mechanism should recover correct events by **predicting physical continuation opportunity** at a newly timed order-intent point (R150 first-passage/VOI branch); calibrate and score new bid/ask executable action-horizon truth rather than reusing original t0 label. At the same time, the next residual specialist should gain full direct R120/R147 state + source-normalized quote-event intensity and richer causal first-passage survival—not simply another parent-score teacher mimic.

Freeze R148B decisions and R149/R150B telemetry. Move only source-exact unapproved experiment receipts to MT5_EXPAND /00 ledger and /01 evidence. NO /02 promotion, PRIMARY write, main merge, self-approval or trading-profit claim.
