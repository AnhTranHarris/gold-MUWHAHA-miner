# R9 M60 — Coinexx-only quote-pressure proxy research

**Completed 13 November 2026 — SHADOW RESEARCH, NO PROMOTION.**

## Question

Can Hawkes-style marked quote-event excitation, a latent pressure state filter, and quoted-spread resilience *inferred from Bid/Ask only* increase 5-second first-passage ROC-AUC toward 0.80 while preserving the existing high-frequency R9 opportunity universe?

**Measured answer:** No demonstrated AUC improvement under the present five-fold direct-classifier training design. None of the three proxies improved mean ROC-AUC. All 27 combined proxy features slightly decreased mean pooled AUC and mean original-direction AUC.

## Data provenance and constraints

- Original source: nine archived Coinexx XAUUSD broker quote files Jan–Sep 2026, 72,129,347 actual source rows, source SHA-256 match per month, untouched.
- Original frozen R9 entry decisions: 303,934. Both hypothetical BUY and SELL counterfactuals: 607,868 rows. The 5s target and adaptive barrier definitions are the same as in the preceding 155-feature experiment; no trigger or exit changed.
- `last`, `volume`, `volume_real` are zero in historical broker files; actual traded quantity, aggressor side, L2 book size, market order arrivals, and actual liquidity cannot be recovered.
- Derived dataset is source-ordinal and **as-of**: includes current quote and only earlier events, preserves same-millisecond order, resets calculation after 60 seconds or a >15s quote gap (same segmentation limit as prior CUSUM pilot).
- Original 155-feature baseline includes event-time nested-trend, QRB/QAF, CUSUM, signed-quote-intensity and analytical first-passage features. Each variant appends precisely one new feature family or all three; no older features removed.

## Implemented feature families

**Hawkes-inspired marked quote excitation (12 features):** Time-decayed positive and negative quote-revision marks with 200ms, 1000ms and 5000ms kernels; marks are bounded absolute midpoint moves normalized by lagged spread; signed balance, fast/slow ratio, cross-scale agreement, and recent mark size. **Not a fitted Hawkes point process**: kernel decay constants are frozen heuristics, no conditional likelihood or estimated branching matrix, no reconstructed trade prints.

**Latent directional pressure (7 features):** Causal, two-timescale spread-noise-adaptive scalar Kalman-style filter, including fast pressure, slow pressure, disagreement, innovation, uncertainty, gain and confidence. The hidden state is a *model of quote dynamics*, not identified institutional inventory or actual buy/sell volume.

**Quoted-spread resilience (8 features):** Spread relative to prior exponentially smoothed spread, spread excess, shock age, shock excess, recovery state, decaying shock activity, single-event normalized contraction and smoothed absolute spread revision. This measures only recovery of the quoted spread, not limit order-book replenishment or executable fill liquidity.

## Five chronological, unchanged-target comparisons

Five-second first favorable barrier prediction. Both-side ROC-AUC is on hypothetical BUY/SELL actions at original R9 times; original-direction ROC-AUC is scored on only the R9 side. R9 original-direction is the more meaningful metric for unchanged trading behavior.

| Held-out month | Saved 155 baseline | +Marked excitation | +Latent pressure | +Spread resilience | +All 27 | Baseline R9-side | All-27 R9-side |
|---|---:|---:|---:|---:|---:|---:|---:|
| 05 | 0.71976 | 0.71967 | 0.71958 | 0.71951 | 0.71980 | 0.70508 | 0.70537 |
| 06 | 0.73042 | 0.73045 | 0.73054 | 0.73037 | 0.73007 | 0.71411 | 0.71366 |
| 07 | 0.75606 | 0.75615 | 0.75585 | 0.75613 | 0.75553 | 0.73893 | 0.73866 |
| 08 | 0.75007 | 0.75063 | 0.75016 | 0.75005 | 0.75021 | 0.73453 | 0.73480 |
| 09 | 0.73626 | 0.73559 | 0.73561 | 0.73589 | 0.73598 | 0.72321 | 0.72281 |
| Mean | 0.73851 | 0.73850 | 0.73835 | 0.73839 | 0.73832 | 0.72317 | 0.72306 |

**Five-month delta, all proxies vs saved baseline:** pooled -0.0001958; original-R9 direction -0.0001144. All five model families were fitted using the **identical frozen 95-tree LightGBM hyperparameters**; the baseline scores were replayed from the original saved model files. Full held-out original entry universe retained, without thinning evaluation rows (except unchanged censored-label convention).

**Threshold:** no family reached original-direction AUC 0.75 in any of the five months. Baseline already exceeded pooled AUC 0.75 in July and August; no new family raises the number of passing pooled months. No family demonstrated AUC 0.80.

**Day-block paired resampling of original-direction AUC differences, descriptive only:** marked excitation mean -0.0000645, 95% interval [-0.0004640, +0.0003957]; all 27 mean -0.0001144, interval [-0.0005961, +0.0003589]. Both intervals contain zero and neither proves an improvement. Months previously researched are **not pristine prospective OOS**. Day blocks reduce naive intraday independence claims but do not remove researcher exposure to the test months.

## In-sample final model

All nine months were fitted separately with the 182-feature direct model for offline research. Final receipt: 303,934 original decisions, 607,748 uncensored actions, 182 total features, SHA-256 `c43438977bff8af31e1f8749a6754c63fb8cdef0b32aab86ae6f96f684e433a7`. **NO out-of-sample score exists for this final all-month model.** Do not use it to claim any held-out, demo, or live gain.

## Opportunity frequency and execution

- All 303,934 R9 decision times remain eligible to be *scored* by each model, so this experiment did not discard high-frequency opportunities. This does **not** mean all of them produce trades: the model is deliberately not connected to order routing.
- AUC is not after-cost PnL, win rate, or an execution/backtest pass. Existing friction, slippage, occupancy, rearm, stop/exit timing and actual after-cost account economics were **not** re-simulated here.
- No changes to the R9 EA, its enabled QRB/QAF observation, its entry timestamps, stop geometry, trailing, lot sizes or trade decisions.

## Verification and interpretation

- Eight Python unit tests: no future input influence, identical-millisecond quote order, segment/gap reset, flat prices, spread shock/recovery, finite outputs and invalid ordinals.
- All 9 monthly raw file digests and original entry ordinals were verified before feature extraction.
- All 20 saved chronological proxy models reload at the original SHA and reproduce 80 AUC/average-precision metrics; the all-nine in-sample model hash also matches its receipt.
- Negative result is specific to **fixed-kernel marked excitation, this chosen state-space filter, quoted-spread resilience and the frozen 95-tree classifier**. It is not proof that no possible quote-only model can improve AUC, nor evidence that true liquidity can be inferred from Bid/Ask alone.
- Since training-parameter and label-horizon changes can alter the comparison, none was made in this phase. Do not optimize further against July/August threshold crossings or repeatedly exposed September.

## Preservation and next decision

Keep the feature extractor, derived cache and checkpoints as **non-deployed research assets**, but retain the frozen 155-feature direct classifier as the best matched average-AUC model. Another large price-only proxy sweep is not justified by the measured gain. If R9 entry/exit and stop geometry are investigated next, treat that as a separate predeclared experiment with a complete opportunity-to-trade simulation and genuine later unseen evaluation.

Scientific distinction: Bacry and Muzy (2014), *Hawkes model for price and trades high-frequency dynamics* (https://doi.org/10.1080/14697688.2014.897000) studies market-order and price processes. Our quote-only marked kernel is not their fitted model. Cont, Kukanov and Stoikov (2014), *The Price Impact of Order Book Events* (https://ideas.repec.org/a/oup/jfinec/v12y2013i1p47-88.html) uses genuine LOB events and depths; those inputs are absent from Coinexx archived quotes.

### Reproduction

Research root is pinned to `/mnt/data/r9_m60_proxy_20261113`. Required previous source-derived `full_month_`, `event_` and `priority_` caches are kept as separately referenced upstream frozen archives. `PYTHONPATH=src python src/extract.py --months 01 .. 09`; `python -m unittest discover -s tests -v`; `python src/train_proxy.py --fold 4` through `--fold 8`; `python src/train_proxy.py --summarize`; `python src/train_proxy.py --full` (*in-sample only*); `python src/verify.py`. Pin old baseline artifact `R9_M60_JanSep_FullTraining_155Features_20261113.zip` unchanged.
