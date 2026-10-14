# January 2026 R9 SYNTH versus R9 OVERFIT: ten random-start forensic audit

**Status: original-source diagnostic; neither a newly executed Dukascopy strategy nor broker-certified $100 replay.** Dated 2026-10-14. No engine/trading/scientific-state change.

## Reproducible cohort

Seed `20261014`; Python `random.Random(seed).sample()` without replacement from the 21 original R9 SYNTH January trading dates, sorted after sampling. The 10 UTC start dates are 2026-01-08, 2026-01-09, 2026-01-14, 2026-01-16, 2026-01-21, 2026-01-23, 2026-01-26, 2026-01-27, 2026-01-29, 2026-01-30. Each cash overlay resets to $100.

## Raw source identity

- R9 SYNTH: `ReportTester-871471_jan2026_jul2026_R9_ticklog_synth(4).xlsx`, SHA-256 `e5fcf4d6879193fac88e7a8e101db1111d59e1a7f5abfb793c970b06cfce7cc7`; its January exit-day reference is `r9_synth_jan_daily_weekly.json` from GRID0272. Original tester settings **initial deposit $100,000**, leverage **1:500**, **InpLots=0.01**.

- R9 OVERFIT original offline score file: [January OVERFIT scores](https://drive.google.com/file/d/1wOtzi6-uflYWTDPLZH_6ZleRAEn29XQx/view), SHA-256 `67b2d994ba6a00ad24a99120f21faa857441c4ffd92f3815da70fc0fc0d059a3` (20,886 labels); [January REAL↔SYNTH matched pairs](https://drive.google.com/file/d/1Nk3BgnEyRvu6hazSSBUNFxDMILOJeCZ5/view), SHA-256 `5c4eea18429100a89b5052c70c0ae6ece40fd68da2681d76e821fe3422cf7e6a` (20,886 matched pairs). All (entry_time_msc_r, side) joins verified one-to-one. Original archival location: [teacher corpus](https://drive.google.com/drive/folders/1ES78vXb2mFsOsa50BiwCLsT6BXgLe-Oe).

## R9 SYNTH: copy-the-original-close-cash arithmetic only

Each original January date supplies complete historic SYNTH closing-trade net, gross profit, gross loss, wins and trade counts. Reset balance to $100, credit the full original test P&L of each day **without order rejection, liquidation, new fees, funding changes, spread re-pricing or modification to signal decisions**. Stop at the first END-OF-DAY checkpoint ≥$10,000 or January 30. Intraday crossing could occur earlier; this is not a tick-executable $100 replay.

| Start (UTC) | First ≥$10k at day-end | Calendar day # | Net to checkpoint | Gross loss | PF | Win % | Trades |
|---|---|---:|---:|---:|---:|---:|---:|
| 2026-01-08 | 2026-01-21 | 14 | $12,141.12 | −$893.32 | 14.59 | 85.24% | 11,909 |
| 2026-01-09 | 2026-01-21 | 13 | $11,088.97 | −$803.77 | 14.80 | 85.25% | 10,734 |
| 2026-01-14 | 2026-01-23 | 10 | $11,038.94 | −$699.06 | 16.79 | 86.47% | 10,172 |
| 2026-01-16 | 2026-01-26 | 11 | $11,797.06 | −$622.70 | 19.95 | 87.20% | 9,579 |
| 2026-01-21 | 2026-01-27 | 7 | $11,472.74 | −$486.08 | 24.60 | 88.49% | 8,320 |
| 2026-01-23 | 2026-01-28 | 6 | $10,773.67 | −$419.40 | 26.69 | 88.47% | 7,191 |
| 2026-01-26 | 2026-01-29 | 4 | $14,758.72 | −$395.36 | 38.33 | 89.10% | 7,176 |
| 2026-01-27 | 2026-01-29 | 3 | $11,779.10 | −$287.07 | 42.03 | 89.29% | 5,314 |
| 2026-01-29 | 2026-01-30 | 2 | $12,613.76 | −$114.59 | 111.08 | 91.65% | 2,695 |
| 2026-01-30 | Not by Jan 30 | — | $6,892.02 | −$47.61 | 145.76 | 92.24% | 1,211 |

Crossed by Jan30: **9/10**. Crossed at a day-end checkpoint within first 7 calendar days: **5/10**; January 30 start is right-censored. Not margin-valid or quote-executable from $100.

## OVERFIT: this is NOT a second backtest or an account-equity stream

The genuine OVERFIT artifact is a **retrospective score sidecar**, not a standalone funded strategy. `teacher_synth_survive20` represents whether the historical synthetic counterpart survived ≥20 **seconds**, not whether a $100 account survived. To expose cross-feed transfer risk, the following diagnostic takes the matched historical **R9 REAL** trades whose *in-sample* `teacher_synth_win_score_overfit >= 0.90`, and sums `pnl_price_r` from each start through Jan30. This arbitrary illustrative cutoff is *not* an independently tested execution policy, and these dollar-like price changes exclude broker fees, margin and adverse liquidity. The 10 starts share many later trades.

| Start | Selected REAL trades | Price-only net to Jan30 | Gross loss | PF | Win % | Peak-to-trough closed cash DD | First $100 cash balance ≤0 |
|---|---:|---:|---:|---:|---:|---:|---|
| 2026-01-08 | 6,069 | −$722.80 | −$1,743.15 | 0.58 | 49.83% | $733.99 | 2026-01-13 |
| 2026-01-09 | 5,747 | −$689.01 | −$1,664.60 | 0.59 | 49.59% | $697.21 | 2026-01-14 |
| 2026-01-14 | 4,839 | −$606.61 | −$1,438.03 | 0.58 | 48.73% | $614.43 | 2026-01-16 |
| 2026-01-16 | 4,235 | −$524.44 | −$1,277.02 | 0.59 | 48.38% | $532.05 | 2026-01-20 |
| 2026-01-21 | 3,522 | −$424.49 | −$1,082.60 | 0.61 | 48.50% | $433.07 | 2026-01-23 |
| 2026-01-23 | 2,621 | −$338.16 | −$840.77 | 0.60 | 47.04% | $354.85 | 2026-01-27 |
| 2026-01-26 | 2,230 | −$307.38 | −$738.12 | 0.58 | 46.10% | $314.99 | 2026-01-27 |
| 2026-01-27 | 1,729 | −$245.99 | −$596.55 | 0.59 | 44.42% | $256.18 | 2026-01-28 |
| 2026-01-29 | 649 | −$87.53 | −$264.59 | 0.67 | 40.68% | $106.36 | Not observ |
| 2026-01-30 | 267 | −$37.71 | −$115.55 | 0.67 | 39.70% | $50.79 | Not observ |

**No one of the ten OVERFIT-score-filtered paired-REAL P&L overlays approaches +$9,900.** Eight of the ten become nonpositive even on the **closed-cash-only** overlay. The other two are curtailed by January 30. Price-only synthetic selection cannot show broker survival.

Across all January pairs (not 10 independent accounts): 20,886 original matched REAL trades generated **−$2,720.55** price P&L, price-only PF **0.539**. The 7,352 illustrative `score >= .90` subset generated **−$871.12** price P&L, **−$2,079.37** gross loss, PF **0.581**, **50.10%** price-positive. All 21 January UTC trade dates had net-negative corresponding pair-sample REAL P&L. A paired SYNTH subset had **+$33,733.33** price P&L; it is not directly comparable to the full original SYNTH January net +$41,520.82.

## Mandatory limitations and disposition

1. R9 SYNTH original initial cash **$100,000**. Its January original historical full-sample P&L **+$41,520.82**, gross loss **−$1,827.87**, PF **23.7154**, 27,980 trades, 87.09% winning, reported January max **balance** DD **$3.40**. Historical dollar drawdown on the high-capital original tester is **not** independently verified $100 floating equity or margin DD. Daily max balance-DD figures are source reference only.

2. The displayed ten-start SYNTH numbers are a cash-flow overlay at daily exit granularity, **not tick-by-tick price execution or actual fundability**. Drawdown, broker stop-out, initial required margin, overlapping positions and latency under $100 are **unknown**. No full original R9 OVERFIT funded position/deal ledger exists in the examined corpus.

3. The OVERFIT scores were learned on the SAME historical months and select source-paired trades retrospectively. Neither the score nor the selected REAL pair population may be used to authorize a live or causal Dukascopy entry. The `survive20` feature is **20-second trade duration**, never account solvency.

4. To establish the requested genuine comparison, each strategy must generate its **own causal entries** and fill via first available ordered original Dukascopy Bid/Ask at execution latency. Replay at fixed 0.01 lots and $100 true starting cash with original-realistic broker contract, per-symbol margin and account stop-out, forced close, fees, spreads, slippage, position concurrency, hourly mark-to-market DD, and first actual $10k touch. That verified experiment has not been completed for original SYNTH or OVERFIT.

**Status:** Analytical source comparison complete; genuine R9 OVERFIT account equity path **not derivable**; $100 account survival **not certified**; active V1 engine unchanged, scientific J0183, August SEALED, trading OFF.


## Archived reproducibility package
- Original inputs, source-matched CSVs and rerun scripts: https://drive.google.com/file/d/1SXiCp2V0eY3WsCh6XXO_vNaumg7qHtql/view
- Package SHA256: `c35f83340f046b28469fc008af8dc738fd9b89ff32acc89ebcded727019fe340`
- Original preserved report: https://drive.google.com/file/d/1D6jGl405mbx0NdZucrcgb8Q8ZrbstquB/view
- **UNPROMOTED SOURCE DIAGNOSTIC. NOT a Dukascopy $100 executable backtest.** No engine code or J0183 change.
