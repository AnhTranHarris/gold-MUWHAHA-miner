# R9 V12 exact-millisecond micro180 — completed Jan–Sep recovery and QA

**2026-11-15 | Research-only | GitHub PR #50 draft | No order execution changes**

## Recovery after connection interruption

The prior response was interrupted after V12 research files were developed. Repository HEAD, source-preservation tests, and the nine-month pre-interruption source-proof CSV remained intact, but the local 9 derived trade-event ledgers and consolidated report were missing.

Recovered the **exact CI-tested** V12 Python research source (GitHub Actions artifact), re-read the existing original Coinexx monthly `*.csv.gz` sources **once** per month, and rebuilt **only derived trade-level** event ledgers. No tick-data libraries, sampled bars, or source archives were regenerated or uploaded to GitHub/Drive. An independent `verify_recovered_events.py` pass re-read all derived CSV.gz event ledgers and checked chronology, unique entry ordinal, exit ordinal/time relationship, hold duration, first-passage ordinal and all pre-interruption monthly row counts/source SHA/compressed byte sizes. **9/9 match exactly.**

| Month | Original quote records | Original V9 entries | Closed V9 trades | Derived ledger compressed bytes |
|---|---:|---:|---:|---:|
| Jan | 7,699,274 | 35,500 | 35,500 | 3,775,394 |
| Feb | 7,102,818 | 42,742 | 42,742 | 4,514,751 |
| Mar | 8,859,103 | 51,841 | 51,841 | 5,591,051 |
| Apr | 7,831,685 | 37,341 | 37,340 | 4,011,139 |
| May | 8,011,360 | 32,514 | 32,514 | 3,505,863 |
| Jun | 9,347,508 | 37,190 | 37,190 | 4,051,665 |
| Jul | 8,075,197 | 33,758 | 33,758 | 3,600,430 |
| Aug | 7,468,061 | 32,896 | 32,896 | 3,509,868 |
| Sep | 7,734,341 | 34,283 | 34,283 | 3,663,594 |
| **Total** | **72,129,347** | **338,065** | **338,064** | **36,223,755** |

The **count** reconciliation is independent of the old summary; do not misrepresent it as a second model that independently replayed all 338k individual tuples. Full source hashes checked against frozen V9 pins. One position remained open at April monthly reset.

## Frozen V9 millisecond-ordered lifecycle (simulated, NOT broker deals)

- Mean hold **6.6916 seconds**, median **3.475 seconds**, 90th percentile **15.765 seconds**.
- **65,580 / 338,064 (19.399%)** closed within 1s; **206,467 (61.073%)** closed within 5s.
- **195,127 (57.719%)** simulated stop exits; **127,247 (37.640%)** cash-0.10 harvest; **8,424** timeouts; **6,953** stale-quote; **313** preferred-cash cap.
- Average entry quoted Bid/Ask spread **19.772 cents per oz**, not fees or real fill slippage.
- **216** completed trades had at least one source quote later in the **same millisecond** as their entry and during the actual holding interval. Original source ordinals, not 1s OHLC, determined the path.
- **30,152** post-entry research trajectories censored by quote gap exceeding 2.5s; two at file-end. Marks after the actual exit are *counterfactual quote observations*, not realizable fills.

**Basket-lane counts, stop frequencies:** 1 lane **35,089 trades / 57.252%** stops; 2 lanes **166,640 / 57.643%**; 4 lanes **136,335 / 57.932%**. More concurrent lanes did not automatically reduce stops. No filtering authorized.

**Pre-entry quote intensity:** 0–4 prior-second quotes **148,238 / 56.050%** stops; at least 5 quotes **189,826 / 59.022%** stops (+2.973 percentage points). All nine months show the same direction, range **+1.081 to +4.155 pp**. This is an observational proxy, potentially confounded by volatility, session and spread, **not actual traded volume or a proven out-of-sample signal**.

**Strict one-second surviving-trade landmark:** Among **268,488** trades that remained open until a valid mark at or after the 1s landmark, **75,788** had source-ordinal observed adverse liquidation-price drift at least $0.10/oz within the first second. Their *later* simulated stop rate was **69.588%**, versus **50.649%** in the remaining 192,700. The 19.4% of trades closed before 1s are excluded; this selection effect, and absence of untouched OOS, forbid activating an automated exit.

The forward executable-side quote marks relative to original entry execution averaged -19.128c (250ms), -19.150c (1s), -19.342c (3s), -19.604c (5s), -20.151c (15s), -19.795c (60s); these are **not broker fill forecasts or a hold-longer rule**.

## MT5 DEMO telemetry observer — recovered and corrected

New standalone source: `Experts/GoldMuwahahaR9V12DemoTelemetryObserver.mq5`. It defaults OFF, checks `ACCOUNT_TRADE_MODE_DEMO`, filters symbol and magic, and never sends, changes or closes orders. Original trade callback receipt time and actual historical `DEAL_TIME_MSC` are kept distinct.

The interruption audit found two **real defects**, both fixed in this branch and regression tested:
1. Native `LOSS_DIAGNOSTIC` output contained **27 columns against a 26-column CSV schema**. Corrected to 26; static source arity regression added.
2. The Python validator sometimes returned `quality_pass_for_execution_inference=true` despite unmatched or ambiguous deals. Now it requires complete one-to-one uniquely matched order/deal coverage, zero loss rows and no duplicate events.

Official execution telemetry such as historical deal price, fee, commission, reason and partial fills can be captured **after a separately authorized DEMO-only setup**. No terminal MetaEditor compilation or real DEMO transaction session was performed; **request-submit-to-fill latency, actual broker slippage or real PnL have NOT been measured**. A request callback is not request submission time, and an OnTimer file write is not fill time.

## QA and disposition

- [Successful V12 CI #43755944373](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/actions/runs/43755944373): **71 micro180 tests (2 skipped), 40 V10/V11 tests, 9 telemetry tests**; 118 non-skipped passed, 0 failures. Immutable original R9/V8/V9/V10/V11 source hashes checked.
- Draft [PR #50](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/pull/50) targets V11, **not main**. No merge, no broker order activation, no protective-stop change.
- Recoverable conversation artifact: `R9_V12_ExactMs_JanSep_Recovery_Evidence_20261115.zip`, **36,422,054 bytes**, SHA-256 `cdd11498e987e5922dedfa999a5242d72597791ead1866f6c97bfd05f0ffe791`. Contains 27 entries: nine derived CSV.gz, nine monthly JSON, full aggregate, both source-proof CSVs, QA manifest/script, report, run logs and **latest** CI-tested Python source ZIP; **zero raw Coinexx quote archives**.
- All nine January–September 2026 months have been reused for research and are **in-sample**, not untouched OOS. This audit measures existing behavior, not a validated modification to trading policy.

**Next scientific gate:** Freeze the diagnostic features for later untouched dates; perform explicit spread/session conditioning and a user-authorized DEMO event-feed compile/QA before comparing any actual execution costs or contemplating a change to micro180 entries/exits. No new indicators, order-flow fiction or mass data downloads.
