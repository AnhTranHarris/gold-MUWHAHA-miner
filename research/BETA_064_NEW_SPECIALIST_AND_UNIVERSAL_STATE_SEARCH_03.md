# BETA064 — NEW SPECIALIST / UNIVERSAL-STATE SEARCH 03

**Date:** 2026-09-30  
**Status:** RESEARCH CHILD — NO CHECKPOINT CHANGE — NO MQL5 AUTHORIZATION  
**Frozen control:** Major Checkpoint 02 = 5,070 Jan–Jul Entry→Hold trades / 88.44% weighted survivability / all observed months >85%  
**August:** SEALED  
**Alpha/GAMMA:** not used

## Objective

Search reconstructible community mechanisms for genuinely orthogonal Entry specialists or universal state layers that could expand BETA064 Entry→Hold opportunity coverage without weakening the preferred >=85% monthly survivability standard.

This unit specifically evaluated:
- Structural Fibonacci / OTE pullback
- Heikin-Ashi pullback / reacceleration
- Auction / Market Profile acceptance and rejection
- Hurst / entropy regime state
- two-state Kalman level/velocity + innovation state
- Ornstein-Uhlenbeck / half-life / stationarity mean-reversion state
- developing TPO / POC / Value Area context

Community performance claims were not imported. Only reconstructible mechanics were implemented and tested on the original Dukascopy Jan–Jul Bid/Ask tick corpus.

## Community mechanics retained as hypotheses

### Fibonacci / OTE

Public open implementations commonly:
- anchor retracement zones to confirmed market structure / BOS / CHoCH;
- use roughly 61.8%-78.6% retracement zones;
- require a completed displacement leg and later retracement;
- often add session, FVG, ATR or volatility context.

BETA interpretation: this is structurally closest to an E2/E4 pullback child, not an automatically orthogonal universal Entry desk.

### Heikin-Ashi

Public implementations generally use HA as a smoothing / trend-state transform, then require real-price EMA/trend/momentum context and a pullback/reacceleration sequence.

BETA interpretation: HA is a potential timing/state adapter, not sufficient evidence for standalone direction.

### Auction / Market Profile

Public open implementations expose:
- POC;
- VAH / VAL;
- Initial Balance;
- value migration;
- acceptance vs rejection;
- profile shape / balance vs imbalance;
- excess / single prints.

BETA interpretation: this is more orthogonal than Fib or HA and could theoretically serve as a universal auction-state layer or a new specialist family.

### Hurst / Kalman

Public implementations use:
- Hurst >~0.5 for persistence/trend and <~0.5 for anti-persistence/mean reversion;
- Kalman level + velocity as latent trend state;
- innovation / surprise magnitude as a regime / shock descriptor.

BETA interpretation: candidate universal state layer.

### OU / statistical mean reversion

Open implementations estimate:
- equilibrium mean mu;
- mean-reversion speed theta;
- half-life;
- residual/stationary sigma;
- z-score / overshoot;
- often combine these with Hurst, ADF/stationarity or variance-ratio gates.

BETA interpretation: candidate E6-specific admission state intended to reject trend-contaminated “false reversion” excursions.

## E17-E19 causal tick-level test

All candidate states were computed only from completed historical bars / current completed state. Future raw Bid/Ask ticks were used only for offline Entry→Hold labeling under the existing BETA barrier geometry.

### E17 Structural Fibonacci OTE

Mechanism:
confirmed structural impulse -> causally locked leg -> 61.8%-78.6% retracement -> same-direction reacceleration.

Jan–Jul:
- 6,964 proposals
- 12.65% raw Entry→Hold survival
- 10.27% favorable-first-passage
- negative diagnostic path value

Leave-one-month-out admission modeling:
- no fold could construct a six-development-month gate satisfying >=85% survival with positive diagnostic value.

Decision:
**REJECT standalone Entry authority.**
Carry Fibonacci retracement depth / structural-leg location only as potential E2/E4 context.

### E18 Heikin-Ashi Pullback Reacceleration

Mechanism:
completed 15-second HA state; real-price higher-horizon trend ownership; one/two adverse HA bars; HA flip/reacceleration with limited adverse wick and friction controls.

Jan–Jul:
- 18,139 proposals
- 17.91% raw survival
- 11.90% favorable-first-passage
- negative diagnostic value

Held-out survival-model discrimination remained nonrandom, with monthly AUC approximately 0.687-0.744, but no six-development-month >=85% admission gate existed.

Decision:
**REJECT standalone Entry authority.**
Retain HA state as possible E2 structural-pullback timing context.

### E19 Auction Profile

Two clocks were tested from a causal developing TPO profile:
- E19_AUCTION_ACCEPT: repeated completed closes outside VAH/VAL with activity and non-opposing POC migration.
- E19_AUCTION_REJECT: excursion beyond value edge followed by completed close back inside value toward POC.

Jan–Jul:
- Acceptance: 23,631 proposals / 15.85% raw survival
- Rejection: 3,622 proposals / 22.17% raw survival
- both negative diagnostic value

Held-out survival discrimination:
- Acceptance monthly AUC roughly 0.709-0.752
- Rejection roughly 0.673-0.749
- no six-development-month >=85% admission gate for either clock.

Decision:
**REJECT standalone Entry authority.**
The information is real but insufficient as a new position-owning desk.

## Universal Hurst / entropy / Kalman ablation

A completed 15-second universal state packet was added to reconstructed E1-E12 candidate populations:
- R/S Hurst estimate
- sign entropy
- two-state Kalman normalized velocity
- normalized innovation shock
- normalized state uncertainty
- side-aligned velocity / innovation

Cross-month survival-AUC delta versus the same model without these features:

- E2 Pullback/Reacceleration: **+0.0344** — material
- E7 Sweep/Reclaim: +0.0014
- E11 Kinetic Ignition: +0.0013
- E12 Failed Expansion: +0.0010
- E6 Value Reversion: +0.0008
- E8 Level Bounce: +0.0005
- E10 Compression Release: +0.0004
- E9 Level Break: approximately flat
- E5 VWAP Reclaim: slightly negative
- E3 / E1 / E4: negative

Decision:
**REJECT as universal router.**
Carry Hurst/Kalman as a targeted E2 structural-pullback adapter and possibly limited diagnostic context elsewhere.

## E6 OU / statistical-reversion ablation

Added:
- AR/OU phi
- half-life
- OU z-score
- ADF-like stationarity slope statistic
- variance ratio q=4
- side-aligned OU z-state

On broad reconstructed E6:
- baseline weighted held-out survival AUC: ~0.69900
- OU-enriched AUC: ~0.69973
- delta: **+0.00073**

OU-ranked held-out tails:
- top 1%: ~63.5% survival
- top 0.5%: ~66.9%
- top 0.2%: ~68.3%
- top 0.1%: ~75.9%, approximately flat / slightly negative aggregate diagnostic value

Decision:
**OU is not the missing E6 engine.**
Retain half-life/stationarity/OU z-state as secondary E6 features only.

## TPO / Market Profile parent-context ablation

A causal developing profile state was attached to broad E5/E6/E7/E9/E10/E12 candidates:
- POC
- VAH / VAL
- normalized location vs POC
- value-area width
- POC migration
- value-area expansion
- profile-shape skew
- side-aligned location / migration

Weighted held-out survival AUC deltas:
- E6: +0.00009
- E12: -0.00004
- E9: -0.00014
- E7: -0.00149
- E10: -0.00154
- E5: -0.00183

Decision:
**REJECT TPO as a universal BETA router in this form.**

## Scientific conclusion

The search does not support adding Fibonacci, Heikin-Ashi, Auction Profile, Hurst/Kalman, OU, or TPO as a thirteenth universal Entry system.

The repeated pattern is:

1. each mechanism contains some measurable state information;
2. none provides a portable new >=85% Entry→Hold opportunity population;
3. added complexity does not justify production authority merely because a method is sophisticated;
4. specialist-specific use is more defensible than universal gating.

## Carry-forward map

### E2 Structural Pullback / Reacceleration
Highest-value new context:
- Hurst persistence state
- Kalman latent velocity / innovation
- optional Fibonacci retracement-depth state
- optional completed HA pullback/reacceleration state

This is the clearest positive information gain in this unit.

### E6 Value Reversion
Carry as secondary features only:
- OU half-life / stationarity / z-state
- Hurst anti-persistence
- auction/value location
Do not broaden the E6 clock.

### E7 / E9
Continue existing parent-quality repair.
Auction/TPO and universal regime additions did not solve portability.

### E10 / E12 / E5
Continue parent-adjacent capacity recovery.
The broad universal layers did not improve their held-out discrimination.

### E11
Remain saturated / control. Do not expand.

## Next recommended bounded research

**BETA064_C02H_PARENT_ADJACENT_RECOVERY_WITH_SPECIALIST_SPECIFIC_ADAPTERS**

1. Recover / reconstruct unused parent-adjacent candidate states rather than inventing new clocks.
2. E2: explicitly test combined Fib depth + HA state + Hurst/Kalman adapter.
3. E6: combine OU/half-life only with the authoritative session-specific C02G derivative state; do not use OU as standalone authority.
4. E10/E12/E5: capacity recovery through exact parent state and one-position ownership.
5. E7/E9: quality repair through parent thesis, not broad market-profile complexity.
6. Require new additions themselves to demonstrate >=85% held-out survival where sample size is adequate, positive diagnostic value, and increased final portfolio trade count.
7. Major Checkpoint 02 remains immutable.
8. Hold->Exit deferred.
9. August sealed.
10. No MQL5 change.

## Public reconstructible references

- MQL5 Hurst Exponent article: https://www.mql5.com/en/articles/15222
- TradingView Kalman State-Space Trend: https://www.tradingview.com/script/1coOxasg/
- TradingView Joint-State Kalman Filter: https://www.tradingview.com/script/keVAuPgL-Joint-state-Kalman-Filter-Linear-Extended-Unscented/
- TradingView Fibonacci Entry Zone OTE: https://www.tradingview.com/script/eiPdcVDT/
- TradingView Fibo/FVG: https://www.tradingview.com/script/058CAuCS-Fibo-FVG/
- TradingView Heikin-Ashi Trend: https://www.tradingview.com/script/bc5hpyBr-Rishi-Heikin-Ashi-Trend/
- TradingView TPO Auction & Value Profile: https://www.tradingview.com/script/46QaaPri-TPO-Auction-Value-Profile/
- TradingView Statistical Mean-Reversion Engine: https://www.tradingview.com/script/RwVTfoTY-Statistical-Mean-Reversion-Engine-SMRE/
- TradingView Ornstein-Uhlenbeck Reverter: https://www.tradingview.com/script/0soh5Bfu-Ornstein-Uhlenbeck-Reverter-forexobroker/
