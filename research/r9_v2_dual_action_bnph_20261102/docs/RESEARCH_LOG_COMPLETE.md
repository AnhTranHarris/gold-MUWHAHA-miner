# R9 v2 — TRUE DUAL-ACTION BAYES / NEYMAN–PEARSON / HAWKES SOURCE-EXACT RESEARCH LOG

**Scientific state:** NOT APPROVED. No MT5 compile, paper trading, demo, or live activation. All original v2, R9, teacher and failed research sources remain unchanged.

## Scope and preservation

The original source-exact eight full month/broker paired counterfactual archives were read as binary NPZ artifacts, not recreated from remembered summaries. Full original source included inside every paired archive and pinned in recovery ZIP. All eight complete original baseline entry-event universes (2,481,012 events) were loaded, not sampled. Every event has original BUY/SELL paired outcomes including first-passage strict good/incorrect/neutral, exact bid/ask net, original entry side, and the exact 102 dimensional past-only features. Corrected SELL payoff is verified by the original paired source code: `(liquidation_price - entry_price) * side - fee`, with SELL entry at bid and liquidation at ask; original baseline side was reconciled for all 2,481,012 trades by the prior audit. The unrelated erroneous SELL sign in 250ms delay-teacher source must never be substituted.

Training in this new experiment: eight separate source-month 50%/22%/28% chronological fit/calibration/check folds, 60s purge at boundaries. All rows in each fold's eligible calendar segment were used, except terminal-end hypothetical positions with no executable future close; those censored labels remain stored unchanged in source ZIPs and are reported. This first pass does not train cumulatively across earlier months; the attempted cross-month training job did not finish and is not reported as a result. All check data are later than both fit and calibration; the scoring thresholds and payoff buckets use calibration only. Labels from hindsight never enter feature vectors.

## Mechanism: direction is predicted, not nominated

Original specialist score is kept only as a causal context feature, never an entry-side decision. The new canonical action tensor is always `[BUY,SELL]` for the same quote. Both actions are scored with a 3-class conditional model. Separate class outcomes are `[INCORRECT,NEUTRAL,CORRECT]` for each side; neither neutral nor censored is silently treated as success. A researched hierarchical Bayesian side-specific Dirichlet prior is implemented for future calibrated regularization, not retroactively applied to these saved training metrics. Full five-minute and 15m/1h/4h v2 context is preserved through exact source-validated 102-feature as-of extraction; the original FastClock with its multi-timescale Hawkes lives in the online shadow adapter. Extra state-dependent six-channel marked bid/ask/spread Hawkes intensity component implemented with stability test; its values are **not fitted outcome probabilities** and do not receive a speculative positive score boost.

The quote-time online adapter uses the original complete `FastClock`, no lookahead, and reconstructs the 102 original as-of features in a bounded four-hour rolling buffer. A parity test checks original archived Coinexx raw quote history. The online router reevaluates BUY, SELL and WAIT at eligible 250ms quote updates, then invokes the existing tick-exact R9 exit simulator for any accepted research position. No fixed `pending.side`; a genuine opposite-side signal is possible. It fails closed when no approved model exists. Existing trained research models are not approved for live deployment.

## Eight complete held-out direction checks

The direction score below is conditional on a single strict-good side existing under retrospective teacher labels. These are NOT complete on-policy trade outcomes and must not be called win rate. In particular, all policies with strict >=80% correct, >=85% monthly R9 SYNTH trade count, and positive net have failed/are unverified. The single-positive-side reference population is a hindsight-defined evaluation stratum, not a runtime feature.

| Broker | Month | Source events | Old directional match | Dual-action match | Check side AUC BUY/SELL | Model accepted? |
|---|---|---:|---:|---:|---|---|
| coinexx | 2026-01 | 414,938 | 50.52% | 51.61% | 0.5150/0.5102 | NO |
| coinexx | 2026-02 | 477,916 | 51.04% | 51.33% | 0.5105/0.5165 | NO |
| coinexx | 2026-06 | 387,283 | 50.53% | 51.70% | 0.5228/0.5212 | NO |
| coinexx | 2026-07 | 312,856 | 50.79% | 53.53% | 0.5421/0.5355 | NO |
| dukascopy | 2026-01 | 238,644 | 49.34% | 51.78% | 0.5595/0.5450 | NO |
| dukascopy | 2026-02 | 236,293 | 50.01% | 54.04% | 0.5505/0.5531 | NO |
| dukascopy | 2026-06 | 235,139 | 50.35% | 52.55% | 0.5610/0.5610 | NO |
| dukascopy | 2026-07 | 177,943 | 49.96% | 51.57% | 0.5915/0.5851 | NO |

All 8 models selected ZERO entries under strict 80%-correct, side-specific empirical NP cutoff, positive calibration-conditional expected payoff, and minimum BUY-vs-SELL posterior margin. The model is correctly rejected; zero entries fails the 85%-of-SYNTH volume floor. This is NOT evidence that the model meets high frequency targets. Full on-policy replay with a qualified policy is NOT EVALUATED.

## Critical validity limits

1. Original source proposal events are conditional on the OLD single-position lane entering. All-event opportunity expansion when trades are rejected or shortened is absent. Therefore no claim of EA return, full-volume, daily/weekly/monthly acceptance, or true online forecasting is authorized.
2. Trained 3-class LightGBM returns probability-like scores which are NOT yet individually calibrated probability estimates. The side-specific NP quantile is only an empirical threshold on time-dependent calibration labels; not an IID population false-entry guarantee.
3. A direction-ranking score of 51–54% on favorable-exclusive historical events is a weak edge, NOT 80% profitable trading. The rate among all events is lower due to 'neither direction good' events.
4. Explicit bid/ask marked Hawkes extension and hierarchical Dirichlet beliefs are implemented and tested but not fitted jointly into the 103-dimensional LightGBM model. They are not allowed to create fictitious edge or inflate the reported results.
5. 60s teacher and legacy filters are preserved but not used to cheat at the decision timestamp. Full 15s/30s survival and 85% volume require a genuine on-policy re-run after independent calibration.
6. No real broker slippage/margin/stop-level/capacity is reconstructed; the original source payoff uses 0.01 lot, bid/ask and $0.02 fee. More conservative costs are necessary.

## Advanced hypotheses for the next strictly causal falsification cycle

**H1 - Marked cross-quote response:** fit and validate a spread-dependent six-event Hawkes branching matrix by source/session; diagnose bid-leads-ask versus ask-leads-bid and spread toxicity. Stability, log-likelihood, post-fit residuals and out-of-time incremental AUC vs original quote features are required before adopting the intensity as a direction likelihood.

**H2 - Event-sequence teacher distillation:** encode 250ms→3s paths as state transitions using only actually observed revisions; teacher may label later 15s/30s/60s first-passage events offline. At runtime WAIT then recompute both directions from the newly arrived quote, never choose a best future delay.

**H3 - Pairwise action ranking + opportunity classifier:** separate P(any profitable direction) from P(BUY best | exactly one), then jointly calibrate cause-specific path hazards, expected net, and downside tail. Rejection/WAIT must remain economically meaningful and cannot be overridden to fill monthly trade-count quotas.

**H4 - Regime-dependent Bayesian/NP:** model session/volatility/spread-conditioned class priors; only use regime priors from completed prior periods. NP thresholds chosen with chronological out-of-period calibration and block dependence diagnostics; no assumption overlapping 250ms labels are IID.

## Literature / engineering sources actually consulted

- Lee & Seo, “Modeling bid and ask price dynamics with an extended Hawkes process and its empirical applications for high-frequency stock market data” (2022/2023): https://doi.org/10.1093/jjfinec/nbab029
- Lee & Lee, “A Spread-Gated Hawkes-Flocking Model for Best Bid and Ask Dynamics” (2026): https://arxiv.org/abs/2609.36631
- Tong et al., Neyman-Pearson classification algorithms: https://pmc.ncbi.nlm.nih.gov/articles/PMC5804623/
- MQL5 authoritative CopyTicks: https://www.mql5.com/en/docs/series/copyticks
- MQL5 CopyTicksRange: https://www.mql5.com/en/docs/series/copyticksrange
- Time-dependent purging/embargo: https://ppuertos.github.io/financial-ml-core/reference/model_selection/split/

## Complete original sources (not substitutes)

- https://docs.google.com/document/d/1vJPgj_nWadWVALQC0UWB68evqSkKuKwz7KIF_LhXqkA/edit
- https://docs.google.com/document/d/1yurW_yYdCnPQdhxqexL9TgUqyFkj4muMUPuUmUriufw/edit
- https://docs.google.com/document/d/1wHz2c8aLUFqux7J-RTYcgG6hYXKoQaLHQfuSWeIGBgg/edit
- https://docs.google.com/document/d/1HMwR1WvSK887Lk8glrUe6KEUJfGfqmzZ7XZtpOx27Ho/edit
- Original eight complete paired-action recovery ZIPs, exact names and hashes pinned in SOURCE_EXACT_SHA256_MANIFEST.json; original untrained baseline ZIPs, original v2 source and 60s teacher archives are independent immutable artifacts.

**The executable Python source, frozen model weights, calibration payoff buckets, full original source dependencies, SHA-256 checks, and exact input ZIP identities in this recovery package are the source of truth. Never rebuild from this log instead of reading the whole code/data.**
