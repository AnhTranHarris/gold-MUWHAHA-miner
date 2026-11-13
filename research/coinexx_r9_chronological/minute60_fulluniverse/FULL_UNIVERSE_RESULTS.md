# R9 60-second full-universe causal research continuation — 2026-11-13

**Decision: ALL MODEL FOLDS FAIL owner's ROC-AUC threshold 0.75. No promotion to EA, no claim of profitable trading.**

## Source-exact provenance

- Frozen original R9 source-ordered Coinexx XAUUSD January–September 2026: **72,129,347 original quote rows**; monthly raw SHA256s preserved in old baseline receipt and new full receipts. **303,934 frozen R9 actual-source entry opportunities**, 269,704 (88.74%) complete causal 60s history, 34,230 past-only 60s unavailable (kept as NaN, with frozen R9 context).
- **All 8,189 previously published pilot observations** agree on entry timestamp/ordinal, all 103 derived HFT features and all three future first-passage labels; source quotes at equal millisecond retain original source ordinal; old baseline files and EA unmodified.
- Original bars are **never reconstructed**. Past-only 120×500ms grid of last observed quote for each R9 entry, age-limited to 2,500ms, including as-of ordinal clamp. Missing full history retained, not silently dropped. 14 frozen causal R9 source entry features +103 existing HFT summaries +28 experimental regime/path features.
- Label: original R9 side: favorable executable liquidation move **+$0.50 quoted gold price before adverse −$0.30**, observed within **5/15/30 seconds**; future quote sequence only computes y, **never X**. Extra modeled **$0.20 gold PRICE** cost, NOT verified US-dollar brokerage commissions / fills / slippage. For models, NO_BARRIER is a negative outcome, tiny CENSORED excluded. Applies to hypothetical fixed first-passage policy, not existing EA on-policy economics.
- Five successive chronological folds Jan–Apr→May, Jan–May→June, Jan–June→July, Jan–July→Aug, Jan–Aug→Sep. One equal month held out across each model family; 60s chronological purge. All evaluation months previously exposed at project level: **retrospective development checks**, not pristine post-September certification.
- The original canonical MiniROCKET package was not installed; prior 8,189-sample fixed-kernel PPV fallback failed and remains archived. **No claim that full-universe MiniROCKET was trained.** This continuation expands the 60-second HFT and nonlinear state models to the entire 303,934-candidate universe. Do not substitute or retroactively erase previous failed PPV receipts.

## Full-universe training: 20 matched evaluations

Model families: R9 context (14 features), 60s HFT (117), HFT plus 28 causal volatility/session/path descriptors (145), and a larger boosted-tree capacity control (145). Constant 96-tree/15-leaf conservative LightGBM vs 180-tree/31-leaf capacity control, max_bin=63, force_col_wise=True, identical specifications across all five folds. These compute-bounded resource settings replace *this continuation's* interrupted first local pilot fit, not the original frozen 8,189-sample research settings. All evaluation folds remain exposed.

| Held-out month | R9-only 14 | 60s HFT 117 | HFT + 28 state | Higher capacity |
|---|---:|---:|---:|---:|
| 05 | 0.5712 | 0.5766 | 0.5762 | 0.5757 |
| 06 | 0.5705 | 0.5753 | 0.5753 | 0.5744 |
| 07 | 0.6011 | 0.6086 | 0.6100 | 0.6062 |
| 08 | 0.5849 | 0.5929 | 0.5924 | 0.5903 |
| 09 | 0.5855 | 0.5936 | 0.5937 | 0.5935 |

**Best: 0.6100 (July). 0 of 20 model/folds pass 0.75.** Larger model trained AUC 0.6577–0.6797 while heldout stays ~0.57–0.61. Extra nonlinear state features add almost no marginal information. The data do not establish a mathematical upper bound on predictability, only an empirical ceiling for these specific model/target classes.

## Predictive-horizon and economics diagnostic

Same 117-feature causal 60s model independently trained at each first-passage horizon. These are DISTINCT targets, so differences are not direct model quality improvements on one task:

| Month | 5 sec AUC | 15 sec AUC | 30 sec AUC | 5 sec positive rate |
|---|---:|---:|---:|---:|
| 05 | 0.6644 | 0.5766 | 0.5400 | 7.27% |
| 06 | 0.6628 | 0.5753 | 0.5394 | 8.20% |
| 07 | 0.7043 | 0.6086 | 0.5644 | 6.35% |
| 08 | 0.6993 | 0.5929 | 0.5520 | 7.09% |
| 09 | 0.6885 | 0.5936 | 0.5468 | 6.82% |

The 5-second target is more discriminating (max 0.7043) but positive only ~6%–8% of opportunities. Target +0.50 before -0.30 is hard for the source-side liquidation price at this horizon. With preceding frozen training score threshold at 80th percentile:

| Month | 5s AUC | Top prior-training 80% score: count | Hit rate | Quote-price expectancy |
|---|---:|---:|---:|---:|
| 05 | 0.6644 | 997 | 18.76% | -0.4074 |
| 06 | 0.6628 | 1,343 | 18.84% | -0.4152 |
| 07 | 0.7043 | 888 | 23.54% | -0.3523 |
| 08 | 0.6993 | 1,933 | 19.97% | -0.3989 |
| 09 | 0.6885 | 1,874 | 18.30% | -0.4159 |

Every retained subset has **negative modeled quote-price expectancy**, with low retained coverage (~2.7–6.2% here). Filtering 20% risk in separate 1s stop-hazard diagnostic retains ~69–88% of opportunities and AUC ~0.656–0.668, but still has negative economics; neither is a viable strategy.

## Primary explanatory findings

1. **Execution geometry consumes the adverse buffer:** Median quoted entry spread **$0.20 gold price** (p5 $0.18, p95 $0.22); compared with the research adverse barrier **$0.30**, only about **$0.10** additional adverse quote displacement beyond the entry spread is needed. Favorable **+$0.50** liquidation move needs roughly **+$0.70** favorable quote movement from the pre-entry mid reference under constant $0.20 spread. These are approximate mid-based illustrations; executable Bid/Ask flags and spread changes are source of truth. Exactly **103,066/303,934 (33.91%)** of entries stopped within one second; **231,131/303,934 (76.05%)** hit adverse first within 15s. This structure dominates label economics.
2. **Target labels shift by calendar regime:** fixed 15s favorable-first fraction rises to 23.24% in March, falls to 12.45% in May. Prevalence drift alone does NOT mathematically force AUC down, but it affects calibration and indicates changes in conditional dynamics.
3. **Missing history is non-random:** 34,230/303,934 entries fail 60s quote freshness. Their positive-label rate differs from complete-history entries. Explicit missingness accounted for in each OOS model.
4. **Complete source lacks executed order flow:** across **72,129,347** raw ticks, Last !=0 **0**, volume !=0 **0**, volume_real !=0 **0**. Quote flag **134 occurs 67,745,917 (93.92%)** of rows, 130 3.05%, 4 3.03%. These are quote revisions, NOT actual aggressor flow, market order size, bid/ask depth, or institutional executions.
5. **500ms resampling suppresses sub-500ms sequence detail:** original raw ticks contain order within equal milliseconds and subsecond quote arrivals; the 120-bin representation collapses dozens of quote changes per bin. Especially for 5s first-passage behavior, event-time waiting times and exact revision bursts may contain useful *unmodeled* information. This is a concrete available-data representation gap, not evidence of hidden alpha.
6. **Increasing estimator capacity does not rescue discrimination:** capacity raises train AUC, with future AUC flat/slightly worse. Pointing to underfitting alone would be unjustified; multiple selection and regime-specific memorization remain concerns.

## Proposed next mechanisms (unapproved, not trained)

**Priority A — execution-normalized barrier and dynamic action utility.** Instead of fixed gross +0.50/−0.30 irrespective of spread, define distances as functions of as-of spread, noise-robust local volatility and observed adverse excursion; evaluate BUY and SELL counterfactual quotes and WAIT at each eligible time, including trade occupancy. A stop must not sit immediately inside normal spread-induced mark-to-market. Suggested *research* forms: stop gap \(L_t=a \cdot s_t+b\hat{\sigma}_{1s,t}\), favorable gap \(G_t=c \cdot s_t+d\hat{\sigma}_{1s,t}\); optimize on earlier train months with fixed withheld future month, not on already exposed test labels.

**Priority B — exact event-time hazard rather than 500ms sampled path signatures.** Keep all original raw quote intervals and flags (e.g., 1,5,25,100,500ms); estimate as-of **excitation, signed revision cascades, waiting-time entropy, quote flip/reversion** and competing conditional hazards of BUY/SELL first passage. No fake signed order volume. Preregister feature groups and compare marginal AUC/coverage on equal dates.

**Priority C — collect genuinely missing market data only if needed.** L1 Bid/Ask **sizes** at source dealer, trade-side aggressor volume/prints, L2 depth, and actual dealer order fills/commission/latency. They are absent from these nine files; formulas alone cannot reconstruct them. External indices deliberately out of scope per owner. Do not ask for another Coinexx export.

**Volume objective:** maintain full original candidate universe for denominator. Require both above-0.75 AUC (target >0.80) *and* enough after-cost positive opportunities at a predeclared meaningful retained rate (e.g. >=25% of this universe), plus independent full-system risk/drawdown. A higher AUC on a rare stop hazard or selective easy subset does not satisfy that requirement by itself.

## Reproduction and integrity

Original source modules (the prior frozen ones), prior source receipts, nine month derived features, full results, self-contained numerical tests and exact schema are saved in this continuation. `PYTHONPATH` includes previous frozen `minute60_firstpassage/src` for original immutable first_passage and HFT operators; `full_extract.py` imports them rather than rebuilding. Execution tests are **16 local passed**, full-data parity with old sample **8,189/8,189**, all five 117-feature fold models serialized and score-replayed at exact matching AUCs, all original gzip hashes checked, and quote fields fully audited. GitHub CI status must be separately verified; do not infer success from local tests. Raw source never overwritten.
