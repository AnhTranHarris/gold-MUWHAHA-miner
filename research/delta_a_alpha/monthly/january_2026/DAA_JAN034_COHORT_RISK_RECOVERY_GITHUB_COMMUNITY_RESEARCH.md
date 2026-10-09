# DAA January Unit 034 — Reproducible Risk, Clone Admission and Recovery Research

**Status:** 54 completed and QA-checked January 2026 real Dukascopy Bid/Ask *original-source candidate-tape counterfactual* experiments. **NO promotion to the owner-whitepaper V1 EA.** All preserved January 032 and 033 data and immutable source are unchanged.

**Permanent architecture authority:** full original 14,232-character owner Google V1 whitepaper, `research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt`, L0–L7. L3 London/overlap/NY hourly plus independent Asia; L4 Watchdog; L5 native trend-within-trend; L6 conditional wrong-direction recovery; L7 physical governor. Do not rewrite this architecture or reduce it to entries from indicator shells.

## Data and model

- Exact original January Gamma 131E plus 131D/LEAN4/COLD64 source reconstruction from unit 032, **47,511 quote-side candidate trades**, 9,135,062 Dukascopy ticks from January 2026.
- Raw gzip SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`.
- Original raw-quote reference: net **+$93,425.311**, gross profit +$125,371.765, gross loss -$31,946.454, PF3.9244, max real-quote tick equity drawdown $56,921.60, 47,511 entries, 90.489% winners.
- Fixed 0.01 lot, **research assumption** 1 XAU oz per 0.01 lot and $0.02 additional ticket fee, no invented normalized spread, no loss-dependent sizing, no MT5/Coinexx margin or actual order accept/slippage certification. On a hedging account, details of order execution and close-by availability require broker and symbol checks.
- **Critical scientific constraint:** Frozen 131E candidate proposal tape. When an intervention rejects or liquidates a Watchdog ticket, the simulator DOES NOT yet rebuild the future parent/child admission stream from physically funded fast-child history. Therefore these are mechanically correct quote-side *sensitivity/counterfactual* results **not causally complete full-system deployable V1 performance**; the resulting original proposals may depend on hypothetical funded descendants. The source predates the later independent fully funded native and recovery layers. `stream_cohort_risk_034.py` is an overlay, not a replacement trading algorithm.
- Independent new recovery uses only previously completed M5 or M15 EMA context and already-seen quotes. It does not predict future price. It is **not** a source-exact recreation of preserved February 134K or later L6, only a bounded mechanism probe. First-touch stop variants are also probes.

## Full experimental matrix

**37 independent risk/admission and independent-recovery overlay cases**, plus **17 per-ticket first-touch stop cases**. Every scenario saved immediately as JSON plus its accounting tape NPZ. Original no-change run exactly reproduced 47,511 trades, +$93,425.311 and $56,921.60 max drawdown. All 54 cases passed audited QA (original-normal-close subset, actual quote-side first-touch stop P/L parity, completed-bar context, unchanged L3 hourly economics and exit chronology).

| Scenario | Net $ | Tickets | Gross loss $ | PF | Full-tick equity DD $ | Comments |
|:--|--:|--:|--:|--:|--:|:--|
| Unmodified original raw quotes | 93,425 | 47,511 | -31,946 | 3.92 | 56,922 | Unacceptable DD and loss concentration |
| Watchdog max **16 same-quote entries** | 69,921 | 15,796 | **-4,799** | **15.57** | **6,863** | Defensive gate; fails R9 velocity |
| Watchdog max 64 same-quote entries | 76,265 | 20,857 | -6,307 | 13.09 | 14,764 | Profitable lower-heat gate; fails R9 velocity |
| Watchdog max 96 same-quote entries | 79,385 | 23,399 | -7,192 | 12.04 | 17,610 | Profitable lower-heat gate; fails R9 velocity |
| Watchdog max 128 same-quote entries | 81,959 | 25,673 | -8,178 | 11.02 | 20,456 | Near R9 velocity |
| Watchdog max **192 same-quote entries** | **86,668** | **29,801** | **-10,045** | **9.63** | **26,148** | Best balance tested for >R9 SYNTH ticket velocity and low loss/heat; 20/21 positive days, 5/5 positive weeks and all five R9-beating weeks |
| Watchdog max 256 same-quote entries | 90,651 | 33,510 | -12,018 | 8.54 | 31,841 | Higher net/velocity at more loss and DD |
| Max 64 when observed spread >= $2 | 82,316 | 29,098 | -12,988 | 7.34 | 22,117 | Entry-known spread-conditioned permission; does NOT imply $2 is an optimized general rule |
| Max 192 plus Watchdog global cap 384 | 84,849 | 28,264 | -9,820 | 9.64 | 26,148 | Slower without material DD gain |
| Whole-WD forced close at -$2,000, cooldown 60s | 37,344 | 33,476 | -47,283 | 1.79 | 26,641 | **Reject: destroys net and realized losses** |
| Above plus independently confirmed 0.01-lot L6 recovery | 37,342 | 33,478 | -47,285 | 1.79 | 26,641 | 2 recovery trades, -$2.06; **reject** |
| Per-ticket $8 first-touch stop, M5 opposition required | 90,793 | 47,511 | -34,448 | 3.64 | 56,922 | **Reject: net/PF/loss worsen** |

See all exact variants in JSON and CSV, not only best configurations. **This search selected parameters using January outcomes**: parameter attractiveness is January-specific and must not be presented as blinded performance.

### Why the initial 'close all losers' and simple reversal systems failed

The original winning Watchdog children produce numerous small gains over an owned 30-minute parent lifecycle and can have adverse intralifecycle excursions. Closing entire cohorts on arbitrary dollar drawdown simultaneously realizes many otherwise recoverable positions; adding a rapid opposite-direction 0.01-lot trade does not offset hundreds of existing 0.01-lot same-direction tickets. The $2,000 cohort stop produced **19** closures and liquidated over 10,000 original child positions while collapsing portfolio PF to 1.79. The source's actual L5 and L6 opportunity sources, not a guessed generic opposite signal, must be restored for a meaningful native/recovery test.

The first-touch stop family included $3/$5/$8/$12/$16/$25 adverse executable displacement, 15s/60s age gates and completed-M5 or M15 reversal confirmation. Across **17** cases there was no Pareto improvement in net profit, gross loss and equity DD over the original source. Broad stops usually crystallized repeated losers before recovery; some increased drawdown.

## Original whitepaper system-wide candidates for physical replay — NOT promoted

1. **L1+L4+L7 – Price-time inventory admission, not loss-driven lot sizing:** The original grid event genealogy must limit physically funded *clone entries at one observed quote* and already-open **per-parent directional stress**. A single price level producing 538 nearly identical shorts is not 538 independent pieces of evidence. Preserve independent child signals, but permit deferred admission on **new genuine distinct price/tick events** only after re-evaluating the current H4/H1/M15/M5, already-earned Watchdog fast-child proof and broker margin. A deferred order is *not a free or backfilled fill*. Candidate state must expire.
2. **L4 – Funded earned-credit integrity:** Original four good ≤60s funded-child confirmations unlock future parents; rejected hypothetical children never unlock. Record child→parent→campaign genealogy and previously completed outcome/depth/time/P&L buckets per preserved April T2 science. Bad/slow outcomes relock per original source.
3. **L2+L4+L5 – Directional failure evidence bus:** Original H4 broad environment, H1 parent structure, M15 phase and M5 transfer control both Watchdog stop-new permissions and native trend-within-trend **opposite-direction eligibility**. Detect failed ignition (original L6 shadow contract, observed adverse movement), completed genuine structural transfer, local tick momentum and quote friction before any source-specific wrong-side campaign ownership change. Avoid 'all 4 EMA votes' stand-ins.
4. **L6 – Independent bounded recovery *after* confirmed failed source event:** Fixed 0.01 lot, separate entry/TP/SL, 1 per failed parent source event, no adverse averaging and no Martingale. Recovery must not simply place an equal hedge against the losing campaign. It should exploit a *new independently valid native/grid opportunity* following a failed break/reclaim; L7 must first reserve risk capacity and close/reduce invalid inventory as its own cause. Never claim recovery profit will erase previous loss or guarantee a positive recovery net.
5. **L7 – Signed risk, not only global count:** A global 640-short campaign has ~$640 per $1 rising Gold under research assumptions. Estimate conditional shock from completed observed volatility and executable spreads; stress funded portfolio at each admission, including L3 supplement and L6. Keep L3 hourly harvester independently fundable where its real risk fits; avoid using broad global drawdown thresholds that cut L3 for WD's errors. A stop-new/no-admission control may be less destructive than automatic cohort liquidation.
6. **L0 – Physical broker truth:** Bid for closing buys, Ask for closing shorts; MT5 `OrderCalcProfit`, `OrderCalcMargin`, hedging `PositionCloseBy` only if permitted, rejection/retcode, order queue/tick processing and fees/slippage all need source-preserved deterministic tests. A source candidate 640 cloned same-tick fills is **not** proof the broker can fill 640 executions identically.

### Quantitative promotion gates

The January canonical R9 SYNTH trade metric is **+$41,520.82 / 27,980 / -$2,071.61 gross loss / PF21.042778 / 87.13% win**. No 034 candidate beats all its criteria. Example 192 cap beats net, ticket count, win, and is far lower floating DD than unfunded raw original but still has roughly **4.85× R9 SYNTH gross loss** and PF less than half 21.04. Achieving R9 PF at the cap192 gross profit +$96,713 requires gross loss ≤$4,596, vs currently -$10,045 (a further ~54.2% reduction while preserving gross profit), *not established*.

Measured against R9 net for **the same January ISO weeks**, cap192 earns 1,147 / 6,577 / 16,990 / 19,297 / 42,657 USD (all 5 weeks above R9's 1,028 / 5,332 / 5,817 / 7,692 / 21,651). 20/21 R9 active days positive; 13/21 exceed R9 daily net. **Overfitting and Jan30 concentration remain.** Jan 1 five-minute readiness is not certified without December 2025 HTF context; Aug sealed, Sep reserved.

## External reconstructible community research, not performance evidence

- QuantConnect LEAN GitHub, actual framework code: [MaximumDrawdownPercentPortfolio.py](https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Risk/MaximumDrawdownPercentPortfolio.py) and [TrailingStopRiskManagementModel.py](https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Risk/TrailingStopRiskManagementModel.py). Useful **structural pattern**: risk decisions use live holdings; do not claim these parameters work for XAUUSD.
- [QuantConnect risk integration API](https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/risk-management/key-concepts): several risk models adjust targets between portfolio construction and execution, conceptually consistent with original L7. Must not overwrite owner V1 architecture.
- [MQL5 grid-system finite cycle, regime and CUSUM implementation](https://www.mql5.com/en/articles/21833): explicit risk cycles, observed regime shifts and adaptive spacing are reconstructible; its equities and algorithm are **not** validated against our January Dukascopy file, and the article's lot-sizing option violates fixed 0.01 lot.
- [MQL5 Chinese risk manager article](https://www.mql5.com/zh/articles/18918): entry-risk gate before opening and account drawdown protection; some demonstrated Martingale controls are **not admissible** in our V1.
- [MQL5 `OrderCalcProfit`](https://www.mql5.com/en/docs/trading/ordercalcprofit) and [hedging Close-By](https://www.mql5.com/en/docs/trading/positioncloseby) / [CTrade PositionCloseBy](https://www.mql5.com/en/docs/standardlibrary/tradeclasses/ctrade/ctradepositioncloseby), for quote, broker symbol/account checks. Opposite position opening can be prohibited or differently margined; an opposite hedge does not neutralize historical realized losses.
- [Freqtrade MaxDrawdown implementation](https://github.com/titouannwtt/freqtrade-ultimate/blob/main/freqtrade/plugins/protections/max_drawdown_protection.py): independently held position risk gates and cooldown patterns that can inform event-bus architecture, not proof of profitable grid recovery.
- [Reddit algotrading community](https://www.reddit.com/r/algotrading/comments/1dg1tqg/techniques_for_reducing_drawdowns/): breakeven and hedging proposals are user anecdotes, not robust evidence; our January exact tick tests show naive stops/reversals fail.

## Next source parity build / versioned monthly recording

**Next:** reconstruct ORIGINAL full funded L0–L7 events under a single broker-capacity ledger, using original frozen 049→051→075→084→119→131E Watchdog and February→March→April *unaltered native/recovery* helper source before changing their parameters. Compare unchanged original, physical original, each 034 hypothesis, and R9 SYNTH daily/weekly/monthly. Retain original parent/child ownership graph and chronological release of funds; shadow outcomes can never unlock physical parents. For Jan→July, append UTC session + hour/subphase, completed H4/H1/M15/M5 role, session grid cell/freshness, child depth, realized prior child P/L and hold buckets, signed open-ounce exposure, observed 1/5/15/60s displacement, executable spread, funded/denied reason, mark-to-market DD, R9 daily/week/month, and recovery parent lineage. Do not use calendar month as a model input. Holdouts August/September remain sealed.

This research is a **candidate-mechanism discovery** and **failed-hypothesis record**. Full V1 broker/economic parity **NOT CERTIFIED**; production EA unchanged.