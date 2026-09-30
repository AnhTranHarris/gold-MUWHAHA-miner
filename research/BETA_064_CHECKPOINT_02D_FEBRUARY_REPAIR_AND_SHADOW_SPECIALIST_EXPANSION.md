# BETA064 CHECKPOINT 02D — February Regime Repair + Four New Shadow Entry Specialists

**Date:** 2026-09-30  
**Parent control:** BETA064 Major Checkpoint 02 — frozen  
**Immediate parent child:** Checkpoint-02C  
**Status:** ROBUST RESEARCH CHILD / MAJOR-CHECKPOINT CANDIDATE — NOT FROZEN  
**Scope:** ENTRY→HOLD only  
**Hold→Exit:** deferred  
**August:** sealed and not read  
**Alpha/GAMMA contamination:** prohibited; no Alpha/GAMMA rules or code were used.

## Objectives

1. Remove the Checkpoint-02C February leave-one-month-out survivability defect without collapsing opportunity count.
2. Search for up to four genuinely orthogonal new causal Entry specialists that can broaden the BETA opportunity universe.
3. Admit no new specialist unless it supports the owner's >=85% Entry→Hold survivability standard.

## Part A — February regime repair

Checkpoint-02C produced 5,519 Jan–Jul trades at 88.20% weighted survivability, but leave-one-month-out February landed at ~84.95%.

Attribution showed the weak additions were concentrated in:
- E9 Level Break;
- E7 Sweep/Reclaim;
with Australia/Asia particularly weak in February.

The repair is deliberately small and architecture-preserving:

- E9 child minimum `ps_b75`: **0.915**
- E7 child minimum `ps_b75`: **0.915**
- all other Checkpoint-02C rules unchanged.

This is only +0.0005 above the previous shared 0.9145 child authority.

### Fixed-rule Jan–Jul result

| Month | Trades | Survivability | FP success | Diagnostic value |
|---|---:|---:|---:|---:|
| Jan | 761 | 88.83% | 61.63% | +$760.67 |
| Feb | 1,021 | **85.99%** | 58.28% | +$1,158.88 |
| Mar | 1,484 | 87.80% | 60.31% | +$1,730.66 |
| Apr | 657 | 88.74% | 61.19% | +$718.73 |
| May | 582 | 90.55% | 64.09% | +$646.40 |
| Jun | 636 | 89.94% | 62.42% | +$693.56 |
| Jul | 328 | 89.94% | 59.45% | +$272.76 |
| **Total** | **5,469** | **88.39% weighted** | **60.82% weighted** | **+$5,981.67** |

Relative to frozen Major Checkpoint 02:
- trades: 5,070 → **5,469**
- incremental trades: **+399**
- incremental trade count: **+7.87%**
- weighted survivability: 88.44% → **88.39%**
- every month remains >=85%.

Relative to C02C:
- trades: 5,519 → 5,469
- 50 marginal trades removed;
- February observed survivability rises from 85.56% to 85.99%;
- weighted survivability rises from 88.20% to 88.39%.

### Leave-one-month-out result

For each held-out month, the E9/E7 authority pair was selected using the other six months only, requiring all six training months to remain >=85% while maximizing retained trade count.

Every fold selected the same pair:

`E9 >= 0.915; E7 >= 0.915`

Held-out results:

| Month | Held-out trades | Held-out survivability |
|---|---:|---:|
| Jan | 761 | 88.83% |
| Feb | 1,021 | **85.99%** |
| Mar | 1,484 | 87.80% |
| Apr | 657 | 88.74% |
| May | 582 | 90.55% |
| Jun | 636 | 89.94% |
| Jul | 328 | 89.94% |

**7/7 held-out months pass.**

This fixes the Checkpoint-02C robustness failure without using February to choose a special February-only exception.

## Condition-matched SYNTH coverage

Frozen SYNTH Entry→Hold denominator: 71,810.

- Major Checkpoint 02 matched: 3,044 = 4.24%.
- C02C matched: 3,164 = 4.41%.
- C02D matched: **3,127 = 4.35%.**

C02D sacrifices 37 condition-cell matches versus C02C to remove the weak E7/E9 tail, but remains above the frozen parent's condition-cell coverage and preserves +399 real Entry→Hold trades.

## Part B — New specialist research

Community research was used only for reconstructible mechanics, not performance claims.

Key mechanics reviewed:
- session/opening-range break → retest → re-break;
- liquidity sweep → post-sweep FVG → retrace;
- online regime-change detection as a causal primitive;
- opening-drive first pullback;
- second-entry trend pullback;
- price/pressure absorption divergence.

Representative public sources:
- MetaQuotes ORB retest/re-break implementation: https://www.mql5.com/en/articles/18486
- MetaQuotes BOCPD causal regime-break implementation: https://www.mql5.com/en/articles/23482
- MetaQuotes Liquidity Sweep on BoS: https://www.mql5.com/en/articles/20569
- TradingView open-source Liquidity Sweep → FVG → retrace: https://www.tradingview.com/script/loNFaWST-Liquidity-Sweep-Signals/
- TradingView open-source FVG/Liquidity Void logic: https://www.tradingview.com/script/q67i2j7X-Fractal-Break-Imbalance-Fair-Value-Gap-FVG-Liquidity-Void/
- TradingView Opening Pullback Planner: https://www.tradingview.com/script/ZDApgmmt-Opening-Pullback-Planner-AGPro-Series/
- TradingView Absorption Signals: https://www.tradingview.com/script/Vv1cMEUF-Absorption-Signals/

### Shadow specialist registry

Four new Entry clocks are retained for **SHADOW RESEARCH ONLY**:

#### E13 — Opening Drive First Pullback
Mechanism:
session opens → first 15-minute directional drive locks → first constructive pullback → causal reacceleration.

Observed Jan–Jul raw candidate population:
- 699 candidates
- 11.73% raw survival
- 8.30% FP success

LOMO models showed useful discrimination in several months, but no stable >=85% tail.

**Status: SHADOW ONLY.**

#### E14 — Sweep → FVG → Retest
Mechanism:
confirmed prior-structure sweep/reclaim → directional displacement creates literal three-bar imbalance → first retest of imbalance → directional confirmation.

Observed:
- 18,416 candidates
- 12.68% raw survival
- 7.80% FP success

LOMO AUC was generally ~0.61–0.70, but even the top 0.5% OOF survival tail was only ~53.8%.

**Status: SHADOW ONLY.**

#### E15 — Regime-Shift First Pullback
Mechanism:
causal standardized 30-second displacement + volatility expansion/change event → counter pullback → retained impulse → renewed directional extreme.

Observed:
- 3,206 candidates
- **35.46% raw survival**
- 21.68% FP success

This was the strongest new raw survival population.

LOMO AUC was roughly 0.58–0.67. The top 1% OOF survival tail reached ~63.6%; top 0.5% reached ~70.6% but was sparse and unstable.

**Status: HIGH-PRIORITY SHADOW; not authorized to trade.**

#### E16 — Second-Entry Trend Pullback
Mechanism:
persistent 15-minute/5-minute trend context → first counter pullback → first continuation attempt → second pullback → renewed continuation.

Observed:
- 4,461 candidates
- 24.16% raw survival
- 18.54% FP success

LOMO AUC was unusually consistent around ~0.63 across all months. The top 1% OOF tail reached ~62.2% survival and ~40% FP success with slightly positive diagnostic value, but remained far below the 85% survivability standard.

**Status: HIGH-PRIORITY SHADOW; not authorized to trade.**

### Rejected active specialist variants

The following are explicitly rejected for active BETA routing:
- broad FVG retest;
- quote-pressure absorption as a standalone entry;
- broad session handoff retest;
- independent session-value-only reversion;
- ORB retest/re-break in its first tested form.

The ORB retest/re-break sequence generated roughly 109–131 trades/month but only ~9–21% raw survival depending on month.

## Order-flow caution

Dukascopy quote/tick volume is not centralized exchange aggressor delta.

Therefore absorption/pressure variables may remain contextual features but must not be presented as true centralized order-flow evidence.

## Quant decision

### Active child
Carry C02D forward as the strongest post-Major-Checkpoint-02 child:
- 5,469 trades;
- 88.39% weighted survivability;
- 7/7 month pass;
- 7/7 leave-one-month-out pass;
- 4.35% SYNTH condition-cell coverage.

C02D is a **major-checkpoint candidate**, but is not frozen in this unit.

### New specialists
Introduce E13–E16 into the BETA research taxonomy only as **shadow specialists**.

They may:
- generate proposals;
- log causal features;
- receive counterfactual survival/FP labels;
- participate in future offline research.

They may not:
- own a live/research position;
- dilute the active >=85% portfolio;
- change Major Checkpoint 02;
- change C02D active routing.

### Next bounded research
1. continue E15/E16 refinement because they showed the strongest reproducible discrimination;
2. investigate whether E15/E16 can become state-specific session specialists rather than universal desks;
3. use E13/E14 primarily as event/context features unless materially better causal definitions emerge;
4. continue opportunity recovery in proven E5/E10/E12 cells;
5. preserve E11 as saturated control;
6. hold Hold→Exit unchanged;
7. keep August sealed.

No Alpha/GAMMA imports.
No MQL5 change.


## E15/E16 bounded gap-fill graduation test — rejected

After the initial shadow evaluation, E15 Regime-Shift First Pullback and E16 Second-Entry Trend Pullback were given one additional opportunity to qualify without changing C02D.

Method:
- reserve every C02D active trade interval first;
- consider only E15/E16 proposals that occur while C02D is flat;
- use leave-one-month-out survival probabilities already generated without the proposal's month in model training;
- test bounded survival thresholds and session-specific tails;
- preserve one-position chronology;
- require the combined portfolio to remain >=85% survivability in every month.

Idle shadow pool:
- E15: 1,472 proposals;
- E16: 2,617 proposals;
- total: **4,089** proposals.

A post-hoc grid can force approximately 150 additional proposals into the combined portfolio while keeping the headline minimum month barely above 85%. However the added trades themselves have only roughly 40–46% Entry→Hold survival and negative diagnostic path value.

Representative maximum-count admissible combination:
- 157 added trades;
- added-trade survivability ~44.6%;
- added diagnostic value approximately -$211.70;
- combined minimum-month survival ~85.02%.

A separate specialist × session scan found **no** E15/E16 gap-fill subset with at least five added trades that simultaneously achieved:
- >=85% own Entry→Hold survivability; and
- positive diagnostic path-resolution value.

Therefore the apparent portfolio-level admissibility is rejected as survivability-buffer dilution.

**Decision:** E15 and E16 remain high-priority shadow research desks only. They may not own positions in C02D or Major Checkpoint 02.

This reinforces a hard BETA principle: a strong parent portfolio may not be used to hide a weak specialist.
