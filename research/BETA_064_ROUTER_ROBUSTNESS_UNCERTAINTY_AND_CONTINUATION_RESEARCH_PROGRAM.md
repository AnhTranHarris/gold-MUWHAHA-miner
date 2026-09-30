# BETA064 — Router Robustness, Uncertainty Calibration & Continuation Reliability Research Program

**2026-09-29 | independent beta branch | RESEARCH DESIGN ONLY | no MQL5 authorization | August 2026 SEALED**

## Purpose

BETA063 established the first-generation state-conditioned Entry→Hold MoE, but its seven-month incremental edge over BETA039 was only 1.755% and all seven months remained negative. BETA064 already replaces the fixed Ridge blend with heterogeneous experts, a learned state-conditioned router, an independent event clock, online shadow trust and a multi-age shared continuation-value process.

The next robustness program is therefore not another strategy-family expansion. It is a controlled study of whether BETA064 can reliably determine when an expert is locally competent, when the router is uncertain or misallocating state, when the market distribution has shifted beyond calibration, when continuation value is persistent rather than transient, and whether estimated edge survives executable spread, quote-path and latency stress.

## Fresh Jan–Jul market-state drift audit

A new bounded audit was run directly on the seven original Dukascopy XAUUSD monthly CSV.GZ files. It did not optimize or test a strategy.

| Month | Ticks | Median spread ($/oz) | P90 spread | 1s return std | 1s sign persistence | 1s return ACF(1) |
|---|---:|---:|---:|---:|---:|---:|
| Jan | 9,135,062 | 0.7000 | 1.360 | 0.4263 | 0.4944 | +0.0308 |
| Feb | 7,538,339 | 0.8855 | 1.860 | 0.5339 | 0.4932 | +0.0128 |
| Mar | 9,433,179 | 0.7900 | 1.110 | 0.4604 | 0.4937 | +0.0080 |
| Apr | 7,470,570 | 0.7100 | 0.984 | 0.3057 | 0.4904 | +0.0055 |
| May | 8,333,165 | 0.5800 | 0.770 | 0.2472 | 0.4879 | -0.0163 |
| Jun | 8,201,406 | 0.6300 | 0.770 | 0.2637 | 0.4865 | -0.0014 |
| Jul | 7,415,841 | 0.6700 | 0.810 | 0.2165 | 0.4775 | -0.0072 |

Distribution shift versus January on deterministic samples:

- spread KS statistic: 0.129–0.419 across Feb–Jul;
- spread Wasserstein distance normalized by January IQR: 0.50–1.21;
- absolute 1-second return KS: 0.021–0.111;
- absolute-return normalized Wasserstein: 0.16–0.38.

The most material drift is not merely directional price behavior. Executable friction and short-horizon volatility change substantially across months, while one-second serial persistence weakens and becomes mildly negative later in the sample. A formal distribution-shift and calibration layer is justified.

## Core robustness hypothesis

A robust BETA064 should not ask only “which expert predicts the highest value?” It should ask “which expert has the lowest expected regret in this state, how uncertain is that routing decision, is the current state inside calibrated support, and does remaining continuation value still exceed executable exit value after current friction?”

Keep three uncertainty channels distinct:

1. Expert predictive uncertainty — uncertainty in BUY/SELL/WAIT and continuation value.
2. Router uncertainty — uncertainty about which expert is locally competent, measured by route entropy, top-two regret gap, counterfactual route regret and expert disagreement.
3. Regime/change uncertainty — uncertainty that the market state itself changed, measured by BOCPD change probability/run length and HSMM posterior/residual duration.

Do not collapse these into one confidence score.

## R1 — Counterfactual regret router

Train the router on out-of-fold expert regret and executable counterfactual utility, not merely forecast error.

For candidate state z_t and expert k:

U_k(t) = realized executable utility under the frozen common lifecycle  
BestU(t) = best eligible expert/action utility  
Regret_k(t) = BestU(t) - U_k(t)

Router target: expected conditional regret and uncertainty, not a hard regime label.

Required diagnostics:
- top-1 versus top-2 regret gap;
- route entropy;
- route stability under small state perturbations;
- realized regret by state/month/session;
- expert error correlation and counterfactual win matrix;
- percentage of cases where an equal-compute alternate expert materially beats the routed expert.

Start with soft top-2 routing. Do not impose uniform expert usage; the target is semantic specialization, not artificial load balance.

## R2 — Expert diversity and redundancy audit

Before expanding expert count:
- block-permutation Partial Information Decomposition / synergy screen;
- residual-prediction correlation matrix by month and regime;
- route overlap and expert activation concentration;
- incremental executable value when each expert is removed;
- performance of each expert on states where it was not selected.

Frequently selected experts with no unique or synergistic information should be merged or removed. Rare experts that dominate a narrow stable state may remain.

## R3 — Distribution-shift calibrated uncertainty

Add a calibration layer to expert value distributions and the router:
- cross-fitted value/quantile heads produce q10/q50/q90 executable utility;
- conformal residual calibration conditioned on volatility/spread/regime state;
- online coverage controller checks whether realized utilities remain inside intervals;
- BOCPD change spikes shrink online trust toward neutral and widen uncertainty rather than dictating direction;
- severe calibration failure yields WAIT/FLAT, not forced reversal.

Track coverage, interval width, tail miss rate and economic calibration by month/state.

## R4 — Strongly adaptive expert trust

Replace a single EWMA trust horizon with a multi-timescale online aggregation layer.

Maintain expert shadow rewards only after outcomes are observable. Combine short/medium/long trust horizons using a Bernstein Online Aggregation or strongly-adaptive-regret style meta-layer.

Rules:
- trust affects routing weight only; shadow ledgers never become account P&L;
- minimum effective sample size and shrinkage toward neutral;
- cap single-update influence;
- reset/shrink on high BOCPD probability;
- no live parameter refitting of expert models in this phase.

## R5 — Shared continuation as conditional survival/value

Test shared continuation as a conditional survival/value process rather than a later horizon classifier.

At approximately 250ms / 1s / 3s / 5s / 10s and material state changes estimate:
- probability of favorable harvest before catastrophic failure;
- probability of catastrophic failure before harvest;
- expected remaining executable value conditional on survival;
- EXIT NOW versus CONTINUE expected value.

Compare cross-fitted fitted-policy iteration against a discrete-time competing-risks hazard model on the same incumbent entries.

## R6 — Execution-cost robustness

Because spread is one of the largest measured distribution shifts, BETA039 friction should be modeled as a stochastic state/cost estimate.

Stress every candidate with:
- observed source spread;
- +10/+25/+50% spread inflation;
- latency jitter buckets;
- quote gaps/staleness;
- same-millisecond ordering;
- delayed fill to next observed executable quote;
- commission/slippage neighborhood after Coinexx contract verification.

Promotion must survive a friction surface, not one cost point.

## R7 — State perturbation and route-stability tests

Perturb only causally available inputs:
- spread plus/minus a small quantile step;
- return/efficiency/volatility within measurement noise;
- one missing 250ms bucket;
- small quote-time jitter;
- one delayed higher-timeframe update;
- small posterior-probability perturbation.

Measure action flip rate, expert flip rate, route entropy, value-margin change and economic damage.

## R8 — Chronological robustness protocol

Initial development remains Jan 1–Jan 18 12UTC with the established historical fit/cal/diagnostic partitions.

If a candidate clears the initial gate:
1. freeze all parameters;
2. replay Jan–Jul without retuning;
3. report monthly net, GP, GL, PF, DD, winners, trade retention, router regret, uncertainty calibration and expert usage;
4. use month-drop/rolling-origin analysis only as robustness diagnostics, not pristine OOS claims;
5. keep August SEALED.

Use purged/embargoed folds inside training where labels overlap. Do not use ordinary random k-fold validation.

## Required ablation ladder

A — BETA039 incumbent.  
B — BETA064 heterogeneous experts + fixed router.  
C — B + counterfactual-regret learned router.  
D — C + router uncertainty / top-2 soft routing / WAIT.  
E — D + strongly-adaptive shadow trust.  
F — E + regime/change uncertainty shrink/reset.  
G — F + distribution-shift conformal calibration.  
H — shared continuation only on the best entry arm.  
I — full robust BETA064 Entry→Hold.

Do not skip directly from A to I. Any gain must be attributable to a specific robustness layer.

## Promotion gate

The owner-facing threshold remains:
- >20% guarded whole-system improvement versus the correct BETA039 incumbent for a chat-worthy breakthrough;
- economic quality, not only prediction metrics;
- explicit seven-month reporting;
- gross loss and floating DD cannot materially worsen;
- winner/opportunity retention required;
- improvement cannot come from deleting most trades;
- August SEALED;
- no MQL5 implementation without explicit owner approval.

## Public reconstructible research basis

- MetaQuotes — Hidden Semi-Markov Models for Duration-Aware Regime Detection in MQL5 (2026): https://www.mql5.com/en/articles/24460
- MetaQuotes — Bayesian Online Change-Point Detection in MQL5 (2026): https://www.mql5.com/en/articles/23482
- MetaQuotes — Survival Analysis for Trade Exits: A Discrete-Time Competing-Risks Model in MQL5 (2026): https://www.mql5.com/en/articles/24106
- MetaQuotes — Partial Information Decomposition (2026): https://www.mql5.com/en/articles/24382
- MetaQuotes — Rough Volatility (2026): https://www.mql5.com/en/articles/24480
- MetaQuotes — Unified Validation Pipeline Against Backtest Overfitting (2026): https://www.mql5.com/en/articles/21603
- Zheng et al. — FactorMoE (2026): https://link.springer.com/article/10.1007/s40747-026-02307-2
- Ciliberti et al. — Expert aggregation for financial forecasting (2023/2024): https://www.sciencedirect.com/science/article/pii/S2405918823000247
- Bhatnagar et al. — Strongly Adaptive Online Conformal Prediction (ICML 2023): https://proceedings.mlr.press/v202/bhatnagar23a.html
- Oancea — Dynamic Regime-Aware Conformal Calibration (2026 preprint): https://arxiv.org/abs/2608.17079
- Liu — FreqMoE (AISTATS 2025): https://proceedings.mlr.press/v258/liu25i.html

Community/academic sources provide reconstructible architecture and diagnostics only; none transfers profitability to XAUUSD.

## Next bounded scientific unit

**BETA_064_R1_COUNTERFACTUAL_REGRET_ROUTER_AND_UNCERTAINTY_JAN17P5**

Scope:
1. preserve five heterogeneous expert definitions;
2. construct out-of-fold expert counterfactual utility/regret labels;
3. train learned regret router;
4. add route entropy/top-two regret gap and explicit WAIT;
5. no online trust yet;
6. no new exit model yet;
7. compare BETA039 and fixed-router BETA064 on identical chronology;
8. archive failures and surface only a >20% guarded breakthrough in chat.

This isolates the highest-leverage robustness question first: can the model route specialists reliably before adding adaptation and survival complexity?
