# F401-R118-H — L1 microprice / depletion / replenishment toxicity state — PREDECLARED

R118-G cooperative council is parked after weak Jan VAL and weak frozen transfer. R118-H changes the source-state mechanism, not thresholds or meta-model structure.

## Mechanistic basis
Use only the registered Dukascopy best bid/ask prices and quoted sizes. Construct the opposite-size weighted L1 microprice:
microprice = (ask * bid_size + bid * ask_size) / (bid_size + ask_size).
This is a top-of-book quoted-liquidity estimator. It is NOT L2 depth, executed trade volume, aggressor flow, queue position, or proof of tradable alpha.

The mechanism is informed by Stoikov-style microprice/imbalance research and order-flow-imbalance literature, but is independently implemented on the authorized XAUUSD source. Public implementations/papers are hypothesis sources only.

## Causal state families
For each original immutable t0, consume source quotes with timestamp strictly < t0.

Across 0.25/0.5/1/2/5/10/30/60/120s and last 8/16/32/64/128 quotes derive:
1. side-aligned microprice-mid edge / spread, persistence, sign flips, slope, dispersion and price-vs-microprice divergence;
2. best-bid/best-ask quoted-size depletion/replenishment conditional on unchanged best price;
3. size shocks accompanying bid-only / ask-only / joint price revisions;
4. absorption proxy: repeated unchanged best price with same-side size replenishment after depletion;
5. liquidity-vacuum proxy: own-side quoted liquidity depletion while opposite-side liquidity persists or replenishes;
6. replenishment/depletion velocity per second and per quote;
7. signed size-adjusted spread pressure and imbalance acceleration;
8. microprice crossings/divergence relative to completed M1/M5/M15/H1 support/resistance and 0.5/1/2/5/10-dollar grids;
9. state duration / transition counts for favorable-pressure, adverse-pressure, vacuum and absorption states.

No current/equal-time quote is used. No missing L2 event type is fabricated.

## Foresight heads
Fit on Jan chronological FIT only:
- direct wrong-vs-correct;
- opposite-vs-correct;
- neutral-vs-correct;
- teacher-veto phenotype auxiliary/distillation;
- independent correct guardian.
Use high-capacity deterministic LightGBM with the new microstructure bank plus only minimal causal context: side/session, completed multi-TF geometry, matured prior outcomes. Do not feed the earlier R118 aggregate scores.

Freeze score formula/cut on Jan CAL at predeclared correct-loss budgets 0.10/0.25/0.50/1/2/5%, then score Jan VAL and full Feb/Jun/Jul unchanged. Report wrong/opposite/neutral veto, correct lost, teacher overlap/missed wrong, side/session stability and total four-month unique wrong veto.

## Stop rule
If explicit microprice/depletion/replenishment states do not materially raise selective wrong-veto capacity, retire this exact mechanism. Next successor must change representation/supervision again (self-supervised quote-state pretraining or latent regime mixture), not retune nearby horizons/leaves/cuts.
