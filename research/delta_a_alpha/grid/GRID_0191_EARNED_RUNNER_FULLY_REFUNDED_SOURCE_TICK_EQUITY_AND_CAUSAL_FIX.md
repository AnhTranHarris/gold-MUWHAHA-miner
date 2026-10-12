# GRID0191 — causal single-funded 30/90 → 90/210min earned-runner mechanism and quote-full-equity research (UNPROMOTED)

**Purpose:** continue owner-governed `delta-A-alpha` V1 high-performance research. Scientific cursor J0183 and runtime EA trading_enabled=false remain unchanged; August is SEALED. 75% of R9 SYNTH multi-horizon *whole broker account* economics not achieved. **Not an investor success report**.

## Complete reproducible science, original source, parameter matrix

[**Download full GRID0191 source, 62 runnable or provenance files, original J179F offers, 4-month matched portfolios, full original Bid/Ask equity tick risk, source hashes and 23-plus experimental tests**](https://drive.google.com/file/d/17oZPkZsXinlG-giqc4Xkna1t94pV_D47/view).

ZIP SHA256 **`c8a1e95597884ea10d6ee6adfbfeca3fb5f14b1eabd6d9e29ed4af1949434568`**; size **2,753,028 bytes**, testzip passed. Raw original Dukascopy source files have not been altered or duplicated into the ZIP. They remain referenced by exact original source SHA256 in manifest. The 4-month original source quote path used **31,420,982 tick records**.

**Engineering discovery:** original source helper shortcut `g.valid` included future scheduled `exit_valid` even at the T1 invitation (and earlier extension experiments gated on future quote availability). GRID0191 corrected to entry freshness only at the time of reservation, and selected extensions only at the actually observed original scheduled exit tick. Required future quotes are used ONLY for subsequent settlement of physically held tickets. Preserve corrected no-future-availability engine over historical contaminated helper; do not promote original shortcut.

## Testable mechanism: earned continuation while reserving actual capital

New L5 **earned runner extension**: at the first real 30/90-minute Bid/Ask exit quote, examine the position's *already observed* realized-equivalent closing value. If >= fixed +$8/oz source quote PnL, hold **the same ticket for another 120 minutes** subject to known NY 17:00 day boundary, with one global 8-position cap, original T1 10-second pending invitation, observed T2 actual source quote, sole source-exit cost +$0.52/oz equivalent, L4 prior genuinely closed funded 4h transition credit, source structural roles and spread. No new ticket, Martingale, loss-dependent sizing, early knowledge of future payoffs, or month selector. Compares simultaneously to unextended control with same original source and global funding ledger.

### April–July historical quote proxy (NOT real Coinexx cash)

| Metric | as-of NY17-safe 30/90 control | NY17-safe + 120m earned winner runner |
|---|---:|---:|
| Quote USD/oz-equivalent net | +2,975.236 | **+4,584.007** |
| PF | 2.2357 | **2.8294** |
| Funded closes | 741 | 703 |
| Positive funded UTC close hours | 109 | 103 |
| Positive NY17 close days | 44 | 40 |
| Gross loss (lower is better) | 2,407.795 | 2,505.699 |
| Full original-tick max intramonth floating equity drawdown (lower is better) | 355.72 | 425.44 |
| Worst intraday DD | 237.375 | 258.32 |
| Worst intrahour DD | 192.88 | 192.88 |
| Max concurrent funded tickets | 8 | 8 |
| Source quote max hold | 90.36 minutes | 210.12 minutes |

New policy improved source quote net +54% but **did NOT improve funded trade velocity, gross loss, drawdown, winning-day rate, or positive-hour count**, and improved mainly May/June rather than being robust per month. A +0.52 USD/oz assumption is only source stress, not Coinexx order accounting. All April–July months had already been inspected; a set of post-hoc 12/15/20 threshold follows is explicitly **not** independently frozen holdout.

The original R9 SYNTH April–July count is 116,854 positions. Even 703 current quote-only trades = **~0.60%** of the R9 completed-trade proxy, well short of owner's soft 75% multi-horizon objective. The source quote PnL units **cannot be compared** as MT5 account-dollar profit until verified 0.01-lot broker contract specs, commission, margin and MT5 fill parity are available.

This mechanism is a **conditional low-frequency runner** only; it cannot substitute for profitably executable independent 10–30-second L3 core. The next substantive program must recover working original January/February L1/L3 high-velocity source **logic** and true paid-parent-child L4 genealogy, not simply quote retrospective selected winners; supplement with reusable regime-aware harvesting if full quote-side costs and L7 account margins validate it. One global risk governor and completed H4/H1/M15/M5 roles remain frozen.

### Evidence rules

- No promotion; no rewriting raw R9/Dukascopy data, no new Git branch, no August use.
- Full ZIP retains losing variants and structural-stress parameters for reproducibility, not long investor reports.
- MQL5 public research [finite restartable constrained grid](https://www.mql5.com/en/articles/21833), [ATR time-dependent exit research](https://www.mql5.com/en/articles/16213), and TradingView session-VWAP examples informed reconstructible hypotheses, **not proof of financial results**.
- Owner original frozen [whitepaper](../whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt), [verbatim 75% soft-aspirational directive](../governance/OWNER_75PCT_FOUR_HORIZON_SOFT_GOAL_ADDENDUM_VERBATIM_2026_10_11.md), J0183 original scientifically accepted state take priority.

**Owner notification gate:** until an integrated L0–L7 broker-cash comparable V1 genuinely reaches >=75% relevant financial performance on aligned hour/day/week/month as specified, this checkpoint must not be described as the requested investor performance milestone.
