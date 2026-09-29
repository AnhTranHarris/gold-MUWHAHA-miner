# BETA 014 — Corrected 0.01-lot candidate versus R9 control with BETA 013 prop-risk rules

**Date:** 2026-09-29. **Status:** ORIGINAL DUKASCOPY TICK REPLAY, NOT PROFITABLE, NO OWNER-APPROVED EA, NO MQL5. **Markets:** XAUUSD only. **August:** SEALED, unread. **Evidence:** `BETA_014_PROP_RISK_REPLAY.py`, `BETA_014_PROP_001LOT_FUNDED_RERUN.json`, `BETA_014_PROP_RISK_QA.py`, `BETA_014_PROP_RISK_QA.json`.

## Result in one sentence

The historical R9 feed-normalized control breached the $90,000 funded-equity floor on **2026-01-14 23:03:37.369 UTC**; R09_BETA_001_ADAPTIVE_IGNITION_ENTRY breached the **same floor on 2026-01-21 23:24:08.421 UTC**. **Both failed in January**, so under BETA 013 *neither opens another funded trade during the remainder of Jan–Jul.* The candidate survives roughly **7 days 20 minutes** longer on this feed, but cannot be considered a profitable or prop-firm-eligible strategy.

## Firm-style research rules actually enforced

- **Initial marked equity/balance:** $100,000. Exactly **0.01 lots**, 100 oz per standard gold lot assumed, hence **1 oz exposure**; a $1/oz price move translates to $1 of gross P&L for a 0.01-lot trade.
- **Per-deal fee:** **$0.01 when opening**, **$0.01 when closing**, equal to **$0.02 full round trip** per completed trade. As-observed Dukascopy Ask enters buys and Ask exits shorts; Bid enters sells and exits buys. Price costs therefore include observed actual spread. **Zero additional slippage assumption**, not a claim of broker parity.
- **Same entry/hold/exit geometry as BETA 009–011:** R9 completed S1 momentum plus completed M5 ATR, while R09_BETA_001 uses the additional 250ms/1s/5s early momentum, absolute $1.00 spread cap and spread/recent-range ≤0.65. Fixed Hold/Exit $0.30 stop measured from observed bid/ask, trail activation $0.10, trail distance $0.03, 30-second maximum hold, one simultaneous position shared across specialists, up to three same-minute opposite rearms when applicable.
- **Planned per-trade risk veto:** do not enter when estimated quote-side stop loss (including spread and both fees) would exceed 0.25% of current marked equity. **Never vary lot size**; zero risk-cap vetoes observed before either terminal stop.
- **Research day:** 17:00 America/New_York (DST aware), with each new day's reference fixed to the **larger of opening balance and marked equity**. No new trades after daily equity slips more than **$4,000** from reference; compulsory liquidation at **$5,000** daily loss if this threshold is touched. Neither day cap activated before termination.
- **Overall permanent terminal gate:** current marked equity ≤**$90,000**, exit at the **actual next available model tick's executable quote** and permanently terminate funded replay. **No simulated funding refills**. Account-wide daily and total floors operate on FLOATING equity, not just closed balance. A 100:1 illustrative margin sufficiency condition was also checked but never bound before the $90k floor; **actual Coinexx leverage, stopout, stop-level and sessions were not observed**.
- **Market availability proxy:** only available observed Dukascopy ticks; no new trade in an assumed 16:55–17:05 New York rollover window and on Fridays after 16:55 New York. **This proxy cannot establish exact Coinexx XAUUSD tradable hours.**
- **News gate NOT EVALUATED:** no point-in-time verified economic-calendar event file was attached. BETA 013's proposed ±5-minute high-impact event exclusion was not silently fabricated, nor considered proof of compliance.

## Actual risk-constrained funded replay

| Measurement | Feed-normalized R9 control | R09_BETA_001 Adaptive Ignition |
|---|---:|---:|
| Funded trades before permanent stop | **13,429** | **14,719** |
| Winning trades before stop | **2,707** | **3,876** |
| Winning rate | **20.1579%** | **26.3333%** |
| Gross profit after fee allocation | +$601.38 | +$951.01 |
| Gross loss after fee allocation | −$10,603.76 | −$10,951.58 |
| Net P&L | **−$10,002.39** | **−$10,000.58** |
| Final simulated balance | **$89,997.61** | **$89,999.42** |
| Lowest tick-marked equity | **$89,997.61** | **$89,999.27** |
| Maximum tick-marked equity DD | **$10,002.39** | **$10,000.73** |
| Maximum closed-balance DD | $10,002.39 | $10,000.58 |
| Day-level soft stops / hard stops | **0 / 0** | **0 / 0** |
| Maximum observed daily equity drawdown from fixed reference | **$1,281.88** | **$1,474.99** |
| Forced terminal-liquidation trades | **1** | **1** |
| First terminal breach, UTC | **2026-01-14 23:03:37.369** | **2026-01-21 23:24:08.421** |

**Decimal caveat:** Summing individually printed gross profit/gross loss values rounded to cents may differ from the independently rounded net by $0.01. Values were accumulated at the raw Dukascopy quote precision, not rounded per execution to mimic every broker's trade ledger.

## Critical comparison: unequal survival windows can mislead

The candidate has more wins over its **longer** funded lifespan, but that **does not demonstrate an absolute winning-trade improvement for the same calendar period**. Through the last *full shared New-York risk day*, **2026-01-13**:

| Same-date statistic | R9 feed-normalized control | Adaptive Ignition |
|---|---:|---:|
| Trades | 13,422 | 8,746 |
| Wins | 2,707 | 2,232 |
| Win rate | 20.1684% | 25.5202% |
| Net P&L | −$9,979.02 | −$6,021.01 |
| Balance | $90,020.98 | $93,979.00 |

The candidate **lost less and had higher win rate over this matched window**, but **had fewer absolute wins**. It remains a research hypothesis, not a >10%-win-count formal entry breakthrough.

## Jan–Jul prop-feasible calendar (no capital replenishment)

- **January 2026:** both strategies traded, lost their $10,000 account drawdown budgets, and were permanently stopped on the separate January UTC timestamps above.
- **February, March, April, May, June and July 2026:** **zero additional funded trades and $0 additional funded P&L for each strategy** under the permanent $90k floor. No later market data needed opening: the stop state is immutable. This run **fully reads and validates January's 9,135,062 ticks** and its gzip SHA; it does **not** purport to have reread the February–July gzip files when no further funded execution was permitted. Previously preserved BETA 011 month-by-month unbounded-credit results remain **SHADOW_DIAGNOSTIC**, not prop-funded outcomes.

## QA and scientific limits

- Independent QA checked nine invariants: January SHA and row count, contract/fee, two winter/DST 17:00 NY day resets, Friday close, P&L conservation, trades/wins conservation, actual permanent stop and future zero-trade months, plus matched-calendar comparison. The replay was run twice with identical summaries.
- The Python R9 **feed-normalized** control is not the actual Coinexx R9 REAL MT5 account: Dukascopy and Coinexx have different spread paths; the historical broker-specific `InpMaxSpreadPoints=25` filter was disabled in this same-feed Python control. Hence the exact historical R9 REAL −$50,285.28 figure is **not** this scenario's baseline.
- The news filter was not evaluated. Broker margin/leverage, spread treatment during locked markets, stopout, swap, any slippage/latency, dollar/contract mapping changes, execution-rejected trades, and exact Coinexx trade sessions remain unverified. No owner authorization to write MQL5 was provided.
- An after-the-fact cross-calendar comparison is descriptive only; January is already the search/development set, so no untouched forward statistical validation is claimed. **August remains SEALED.**

## Outcome / next research direction

**R09_BETA_001 does NOT qualify as prop-survivable.** It retains some valuable earlier entry-quality evidence, but the economically dominant bottleneck remains cost/spread/entry-edge adequacy, not the lack of a daily shutdown rule. The prop-risk governor prevents catastrophic hypothetical negative equity; it does not create profitable expectancy or certify the bot for a prop account. Continue cost/entry research using the exact same-file, same-time, same-risk-budget comparison, and preserve 0.01 lot until the owner decides otherwise. 

**BETA lineage:** documentation + original-tick research only; `approved_beta_ea=null`, `current_approved_baseline=null`. This unit is not an owner-approved EA nor a formal new winning breakthrough.