# BETA064-R1B — Multi-Desk ENTRY→HOLD Specialist Architecture & Community Source Audit

**Date:** 2026-09-30  
**Branch:** beta  
**Status:** RESEARCH ARCHITECTURE / SOURCE AUDIT ONLY — NO MQL5 AUTHORIZATION — AUGUST SEALED

## Why this unit exists

BETA064-R1A showed that five broad specialists plus one shared continuation model still leave major conditional-expectancy gaps. The next question is not merely whether the router needs a better loss function. It is whether the specialist universe is too narrow and too overlapping.

This note audits the historical “12-strategy/specialist” community sources and defines a larger but deliberately orthogonal two-floor architecture:

1. multiple ENTRY specialists, each owning a distinct market mechanism and timeframe hierarchy;
2. multiple HOLD specialists, each owning a distinct post-entry trajectory state;
3. one shared economic router/value arbiter above each floor;
4. no dedicated HOLD+EXIT optimization yet.

## Source audit

### 1. BAKOME-Hub/BakomeBandiaEA — historical 12-strategy lead

Repository:
https://github.com/BAKOME-Hub/BakomeBandiaEA

The project describes itself as an XAUUSD EA with 12 strategies, ICT concepts, grid logic, session filters and multi-timeframe analysis.

However, the current repository is not a usable implementation source. The file named `BakomeBandiaEA.mq5` contains the same README/marketing text as `README.md`, not executable MQL5 strategy code. The twelve strategy definitions therefore cannot be reconstructed from this repository.

Decision:
- performance claims receive zero evidentiary weight;
- do not import/copy strategy logic because the logic is not actually disclosed;
- keep only the architectural hypothesis that a broader multi-strategy XAUUSD system was intended.

### 2. Gold Beaver — 12 selectable XAUUSD operating modes

Public MQL5 page:
https://www.mql5.com/en/market/product/177869

The current public page documents 12 selectable modes grouped as:
- CONS: HiWR-V3, F90-PathW, V3-A-Only
- BAL: HiWR-V2, V3-2Eng, V3-A-Active, V2-Legacy, F91-Balanced
- AGG: V3-Triple, V3-Triple-V2, V3-A-Dual, F92-Aggressive

It also ranks the modes over recent 7/14/30-day broker results.

But detailed strategy formulas are not public; user reviews explicitly note limited documentation of the differences between the 12 modes.

Decision:
- useful architectural evidence for dynamic strategy ranking / mode adaptation;
- not reconstructible enough to become a BETA specialist source;
- do not infer hidden strategy formulas from names.

### 3. RobertN1D XAUUSD Gold Scalper — inspectable 11-generator architecture

Repository:
https://github.com/RobertN1D/XAUUSD-GOLD-SCALPER-MT5-EA-FREE-SOURCE-CODE

This is the most useful reconstructible community source discovered in the earlier project work.

Its current source documents eleven entry generators:
1. SPIKE
2. FLAG
3. ORB
4. VWAP_RECLAIM
5. VWAP_REJECT
6. ABCD
7. LEVEL_BOUNCE
8. LEVEL_BREAK
9. EMA_PULLBACK
10. NEWS_CONT
11. FADE

Architecture:
- each generator creates one normalized setup proposal;
- proposals receive universal context scoring;
- strategy-specific recent-loss suspension can disable a generator;
- a central ranker chooses among proposals;
- global execution gates run only after ranking;
- once in a position, a separate every-tick AutoProtect / trailing lifecycle engine manages the trade.

This separation between proposal generation and post-entry lifecycle is more relevant to BETA064 than the literal number of strategies.

No profitability claim from this repository is accepted as evidence for BETA.

### 4. Japanese independent-strategy portfolio evidence

Japanese community source “Gorilla Blizzard” publicly describes three independent XAUUSD strategies inside one EA:
- early-morning pullback main engine;
- sudden-drop rebound hunter;
- short-term overheating/rebound sniper.

The source is black-box and its performance claims are not accepted. The useful architectural point is independent logic ownership rather than universal voting.

### 5. Chinese regime-separation evidence

A Chinese MQL5 XAUUSD researcher reported a validation PF that collapsed on untouched blind data and explicitly concluded that one parameter set should not be forced across trend expansion, liquidity sweeps, range mean reversion and news shocks.

This directly supports market-condition ownership by different specialists.

## BETA064-R1B architectural change

Do NOT simply increase five experts to twelve copies of the same learner.

Build two different specialist floors.

# FLOOR A — ENTRY SPECIALISTS

Each desk must own a different causal market mechanism and a defined timeframe hierarchy.

## E1 Macro Structural Trend
Timeframes: H4/H1/M15 → M5 trigger.

Purpose:
persistent higher-timeframe displacement / structural trend participation.

Features:
confirmed pivots, accepted breaks, trend efficiency, volatility-normalized displacement, HSMM regime duration.

## E2 Structural Pullback / Reacceleration
Timeframes: H1/M15 context → M5/M1 setup → S5/S1 reacceleration.

Purpose:
enter mature trend only after retrace and renewed drive.

## E3 Session Opening-Range Break
Timeframes: M15/M5 range construction → M1/S5 break/retest.

Purpose:
London/NY/other predeclared session transition and opening-range expansion.

## E4 VWAP Trend Pullback
Timeframes: H1/M15 trend → M5 VWAP location → M1/S5 rejection/reacceleration.

Purpose:
trend continuation from value.

## E5 VWAP Break / Reclaim
Timeframes: M15/M5 environment → M5/M1 reclaim → S5 execution.

Purpose:
early regime-direction transition around accepted value migration.

## E6 Statistical Value Reversion
Timeframes: M15/M5 rotational regime → M1/S5 extreme.

Purpose:
mean reversion from volatility-normalized VWAP/value excursion only in non-trending state.

## E7 Liquidity Sweep / Reclaim
Timeframes: M5/M1 structural level → S15/S5/S1 sweep → 250ms reclaim quality.

Purpose:
failed liquidity excursion and rejection.

## E8 Key-Level Bounce / Auction Rejection
Timeframes: H1/M15/M5 level ownership → M1/S5 rejection.

Purpose:
support/resistance/round/session/pivot rejection without requiring a classical sweep.

## E9 Key-Level Break / Acceptance
Timeframes: H1/M15/M5 level ownership → M1 body acceptance → S5/S1 continuation.

Purpose:
distinguish genuine structural migration from wick-only break.

## E10 Compression → Expansion
Timeframes: M5/M1 compression → S15/S5/S1 release → 250ms acceleration.

Purpose:
volatility-transition entry before mature trend confirmation.

## E11 Kinetic Ignition
Timeframes: S15/S5/S1/250ms.

Purpose:
tick velocity/acceleration/jerk, quote-intensity and efficiency ignition with cost-aware side value.

## E12 Failed Expansion / Contradiction
Timeframes: M1/S15/S5/S1/250ms.

Purpose:
attack breakouts where effort rises but displacement/renewal deteriorates and price falls back inside structure.

### Optional later event specialist

NEWS_CONT / macro-event shock continuation should remain separate and disabled until a reproducible historical economic-calendar feed is integrated into the Python harness. It should not be simulated from price alone.

# FLOOR B — HOLD SPECIALISTS

These specialists only become eligible after an actual fill. They do not decide initial direction.

Every hold expert receives:
- origin entry specialist and entry thesis;
- executable current P/L;
- MFE/MAE and their timing;
- hold age;
- return-to-entry count;
- favorable/adverse excursion speed;
- pullback depth;
- new-extreme renewal;
- spread and quote-staleness evolution;
- structural owner changes;
- HSMM/BOCPD state updates;
- cross-scale efficiency/velocity surface.

## H1 Ignition Confirmation
Question:
did the expected first impulse actually materialize after fill?

Primary ages:
250ms–3s.

## H2 Extension / Runner Persistence
Question:
is favorable displacement continuing with sufficient residual runway?

Primary ages:
1s–60s+, conditional on origin family.

## H3 Healthy Pullback Tolerance
Question:
is the adverse movement a normal pullback inside a still-valid trend/auction thesis?

Purpose:
avoid killing valid trades merely because they retrace.

## H4 Reacceleration
Question:
after pullback or stall, has directional drive resumed?

Purpose:
separate temporary weakness from renewed continuation.

## H5 Quick-Scalp / Transient Opportunity
Question:
did the entry produce a small favorable excursion but fail to acquire runner characteristics?

This specialist estimates continuation fragility; it does NOT implement a new exit policy in this phase.

## H6 Stall / Chop
Question:
has the trade entered high-turn, low-efficiency, low-renewal two-sided noise where remaining continuation value is decaying?

## H7 Failed Acceptance / Thesis Failure
Question:
has price recrossed the structural/value boundary that justified entry, with adverse state transition?

This expert produces catastrophe/thesis-failure probability.

## H8 Exhaustion / Climax
Question:
has extreme favorable velocity/extension become unsustainable, with declining renewal and rising reversal hazard?

Again this produces continuation-value information only in Entry→Hold phase.

# Shared HOLD value arbiter

Keep the BETA064 shared continuation-value concept, but change its inputs.

Instead of one monolithic continuation model trying to represent every trajectory directly:

`post-fill state → H1..H8 hold specialists → state-conditioned hold router → shared continuation-value arbiter`

Each HOLD expert outputs:
- P(favorable first passage before adverse failure);
- expected remaining executable value;
- continuation survival probability by age;
- tail/adverse value;
- uncertainty.

The shared arbiter estimates the single economic quantity:

`AdvantageHold = ExpectedRemainingExecutableValue - ExitNowExecutableValue`

Dedicated HOLD+EXIT policy optimization remains deferred. In this phase the hold floor is being trained to classify trajectory and continuation worthiness.

# Entry-to-Hold thesis packet

When ENTRY specialist Ek opens a position, attach a causal thesis packet:

- origin expert;
- expected market mechanism;
- expected useful horizon distribution;
- structural/value boundary that defines thesis validity;
- predicted first-passage profile;
- macro/meso/micro state at entry;
- uncertainty;
- cost state.

The HOLD floor evaluates whether the observed trade is behaving consistently with that thesis.

This avoids forcing a sweep-reclaim trade, an H4 trend trade and a 250ms ignition trade through identical hold expectations.

# Router topology

Do not make all 20 specialists vote together.

Use hierarchy:

1. MARKET STATE ROUTER
   - determines eligible Entry desks.

2. ENTRY REGRET ROUTER
   - ranks only eligible Entry specialists plus WAIT.

3. POSITION ORIGIN / THESIS
   - persists the selected entry mechanism after fill.

4. HOLD STATE ROUTER
   - routes among H1-H8 based on post-entry path.

5. SHARED CONTINUATION VALUE
   - common economic comparison layer.

This design preserves attribution and reconstructibility.

# Why this addresses BETA064-R1A

R1A found:
- insufficient gross directional edge in broad short-horizon models;
- instability across the Jan CAL→diagnostic transition;
- adding one generic micro-liquidity specialist and one generic macro specialist did not solve the problem;
- a hindsight expert oracle remained much stronger than deployable routing.

The two-floor architecture attacks three likely causes:
1. expert state definitions were too broad;
2. multiple distinct market mechanisms were compressed into five heads;
3. a single continuation model was asked to represent trajectory types with very different lifecycle geometry.

# Next empirical test order

1. Do not build all specialists simultaneously.
2. Construct common causal feature/state caches.
3. Run an ENTRY opportunity ceiling for E1–E12 using path-aware first-passage labels.
4. Eliminate desks with no unique/calibrated economic value.
5. Train the Entry regret router only on survivors.
6. For trades from surviving Entry desks, generate post-fill path states.
7. Test H1–H8 as independent continuation specialists.
8. Measure whether Hold-MoE reduces continuation-value regret versus the current single shared continuation model.
9. Freeze any passing architecture before Jan–Jul.
10. August remains SEALED.

# Promotion rules

No specialist is accepted because it exists in community code.

It must show:
- reconstructible logic;
- causal runtime features;
- unique or synergistic information;
- positive incremental executable value after spread/fees;
- stability across historical partitions;
- no dependence on future bars;
- adequate opportunity/winner retention;
- reproducible Python implementation;
- later MT5 parity only with explicit owner approval.

No official MQL5 code is authorized by this document.
