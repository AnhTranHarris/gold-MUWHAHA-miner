# BETA064 — Self-adaptive ENTRY+HOLD Mixture-of-Experts with state-conditioned online trust and shared continuation value
**2026-09-29 | DESIGN ONLY, NOT YET BACKTESTED | independent beta | no MQL5 authorization | August SEALED**

## Why BETA063 was insufficient
BETA063 already implemented five soft experts (TREND, SWEEP, COMPRESSION, ROTATION, PREENTRY_LEADUP), 59+/state features, a global+specialist Ridge blend, an observed +5s continuation update, and P89 cost admission. It achieved +14.12% less negative loss on the 17.5-day Jan research window but only +1.755% vs the correct P89 incumbent on frozen Jan–Jul; PF fell .2506 -> .2353, two months regressed, zero profitable months. Therefore do NOT add more hard confirmations or more near-identical specialist families.

Specific structural limitations to replace:
1. Fixed blend `0.60*global + 0.40*soft specialist mixture`; routing is not learned directly from realized economic utility.
2. Specialist models are standardized Ridge regressions; insufficient nonlinear state/expert interaction.
3. Lead-up scheduler is primarily a 350ms spread-narrowing timing rule, not a true pre-entry sequence predictor.
4. Shared continuation gets first state update at +5s and selects discrete 15/30/60/90s horizon; it is not a recurrent optimal-stopping value process.
5. Entry remains anchored to original R9 side with a fixed inversion threshold. R9 should be a prior expert, not direction authority.
6. BETA039 P89 is still a hard admission gate; useful friction state should become a continuous cost term unless broker feasibility itself requires rejection.
7. $2 stop/$2 target remains fixed and obscures whether the continuation model owns the position economically.

## New architecture: one state encoder, five predictive experts, one shared value function

### Causal state encoder
Maintain posterior rather than label-only state:
- HSMM posterior over {TrendUp, TrendDown, Range, HighVolChop} plus expected residual regime duration.
- BOCPD probability of regime break/change and expected run length.
- multi-timeframe H1/M15/M5 efficiency, normalized vol and trend state;
- M1/M5 confirmed pivot/acceptance/sweep/touch age and Gold-Hunter M1-boundary/rearm state;
- 250ms/1s/5s/15s return, acceleration, quote intensity, source-side-signed quote pressure, spread percentile, quote gaps/staleness;
- live position executable PnL, MFE/MAE-so-far, favorable/adverse impulse ages and hold age.
All are as-of current original tick; no future pivot, max/min, SYNTH or OVERFIT runtime feature.

### Five experts (same conceptual families, changed outputs)
Each expert k outputs **continuous distributional economic predictions** for BUY and SELL, never a binary confirmation:
1. TREND_CONTINUATION — multitimeframe directional persistence / accepted-break value.
2. SWEEP_ROTATION — failed-acceptance vs continuation value.
3. COMPRESSION_EXPANSION — latent volatility release direction and persistence.
4. RANGE_BOUNDARY_REARM — Gold-Hunter-derived M1 boundary ownership / range rotation / rearm economics.
5. PREENTRY_SEQUENCE — replace BETA063 liquidity scheduler with a genuine small causal GRU/TCN or deterministic recurrent manifest over 250ms→1s→5s→15s trajectory, structural-distance trajectory, spread trajectory, tick-intensity and state-posterior trajectory. Output Q_BUY/Q_SELL, uncertainty, expected useful horizon and entry-hazard curve.

Initial nonlinear candidates: shallow gradient-boosted trees or piecewise-spline/GAM for four tabular experts; compact state-conditioned GRU for lead-up. All final live inference must export exact tree/coefficients/native recurrence or ONNX and have Python↔MQL5 feature/vector parity.

### Learned state router, plus causal online trust adaptation
For each expert k:
```
gate_logit_k(t) = f_gate(Z_t)_k
offline_weight_k = softmax(gate_logit_k - lambda_unc * uncertainty_k)

shadow_reward_k(t) = causal realized net reward from expert k's virtual decision
                      after that outcome becomes observable
perf_k(state,t) = EWMA or Bayesian-shrunk rolling reward / downside in this state

online_trust_k(t) = exp(eta * clip(perf_k(state,t), -rmax, rmax))
g_k(t) = normalize(offline_weight_k * online_trust_k)
```
Every expert maintains a **shadow/virtual ledger for trust only**; shadow returns are NEVER summed as account PnL. This borrows the adaptive-system idea of multiple virtual strategies while preserving a single real chronological position.

Update trust only after outcomes are observable. Use shrinkage/min-sample floors so a handful of lucky trades cannot dominate. BOCPD high change probability temporarily shrinks rolling performance back toward neutral rather than flipping direction itself. HSMM residual duration changes weights smoothly: continuation expert rises in mature/healthy trend with runway; rotation/rearm rises in range; lead-up rises around new regime formation.

### Entry value, not a confirmation stack
For action a ∈ {BUY, SELL} and horizons h:
```
mu_k(a,h), q10_k(a,h), q50_k(a,h), q90_k(a,h) = expert distribution
Q_side(a,t) =
    SUM_k g_k(t) * SUM_h horizon_weight_h(Z_t) * mu_k(a,h)
    - ExpectedExecutionCost(Z_t,a)
    - lambda_tail * abs(ensemble_q10(a,t))
    - lambda_churn * ExpectedRearmCost(Z_t,a)
```
BETA039 spread percentile becomes `ExpectedExecutionCost` / cost-z input, NOT a binary signal veto, except real broker invalidity/staleness. Original R9 side is an additional PRIOR LOGIT (or baseline feature), not a fixed side that must be inverted by threshold.

Actions are BUY, SELL, WAIT bounded by max latency, and optional FLAT if both sides are economically negative. Coverage deletion is penalized/guardrailed; there is no chain requiring five experts to agree.

## Shared continuation value = fitted optimal stopping
After fill, every position—regardless of originating expert—uses ONE shared value model:
```
ExitValue_t = executable current PnL on opposite quote after known fee
ContinueValue_t = E[optimal future executable position value | Z_t, Position_t]
AdvantageHold_t = ContinueValue_t - ExitValue_t
```
Re-score on every observed 250ms/1s checkpoint (or every tick if computationally safe), not only at +5s. Use hysteresis around zero to stop rapid hold/exit oscillation.

Train continuation with causal cross-fitted fitted-policy iteration, not realized hindsight-max labels:
1. Start with current BETA039/BETA063 lifecycle as behavior policy.
2. Fit side/horizon value distributions using future outcomes in TRAIN labels only.
3. For tick block t→t+Δ build Bellman-style target from executable exit at t+Δ versus **out-of-fold predicted continuation at t+Δ**.
4. Refit shared value model.
5. Recompute expert entry utilities using the fitted continuation policy.
6. Refit router on out-of-fold specialist predictions and realized whole-trade reward.
7. Iterate 2–3 bounded policy-improvement rounds; freeze.
This is model-based fitted policy iteration, not thousand-parameter brute-force.

Safety stop becomes catastrophe/risk floor, not routine profit-harvest owner. Normal exit is the shared continuation comparison; later EXIT-specialist phase can add richer harvest actions.

## Feature synergy and overfit control
Before adding feature interactions, use Partial Information Decomposition / block-permutation or equivalent purged interaction screening to find feature pairs that add synergy beyond individual information. Do NOT keep a feature simply because it is popular. Use source-month/day blocks and out-of-fold expert predictions; router never trains on in-sample expert forecasts. Jan1–Jan9 fit, Jan9–11 gate/calibration, Jan11–18 diagnostic can be reused as historical discovery partitions, never called untouched OOS.

## Community implementation basis, not imported alpha
- MetaQuotes adaptive systems (2010): virtual multiple strategy ledgers and selecting/adapting among strategies. https://www.mql5.com/en/articles/143
- MQL5 Ensemble Intelligence (2025): performance-weighted ensemble/online coefficient adaptation. https://www.mql5.com/en/articles/20238
- HSMM duration-aware XAUUSD state model (2026): explicit regime duration and remaining-time posterior. https://www.mql5.com/en/articles/24460
- BOCPD causal change probability (2026): state break primitive, explicitly not direction signal. https://www.mql5.com/en/articles/23482
- HMM + regime-specific GRU (2026): separation of latent regime and sequence model; BETA064 uses continuous value, not hard veto. https://www.mql5.com/en/articles/24056
- Partial Information Decomposition (2026): interaction/synergy test with block-permutation null; its own gold example does not establish alpha. https://www.mql5.com/en/articles/24382
- Optimal stopping: Dwarakanath et al., arXiv:2209.14738; Dai et al., arXiv:2408.09242. Use mathematical continuation-vs-stop framing, not their instruments/results.

Community material supplies reconstructible architectures only. No community profitability is transferred to XAUUSD or this EA.

## Exact BETA064 research contract
Stage 1 original Jan1–Jan18 12UTC Dukascopy quotes:
- fit/compare four tabular nonlinear experts + genuine pre-entry recurrent sequence expert;
- cross-fitted learned gate;
- state-conditioned causal online shadow trust;
- shared recurrent continuation value;
- P89 friction as continuous cost state;
- same one-position Bid/Ask chronology and source ordinal.
Required ablations:
A incumbent P89 + old L30;
B BETA063 five-Ridge MoE;
C nonlinear experts + fixed gate;
D nonlinear experts + learned offline gate;
E learned gate + online trust;
F shared continuation only on incumbent entry;
G full BETA064 entry+hold.

Only G can be called combined candidate. Strict >10% whole-trade improvement vs BETA039 current incumbent + coverage/safety guard advances frozen Jan–Jul; >20% is breakthrough goal. Must show PF, net, GP/GL, DD, winner/trade retention and monthly sign. No failed-run chat announcement required unless user asks; preserve failures in BETA Research Journal and reproducibility bundle.

**No BETA064 test result exists yet.**
