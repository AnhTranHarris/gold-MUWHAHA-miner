# AR1 January R7 — Profit-First Rebuild, Source-Exact January Self-Proof, and Active-Control Certification Boundary

**XAUUSD HTF / Gold MUWHAHAHA Miner** · January 2026 historical research · 18 November 2026 research handoff.

**VERDICT: The profit-first observational engine and source-exact acceptance test PASS. An effective active account-risk policy has NOT been certified. Do not deploy R7 as an order-changing governor.** This release is not a report claiming a failed capital-protection mechanism is successful.

## 1. Owner-authorized procedure recovered from the complete conversation

1. Preserve the existing R9 SYNTH historical record of fixed entries, exits, 0.01-lot-reference net P&L/fees, realized balances, cycle identities and chronological source row order **without rebooking or removing trades**.
2. Use only original Coinexx REAL TickLogger Bid/Ask millisecond quote paths as measured intratrade movements. Do **not** use R9 synthetic intraday OHLC. The frozen S100 V2 remains fully unchanged.
3. **Select historical evidence first with AR1 Atlas R0**, not formula-first feature shopping. The full 27-family (23 atomic, four overlapping parent summaries), 10-S100-level, and 240 January risk witness zones provide targets and nearby protected controls.
4. The hard protected set is the **union** of individually profitable R9 trades and all legs of historically net-profitable complete cycles. The fact that some of those component legs individually lost money does not make them dispensable.
5. Reverse-engineer surrounding Coinexx real-tick neighborhoods: completed micro HA persistence, confirmed Fibonacci swing context, adverse/favorable movement, spread, quote intensity, cycle phase and prior closed account/loss context. No future bar/cycle/price input is permissible in online features.
6. Fit and test **only after mechanism discovery**. At every candidate signal, distinguish: causal risk detection; zero protected-trade interference; and **independent evidence of economically beneficial risk intervention**, including observed quote-side mark and broker fill uncertainty.
7. Test against all 27,980 original January trades, 21 daily Coinexx original gzip streams, all Atlas cells/witnesses and entire original account ledger. Missing quote intervals stay labeled unknown; no synthetic substitute prices invented. Fail-closed **action authority** remains disabled unless protection and genuine risk reduction both pass.

No full raw tick library was rebuilt. The prior validated optimized C++ January 1s/5s/15s/30s Heikin-Ashi/Fibonacci pre-entry feature scan was **reused**. This R7 study independently reread the 21 original Coinexx gzip streams with Python and produced only 5s/10s/15s small causal checkpoint summaries.

## 2. Protected-trade account economics (original R9 SYNTH accounting, not Coinexx executed profit)

| Cohort | Original positions | Original fee-inclusive recorded net |
|---|---:|---:|
| Individually net-profitable legs | 24,368 | (subset, not additive) |
| All legs of profitable complete cycles | 26,148 | (overlapping, not additive) |
| **Unique protected union** | **26,576** | **+$42,227.83** |
| Outside protected union | **1,404** | **−$707.01** |
| **Full January original ledger** | **27,980** | **+$41,520.82** |

Original opening booked account **$100.00**, ending booked account **$41,620.82**. There are 3,606 losing individual legs, **2,202 of which are protected companion legs in historically profitable complete cycles**. The 1,404 outside-protected legs represent a small booked-loss opportunity compared with the $42,227.83 protected net result. This is an asymmetrical profit-preservation constraint, not a generic loss-classifier problem.

## 3. Reverse-engineered January mechanisms BEFORE selecting action formulas

### 3.1 Intratrade adverse pressure is not failure in R9

The largest observed Coinexx fixed-window **peak-to-trough giveback** of protected January legs was **$28.05**, vs **$2.03** in the outside-protected cohort. By S100 tier and known first/second-leg phase, *none* of the outside-protected trades exceeded that stratum's protected maximum giveback. No increasing scalar DD or S100-utilization trigger can capture one of these outside-protected trades with zero protected collisions in this population.

| Coinexx observed S100 utilization | Protected trade legs observed | Outside protected trade legs observed |
|---|---:|---:|
| ≥10% | 7,972 | 226 |
| ≥25% | 925 | 5 |
| ≥50% | 110 | 0 |
| ≥75% | 24 | 0 |
| ≥90% | 7 | 0 |

Five/ten/fifteen-second chronological checkpoints deepen this finding: protected P95 givebacks approx **$1.56/$2.05/$2.57** vs outside-protected **$0.62/$0.85/$1.05**. Tightening intratrade losses to suppress the N-cycle cohort would preferentially interrupt profitable recoveries.

### 3.2 Loss-cycle labels and future recovery cannot be used as online knowledge

- **Row 18,126 (23 Jan, first leg):** original R9 leg **−$0.52**, followed by second leg **+$0.62**, net profitable full cycle **+$0.10**. This entire pair is protected. Its quote state can appear hazardous before the recovery leg exists.
- **Row 13,924 (20 Jan, first leg):** original R9 leg **−$0.52**, net negative cycle **−$0.52**. Distinguishing it at entry requires causal features, not retrospective `N1`/`C2` or the next leg's future outcome.
- The known historical frequency of nonprofitable complete cycles decreased across January. The R7 cycle-intensity model uses *only previously completed* R9 cycles ending strictly before a new entry. The family labels are never predictive inputs.

### 3.3 Causal measurement clock and spread reference audit

- Market features from earlier optimized C++ micro scan are strict before the **beginning of the original R9 entry second**. They do not inherit the earlier plus-one-second feature snapshot error.
- For an already-open position, cumulative risk checkpoints are at +5s, +10s and +15s, **only while the original scheduled position is still open**, from actual in-window Coinexx quotes.
- During R7 QA, a checkpoint MFE/MAE reference mismatch was caught: correct MFE/MAE are **BUY: Bid(t) − first observed Ask; SELL: first observed Bid − Ask(t)**, including the entry-spread mark. Peak-to-trough DD is computed separately from the liquidation-side price path. The temporary incorrect reference was discarded, **all quote files reread, all source outcomes retested**, and final MFE/MAE/DD/count parity assertions are exact across all 27,980 positions.
- The 33 original no-inside-quote windows remain in the dataset with unavailable Coinexx intratrade metrics, not zero risk.

## 4. January R7 derived candidate models — evaluation chronology

The January outcome classes are **UNIQUE protected union vs net-nonprofitable complete-cycle legs** (different from R5's individual losing-leg prediction). R7's completed historical 5/10/15-second snapshots include **65,802** observed checkpoint records. About 1,966 R9 trades have no such checkpoint; they are retained in the complete historical ledger and are not deemed safe.

To avoid fitting the action threshold to its test period, source events were divided by original January date:
- **Training:** Jan 2–15, 11,137 positions with a checkpoint.
- **Calibration:** Jan 16, 19, 20, 2,865 checkpoint-eligible positions. The action-proposal ceiling is greater than the **largest protected-position risk score in calibration**; no actual trade action occurs.
- **Held-out chronological self-proof:** Jan 21–30, **12,012** checkpoint-eligible positions, **11,750 protected** and **262 outside protected**.

| Atlas-derived candidate | Held-out average precision | Held-out ROC-AUC | Protected collisions at earlier-calibrated proposed action limit | Nonprotected signals |
|---|---:|---:|---:|---:|
| Coinexx/phase/size mechanism | 0.15795 | 0.87089 | 0 | 0 |
| **Joint micro Heikin-Ashi × confirmed Fibonacci × phase** | **0.18766** | **0.88000** | **0** | **1** |
| + causal prior nonprofitable-cycle intensity | 0.15615 | 0.86951 | 0 | 0 |
| Joint HA/Fib + causal cycle intensity | 0.19385 | 0.87953 | 0 | 0 |

The outside-protected held-out prevalence is only **2.18%**. The combined HA/Fib model's zero-collision, single-signal result clears a *minimum collision check*, **not** an account protection test. The four models are compared on the same strict later-January cohort. Models were developed during January research, so even these blocks are internal, not independent prospective proof. Never claim “zero collisions in all possible future paths.”

## 5. Mandatory quote-side economic stress of the sole held-out signal

The **one** earlier-calibrated held-out joint HA/Fib signal is original **R9 source row 15,855**, Jan 21, first leg, `N1__prior1_reverse` retrospective classification. Its original R9 booked outcome was **−$0.52**; its original scheduled entry/exit times remain unchanged.

The model first cleared its calibrated diagnostic limit **15 seconds after entry**:

| Original Coinexx REAL TickLogger liquidation-side first-entry-quote reference | Quote-side mark |
|---|---:|
| +5s checkpoint | −$0.47 |
| +10s checkpoint | −$0.43 |
| **+15s, first eligible model alert** | **−$0.94** |
| Last Coinexx quote inside original scheduled R9 exit window | **−$0.57** |

The +15s mark was **$0.37 worse** than the observed mark at the original fixed exit. These marks are quote-based diagnostics, **not guaranteed broker fills and not equivalent to the synthetic R9 booked P&L**. Consequently, even a correctly identified unsuccessful-cycle leg does **not** demonstrate beneficial early-close economics at that alert. This candidate cannot be certified as capital protection or promoted to an MT5 order-changing rule.

For comparison, retrospective calibration witness row **13,924** first cleared its model limit at +15s; it does not supply independent later-date effectiveness evidence.

## 6. Full January integration and enforced action gating

`04_ar1_profit_first_state_machine_and_acceptance.py` rebuilds a **profit-first, non-intervening account-risk observer** that carries all original trade/account/quote/family records and gives live-compatible `WATCH`/`UNKNOWN` risk states. The **execution action is locked** (`LOCKED_NO_INTERVENTIONS`) in every January row because no proposed intervention has passed *both* profit-preservation and economically beneficial protection.

Required action-gate certifications (all must pass):
1. **Exactly zero protected individual legs and protected profitable-cycle companions subjected to any trade action** on all 27,980 positions.
2. Selected action must correctly use only as-of information; a retrospective family/positive-cycle label is permitted solely for offline acceptance scoring.
3. Meaningful held-out benefit for **net-nonprofitable complete-cycle risk**, not merely successful loss classification or score rank.
4. Causal intratrade quote and spread reference validated, plus missing-tick proxy uncertainty and execution/slippage model where an actual trade-action policy would need them.
5. Account reconciliation and frozen S100 thresholds maintained; any cash transfer or changed account-balance convention would require independent owner approval.
6. No trade actions enabled in MetaTrader 5 or GitHub EA before certification.

R7 does **not** pretend that action disabled equals successful capital protection. The source-exact observer is correctly built and tested; the **requested active January capital-protection governor is not certified** because the one selective candidate does not demonstrate economic protection. This is a hard failure of the *active protection* acceptance test, not a success report.

## 7. Integrity receipts and reproducibility

- Python reread **7,699,274 original Coinexx REAL quotes** from all **21 original January** gzip files; 2,272,602 quotes belong to exact fixed R9 holding windows.
- All 21 original gzip SHA-256s agree with the previously pinned January R1 source receipt.
- Exact trade-level quote count, MFE, MAE and peak-to-trough DD checks pass **27,980 / 27,980** original positions; 33 zero-quote original windows retained.
- All **240 January Atlas source-witness lines** and **270 27-family × 10 frozen S100 level cells** are verified. The 23 atomic family rows partition the original population; four parent rows overlap and are never added.
- Original R9 $100 → $41,620.82 book, unchanged net, unchanged entry/exit/fees and S100 V2. No broker fills or intraday synthetic OHLC were invented.
- See `JAN_R7_FULL_MONTH_PROFIT_FIRST_ACCEPTANCE_AND_SOURCE_RECEIPT.json`, `JAN_R7_TICK_CHECKPOINT_SOURCE_RECEIPT.json`, and `JAN_R7_SELECTIVE_ACTION_REJECTION_AUDIT.csv`. All model scores/triggers are research-only views, not actual entry filters, alternative exits or rebooked P&L.

### Dependencies kept external to avoid storage waste

- [AR1 original Atlas R0](https://drive.google.com/file/d/175yPSkvCBsY6cW0DRtTisjEYaOK3nhAn/view)
- [January R1 source-verified base](https://drive.google.com/file/d/1pngujzYxewjUNn95uVtfgfOI0Cqk9kgU/view)
- [January R5 micro HA/Fib C++ and causal source](https://drive.google.com/file/d/1JPqefJIXQMvaKGQcbnPyjRqVRLIk9Dkf/view)
- [January R6 full integrated source account observer](https://drive.google.com/file/d/1YUXX0-GhewLLXHB44Gg_2E-CQIZrEOY7/view)
- [Owner frozen S100 V2](https://drive.google.com/file/d/1yOOFHp08kLx4Y0g6qGWgadGcqbB8fLSO/view)

**Research decision:** Reject destructive per-trade drawdown triggers; reject conversion of loss score into a stop. Preserve the zero-collision combined microstructure model as an **unapproved research diagnostic**. Do not certify active account-capital protection until demonstrated risk mitigation coexists with exact profit preservation under causal, source-exact testing. No reporting downgrade from `FAIL_UNCERTIFIED` to `PASS` simply because the software correctly produced a risk score.
