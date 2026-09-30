# BETA064 C02H-A — Community System Specialist + Context-Adapter Screen

**Parent:** BETA064 Major Checkpoint 02 / C02G continuation authority  
**Status:** RESEARCH SUB-UNIT — NO CHECKPOINT MUTATION  
**Scope:** Entry→Hold only  
**Hold→Exit:** deferred  
**August:** sealed and not read  
**Alpha/GAMMA:** prohibited and not used  
**MQL5:** no authorization / no change

## Objective

Continue repairing and expanding the twelve Entry specialists while screening reconstructible community systems that could either:

1. become a genuinely orthogonal new Entry specialist; or
2. provide a specialist-specific causal context adapter that improves Entry→Hold discrimination without creating another weak signal clock.

The owner specifically proposed Fibonacci and Heikin-Ashi as examples. Additional reconstructible systems screened here include adaptive Kalman pullback recovery, Donchian+ADX breakout confirmation, Hurst/entropy regime state, Bollinger/Keltner squeeze state, and causal harmonic Fibonacci structures.

Community performance claims were not treated as evidence. All mechanisms were independently reconstructed and tested on original Dukascopy XAUUSD Bid/Ask ticks January–July only.

## Frozen control

Major Checkpoint 02 remains immutable:

- 5,070 one-position Entry→Hold trades
- 88.44% weighted survivability
- every observed month >85%
- seven of seven leave-one-month-out months >85%

C02C remains the main larger research child:

- 5,519 trades
- 88.20% weighted survivability
- every observed month >85%
- February held-out remains the historical binding regime in the original C02C threshold exercise

## Community source families reconstructed

### Fibonacci pullback geometry

Public MQL5 implementations define Fibonacci retracement from completed swing/range anchors and commonly test 0.382, 0.500, 0.618 and 0.786 zones. For BETA, Fibonacci was made causal by using only completed prior ranges and requiring short-horizon reacceleration before the proposal.

Sources:
- https://www.mql5.com/en/articles/20221
- https://www.mql5.com/ja/articles/12301
- https://www.mql5.com/ja/articles/20289

### Heikin-Ashi

Heikin-Ashi is reconstructible from completed OHLC values and is useful as a smoothed trend-state representation. It must not be used as an executable fill price because its displayed OHLC is synthetic. BETA therefore used completed HA only for state and always labeled/executed on real Dukascopy Bid/Ask.

Sources:
- https://www.mql5.com/en/articles/17021
- https://www.mql5.com/en/articles/20851
- https://www.tradingview.com/script/xFBoQENG-Heikin-Ashi-Strategy-Example/
- https://www.tradingview.com/script/9z16eauD-Heikin-Ashi-Supertrend/

### Hurst / entropy / regime state

Public reconstructible research uses Hurst-like persistence and entropy/efficiency measures to distinguish persistent, anti-persistent and chaotic states rather than applying the same strategy to every regime.

Sources:
- https://www.mql5.com/en/articles/22553
- https://www.mql5.com/en/articles/23351
- https://www.mql5.com/en/articles/21743
- https://www.mql5.com/en/articles/24161

### Bollinger/Keltner squeeze

The squeeze concept compares Bollinger statistical dispersion with an ATR-based Keltner envelope. This differs from BETA's existing range-compression ratio and was tested as contextual state.

Sources:
- https://www.tradingview.com/script/qY4V9d04-TTM-Squeeze/
- https://www.tradingview.com/script/yU4Zq0jT-BB-Keltner-Squeeze-Strategy/

### Donchian + ADX

Public Donchian systems combine channel breaks with ADX and directional movement confirmation to distinguish directional breaks from false breaks.

Source:
- https://www.mql5.com/en/articles/3146

### Harmonic Fibonacci structures

AB=CD and Gartley systems use confirmed pivot sequences plus explicit Fibonacci retracement/extension ratios. BETA used causal pivot confirmation; a D pivot was not actionable until the required right-side confirmation bars had completed.

Sources:
- https://www.mql5.com/en/articles/19111
- https://www.mql5.com/en/articles/19442
- https://www.mql5.com/en/articles/19331

## Standalone new-desk screen

Four initial new specialist families were generated on completed causal state and labeled with the existing BETA Entry→Hold barrier geometry.

### E17 — Fibonacci Structural Pullback

Best raw variant:
- 15m 0.382–0.500 zone
- 362 proposals
- 25.69% survival
- 14.09% favorable-first-passage
- negative diagnostic value

Other 15m/1h Fib zones were weaker or too sparse.

### E18 — Heikin-Ashi Trend Restart

M1 HA restart:
- 2,133 proposals
- 23.63% survival
- 16.36% favorable-first-passage
- negative diagnostic value

M1 strong HA continuation:
- 18,861 proposals
- 22.38% survival
- negative diagnostic value

Leave-one-month-out refinement could form development gates in four HA-restart folds, but all four failed the omitted month. Aggregate gated held-out sample:
- 19 trades
- 31.58% survival
- negative diagnostic value

### E19 — Kalman Pullback Recovery

- 5,237 proposals
- 20.15% survival
- 14.21% favorable-first-passage
- negative diagnostic value
- no portable six-month >=85% development gate

### E20 — Donchian + ADX

- 14,656 proposals
- 20.14% survival
- 16.78% favorable-first-passage
- negative diagnostic value
- no portable six-month >=85% development gate

**Decision:** E17–E20 are rejected as standalone Entry desks.

## Harmonic shadow screen

Causal M1 pivot confirmation was tested with 3/5/8 left-right confirmation bars.

AB=CD:
- LR3: 1,559 proposals / 11.29% survival
- LR5: 980 / 11.22%
- LR8: 623 / 10.59%
- all negative diagnostic value

Gartley:
- LR3: 348 proposals / 12.93% survival
- LR5: 218 / 9.63%
- LR8: 127 / 8.66%
- all negative diagnostic value

**Decision:** AB=CD/Gartley are rejected as position-owning specialists. Harmonic/Fibonacci geometry may remain context/location information only.

## Context-adapter result on the valid C02C Entry population

The key positive result came from applying community mechanics as **specialist-specific state**, not as new clocks.

Held-out AUC comparisons against the corresponding micro-derivative model:

### E6 Value Reversion — Hurst/entropy regime adapter

Micro baseline mean held-out AUC:
- 0.5091 in the controlled component ablation

Micro + Hurst/entropy/efficiency/variance-ratio state:
- **0.5732**
- delta **+0.0641**

The strongest fitted importance was concentrated in:
- 1h entropy
- 1h Hurst
- 15m variance ratio
- 15m entropy/Hurst
alongside existing micro jerk/velocity state.

Interpretation:
E6 requires explicit persistent-vs-anti-persistent regime discrimination. This is a meaningful parent-specialist repair feature.

Important boundary:
when the same regime features were applied to the enormous raw E6D2 derivative opportunity surface, mean LOMO AUC was effectively unchanged:
- base ~0.72981
- regime ~0.72977

No six-development-month >=85% standalone tail emerged.

Therefore Hurst/entropy is an **E6 parent-admission adapter**, not permission to manufacture more E6 clocks.

### E7 Sweep/Reclaim — Heikin-Ashi state adapter

Micro baseline:
- 0.5729

Micro + completed HA state:
- **0.6014**
- delta **+0.0286**

Interpretation:
smoothed directional persistence/restart state helps distinguish higher-quality sweep reclaims, but HA may not supply executable prices or own trades.

### E9 Level Break — Heikin-Ashi and squeeze context

Micro baseline:
- ~0.515–0.524 depending ablation harness

HA state:
- delta about **+0.0197**

Squeeze state:
- delta about **+0.0156**

Interpretation:
E9 benefits from separating accepted directional migration from noisy/failed breaks using state persistence and pre-break volatility structure.

### E12 Failed Expansion — squeeze state

Micro baseline:
- ~0.453

Micro + Bollinger/Keltner squeeze state:
- **~0.529**
- delta **+0.0756**

Fibonacci location alone also produced a smaller positive delta of about +0.0129.

Interpretation:
squeeze/volatility-cycle state is highly relevant to whether an attempted expansion is genuinely failing. Fibonacci geometry is secondary location context.

### E5 VWAP Reclaim — squeeze + directional context

Micro baseline:
- ~0.655

Micro + squeeze:
- ~0.693
- delta **+0.0382**

Micro + ADX/directional state + squeeze:
- **~0.703**
- delta **+0.0477**

HA alone was only a small positive increment.

Interpretation:
E5 is better treated as a value migration/reclaim event whose quality depends on the surrounding expansion/compression and directional regime.

### E10 Compression Release — negative control

Micro baseline:
- ~0.673

Adding squeeze:
- ~0.636
- delta **-0.037**

Adding HA/Fibonacci/Hurst-style context also reduced discrimination in separate tests.

Interpretation:
E10 already owns compression→expansion. Adding another squeeze representation duplicates or contaminates the useful micro information. Keep E10's existing derivative/micro state rather than making it more complex.

## Universal-complexity rejection

A global C02C model with Hurst/entropy/HA/Fibonacci regime state did not beat the existing micro-derivative model:

- base micro derivative mean held-out AUC: ~0.6690
- micro + full regime bundle: ~0.6673

A second-stage tailored stack likewise failed to improve the global cross-fitted discriminator:

- existing derivative meta AUC: ~0.67436
- stacked specialist-context AUC: ~0.67381

**Decision:** do not build a universal mega-filter. The new features have value only when conditioned on the specialist thesis.

## Current recommended C02H adapter matrix

| Specialist | Adapter decision |
|---|---|
| E1 Macro Trend | preserve current state; no new adapter yet |
| E2 Pullback/Reaccel | preserve; Fib clock rejected |
| E3 ORB | preserve; no new independent clock |
| E4 VWAP Pullback | preserve |
| E5 VWAP Reclaim | **add research adapter: squeeze + directional state** |
| E6 Value Reversion | **add research adapter: Hurst/entropy/variance regime** |
| E7 Sweep/Reclaim | **add research adapter: completed Heikin-Ashi state** |
| E8 Level Bounce | preserve pending stronger level-ownership work |
| E9 Level Break | **add research adapter: HA state + squeeze context** |
| E10 Compression Release | **do not add new complexity; existing micro/derivative state wins** |
| E11 Kinetic Ignition | saturated control; do not expand |
| E12 Failed Expansion | **add research adapter: squeeze state; Fib location secondary** |

These adapters are research features only. They do not yet authorize added trades.

## Scientific conclusion

The missing opportunity is **not another generic technical strategy**.

Repeated standalone screens now reject:
- broader versions of E1–E12;
- Fibonacci pullback clocks;
- Heikin-Ashi Entry clocks;
- Kalman pullback clocks;
- Donchian+ADX clocks;
- AB=CD harmonic reversal;
- Gartley harmonic reversal.

The useful discovery is that several community systems become informative when reinterpreted as **conditional state lenses inside the specialist that economically owns that mechanism**.

This supports the next C02H construction:

parent Entry proposal
→ session authority
→ specialist-specific context adapter
→ frozen survivability authority
→ coverage-deficit + novelty + execution-feasibility utility
→ one-position ownership
→ H1–H8 Hold floor

Do not replace C02G's session derivative authority matrix. The new adapter matrix should sit beside it and be evaluated only at the same parent proposal timestamp using already-completed data.

## Next bounded research

1. Reconstruct exact parent-adjacent unused/rejected candidate states wherever durable artifacts permit.
2. Apply only the adapter relevant to that parent specialist:
   - E5: squeeze/directional
   - E6: Hurst/entropy/variance regime
   - E7: HA state
   - E9: HA + squeeze
   - E12: squeeze + Fib location
3. Keep E10/E11 as negative controls for excess complexity.
4. Require new additions themselves—not merely the combined strong portfolio—to demonstrate >=85% Entry→Hold survival with positive diagnostic path value under held-out-month testing.
5. Spend any quality reserve on **new idle opportunities**. Do not call deletion-only quality improvement a coverage breakthrough.
6. Major Checkpoint 02 remains immutable.
7. Hold→Exit remains deferred.
8. August remains sealed.
9. No MQL5 change.
