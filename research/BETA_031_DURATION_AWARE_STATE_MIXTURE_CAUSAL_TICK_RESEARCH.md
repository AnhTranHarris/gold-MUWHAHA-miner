# BETA031 — Duration-aware state mixture: an interpretable AI bridge test

**Date:** 2026-09-29. **Status:** measured research only, **NO PROMOTION / NO MQL5 EA / NO FUNDED BETA015 SIMULATION**. Branch `beta` remains independent; BETA030 = parent research comparator. August 2026 **SEALED**.

## Owner mission and scientific partitions

Build two independent but interactive optimization tracks: (A) MICRO = absolute correct entry count, quote-executable entry accuracy, original R9 SYNTH/OVERFIT clock and action correlation (retrospective teacher **evaluation only**); (B) integrated portfolio = one-position ENTRY/HOLD/EXIT/PROFIT, gross-loss, drawdown, trade velocity, opportunity suppression and BETA015 funded survival. ENTRY remains the more important discovery axis, with no allowable material deterioration in system integrity or capital economics. Historical R9 REAL/SYNTH generated tester populations and independent Dukascopy feed must never be equated.

The owner describes Gold Hunter V8 reverse engineering as Gold MUWHAHA Miner genealogy. This is only an **UNVERIFIED SECONDARY search lead**. No opaque vendor logic, unverified performance or hidden order-flow information was used.

Data: the previously inspected January–July 2026, **57,527,562** original Dukascopy XAUUSD Bid/Ask quote ticks, exact source-order/observed tick fills. Parent first-cycle E060 model is a **relaxed $1.20 Dukascopy-spread research comparator**, NOT original Coinexx R9 25-point spread parity and NOT original full EA rearm. January–March discovery/fit, April threshold calibration, May–July frozen retrospective diagnostic: **NOT pristine OOS**, because these months had been repeatedly researched. No August access.

## Why a custom state model?

BETA030 established that a 59-variable, state-gated gradient-boosted quant model (26 quote/micro; 26 causal structural-event registry; 7 path-shape/CUSUM/variance/quote-intensity) produced only **+52** May–July after-cost +15s positive signals, **-$46.68** incremental summed markouts and **-157** historical selected SYNTH matches; the seven new advanced shape descriptors produced **no extra absolute positive count** at its fixed test threshold. On four full original logger days, SYNTH same-side ±5s went 1,022 -> 1,012. Complexity alone did not repair real vs synthetic event-clock differences.

BETA031 instead tests whether a fully specified duration-conditioned linear mixture can act as a more interpretable direction owner. Input `X_t` has the 59 strictly observed source-time features from BETA030, plus four history-derived variables:
1. `log1p(event-sampled regime_age_seconds)` (resets on changed state or prior R9 event gap >180s);
2. `log1p(min(previous_event_gap_seconds,180))`;
3. `state_changed` binary at this event;
4. `S_s(a)` = historical empirical survival P(completed state event-run duration >= current event-sampled age), from January–March; clipped [.05,1].
**Important precision:** these are **event-sampled semantic-regime age proxies**, NOT continuously observed true tick-time regime duration and NOT a full hidden semi-Markov posterior. The length samples' per-month final runs include censored month tails; retrospective source research does not qualify a formal survival model.

Offline fit target: `y_t=clip(R_inverse_15s - R_original_15s,-4,+4)`, where side returns are from later observed executable Ask/Bid quote +$0.02 round-trip cost. Future returns are **train-only labels**, never inputs to live decisions. Common fitted standardized Ridge with `alpha=300`, global expert `G_t=bG+SUM_j wGj z_j`, separate four state experts `L_{s,t}=b_s+SUM_j w_sj z_j`.
The *explicit tested formula*:
```text
lambda = clip(0.10 + 0.65 * S_s(age) - 0.35 * state_changed, 0.05, 0.75)
DeltaUtility = (1-lambda)*G_t + lambda*L_{s,t}
if DeltaUtility > $0.20/oz: action = inverse(original R9 side)
else:                         action = original R9 side
Entry = current ORIGINAL observed Dukascopy tick Ask (buy) or Bid (sell)
```
Threshold 0.20 selected on April. Never change order timestamp or fill backward. No dynamic-proof delay implemented by BETA031. The fitted model, 63 feature order, per-state standardization and all estimated coefficients/training historical duration CDF are in exact-size `BETA031_MT5_MANIFEST.json` preserved in the local bundle; output source SHA in hashes below. A pure numeric Python implementation can reproduce it without LightGBM runtime; MQL5 `OnTick` deployment remains **unapproved**. For real broker inference, handle millisecond source order, missed tick coalescing/CopyTicksRange, completed-bar timestamps, quote-age and spread, broker point and 0.01-lot commission.

### Numerical validation and caveat

BETA031's 28 independent unit/aggregate tests passed. Separate export-manifest arithmetic parity test imported the JSON manifest from disk and compared the manual `(X-mu)/scale -> global/state regression -> duration lambda -> flip` route against its fitted Python predictor. Jan, Apr, May, Jun, Jul = **0 max prediction error, 0 action disagreements** across tested event vectors. This is **Python JSON/numeric export parity**, not native MQL5 compilation/forward parity, and NOT BETA005 17-layer cache certification.

The originally described Jan–Mar 'leave-one-month-out' ridge alpha calibration has a methodological limitation: its reference `S_s(age)` distribution was constructed once from *all* Jan–Mar durations, **including the CV holdout month**, so it is NOT a fully isolated duration-feature cross-validation. It does not use May–Jul in the final model fitting, but its alpha CV should be repaired fold-locally before any formal promotion. State duration is event-sampled and run durations have month-end right censoring. No direct full HSMM/BOCPD was tested in this unit.

## Original Dukascopy entry observations

| Window | Parent +15s positive / eligible | BETA031 +15s positive | Parent after-cost markout sum | BETA031 after-cost markout sum |
|---|---:|---:|---:|---:|
| Jan–Jul | 34,784 / 183,222 | **35,397 (+613)** | -$132,571.24 | **-$130,675.86** |
| **May–Jul frozen, historically inspected** | **13,650 / 80,165** | **13,788 (+138)** | -$52,550.62 | **-$52,470.30 (+$80.32)** |

All net markout sums remain negative. Day-block bootstrap across 79 May–July calendar days (20k draws) is descriptive: extra positives **[+42,+238]** at 95%, dollar delta **[-$251,+$405]** at 95%; this is not external generalization.

### Integrated one-position May–July shadow (different future opportunity sets)
| Lifecycle | Parent positions/wins/net | BETA031 positions/wins/net | Net difference |
|---|---|---|---:|
| 15-second expiry | 70,269 / 13,007 / -$45,483.77 | 70,269 / 13,129 / -$45,449.98 | +$33.78 |
| 30-second $2-stop/$2-target | 61,741 / 15,780 / -$39,918.36 | 61,724 / 15,871 / -$39,812.64 | +$105.72 |
| 45-second $2-stop, $0.60 activate / $0.35 trail | 55,734 / 20,526 / -$36,280.10 | 55,723 / 20,608 / -$36,170.51 | +$109.59 |

All net negative. This is one-position **shadow** replay, not capital-feasible funded account P&L, equity DD certification, MT5 spread/slippage parity or BETA015 risk-governed trading.

### R9 SYNTH teacher correlation — critical failure

Previously-selected 165,630 historical REAL↔SYNTH same-minute/same-side ordinal pair cohort (NOT all 219,342 SYNTH entries): Jan–Jul parent 34,394 same-side ±5s vs **BETA031 32,957 (-1,437)**; May–Jul parent 13,495 -> 12,885 (-610).

Four full unselected original Coinexx logger days, 2026-01-02/02-20/05-20/07-20, containing 5,105 original SYNTH events and 6,192 REAL: matched original SYNTH same-side ±5s **1,022 -> 951 (-71)**; REAL **2,976 -> 2,812 (-164)**. Model flips direction but holds event timestamp identical: cannot improve near-time-clock match. Therefore **NOT** a recovered R9 SYNTH action/clock advantage. Original OVERFIT hindsight action labels never used for fitted training or runtime.

## Reconstructible public methods, with honest scope

- Hidden Semi-Markov Models for Duration-Aware Regime Detection in MQL5 (published 2026-09-28): https://www.mql5.com/en/articles/24460 . Shows full duration-explicit MQL5 forward filter and Python-fit JSON manifest; **BETA031 is simpler empirical state-age blending, not this HSMM**.
- Bayesian Online Change-Point Detection: https://www.mql5.com/en/articles/23482 . BOCPD detects state change but **does not supply directional BUY/SELL by itself**; not yet implemented in BETA031.
- Open-source market structure break/retest: https://www.tradingview.com/script/d2j00089-Market-Structure-Break-Retest/ . Context & sequence, not performance evidence for this EA.
- MQL5 official ONNX: https://www.mql5.com/en/docs/onnx/onnx_mql5 (alternative to explicit linear manifest, no production ONNX artifact), official tick events https://www.mql5.com/en/docs/event_handlers/ontick .

## Reproducibility

`BETA031_DURATION_AWARE_MOE.py` original SHA-256 `df91d2f091f880dedf0a4b05f4804f39c7b970ed8d520ba81dad87e67c31b7c9`.
`BETA031_DURATION_AWARE_MOE_RESULTS.json` SHA-256 `b862c9850e91e20ff81b5f2a412340fcde048ec8befcd30c10fd935fcd969221`.
`BETA031_MT5_MANIFEST.json` SHA-256 `98a892d1776f33558be20dce4dcbea5116c3b8607cb09f823ce082ba1861056b` (322,750 bytes including duration ECDF).
`BETA031_MANIFEST_NUMERICAL_PARITY_QA.json` SHA-256 `20a2be10d1aa8b8a2665ebbee6140811afd01afc2bd2484a772bc9890dbeda92`.
Full BETA030 input/cache/derived tick-source lab: `BETA030_STATE_AWARE_AI_REPRODUCIBILITY_BUNDLE.zip` SHA `e8854e6925cbbbe2f26a28632a4ebdcffc949bbc434ad8e4e417719cc75f17d4`; 63 files. BETA031 delta code/model/results/full original 4-day audit/parity script: `BETA031_STATE_AWARE_AI_RESEARCH_BUNDLE_WITH_PARITY_QA.zip` SHA **`ad8255ced778eebda227933f70c447ffc829d2fd2476b3ddc7b83d01a50a6458`**, 22 files; ZIP CRC verified. Neither includes user original full market compressed quote files, and neither is uploaded to GitHub through this note. Keep separate blessed source identities; do not fabricate same-feed native Coinexx parity.

## Decision and future falsifiable target

**NO PROMOTION.** The custom model is not sufficient to reproduce R9 SYNTH or OVERFIT. Do not resurrect hindsight clocks, Gamma_2 profits, P8/P9 values, or fabricate true order flow from quote-only Dukascopy data. Next priority (1) full original logger unselected 149-day R9 REAL/SYNTH teacher recall, (2) actual **clock/actionability** model with first later observed tick, (3) formal BOCPD or HSMM duration survival **independent router** vs empirical survival, (4) secondary conditional HOLD/EXIT early-failure vs runner only after entry, (5) full source feature parity BETA005 and BETA015 one-account funded risk, (6) genuine untouched forward data with owner August authorization. Owner explicit approval before any official MQL5 EA code. Until then, carry only source-reproducible Python research states.


## Independent audit addendum (same-session, no parameters retuned)

After the initial BETA031 model was fit, two further proof checks were executed:
- **7/7 months** independent `BETA031_PURE_MANIFEST_OWNER.py` versus the fitted `BETA031_DURATION_AWARE_MOE.py` action signals: **0 differences**, maximum floating-point prediction error **0.0**; 14 strict parity assertions passed (two per month). The GitHub code blob for `research/experiments/BETA_031_PURE_MANIFEST_OWNER.py` read back as **`d5c0e3dafb06946ae1cdb5184644a2e6631b4c21`**, matching the *actual local source's* `git hash-object`. This certifies serialized JSON model formula *arithmetic* only, not tick-feature rebuilding or MQL5 compiling.
- **Jan–Mar ridge leave-one-month-out duration-leakage repair audit** recomputes the empirical duration survival reference from each fold's TWO training months only. Grid alpha 3,10,30,100,300; minimum MSE is still alpha **300**. Note the final BETA031 coefficients were not refitted by this audit and month-end censored runs remain a limitation.

Local verification artifacts: `BETA031_PURE_MANIFEST_OWNER_QA.py`, `BETA031_PURE_MANIFEST_OWNER_QA.json`, `BETA031_DURATION_CV_LEAKAGE_REPAIR_AUDIT.py`, `BETA031_DURATION_CV_LEAKAGE_REPAIR_AUDIT.json`. Source hash proof: `research/experiments/BETA_031_PURE_MANIFEST_OWNER.py` SHA256 `8b6946b22a1fcab117168a049cb857e542cced1a0ffcc0294fe6c3deb6693a7f`; fold repair script SHA256 `14dee79c396da3e4a7efe03cc7f7577912479e03d769ef29f1a0eab8164cf3a7`. Full **27-file BETA031 verified bundle** `BETA031_STATE_AWARE_AI_RESEARCH_BUNDLE_VERIFIED.zip` SHA256 **`7873ed9d6eed1f8c6f075ec5ecb914f6d5b512cee61d7807e4f25db4b520e577`**, 95,329 bytes, compressed CRC PASS, carries report, full fit script, source refs, coefficients/complete native-export manifest, original logger sample audits, independent formula parity and CV repair artifacts. Large 7-month market tick files absent by design.

Do not confuse the 28 original BETA031 QA assertions with 14 additional formula-readback assertions or 5-month earlier manual parity assertions: they check different scopes, not a single independent comprehensive certified test.
