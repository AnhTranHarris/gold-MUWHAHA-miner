# BETA030 — State-aware quant model, strict tick causality, dual-path system validation

**Date:** 2026-09-29. **BETA lineage only.** `NO PROMOTION` / `NO MQL5 OWNER AUTHORIZATION` / `August SEALED`.

## Actual completed experiment, not claims of profit

Read the full report `BETA030_STATE_AWARE_QUANT_RESULTS_REPORT.md` in conversation reproducibility bundle `BETA030_STATE_AWARE_AI_REPRODUCIBILITY_BUNDLE.zip`, SHA256 **e8854e6925cbbbe2f26a28632a4ebdcffc949bbc434ad8e4e417719cc75f17d4**, 63 files (ZIP CRC PASS). The 7 original multi-million-row Dukascopy CSV.GZ market inputs are separately owned by the user and **NOT** in the zip. The bundle carries the complete actual Python execution/QA scripts, 7 E060 exact-source-ordinal event cohorts, 7 existing BETA028 structural-state NPZ, 7 historical **SELECTED** R9 teacher pair ledgers, 10 fitted model text files, month-resolved scorecards, four full ORIGINAL teacher-day results and SHA manifest. Never fabricate a link to the ZIP inside GitHub; retrieve the actual preserved attachment and verify its SHA.

**Inputs:** 57,527,562 ORIGINAL ordered Dukascopy XAUUSD Bid/Ask quote ticks, Jan–Jul 2026. R9-like independent E060 first-cycle control 191,674 opportunity events; valid +15s markouts 183,222. Exact event tick ordinals were **recomputed** from full raw sources in every month and independently matched cached source event order and returned markouts (0 ambiguities/changed outcomes in this cohort). Entry Buy Ask→Bid, Sell Bid→Ask, spread from actual Dukascopy quotes, additional assumed $0.02/roundtrip for 1oz fixed 0.01 lot. Research spread cap **$1.20** is NOT original Coinexx R9 25-point broker gate; no original full R9 EA exit-enabled rearm, fill parity, or native MQL5 test is claimed.

**Temporal partition:** Jan–Mar discovery/training (80,938 events), April **one-time calibration** chooses GLOBAL-only model and a `$0.20/oz` predicted-return advantage threshold; May–Jul freeze diagnostic. All months Jan–Jul previously inspected by prior chats: **May–Jul NOT pristine/blind OOS**. Gold Hunter V8 is owner-reported historical reverse-engineering inspiration only; no purported internal algorithm imported as truth. R9 REAL/SYNTH/OVERFIT are **separate historical reference feeds**, never live decision inputs. R9 SYNTH generated-tick result is not an achievable proof or PnL target on independent tick data. Historical Gamma/Alpha profits remain archived, not approved BETA ancestry. P8/P9/C27 economics and retrospective-timestamp results QUARANTINED.

## Actual tested high-level math

Input `X_t` = 26 previously source-reconstructed BETA026 at-decision quote/event features + 26 completed-bar BETA028 M1/M5 registry features + 7 newly causal 20-second observed-intrinsic-quote-shape features. Features 53–59 are (i) normalized ordinal-pattern entropy for 3-length sign/rank patterns of 20 observed 1s midpoint returns, (ii) 2 finite-window positive/negative two-sided CUSUM diagnostic sums (update: `S+=max(0,S+ + r/vol - 0.3)`, `S-=max(0,S- - r/vol - 0.3)`), (iii) sign-recross fraction, (iv) 20s displacement/travel efficiency, (v) empirical 5s/1s variance-ratio proxy, (vi) 1s vs 5s relative quote arrival count. Each anchored sample/return is no later than the actual source tick ordinal. These are **proxies**, NOT full BOCPD or fitted HSMM algorithms, and no live order-book volume is asserted.

`S_t` independent pattern/regime ownership: `ACCEPTED_EXPANSION` if already-accepted M1/M5 and prior eff5>0.3 and side-relative mid_5s>0.08; `FAILED_SWEEP` if prior sweep count≥1 and no accepted close; `ROTATION_CHOP` if prior efficiency15<0.16 or efficiency30<0.12 (overrides earlier); `UNRESOLVED_TRANSITION` otherwise.

For each `d ∈ {original_R9, inverse_R9}`: fit bounded shallow gradient-boosted trees `f_d(X_t)` estimating future **clipped-to-[-4,+4] after-Bid/Ask-and-fee +15s markout** from Jan–Mar. For each state also fit `f_{d,s}`. Candidate state-weighted inference
`U_{d,t}=0.60 f_d(X_t)+0.40 f_{d,S_t}(X_t)` versus global `U=f_d(X_t)`. This blend is a preregistered hypothesis, not a mathematical truth. On April the **GLOBAL-only** method was selected and one-sided direction flip used iff `U_inverse - U_original > $0.20` on the CURRENT observed tick; otherwise keep original. No SYNTH/OVERFIT scores or future timestamps enter the rule. **This direction classifier does not itself change the entry clock.**

Model hyperparameters in actual script: LightGBM regression `n_estimators=85, learning_rate=.035, num_leaves=12, max_depth=4, min_child_samples=750, colsample=.85, subsample=.85, reg_lambda=3, max_bin=96, random_state=29`. State experts: 65 iterations, 8 leaves, 250 minimum child samples. All code and serialized text trees are in ZIP. Binary-file ONNX and MQL5 numerical parity NOT certified.

## Explicit matched-base results

| Period | Parent +15s correct / valid | Global AI +15s correct | Regime AI correct | Selected paired SYNTH side+time parent→Global |
|---|---:|---:|---:|---:|
| Jan-Jul | 34,784 / 183,222 | **35,424** | 35,562 | **34,394→33,715 (-679)** |
| May-Jul (historically inspected, not pristine forward) | 13,650 / 80,165 | **13,702 (+52)** | 13,702 | **13,495→13,338 (-157)** |

May–Jul true unclipped executable +15s after-cost mean **-$0.65553 parent** versus **-$0.65611 Global**; **-$46.68 incremental modeled USD** across 80,165 marks, even though +52 outcome labels went positive. Day-block descriptive bootstrap over 79 calendar days (20k, seed 20260929) incremental USD CI **[-$337.84, +$238.95]**. A better +15s positive count is not itself better expectancy.

**Critical unselected whole ORIGINAL Coinexx logger check:** four complete days Jan02, Feb20, May20, Jul20 (5,105 original SYNTH and 6,192 original REAL entry markers): ±5s same-side SYNTH 1,022 **→1,012**, REAL 2,976→2,930. Reversals change direction but **not clock**, and show **no SYNTH teacher overlap gain** on all-original sampled events. Source server→UTC uses -2h Jan/Feb, -3h May/July, verified prior BETA024. Full 149-day all-unpaired teacher event ledger still outstanding.

**Complexity ablation:** disabling all seven added entropy/CUSUM/variance/quote-shape features yielded **13,702** May–Jul positives, EXACT SAME positive count as full 59-feature Global and four-regime mixture under fixed 0.20 threshold; no incremental complexity benefit. State expert mixture likewise does not outperform the selected Global positive count in May–Jul.

**Observed-entry proof lanes:** first sweep wait, weak-adverse wait, high-spread wait, and fresh continuation wait each execute on a real subsequent quote or cancel, NEVER retroactively. All have fewer May–Jul absolute positive 15s results and fewer selected teacher matches than the immediate AI control. This is a test of event-relative quote retreat/renewal, not a literal confirmed-level price retest.

**Whole lifecycle (shadow, one-open-position exact tick, NOT BETA015 funded):** 
- Jan–Jul L15: Parent 158,701 positions/32,833 wins/net **-$114,001.73**; Global 158,701/33,466/**-$110,606.99**. This is predominantly discovery period, NOT verified forward.
- **May–Jul L15:** Parent 70,269 positions, 13,007 winners/net **-$45,483.77**; Global same entries, 13,059 winners/net **-$45,542.76** (WORSE ~$59 despite +52 winners).
- May–Jul L30 $2 stop/$2 target: Parent -$39,918.36, Global -$39,918.29 (negligible); L45 stop/trail Parent -$36,280.10, Global -$36,308.28 (worse). Every lifecycle net remained negative.
- BETA015 daily soft/hard, $90k terminal floor, real marked-equity funded propagation NOT applied. These shadow PnLs are NOT feasible funded-account profits; do not inherit as a proposed EA.

**QA:** 126 NEW assertions PASS: all seven original source cohort identities, exact source ordinal, upper/lower bid/ask quote-side marked outcomes, replay control totals, no-future sampled shape **prefix invariance even with same-ms quote fixtures**, pending order no-retroactivity, training split, archive/auth state, four full teacher days, and reproducible nonblind day bootstrap. BETA005 entire 17-layer cached feature equivalence still INCOMPLETE. BETA015 funded guard NOT run.

## Reproducible public methods — source vs our implementation

- BOCPD Bayesian online change points **available as disclosed MQL5 method**, but BETA030 uses **finite-window CUSUM proxies only**: https://www.mql5.com/en/articles/23482 .
- Hidden semi-Markov duration-aware four-state market-regime filter **disclosed source design for XAUUSD M5**, but **NO fitted HSMM tested here**: https://www.mql5.com/en/articles/24460 .
- Ordinal-pattern *transition network* + permutation entropy **public source**, BETA030 tests only simple 3-point **histogram entropy**, NOT full transition-network irreversibility: https://www.mql5.com/en/articles/23451 .
- MQL5 structural swing/BOS/CHoCH source: https://www.mql5.com/en/articles/19365 ; context only.
- Label concurrency, proper purged CV important before any model promotion: https://www.mql5.com/en/articles/19850 and https://www.mql5.com/en/articles/20117 .
- MQL5 ONNX API (potential frozen-model inference when authorized): https://www.mql5.com/en/docs/onnx/onnx_mql5 ; OnTick coalescing https://www.mql5.com/en/docs/event_handlers/ontick ; historical CopyTicksRange https://www.mql5.com/en/docs/series/copyticksrange .

## Research decision and next falsifiable unit

**NO PROMOTION, no new MQL5 EA, August SEALED, approved_beta_ea=null.**
The screened model modestly changes short-horizon side and does not solve SYNTH **timing/trajectory** gap or profitability. Preserve BETA025/026 baseline and BETA028 registry. Do not auto-integrate this failed improvement.

**Next bounded research**: rather than simply add more indicators, implement a causal 3-action `ENTER_NOW / WAIT_FOR_PROOF / ABSTAIN` with *explicit opportunity clock and state-duration hazard*, outcome labels that use realistic per-tick stop/target/time barriers and MFE/MAE as OFFLINE labels only; compare expected return/net, positive count, teacher FULL original unselected matches, lost opportunities and BETA015 funded equity under genuinely chronological one-account replay. Candidate full BOCPD+HSMM must be trained without future regime labels and validated on a genuinely untouched future segment; August remains sealed until user explicitly authorizes opening. Gold Hunter V8 merely a secondary external search clue, not a verified algorithmic parent. Human approval required BEFORE official candidate MQL5 coding. 

**Static checkpoint provenance:** actual ZIP above; original monthly market quotes user-supplied separately. The presence of a GitHub explanation alone is NOT proof full source code/model bytes reside in the repository.
