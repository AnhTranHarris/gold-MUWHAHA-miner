# BETA064-R1 — Entry→Hold Ceiling, Counterfactual-Regret Router & Uncertainty Specification
**2026-09-29 | independent beta branch | RESEARCH ONLY | no MQL5 authorization | August 2026 SEALED**

## Purpose
BETA063 proved that a five-specialist Entry→Hold MoE can reduce short-window loss, but the frozen Jan–Jul improvement versus the correct BETA039 incumbent was only 1.755%, all seven months remained negative, and most apparent gain still came from inherited friction avoidance.

BETA064 changes the architecture to an independent causal event clock, five genuinely heterogeneous experts, learned state-conditioned routing, explicit WAIT, and multi-age shared continuation value.

This R1 unit must determine **where the remaining loss actually lives before adding more complexity**:
1. expert pool lacks executable alpha;
2. event clock is late/wrong;
3. experts are complementary but router allocates them badly;
4. uncertainty is miscalibrated so the system commits when it should WAIT;
5. entry looks good but continuation value decays immediately after fill;
6. execution friction erases otherwise valid edge.

No new EXIT-specialist logic is authorized in this phase.

## Research principle: ceiling before router
Before fitting a learned router, calculate a non-deployable diagnostic ceiling from the five frozen heterogeneous experts on the same causal candidate events and fixed common lifecycle.

For event/state t and expert k:
- U_k(t) = realized executable utility of expert k's frozen action under the identical lifecycle, observed Bid/Ask chronology, fees and source ordinal.
- U_WAIT(t) = 0.
- U_ORACLE(t) = max(U_WAIT(t), U_1(t),...,U_5(t)).
- Regret_k(t) = U_ORACLE(t) - U_k(t).

The oracle is **diagnostic only** and may never become an inference rule.

Decision logic:
- if the expert-pool oracle is weak/negative after costs, do **not** spend the next unit optimizing the router; repair expert/event-clock coverage;
- if oracle value is strong but routed value is weak, routing is the bottleneck;
- if oracle value is strong but concentrated in one expert, the MoE may be unnecessary or redundant;
- if oracle value is strong and distributed across specialists, proceed to learned regret routing.

This ceiling test prevents a sophisticated router from being blamed for an expert set that contains no sufficient conditional edge.

## R1.0 — Independent event-clock and expert-pool ceiling audit
Use the BETA064 causal event clock:
- completed 250ms buckets;
- material BOCPD state-change updates;
- confirmed structural-level interactions;
- V8 original-minute boundary interactions;
- deterministic event/state deduplication.

E060 is recorded as a feature/benchmark only.

For each candidate event record:
- event family and source ordinal;
- E060 lead/lag relationship when applicable;
- current executable Bid/Ask and BETA039 friction state;
- five expert state inputs and outputs;
- each expert's BUY/SELL/WAIT action;
- realized executable counterfactual utility under one common fixed lifecycle;
- multi-age markouts/continuation labels at causal ages 250ms, 1s, 3s, 5s and 10s where alive.

Required diagnostics:
- event density and duplicate suppression;
- positive post-cost opportunity rate by event family;
- event-family overlap;
- expert oracle net / GP / GL / PF;
- oracle value captured by each single expert;
- unique-winning-event share by expert;
- expert residual and utility correlation;
- best-expert confusion/win matrix by state, session and month;
- realized value lead/lag versus E060.

## R1.1 — Five heterogeneous expert integrity test
Freeze five distinct inductive biases before router training:

1. TREND_IGNITION_SEQUENCE
   - compact causal TCN/GRU;
   - micro sequence + M1/M5 trend + HSMM residual duration + BOCPD + rough-vol/cost state;
   - no completed BOS requirement.

2. STRUCTURAL_RETRACE_TREE
   - shallow gradient-boosted tree / exported tree ensemble;
   - confirmed M1/M5 structure, retrace depth, acceptance vs wick sweep, volatility-normalized level distance, compression/expansion.

3. RANGE_SWEEP_HAZARD
   - discrete-time hazard / interpretable nonlinear hazard model;
   - sweep→reclaim, failed acceptance, rotation and transition risk;
   - outputs state-conditioned action value and useful-horizon hazard.

4. V8_M1_AUCTION_FSM
   - deterministic finite-state auction/boundary owner;
   - M1 boundary interaction, ownership, rearm and range-rotation economics;
   - serves as a mechanistically different expert, not another fitted regressor.

5. INDEPENDENT_TRANSITION_PRECURSOR
   - causal pre-entry event-hazard model using BOCPD/run length, HSMM posterior/residual duration, micro acceleration, quote intensity, structural-distance trajectory and spread trajectory;
   - must generate pre-E060 opportunities rather than wait for E060.

Common expert output contract:
- Q_BUY and Q_SELL expected executable value;
- q10/q50/q90 or equivalent calibrated distributional value;
- P(value > 0);
- expected useful horizon / persistence;
- uncertainty.

Do not let all five experts share the same learner class or nearly identical feature ownership.

## R1.2 — Out-of-fold counterfactual regret labels
The router must never train on in-sample expert forecasts.

Use chronological purged/embargoed folds inside the established Jan fit region. Embargo must cover the maximum forward label/lifecycle overlap used by the unit. Do not use random k-fold.

For every router-training row:
- expert predictions must be generated out-of-fold;
- realized counterfactual utility is calculated only from future quotes used as labels, never as features;
- same-millisecond source ordering is preserved;
- no retrospective ideal fill;
- BUY executes at observed Ask, SELL at observed Bid;
- exit valuation uses the opposite executable quote and known fee contract.

Router target is conditional expected regret, not regime classification and not raw forecast MSE.

## R1.3 — Learned state-conditioned regret router
Inputs:
- hierarchical MACRO/MESO/MICRO/latent/execution state;
- out-of-fold expert value distributions;
- expert disagreement;
- expert predictive uncertainty;
- BETA039 friction/cost state;
- E060 benchmark features;
- no online trust features yet.

Outputs:
- expected regret per expert;
- soft top-2 expert weights;
- BUY / SELL / WAIT economic action;
- route entropy;
- top-two regret margin.

Start with a compact, reconstructible router such as shallow GBDT/GAM or small MLP only if a simpler model materially underfits.

Do not enforce uniform expert usage. Specialist concentration is acceptable if it is stable and economically justified.

## R1.4 — WAIT as economic deferral, not confidence decoration
WAIT is a real action with zero immediate trading reward and measurable opportunity cost.

The router should WAIT when:
- all actions have negative expected executable value; or
- uncertainty/regret gap is too small to justify spread/fee exposure; or
- the state is outside calibrated support.

Calibrate WAIT on the Jan calibration window with the existing opportunity/winner-retention guard. Do not achieve apparent improvement by deleting most trades.

Report the risk–coverage frontier:
- fraction traded;
- winners retained;
- gross profit retained;
- gross loss avoided;
- net value;
- route regret;
- WAIT false-negative opportunity cost.

## R1.5 — Router attribution metrics
Primary economic comparison:
A. BETA039 incumbent;
B. heterogeneous experts + fixed router;
C. B + learned counterfactual-regret router;
D. C + route uncertainty / top-2 / WAIT.

For every arm report:
- after-cost net;
- gross profit / gross loss;
- PF;
- floating DD;
- trades and winners retained;
- monthly/session/state decomposition where applicable.

Router-science diagnostics:
- mean/median realized regret;
- oracle gap;
- positive-oracle-value captured;
- expert selection frequency;
- top-two margin calibration;
- route entropy;
- route flip rate under small causal perturbations;
- alternate-expert win rate.

Do not proceed to online trust until the learned router materially beats the fixed-router arm for economic reasons.

## R1.6 — Entry→Hold continuation reliability without new EXIT optimization
The user has explicitly deferred HOLD+EXIT optimization. Therefore this unit may train and evaluate continuation value, but it must not introduce a new exit-specialist policy.

Use the shared continuation surface to answer:
- did the entry retain positive executable value after 250ms/1s/3s/5s/10s conditional on survival?
- which router/expert states show immediate value decay?
- does entry value remain calibrated after the initial fill cost?

Track:
- continuation calibration by age;
- conditional favorable/adverse event incidence;
- value decay from entry to each age;
- expert/router origin;
- friction and regime state.

Only after ENTRY routing is materially improved should continuation be granted additional control authority.

## R1.7 — Distribution-shift and execution-stress preflight
The existing Jan–Jul audit already shows material spread and short-horizon volatility drift. Keep cost state stochastic.

For any R1 candidate that clears Jan:
- freeze all parameters;
- replay Jan–Jul;
- report month-by-month economics and router regret;
- stress spread +10/+25/+50%;
- delayed fill to the next observed quote;
- quote gaps/staleness;
- same-millisecond ordering;
- latency jitter neighborhoods;
- no August access.

Uncertainty channels remain separate:
1. expert predictive uncertainty;
2. router allocation uncertainty;
3. regime/change uncertainty.

## Decision tree after R1
1. Oracle weak -> expert/event-clock redesign; do not optimize router.
2. Oracle strong, expert redundancy high -> prune/merge expert pool.
3. Oracle strong, complementary experts, router weak -> improve regret router.
4. Router strong, WAIT improves loss but destroys opportunity -> recalibrate deferral/uncertainty.
5. Router strong, entry value decays immediately -> continuation model becomes next research focus.
6. Entry and continuation both materially improve -> then authorize the later HOLD+EXIT research phase separately.

## Validation contract
Initial historical development window:
- FIT: Jan 1–Jan 9;
- CAL: Jan 9–Jan 11;
- DIAGNOSTIC: Jan 11–Jan 18 12UTC.

These are historically inspected and are not pristine OOS.

Any candidate crossing the internal continuation gate is frozen before Jan–Jul replay. August remains SEALED.

Owner-facing breakthrough gate remains >20% guarded whole-system improvement versus the correct BETA039 incumbent, with gross loss/DD/opportunity-retention safeguards. No official .mq5 without explicit owner approval.

## Reconstructible public research basis
- HSMM duration-aware state / residual duration: https://www.mql5.com/en/articles/24460
- BOCPD causal change probability/run length: https://www.mql5.com/en/articles/23482
- PID / synergy and redundancy with permutation null: https://www.mql5.com/en/articles/24382
- Unified purged validation / V-in-V / CPCV concepts: https://www.mql5.com/en/articles/21603
- Expert aggregation for financial forecasting / Bernstein Online Aggregation: https://www.sciencedirect.com/science/article/pii/S2405918823000247
- FactorMoE dynamic market/performance-conditioned gating: https://link.springer.com/article/10.1007/s40747-026-02307-2
- Strongly adaptive online conformal prediction: https://proceedings.mlr.press/v202/bhatnagar23a.html
- Multiple-expert learning-to-defer theory: https://proceedings.mlr.press/v267/mao25c.html
- FreqMoE as evidence that useful specialization can be induced by deliberately different signal domains: https://proceedings.mlr.press/v258/liu25i.html
- Trade survival/competing-risk framing is reserved as methodology input for later continuation/exit work, not as evidence that exits can rescue weak entries: https://www.mql5.com/en/articles/24106

None of these sources transfers profitability to XAUUSD. They support reconstructible architecture, validation and diagnostics only.

## Immediate bounded unit
**BETA_064_R1_COUNTERFACTUAL_REGRET_ROUTER_AND_UNCERTAINTY_JAN17P5**

Execution order:
1. R1.0 expert/event-clock oracle ceiling;
2. R1.1 expert heterogeneity integrity;
3. R1.2 OOF regret labels;
4. R1.3 learned router;
5. R1.4 WAIT/uncertainty;
6. R1.5 attribution;
7. R1.6 continuation reliability diagnostics;
8. if Jan gate passes, frozen Jan–Jul R1.7.

No online trust, conformal adaptation, or new exit policy is added until this unit establishes that the entry router itself has sufficient executable edge.
