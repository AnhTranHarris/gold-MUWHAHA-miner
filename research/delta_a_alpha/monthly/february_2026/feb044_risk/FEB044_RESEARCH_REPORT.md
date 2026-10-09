# FEB044 — February vertical-grid risk-concentration and market-state discovery

**Research status:** COMPLETE exploratory retrospective February source-proposal testing; **STRICT $10K GROSS-LOSS AND $10K FULL-TICK-DD TARGETS NOT MET**. January/February source lineage preserved. Do not call this fully funded owner V1, deployable EA, or month-blind success.

## Owner objective and final evidence

Hard target: monthly profit ≥$200,000; ≥12,000 completed trades; absolute gross loss < $10,000; true tick-equity DD < $10,000.

| Metric | Frozen FEB043 balanced (comparison) | FEB044 strongest verified joint improvement | Hard target | Result |
|---|---:|---:|---:|---|
| Net | +$209,415.695 | **+$212,710.922** | ≥$200,000 | PASS in source model |
| Trades | 39,270 | **30,923** | ≥12,000 | PASS in source model |
| Gross loss | -$56,733.545 | **$-23,464.931** | >−$10,000 | **FAIL** |
| Profit factor | 4.6912 | **10.0651** | track | improvement |
| Full quote-path equity DD | $25,651.986 | **$23,272.669** | <$10,000 | **FAIL** |
| Max open | 1,536 | **1,536** | lower preferable | unchanged |
| Winning trade pct | n/a | **81.19%** | track | descriptive |
| Profitable days/weeks | 12/14, 4/4 | **13/15, 4/4** | consistency | descriptive |

Gross loss reduction versus FEB043 balanced: **58.64%**. Exact equity-DD reduction: **9.28%**. Net increased $3,295.227 while trading volume fell 21.26%. An additional fixed $0.20 per trade leaves $206,526.322 net; extra $0.50 leaves $197,249.422. Fee perturbation is not an executable broker-slippage simulation.

## Fully recovered sources and methodology

- Original owner V1 *unabridged* whitepaper (not a substitute short spec): `research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt` on active `delta-A-alpha`. All original eight roles L0→L7, including separate Asia geometry, complete H4/H1/M15/M5 structure, hourly L3, authentic paid Watchdog genealogy, native trend routing, conditional recovery, and global physical governor remain mandatory.
- February Dukascopy `XAUUSD_DUKAS_2026_02_ticks.csv(3).gz`: **7,538,339** ordered ticks; SHA-256 `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`. Last 3,900,880 January history quotes supply context; original January SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`; combined 11,439,219 tick equity replay.
- Fixed 0.01 lots, Bid/Ask executed sides, $0.02/model trade, research account $100,000, *modeled* margin/leverage and up to ten new admissions per second. Original FEB041→FEB043 source proposals and first-touch exits retained. No changing lot size, DCA, Martingale, weekend or date identity trigger.
- **459** recorded scenario evaluations across 9 screening families (some repeat settings); scripts and original screen outputs saved for reconstruction. A clean FEB044 selected-case replay (`feb044_reference_replay.py`) exactly reproduced profit, gross loss, trade count and max equity DD, then separately computed tick equity from raw position cashflows and all 11.4m quote observations; discrepancies within ≤0.002.

## Mechanism discovery: in-sample and reconstruction limits

1. **Source and subphase conditional permissions**: suppress exposure in original S19 hour phases 0,1,4,5 and S17 phases 1,5; suppress source S25 if *previous completed 10-minute range* is within [12,16) in original price units; suppress S21 previous range [4,6) and S23 previous range [12,16). No date-specific triggers.
2. **Selective original opportunity expansion**: source S22 previous completed range bands [0,4) and [24,48); S24 [0,12); S26 [8,16). These are original source-generated events and not new “hallucinated” fills. S22, S24, S26 opportunity identification is fitted to February and *not* validated across other months.
3. **L3 cohort ownership / source-level exposure**: total account cap 1536, S22 concurrent cap 768, S27 *combined cross-phase* cap 64; retain prior S27 phase caps, S25 original phase budgets, and actual completed-child Watchdog unlocks only for truly accepted positions inside the model. The governor does not use unbounded averaging or loss-dependent sizing.
4. **First-profit touch**: original FEB043 S21 target $20, S23 $15, S25 $25, S27 $50 per fixed 0.01 lot and S25 phase1 $15 / phase5 $10. Executed only at subsequent true quote-side first touch. No future outcome as an entry signal.
5. **Rejected experiments preserved**: individual premature adverse stops at $2–$30 frequently **increased gross loss or destroyed net**; naive hard caps often reduced volume/profit below target. Masks were selected on full February history. There is no statistically blind winning selector.

## Causal inventory and risk migration diagnosis

The original FEB043 full-tick maximum DD was about $25,652 during **February 23**, with 892 original S25 longs floating roughly −$20,163; their eventual aggregate settled P/L was just +$910. Under other causal source masks, the max-DD event moved to **February 2**, when 1,024 S27 shorts were temporarily −$22,061 before eventually contributing +$12,089. Expanded S22 source without a cap created a **February 11** basket of 1,325 longs floating roughly −$20,757 and raised exact DD to $33,087, despite attractive closed-trade net. A source-governor prevents that migration but moves the drawdown back to a large S25 cohort on February 20. These data confirm **directional position concentration and overlapping campaign ownership**, not a simple “bad stop threshold,” as the current main obstacle.

## Community ideas researched (conceptual, not copied/opaque strategies)

- MQL5 English finite restartable constrained grid and observed-equity circuit breaker: https://www.mql5.com/en/articles/21833 . The paper's equity-risk concept does not certify its mathematical assumptions for our nonlinear overlapping campaigns; we use actual quote equity instead.
- MetaQuotes Chinese drawdown monitoring/exit mechanics: https://www.mql5.com/zh/articles/18038 . Its Martingale component is **explicitly excluded** from our owner V1.
- MQL5 Japanese floating vs closed-trade drawdown attribution: https://www.mql5.com/ja/articles/2704 ; Japanese daily drawdown limiter: https://www.mql5.com/ja/articles/15199 .
- Reddit multi-strategy correlated heat risk: https://www.reddit.com/r/algotrading/comments/1rtwnfm/approaches_to_risk_management_and_order_size/ . Community anecdotes are hypothesis generators, not quantitative validation.
- TradingView observable volatility-regime transformation examples: https://www.tradingview.com/script/Lwf3gmiQ-Structural-Volatility-Expansion-Strategy/ . Independent completed-candle features only; do not replace owner H4/H1/M15/M5 with simplified MA votes.

## Honest scientific disposition

**Retain as a research frontier only, not an accepted deployable V1 improvement.** Exactly two of the owner's four hard February goals pass in the source model. The remaining shortfall is **$13,464.931 in gross loss** and **$13,272.669 in full-tick DD**. Numerically optimizing an exposed historical February tape by adding narrower date-like state masks would amplify overfit. FEB044 still relies on the inherited original source proposal tape that fails to regenerate every unfunded Watchdog descendant and does not independently certify native L5, bounded L6 or Coinexx full L7 broker fills/margin/stop-out. It is not a small-capital EA.

**Next appropriate gate:** reconstruct genuinely funded parent-child proposal progression on accepted trades with physical L0–L7 account/broker execution under 033; calculate real-time source/side/price-cell pending adverse heat and forward-only source quality from already-closed funded outcomes; recalibrate state-conditioned risk thresholds only using earlier time partitions, then test February across genuinely unseen regimes. Do not use August 2026 (SEALED) or September (RESERVED).