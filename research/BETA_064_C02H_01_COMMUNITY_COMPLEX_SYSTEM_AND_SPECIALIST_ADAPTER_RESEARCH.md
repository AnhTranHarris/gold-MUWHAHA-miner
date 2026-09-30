# BETA064 C02H-01 — Community Complex-System Search + Specialist Adapter Research

**Date:** 2026-09-30  
**Branch:** beta  
**Parent control:** BETA064 Major Checkpoint 02 — immutable  
**Research parent:** C02C/C02G opportunity-expansion line  
**Scope:** Entry→Hold only  
**Hold→Exit:** deferred  
**August:** SEALED and not read  
**Alpha/GAMMA:** prohibited and not used  
**MQL5:** no authorization / no change  
**Status:** RESEARCH CHILD — NO CHECKPOINT PROMOTION

## Objective

Continue the user's requested repeated research/refinement/repair program for the twelve Entry→Hold specialists, and search reconstructible community systems for mechanisms that might bridge missing opportunity coverage without weakening the preferred >=85% monthly Entry→Hold survival requirement.

The search explicitly included Fibonacci pullback systems, Heikin-Ashi state systems, Ichimoku equilibrium/cloud logic, Bollinger/Keltner squeeze-release systems, second-entry pullback logic, Kalman state-space filters, CUSUM/BOCPD-style structural-change detection, and entropy/regime concepts.

Community performance claims were treated as hypotheses only. Only reconstructible causal mechanics were tested.

## Public reconstructible research basis

Examples inspected during this unit:

- MetaQuotes Fibonacci Retracement Trading with Custom Levels: https://www.mql5.com/en/articles/20221
- MetaQuotes Kumo Breakout / Ichimoku + AO: https://www.mql5.com/en/articles/16657
- MetaQuotes Heikin-Ashi signal EA: https://www.mql5.com/en/articles/17021
- MetaQuotes professional Heikin-Ashi system: https://www.mql5.com/en/articles/18810
- MetaQuotes Bollinger-on-Keltner architecture: https://www.mql5.com/en/articles/13861
- MetaQuotes BOCPD regime-break detector: https://www.mql5.com/en/articles/23482
- MetaQuotes CUSUM structural-break detector: https://www.mql5.com/en/articles/23043
- MetaQuotes CUSUM validation follow-up: https://www.mql5.com/en/articles/23103
- TradingView open-source Heikin-Ashi real-price execution example: https://www.tradingview.com/script/xFBoQENG-Heikin-Ashi-Strategy-Example/
- TradingView Japanese Fibonacci/OTE catalog: https://jp.tradingview.com/scripts/fibonacci/
- TradingView Chinese Heikin-Ashi catalog: https://cn.tradingview.com/scripts/heiken-ashi/
- TradingView Japanese Kalman catalog: https://jp.tradingview.com/scripts/kalman-filter/
- TradingView Korean Fibonacci catalog: https://kr.tradingview.com/scripts/fibonacciretracement/
- TradingView open-source sample-entropy regime detector: https://www.tradingview.com/script/1ZBMuq8g-Sample-Entropy-SampEn-Regime-Detector/
- TradingView open-source two-state Kalman trend/velocity implementation: https://www.tradingview.com/script/tnWkCBVp-Kalman-Trend-Filter-JOAT/

These sources support testable mechanics, not accepted profitability.

## Part A — five new standalone complex Entry clocks

Five new causal candidate families were reconstructed directly from original Jan-Jul Dukascopy Bid/Ask ticks:

1. X17 Fibonacci BOS → pullback → reacceleration
2. X18 Heikin-Ashi BOS transition
3. X19 Ichimoku Kumo breakout → retest
4. X20 Bollinger/Keltner squeeze release
5. X21 second-entry trend pullback

All execution labels used actual Bid/Ask and the frozen BETA Entry→Hold research geometry.

### Aggregate raw Jan-Jul results

| Candidate | N | Raw survival | FP | Diagnostic value |
|---|---:|---:|---:|---:|
| X17 Fibonacci BOS pullback | 523 | 11.66% | 7.84% | -$433.37 |
| X18 Heikin-Ashi BOS transition | 5,258 | 8.54% | 5.42% | -$4,030.05 |
| X19 Ichimoku Kumo retest | 1,559 | 6.35% | 6.99% | -$1,249.37 |
| X20 BB/KC squeeze release | 588 | 6.80% | 6.97% | -$475.78 |
| X21 second-entry pullback | 1,730 | 8.79% | 6.76% | -$1,382.71 |

Decision: **all five standalone clocks rejected**.

A separate leave-one-month-out survival/value refinement was then run on each candidate family. None could form even one six-month development threshold satisfying the research requirement of >=85% survival with positive path value and minimum activity.

This is a strong rejection of these mechanics as new full-authority Entry specialists in their tested forms.

## Part B — community systems as context adapters on valid C02C entries

The same concepts were then used as causal state descriptors on the already-valid 5,519-trade C02C selected Entry population.

Tested context families:

- Fibonacci/trend geometry:
  - trend side
  - trend strength
  - rolling swing position
  - causal retracement depth
  - 0.382–0.786 retracement-zone membership
- Heikin-Ashi:
  - completed 15-second HA side
  - prior/current streak length
  - HA body/range strength
  - opposing-wick cleanliness
  - side alignment with the parent Entry
- Ichimoku:
  - causal current Kumo location
  - Tenkan/Kijun side
  - cloud distance
- BB/KC squeeze:
  - squeeze state
  - squeeze duration/charge
  - normalized band width
- Regime state:
  - two-state Kalman level/velocity
  - normalized Kalman innovation
  - Kalman uncertainty/gain
  - price-to-state gap
  - sequential two-sided CUSUM event/age/pressure
  - sign entropy
  - lag-1 return autocorrelation
  - short regime efficiency

### Global leave-one-month-out survival discrimination

Mean held-out AUC:

- Base frozen score features: 0.653315
- Base + existing 1s microstate: 0.674271
- + Fibonacci context: 0.674662
- + Heikin-Ashi context: **0.684662**
- + Ichimoku context: 0.672028
- + squeeze context: 0.675422
- + all first-wave community context: 0.681800

Heikin-Ashi produced the strongest global incremental information.

Important methodological rule: Heikin-Ashi synthetic prices were **never** used as executable fills. HA is state/context only; actual execution remains Dukascopy Bid/Ask.

## Part C — specialist-specific context ablation

One universal context stack was inferior to specialist-specific assignment.

Mean held-out AUC deltas versus each desk's micro-only model:

### Heikin-Ashi effects

- E12 Failed Expansion: **+0.181473**
- E9 Level Break: **+0.049503**
- E6 Value Reversion: **+0.034061**
- E7 Sweep/Reclaim: approximately neutral
- E11 Kinetic Ignition: approximately neutral
- E10 Compression Release: -0.006668
- E5 VWAP Reclaim: -0.008938

### Fibonacci effects

- E5 VWAP Reclaim: **+0.033066**
- E12 Failed Expansion: +0.025630
- E10 Compression Release: +0.019395
- E9 Level Break: +0.014846
- E11 essentially neutral
- E7 and E6 degraded

### Squeeze-state effects

- E12 Failed Expansion: **+0.041512**
- E5 VWAP Reclaim: +0.021507
- E9 Level Break: +0.015441
- E11 small positive
- E6/E10 degraded

### Kalman/CUSUM/entropy regime effects

- E12 Failed Expansion: **+0.067765**
- E7 Sweep/Reclaim: **+0.052402**
- E9 Level Break: +0.009381
- E6 Value Reversion: +0.007641
- E11 small positive
- E5/E10 degraded

Combining HA + regime improved:

- E12: **+0.184831**
- E7: +0.061520
- E6: +0.049922
- E9: +0.046045

## Part D — specialist-adapter matrix

A fixed research adapter map was then declared from the ablation evidence:

- E5 VWAP Reclaim → Fibonacci + squeeze
- E6 Value Reversion → Heikin-Ashi + regime
- E7 Sweep/Reclaim → regime
- E9 Level Break → Heikin-Ashi + Fibonacci + squeeze
- E10 Compression Release → Fibonacci
- E11 Kinetic Ignition → squeeze only as a diagnostic; no expansion priority
- E12 Failed Expansion → Heikin-Ashi + regime + squeeze + Fibonacci

Leave-one-month-out AUC versus micro-only:

| Specialist | Micro AUC | Adapter AUC | Delta | Positive folds |
|---|---:|---:|---:|---:|
| E12 | 0.503274 | **0.679772** | **+0.176499** | **7/7** |
| E9 | 0.500592 | **0.570185** | **+0.069593** | **7/7** |
| E6 | 0.510093 | 0.576432 | +0.066339 | 4/7 |
| E5 | 0.639800 | 0.693146 | +0.053346 | 5/7 |
| E7 | 0.579872 | 0.632755 | +0.052884 | 4/7 |
| E10 | 0.642860 | 0.659614 | +0.016753 | 4/6 |
| E11 | 0.644617 | 0.647973 | +0.003356 | 3/7 |

### Most important finding

E12 and E9 adapter improvement reproduced in **every held-out month**.

This is materially stronger than the standalone-system experiments and stronger than applying every context to every desk.

## Part E — E12 quality-reserve stress test

A nested LOMO threshold test was run for E12 using the Heikin-Ashi adapter.

At a training-month target of >=87% survival, the cross-fitted E12 HA adapter retained 256 held-out trades with:

- weighted held-out survival: **90.23%**
- every held-out month >=85%
- positive aggregate diagnostic path value
- monthly held-out survival:
  - Jan 90.91%
  - Feb 100%
  - Mar 95.59%
  - Apr 85.71%
  - May 88.89%
  - Jun 85.25%
  - Jul 100%

This is **not an opportunity expansion result** because it selects a high-quality subset of existing E12 trades. It is a quality reserve and evidence that E12 rejected/unused parent-adjacent candidates are a high-priority expansion target once the exact parent candidate universe is recovered.

## Current scientific conclusion

The user's hypothesis that a missing complex system may bridge BETA's opportunity deficit is partly supported, but not in the form of a thirteenth universal Entry clock.

The strongest design is:

`validated parent specialist → specialist-specific complex-state adapter → survival/value admission → coverage utility → idle-slot ownership`

rather than:

`new universal indicator → trade`

### Carry forward

- **E12:** HA + Kalman/CUSUM/entropy regime + squeeze + Fib context — highest priority.
- **E9:** HA + Fib + squeeze — second highest priority; 7/7 positive AUC folds.
- **E6:** HA + regime only; do not use Fibonacci.
- **E7:** regime/change-state context.
- **E5:** Fibonacci + squeeze context.
- **E10:** Fibonacci context only.
- **E11:** preserve as saturated control.

### Reject as standalone authority

- naked Fibonacci retracement Entry
- Heikin-Ashi color/flip Entry
- Ichimoku Kumo retest Entry
- BB/KC squeeze release Entry
- generic second-entry pullback Entry

### Next bounded unit

**BETA064_C02H_02_PARENT_ADJACENT_ADAPTER_EXPANSION**

Goal:

1. recover/reconstruct as much exact unused/rejected parent opportunity state as is scientifically possible;
2. apply the fixed adapter matrix above;
3. prioritize E12 and E9 first because their discrimination gain passed 7/7 folds;
4. require new additions themselves to clear >=85% Entry→Hold survival by month, not merely hide inside the strong parent portfolio;
5. require positive diagnostic path value;
6. increase condition-matched coverage and final trade count;
7. preserve frozen Major Checkpoint 02 first ownership;
8. keep August sealed;
9. no MQL5 until owner authorization.

Major Checkpoint 02 remains unchanged.
