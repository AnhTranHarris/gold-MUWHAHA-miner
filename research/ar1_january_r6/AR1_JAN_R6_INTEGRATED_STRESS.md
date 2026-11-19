# AR1 January R6 — Integrated account-risk observational policy and source-exact full-month stress test

**Date:** November 18, 2026. **XAUUSD HTF / Gold MUWHAHAHA Miner**  
**Status:** Integrated observational risk engine completed and January self-proof passed for source and risk-state semantics. **Not** an approved trade-altering governor, tested brokerage execution or independently certified capital-protection policy.

## 1. Owner mandate fulfilled within the historical observation boundary

This release **integrates** January R5's stronger strictly pre-entry loss predictor into the complete January AR1 account-risk research framework instead of treating it as a standalone classifier. It tests the integrated risk states against **all 27,980 original R9 SYNTH fixed trades**, read-only, while replaying **all 7,699,274 original January Coinexx REAL TickLogger quotes** using Python. The source-exact within-hold quote count is **2,272,602**. All 21 original January gzip source hashes match the source manifest. No R9 trade, price source, original net P&L, original booked balance, fixed S100 tier, account fee, entry or exit was changed. It does **not** silently substitute R9 synthetic intraday prices for actual Coinexx quotes.

**Non-negotiable source contract:** R9 SYNTH exclusively supplies historical entry/exit seconds, recorded fee-inclusive trade results, side, cycles/legs, and original $100-start chronological **booked** account ledger. Coinexx REAL TickLogger exclusively supplies true observed millisecond Bid/Ask quote chronology, and true observed quotation-side MFE/MAE, giveback and spreads. These source roles are not combined into an executable Coinexx account-equity curve. The owner-frozen S100 V2 gap ladder is unchanged: `$100→$4`, `$700→$5`, `$1,100→$9`, `$16,200→$11`, `$19,900→$14`, `$27,500→$15`, `$29,300→$23`, `$33,200→$24`, `$33,300→$30`, `$340,100→$74`.

## 2. Integrated quantitative policy: six causally distinct research channels

### (i) Original R9 booked-capital stress

For previous *originally completed* fixed exits at time `t`, `B_t = 100 + Σ R9_net_exit_before(t)`, `H_t=max_{u≤t} B_u`, `booked_drawdown_pct(t)=100*(H_t-B_t)/H_t`. A rolling `GrossNegativePnL_Δ(t)=Σ_{original exits in (t−Δ,t)} max(0,−R9_net)` is maintained at Δ=1/5/60/240/1,440 minutes. The prior consecutive losing-exit run is tracked separately. These are realized **R9 SYNTH** history, not real Coinexx broker outcomes.

### (ii) Strict pre-entry losing-trade risk

Use the January R5 Atlas-first fitted nonlinear model `p_losing_leg(t | causal features known strictly before entry)` with **105 original microstructure, HA/Fibonacci interaction, prior booked-account and R9 lifecycle features**. Earlier-trading-day-trained predictions exist for only **21,069** January trade entries; **6,911 early entries have no prior-January-trained predictor** and are explicitly `JAN_WARMUP_NO_CAUSAL_JAN_TRAINING`. The R5 full-January fitted diagnostic score is *not* used to replace the unavailable prior-day scores in these early entries. January R5 predictive source code, parameter archive and model receipts remain an immutable, exact versioned dependency, not recreated here.

### (iii) Quote-side intratrade pressure and original S100 utilization

BUY liquidation state is current Coinexx Bid; SELL is `−Coinexx Ask`. At timestamp `t` within the original fixed R9 source quote window: `D(t)=max_{u≤t}(quote_side(u))−quote_side(t)` and `U(t)=D(t)/G_S100(original_R9_booked_balance_at_entry)`. `U=25%,50%,75%,90%,100%` are **observational state boundaries**, not orders. The full January Python quote replay verifies first-crossing timestamps, chronological quote counts, MFE, MAE and DD for every trade against archived R1/R5 sources. **Zero mismatches**; zero observed full S100 touches.

### (iv) Coinexx market-state and combined advanced structural indicators

The frozen R5 model uses completed Coinexx-derived 1/5/15/30-second Heikin-Ashi, delayed-confirmed Fibonacci swing geometry, preceding quote displacement/spread/activity, and explicitly combined lifecycle/swing/recovery interactions. R6 retains those predictive features and exposes the relevant observable HA, Fibonacci and microstructure state variables in the integrated ledger. It **does not refit R5 or invent a new metric that bypasses Atlas-led historical research**.

### (v) Incomplete Coinexx evidence and distributional proxies

Retain all **33 original fixed windows without an inside quote**, plus **195 quoted but non-strict timing cases**. The historical risk engine returns an explicit source-quality flag, never fictitious observed MAE/DD. A separate strictly prior-exit, prior-source-quote conditional distribution proxy uses past Coinexx observed intratrade DD/S100 ratios, same leg and tier where sample permits; otherwise leg-normalized/global historical fallback. Calibration is declared unavailable if fewer than 100 earlier strict observed paths. Its output is **an uncertainty range**, not reconstructed tick prices or a stop touch.

### (vi) Original account and operational integrity

There are **21 same-second prior-exit/next-entry ambiguities** where the prior realized outcome is not assured to have been known at the new entry second. R5's predictor flags that ambiguity; R6 preserves the original recorded booked balances while keeping the ambiguity status. All states have `trade_action=NONE_OBSERVATIONAL_ONLY`: no entry filter, force close, revised fee/lot, alternative exit or shadow equity book.

## 3. January self-proof: original source custody and complete account history

| Audit | Result |
|---|---:|
| Original R9 positions retained | **27,980 / 27,980** |
| Original individually profitable/negative/zero | **24,368 / 3,606 / 6** |
| Original R9 positive completed cycles / all their component legs | **18,413 / 26,148** |
| Original adverse legs contained inside net-positive cycles | **2,202** |
| Original R9 booked account | **$100.00 → $41,620.82**, **+$41,520.82** |
| Independently recomputed largest original booked drawdown | **$3.40**, max percentage **0.5409%** |
| Original Coinexx January quotes read and source-hash verified | **7,699,274, 21 files** |
| Coinexx observed quotes inside fixed source R9 windows | **2,272,602** |
| Python original count / MFE / MAE / DD / event timestamp discrepancies | **0** |
| State-machine original-book / source S100 tier discrepancies | **0** |
| Source-exact no-quote / nonstrict quote windows | **33 / 195** |
| Original R9 consecutive losing episodes / longest length | **3,338 / 4** |
| Observed S100 25% / 50% / 75% / 90% touches | **930 / 110 / 24 / 7** |
| Observed complete S100 gap touches | **0** |
| Owner Atlas witness rows / 27 family × 10 tier reporting cells | **240 / 270** |
| Independent runtime-state unit tests | **6 passed / 0 failed** |

The 27 reporting lines are **23 mutually exclusive atomic families and four overlapping A/B/C/D parents**, never added together. January has nine observed S100 gap levels; `$74` is correctly zero-population. All N1/N2 net-nonpositive-cycle patterns and profitable companion legs remain in their historical records.

## 4. January R5 predictive model rechecked inside full AR1

Strictly prior-day-trained January loss probabilities are evaluated only on the 21,069 available later-date trades. These *same predictions* were carried unchanged into R6 and reconciled against original R9 results. R6 did not train on this test population or regenerate R5's coefficients.

- **Average precision:** 0.7186568306; negative R9 baseline frequency 0.125160188.
- **ROC-AUC:** 0.9522948622; **Brier:** 0.056082814.
- At **0.25 review probability**, 2,186 of 2,637 original R9 losing legs flagged, **1,456 originally profitable legs also flagged**.
- At **0.50 review probability**, 1,633 of 2,637 losing legs flagged (**61.93% recall**), **737 originally profitable legs also flagged**. Those 737 winners originally generated **+$437.57** in the R9 booked ledger; it is a **retrospective protected-profit collision measure**, not counterfactual lost profit under a changed system.
- At **0.75 review probability**, 612 losing legs and **119 profitable legs** flagged.
- **1,724 of the 2,371** 0.50-or-higher flagged legs belong to ultimately profitable *complete cycles*, including their negative companion legs. Do not treat these as independently losing trades, automatically suppress them or rebook cycle outcomes.

### State-conjunction stress

- R9 booked balance already below its original prior peak at entry: **4,415 trades**, including **4,018 profitable legs**. Booked drawdown alone is an unsafe historical entry-veto candidate.
- Previous consecutively closed R9 losing run of 2+ at entry: **267 trades**, including **231 profitable legs**. Loss-cluster telemetry alone also would affect profitable trades.
- High entry loss score `p≥0.5` **AND** prior booked account underwater: **267 later-date trades**, **191 losing / 76 profitable**. This is observationally more targeted but still collides with valuable outcomes.
- Coinexx measured U≥25%: **930 trades**, **99 original losing / 831 profitable**. Coinexx measured U≥50%: **110 trades**, **13 losing / 97 profitable**. A high observed floating excursion alone is NOT a booked R9 loss forecast.
- Jan29/30 actual shock days show degraded **per-day average precision**: **0.6418 / 0.5537**, versus January-wide held-date pooled **0.7187**. Source regime variation is not erased by a high aggregated score.

The release's `JAN_R6_CONJUNCTIVE_RISK_STATE_STRESS.csv`, `JAN_R6_DAYWISE_CHRONOLOGICAL_STRESS.csv`, `JAN_R6_DIAGNOSTIC_ALERT_THRESHOLD_SENSITIVITY.csv`, `JAN_R6_ALL_ORIGINAL_NEGATIVE_BOOKED_LOSS_EPISODES.csv.gz` and `JAN_R6_ATLAS_240_WITNESS_INTEGRATED_POLICY_STRESS.csv` contain every above attribution and source-row trace.

## 5. Missing-tick and historical proxy stress (corrective iteration)

A deliberate **1-in-41 masked-known-window test** creates a derived validation *view*, not a modification of any original raw quote file. **677** strict-known windows are masked in the view; **674** have at least 100 earlier strict observed examples to calibrate the proxy, three have insufficient prior history. Original missing and nonstrict windows remain additional research targets.

- Initial conditional historical **P95** DD/S100 envelope covered only **93.62%** of the 674 masked, actually known outcomes: **FAILED** its own nominal 95% target. The initial approach was not called successful.
- A more conservative **P97.5** envelope covered **96.44%** in those same masked windows, including **95.38%** on the 65 Jan29/30 masked stress cases. P99 covered **98.37%** overall. These are **exploratory same-month observations after researching the P95 miss**, not an independently pre-specified prospective calibration test and not a quote-path reconstruction.
- A distributional estimate can be provided for **32 of 33** original no-quote holding windows and **189 of 195** nonstrict windows; the remaining cases are explicitly uncalibrated, not secretly assumed risk-free.
- Historical missingness may be nonrandom. The masked-window coverage test is not proof the original missing windows have the same risk distribution.

## 6. Certification table

| Requested concern | R6 disposition |
|---|---|
| R5 loss predictor integrated into *entire* January account-risk state machine | **PASS**: actual original-book update + quote-path event transitions + prior-day predictions + microstructure + proxy status |
| Full fixed-R9 Coinexx REAL TickLogger Python replay | **PASS**: all 21 original source files, 27,980 positions, all January real quotes, zero price/account event discrepancies |
| All Atlas witness, family, S100 tiers, positive trades and negative clusters preserved | **PASS** |
| Real original R9 profit or balance altered / any trade deleted | **NONE** |
| Early January $4/$5 tier trained loss prediction | **NOT ESTABLISHED** (6,911 January warmup observations without earlier-Jan fitted scores) |
| Predictive performance robust to Jan29–30 shock regime | **DEGRADED** on those two days; see per-day metrics |
| Original winners unaffected by mere read-only monitoring | **PASS** (no actions issued); **737 profitable collisions** at p≥0.5 demonstrate hypothetical trade filtering risk |
| 95% masked-known quote proxy calibration | **FAILED** at P95, exploratory conservative P97.5 covers 96.44% but not independent OOS certification |
| Executed capital preservation, altered-order profitability, stop fill/slippage | **NOT TESTED / NOT CERTIFIED**. Cannot infer from an unchanged original R9 book. |
| Future post-December regimes / February-January extrapolation | **NOT TESTED**, January study only |

**Precise claim:** The requested integrated January **observational account-risk policy** works according to its declared mathematical and source-data semantics, and its predictive module retains the earlier January internal results. It is **not** evidence that a trade-intervening portfolio protection policy would preserve January synthetic profits and/or live Coinexx account equity. A human-approved execution rule, if pursued, must separately specify allowed actions and test full causal portfolio consequences rather than retroactively counting original R9 gains from blocked trades.

## 7. Source preservation and reproducibility

Pinned original references:
- [R9 SYNTH original mapped marks](https://drive.google.com/file/d/1CC30szLw0_R9UpaRScPJZamgasqGjEsm/view)
- [AR1 Atlas R0 master](https://drive.google.com/file/d/175yPSkvCBsY6cW0DRtTisjEYaOK3nhAn/view)
- [Frozen S100 V2](https://drive.google.com/file/d/1yOOFHp08kLx4Y0g6qGWgadGcqbB8fLSO/view)
- [January R5 Atlas-first model, source and self-proof](https://drive.google.com/file/d/1JPqefJIXQMvaKGQcbnPyjRqVRLIk9Dkf/view)
- [January R5 source report](https://drive.google.com/file/d/1iX74oHE3uv0odIdHDnNDRTDq1z539Rnp/view)
- [January R1 source manifest and prior outcomes](https://drive.google.com/file/d/1pngujzYxewjUNn95uVtfgfOI0Cqk9kgU/view)

`ar1_january_integrated_policy.py` is the independent read-only policy state machine; `integrated_january_ar1_policy_stress.py` is the full original-real-quote Python replay and 27,980-trade account observer; `proxy_missing_and_gap_stress.py` and `stress_qc_and_atlas_acceptance.py` implement uncertainty, false-positive and book/cycle stress; `test_integrated_runtime_contract.py` supplies independent invariant fixtures. Existing original January gzip quotes and source R1/R5 files remain immutable external dependencies; no raw quote data is duplicated or regenerated. The release ZIP contains compact derived results, source and source hashes, not original large tick archives.
