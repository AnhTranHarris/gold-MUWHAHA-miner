# Gold MUWHAHA Miner — Foresight ↔ Hindsight Two-Way Entry Audit

**Audit date:** 2026-11-01. **Status:** READ-ONLY FORENSIC AUDIT. **No candidate promoted, no MT5 compile, no new trades.**

## Source and scope

The existing R9 HybridGate source is pinned at `8729a6345655a7b4ea31facc81982004ee2b8921`; the current four-month BNP–Hawkes research archive is `R9_BNP_HAWKES_FOUR_MONTH_DEV_20261101.zip` in the main Google Drive Micro_account folder. The exact research program includes `entry_model.py`, `four_month_train.py`, `nonlinear_student.py`, and `nonlinear_student_paired.py`, plus independently labeled Coinexx and Dukascopy real-tick outcomes.

Development months January, February, June, July 2026 were **sampled as four nonadjacent days per month per source**, not full-month training. March, April and May, and August/September, have not been used for this entry policy. Sampled candidate outcomes simulate a fixed 0.01 lot, R9 entry-side stop/activation/trail/30-second timeout, and $0.02 fixed fee. They exclude broker stop-distance, slippage, margin, and partial-fill behavior. They are independent hypothetical entries, **not** a nonoverlapping account equity curve.

## Audit A: Foresight -> hindsight (prospective signal quality)

The live feature vector at quote event t is causal: seven completed bucket clocks (250ms, 500ms, 1s, 5s, 15s, 30s, 45s) plus current quote-event Hawkes state and spread. Its 11 features include scaled impulse, path efficiency, pseudo-Hawkes pressure, ATR ratio, signed RSI proxy, normalized Bollinger dislocation, quote-update-weighted price dislocation, range/Fibonacci-location proxy, cross-clock agreement and spread score. The current candidate side is chosen by combined momentum/Hawkes direction; the paired study also evaluates the opposite side at the same event. Neither future real outcomes nor synthetic teacher flags enter runtime features.

Observed unselected real-tick candidate outcomes:

| Statistic | Coinexx | Dukascopy |
|---|---:|---:|
| Forward-labeled single-direction candidates | 93,042 | 65,944 |
| Net win fraction | 42.68% | 23.63% |
| Training survival-label fraction (net > $0.10) | 28.23% | 15.66% |
| Average candidate net | -$0.21625 | -$0.73111 |
| Average MFE | $0.1662 | $0.0949 |
| Mean absolute MAE | $0.4406 | $1.0080 |
| Stop-exit fraction, incl. trailing stop | 97.25% | 91.71% |
| Median spread at candidate | $0.20 | $0.687 |

Conditional on a profitable result, average gain is about $0.263 (Coinexx) and $0.260 (Dukascopy). Conditional on a nonprofitable result, average loss magnitude is about $0.570 and $1.036 respectively. Given those **unselected** payoff magnitudes, breakeven requires roughly 68.4% Coinexx wins or 79.9% Dukascopy wins. These thresholds change under selective trading, but they explain why merely improving directional hit rate is insufficient.

The three attempted optimizer families—70 binned Bayesian + NP variants, 120 nonlinear survival/payoff variants, and 36 paired-side variants—produced **zero** approved positive-P&L configurations across both brokers. Best paired development-check diagnostic: 1,470 nonoverlapping modeled actions / -$298.40; Coinexx 1,465 / -$295.72, Dukascopy 5 / -$2.68. This was selected among trials on development-check days and is not OOS.

### Causal-input defects and scientific limitations

1. `SCAN_MS=10000` in `four_month_train.py`: features can update in 250ms clocks, but the collector emits potential decisions only once per **10 seconds**; consequently the model is NOT yet a truly subsecond opportunity router. A later design may scan on 250/500ms events while using a causal candidate-trigger/refractory rule to control label overlap.
2. `Hawkes2` uses fixed unestimated baseline, `beta=4`, `alpha_same=0.7`, `alpha_cross=0.2`, and one midpoint move-sign event stream. It is a Hawkes-like engineered feature, not a calibrated event-intensity model for bid/ask revision families.
3. `Clock.summary` uses signed gain-loss ratio labeled RSI (not Wilder RSI), normalized price-to-band location (not Bollinger bandwidth dynamics), and a rolling high-low location proxy labeled Fibonacci (no retracement-event state). QWAP weights *bucket closes by quote counts*, not individual bid/ask updates and certainly not executed trade volume. These are allowed causal proxy features but must not be mistaken for the advanced technical mechanisms suggested by their names.
4. The model does not encode bid-only vs ask-only updates, spread expansion/contraction trajectories, interarrival-time burst asymmetry, or liquidity availability at the executable side. Those omissions are acute for a seconds-scale strategy.
5. The label `net > $0.10` is not the same objective as positive expected net P&L under spread, gap, broker stops and slippage. A classifier can optimize this cutoff while worsening tail loss.
6. The LightGBM ranking score blends dollar net forecasts and class probabilities with an arbitrary `.6/.4` coefficient. It is neither a calibrated posterior probability nor a coherent expected utility quantity.
7. The held-out NP order-statistic threshold is constructed from correlated, overlapping market candidates and is searched across many hyperparameters on development-check days; no unconditional live false-entry guarantee or truly independent selected performance follows from the alpha setting.
8. The global four-month fit and calibration use June/July data when evaluating January/February development days. The **features themselves** remain causal, but this is retrospective holdout evaluation, **not chronological walk-forward** training or validation. A forward time-fold must fit/calibrate only earlier source dates and purge overlapping 30s label intervals before scoring later quotes.

## Audit B: Hindsight -> foresight (inverse reconstruction)

For each identical historical candidate tick, the paired dataset independently walks the subsequent real bid/ask sequence for both BUY and SELL, with the same R9-style exit model. Looking back, a perfect oracle can select the better realized direction at each sampled opportunity. This is deliberately future-privileged and cannot be executed, but it quantifies the ceiling of **direction-only** inference given current event selection.

| Hindsight best-of-two diagnostic | Coinexx | Dukascopy |
|---|---:|---:|
| Completed paired opportunities | 93,040 | 65,939 |
| At least one side later profitable | 86.25% | 47.25% |
| Both sides later unprofitable | 13.75% | 52.75% |
| Best-side oracle mean net if forced to act every candidate | +$0.20429 | -$0.29072 |
| Random-side mean net | -$0.21331 | -$0.73022 |

This is not an optimized nonoverlapping trading backtest. It proves neither a learnable 86.25% forecast rate nor a strategy edge. It does show that Coinexx has ample potentially profitable **direction-conditioned** candidate outcomes, but we have not found features to pick those sides before the move. It also shows that on Dukascopy, **even perfect side selection loses money on average if every generated opportunity must be traded**. Reliable ABSTAIN is therefore a primary modeled action, not an auxiliary spread threshold.

### Teacher inverse audit

The extracted SYNTH R9 teacher stores the outcome of trades under **MT5-generated quote paths** and labels a candidate positive when a profitable synthetic trade occurred in the same Coinexx-server minute and side. The teacher is weak/offline and not a runtime feature, avoiding direct inference leakage. Nevertheless, same-minute/same-side does **not** establish same entry event, fill, spread, exit path or comparable forward opportunity. The teacher label can be timestamp-future relative to a candidate within that minute. It is not a valid tick-exact answer key and must not be treated as one.

For original single-direction candidates, Coinexx teacher marker rates split real survival 35.32% (marked) vs 20.40% (unmarked). Dukascopy splits 21.85% vs 7.26%. Those are correlations on **development data**. Both teacher-marked groups still have **negative average real-tick P&L**: -$0.1402 Coinexx and -$0.6357 Dukascopy. Therefore teacher status alone does not clear economic viability, and a high teacher-alignment rate need not equal foresight skill.

The inverse audit's correct question is not “how do we reconstruct synthetic winning labels?” but “which observable quote-response signatures at t occur *before* a genuinely real-tick favorable-first barrier path, and which are merely hindsight artifacts of the generated path?” Label future path *once* for research, then independently test whether past-only observations can predict its cause-specific outcome.

## Required additional entry mechanisms, in priority order

**M1 — Executable quote-response state (new raw information).** Build multi-stream bid/ask revision events: bid-only up/down, ask-only up/down, simultaneous changes, spread expansion, spread compression, stale-quote and quote-refresh bursts, sign persistence/reversal, failure-to-extend after quote impulse, and consecutive clean midprice advances. Calculate tick-to-tick response and 250/500ms rates; do not invent order-book depth or call quote movement true OFI. Quote-derived signals are proxies and must pass source-specific validation.

**M2 — Competing-risks first-passage model (new target).** At each candidate event record whether the R9-compatible net-profitable frontier or adverse/hard-stop frontier arrives first. Keep discrete elapsed bins 0–250ms, 250–500ms, .5–1s, 1–3s, 3–5s, 5–10s, 10–15s, 15–30s. Model cause-specific hazards of favorable-first, adverse-first, and timeout/no-follow-through. Also model trailing-stop outcome and downside tail. Preserve time-to-first-event and event ordering, not just aggregate MFE/MAE. Forecast **expected executable net and tail loss**, not just P(net > $0.10). R9 exits remain unchanged during entry-only study.

**M3 — Dynamic BUY/SELL/WAIT sequential decision router.** Replace fixed 10-second candidate scanning with event-triggered forecasts evaluated at next 250ms or 500ms observation after a material quote state change. A sequential evidence accumulator requires persistent support from independent quote-response and hazard components before BUY or SELL. WAIT retains optionality; expiry/cooldown prevents reusing an outcome window or flooding with duplicate overlapping labels. Do not convert future peak-to-trough paths to entry features.

**M4 — Broker-conditioned execution viability.** Reconcile expected quote continuation with observed effective spread, additional stop distance, adverse fill/stop slippage and expected liquidation-side exit. Same structural signal may abstain on Dukascopy and trade on Coinexx. Optimize a common causal core but calibrate execution feasibility to each source without merging their ticks or claiming the sources are economically interchangeable.

**M5 — Calibrated Bayesian/Hawkes risk supervisor.** Fit quote-event-type multivariate Hawkes intensities (possibly with regime-conditioned decay), validate residuals, and check stability. Feed *predicted cause-specific hazard and net payoff distribution* into a calibrated posterior/action-value model. Apply Neyman–Pearson or selective-risk constraints as a separate layer, not a replacement for expected P&L. Calibrate with disjoint chronological days and reliability plots/Brier/log-loss.

**M6 — Weak synthetic contrastive teacher, not an oracle.** Use synthetic R9 primarily to study which generated-tick motifs created falsely perfect outcomes and rank hypotheses. Align future-only teacher metadata only in training, avoid assigning whole-minute teacher success as a candidate-level causal truth, cap teacher influence, and let actual Coinexx/Dukascopy bid/ask returns veto synthetic suggestions.

## Minimal next audit-driven experiment (NOT another grid)

1. Preserve prior code/models and their hashes; build no new tick engine and do not compile MT5.
2. Add only one new causal event extractor and one new event-order labeler to the existing two replay environments. Record raw bid/ask revision sequence and exact first passage times. Existing R9 trailing/30s stop is untouched.
3. Re-evaluate the same four research months with historical training **only from earlier chronological dates**, plus purged label overlap and explicit event-generation cooldown; no mixing later fitted parameters into earlier development checks. For retrospective Jan/Feb/Jun/Jul analysis, mark any fits involving later months as retrospective research, not forward OOS.
4. Test ablations: previous BNP–Hawkes features only vs +quote-response vs +first-passage hazard vs +WAIT action. Use the same source ticks and exact execution-cost assumptions in all comparisons.
5. Only score accepted **nonoverlapping** simulated trades with actual bid/ask, spread-cost stress, stop slippage stress, margin constraints for $100/$1,000/$100,000, per-broker trade count and full P&L/tail diagnostics. Demand positive robust expectancy on both sources before considering model promotion.
6. Do not tune March–May/ Aug–Sep in this stage. After freeze, evaluate March–May as untouched historical interpolation and August/September as later Coinexx-only chronological OOS; do not call March–May forward OOS when the model has already learned June/July.

## Scientific boundary and source context

A Hawkes process with price-and-trade event kernels is established in Bacry & Muzy (Quantitative Finance, 2014), but this archive supplies quote events, not their true trade arrival sequence. True order-flow imbalance (Cont, Kukanov & Stoikov, 2014) requires limit-order-book price/size events; our best-bid/ask-only files cannot reconstruct it exactly. Competing-risk cause-specific hazard and cumulative incidence models are established in survival analysis. Chronological purging/embargo and independent probability calibration avoid several known financial-model assessment errors; they do not guarantee profit.

References:
https://www.tandfonline.com/doi/full/10.1080/14697688.2014.897000
https://academic.oup.com/jfec/article-abstract/12/1/47/816163
https://support.sas.com/resources/papers/proceedings12/344-2012.pdf
https://ppuertos.github.io/financial-ml-core/reference/model_selection/split/
https://scikit-learn.org/stable/modules/calibration

**Verdict:** The most valuable new entry mechanisms are (1) quote-response microstructure information, (2) executable first-passage competing hazards, and (3) a true WAIT/ABSTAIN decision that refuses unfavorable economics. More combinations of the existing ATR/RSI/Bollinger/Fibonacci features are not the immediate priority.
