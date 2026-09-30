# BETA064 — Hierarchical State-Conditioned Entry→Hold Mixture-of-Experts
**Date:** 2026-09-29  
**Status:** NEXT-ARCHITECTURE / HANDOFF ONLY — **NO NEW EMPIRICAL PROMOTION** — **NO MQL5 AUTHORIZATION** — **AUGUST SEALED**

Canonical detailed Google Doc:
https://docs.google.com/document/d/11i_q0MGhxxF6qamycPq6uGHliNVBVF1MlmWx4JmkkFQ/edit?usp=drivesdk

## Current empirical frontier

Latest verified empirical unit remains:
BETA_063_FIVE_SPECIALIST_SHARED_CONTINUATION_ENTRY_HOLD_FROZEN_7MO_62QA_NO_PROMOTION

Source:
https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/beta/research/BETA_063_FIVE_SOFT_EXPERT_ENTRY_HOLD_SHARED_CONTINUATION_VALUE_SPEC.md

BETA063 already implemented five soft experts plus shared continuation value. Do NOT rebuild BETA040–063 as new research.

## Why BETA064 must be structurally different

The next design addresses these BETA063 constraints:

1. E060 was still the mandatory parent opportunity clock.
2. Five specialists were semantically different but mathematically similar Ridge models over overlapping features.
3. The gate did not directly learn which expert has lowest state-conditional counterfactual regret.
4. Live continuation was principally refreshed at +5s rather than across several causal ages.
5. The fifth lead-up family adjusted an E060-based fill rather than creating an independent pre-E060 action clock.
6. The inherited BETA039 P89 cost gate carried substantial apparent benefit; the next model must find independent post-friction directional/continuation edge.

## BETA064 key change: independent causal entry clock

E060 becomes a feature and benchmark, NOT the master eligibility gate.

When flat, evaluate action on deterministic opportunity clocks such as:
- completed 250ms state update;
- material BOCPD change event;
- confirmed structural-level interaction;
- V8 M1 original boundary interaction.

Deduplicate clustered equivalent states deterministically.

The model directly compares LONG / SHORT / WAIT.

## Hierarchical state encoder

MACRO:
H4/H1/M15 trend/structure, regime posterior, regime age, residual duration.

MESO:
M5/M1 confirmed structural owner, literal level distance, touch count, acceptance/sweep, range state, compression/expansion.

MICRO:
S15/S5/S1/250ms displacement and acceleration, correctly signed quote pressure, tick/quote intensity, spread state, turns/efficiency, local roughness/vol-of-vol.

LATENT:
HSMM state posterior/residual duration + BOCPD change probability/run length.

EXECUTION:
live Bid/Ask, friction estimate, V8 minute boundary owner/rearm state, broker feasibility.

## Five heterogeneous specialists

1. TREND_IGNITION_SEQUENCE
Causal TCN/compact GRU. Predict early momentum continuation and residual runway from multi-scale sequence + HSMM/BOCPD state.

2. STRUCTURAL_RETRACE_TREE
Small nonlinear tree ensemble. Own literal confirmed M1/M5 level interactions, pullback depth, touch/age, acceptance and reacceleration.

3. RANGE_SWEEP_HAZARD
Discrete hazard/logistic model. Distinguish range rotation, failed sweep/reclaim, true acceptance and unresolved state.

4. V8_M1_AUCTION_FSM
Explicit finite-state/semi-Markov expert around authenticated V8 minute OCO/original-boundary/rearm state. No invented proprietary indicators.

5. INDEPENDENT_TRANSITION_PRECURSOR
Two-stage causal expert:
A. BOCPD/HSMM transition hazard.
B. GRU/TCN directional resolution.
Produces UP / DOWN / unresolved probability, expected time to resolution and executable value BEFORE/AT/AFTER traditional R9 events.

## Learned router: expert regret, not confirmations

Build a training-only counterfactual table for each opportunity clock and specialist action:
LONG / SHORT / WAIT plus bounded preliminary hold choices using observed future Bid/Ask for labels only.

For expert k:
Regret_k = best_counterfactual_value - value_of_expert_k_action.

Train a gate to predict low-regret experts and gate uncertainty.

No expert must confirm another expert.
Expert disagreement/entropy becomes a state feature and can make WAIT win naturally.

## Bounded online self-adaptation

Base gate weight = learned state-conditioned weight.

Reliability overlay updates only after completed historical outcomes:
- Brier/log-loss;
- value forecast error;
- state-bucketed exponentially decayed reliability.

Final weight proportional to base weight × exp(eta × lagged reliability).

Cap weight changes, minimum observations and expert min/max weights. Base neural/tree weights remain frozen live initially.

## Shared multi-age continuation value

Each expert predicts for LONG/SHORT and horizons such as 1/3/5/10/15/30/60s:
- expected executable after-cost return;
- uncertainty;
- adverse-tail quantile;
- continuation probability;
- failure probability.

The router aggregates those distributions.

Shared continuation value subtracts:
- expected spread/commission/slippage stress;
- uncertainty penalty;
- downside-tail penalty;
- opportunity cost.

At position age zero:
compare Q_LONG / Q_SHORT / Q_WAIT.

After fill:
the same value surface becomes Q_CONTINUE(current side, age), refreshed on causal age/state updates instead of only +5s.

For BETA064 Entry→Hold, keep terminal protective stop/target/hard-life fixed for attribution. HOLD→EXIT is a later phase.

## BETA039 friction role

Use BETA039 spread percentile as expected execution cost state, not a broad directional confirmation veto. Hard reject only for physical broker/order validity, stale/missing data or BETA015 risk/capital lock.

## Feature synergy

Use Partial Information Decomposition or controlled interaction tests to identify genuine synergy and redundancy rather than add filters.

Priority pairs:
- HSMM residual duration × micro acceleration
- structural distance × BOCPD change probability
- spread percentile × correctly signed quote pressure
- range state × reclaim velocity
- trend alignment × rough volatility
- V8 boundary age × regime state

## Research sources

- HSMM: https://www.mql5.com/en/articles/24460
- BOCPD: https://www.mql5.com/en/articles/23482
- HMM + GRU: https://www.mql5.com/en/articles/24056
- Market Intent MTF architecture: https://www.mql5.com/en/articles/24184
- PID: https://www.mql5.com/en/articles/24382
- Rough volatility: https://www.mql5.com/en/articles/24480
- TFT/divergence: https://www.mql5.com/en/articles/23493
- Adaptive financial MoE: https://www.sciencedirect.com/science/article/pii/S1877050926019988
- Expert aggregation: https://www.sciencedirect.com/science/article/pii/S2405918823000247
- FactorMoE: https://link.springer.com/article/10.1007/s40747-026-02307-2
- FreqMoE: https://proceedings.mlr.press/v258/liu25i.html
- Sparse MoE MQL5: https://www.mql5.com/en/articles/18527
- Hold→Exit competing risks reserved for phase two: https://www.mql5.com/en/articles/24106
- Gold Hunter V8 forensic: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/v8-cleanroom-baseline/docs/V8_RECONSTRUCTION.md

These are mechanism sources, not transferable XAUUSD profit guarantees.

## Stage-1 research

Window:
2026-01-01 00:00 UTC inclusive through 2026-01-18 12:00 UTC exclusive.
Original ordered Dukascopy Bid/Ask.

Historical nonblind partitions:
FIT Jan1–Jan9
CAL Jan9–Jan11
DIAGNOSTIC Jan11–Jan18 noon

Parallel arms:
1. Trend expert
2. Structural expert
3. Range hazard expert
4. V8 auction expert
5. Independent precursor expert
6. hierarchical MoE
7. hierarchical MoE + bounded online reliability

Incremental comparison must use the CURRENT incumbent, not the weak raw E060 baseline.

Owner reporting rule:
- >10% guarded improvement may justify further internal research.
- Only a **>20% guarded realized after-cost improvement** merits a breakthrough chat message.
- Failures stay in durable Google/repro records and trigger materially different model/source corrections.
- No daily automation and no background promise.

If a candidate qualifies, freeze parameters then run Jan–Jul. Jan–Jul is historically inspected, not pristine OOS. August remains sealed.

## Current safety/repro gates

- BETA005 full 17-layer materialized feature parity incomplete.
- BETA015 funded exact-risk proof required before investor claims.
- Coinexx native spread/commission/slippage/contract parity unresolved.
- Full original R9 REAL/SYNTH action/rearm parity incomplete.
- One position / 0.01 lot research convention.
- No official MQL5 source without owner approval.

## Next bounded unit

BETA_064_HIERARCHICAL_INDEPENDENT_CLOCK_ENTRY_HOLD_MOE_JAN17P5

New chat reads first:
1. beta/CURRENT_STATE.json
2. BETA063 report
3. this BETA064 handoff
4. BETA039 report
5. BETA035 V8 forensic
6. canonical BETA064 Google Doc
7. BETA Research Journal

### New-chat starter

Carson, continue Gold MUWHAHA Miner BETA from BETA064. Read live beta/CURRENT_STATE.json, BETA063, BETA064 handoff/Google Doc, BETA039 and BETA035 before testing. Do not repeat BETA040–063. E060 is now a feature/benchmark, not the master entry clock. Build five heterogeneous specialists: Trend Sequence, Structural Tree, Range/Sweep Hazard, V8 Auction FSM, and Independent Transition Precursor. Train a learned state-conditioned gate on expert regret/counterfactual utility, add bounded lagged expert reliability, use BETA039 friction as cost rather than confirmation, and use one shared multi-age continuation-value surface for Entry→Hold. Initial window Jan1–Jan18 12UTC original Dukascopy. Failed tests stay in durable research docs; only report >20% guarded breakthroughs. Freeze qualifying parameters before Jan–Jul. Do not open August. Do not write official MQL5 without explicit owner approval. Hold→Exit remains phase two.
