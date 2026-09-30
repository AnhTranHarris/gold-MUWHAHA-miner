# BETA064 R1A — Ceiling, Router Learnability & Microstructure Diagnostic Record

**Date:** 2026-09-29  
**Branch:** `beta`  
**Status:** DIAGNOSTIC RESEARCH ONLY — NO PROMOTION — NO MQL5 AUTHORIZATION — AUGUST SEALED

## Purpose

Execute a bounded empirical preflight for `BETA_064_R1_COUNTERFACTUAL_REGRET_ROUTER_AND_UNCERTAINTY_JAN17P5` before investing further complexity in the learned regret router.

The immediate questions were:

1. Does the five-family pool contain enough executable post-cost opportunity for routing to matter?
2. Are expert-local WAIT thresholds starving the router?
3. Does a longer Entry→Hold horizon expose more conditional opportunity?
4. Can tabular heterogeneous experts, economic classifiers, direct executable-utility regressors, or compact causal sequence models identify that opportunity?
5. Does adding tick-rule flow / quote-size imbalance materially improve learnability?

This record is deliberately diagnostic. It is not the final cross-fitted R1 proof and does not alter the latest verified BETA063 durable frontier.

## Data actually used

Source:
`XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`

Observed full file endpoint:
2026-01-30 21:59:51.954 UTC.

For the intended Jan1-Jan18-noon R1 window, market quotes naturally stop at the Friday Jan16 close before the Jan18 Sunday-noon cutoff.

No August data was accessed.

Execution economics in all reported screens:
- BUY enters observed Ask;
- SELL enters observed Bid;
- future valuation uses opposite executable quote;
- round-trip fee = $0.02 at the 0.01-lot / one-ounce research convention;
- source chronology retained;
- fixed-horizon Entry→Hold diagnostics only;
- no new EXIT specialist.

## Diagnostic 1 — 250ms five-family heuristic ceiling

The first bounded implementation reduced approximately 4.206M source ticks in the Jan1-Jan18-noon window to approximately 2.124M nonempty causal 250ms buckets.

Five deliberately different causal proxy families were evaluated:
- TREND;
- RETRACE;
- SWEEP;
- V8FSM;
- TRANSITION.

At the 15-second fixed-horizon diagnostic, every standalone proxy expert remained strongly negative after executable spread.

Sequential one-position results:

| Expert | Trades | Wins | Net | PF |
|---|---:|---:|---:|---:|
| TREND | 6,151 | 1,223 | -$4,416.01 | 0.173 |
| RETRACE | 2,214 | 385 | -$1,806.35 | 0.147 |
| SWEEP | 1,043 | 299 | -$776.69 | 0.285 |
| V8FSM | 3,666 | 586 | -$2,574.13 | 0.130 |
| TRANSITION | 6,264 | 1,266 | -$4,379.10 | 0.173 |
| naive fixed router | 10,382 | 1,802 | -$7,346.92 | 0.144 |

A hindsight-only expert-pool oracle was positive, but initially only about 1.65% of bucket events contained a positive 15-second action once expert-local activation thresholds were imposed.

Interpretation:
the expert-local admission thresholds were starving the pool. A router cannot allocate among specialists that mostly self-abstain.

## Diagnostic 2 — centralize WAIT ownership

Expert-local admission thresholds were removed. Each expert continuously published direction/value, and the shared router alone owned WAIT.

This materially increased the diagnostic ceiling:
- 15-second oracle-positive event rate: ~27.94%;
- sequential hindsight oracle: +$4,559.08 / 14,170 non-overlapping 15s trades;
- oracle ownership was distributed, not single-expert collapse:
  - TREND ~57.4% of positive oracle events;
  - RETRACE ~18.2%;
  - V8FSM ~19.1%;
  - TRANSITION ~5.1%;
  - SWEEP ~0.1%.

However, the FIT-only HGB utility router could not learn the allocation. The CAL interval contained no defensible positive threshold with sufficient trade count, and the later DIAG replay remained strongly negative.

Decision:
**WAIT should remain router-owned. Do not restore five separate expert admission gates.**

## Diagnostic 3 — Entry→Hold horizon sweep

The continuous expert pool was replayed at 15s / 30s / 60s / 90s.

Best standalone PF improved with longer holding horizon but remained unprofitable:

| Horizon | Best standalone PF | Best family | Oracle-positive event rate | Sequential oracle net |
|---:|---:|---|---:|---:|
| 15s | ~0.111 | SWEEP | 27.94% | +$4,559.08 |
| 30s | ~0.202 | V8FSM | 40.03% | +$4,623.88 |
| 60s | ~0.325 | V8FSM | 50.97% | +$4,095.41 |
| 90s | ~0.354 | V8FSM | 56.25% | +$3,582.94 |

Interpretation:
longer Entry→Hold horizons reveal much more ex-post path opportunity, but current causal expert scores still do not forecast ownership well enough to overcome spread.

## Diagnostic 4 — heterogeneous learned 60-second expert heads

A memory-bounded 1-second causal training representation was used as a computational diagnostic. This does **not** replace the eventual 250ms implementation target.

FIT: Jan2-Jan9, deterministic 1-second training sample.  
CAL: Jan9-Jan11.  
DIAG: Jan11 through the available Friday Jan16 close.

Expert classes:
- TREND_HGB;
- STRUCT_HGB;
- SWEEP_RIDGE;
- TRANS_HGB;
- V8_FSM_VALUE.

Best DIAG standalone PFs:
- TREND_HGB ~0.539;
- STRUCT_HGB ~0.526;
- SWEEP_RIDGE ~0.505;
- TRANS_HGB ~0.544;
- V8_FSM_VALUE ~0.514.

Learned router:
- 8,672 sequential 60s trades;
- 3,332 winners;
- net -$7,506.91;
- PF ~0.533.

Hindsight expert-direction oracle:
- +$27,843.16;
- 18,089 non-overlapping positive trades;
- ~55.98% event-level positive availability.

Interpretation:
heterogeneous learners improve raw directional quality relative to the initial proxies, but router learnability remains far below the expert-direction ceiling.

## Diagnostic 5 — positive-after-cost classification

A direct economic classification probe predicted:
- P(BUY executable utility > 0);
- P(SELL executable utility > 0).

FIT positive rates were approximately:
- BUY 26.61%;
- SELL 25.28%.

The classifier showed some discrimination: later high-score bins reached approximately 41% positive outcomes. But average executable utility remained negative in every probability bin and every CAL threshold with meaningful coverage.

Selected DIAG:
- 4,682 sequential trades;
- 1,908 wins;
- net -$3,909.72;
- PF ~0.549.

Interpretation:
directional probability alone is insufficient; adverse magnitude and friction dominate.

## Diagnostic 6 — direct executable-utility regression

Two HGB heads directly predicted BUY and SELL future executable dollar utility rather than mid-return or binary profitability.

FIT mean 60-second executable utility:
- BUY approximately -$0.749/event;
- SELL approximately -$0.792/event.

No meaningful CAL threshold had positive expected utility.

Selected DIAG:
- 6,949 trades;
- 2,586 wins;
- net -$5,059.40;
- PF ~0.499.

Interpretation:
changing the target from price return to direct utility did not recover a deployable edge. This argues against a mere loss-function mismatch.

## Diagnostic 7 — compact causal TCN sequence probe

A small causal temporal convolutional network consumed the preceding 30 one-second states and classified BUY / SELL / WAIT for 60-second executable outcomes.

Bounded CPU run:
- 71,393 FIT sequences;
- 33,019 CAL sequences;
- 3 epochs.

Training loss remained near the three-class entropy floor and confidence collapsed tightly around one-third. The model overwhelmingly selected SELL and produced no economically useful confidence separation.

DIAG:
- 12,642 trades;
- 3,883 wins;
- net -$10,324.43;
- PF ~0.461.

Interpretation:
simply replacing tabular heads with a generic neural sequence model is not sufficient. No neural-model promotion is justified.

## Diagnostic 8 — tick-rule flow + quote-size imbalance

A materially different microstructure state source was constructed from the original ticks:
- tick-rule direction / signed tick-flow;
- rolling flow imbalance;
- quote-update intensity;
- Dukascopy bid/ask quote-size imbalance;
- spread level and spread transition/compression;
- volatility-normalized displacement;
- session phase.

Important limitation:
Dukascopy quote sizes are quote-state proxies, not true aggressor trade volume.

Direct 60-second utility HGB results:
- selected DIAG: 4,652 trades;
- 1,709 wins;
- net -$2,742.77;
- PF ~0.543;
- WAIT ~92.0%.

A simple strong flow + quote-imbalance agreement cohort was worse:
- 7,963 trades;
- net -$7,280.50;
- PF ~0.463.

Interpretation:
microstructure proxies reduce loss relative to several generic screens but do not yet create positive after-cost expectancy. Simple flow alignment is specifically rejected.

## Consolidated finding

The repeated diagnostics support five conclusions:

1. **There is substantial hindsight conditional path diversity.**
   The five-family action pool frequently contains a positive side at 30-90 second horizons.

2. **The current causal representation cannot identify that ownership reliably enough.**
   This remains true across heuristic routing, heterogeneous tabular models, economic classification, direct utility regression, a compact TCN, and first-pass tick-flow microstructure features.

3. **Expert-local WAIT is structurally harmful.**
   Experts should publish value distributions; the shared router should own WAIT.

4. **Longer Entry→Hold horizons are more promising than 15 seconds.**
   60-90 seconds materially improve standalone PF and increase conditional positive opportunity, though still not to profitability.

5. **The next research problem is state/event definition, not router sophistication.**
   Further router optimization on the current feature contract would be polishing the wrong bottleneck.

## Public reconstructible source correction

The next mechanism should use event-conditioned microstructure state rather than more clock-grid return lags.

Relevant reconstructible public basis:

- MetaQuotes, *Market Microstructure in MQL5 (Part 5): Microstructure Noise*:
  https://www.mql5.com/en/articles/22938
  - emphasizes that friction/noise and volatility are distinct;
  - states that genuine microstructure work belongs at tick/sub-minute resolution.

- MetaQuotes, *Market Microstructure in MQL5 (Part 6): Order Flow*:
  https://www.mql5.com/en/articles/22939
  - supplies intensity / flow-state concepts.

- MetaQuotes, *Beyond the Clock (Part 1): Building Activity and Imbalance Bars in Python and MQL5*:
  https://www.mql5.com/en/articles/22063
  - supports adaptive event sampling based on directional activity rather than fixed clock intervals.

- MetaQuotes, *Tick Buffer VWAP and Short-Window Imbalance Engine*:
  https://www.mql5.com/en/articles/19290
  - reconstructible tick-buffer imbalance / flow / spread concepts.

These are mechanism sources only; none is accepted as transferred XAUUSD alpha.

## Next bounded unit

**BETA_064_R1B_EVENT_CONDITIONED_MICROSTRUCTURE_HAZARD_AND_INFORMATION_CLOCK**

Do not add Hold+Exit.

Goals:
1. replace the unconditional 250ms opportunity flood with an **information-event clock** driven by causal activity/imbalance state change while preserving the ability to act pre-E060;
2. construct tick-level state transitions rather than only rolling summaries:
   - imbalance acceleration/deceleration;
   - sign-run persistence and reversal;
   - quote-pressure transition;
   - spread compression/expansion trajectory;
   - intensity burst and decay;
   - volatility-normalized displacement;
   - sweep/reclaim ownership;
3. train a transition/hazard model for:
   - profitable continuation emerging within 1/3/5s;
   - useful 30/60/90s runway;
   - failure/noise state;
4. preserve expert continuous outputs and central router WAIT;
5. only return to counterfactual-regret routing if R1B materially improves expert-pool **predictability**, not merely the hindsight oracle.

No August access. No official MQL5.
