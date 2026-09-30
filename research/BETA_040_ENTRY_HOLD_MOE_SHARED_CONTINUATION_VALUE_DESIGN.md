# BETA040 — State-conditioned Entry→Hold Mixture of Experts with Shared Continuation Value

**Date:** 2026-09-29  
**Status:** RESEARCH DESIGN / NOT YET BACKTESTED / NO MQL5 AUTHORIZATION / August SEALED  
**Parent evidence:** BETA031, BETA033, BETA035, BETA039. This document changes how previously weak modules are combined; it does not claim a breakthrough result.

## Problem being solved

Earlier BETA research repeatedly used a valid mechanism as a hard confirmation/veto. That often improved conditional precision or reduced loss exposure while deleting too many original winning opportunities. The owner now wants ENTRY + HOLD treated as a coupled state-dependent problem, not as sequential binary filters. EXIT remains downstream and will consume the same continuation value but is not the primary BETA040 optimization target.

**Core architectural change:** every specialist emits a *continuous economic forecast*, not a YES/NO confirmation. A soft state router weights experts by market/regime/structure context. A shared continuation-value model estimates whether the current position should continue, independent of which expert originated the trade.

## Evidence carried forward, reinterpreted

- **BETA031 duration-aware mixture:** keep the idea that state identity and state age affect expert credibility; discard the hard `DeltaUtility > .20 => flip` as the final decision. HSMM-like residual duration becomes a soft gating feature.
- **BETA039 rolling friction:** corrected signed rolling P89 module is not a signal; convert from a binary veto into expected execution-cost / friction penalty. Its seven-month historical research result reduced modeled losses 11.881% while all months remained negative. It is a cost term, not alpha.
- **BETA033 FAST_ACCEPT / RETRACE_CONTINUE / SWEEP_CONTEXT / REGIME_HARVEST:** stop requiring each pattern to confirm before an entry. Each becomes a specialist producing expected signed value and uncertainty.
- **BETA035 Gold Hunter V8 ancestry:** keep M1 boundary owner, OCO/rearm count, minute age, distance to original opposite boundary and prior same-minute outcome as state variables. Do not assume proprietary hidden V8 indicators.
- Never use R9 SYNTH/OVERFIT future outcomes as runtime features. They remain offline diagnostic teachers only.

## State vector Z_t

Every opportunity and every live position gets an as-of state snapshot with strict source tick ordinal.

**Macro / regime:** H1/M15/M5 direction-efficiency, normalized realized volatility, volatility-of-volatility, range/trend/chop posterior, explicit regime age / expected remaining duration, BOCPD change probability, session and minute age.

**Structure:** causal M1/M5 confirmed pivots, distance/side to nearest live level, acceptance/sweep/reclaim counts, touch age, compression/range width, distance to V8 original same-minute boundaries, rearm number.

**Micro path:** 250ms/1s/5s/15s signed returns, acceleration, path efficiency, signed quote-pressure already relative to proposed side, tick intensity, short realized variance, spread percentile, quote staleness/gaps.

**Position:** entry side, age milliseconds, executable current PnL, MFE/MAE-so-far only, path efficiency since entry, time since last favorable/adverse impulse, current stop distance, structural distance, remaining regime duration.

All multi-timeframe features are either completed bars or explicitly current partial-tick statistics. No future high/low or retrospective swing visibility.

## Five ENTRY→HOLD specialists

1. **Impulse / Fast Continuation Expert** — predicts value of joining clean directional acceleration now. Its natural state is high efficiency, aligned M5/M15 posterior, favorable micro acceleration, enough HSMM residual trend duration and low BOCPD break probability.
2. **Pullback / Reacceleration Expert** — uses prior structural ownership plus current origin/level distance, adverse excursion shape and renewed acceleration. The old RETRACE_CONTINUE is no longer a gate; it outputs expected BUY/SELL value even when the textbook pattern is incomplete.
3. **Sweep / Rotation Expert** — estimates whether penetration/failed acceptance is more likely to rotate than continue. Previous sweep/reclaim state is evidence, not compulsory confirmation.
4. **Range / Boundary-Rearm Expert** — Gold-Hunter-derived minute-boundary ownership expert. Uses minute age, boundary distance, previous same-minute direction/result, range/chop posterior and transition hazard; it predicts continuation vs opposite-boundary rotation without blindly rearming.
5. **Lead-Up Sequence Expert (owner requested family)** — explicitly models what happens *before* the adaptive entry. Use a small causal sequence model (initial candidate: state-conditioned GRU or compact temporal convolution / explicit recurrent manifest) over 250ms→1s→5s→15s path state, regime posterior trajectory, structural-distance trajectory, tick intensity and spread trajectory. Output expected net value BUY and SELL plus uncertainty; do NOT use it as a veto. This is the specialist meant to recognize accumulation / directional build-up before a traditional confirmation occurs.

Specialists may be linear/GBDT/small recurrent models, but every final live artifact must be exportable to deterministic coefficients/tree/ONNX/native recurrence with exact feature order and Python↔MQL5 parity tests.

## Soft state router — no stacked confirmation filters

Let each specialist k output for side a in {BUY, SELL}:
- mu_k(a,t): expected net incremental value if entered now and managed by shared hold model;
- sigma_k(a,t): predictive uncertainty;
- h_k(a,t): expected persistence / useful horizon.

Let state-router logits be r_k(Z_t). Define:
```
g_k(t) = softmax_k( r_k(Z_t) - lambda_unc * sigma_k(t) )
```
The router uses HSMM regime probabilities/residual duration and BOCPD change probability as **continuous inputs**. There is no “H1 says trend AND M5 confirms AND 5s confirms” cancellation chain.

The old BETA039 friction formula becomes:
```
F_t(a) = current_spread + expected_commission + staleness_penalty
         + tail_slippage_proxy(state)
```
rather than a binary admission veto.

Aggregate side value:
```
Q_entry(a,t) =
    sum_k g_k(t) * mu_k(a,t)
    - F_t(a)
    - lambda_tail * downside_quantile(a,t)
    - lambda_churn * expected_rearm_cost(a,t)
```

Direction is `argmax(Q_entry(BUY), Q_entry(SELL))`. A low-value event may DEFER briefly with an explicit maximum decision clock, rather than requiring a fixed list of confirmations. Coverage is an explicit optimization constraint so the model cannot manufacture “accuracy” by deleting most events.

## Shared continuation-value model

Once a position exists, its origin specialist no longer owns the trade. All positions feed ONE shared model:
```
C_hold(t) = E[ future executable value if position remains open | Z_t, Position_t ]
V_exit(t) = executable current PnL after opposite quote and remaining known fees
Delta_hold(t) = C_hold(t) - V_exit(t)
```

The intended research actions are:
- HOLD when Delta_hold is materially positive;
- HARVEST/EXIT when Delta_hold turns negative with hysteresis;
- PROBATION for very young positions where model uncertainty is high but state persistence remains favorable;
- optional REVERSE/REARM evaluation later as a separate value action, not automatic Gold-Hunter ping-pong.

**Do not train a hindsight “best future exit” label and call it causal.** Preferred estimator: cross-fitted dynamic continuation regression / fitted-Q style Bellman targets on actual next observed tick blocks. For a small interval delta:
```
target_t = max( executable_exit_value_at_t+delta,
                discounted_predicted_continuation_at_t+delta )
```
where the continuation estimate used in the target is generated out-of-fold / prior-fold to prevent same-sample target feedback. Alternative first screen: multiple fixed future horizons {2s,5s,10s,20s,30s,45s,60s}, predict each executable net distribution separately, then select the maximum *predicted expected* value live. Never use the realized hindsight maximum as the runtime signal.

The continuation model should predict **distributional** value, not only mean: expected net, probability net>0, adverse 5/10% quantile, expected time-to-value, and expected residual regime duration. HOLD utility can then penalize tail risk without a hard stop filter.

## Training / validation objective

Train specialists to minimize economically weighted regression / distributional loss, not direction accuracy alone. Train router with out-of-fold specialist predictions only. Optimize whole-trade chronology with coverage and downside constraints:
```
Objective = realized_net_after_cost
            - lambda_DD * max_drawdown
            - lambda_GL * gross_loss
            - lambda_tail * CVaR_losses
            - lambda_delete * winner_opportunity_deletion
```
Subject to initial research controls: one 0.01 lot position, exact Ask/Bid, chronology, >=90% incumbent winning opportunities preferred, >=80% trade volume unless a material positive expectancy improvement justifies lower volume, BETA015 guards for any funded-account claim.

Research window stays Jan1 00:00–Jan18 12:00 UTC first. Run 5 expert families independently and the combined MoE in parallel. Only strict >10% guarded whole-system realized improvement advances frozen to Jan–Jul; >20% remains breakthrough target. Do not report failed screens as chat breakthroughs; keep them in durable research logs and use them to drive new source research.

## Community basis and limitations

- MQL5 HSMM duration-aware regime model: https://www.mql5.com/en/articles/24460 — useful for explicit state duration / expected remaining regime time; its published XAUUSD example is not proof of our edge.
- MQL5 BOCPD: https://www.mql5.com/en/articles/23482 — causal change probability, explicitly NOT a direction predictor; use it to change router weights / persistence.
- MQL5 HMM+GRU: https://www.mql5.com/en/articles/24056 — demonstrates separating regime probabilities from a regime-specific recurrent sequence forecaster. BETA040 changes its hard veto pattern into a continuous specialist value score.
- MQL5 Partial Information Decomposition: https://www.mql5.com/en/articles/24382 — use only to identify statistically significant synergistic feature pairs with block-permutation nulls; its own published XAU example did not establish edge.
- Optimal stopping literature: Dwarakanath et al. “Optimal Stopping with Gaussian Processes” (arXiv:2209.14738) and Dai et al. “Learning to Optimally Stop Diffusion Processes, with Financial Applications” (arXiv:2408.09242) motivate comparing continuation value against immediate stopping value, not fixed-horizon label accuracy.
- Meta-labeling literature is cautionary: supervised filters can greatly reduce coverage and label prediction can fail economic return. BETA040 therefore uses continuous router weights / value rather than stacked vetoes.

## Exact next experiment

BETA040-A: build the five expert output matrices on the 17.5-day January original tick window using the existing E060 opportunities **without hard confirmation filters**. Each expert must output BUY/SELL expected net at horizons 2/5/10/20/30/45/60s + uncertainty. Fit state router on cross-fitted predictions. Fit one shared continuation model. Compare:
1) incumbent original entry+L30,
2) each expert + shared continuation,
3) soft MoE entry + fixed incumbent L30,
4) incumbent entry + shared continuation,
5) full MoE entry + shared continuation.

The **full MoE** is the only architecture eligible to be called a BETA040 combined candidate. Any >20% result must still preserve realized opportunity coverage and be reproduced on frozen Jan–Jul before owner review.

**No experiment has yet been executed under this exact BETA040 architecture.**
