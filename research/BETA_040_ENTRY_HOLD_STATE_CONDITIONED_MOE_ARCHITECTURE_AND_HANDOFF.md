# BETA040 — State-Conditioned Entry→Hold Mixture-of-Experts architecture + new-chat handoff
**Date:** 2026-09-29  
**Status:** ARCHITECTURE / RESEARCH DIRECTIVE ONLY — **NO NEW EMPIRICAL PROMOTION** — **NO MQL5 AUTHORIZATION** — **AUGUST SEALED**

Canonical detailed Google Doc:
https://docs.google.com/document/d/11i_q0MGhxxF6qamycPq6uGHliNVBVF1MlmWx4JmkkFQ/edit?usp=drivesdk

## Architectural pivot

Do not stack additional confirmation filters. Treat ENTRY and HOLD as one value problem:

- entry = first hold decision at position age 0;
- every specialist predicts future executable return, downside and continuation probability;
- a soft state-conditioned router weights specialists rather than deleting opportunities with hard confirmations;
- a shared continuation-value head compares LONG, SHORT and WAIT;
- BETA039 signed P89 rolling spread becomes an execution-friction/cost feature rather than the main directional gate, except where broker rules make an order impossible;
- HOLD→EXIT is the next phase after Entry→Hold earns a real breakthrough.

Hard vetoes only: impossible order geometry, stale/missing quote beyond declared tolerance, risk/capital lock, position ownership, margin/lot/broker constraints, and data-integrity failure.

## Five required Entry→Hold experts

1. **TREND_IGNITION_CONTINUE** — salvage fast-accept + compression/expansion; use MTF trend, HSMM duration/runway, short-tick acceleration and volatility state.

2. **STRUCTURAL_RETRACE_REACCEL** — upgrade prior origin-retrace into true confirmed M1/M5 structural-level ownership, retreat depth and reacceleration.

3. **RANGE_SWEEP_RECLAIM** — range/high-vol-chop specialist using confirmed sweep vs body acceptance, reclaim state and counter-momentum.

4. **V8_M1_AUCTION_BOUNDARY_OWNER** — use the authenticated Gold Hunter V8 clean-room M1 OCO/opposite-original-boundary rearm FSM as a specialist state/action model; proprietary hidden logic remains unknown.

5. **TRANSITION_PRECURSOR** — owner-requested lead-up expert. Causal GRU/TCN first; TFT only if simpler sequence model lacks incremental information. Predict transition-to-up, transition-to-down, resolution time and executable return from 250ms/1s/5s/15s/M1 sequences plus regime/structure state.

## Shared state

Use only decision-time-observable inputs:
- live Bid/Ask, spread percentile, quote age, tick intensity;
- 250ms/1s/5s path acceleration, correctly signed quote pressure, efficiency and turns;
- confirmed S15/M1/M5 structure and literal level distance/age/touches;
- M15/H1/H4 trend vector and disagreement;
- HSMM regime posterior + residual duration;
- BOCPD change-point probability / run length;
- rough-volatility / vol-of-vol state;
- V8 minute-boundary ownership and rearm phase;
- once filled: age, executable PnL, past-only MFE/MAE, live state and blocked-opportunity estimate.

## Soft routing and self-adaptation

Base expert weights:
w_base_k(t) = softmax(G_k(State_t)).

State-conditioned reliability is updated only after prior forecast outcomes are fully known.

Final expert weight:
w_k(t) proportional to w_base_k(t) × exp(eta × reliability_k(state)).

Use Brier/log-loss/value calibration rather than recent profit alone. Cap per-update changes and expert weight ranges. Base model parameters remain frozen in live MT5 initially; only bounded lagged calibration adapts online.

## Shared continuation-value model

Every expert k outputs for side d and horizons h={1,3,5,15,30 sec}:
- expected executable after-cost return mu[k,d,h];
- uncertainty sigma[k,d,h];
- adverse-tail estimate qdown[k,d,h];
- favorable continuation probability psurvive[k,d,h].

Mixture:
mu_mix[d,h] = SUM_k w_k × mu[k,d,h].

Shared continuation value:
CV(d,t) = SUM_h horizon_weight(h,state,age) ×
[mu_mix - lambda_uncertainty×sigma_mix - lambda_tail×qdown_mix
 - expected_execution_cost - opportunity_cost]
+ lambda_survival×psurvive_mix.

At age=0 compare Q_LONG, Q_SHORT and Q_WAIT. Choose the highest only when its value clears an uncertainty margin. This is direct value competition, not a confirmation stack.

After fill, recompute CV(current_side, current_position_age, live_position_state) continuously as HOLD_VALUE. During Entry→Hold research use a simple/fixed terminal safety mechanism for attribution; dynamic Hold→Exit is deferred to phase two.

## Prior BETA components repurposed

- BETA031 duration-aware MoE -> regime-age/router prior, not direction owner.
- BETA033 origin retrace -> structural specialist.
- BETA033/BETA039 sweep-reclaim -> range/reversal specialist.
- compression/expansion -> trend-ignition input.
- BETA035 V8 OCO/rearm -> auction-state specialist + opportunity generator.
- BETA039 signed-P89 spread -> friction/cost term.
- BETA030/031 multivariate features -> shared state representation.

## Source models worth reconstructing

- HSMM XAUUSD MQL5: https://www.mql5.com/en/articles/24460
- BOCPD: https://www.mql5.com/en/articles/23482
- HMM + GRU regime/sequence: https://www.mql5.com/en/articles/24056
- Multi-timeframe Market Intent: https://www.mql5.com/en/articles/24184
- Partial Information Decomposition: https://www.mql5.com/en/articles/24382
- Rough volatility: https://www.mql5.com/en/articles/24480
- TFT/divergence sequence model: https://www.mql5.com/en/articles/23493
- Meta-labeling: https://www.mql5.com/en/articles/18864
- Adaptive financial MoE: https://www.sciencedirect.com/science/article/pii/S1877050926019988
- Online expert aggregation: https://www.sciencedirect.com/science/article/pii/S2405918823000247
- FreqMoE: https://proceedings.mlr.press/v258/liu25i.html
- Competing-risks exits reserved for phase two: https://www.mql5.com/en/articles/24106

These are mechanisms/architectures, not transferable XAUUSD alpha guarantees.

## Phase-1 targets

Do not train only on fixed +15s direction. For every source event and both sides build OFFLINE-only labels:
- executable after-cost return at 1/3/5/10/15/30s;
- MFE/MAE to each horizon;
- probability of remaining above break-even once positive;
- time to first positive after-cost state;
- time to material failure;
- incremental continuation return at each alive position age.

Use multi-horizon Huber loss, downside quantile loss, continuation-survival log loss, calibration penalty and mild router entropy/load-balancing. Future labels never enter runtime features.

## Experimental funnel

Initial source window: **2026-01-01 00:00 UTC inclusive through 2026-01-18 12:00 UTC exclusive**, original ordered Dukascopy Bid/Ask ticks.

Controls:
A. E060 + fixed L30;
B. BETA039 signed-P89 + fixed L30;
C. each five experts alone with shared continuation head;
D. MoE without adaptive reliability;
E. MoE with lagged adaptive reliability.

Owner reporting rule:
- strict >10% can continue research;
- **only >20% guarded realized after-cost improvement is worth surfacing in chat as a breakthrough**;
- preserve meaningful trade count, winner count, gross loss and risk;
- failed tests stay in durable research docs/repro artifacts, trigger materially different source/model corrections and reruns, and do not become chat failure reports;
- do not brute-force tiny parameter grids around failed ideas.

If initial window passes, freeze parameters and run Jan–Jul. Jan–Jul is historically inspected, not untouched OOS. August remains sealed.

## Current empirical handoff

Last verified empirical unit remains:
BETA_039_SIGN_CORRECTED_CAUSAL_ROLLING_QUOTE_FRICTION_JANJUL_160QA_RESEARCH_ONLY.

BETA039 corrected P89:
- baseline Jan–Jul shadow net: -$134,000.72;
- candidate: -$118,080.34;
- 11.881% less negative net;
- 91.743% baseline winners retained;
- 90.866% trade volume retained;
- all seven months still negative;
- NOT BETA015 funded, NOT Coinexx native parity, NOT approved EA.

BETA005 full 17-layer materialized feature parity remains incomplete. BETA015 funded proof remains outstanding. No official MQL5 candidate is authorized. No recurring/daily automation belongs in this project. August SEALED.

## Next bounded unit

BETA_040_ENTRY_HOLD_STATE_CONDITIONED_MOE_JAN17P5

New chat first reads:
1. live beta/CURRENT_STATE.json;
2. this file;
3. BETA039 report;
4. BETA035 V8 forensic;
5. canonical BETA040 Google Doc.

Do not restart old BETA025–039 experiments.

### Copy-paste new-chat prompt

Carson, continue Gold MUWHAHA Miner BETA research from BETA040 Entry→Hold State-Conditioned Mixture-of-Experts. Read live beta/CURRENT_STATE.json, the BETA040 GitHub handoff and BETA040 Google Doc first. Build/test five experts in parallel: Trend Ignition, Structural Retrace, Range/Sweep-Reclaim, V8 Auction/Boundary Owner, and Transition Precursor. Use soft state routing, HSMM duration, BOCPD change probability, multi-timeframe state, correctly signed quote features, and BETA039 rolling friction as a cost term. Use one shared continuation-value model linking ENTRY and HOLD. Initial test Jan1–Jan18 12UTC original Dukascopy ticks. Failed screens stay in durable docs; only report a >20% guarded breakthrough in chat. Freeze qualifying parameters before Jan–Jul. Do not open August and do not write official MQL5 without explicit owner approval. Hold→Exit is phase two.
