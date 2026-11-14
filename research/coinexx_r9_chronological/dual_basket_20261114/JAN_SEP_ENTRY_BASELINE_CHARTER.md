# R9 dual micro-basket entry baseline: January–September 2026

**Date:** 2026-11-14. **Status:** In-sample, research-only calibration. No trading promotion.

## Explicit human-in-the-loop scope

Replace the R9 60-second entry basket in the *research candidate* with independent 5-second and 15-second baskets. Each lane uses original source-ordered quotes only, anchored to the first observed midpoint after a wall-clock basket reset. Each basket tests breakouts across the last 15 and 30 seconds of **completed observed second-close bid/ask midpoints**. Four valid lanes: 5/15, 5/30, 15/15 and 15/30. The four lanes issue **at most one** position, with conflicting sides abstaining and a source-minute cap of four filled entries. The original R9 S1/ATR/session/spread gate and original R9 stop/trailing/30-second hold exit remain controls.

The existing $0.10 midquote basket displacement and $0.01 breakout confirmation buffer are inherited **fixed engineering parameters**. They are price-distance thresholds, **not the owner's separate $0.10 NET account-currency minimum profit**. The $0.10 and $1.75 cash-exit alternatives are intentionally **not evaluated in the first entry-only scorecard** to avoid entangling entry and exit effects.

The prior 155-feature, approximately 0.72-AUC classifier is **not used, retrained, transferred, interpolated or evaluated** on the new entry ordinals. No volume claims or rebuilt tick datasets.

## Data pins, comparators and experiment order

- Source: original **nine Coinexx monthly gzip archives** for 2026-01 through 2026-09 in the already existing primary Drive; exact filename `XAUUSD_MT5_BROKER_2026_MM_ticks_ALL.csv.gz`.
- Existing frozen receipt: `R9_P1_Coinexx_9Month_SourceOrdinal_ASOF_CANDIDATE_CACHE_20261113.zip`. It declares **72,129,347 original source quote rows** and **303,934 old R9 trades**, with per-month SHA256 and original trade-entry/exit ordinals.
- No resampling to candles for execution, no lookahead, no synthetic current-second extrema; source-native timestamps and order preserved, including equal timestamps.
- Initial entry-only study: candidate dual 5/15 x 15/30 with ORIGINAL stop/trailing/30-second exit vs original R9 60-second bracket entry with the SAME exits. Not a search of thousands of candidate thresholds.
- Target economic proxy is K=1 USD per $1 XAUUSD price change for 0.01 lot and incremental completed trade C=$0.20, as used in prior research; Coinexx Bid/Ask spread is already in entry and liquidation sides. Both values must be broker-verified before deployment.
- Five parallel chronological partitions are permitted **only for developmental calibration**. Each new partition causally replays the preceding seven calendar days, preserving exact source quote order. Wilder ATR is recursively initialized and may differ at machine precision from an uninterrupted nine-month chain; thus **source-exact monthly bytes is not whole-engine state-exact nine-month parity**. The stronger release gate remains an uninterrupted January–September pass and exact frozen-original-R9 ledger parity.
- Entry analysis records: completed trades, after-cost net cash/month, net/hour, trade retention, gross losses, cash CVaR95, drawdowns, cash threshold hit rates, duration, buy/sell ratio, and four lane-attribution counts. Multi-lane attribution overlaps and is **not** four trades per signal.
- January–September have already been heavily inspected. This is development **in-sample**. Do not call any one of the nine months untouched out-of-sample. Test a frozen policy on later independent quotes before MT5 promotion.

## Guardrails

Original compiled MQ5 and R9 v1.90 rollback unchanged. Do not alter the original source data, Coinexx/Dukascopy downloader, or tick simulator. Save only compact result/lineage metadata. **No automatic strategy promotion if net cash remains negative.** If this baseline loses over the nine months, use the failure to audit noise rejection and entry timing next; do not optimize cash exits to conceal a losing entry geometry.

This charter is a pre-result scope freeze. Subsequent calibration results must cite exact source hashes, code commit SHA, the chosen treatment of month boundaries, the held-fixed controls, and all losing months.
