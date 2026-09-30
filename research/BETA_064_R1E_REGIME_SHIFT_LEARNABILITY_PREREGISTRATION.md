# BETA064-R1E — Regime-Shift Learnability & Adaptive Expert Representation Preregistration
**2026-09-29 | independent beta branch | RESEARCH ONLY | no MQL5 authorization | August SEALED**

## Trigger
The frozen BETA064-R1D January candidate achieved approximately 22.0% less loss on the historically inspected Jan11-Jan18 diagnostic window, but failed immediately on the first frozen February week. The first Feb segment produced approximately -$5,348 across 5,541 closes.

A causal support guard built only from January FIT limits reduced that February-week loss materially, but only by rejecting a large majority of February states. A normalized opportunity classifier retained Jan diagnostic discrimination near AUC 0.65 but fell to about 0.53 on the same February shock week. The five January-trained experts also failed together in the February shift. Therefore this is not treated as a router-threshold problem.

## Scientific question
When XAUUSD enters a scale/regime state outside January support, is Entry→Hold opportunity quality recoverably learnable from causal normalized state after a small amount of same-regime experience, or is the state intrinsically non-predictive at the required horizon/cost?

This unit tests learnability before implementing online adaptation.

## Data wall changed before deeper February outcome inspection
The first February week is already contaminated by the R1D frozen-failure diagnosis. It is therefore reassigned as a research/adaptation window and can never be called untouched validation.

Within that already-contaminated week:
- ADAPT-FIT: Feb 1 00:00 UTC through Feb 4 00:00 UTC exclusive.
- ADAPT-CAL: Feb 4 00:00 UTC through Feb 5 00:00 UTC exclusive.
- ADAPT-DIAG: Feb 5 00:00 UTC through Feb 7 00:00 UTC exclusive.

Later February segments and March-July are not to be used for R1E model selection. They remain later frozen replay windows, while acknowledging all Jan-Jul have historical project exposure and are not pristine OOS.

August remains SEALED.

## Mechanism
Keep the BETA064 independent causal 250ms event clock and exact Bid/Ask lifecycle.

Build a state-normalized representation using only contemporaneously observable quantities:
- spread / trailing range;
- return/displacement / trailing range;
- confirmed structural distance / completed M1 range;
- compression/expansion ratios;
- path efficiency;
- relative quote intensity;
- time-of-day;
- optional causal change/run-length descriptors.

No future normalization statistic is allowed.

Test three bounded questions:
1. opportunity learnability: P(max executable BUY/SELL utility > 0);
2. side learnability conditional on opportunity: BUY versus SELL;
3. side-specific value learnability: P(BUY utility > 0), P(SELL utility > 0).

Models are compact and reconstructible: shallow LightGBM / logistic / GAM-style tabular learners. No deep search.

## Advancement interpretation
- If same-regime opportunity AUC remains near chance, high-volatility states should be treated primarily as WAIT/OOD until a materially different expert mechanism is found.
- If opportunity discrimination returns materially but side discrimination does not, add a shared adaptive opportunity/support head while retaining heterogeneous directional experts.
- If both opportunity and side discrimination recover, proceed to a causal lagged adaptive expert/router layer whose updates use only outcomes after they become observable.
- If apparent economics come only from rejecting most opportunities, reject the mechanism.

This is a diagnostic learnability unit, not a strategy promotion.

## Constraints
- Original ordered Dukascopy Bid/Ask.
- BUY Ask / SELL Bid; exits on opposite executable quote.
- Same-ms source order preserved.
- $2 stop / $2 target / 30s common Entry→Hold lifecycle / $0.02 research fee for comparability.
- No SYNTH or OVERFIT inference.
- No new Hold→Exit specialist.
- No official MQL5 without owner approval.
- August SEALED.
