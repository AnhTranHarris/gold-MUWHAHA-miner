# XAUUSD HTF R00 — 058A/059A original-source native-tick continuation receipt

**Date:** 2026-10-18. **Research:** ENTRY SIGNAL ONLY. **Disposition:** RESEARCH_ONLY, NOT_QUALIFIED, NO_FUTURE_UNSEEN_VALIDATION. This is an INDEX into intact original artifacts and full code/result arrays; not a condensed replacement for reports or governance documents.

## Binding untouched FULL originals (read originals on every restart)
- Report 1: https://drive.google.com/file/d/19IS6aelL4Sj9m2hnevkGWqlNkcMhqaCp/view
- Report 2: https://drive.google.com/file/d/1JJitSmvENPubAKD_f_HBxVKezgma8oDx/view
- Report 3: https://drive.google.com/file/d/1nPlaRXsQctmw5TP3lMvl9-pqHEXwCM9c/view
- Report 4: https://drive.google.com/file/d/1D5JxeJJTOaZPCkcqwlQ9jhJkh6hzRt9e/view
- Investor original: https://drive.google.com/file/d/1rSWeGBht_IvEWzS9gf5qIZprPIotuxvb/view
- GOV original: https://drive.google.com/file/d/1kS11NY0RRFaL0NQ-BxUc21u85Dej5VFq/view
- Source supersession: https://drive.google.com/file/d/1qElhwjYLxunB1D_whIC6EJOSY8cHZ3qa/view
- System governance original: https://docs.google.com/document/d/1f65dWnWa9AGGTKYoqQ_7rr28lQbx4EppQEGUUAMWW9U/edit
- Continuity law original: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/f9ca199d5c7627678b725c915e4c6eab279029da/research/htf_dual_ticklab/governance/CROSS_CUTTING_CONTINUITY_LAW_v1.2.md
- Handoff protocol: https://docs.google.com/document/d/1u1ClV5rT4M31aS2LxfgN1CBFFZkSH70_kYjmOwC1fmE/edit

## Live GitHub version targets independently checked at resumption
- Infrastructure `carson/htf-dual-broker-utc-alignment-v0.3` = `ca4b58aec597174b6f6d18ab2f36cba6836e4f4c`.
- Governance `carson/htf-handoff-emergency-v1.3` = `f9ca199d5c7627678b725c915e4c6eab279029da`.
- Read-only R9 `carson/mt5-r9-hybrid-gate-certification` = `8729a6345655a7b4ea31facc81982004ee2b8921`.
- New 058/059 research files here are **not claimed to be uploaded to GitHub** unless a separately verified code commit is recorded.

## Actual source-time and training mechanics
- EXACT source bytes checked SHA-256 **8/8** against `source_registry.py`. Original Jan/Feb/Jun/Jul independent Coinexx and Dukascopy `.csv.gz`; no third-party price data.
- Coinexx original export timestamp preserved in source, derived research UTC minus 120 minutes Jan/Feb and 180 minutes Jun/Jul; Dukascopy unchanged UTC.
- January per-broker fitting of 058 three-class LightGBM model for each +1s and +3s confirmation clock. 56 causal predictors: 43 cached original at-ARM features, four independent original specialist state emissions, nine newly captured source-native at-CONFIRM features. February-only parameter calibration and policy selection. June and July historical-transfer months ALREADY EXPOSED across prior studies.
- Exactly confirmed native observed source quote must be available at first tick at/after arm+1s or arm+3s, no more than 2s late; label first observed native quote at/after CONFIRM+30s no more than 2s late. BUY correct iff future signed midpoint price > 0.10; SELL vice versa. NEUTRAL and missing are WRONG. This is not order/fill outcome.
- Four prior specialist lifecycles preserve causal prior-event arm/confirm/reset code. 058 conditional expert policies and 059 stateful fast-defer-slow confirm clock are additional tested signal routers; neither may emit using post-decision label availability.

## Critical causal correction / quarantine
- Original R00-058 and R00-059 used `np.isfinite(d30)` in the decision-time emission validity gate. That is **future information**. Their original scores are quarantined and cannot be promoted. **Exact original source and output files were not altered.**
- R00-058A and R00-059A are additive versioned fixes: at decision time only the actual observed confirmation validity is consulted; missing future outcome counts as incorrect in scoring. 058A additionally recalculates February confidence thresholds using confirmation-valid events rather than the future-label presence. The January models and 16 native confirmation datasets were reused unchanged.
- A partial gzip/NPZ from a prior runtime timeout was detected through ZIP CRC, rederived from the original Dukascopy June source and replaced in the derived cache only. Integrity check against source reverified; original user raw data untouched.

## Corrected June/July evidence, independent broker-month reporting (no pooling into a fictitious account)
| Exact research method | Emitted source-native signals | Correct fixed 30s midpoint directions | Accuracy | Selection |
|---|---:|---:|---:|---|
| R00-040 archived | 1,231,388 | 546,059 | 44.345% | historical reference |
| R00-054 weighted-oracle control | 1,231,388 | 548,099 | 44.5107% | February selected original |
| R00-056 level-reclaim override | 1,231,388 | 548,924 | 44.5777% | **historical post-selection; NOT promoted** |
| R00-058A +3s exhaustion | 1,202,556 | 536,277 | 44.5948% | February-selected after causal repair |
| R00-058A +1s dual-horizon exhaustion | from separate original `R00_058_ALL_COMBINATIONS_SUMMARY.csv` | 543,591 | 45.1067% | **historical post-selection; NOT promoted** |
| R00-059A sequential fast-deferral consensus | 923,901 | 415,144 | 44.9338% | February-selected after causal repair |
| R00-059A all-fast historical | see `R00_059_COMPLETE_COMPARE.csv` | 544,627 | 44.4324% | predeclared control, NOT Feb selected |

The R00-058A corrected February choice meets 90% of original R9 SYNTH trade counts in **2,002 / 2,006 hourly windows and 108 / 110 UTC day windows**, with four genuine missing Dukascopy month-boundary hours / two days, as recorded in exact source R9 ledgers. R00-059A has the same hourly/day boundary result. The original correct counts compare diagnostic events against R9 SYNTH completed trades, not equivalently executed trade sequences.

**80% initial direction precision NOT REACHED.** No executable orders, holds/exits, P&L, broker-fill calibration, 0.01 lot feasibility, $100/$200 survivability, full-EA comparison, or unknown-month validation conducted. Missing/inconclusive metrics remain NOT MEASURED rather than passes.

## Explicit forward action / R00-060 design-only
1. Recover missing upstream R00-040/046 Python/model source lineage or keep affected claims blocked; retain all original 054-059 artifacts and source hashes.
2. Repair precise R9 matching UTC boundary hours using **existing separately authorized adjacent source files only** with source SHA verification and provenance, not fabricated quotes, or formally identify source-window infeasibility.
3. Develop a genuinely independent *event-onset detector* from native irregular-tick streams, with fresh causal ARM episodes not anchored to every existing five-second sample. Record actionability, all rejected events, quote-side spread/latency, confirmed M15/H1 states, session changes, and prospective calendar segmentation. Fit January, select February, test June/July as exposed, not OOS.
4. Test separate native tick-side first-passage and *label-time horizon stability* strictly as diagnostics alongside, NOT substituting for, the unchanged original 30s signed midpoint correctness definition. Test side-specific uncertainty/reliability. Use real-quote signal lifecycle, explicit per-expert ablations, and compare full per-hour/day/week/month correctly directed event capacity to R9 reference.
5. Once entry-direction research is acceptable, commission an independently validated shared-account arbitrated bid/ask executor; until then R9 profitability and investor net-performance goals are NOT MET / NOT TESTED, not implicitly discarded.

## Necessary files in preservation packages
- `R00_058_NATIVE_EVENT_CLOCK` — full original source parsers, models, original approved native confirmation cache files, quarantined pre-repair research results.
- `R00_058A_CAUSAL_REPAIR` — corrected full Python scoring engine, unchanged Jan model references, complete all-36-arm per-broker/month transfer, June/July event-level arrays, exact hourly/daily/weekly/monthly R9 selected ledger, negative scores, February selection and plan.
- `R00_059_TWO_STAGE_ORACLE` — quarantine original 30-arm 059 trial and intact code.
- `R00_059A_CAUSAL_REPAIR` — corrected 30-arm sequential causal router and frozen results / exact R9 hours/day/week/month / full native observations.
- `R00_060_NEXT_EXPERIMENT_DESIGN_ONLY.json` — never score/promote without an actual frozen design, source and environment verification, no changed target after the fact.
- `SOURCE_SHA256_8_INPUTS.json`, `COMPLETE_ARTIFACT_SHA256_MANIFEST.json`, the native-confirmed month archives and original-approved upstream source files on their original Drive locations.

**No authenticated full ChatGPT export is held; conversation continuity is evidence artifacts, not asserted verbatim historic transcripts.**
