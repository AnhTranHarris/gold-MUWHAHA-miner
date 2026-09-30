# BETA064 CHECKPOINT 02E — Session-Aware Entry-Specialist Derivative Opportunity Research

**Date:** 2026-09-30  
**Branch:** beta  
**Parent control:** BETA064 Major Checkpoint 02 — immutable  
**Research parents:** Checkpoint-02C / Checkpoint-02D  
**Scope:** ENTRY→HOLD only  
**Hold→Exit:** deferred  
**Alpha/GAMMA:** dead / prohibited dependencies  
**August:** sealed and not read  
**Status:** DIAGNOSTIC RESEARCH COMPLETE — NO NEW MAJOR CHECKPOINT

## Research question

Can first-, second-, or third-order derivatives of an existing Entry specialist increase the number of Entry→Hold opportunities while preserving the preferred >=85% survivability requirement, especially when each derivative inherits the parent specialist's session context?

The term **derivative specialist** in this record means a causal state descendant of a parent trading thesis, not a mathematical price derivative.

- **D0 parent:** original specialist opportunity.
- **D1:** first causal continuation/retest/reclaim/turn after the parent state.
- **D2:** a second confirmation/stabilization/rebreak/reacceleration after D1.
- **D3:** a later handoff/re-entry state after the prior episode has substantially progressed or crossed a session/state boundary.

## Community cross-reference

Public, reconstructible mechanics strongly support staged entry logic, but not indefinite chaining.

Examples used as mechanical inspiration only:

1. TradingView open-source PA System: confirmed structure → pullback → H1/L1 → H2/L2 second entry through a micro-range breakout; optional BoS/CHoCH and liquidity-sweep context.
   https://www.tradingview.com/script/tJCbhCA5-PA-System/

2. MQL5 Opening Range Breakout article (Chinese/Japanese/English variants): explicit state machine for **break → retest → rebreak**, with session reset and delayed confirmation.
   https://www.mql5.com/zh/articles/18486

3. MQL5 adaptive breakout/retest article: retest confirmation is used to reduce premature entries and weak breakouts.
   https://www.mql5.com/ja/articles/21443

4. TradingView open-source Sweep Reclaim Retest: bias → level → sweep → reclaim → retest → signal, with expiry/invalidation and session windows.
   https://www.tradingview.com/script/pqn79edL-Sweep-Reclaim-Retest-Clean-v1/

5. TradingView open-source Liquidity Sweep + OB Retest: sweep → CHoCH → order block → retest → reaction.
   https://www.tradingview.com/script/5qXfyxql-ICT-Setup-05-TradingFinder-Liquidity-Sweep-OB-Retest/

6. MQL5 liquidity-sweep implementations distinguish sweep/reclaim from true breakout and use closed-bar or confirmed swing logic.
   https://www.mql5.com/en/articles/20569
   https://www.mql5.com/en/code/76586

7. Chinese community material explicitly describes second-entry logic after volatility/emotional expansion cools and emphasizes session filtering for gold.
   https://www.fxear.com/zh/blog/article.php?slug=260907-784-xauusd-ea

8. Japanese re-entry commentary emphasizes that a re-entry must be evaluated as a **new scene with a new reaction and invalidation**, not merely a continuation of the previous trade.
   https://ameblo.jp/fx-gold-com/entry-12975214715.html

9. Arabic gold material commonly distinguishes London/NY timing and breakout/retest re-entry, reinforcing session-aware rather than universal re-entry handling.
   https://www.tmgm.com/ar/academy/trading-academy/gold-breakout-retest-strategy
   https://fxnx.com/ar/blog/%D8%A5%D8%AA%D9%82%D8%A7%D9%86-%D8%AA%D8%A3%D8%B1%D8%AC%D8%AD-%D9%8A%D9%87%D9%88%D8%B0%D8%A7-ict-%D9%81%D9%8A-%D8%A7%D9%84%D8%B0%D9%87%D8%A8-%D8%AA%D8%AF%D8%A7%D9%88%D9%84-%D9%81%D8%AE-%D9%84%D9%86%D8%AF%D9%86

Community performance claims were not accepted as evidence. Only reconstructible mechanics were tested.

## Derivative families tested

### D1 — first-order descendants

Parent families:
- E5 VWAP Reclaim → E5D1 Session-VWAP Reclaim Retest
- E6 Value Reversion → E6D1 Session-Value Turn
- E7 Sweep/Reclaim → E7D1 Pre-open Sweep/Reclaim
- E9 Level Break → E9D1 Break-Accept-Retest

Jan–Jul raw result:

| D1 specialist | Candidates | Survivability | FP success |
|---|---:|---:|---:|
| E6D1 Session Value Turn | 150,063 | 23.87% | 12.95% |
| E9D1 Break Accept Retest | 14,476 | 15.92% | 12.43% |
| E5D1 SVWAP Reclaim Retest | 11,274 | 21.64% | 11.79% |
| E7D1 Pre-open Sweep Reclaim | 4,913 | 20.86% | 11.85% |
| **All D1** | **180,726** | **23.01%** | **12.81%** |

D1 greatly expands the opportunity search surface but is far below the 85% survivability authority.

Leave-one-month-out high-tail selection also failed to create stable >=85% standalone opportunities.

### D2 — second-order descendants

D2 adds another causal state transition:

- E6D2 Sustained Extreme Reversal
- E7D2 Sweep/Reclaim Stabilize
- E9D2 Expansion Break Retest
- E5D2 Trend SVWAP Retest

Jan–Jul raw result:

| D2 specialist | Candidates | Survivability | FP success |
|---|---:|---:|---:|
| E6D2 Sustained Extreme Reversal | 12,955 | 56.02% | 29.13% |
| E7D2 Sweep/Reclaim Stabilize | 748 | 51.20% | 24.47% |
| E5D2 Trend SVWAP Retest | 410 | 50.24% | 24.63% |
| E9D2 Expansion Break Retest | 401 | 39.40% | 26.93% |
| **All D2** | **14,514** | **55.15%** | **28.70%** |

This is the strongest derivative finding.

**Second-order confirmation approximately doubles raw survivability relative to D1**, especially for E6/E7/E5.

However, it still does not reach the preferred 85% survivability requirement as an independent Entry desk.

Best sizeable raw session cells include:
- E7D2 Europe ~67.1%
- E6D2 Australia ~63.5%
- E6D2 Asia ~62.6%
- E5D2 Australia ~62.7%
- E5D2 Europe ~61.4%
- E6D2 Middle East ~60.0%
- E6D2 UK ~57.8%
- E6D2 NY ~53.6%

These are useful state descriptors but not executable desks.

### D3 — third-order / session-handoff descendants

Later handoff variants were tested:

- E7D3 Handoff Sweep/Reclaim
- E9D3 Handoff Break-Accept-Retest
- E5D3 Handoff VWAP Reclaim

Jan–Jul raw result:

| D3 specialist | Candidates | Survivability | FP success |
|---|---:|---:|---:|
| E5D3 Handoff VWAP Reclaim | 409 | 40.83% | 21.52% |
| E7D3 Handoff Sweep/Reclaim | 1,759 | 31.32% | 17.34% |
| E9D3 Handoff Break Accept Retest | 470 | 30.64% | 22.34% |
| **All D3** | **2,638** | **32.68%** | **18.88%** |

D3 degrades materially from D2.

The later handoff tends to arrive after the original edge has decayed or after the thesis has changed enough that it should be treated as a new parent episode.

## Session-aware derivative model tests

Session-specific classifiers and rule searches were run for the D2 families.

They did not produce a stable, sizeable >=85% held-out tail.

Examples:
- UK E6D2 could isolate a few additions in some held-out months, but held-out add survivability frequently fell to 50–75%.
- NY E6D2 produced occasional high-quality singletons but no stable broad tail.
- E7D2 NY generated one strong held-out addition in one month, not a reproducible opportunity family.
- Other sessions either produced no eligible tail or too few observations.

A portfolio-level LOMO derivative insertion test produced **51 total held-out derivative additions** with only **68.63% weighted add survivability** and approximately **-$37.7** diagnostic value. The overall parent portfolio remained ~88.4% survivable only because the existing frozen/child trades provided a large quality buffer.

That is not acceptable evidence for promoting derivative entries.

A coverage-utility variant became even more conservative:
- only 7 derivative additions;
- ~71.4% add survivability;
- still insufficient.

## Numeric derivative-feature test

A separate leave-one-month-out classifier compared:

- parent/base state descriptors only;
- parent/base state plus derivative/change descriptors.

Average held-out AUC:
- base: **0.6005**
- derivative-enriched: **0.6116**
- improvement: **+0.0111 AUC**

Derivative state information is therefore **modestly informative**, but not enough to isolate a production-quality >=85% opportunity tail by itself.

## Quant conclusion

### Answer to the owner's proposal

**Yes, second-order derivatives are useful.**
But the evidence says they should currently be treated as:

- router features;
- parent-thesis state transitions;
- opportunity ranking metadata;
- shadow/probationary candidate clocks;

rather than new executable Entry specialists.

**Third-order derivatives do not help at this stage.**
The D3 handoff layer loses quality relative to D2 and increases semantic drift from the original thesis.

### Frozen derivative-depth policy for continued BETA research

1. Maximum derivative depth for active research: **D2**.
2. D1/D2 always inherit:
   - parent specialist id;
   - parent thesis boundary;
   - side;
   - session authority;
   - episode id;
   - state age.
3. A derivative is not a retry. It must have:
   - a new causal state transition;
   - a new timestamp;
   - a new observable confirmation;
   - an explicit invalidation.
4. Cross-session D3 handoff is not automatically inherited. A materially new session/state is treated as a **new parent episode**.
5. No derivative can own a position unless its own session×parent family eventually proves >=85% standalone LOMO survivability with adequate sample support.
6. Portfolio-level survivability may not be used to hide a low-quality derivative add stream.
7. Coverage utility may rank qualified candidates, but may never override the survivability gate.
8. E11 remains saturated and should not receive derivative expansion priority.
9. Highest derivative research priority remains E6, then E7/E9, because those are the largest condition-matched deficits.
10. Hold→Exit remains deferred.
11. August remains sealed.

## Recommended next architecture — Derivative State Router

Do not create E17–E40 by mechanically multiplying every specialist by every derivative state.

Instead add a single **Derivative State Router (DSR)** layer:

`parent specialist thesis`
→ `episode state D0 / D1 / D2`
→ `session-conditioned derivative descriptors`
→ `survivability authority`
→ `coverage/novelty utility`
→ `WAIT or candidate`

Minimum episode metadata:
- parent_specialist
- parent_episode_id
- derivative_order
- derivative_state
- parent_session
- current_session
- episode_age
- parent_thesis_valid
- parent_invalidation_distance
- first_retest_age
- number_of_retests
- acceptance/reclaim count
- excursion efficiency
- spread/ATR trajectory
- quote-activity trajectory
- session age
- cross-scale ownership
- novelty vs already selected opportunity cells

Recommended DSR research gate:
- standalone derivative session×parent survivability >=85% in leave-one-month-out validation;
- minimum sample requirement before executable probation;
- no more than one D1 and one D2 opportunity per parent episode;
- D3 causes episode reset instead of further chaining.

## Next bounded unit

**BETA064_CHECKPOINT_02F_DERIVATIVE_STATE_ROUTER_E6_E7_E9_SESSION_DISCRIMINATION**

Objectives:
1. encode D0/D1/D2 as parent-state transitions rather than separate strategy proliferation;
2. use D2 descriptors to improve E6/E7/E9 discrimination;
3. explicitly optimize for under-covered session×specialist cells only after the 85% survivability gate;
4. compare base-only vs derivative-enriched models out of month;
5. retain E13 as shadow only;
6. no MQL5 change;
7. no Hold→Exit;
8. no August.

## Durable local result artifacts used

- BETA064_CKPT02E_LOMO_E5D1_SVWAP_RECLAIM_RETEST.csv
- BETA064_CKPT02E_LOMO_E6D1_SESSION_VALUE_TURN.csv
- BETA064_CKPT02E_LOMO_E7D1_PREOPEN_SWEEP_RECLAIM.csv
- BETA064_CKPT02E_LOMO_E9D1_BREAK_ACCEPT_RETEST.csv
- BETA064_CKPT02E_V2_LOMO_E5D2_TREND_SVWAP_RETEST.csv
- BETA064_CKPT02E_V2_LOMO_E6D2_SUSTAINED_EXTREME_REVERSAL.csv
- BETA064_CKPT02E_V2_LOMO_E7D2_SWEEP_RECLAIM_STABILIZE.csv
- BETA064_CKPT02E_V2_LOMO_E9D2_EXPANSION_BREAK_RETEST.csv
- BETA064_CKPT02E_SESSION_DERIVATIVE_ML_LOMO.csv
- BETA064_CKPT02E_PORTFOLIO_LOMO_DERIVATIVES.csv
- BETA064_CKPT02E_COVERAGE_UTILITY_LOMO_DERIVATIVES.csv
- BETA064_CKPT02F_BASE_VS_DERIVATIVE_LOMO_BASE.csv
- BETA064_CKPT02F_BASE_VS_DERIVATIVE_LOMO_DERIV.csv

Major Checkpoint 02 remains immutable.
