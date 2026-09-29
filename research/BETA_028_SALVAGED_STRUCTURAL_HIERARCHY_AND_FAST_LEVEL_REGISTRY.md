# BETA 028 — Salvaged structural hierarchy + fast event registry + secondary lifecycle optimization

**Date:** 2026-09-29  
**Lineage:** independent `beta` only  
**Data:** ORIGINAL ordered Dukascopy XAUUSD Bid/Ask ticks, Jan–Jul 2026  
**August:** SEALED  
**Status:** RESEARCH-ONLY / NO PROMOTION / NO MQL5 EA AUTHORIZATION

## Scope

Retain BETA025/026 entry foundations; salvage only causally reproducible old structural/event-state mechanisms; reopen HOLD/EXIT with lower weight than ENTRY accuracy. Historical R9/R10/Gamma code/results remain evidence-only. No quarantined P8/P9 economics, retrospective timestamps, or old fitted thresholds are inherited.

## BETA027 recovered mechanisms

A full salvage pass re-read **57,527,562** original Dukascopy quote ticks and rebuilt completed S1/M1/M5/M15/H1 structure, confirmed two-right-bar pivots, ownership context, sweep/acceptance state, quote toxicity, CONTINUE/FADE/PENDING routing, qualified-rearm archaeology and exact one-position lifecycle.

Common first-cycle population: **191,674** events; **183,222** evaluable +15s events. BETA025/026 control: **34,784** positive +15s entries (**18.985%**) and **34,394** selected historical R9 SYNTH same-side ±5s matches.

No BETA027 deterministic structural variant materially beat that control. A learned causal direction model added +563 positive +15s entries but lost 2,106 selected teacher matches and regressed in June/July. Its high-precision abstention policy retained only ~25% of opportunities. Not promoted.

Qualified second-opportunity rearm increased REAL-like churn: on four complete original Coinexx logger days, one-position SYNTH matches changed 883 -> 873 while REAL matches increased 2,424 -> 2,903. Tested rearm rejected.

Lifecycle exact-tick results remained negative after cost. 15s expiry: 158,701 positions / 32,833 winners / -$114,001.73 shadow net. 30s expiry: 136,476 / 38,408 / -$96,485.27. 60s expiry: 83,106 / 28,710 / -$57,953.97. Longer hold reduces position count; trailing raises positive-close count but worsens average economics in tested configurations. Hold/exit remains secondary.

## BETA028 persistent M1/M5 level registry

To repair M15 sparsity for 5–15s entry problems, BETA028 reconstructed causal M1/M5 pivot state directly from original ticks. Each confirmed level carries:
- level age;
- first/repeated touch count;
- accepted body/close state;
- wick/sweep count;
- time since interaction;
- side-specific ATR-normalized penetration/distance;
- side-specific event age.

Pivots become visible only after two required right-hand bars close; event state comes only from completed bars.

**64 QA assertions PASS** and exactly reproduce control totals: 191,674 events; 183,222 valid; 34,784 positives; 34,394 teacher matches.

### Registry-only result

Best deterministic immediate registry rule: **34,800** positives versus 34,784 control (**+16**). Precision 18.985% -> **18.993%**. Selected teacher matches decline by ~25. Monthly correct deltas Jan–Jul: +0/+3/+3/+3/+2/+1/+4. Diagnostic only.

### Registry-conditioned micro specialist

The strongest conservative structure-conditioned rotation/chop branch adds **39** positive entries while losing **30** selected teacher matches Jan–Jul.

The broader highest-scoring short-horizon branch adds **78** positives while losing **77** teacher matches, flipping 824/191,674 events. Monthly positive deltas: **-11, +20, +25, +4, +30, +7, +3**. Precision becomes **19.027%**. Mean after-cost +15s markout remains negative.

Critically, the broader optimizer's best rule does **not** require the new registry state; it collapses back to weak-S1 + adverse 250ms motion + quote-pressure reversal. Thus the registry has **not earned incremental directional authority**. Preserve it as context/pattern memory only.

A shallow regime-specific registry/micro classifier reached ~37% discovery/calibration precision but acted on ~9% of opportunities with <2% selected-teacher recall; classic trade-deletion precision inflation. Rejected as primary entry solution.

## Scientific interpretation

The evidence now separates:
1. **Eligibility** — R9-like minute/S1 event generation remains the high-coverage control.
2. **Structural ownership** — H1/M15 + persistent M1/M5 accepted levels describe pattern state, not reliable direction by themselves.
3. **Exact timing/direction** — sub-second/one-second path behavior remains the strongest incremental signal; broad use harms teacher alignment, so it requires pattern-specific proof.
4. **Lifecycle** — hold/exit changes winner conversion and future opportunity ownership but cannot rescue a poor entry population.

The old durable insight is preserved and sharpened: **entry eligibility, directional ownership, exact timing and lifecycle are separate states.** Structure should determine which proof sequence is allowed; lower-timeframe state determines the executable tick.

## MT5-reproducible architecture carried forward

1. `OnTick` updates exact Bid/Ask, spread and millisecond clock.
2. S1/S5/M1/M5/M15/H1 buffers close only after actual period completion.
3. Pivots confirm only after right-hand bars close.
4. Persistent `LevelState`: price, side, confirmation time, age, touch_count, sweep_count, accepted_close, last_interaction, consumed/reset.
5. R9-like detector emits unique `setup_id`; does not automatically own direction.
6. Router chooses CONTINUE / FADE / PENDING from regime + level state.
7. Exact tick proof: accepted-level retest/re-break or failed-acceptance/reclaim; no retroactive fill.
8. Cost/spread veto + one-open-position admission.
9. Secondary lifecycle selected only after proof state.
10. Rearm only after actual exit acknowledgement and genuine level/reset transition.

## Carry / reject

**Carry:** BETA025/026 eligibility; weak sub-second reversal as specialist hypothesis; persistent M1/M5 registry; H1/M15 context; CONTINUE/FADE/PENDING; exact tick proof; one-position chronology; secondary lifecycle research.

**Reject / do not restore:** quarantined P8/P9 economics; generic MTF voting; immediate structure-only direction flips; tested extra rearm; broad abstention classifiers; old fixed pullback depths; retrospective timestamps.

## Decision

**NO PROMOTION.** All mean executable markouts and tested lifecycle economics remain negative. BETA005 17-layer parity, full original Coinexx all-trade/rearm equivalence, and multi-broker execution parity remain unresolved. August SEALED.

**Next target:** pattern-specific dynamic proof engine:
- CONTINUE = accepted level -> bounded retest -> re-break/renewed impulse;
- FADE = first penetration -> failed acceptance -> reclaim -> micro structural shift;
- PENDING = unresolved first touch with deterministic expiry;
- lifecycle only after proof, with entry metrics weighted highest.

Reproducibility artifact in originating conversation: `BETA028_SALVAGE_REPRO_BUNDLE.zip`, SHA-256 `fcbb2ca69cc5fc9ebb878dfa56c37bb7550264bb347b21278cebb92ff23915d9`.
