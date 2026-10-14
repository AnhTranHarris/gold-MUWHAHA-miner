# GRID0312–GRID0319 — January original-tick $100/7-day execution, liquidation and velocity research

**2026-10-14 | Status: UNPROMOTED / January independent owner QC PENDING / NO MQL5 or live trading.**

## 0. GOVERNING SOURCE — NEVER SUBSTITUTE THIS REPORT FOR ORIGINAL LAW

- Original owner permanent L0–L7 whitepaper, exact GitHub blob `1b92b3c89159681a7181508de158af685cf5780c`:
  `research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt`, `delta-A-alpha`.
- Owner-ratified complete conversation: https://docs.google.com/document/d/1J9d_P4ooCnNmcxPwG1F178aE4ktpkLrFclcyQPaQJ8k/edit
- Anti-drift, exact-source/QC law: https://docs.google.com/document/d/1eG5F76uvm9M-1JXs4LvAaTzPEurU5l4Pgj2sUUelc1o/edit
- January original-source/QC evidence gate: https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit
- Unabridged Jan–July roadmap: https://docs.google.com/document/d/1PcaksxuiayFXVW3QtKfzitARvQj6NyL4IIbGhG8K9z4/edit
- Original owner Dukascopy/R9 roles and no redundant report audits: `research/delta_a_alpha/governance/OWNER_20261013_VERBATIM_DUKASCOPY_TICK_CANDLES_R9_REFERENCE_LOCK.md`.
- Scientific cursor remains **J0183**. Live `FourSessionV1` SHA `64b75c39c41ff8ccd0d0e8b02e45bdf5b9ca54e2` unchanged; August 2026 SEALED; trading OFF.

This is **new original executable research**, not a replacement for original accepted source or the roadmap. All records append-only; previous GRID0272–0311 untouched.

## 1. DEFINITIONS, DATA, AND NEW ACCEPTANCE REQUIREMENT

Owner target: fixed 0.01 lot, no loss-dependent sizing / DCA rescue / martingale, $100 initial cash per randomly seeded independent start, survive 10/10 random starts and pursue $10,000 or higher in **less than one week**, ultra-high completed-trade velocity, 100%+ R9 SYNTH monthly/day/week and 75% R9 OVERFIT six dimensions; explicitly minimize each UTC day's worst hourly floating equity drawdown.

**Source of execution truth:** original January Dukascopy UTC Bid/Ask file `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`, 9,135,062 ordered quotes; SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`. Data is not constructed from R9. Exact original 2026-01 gzip at https://drive.google.com/file/d/1ghF2blUzJwwufFrD-P-1aS3bklGuOSHz/view. One period = **seven complete UTC calendar days** from 00:00 on chosen January day; no extrapolation across February, therefore sample only dates with seven observed days before January's last quote. A different original earlier experiment began on 10 seeded dates and ran to January end; it is **not** comparable to this seven-day metric without horizon adjustment.

Uniform reproducible seed **20261014**; selected from 16 eligible January trading dates (without replacement). Exact sampled dates: **January 5, 8, 9, 12, 15, 19, 20, 21, 22, 23 (2026)**. No historical target information feeds runtime trade admission; the sample selector is evaluation-only. Ten historical starts do not prove 100% future survivability.

**Inherited source:** original GRID0272 archived code and January record; original source-hash exact archive from GRID0307–0311 included as `ORIGINAL_PREDECESSOR_GRID0307_0311.zip`. The 236,324-original-candidate source universe and predetermined source exit events were **historically researched in January**; therefore this experiment is **in-sample** and is not a fully endogenous runtime signal discovery. It may use a future exit index to schedule that future close but never permits future P/L, R9 benchmark labels or future quote prices for admission decisions. New forced exits use **the first actually observed adverse original quote**, and any planned later settlement is canceled.

**Not broker-calibrated:** hypothetical 0.01 lot=1 XAU ounce, margin = entry USD per ounce / hypothetical leverage, initial baseline leverage 500:1, full round-trip modeled cash fee $0.20, 250ms inherited source entry delay, no overnight financing, no verified Coinexx hedge margin or balance tier. Stopout `equity / margin` scenario 0.50 or 1.0; some tests use preemptive 4.0/6.0 self-liquidation. Broker's real stop-out mode, position closing order, order sizing and slippage remain unknown. Coinexx public https://coinexx.com/margin-and-leverage describes **up to** 500:1 leverage, not actual account-specific XAUUSD margin.

## 2. NEW ENGINEERING SOURCES — READ CODE, NOT THE SUMMARY

| ID | Original complete Python filename | Actual function |
|---|---|---|
| GRID0312 | `grid0312_tick_stopout_executable.py` | Full tick-scanned portfolio ledger; actual forced positions close at observed opposing Bid/Ask and book net cash; remove from future planned settlement; update paid-parent and child admissibility and global source inventory |
| GRID0313 | `grid0313_seven_day_ten_start_stopout_frontier.py` | 10 seeded full seven-day starts × 6 margin/defensive policies |
| GRID0314 | `grid0314_aggressive_seven_day_true_liquidation_stress.py` | Distinct aggressive admission and stress cost screens × 10 starts |
| GRID0315 | `grid0315_independent_7day_margin_liquidation_qc.py` | Independent per original quote equity and per-hour drawdown reconstructed from separate booked deal ledger |
| GRID0316 | `grid0316_seven_day_defensive_forced_exit_verified.py` | 10 starts × 6 price-booked defensive exits, all executed deal rows in complete gzip ledger; independent full path comparison across all 60 episodes |
| GRID0317 | `grid0317_coverage_tick_lifecycle_acceleration.py` | Causal original tick TP/SL/hold triggers on existing coverage_gc0/gc2 only, 6×10 falsification variants |
| GRID0318 | `grid0318_leverage_cost_sensitivity_seven_day.py` | Seven-day leverage 100/200/300/500 and adverse fee + slippage sensitivity × 10 |
| GRID0319 | `grid0319_forced_liquidation_adversarial_unit_tests.py` | Hand-calculable favorable-close, forced-close with no ghost settlement, and adverse-gap negative-equity tests |

The complete sources and **actual JSON outputs + full booked trade ledgers + predecessor source** are attached in this ZIP. Never reconstruct the above from an abstract.

## 3. ORIGINAL-TICK 7-DAY CASH FRONTIER (GRID0313/0316)

The preserved admission baseline 20% margin budget at modeled 500:1 leverage, fixed 0.01 lot:
- **10/10** historical episodes with positive marked equity and no triggered modeled broker liquidation.
- **0/10** reached $10,000 within seven days.
- Ending cash range **$185.407–$444.940**; minimum equity observed among all episodes **$78.480**; **859** completed deals across the ten independent seven-day runs.
- Worst UTC-hour floating drawdown among episodes **$164.720**. This is *larger than the starting $100 balance*, because peak-to-trough is an absolute trailing high-water measure after account growth, not necessarily account ruin.
- Independently booked total net across the 10 reset experiments **+$2,148.770**, **$2.5015 per completed trade** (descriptive in-sample only). To earn $9,900 from $100 at the same observed average economics would require about **3,958** winning-and-losing completed trades **per account in seven days**, compared to this test's average **85.9**. It is a scale illustration, not evidence that adding that many trades preserves expectancy or admissibility.

**Defensive margin policy trade-offs from GRID0316** (same sample, fully reconciled):

| Policy | Modeled non-ruin | 7-day $10k | Ending cash across starts | Worst hourly floating DD | Completed trades, 10 starts | Defensive early-close events |
|---|---:|---:|---:|---:|---:|---:|
| 20% admission, no premature liquidation | 10/10 | 0/10 | $185.41–$444.94 | $164.72 | 859 | 0 |
| 35% admission, early partial close at 400% level | 10/10 | 0/10 | $165.79–$393.68 | $146.30 | 893 | 72 |
| 35% admission, early full flatten at 400% | 10/10 | 0/10 | $154.04–$381.32 | **$82.36** | 852 | 30 |
| 35% admission, early partial at 600% | 10/10 | 0/10 | $76.15–$259.10 | $42.60 | 895 | 544 |
| 35% admission, early full flatten at 600% | 10/10 | 0/10 | **$25.52–$59.09** | **$22.90** | 733 | 494 |
| 20% admission, extra adverse $0.10/closed deal | 10/10 | 0/10 | $169.95–$444.30 | $144.13 | 821 | 0 |

**WARNING:** defensive `equity/margin` values are an assumed heuristic for early action, **not** Coinexx's actual stopout. No actual broker stops were triggered in these sampled configurations, so this is *an executor reconciliation exercise*, not validation of actual broker forced-liquidation probabilities. The 600%-flatten policy protects the worst observed hourly DD but loses money relative to starting cash in every tested episode: such a configuration is NOT promoted as a profitable breakthrough.

## 4. DISTINCT NEGATIVE EXPERIMENTS — DO NOT RETEST IDENTICALLY

**GRID0314:** Raising the margin-admission budget from 35% to 65% generated **no additional trading velocity** in this cohort; the earned position-cap tiers were already binding. No policy reached $10,000 under one week. Extra $0.10 adverse slippage reduced results.

**GRID0317:** The source-owned `coverage_gc0`/`coverage_gc2` positive ledgers were examined: under the 10 independent preserved baseline episodes, coverage_gc0 had 289 trades and +$1,533.53; coverage_gc2 had 32 trades and +$282.79; several other sources were negative. Five structurally new causal short-cycle exit designs (TP $2–$8 / loss $2–$6 / 60–240-second maximum hold) **failed**: no variant improved ending cash at even one of ten starts. Ending ranges with an acceleration exit were $71.97–$242.62, all below unmodified exit outcomes. Total completed trade counts were 680–769 vs baseline 859; lowering duration **did not increase net profitable velocity** because truncating the original asymmetric captured edge dominated any new capacity. Research hypothesis REJECTED for these variants. NOTE: `gross_loss_sum` in GRID0317 JSON is a poorly labeled sum of negative **episode nets**, NOT trade-level gross loss, and is **invalid for gross-loss QC**. Never promote that field.

**GRID0318 leverage/cost stress:** 20% margin-admission budget; when modeled XAU 0.01-lot notional margin at 100:1 or 200:1 exceeds $20 opening budget on a $100 account, all 10 runs execute ZERO trades (non-ruin is simply no trading, **not** acceptance). At 300:1: 342 total closed deals across 10, final cash $150.14–$245.01. At 500:1: 859 total deals, $185.41–$444.94. At 500:1 and extra $0.20 roundtrip fee plus $0.10 exit slip: 742 deals, $159.35–$401.82. None reached 100×. Account-specific XAUUSD margin and stop-out terms, not headline broker maximum, must govern production.

## 5. INDEPENDENT SCIENTIFIC QC / FAULT INJECTION

- `grid0315` recomputed tick-level balance, long/short inventory, signed entry basis, open position exit-fee liability, equity curve, absolute equity DD and **every UTC-hour** max peak-to-trough from the **actual booked ledger** (not reading the engine's in-memory marks). Independent cash/mark/DD/hourly outcomes agreed to less than $0.00001 in all 60 GRID0316 policy×sample episodes. Entries and closings were verified at original executable Bid/Ask, with **one close per admitted trade and no double-booking**. The `grid0316_all_booked_deals_original_tick.json.gz` contains full accepted candidate identities, original quote-index closes and reasons, including forced/defensive closes. The experimental cohort has 60 episodes, not 60 independent market histories.
- `grid0319` three hand-calculated adversarial quote sequences: original future scheduled winner books $147.80 without a forced close; an earlier 600% threshold books $47.80 at the actually observed adverse quote and cancels the later planned +$47.80 win; a gap through a 50% threshold can still leave **−$12.20** despite immediate quote-side forced liquidation. **Do not claim guaranteed broker survival** even if 10 historical samples look safe.
- Original January Dukascopy gzip SHA was rechecked for this continuation and matches original governance. Original source and predecessor artifacts untouched.
- For newly written source code see `GRID0312`–`GRID0319` Python files in this archive (hashes in manifest), original predecessor ZIP and actual full JSON result files, not this prose.

## 6. OUTSIDE RECONSTRUCTIBLE ENGINEERING SOURCES (NOT PROOF OF PERFORMANCE)

- MetaQuotes **ACCOUNT_STOPOUT_MODE**, percent vs money, and account margin-mode distinctions: https://www.mql5.com/en/docs/constants/environment_state/accountinformation . Must query actual terminal fields for any later Coinexx parity.
- MetaQuotes Chinese programming guide https://www.mql5.com/zh/book/automation/symbols/symbols_margin : `OrderCalcMargin` omits exposure interaction and hedged margin; `OrderCheck` and symbol margin properties matter.
- MetaQuotes Japanese risk/stop-out account functions https://www.mql5.com/ja/articles/113 : stop-out percent vs money and account currency and stop-out level must be read, not guessed.
- MQL5 Chinese risk manager article https://www.mql5.com/zh/articles/18918 : account-level daily loss protection and avoiding loss-recovery compulsions are implementable principles, not guaranteed success.
- Reddit source https://www.reddit.com/r/algotrading/comments/1vyeq3l/cost_model_in_backtesting_results/ : execution costs should be priced per fill with spread/commission/slippage separately; test maximum sustainable cost. Community testimony is not a verified source of Coinexx parameters.
- Coinexx published leverage description https://coinexx.com/margin-and-leverage : **up to** 500× is a maximum, not a certified per-symbol margin schedule.

## 7. REQUIRED NEXT DEVELOPMENT — NO BACKTRACK / NO UNAUTHORIZED PROMOTION

1. Recover actual **Coinexx account/symbol settings** from `ACCOUNT_MARGIN_SO_MODE`, `ACCOUNT_MARGIN_SO_SO`, `ACCOUNT_MARGIN_MODE`, `ACCOUNT_LEVERAGE`, `SYMBOL_TRADE_CONTRACT_SIZE`, `SYMBOL_TRADE_CALC_MODE`, hedged margin, commission and swap settings. The owner excluded redundant historical tester-report audits; live symbol-contract read for future broker parity is a distinct engineering requirement, **not** a demand to redo reports now.
2. Replace inherited historically selected signal opportunities, exits and parent cell groups with a single genuinely **endogenous** V1 `FourSessionV1` L0–L7 source; must pass original January regressions and then month-blind other months.
3. Pursue genuinely orthogonal **new high-quality opportunity families**, especially January W01/early-session trades. Original R9 SYNTH daily/weekly actual cash and trade-volume targets still unpassed; 75% OVERFIT six per-trade objectives unmeasured. The current high-quality source trades' long holding period is not remedied by mechanically early-exiting them; this research falsifies five such exit shortcuts.
4. Retain source-specific hour-risk/parent controls from GRID0291–0306 as experimental fallback, but add global risk fee/forced-exit model and 10-start seven-day $100 net/gross/velocity/hourly/ruin matrix to independent acceptance. Earned concurrency may increase only from previous CLOSED after-cost profit and is restricted by actual account margin; 0.01 lot fixed; no martingale; no month label runtime feature.
5. The 100×/7-day target requires 100-fold wealth growth, with extraordinary tail risk and strong selection bias on one January in-sample month; **do not imply achievability, broker safety, or statistically guaranteed 100% survival**. Real quote gaps can defeat forced-liquidation thresholds.

**Owner QC:** PENDING. No preferred candidate promoted; no production-engine changes; official cursor J0183, August SEALED, trading OFF.


---
## Verified exact-byte research custody
- Complete original Python/repro/source/ledger archive: https://drive.google.com/file/d/1AExwv8MeePcgaZYQ1TFI0xy_njUtUJ-l/view
- Archive SHA-256: `751790496c9d54a771e799a511368bf4f1fb8bf1ad58870cf1ef58264a69b85c`
- Google Drive same full report: https://drive.google.com/file/d/1z7dSG5a9DrxXW2cAU9-eYKIkOM2wyuo2/view
- Exact 8 runnable experiment source files separately committed under research/delta_a_alpha/monthly_progressive_roadmap_20261013/2026-01_JANUARY/experiments/GRID0312_0319_SOURCE_CODE
- Full booked deals `grid0316_all_booked_deals_original_tick.json.gz` and full JSON variants in archive; never infer from this human report.
- Original governing 2026-01 January folder: https://drive.google.com/drive/folders/1g-NUuHTBoVwySMWQT9WG-i-SUGQH3yXU
- **NO strategy promotion or official scientific cursor advance, no production-engine integration.**
