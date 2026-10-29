# F401-R118I-P1 — Source-native asymmetric original-signal replacement pilot

**2026-10-28 | COMPLETE BOUNDED JANUARY PILOT / NEGATIVE / UNAPPROVED. NOT FOUR-MONTH MODEL ACCEPTANCE.**

## Last checkpoint / original source
Parent: `carson/htf-m-dk01-r118h-source-exact-microprice-20261028`, seven GitHub commits ahead of R117, which remains unchanged. Original frozen engine pin `ca4b58aec597174b6f6d18ab2f36cba6836e4f4c`. Original governance v1.4 and amendments A1/A2/A3, full four-month forensic and 39-objective checklist re-retrieved. As of this research 21/39 historical owner research-only accepted; M-DK-01, S01–S05 and G01–G09 OPEN.

Four authorized raw Dukascopy source tapes downloaded from PRIMARY READ-ONLY and SHA256 checked exactly against original archived F386 source pins: Jan d2ebb9a8..., Feb ed3b3545..., Jun 34686ce5..., Jul e171e8c2... . All four original F395 source-index event populations recovered, unmodified, **total 1,266,934 original events**: {"01": {"n": 344037, "right": 178642, "opposite": 122151, "neutral": 43244}, "02": {"n": 324582, "right": 143923, "opposite": 137216, "neutral": 43443}, "06": {"n": 297035, "right": 132105, "opposite": 129510, "neutral": 35420}, "07": {"n": 301280, "right": 130408, "opposite": 124823, "neutral": 46049}}. No source or engine writes.

## R118I-P1 original experiment actually run
Only January modeled/scored in this pilot (not all four months). Original 344,037 Jan event t0 milliseconds, side, class identity loaded from original F395 parent. January raw L1 BID/ASK and published quote sizes; original side/session plus prior quote mark-history and completed M1/M5/M15/H1/H8 geometry, 335 columns. `searchsorted(t_ticks,t_original,'left')-1` excludes same-millisecond or later ticks. Empty initial history is kept with masked/zero feature and no veto. Current unfinished HTF candle excluded. Future mid-price offsets 2/8/30s constructed from raw source ticks only for FIT auxiliary regression; not input to decision. Training row must have all three forward offsets observed within +1 second, creating an important sample-selection limitation; FIT used **140,653 of 206,422 possible first-60% January event rows**, so this model must not be considered a strong all-regime test.

Model: PyTorch 335→384→192 hidden state with independent classification head 0/1/2 and 2/8/30s future-path regression auxiliary loss, weighted class cross-entropy (1:3:2.2), 3 epochs, seed 118. FIT Jan 0–60%; CAL 60–80%; VAL 80–90%; SHADOW 90–100%, 40s chronological embargo. CAL-only cuts for .5%, 1%, 2% correct-loss ceilings, two predeclared readouts: direct p(opposite)+p(neutral) and future-path-assisted mixture. All periods historically exposed; no independent prospective evaluation.

## Frozen 1% CAL correct-loss operating points (counts on exact original events)

| Readout | Split | Wrong veto | Right lost | Opposite veto | Neutral veto | Bad:right |
|---|---|---:|---:|---:|---:|---:|
| Direct bad | CAL | 336 | 359 | 235 | 101 | 0.936:1 |
| Direct bad | VAL | 186 | 204 | 145 | 41 | 0.912:1 |
| Direct bad | SHADOW | 40 | 46 | 35 | 5 | 0.870:1 |
| Future-path-assist | CAL | 359 | 359 | 272 | 87 | 1.000:1 |
| Future-path-assist | VAL | 220 | 253 | 175 | 45 | 0.870:1 |
| Future-path-assist | SHADOW | 74 | 95 | 66 | 8 | 0.779:1 |

Neither readout shows asymmetrically selective high-capacity veto under a correct-loss cap. No four-month >400k claim. The original Dukascopy January hindsight teacher removed 94,603 incorrect with only 7 correct loss in the same fitted month: model not replicated, nor assumed to be attainable in genuine foresight. Source 30–32s three-way label is not net economic P&L, and no deployment, quotas, MT5, or G gates are claimed.

## Operational interruption / evidence integrity
The initial `np.savez` feature cache job timed out while writing a large 528MB *incomplete ZIP*, before training. The self-contained, fully written NPY X member of shape (344037,335) was recovered byte-exact from that incomplete ZIP local header and validated by NumPy load; future source training happened from this exact X and independently original archived t/side/class. The incomplete ZIP is invalid and is NOT represented as a passing archive or source history. Reproduction source now uses per-array `.npy` atomic writes; all original binary parents untouched. The 4 source-tape hashes, feature/target code and trained model are preserved in local research. No large local research model source cloud upload is claimed. This pilot tests only one trained January model; rest of four-month evaluation not conducted because January CAL/VAL fast-fail criterion failed.

## Proven checks
Four deterministic tests PASS: strict-before-event exclusion, post-t0 future mutation invariance, prior completed bar future-mutation invariance, and independent original label/mask veto recount (both readouts, CAL+VAL+SHADOW). These are bounded tests, not an MT5 compiler result or a full quote-event engine verification.

## Frontier choice
STOP this snapshot multitask variant and do NOT adjust leaves, thresholds or similar models. Distinct NEXT R118J registered: streaming continuous-time marked quote-event likelihood with waiting-time censoring, multiresolution future path latent phase, separate opposite/neutral specialists, genuinely distinct correct guardian, and high-capacity causal arbitration. The point-process and streaming-drift community methods are research inspirations, not imported trade models. Original publisher `QUOTE_ORDER`/accepted F234 composition mask unavailable; marginal accepted-parent filter synergy unverified. No original checklist status mutation. See `NEXT_R118J_PREDECLARED.md`.
