# R9 v1.94 — Five-round January–September Coinexx adaptive-exit training

Date: 2026-11-14. **Research verdict: FAILED for profitability; no promotion to MT5.**

## Source integrity and interpretation
- Replayed exactly 72,129,347 original Coinexx XAUUSD Bid/Ask quote rows, January–September 2026, from the original nine unmodified source gzip files. Verified nine original compressed-file SHA-256 values against the preexisting frozen source receipt. No new tick engine, raw tick archive, model-feature rebuild or regenerated LightGBM.
- Source-ordinal original R9 baseline was run CONTINUOUSLY across all nine month boundaries, preserving ATR, minute brackets, pending positions, second bars and same-minute rearming. It matched the previously frozen 303,934 original trades on exact entry and exit ordinals, timestamps, executable-side quotes, P&L and exit causes across every month.
- Independent-month reset experiments were REJECTED when February trade count differed (35,366 vs frozen 35,382). They were not used in any score.
- Each adaptive arm replayed all original quotes continuously with its own independent exit/position/entry/rearm state. Five fixed policy arms: original baseline; cost-aware adaptive trail; staged harvest/runner; tight cost-aware trail; defensive staged harvest.
- This is a deterministic hyperparameter-policy-selection study, NOT five new trainings of the 155-feature AUC LightGBM. The frozen classifier stays shadow-only. January–September is previously research-exposed; these retrospective chronological folds are NOT pristine prospective OOS.

## Assumed cash economics
- Hypothetical fixed 0.01-lot K = 1.00 USD account-currency profit for a $1 XAUUSD quote movement; incremental roundtrip charge C = 0.20 account units per completed position, on top of Bid/Ask spread already counted once. Real Coinexx contract sizing, actual fills and broker fees were NOT provided by historical tick logs.
- Every number below is SOURCE-EXACT QUOTE-SIDE MODELED CASH, NOT REAL ACCOUNT PERFORMANCE.
- Whole-system actual modeled realized net cash (not $1.75 hypothetical target achievement) is the goal. $1.75 average net cash/trade is aspirational, not a forced TP.
- No live MQL5 EA modifications, no account-level cross-EA gross-loss governor, margin, order rejects, independent OnTimer close, full fee/slippage draws or deployment claims.

## Five chronological expanding-window rounds
Train-only frozen policy selection: total modeled net account cash per source-entry hour MINUS 0.10 times 95% left-tail hourly cash-loss CVaR; trade retention >=80% in each training month, average hold <=30 seconds. The next evaluation month's labels are excluded from selection.

| Fold | Train | Evaluate | Training-selected policy | Evaluation modeled net cash | Original | Incremental vs original | Trade volume retained |
|---|---|---|---|---:|---:|---:|---:|
| 1 | Jan–Apr | May | cost_trail_tight | -13,833.03 | -13,576.41 | **-256.62** | 98.95% |
| 2 | Jan–May | June | baseline | -13,835.74 | -13,835.74 | 0.00 | 100% |
| 3 | Jan–June | July | baseline | -12,859.27 | -12,859.27 | 0.00 | 100% |
| 4 | Jan–July | August | baseline | -12,718.67 | -12,718.67 | 0.00 | 100% |
| 5 | Jan–Aug | September | baseline | -13,391.06 | -13,391.06 | 0.00 | 100% |

**Result: 0/5 selected policies produced positive net cash, and 0/5 beat original R9 in evaluation.** The selected strategy scored -66,637.77 across May–September against original -66,381.15, worsening the total by -256.62. In fold 1, a 3,000-resample paired source-day retrospective bootstrap interval for incremental test-month total was about [-365.53, -150.70], still negative.

## All nine months, independently replayed fixed policy arms
| Month | Original | Cost trail | Staged harvest | Tight trail | Defensive harvest |
|---|---:|---:|---:|---:|---:|
| Jan | -12,488.92 | -12,548.85 | -12,544.97 | -12,499.13 | -12,499.03 |
| Feb | -13,704.48 | -13,262.02 | -13,352.59 | -13,303.88 | -13,337.56 |
| Mar | -14,498.33 | -14,230.53 | -14,270.82 | -14,287.63 | -14,327.83 |
| Apr | -13,139.58 | -13,263.85 | -13,284.51 | -13,282.58 | -13,283.17 |
| May | -13,576.41 | -13,792.34 | -13,786.85 | -13,833.03 | -13,824.08 |
| Jun | -13,835.74 | -13,705.69 | -13,722.86 | -13,802.12 | -13,804.30 |
| Jul | -12,859.27 | -12,801.84 | -12,814.71 | -12,839.84 | -12,848.00 |
| Aug | -12,718.67 | -12,600.66 | -12,605.89 | -12,719.47 | -12,716.25 |
| Sep | -13,391.06 | -13,415.82 | -13,424.78 | -13,463.23 | -13,466.95 |
| **Jan–Sep** | **-120,212.46** | **-119,621.60** | **-119,807.98** | **-120,030.91** | **-120,107.17** |

| Full-policy metric | Original | Cost trail | Staged harvest | Tight trail | Defensive harvest |
|---|---:|---:|---:|---:|---:|
| Completed positions | 303,934 | 298,625 | 298,918 | 300,341 | 300,448 |
| Net cash per completed position | -0.39552 | -0.40057 | -0.40081 | -0.39965 | -0.39976 |
| Net cash per source-entry active hour | -27.315 | -27.181 | -27.223 | -27.274 | -27.291 |
| Gross realized cash loss | 138,113.97 | 155,430.47 | 155,241.38 | 150,505.44 | 150,381.39 |
| Average holding seconds | 7.45 | 10.43 | 10.25 | 9.46 | 9.40 |

The best fixed cost-trail policy had +590.86 less loss in nine months (~0.49% of original loss) but added **17,316.50 gross realized losses**, increased average hold and worsened after-cost return PER TRADE. It is NOT a whole-account risk improvement.

## Commission sensitivity
At ZERO additional C, all are still negative: original -59,425.66; cost trail -59,896.60; staged harvest -60,024.38; tight trail -59,962.71; defensive harvest -60,017.57 account currency. Spread remains in the quote-side execution pricing. Doubling additional C only worsens all. Thus the historical failure cannot be explained only by the additional cost assumption.

## Research improvements indicated by evidence
1. Do not promote cost trail or staged harvest to the R9 v1.94 EA. Positive-net early harvest does not solve widespread losing entries; widened trailing increases gross losses.
2. Next competing-risk candidate: explicitly assess EARLY LOSS ABORT versus HOLD, EXIT NOW and legal MONOTONIC STOP TIGHTEN, conditional on as-of spread shock/recovery, quote freshness, signed revisions, 1s realized volatility, elapsed age, MFE/MAE and current executable quote-side cash. Fit policy-specific cash continuation hazards on strictly earlier data, penalize downside CVaR and the opportunity cost of occupying a trading slot. Keep gross-loss governor as a hard outer constraint.
3. Run paired, otherwise identical indicator ablations with completed-Bid M1 StdDev/EMA (and existing completed-M5 ATR). Current five arms vary multiple parameters jointly, so NO standalone evidence M1 indicator inclusion improved net cash. iVolumes VOLUME_TICK can approximate quote activity only; true executed volume, L2 imbalance, VPIN and real VWAP remain UNOBSERVABLE in Coinexx logs.
4. Require MT5 OrderCalcProfit contract/currency validation, actual fee/reject/slippage estimates, full original broker stop/freeze and account governor simulation, future unseen Coinexx dates, per-hour downside and high throughput before source promotion.
5. No trade strategy is certified; no EA changed. R9 v1.94 MT5 source checkpoint commit 813baf96f2b381be5fc7896aac8b08a966114948 remains unchanged. R9 v1.90 exact critical rollback 8729a6345655a7b4ea31facc81982004ee2b8921 remains unchanged.
