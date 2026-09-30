# BETA064 CHECKPOINT 02E — Session-Aware Entry-Specialist Derivative Opportunity Research

**Date:** 2026-09-30  
**Branch:** `beta`  
**Frozen control:** BETA064 Major Checkpoint 02 — immutable  
**Best executable research child before this unit:** Checkpoint-02D  
**Scope:** ENTRY→HOLD opportunity discovery only  
**Hold→Exit:** deferred  
**Alpha/GAMMA:** PROHIBITED / NOT USED  
**August:** SEALED / NOT READ  
**Status:** SHADOW-OPPORTUNITY RESEARCH — NO EXECUTABLE PROMOTION

## Research question

Can derivatives of existing Entry specialists, made explicitly session-aware, create materially more Entry→Hold opportunities while preserving the preferred >=85% survivability standard?

The derivative architecture was deliberately constrained:

- a derivative must keep the economic thesis of its parent;
- it may change the causal entry clock and session context;
- it begins as a shadow desk with zero position ownership;
- it must prove portable Entry→Hold survivability before admission;
- it may not replace or mutate the frozen Major Checkpoint 02 parent.

## Public/reconstructible mechanics used as hypothesis sources

Only mechanics were borrowed, never community performance claims.

Open-source/session-aware material repeatedly exposes:
- completed session highs/lows as causal liquidity references;
- wick/level sweep followed by close-back/reclaim;
- session-dependent Asia/London/New York treatment;
- sweep followed by displacement / market-structure confirmation;
- session VWAP/equilibrium as a separate value anchor;
- compression/expansion and execution-friction filters.

Those ideas were independently rebuilt and tested on Dukascopy XAUUSD ticks.

## D1 derivative clocks

Four first-generation derivative clocks were built:

### E6-D1 — Session Value Turn
Parent thesis: E6 Value Reversion.

New clock:
- session value excursion;
- prior movement away from value;
- causal micro turn back toward session value.

### E7-D1 — Pre-open Sweep/Reclaim
Parent thesis: E7 Liquidity Sweep/Reclaim.

New clock:
- sweep a locked session pre-open range;
- close/reclaim back through the boundary.

### E9-D1 — Break→Accept→Retest
Parent thesis: E9 Level Break.

New clock:
- break a session boundary;
- require multiple completed outside observations;
- enter the first causal successful retest.

### E5-D1 — Session-VWAP Reclaim→Retest
Parent thesis: E5 VWAP Reclaim.

New clock:
- cross/reclaim evolving session value;
- require a causal retest before proposal.

D1 produced a very large opportunity surface, but raw survivability was low:
- E6-D1: roughly 23–27%;
- E5-D1: roughly 17–24%;
- E7-D1: roughly 17–25%;
- E9-D1: roughly 13–17%.

Therefore D1 is useful only as an opportunity generator.

## D1 admission tests — rejected for execution

Three increasingly strict admission methods were tested.

### Jan-only learned admission

No derivative earned a January calibration gate requiring >=87% survivability plus positive diagnostics.

Approximate January calibration AUC:
- E6-D1 ~0.72;
- E5-D1 ~0.61;
- E9-D1 ~0.59;
- E7-D1 ~0.50.

### Frozen-parent model admission

Derivative clocks were mapped back through the exact frozen parent Entry model.

Result:
almost every derivative proposal was out-of-support for the frozen parent timing distribution.

At even a relaxed parent gate around P_survive 0.80 / score 0.20:
- E6-D1 produced only ~193 proposals at ~53% survival;
- E5-D1 produced essentially one;
- E7/E9 produced effectively none.

The actual frozen 0.88 / 0.30 gates admit practically none.

Interpretation:
the derivative clocks are genuinely novel timing states, not merely rediscovered parent entries.

### Leave-one-month-out learned-tail test

Exploratory full-panel fitting showed apparently excellent top tails, but the signal failed out-of-month.

Held-out results:
- E7-D1: ~256 held-out proposals / ~53.5% weighted survival / 0 of 7 months >=85%;
- E5-D1: ~363 / ~53.7% / 0 of 7;
- E9-D1: ~261 / ~44.4% / 0 of 7;
- E6-D1: ~204 / ~79.9% / only 2 of 7 >=85%.

This invalidates the attractive in-panel top-tail figures as non-portable.

## D2 — tighten the causal clock before using ML

Rather than ask a classifier to rescue a poor clock, the clock definitions themselves were tightened.

### E6-D2 — Sustained Extreme Reversal

Requirements included:
- persistent value extreme across completed 5-second states;
- low spread/ATR friction;
- avoid persistent 15-minute trend ownership;
- current body / r15 turn toward value;
- minimum short-horizon efficiency;
- no accelerating adverse knife-catch state.

Jan–Jul:
- 12,955 proposals;
- **56.02% raw survivability**;
- ~29.1% favorable-first-passage.

Session raw survival:
- Australia ~63.5%;
- Asia ~62.6%;
- Middle East ~60.0%;
- UK ~57.8%;
- Europe ~57.1%;
- New York ~53.6%.

### E7-D2 — Sweep/Reclaim/Stabilize

Requirements included:
- sweep/reclaim of locked pre-open or ORB boundary;
- wait 5–20 seconds for stabilization;
- directional body/r15 confirmation;
- low friction;
- minimum efficiency and level clearance.

Jan–Jul:
- 748 proposals;
- **51.20% raw survivability**;
- ~24.5% favorable-first-passage.

Best session:
- Europe ~67.1%.

### E5-D2 — Trend Session-VWAP Retest

Requirements included:
- session VWAP cross in direction of r900 trend;
- causal retest after the cross;
- body/r15/r60 trend alignment;
- low friction;
- minimum efficiency.

Jan–Jul:
- 410 proposals;
- **50.24% raw survivability**;
- ~24.6% favorable-first-passage.

Best sessions:
- Australia ~62.7%;
- Europe ~61.4%.

### E9-D2 — Expansion Break/Retest

Requirements included:
- quality expansion break;
- minimum volatility/range expansion;
- multiple outside closes;
- shallow retest;
- r15/r60/r300 alignment;
- low friction and overextension control.

Jan–Jul:
- 401 proposals;
- **39.40% raw survivability**;
- ~26.9% favorable-first-passage.

Best session:
- Europe ~52.2%.

## D2 global leave-one-month-out admission — rejected

Even after the raw-clock improvement, learned high-quality tails did not travel month-to-month.

Held-out:
- E6-D2: ~502 proposals / **72.5%** weighted survival / 0 of 7 >=85%;
- E7-D2: ~71 / **60.6%** / 0 of 7;
- E5-D2: ~37 / **59.5%** / only tiny 2 of 7 passing samples;
- E9-D2: ~41 / **43.9%** / 0 of 7.

## Dedicated session-model test

The owner's hypothesis was tested directly: give the same E6-D2 mechanism a separate admission model for each session.

Held-out weighted E6-D2 survivability remained roughly:
- Asia ~56.7%;
- Australia ~60.0%;
- Middle East ~63.8%;
- Europe ~61.0%;
- New York ~64.5%;
- UK ~67.8%.

No session produced a robust >=85% portable tail.

### Key conclusion

**Session awareness helps the opportunity clock materially, but is not sufficient by itself to turn a new derivative into an executable >=85%-survivability specialist.**

This is a positive architectural result:
- derivatives can broaden the search surface;
- they should remain shadow proposals until portable quality emerges;
- execution authority should stay with already-validated parent families.

## E13 session-derivative follow-up

The already-promising E13 Absorption-Divergence shadow desk was also split by session using simple reconstructible rules.

Leave-one-month-out weighted results:
- Asia: ~90.5%, but only 5/7 active held-out months pass and sample is tiny;
- Middle East: ~85.7%, 5/7 pass;
- Australia: ~83.3%;
- New York: ~73.9%;
- Europe: ~64.7%;
- UK: ~62.5%.

This is not enough for execution promotion.

However, Asia and Middle East E13 variants remain worth continued shadow evidence accumulation because their session-conditioned distributions are materially better than the other regions.

## Architecture decision

Derivatives are retained as a **Shadow Opportunity Bus**, not as executable BETA desks.

The bus should record for every proposal:
- parent specialist;
- derivative id;
- session authority;
- side and causal timestamp;
- causal feature/state packet;
- horizon/checkpoint;
- overlap with existing frozen/probationary proposals;
- offline survival/favorable-first-passage labels;
- condition-deficit cell;
- novelty relative to existing E1–E16 proposals.

No derivative may own a position yet.

## Opportunity implication

The experiment answers an important distinction:

More opportunity clocks are easy to create.

More **portable >=85% Entry→Hold opportunities** are not.

The next safest expansion path is therefore not to add progressively looser clocks. It is to mine new session/state substates from the already-proven or near-proven families:

1. E6 Value Reversion;
2. E7 Sweep/Reclaim;
3. E9 Accepted Level Break;
4. E13 Absorption-Divergence shadow evidence.

The next router should prioritize opportunity value, not raw signal count:

`coverage_utility = P_survive × deficit_weight × novelty_weight × execution_feasibility`

Where:
- `deficit_weight` rewards under-covered SYNTH session×specialist cells;
- `novelty_weight` penalizes duplicate/saturated states such as E11-like ignition;
- `execution_feasibility` penalizes friction and ownership conflict.

This utility is research-only until validated.

## Quant decision

- Major Checkpoint 02 remains frozen.
- Checkpoint-02D remains the current executable research child / candidate.
- D1 and D2 Entry derivatives remain shadow-only.
- E13 session variants remain shadow-only.
- No derivative has earned independent position ownership.
- No threshold may be lowered merely to increase signal count.
- Alpha/GAMMA remain prohibited.
- Hold→Exit remains deferred.
- August remains sealed.
- No MQL5 change.

## Next bounded unit

**BETA064 CHECKPOINT 02F — Exact Parent Candidate-Universe Rebuild + Coverage-Utility Routing for E6/E7/E9**

Goal:
recover additional opportunities from causal states adjacent to already-validated parent specialists rather than proliferating weak new clocks.

Required tests:
- reconstruct rejected/unused candidate universe for E6/E7/E9;
- identify session-specific causal substates with portable survivability;
- preserve frozen Major Checkpoint-02 ownership first;
- rank idle opportunities by coverage utility;
- validate month-by-month and leave-one-month-out;
- require >=85% survivability in every accepted validation slice before any new executable-child promotion.
