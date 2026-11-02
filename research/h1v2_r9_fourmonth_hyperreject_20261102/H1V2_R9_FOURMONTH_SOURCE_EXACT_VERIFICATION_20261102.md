# H1V2 R9 — Four-month competing side/neutral/wrong hyper-reject research

Date: 2026-11-02. Status: FAILED H1V2 CORRECTNESS AND VOLUME JOINT TARGET; original MT5 EA/engine untouched.

## Scope, inputs and exact source integrity
- Four Dukascopy full months Jan/Feb/Jun/Jul 2026, **all 15,401,392** eligible first-observed 250ms quote slots scored and independently source-exact ordinal-replayed with original H1V2 30s BUY and SELL outcomes.
- Prior full R9 V2 entry audit read directly. The archived repaired v2 and H1V2 source remain immutable. Do not use old inverted SELL teacher.
- Candidate label ZIPs hash-verified against original `h1v2_dukascopy_{month}_receipt.json`; R7 full 1s/15s/5m/1h nested quote regimes SHA checked per month; R8 full past-only 41-feature `.npy` SHA checked per month. R7 original ordinal IDs checked against original teacher.
- Exact quote-side entry/exit price and first-favorable event labels taken directly from original H1V2 30s R9 teacher, no OHLC, no later quote in same-ms prefix. The source-exact original R9 ActivePath parity check (1,916 entries) was completed before R9 and is a parent dependency, not newly repeated here.
- The sampled learner sees as-of-only 41 R8 causal features plus 12 R7 nested trend regime axes; predictions never receive future quote returns, true BUY/SELL labels, teacher oracle selection, or future entry/exit index. Future only supplies training targets and ex-post audit labels.
- **Deliberate in-sample**: fit uses 85,000 chronologically spread candidate rows PER MONTH PER SIDE, 340,000 training rows for BUY and 340,000 for SELL (the same timestamps with side-specific targets); full 4-month scoring and ordinal replay use every eligible candidate. These are not 15.4 million fitted rows: never misrepresent training coverage.
- Model: separate 3-class LightGBM with labels BAD/NEUTRAL/GOOD; 85 estimators, 55 leaves. Research score penalizes incorrect/neutral posterior mass, takes maximal side and discounts ambiguous BUY/SELL differences. This score is NOT an empirically certified Neyman–Pearson test nor calibrated executable profitability.
- Admission thresholds fixed from a separate uniformly spaced 20,000-row-per-training-month score subsample **before full-month replay**; candidate score fractions tested 0.01%, 0.05%, 0.1%, 0.5%, 1%, 3%, 5%, 10%, 25%. First-pass strict good requires original H1V2 +$0.10 executable move before -$0.10 adverse, and positive R9 style 30s close under $0.02 research fee. NEUTRAL and WRONG admitted signals count against precision and negative economic outcomes remain.

## Every month complete — source-exact one-position nonoverlap
| Month | All 250ms eligible | SYNTH trades | Required 80% count | Best strict precision at any tested cutoff | First volume-met cutoff | Nonoverlap trades | Strict correct | Model net at first volume-met cutoff |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| 01 | 4,025,968 | 27,980 | 22,384 | 24.22% | 0.03 | 47,854 | 20.29% | $-28,920.73 |
| 02 | 3,112,593 | 33,523 | 26,819 | 30.39% | 0.01 | 28,036 | 25.30% | $-17,765.10 |
| 06 | 4,190,620 | 31,801 | 25,441 | 26.00% | 0.01 | 34,211 | 22.41% | $-14,642.59 |
| 07 | 4,072,211 | 24,382 | 19,506 | 22.94% | 0.03 | 34,498 | 16.62% | $-18,965.34 |

**Four-month verdict:** All 15,401,392 candidates scored and replays complete. The joint ≥80% strict correctness AND ≥80% R9 SYNTH trade-count test fails on each month and every tested cutoff. All nine cutoff modeled-net outcomes are negative in every month. No prospective success, live profitability or Coinexx equivalence is established.

## July withheld-month challenge (diagnostic, not true independent historical OOS)
Three-month LOMO07 models fit on Jan/Feb/June only; all July 4,072,211 events scored and exact exit replayed. Note that iterative research has already exposed July to the designer, so this is a **withheld-label model check**, not an untouched blind external validation.
| Metric | July left out of fit | July included in fit |
|---|---:|---:|
| Best strict correctness (any tested cutoff) | 19.69% | 22.94% |
| First ≥80% SYNTH count cutoff | 0.03: 41,201 trades at 14.98% | 0.03: 34,498 trades at 16.62% |
| Net at first volume-met cutoff | $-22,613.67 | $-18,965.34 |

**Important correction:** LOMO July 1% cutoff admitted 19,470 trades, which is 36 BELOW July minimum 19,506, so its 15.82% is NOT a volume-qualified result. The first qualifying LOMO cutoff is 3%, with 41,201 trades at 14.98% correct.

## Forensics: why the apparently sophisticated mechanism failed
- Model gain is overwhelmingly concentrated in `quote_count_60000`, `quote_count_15000`, signed `mid_displacement_300000`, spread, one-hour displacement, and UTC hour. Both independent sides broadly select *activity/structure* rather than the order-sensitive next-30s favorable-before-adverse crossing geometry.
- This is a source-checked feature attribution, not proof that these features causally cause poor outcomes. Feature importance cannot diagnose causal absence by itself.
- The earlier original v2 102-vector information loss counterexample remains relevant: compressed recent histories can hide extremum order and bid→ask leadership. The latest 41+12 as-of representation is not a full multi-thousand-tick path encoder. Numeric multiscale trend alone did not create strong direction asymmetry.
- The posterior scores are uncalibrated model rankings. Penalizing BAD and NEUTRAL after fitting does not manufacture correct direction knowledge; the July negative result falsifies this tested recipe at these settings and volume/cost assumptions.
- Multiple prior R3-R7 grid/marker/six-mark-count/survival experiments were source-checked and were NOT silently repeated; R9 is independent explicit competing-class rejection with exhaustive replay.

## Recovery, reproducibility and continuation
- This recovery ZIP includes sources, tests, model text weights, full-four-month `FULL_REPLAY.json` receipts, frozen thresholds/fit receipts, complete selected ranked score lists needed to reproduce all nine tested cutoffs, model/score hashes and the original audit. It does not duplicate all original Dukascopy ticks or all 15.4m R8 asof rows, which remain reproducible from exact dependency source and Google Drive raw source.
- Every `REPLAY_SELECTED_TOP25.npz` was verified by reconstructing all nine original full-month model admissions and exact tick ordinal replay counts, class distributions and modeled net with zero mismatches. No future good-only teacher selections are used by prediction or filtering.
- Root is configurable with `H1V2_R9_ROOT`, default `/mnt/data`. Restore original H1V2 teacher `results`, R7 full regimes and R8 as-of matrices at documented paths. Reconstruct them with included R7/R8 dependency source and original raw ticks if needed.
- Original complete H1V2 dependency kit (pre-R9): https://drive.google.com/file/d/14Zqs-PyZ70qr0NTvpJRxpT0XcVc8msUu/view; original raw Dukascopy monthly source: https://drive.google.com/drive/folders/1lSCfO_awUKkbR4I6xDTy9orjIl0SrgIV.
- Prior R7 full-population regime archive and R8 feature source references are pinned; do NOT overwrite R7/R8 original dependencies or MT5 EA.
- Unit tests: 5/5 pass. Original R8/R7 source-exact integrity verified. Research status FAIL; no EA deployment, no MQL5 compile, no live authorization.

## Distinct next research hypotheses (NOT yet trained or validated)
1. **Order-sensitive first-passage risk surface:** For every eligible raw quote, estimate competing cause-specific hazards for first favorable and adverse executable barrier in 0–250ms, 250ms–1s, 1–3s, 3–5s, 5–15s, and 15–30s. Include absorbing STOP, NEUTRAL and WAIT. Train with true survival risk sets and censoring, not a single scalar 30s class.
2. **Exact quote-ordinal path grammar:** Encode real bid→ask leads, reversed quote legs, extrema order, signed increments, micro pullbacks, adverse excursion before favorable threshold, quote arrival clustering and signed trend-within-trend segment graph over rolling 30s and 5m. No last-tick-of-250ms future knowledge.
3. **Hierarchical regime specialists with explicit confidence:** Separate trend continuation, exhaustion reversal, sweep/reclaim, velocity burst, spread shock, opening transitions and drift/pullback. Use gating from strictly past-only mixed horizons and compare to R9 ablations, not opaque label memorization.
4. **Calibrated multi-sided rejection:** Fit BUY BAD/GREEN/NEUTRAL and SELL counterparts with neutral/trade cost explicit; formulate Bayesian shrinkage + Neyman–Pearson score with empirical negative distributions and purged day/session blocks, then pre-register strict risk–coverage constraints per month and source.
5. **Real fitted marked excitation:** Fit decay/excitation and 6+ signed quote marks using actual ordinal marked transitions; test whether a fitted Hawkes likelihood adds information beyond past arrivals. Earlier unfitted/counter-only R4–R5 work must not be relabeled as a proven fitted advantage.
6. **Cross-feed execution:** After finding a strong explanatory hindsight motif, require source-exact Coinexx mapping and real MT5 tester execution/latency before any claim. Separately test a new causal foresight student with chronological embargoed freezing; original H1V2 oracle remains offline-only.

## Scientific source on selectivity
Likelihood-ratio-based selective classification is an established reject-option research method (not a shortcut to arbitrarily high accuracy): Heng & Soh, ICLR 2026, https://proceedings.iclr.cc/paper_files/paper/2026/hash/3fe2a777282299ecb4f9e7ebb531f0ab-Abstract-Conference.html ; El-Yaniv & Wiener JMLR 2010 https://jmlr.org/papers/v11/el-yaniv10a.html . R9 uses an NP-inspired rank score ONLY and does not claim the guarantees of these papers.
