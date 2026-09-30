# BETA064 R1 — Counterfactual-Regret Router & Routing-Uncertainty Preregistration

**Date:** 2026-09-29  
**Branch:** `beta`  
**Status:** PREREGISTERED RESEARCH UNIT — NOT YET AN EMPIRICAL RESULT — NO EA PROMOTION — NO MQL5 AUTHORIZATION — AUGUST SEALED

## Scientific question

Can BETA064 improve robustness by learning **which specialist is locally competent** and when to **WAIT**, without adding new expert families, new exit logic, live model refitting, or another hard confirmation stack?

This unit isolates router quality. The five BETA064 expert definitions remain frozen:

1. TREND_IGNITION_SEQUENCE
2. STRUCTURAL_RETRACE_TREE
3. RANGE_SWEEP_HAZARD
4. V8_M1_AUCTION_FSM
5. INDEPENDENT_TRANSITION_PRECURSOR

E060 remains a feature/benchmark, not the master opportunity clock. BETA039 friction remains an expected-cost state unless physical broker feasibility requires a hard block.

## Why routing is the next robustness bottleneck

BETA063 used semantically different experts but mathematically similar Ridge heads and a fixed global/specialist blend. Its frozen Jan–Jul improvement versus the correct BETA039 P89 incumbent was only 1.755%, with all seven months still negative.

Current research therefore treats three uncertainty channels separately:

- **expert predictive uncertainty** — uncertainty in each specialist's executable value forecast;
- **router uncertainty** — uncertainty about which expert is locally competent;
- **regime/change uncertainty** — uncertainty that the market state itself has shifted.

R1 studies only the first two as they affect expert allocation. BOCPD/HSMM state may enter as causal features, but no trust-reset or live adaptation is enabled yet.

## Research basis

Recent work strengthens the case for this sequencing:

- input-adaptive MoE research in financial forecasting warns that dynamic routing can collapse or become variance-unstable without explicit regularization and stability analysis;
- probabilistic MoE work shows that uncertainty over expert selection can be modeled directly rather than hidden inside a point gate;
- online expert aggregation in finance supports lagged performance-aware mixing under non-stationarity, but that belongs to a later BETA064 layer;
- strongly-adaptive and conditional conformal methods support later calibration under changing distributions, but R1 must first establish a router worth calibrating;
- CPCV / nested validation / selection-bias audits remain required because ordinary random K-fold validation is structurally inappropriate for overlapping financial labels.

Public mechanisms only; no published profitability claim is transferable to XAUUSD.

## Data contract

Initial bounded development window:

- source: original ordered Dukascopy XAUUSD Bid/Ask;
- start: 2026-01-01 00:00 UTC inclusive;
- end: 2026-01-18 12:00 UTC exclusive;
- historical FIT: Jan 1–Jan 9;
- historical CAL: Jan 9–Jan 11;
- historical DIAGNOSTIC: Jan 11–Jan 18 12:00 UTC.

These windows are historically inspected and must never be described as pristine OOS.

All label construction must use original source order including same-millisecond ties. BUY fills Ask, SELL fills Bid, exits use the opposite executable quote. No retroactive fill, future bar, unconfirmed pivot, SYNTH runtime feature, or hindsight path maximum may enter inference.

## Purging / cross-fitting

Expert predictions used to train the router must be **out-of-fold**.

Because entry/continuation labels overlap in time, training folds must use chronological purging and an embargo at least as large as the maximum label/lifecycle horizon used by the frozen expert utility table.

Ordinary random K-fold is prohibited.

Router training rows may include only predictions produced by expert models that did not train on that row's outcome interval.

## Counterfactual executable utility table

For every independent causal opportunity-clock event `t`, evaluate each frozen expert `k` under the same common Entry→Hold lifecycle and executable cost model.

For each expert action:

```
U_k(t) = executable realized utility of expert k's frozen action
BestU(t) = max utility among eligible expert actions and WAIT
Regret_k(t) = BestU(t) - U_k(t)
```

WAIT utility is zero before opportunity-cost conventions.

The counterfactual table is a TRAIN/CAL label object only. It is never a live feature.

## Router target

The router predicts **conditional expected regret**, not a hard regime class.

Initial model class should remain deliberately compact and auditable:

- shallow gradient-boosted trees, or
- monotonic / spline GAM where practical.

Do not begin with a deep router.

For each expert, estimate at minimum:

- predicted mean regret;
- upper-tail regret / uncertainty proxy;
- route competence probability or calibrated ranking score.

The routing loss should penalize economically severe misroutes more heavily than trivial expert differences.

## Soft top-2 allocation

Start with soft top-2 routing rather than winner-take-all:

```
score_k = - predicted_regret_k - lambda_u * uncertainty_k
candidate set = two highest score experts
w_k = softmax(score_k / tau) over candidate set
```

The aggregated action value is built only from those two specialists.

Uniform expert usage is **not** a goal. A narrow expert may be valid if it owns a reproducible state.

## Explicit WAIT

WAIT must be an economic action, not an emergency catch-all.

WAIT can win when:

- all specialist expected executable values are non-positive;
- predicted router regret is high;
- top-two regret margin is too small relative to uncertainty;
- expert disagreement is large and no positive economic margin survives cost.

WAIT thresholds are calibrated only in the historical CAL window.

Coverage deletion is monitored explicitly so the router cannot appear robust merely by refusing most trades.

## Primary router diagnostics

Report:

- realized routed regret;
- oracle-regret gap for research diagnostics only;
- top-1 vs top-2 regret margin;
- route entropy;
- effective number of experts;
- maximum expert route share;
- per-expert activation share by state/session/month;
- expert pairwise residual correlation;
- counterfactual win matrix;
- fraction of routed cases where an alternate expert beats the chosen route by a material executable amount;
- WAIT rate;
- trade and winner retention;
- route/action flip rate under bounded causal perturbations.

## Anti-collapse / specialization tests

Do not enforce equal load balancing.

Instead test for **routing collapse without unique value**:

1. Leave-one-expert-out economic ablation.
2. Expert activation concentration.
3. Expert residual-error correlation.
4. Incremental value on the states the expert uniquely owns.
5. Stability of expert ownership across chronological folds.
6. Performance of each expert on states where it was not selected.

An expert that receives high route weight but adds no unique or synergistic value should be merged or removed later. A rare expert with stable narrow-state value may remain.

## Routing-uncertainty metrics

Track router uncertainty separately from expert uncertainty:

- entropy of routing weights;
- top-two predicted-regret gap;
- calibration of predicted regret vs realized regret;
- route-margin conditional error;
- high-entropy economic expectancy;
- low-margin economic expectancy.

The goal is to learn whether uncertainty predicts **economic routing failure**.

## Perturbation robustness

On the frozen diagnostic window, causally perturb only inputs observable at decision time:

- spread ± one small empirical quantile step;
- short-horizon return / efficiency / volatility within measurement noise;
- one missing 250ms bucket;
- small timestamp jitter that preserves order;
- one delayed higher-timeframe state update;
- small HSMM/BOCPD posterior perturbation.

Measure:

- expert-route flip rate;
- BUY/SELL/WAIT flip rate;
- regret-margin change;
- economic damage from flips.

A router that changes ownership excessively under economically negligible perturbations is not robust even if average backtest P&L improves.

## Execution-cost stress

Every R1 candidate that survives initial diagnostics must be replayed under:

- observed source spread;
- +10% spread inflation;
- +25% spread inflation;
- +50% spread inflation;
- delayed fill to the next observed executable quote;
- bounded latency jitter;
- quote gaps/staleness;
- same-millisecond ordering stress.

Commission/slippage neighborhoods remain provisional until Coinexx native contract calibration is complete.

## Required ablation ladder for R1

A. Correct BETA039 incumbent.  
B. Five frozen heterogeneous BETA064 experts with fixed router.  
C. B + learned counterfactual-regret router.  
D. C + router uncertainty + soft top-2.  
E. D + explicit WAIT.

Stop R1 here.

Do **not** add:

- online trust;
- BOCPD trust reset;
- conformal calibration;
- new hold/exit policy;
- live expert refitting;
- additional specialist families.

Those belong to later robustness units only if R1 shows attributable value.

## Economic scorecard

Every arm must report:

- net;
- gross profit;
- gross loss;
- profit factor;
- max floating drawdown where supported;
- trade count;
- winning closes;
- average executable P/L per trade;
- WAIT rate;
- winner/trade retention vs incumbent;
- realized router regret;
- expert usage and route entropy.

Prediction accuracy alone cannot promote an arm.

## Initial advancement rule

Against the correct BETA039 incumbent on identical chronology:

- >10% guarded whole-system economic improvement may justify internal continuation;
- >20% guarded improvement is the owner-facing breakthrough threshold;
- gross loss and floating DD must not materially worsen;
- improvement cannot be manufactured by deleting most opportunities or winners;
- any calibration/selection parameters freeze before Jan–Jul replay;
- August remains sealed.

If an initial candidate passes, freeze it before Jan–Jul.

If it fails, archive the failure and change the mechanism rather than grid-searching tiny thresholds around the same router.

## Later robustness sequence — not part of R1

Only after routing earns its complexity:

R2. expert redundancy / PID / unique-value audit.  
R3. conditional/conformal distribution-shift calibration.  
R4. strongly-adaptive multi-horizon shadow trust.  
R5. BOCPD/HSMM trust shrink/reset.  
R6. shared multi-age continuation via fitted value vs competing-risks survival.  
R7. full execution-friction surface and native Coinexx parity.  
R8. frozen Jan–Jul replay and selection-bias robustness audit.

## Public source references

- MQL5 HSMM duration-aware regime detection: https://www.mql5.com/en/articles/24460
- MQL5 BOCPD: https://www.mql5.com/en/articles/23482
- MQL5 competing-risks exits: https://www.mql5.com/en/articles/24106
- MQL5 unified validation pipeline: https://www.mql5.com/en/articles/21603
- Expert aggregation for financial forecasting: https://www.sciencedirect.com/science/article/pii/S2405918823000247
- Strongly Adaptive Online Conformal Prediction: https://proceedings.mlr.press/v202/bhatnagar23a.html
- Conditional Quantile Adjusted Conformal Prediction for Time Series: https://proceedings.mlr.press/v306/yu26by.html
- FactorMoE: https://link.springer.com/article/10.1007/s40747-026-02307-2
- FreqMoE: https://proceedings.mlr.press/v258/liu25i.html
- Adaptive heterogeneous financial MoE (2026): https://link.springer.com/article/10.1007/s10791-026-10613-z
- Bayesian input-dependent MoE uncertainty in time-series ensembles (2026): https://proceedings.mlr.press/v341/lukashchuk26a.html

## Next executable unit

`BETA_064_R1_COUNTERFACTUAL_REGRET_ROUTER_AND_UNCERTAINTY_JAN17P5`

This preregistration freezes the question before empirical outcome inspection.
