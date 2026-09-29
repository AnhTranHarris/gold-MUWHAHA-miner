# BETA031 — Duration-aware state mixture AI: causal utility improvement vs R9 teacher gap

**Date:** 2026-09-29  
**Lineage:** independent `beta`; BETA029/BETA030 research parents only.  
**Data:** original ordered Dukascopy XAUUSD Bid/Ask Jan–Jul 2026; August SEALED.  
**Status:** BOUNDED CAUSAL RESEARCH / NO PROMOTION / NO OFFICIAL MQL5 EA.

## Question

Determine whether a highly state-aware custom AI formula can bridge more of the R9 REAL tick-action gap toward R9 OVERFIT behavior and R9 SYNTH performance while remaining deterministic enough for eventual native MT5 reproduction.

## BETA030 prerequisite result

BETA030 tested a causal **59-feature** state-aware LightGBM system: 26 quote/micro features + 26 M1/M5 registry features + seven causal intrinsic-time shape features (permutation entropy, finite two-sided CUSUM, sign-recross ratio, path efficiency, variance-ratio proxy and quote-intensity ratio). Jan–Mar fit, April threshold calibration, May–Jul frozen historical diagnostic (all months previously inspected, therefore NOT pristine OOS). The seven new shape/CUSUM features produced **zero incremental May–Jul absolute positive-count gain** over the 52-feature ablation at the locked threshold.

BETA030 Global AI May–Jul: parent 13,650 correct +15s observations -> 13,702 (+52), but costed markout sum worsened by about $46.68 and selected paired SYNTH same-side ±5s fell 13,495 -> 13,338. Four FULL unselected original logger days: parent SYNTH same-side = 1,022, BETA030 = 1,012. Complexity alone did not bridge the teacher gap.

## BETA031 explicit MT5-portable formula

BETA031 keeps the same 59 strictly causal origin features and adds four causal state-duration variables:
1. `log1p(regime_age_seconds)`
2. `log1p(previous_event_gap_seconds)`
3. `state_changed` at the current event
4. empirical Jan–Mar state survival `S_s(age)=P(D_s >= age)` from completed semantic-state runs.

Offline target is `y=clip(R_opposite - R_parent,-4,+4)` where both are executable quote-side +15s outcomes. Future outcome is used only as an offline training label and is never available to execution.

A regularized global ridge expert and one ridge expert per semantic state are fit on Jan–Mar. Leave-one-month-out MSE selected `alpha=300`.

For current semantic state `s`, standardized features `z`:

```
G_t     = betaG_0 + SUM_j betaG_j * z_j
L_t(s)  = betaS_0 + SUM_j betaS_j * z_j
lambda  = clip(0.10 + 0.65*S_s(age_t) - 0.35*I[state_changed], 0.05, 0.75)
DeltaU  = (1-lambda)*G_t + lambda*L_t(s)
```

April calibration selected threshold **$0.20/oz**. Retain original R9 side unless `DeltaU > 0.20`; then flip side **on the same observed origin tick**. No abstention and no timestamp change. This is a directional-owner experiment, not a SYNTH-clock model.

## Results

### Entry / quote outcome

Jan–Jul parent: **34,784 / 183,222** positive +15s; costed markout sum **-$132,571.24**.  
BETA031: **35,397** positives (**+613**) and **-$130,675.86** (**+$1,895.38 relative**, still deeply negative).

Frozen May–Jul historical diagnostic: parent **13,650 / 80,165**, **-$52,550.62**; BETA031 **13,788** (**+138, +1.01%**) and **-$52,470.30** (**+$80.32**).

79-day block bootstrap, descriptive only: correct-count delta 95% interval **+42 to +238**; dollar delta **-$251 to +$405**. These months were previously inspected; this is not untouched validation.

### Integrated one-position shadow May–Jul

| Lifecycle | Parent | BETA031 | Relative net |
|---|---:|---:|---:|
| L15 | 70,269 positions / 13,007 wins / -$45,483.77 | 70,269 / 13,129 / -$45,449.98 | **+$33.78** |
| L30 | 61,741 / 15,780 / -$39,918.36 | 61,724 / 15,871 / -$39,812.64 | **+$105.72** |
| L45 trail | 55,734 / 20,526 / -$36,280.10 | 55,723 / 20,608 / -$36,170.51 | **+$109.59** |

All remain negative. This is shadow chronology, NOT BETA015 funded replay or native broker MT5 parity.

## Critical teacher-gap falsification

The custom formula improves some real-feed utility while moving **away** from R9 SYNTH behavior.

Selected historical paired SYNTH same-side ±5s:
- Jan–Jul parent **34,394** -> BETA031 **32,957** (**-1,437**)
- May–Jul parent **13,495** -> **12,885** (**-610**)

Four FULL unselected original Coinexx logger days (5,105 SYNTH / 6,192 REAL source entries):
- SYNTH same-side ±5s: parent **1,022** -> BETA031 **951 (-71)**
- REAL same-side ±5s: parent **2,976** -> BETA031 **2,812 (-164)**

Near-time match counts do not change because BETA031 changes direction only. The model therefore does **not** solve the synthetic timing gap.

## Quant/community cross-reference

- MQL5 **Hidden Semi-Markov Models for Duration-Aware Regime Detection** (2026-09-28) explicitly separates state identity from state duration and maintains a causal belief over `(state, remaining_duration)`; use as a reconstructible mechanism clue, not BETA profitability evidence: https://www.mql5.com/en/articles/24460
- MQL5 **BOCPD** produces a per-bar causal probability that a regime just broke and explicitly is not a direction predictor: https://www.mql5.com/en/articles/23482
- MQL5 **Ordinal Pattern Transition Networks** implements permutation entropy and time-irreversibility/Jensen-Shannon market-shape metrics: https://www.mql5.com/en/articles/23451
- MQL5 **CUSUM** provides sequential break detection; later empirical calibration work warns theoretical false-alarm run-length formulas can be materially wrong on market data: https://www.mql5.com/en/articles/23043 and https://www.mql5.com/en/articles/23103
- Open-source TradingView breakout/retest implementations support role-separated structure -> breakout -> retest -> managed-risk state machines; performance claims are not imported as evidence.
- Community regime discussions repeatedly warn that hard filters can merely delete trades; BETA029/030 demonstrated this directly.

## Scientific decision

**NO PROMOTION.** Preserve BETA031 as a reproducible *directional ownership* research component because it provides modest real-feed improvement and is exactly representable as standardized linear coefficients + state-survival gating. It does **not** bridge R9 SYNTH/OVERFIT actions, remains negative after costs, and its magnitude is too small.

The current evidence says the bridge needs **separate causal tasks**, not one monolithic AI:
1. **Clock/eligibility model** — predict when a SYNTH-like opportunity is becoming actionable; teacher times remain posthoc labels only.
2. **Directional owner** — BETA031-style expected utility + structural CONTINUE/FADE/PENDING state.
3. **Dynamic proof** — first actually observed proof tick after state transition; never retrospective origin fill.
4. **Lifecycle owner** — early failed ignition vs runner persistence conditioned on causal expected remaining state duration.
5. **Teacher evaluation** — reconstruct full unselected 149-day original REAL/SYNTH teacher entry ledger before selecting a teacher-emulation model. Four days is insufficient.
6. Test **formal BOCPD and HSMM posterior variables as router inputs**, against BETA031 empirical survival. Do not simply enlarge the black-box model.

## Reproducibility

- Full BETA030 script SHA256: `1c7fd2716a089de29af65c954113778943c9291629e2dd53e930c32679ef8e12`
- BETA030 result SHA256: `f67c8f355f97f095bc2cccb02c8ca039d421fa8600d08f6edcfd91a3c367828a`
- BETA031 script SHA256: `df91d2f091f880dedf0a4b05f4804f39c7b970ed8d520ba81dad87e67c31b7c9`
- BETA031 results SHA256: `b862c9850e91e20ff81b5f2a412340fcde048ec8befcd30c10fd935fcd969221`
- Exact MT5 parameter manifest SHA256: `98a892d1776f33558be20dce4dcbea5116c3b8607cb09f823ce082ba1861056b`
- BETA031 QA: **28 PASS**.
- Conversation reproducibility bundle: `BETA031_STATE_AWARE_AI_RESEARCH_BUNDLE.zip`, SHA256 `8318dd12dd54ee4f364cb78715053546a03c363884b74a99b0abaa1b81cf3e1c`.
- August SEALED; approved BETA EA remains null.
