# R9 v1.94 dual micro-basket entry: Jan–Sep 2026 baseline

**Date: 2026-11-14. Result: FAIL / research only / NO MT5 promotion.** This is a pinned, **in-sample entry-only** baseline, not a trained classifier or a profitable entry strategy.

## Frozen experiment

- Dual first-observed-midpoint basket anchors **5s and 15s**; completed source-second-close midpoint breakout **15s and 30s**. Four alternative same-side evidence lanes, **OR** arbitration into exactly ONE position; conflicting directions abstain.
- Basket displacement **0.10 XAUUSD price**, added breakout buffer **0.01 price**, inherited source-native R9 S1/ATR/session/spread quality filter; max four entries per source-native minute.
- Old R9 **30s original protective-stop/trailing/timeout exit FIXED**. Neither new **+$0.10 net** harvest nor **+$1.75 net** stretch was allowed to change exits in this initial entry study.
- 155-feature old-AUC model completely absent. No imputation, no inference, no new market-data generation.
- Existing original nine monthly Coinexx `XAUUSD_MT5_BROKER_2026_MM_ticks_ALL.csv.gz` archives matched all nine frozen source SHA256 checks; **72,129,347** source-ordered ticks. Original R9 frozen nine-month trade ledger from `R9_P1_Coinexx_9Month_SourceOrdinal_ASOF_CANDIDATE_CACHE_20261113.zip`; its source receipt SHA256: `59d3e8e6a2ad797083eb80f8f3248865d8163ea682f3c2bad4838162f051631a`.
- K=1 hypothetical account-currency cash per $1 XAUUSD price move at 0.01 lot and incremental C=$0.20 per completed trade beyond original Bid/Ask spread. Neither verified from actual MT5 fills/commission.
- For bounded runtime this *development calibration* used FIVE independent chronological partitions: Jan–Feb, Mar–Apr, May–Jun, Jul–Aug, Sep; each post-January segment replays preceding **seven calendar days** of actual previous-month quotes. This avoids new tick caches but **does not guarantee the exact recursive ATR/account/position state of one uninterrupted nine-month run**. It is source-byte exact, not full cross-partition engine-state parity.

## Whole-system results

| Metric | Original 60s R9 | New dual micro entry |
|---|---:|---:|
| Completed trades | 303,934 | **419,389** |
| Trade retention | 100% | **137.99%** |
| Net cash (modeled) | **−$120,212.46** | **−$162,656.05** |
| Gross realized loss cash | $138,113.97 | $189,771.14 |
| Additional loss from new entry | — | **−$42,443.59** |
| Increased gross losses | — | **+$51,657.17** |
| Positive months | 0 / 9 | 0 / 9 |

| Month | Original net | New net | New trades | New trades ≥+$0.10 NET |
|---|---:|---:|---:|---:|
| 2026-01 | −$12,488.92 | −$16,534.85 | 44,061 | 14.14% |
| 2026-02 | −$13,704.48 | −$19,330.01 | 52,786 | 20.78% |
| 2026-03 | −$14,498.33 | −$22,217.45 | 63,204 | 19.94% |
| 2026-04 | −$13,139.58 | −$17,899.05 | 46,359 | 13.65% |
| 2026-05 | −$13,576.41 | −$17,142.02 | 40,025 | 10.85% |
| 2026-06 | −$13,835.74 | −$18,547.47 | 45,681 | 12.54% |
| 2026-07 | −$12,859.27 | −$16,742.81 | 42,505 | 10.36% |
| 2026-08 | −$12,718.67 | −$16,866.95 | 41,666 | 10.40% |
| 2026-09 | −$13,391.06 | −$17,375.44 | 43,102 | 10.86% |

### Entry-lane evidence (IMPORTANT: lane counts OVERLAP)

- 15s basket / 15s breakout: **417,806** accepted entries also passed this lane (**99.62%** of all 419,389 trades).
- 15s basket / 30s breakout: **331,563** accepted entries.
- 5s basket / 15s breakout: **326,774** accepted entries.
- 5s basket / 30s breakout: **259,736** accepted entries.

The 5-second lane is *not* responsible for four simultaneous orders; the OR router orders once. However, the 15s/15s signal is already present in nearly all accepted positions, so the first engineering audit should isolate **which clocks reset trade permission, whether 15s/15s is too permissive, and whether 30s persistence is a useful veto**. These counts are overlapping membership, NOT causal attribution of incremental P&L; no performance benefit is claimed from deleting any lane until tested.

## Scientific disposition and next audit

**FAIL the first research-profitability gate.** Nine months of negative after-cost cash and higher gross losses demonstrate that faster OR entry opportunities do **not** establish edge. Increased throughput alone has amplified the losing system.

Next *only after this frozen baseline*: audit signal exclusivity, basket rearm timing, price-displacement/noise, 15/30-second persistence and actual cost concentration; compare a **bounded predeclared** confirmation/veto redesign, frozen against this baseline. Avoid replacing it with a new high-AUC model or conducting a broad hyperparameter sweep. Preserve historical data and compiled EA unchanged.

**Release blockers:** uninterrupted nine-month full engine parity, broker K/C/OrderCalcProfit, slippage and market order/freeze validation, actual account governor parity, later untouched out-of-sample dates, and positive full-system after-cost cash. Any 5s/15s or 15s/30s change must be experimentally validated separately from the $0.10/$1.75 exit controls.

The original v1.94 MQ5 implementation and v1.90 rollback were not changed. The GitHub source implementation is `dual_basket.py` (blob `b56ada74360c410ee33b0c07888e9c2d85303e4a`) and independent tests passed in GitHub Actions. Source monthly digests and expanded entry cash metrics were validated locally in the compact JSON scorecard; **no raw archives or large tick libraries were uploaded to GitHub/Drive**.
