# BETA064 CHECKPOINT 02G — Session-Aware Derivative-State Opportunity Research

**Date:** 2026-09-30  
**Branch:** `beta`  
**Frozen control:** BETA064 Major Checkpoint 02 — unchanged  
**Research lineage:** C02B → C02C → C02D → C02G  
**Scope:** ENTRY→HOLD only  
**HOLD→EXIT:** deferred  
**Alpha/GAMMA:** dead / prohibited dependencies / not used  
**August:** sealed and not read  
**Status:** DIAGNOSTIC + REFINEMENT RESULT — NOT A NEW MAJOR CHECKPOINT

## Research question

Can second- or third-order derivatives of the causal Entry-specialist state expose additional XAUUSD Entry→Hold opportunities while preserving the preferred >=85% survivability target, especially when derivative order is made session-aware like its parent specialist?

## Short answer

**Yes, derivative state adds real discriminatory information, but not enough to act as a standalone Entry specialist or broad gate.**

The strongest use is:

`parent specialist proposal → session authority → same-timestamp derivative-state packet → survival/coverage router`

The derivative layer should **not** wait after the parent signal for confirmation. A causal delayed-confirmation experiment reduced Entry→Hold survival in every observed month.

## Causal derivative definitions

For any causal completed state series `x_t`:

`D1_5S(x,t) = x_t - x_(t-1)`

`D2_5S(x,t) = D1_5S(x,t) - D1_5S(x,t-1)`

`D3_5S(x,t) = D2_5S(x,t) - D2_5S(x,t-1)`

The micro packet uses the same definitions on completed 1-second states.

Interpretation:
- D1 = slope / velocity / state change
- D2 = acceleration / change in slope
- D3 = curvature / jerk / change in acceleration

No derivative may use the currently forming future bucket. The completed 5-second observability contract from Major Checkpoint 02 still controls: [t,t+5s) becomes observable only at t+5s.

Derivative families studied include causal changes in:
- price displacement / short-horizon return state;
- path efficiency;
- spread / friction state;
- quote activity / tick intensity;
- quote pressure;
- quote-volume imbalance proxy;
- value/VWAP displacement;
- related parent-specialist state variables.

## Raw tick reconstruction

Completed 1-second micro derivatives were rebuilt by streaming every available Dukascopy quote in chronological order rather than loading whole months into memory.

Quote rows consumed:
- Jan: 9,135,063
- Feb: 7,538,340
- Mar: 9,433,180
- Apr: 7,470,571
- May: 8,333,166
- Jun: 8,201,407
- Jul: 7,415,842

August was not opened.

## Global derivative-order leave-one-month-out result

The derivative-order comparison used 14,514 C02E-v2 parent-derived candidate opportunities.

Mean held-out discrimination:

| Feature order | Mean AUC | Weighted held-out survival of selected tail |
|---|---:|---:|
| BASE | 0.598637 | 67.79% |
| **D1 5s** | **0.608021** | 67.95% |
| D2 5s | 0.604455 | **68.55%** |
| D3 5s | 0.603413 | 68.02% |
| D3 + 1s micro | 0.607413 | 67.84% |

Interpretation:
- D1 gives the strongest overall discrimination gain.
- D2 gives the highest weighted survival among the tested selected tails.
- neither order creates a robust >=85% standalone opportunity population.
- 1-second micro derivatives add computation but do not improve the global result enough to justify universal deployment.

Therefore derivative state is useful **inside** a parent specialist/router, not as an independent broad Entry clock.

Exact result table:
`research/results/BETA_064_C02G_DERIVATIVE_ORDER_LOMO.csv`

## Session-conditioned E6 result

Derivative order is strongly session-dependent.

Mean leave-one-month-out AUC by session:

| Session | BASE | D1 5s | D2 5s | D3 5s | D3 + 1s micro | Research authority |
|---|---:|---:|---:|---:|---:|---|
| Australia | 0.3371 | 0.5006 | 0.5197 | **0.5789** | 0.5593 | **D3 5s** |
| Asia | 0.4376 | 0.5129 | **0.6874** | 0.6624 | 0.6313 | **D2 5s** |
| Middle East | 0.4883 | 0.5366 | 0.5353 | 0.5411 | **0.5555** | **D3 + 1s micro** |
| Europe | **0.5581** | 0.5313 | 0.5328 | 0.5266 | 0.5273 | **NONE / parent state** |
| UK | 0.6044 | **0.6147** | 0.6030 | 0.6103 | 0.6063 | **D1 5s** |
| New York | 0.5732 | 0.5821 | 0.5804 | 0.5788 | **0.5843** | **D3 + 1s micro** |

This is the strongest C02G conclusion:

**Derivative order must inherit session context. There is no defensible universal second- or third-order derivative setting.**

Proposed research-only Derivative Authority Matrix:
- AUSTRALIA → D3_5S
- ASIA → D2_5S
- MIDEAST → D3_PLUS_1S_MICRO
- EUROPE → NONE / static parent state
- UK → D1_5S
- NY → D3_PLUS_1S_MICRO

Exact result table:
`research/results/BETA_064_C02G_SESSION_E6_DERIVATIVE_ORDER_LOMO.csv`

## Delayed derivative-confirmation experiment — REJECTED

A causal timing experiment allowed up to eight seconds after a parent-derived proposal for a session-appropriate derivative confirmation, then entered at the first observed confirmation second.

This reduced survival in every observed month:

| Month | Confirmed / parent candidates | Survival before wait | Survival after derivative wait |
|---|---:|---:|---:|
| Jan | 1,516 / 1,689 | 56.07% | **51.91%** |
| Feb | 1,581 / 1,787 | 55.85% | **52.88%** |
| Mar | 4,953 / 5,541 | 58.91% | **56.35%** |
| Apr | 1,234 / 1,437 | 60.13% | **59.00%** |
| May | 1,640 / 1,827 | 58.23% | **55.73%** |
| Jun | 1,416 / 1,596 | 57.63% | **54.38%** |
| Jul | 578 / 637 | 56.23% | **53.29%** |

Typical delay was roughly 2.5–2.7 seconds.

**Decision:** derivative state must be observed at the parent proposal timestamp (or as completed pre-entry state), not used as a delayed confirmation trigger.

## Earlier derivative-child families cross-checked

The following parent descendants were also explored before C02G:
- E6D1 Session Value Turn
- E7D1 Pre-open Sweep/Reclaim
- E9D1 Break→Accept→Retest
- E5D1 Session VWAP Reclaim→Retest
- E6D2 Sustained Extreme Reversal
- E7D2 Sweep/Reclaim Stabilize
- E9D2 Expansion Break Retest
- E5D2 Trend Session-VWAP Retest

Representative raw D2 survivability:
- E5D2 ~50.24%
- E6D2 ~56.02%
- E7D2 ~51.20%
- E9D2 ~39.40%

No stable standalone >=85% derivative child was identified.

These results reinforce the same conclusion: derivatives are **state discrimination**, not an independent alpha source.

## Community-source cross-reference

Only reconstructible mechanics were accepted. Community/vendor performance claims were not used as evidence.

### English / MetaQuotes / MQL5

1. Price velocity measurement methods  
https://www.mql5.com/en/articles/6947  
Reconstructible: price velocity as displacement/time or displacement/tick count; lower-timeframe decomposition reveals dynamics hidden in a larger bar.

2. Accelerator Oscillator  
https://www.mql5.com/en/articles/16781  
Reconstructible: acceleration is distinct from velocity and can describe momentum speeding/slowing.

3. Trading Insights Through Volume: Moving Beyond OHLC Charts  
https://www.mql5.com/en/articles/16445  
Reconstructible: first derivative of volume/activity and second derivative/acceleration as participation state.

4. Market Microstructure Execution Noise Filtering  
https://www.mql5.com/en/articles/22772  
Reconstructible: tick velocity, quote gaps and short-term execution-quality state can be measured causally.

5. Triple Derivative Engine  
https://www.tradingview.com/script/sic4VGf6-Triple-Derivative-Engine/  
Reconstructible: velocity → acceleration → jerk; higher derivatives lead but become noisier, and should be combined with structural context rather than used as a single-cross system.

### Chinese-language / TradingView

6. Liquidity Sweep Mean Reversion XAUUSD/XAGUSD  
https://cn.tradingview.com/script/fVu5DNuk/  
Reconstructible: session filter, session-anchored VWAP/value, sweep + structure confirmation.

7. Session Sweep System  
https://cn.tradingview.com/script/RY1SZR8x-Session-Sweep-System-WarRoomXYZ-V1/  
Reconstructible: Asia/London/NY ranges, sweep detection, timing, expansion and trend alignment.

8. AMT Order Flow Suite  
https://cn.tradingview.com/script/A4jmkFCw-AMT-Order-Flow-Suite-v2-2/  
Reconstructible: XAUUSD session value/VWAP, activity/absorption, CVD-style pressure proxy, session-aware failed auction context.

9. Chinese TradingView VWAP/session profile catalog  
https://cn.tradingview.com/scripts/vwaps/  
Reconstructible: treat global sessions as separate auctions with independently resetting value/VWAP and DST-aware time controls.

### Japanese-language / TradingView

10. Session tools  
https://jp.tradingview.com/scripts/session/  
Reconstructible: session-specific anchors and exchange/session boundary handling.

11. XAUUSD tools  
https://jp.tradingview.com/scripts/xauusd/  
Reconstructible examples combine confirmed swing structure, anchored VWAP/value and volatility/chop filters.

12. VWAP/session tools  
https://jp.tradingview.com/scripts/vwapstrategy/  
Reconstructible: Sydney/Tokyo/London/New York session-aware VWAP/value anchors.

### Korean-language / TradingView

13. XAUUSD tools  
https://kr.tradingview.com/scripts/xauusd/  
Reconstructible examples use London/New York gates, VWAP positioning, volatility exhaustion and multi-factor admission rather than an undifferentiated 24-hour rule.

14. VWAP tools  
https://kr.tradingview.com/scripts/vwap/  
Reconstructible: anchored fair-value references and structural/volatility context.

## What the community cross-reference supports

Across languages, the recurring reconstructible pattern is:
- derivative/momentum state is contextual;
- session boundaries matter;
- value/VWAP anchors reset by session or structural leg;
- sweeps/absorption/divergence require structure and timing;
- increasing derivative order increases sensitivity/noise;
- no credible reconstructible source justifies using jerk/acceleration alone as an entry system.

This is consistent with C02G.

## Research architecture after C02G

Recommended next research child:

`BETA064_CHECKPOINT_02H_SESSION_DERIVATIVE_STATE_ROUTER_AND_OPPORTUNITY_BUS`

Flow:

`parent Entry proposal`
→ `session authority`
→ `Derivative State Packet`
→ `frozen/base survival authority`
→ `coverage-deficit + novelty utility`
→ `one-position ownership`
→ `H1–H8 Hold floor`

Derivative State Packet fields should include:
- selected session derivative order;
- D1 velocity/state slope;
- D2 acceleration;
- D3 curvature/jerk;
- activity/tick-intensity derivative;
- spread/friction derivative;
- quote-pressure derivative;
- value-displacement derivative;
- micro 1s packet only where session authority warrants it;
- parent specialist id and thesis.

## Specialist descendants for next unit

Use derivative descendants as **children of the parent**, not new independent desks:

- Australia E6.D3
- Asia E6.D2
- Middle East E6.D3μ
- Europe E6 parent-only
- UK E6.D1
- NY E6.D3μ

For E7/E9/E5:
- keep derivative features in shadow/admission research;
- no execution authority yet because existing D1/D2 populations remain well below 85%.

E11 remains saturated and should not be expanded.

E13 Absorption-Divergence remains probationary shadow/gap-fill only.

E14–E16 remain shadow-only.

## Reproducibility gap created by runtime reset

The exact C02G result CSVs survived and are now durable.

Some transient Python training scripts used during derivative experimentation did **not** survive a runtime reset before they were durably committed.

This must be treated as a reproducibility gap, not reconstructed from memory and silently labeled exact.

The durable reconstruction specification is:
`research/experiments/BETA_064_C02G_DERIVATIVE_STATE_SPEC.py`

A future rerun must:
1. start from frozen Major Checkpoint 02 / C02C candidate sources;
2. implement the formulas in the derivative-state spec;
3. reproduce the two committed C02G CSV tables within deterministic tolerance;
4. only then extend the derivative router.

## Quant decision

- User's second/third-order derivative idea is **validated as useful context**.
- It is **not validated as a standalone opportunity generator**.
- Session-aware derivative order materially outperforms one universal derivative order.
- Europe currently rejects derivative complexity.
- Post-signal derivative waiting is rejected.
- No derivative child is promoted into Major Checkpoint 02.
- Major Checkpoint 02 remains frozen.
- HOLD→EXIT remains deferred.
- August remains sealed.
- Alpha/GAMMA remain prohibited.

## Next bounded unit

**BETA064 CHECKPOINT 02H — Session Derivative-State Router + Coverage-Weighted Opportunity Bus**

Primary research targets:
1. apply the Derivative Authority Matrix at parent proposal time;
2. use coverage-deficit weighting to favor under-covered E6/E7/E9/E5 states;
3. preserve >=85% month-level Entry→Hold survivability;
4. measure condition-matched SYNTH coverage, not raw trade count;
5. keep E11 novelty penalty high because it is already saturated;
6. continue E13 shadow evidence;
7. no HOLD→EXIT until Entry→Hold coverage is sufficient.
