# January 032 — Original Source-Chain Dukascopy Bid/Ask Replay and R9 SYNTH Correlation

**Classification: COMPLETE source-code replay and quote-side execution forensic; NOT full owner-whitepaper funded L0–L7 portfolio certification.**

**Owner's binding whitepaper:** [complete original verbatim on the V1 hardlock GitHub branch](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt). Its original L0–L7 roles remain unchanged. January 032 does not replace those layers. This historical January Gamma 131E source predates the complete February/March/April whitepaper integration; it is recovered evidence, not a claim that all V1 trading mechanics have been restored.

## 1. Scope and hard constraints

- Input original Dukascopy 2026 January gzip: `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`, SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`, **9,135,062** ordered ticks.
- Original frozen January source anchor: GitHub `carson/r9-gamma-02-jan-grid-milestone` commit `e9189398fcf4fc47d7e2940adec54731ae047c31`. Restored 131E helpers plus 019/024/049/051/053/075/084/087/119/131A/131D LEAN4 and funded-cap equity accounting. One missing dependency `gamma02_ny_campaign_inventory_portfolio_001.py` was manually recovered from its exact pinned GitHub displayed logic; the unchanged P75 run **exactly reproduced historical metrics**, which is a source-equivalence regression, not a byte-for-byte hash proof for that individual helper.
- Same original helper with only `stmr_base.materialize` switched from session P75-midpoint synthetic Ask/Bid to **recorded actual Dukascopy ask_raw/bid_raw**. That also changes states, parent eligibility and price first-touches, not just reprices a fixed ticket ledger. Default assumed fixed 0.01 lot=1 troy ounce and $0.02 modeled fee/trade. Broker commission, slip, margin, swap, stopout and netting/hedging were not certified.
- Start research clock: **2026-01-01T00:00:00Z**; first actual quote 2026-01-01 23:00:00.596 UTC. December 2025 pre-T0 completed HTF history is absent, so the **five-minute readiness rule is NOT certified**. First 131E strategy funded-entry timestamp in research source: `2026-01-02T12:45:00.044000+00:00`. An absence of valid signal does not mandate a forced fill.
- January is already known and fitted historically: **retrospective chronological as-of backtest, not pristine blind**. August remains sealed, September reserved.

## 2. Headline: exact historic reproduction versus real executable Bid/Ask

| Metric | Unchanged source P75 replay | Same source real Dukascopy | R9 SYNTH canonical Jan |
| --- | --- | --- | --- |
| Net | $194,425.92 | $93,425.31 | $41,520.82 |
| Trades | 80929 | 47511 | 27980 |
| Gross loss | -$3,642.86 | -$31,946.45 | -$2,071.61 |
| PF | 54.372 | 3.924 | 21.043 |
| Win rate | 98.03% | 90.49% | 87.13% |
| Expectancy | $2.40 | $1.97 | $1.48 |
| Balance DD | $451.92 | $13,171.86 | $3.41 |
| Floating equity DD | $57,139.20 | $56,921.60 | Not comparable |
| Max open | 640 | 640 | Not comparable |
| Days positive | 21/21 | 20/21 | Reference |
| Weeks beating R9 net | 5/5 | 5/5 | Reference |


**Source accounting conflict:** archival R9 daily/week `r9_synth_jan_daily_weekly.json` reports January R9 gross loss -$1,827.87 / PF23.715 with net +$41,520.82 and 27,980 trades. The later canonical MT5 ledger reports gross loss **-$2,071.61 / PF21.0428**, with identical net/trades. **Canonical MT5 gross/PF wins for MONTHLY**, while historic daily/weekly breakdown uses source's own net and trade rows. Don't silently combine per-day old loss with monthly canonical loss.

## 3. Daily scorecard — original 131E same-source actual Bid/Ask against R9 SYNTH

| Day UTC | Real-quote 131E net | Real-quote trades | Real-quote gross loss | R9 SYNTH net | R9 trades | Beat R9 net? |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-01-02 | $1,147.42 | 95 | $0.00 | $1,027.95 | 1083 | YES |
| 2026-01-05 | $1,562.73 | 285 | -$2.11 | $1,304.58 | 1317 | YES |
| 2026-01-06 | $796.72 | 249 | -$162.16 | $906.38 | 1105 | NO |
| 2026-01-07 | $150.87 | 584 | -$589.66 | $1,163.88 | 1243 | NO |
| 2026-01-08 | -$2.84 | 130 | -$89.28 | $1,052.15 | 1175 | NO |
| 2026-01-09 | $4,069.03 | 1269 | -$203.64 | $905.34 | 988 | YES |
| 2026-01-12 | $7,174.48 | 415 | -$64.12 | $1,287.71 | 1336 | YES |
| 2026-01-13 | $9,238.39 | 1563 | -$411.05 | $1,183.15 | 1174 | YES |
| 2026-01-14 | $9.23 | 11 | -$3.35 | $1,110.96 | 1196 | NO |
| 2026-01-15 | $184.21 | 339 | -$284.02 | $1,110.54 | 1259 | NO |
| 2026-01-16 | $383.42 | 311 | -$179.47 | $1,125.02 | 1130 | NO |
| 2026-01-19 | $4,890.47 | 1022 | -$58.41 | $743.89 | 783 | YES |
| 2026-01-20 | $2,196.09 | 736 | -$387.31 | $1,009.98 | 1127 | YES |
| 2026-01-21 | $4,297.20 | 4547 | -$738.89 | $2,612.38 | 1741 | YES |
| 2026-01-22 | $6,611.25 | 523 | $0.00 | $1,589.48 | 1437 | YES |
| 2026-01-23 | $1,553.26 | 197 | $0.00 | $1,736.69 | 1499 | NO |
| 2026-01-26 | $12,116.74 | 1495 | -$885.79 | $2,979.62 | 1862 | YES |
| 2026-01-27 | $3,569.41 | 512 | $0.00 | $2,554.57 | 1781 | YES |
| 2026-01-28 | $3,815.41 | 585 | -$193.24 | $3,502.79 | 2049 | YES |
| 2026-01-29 | $2,760.17 | 342 | $0.00 | $5,721.74 | 1484 | NO |
| 2026-01-30 | $26,901.67 | 32301 | -$27,693.96 | $6,892.02 | 1211 | YES |


Full daily CSV contains source-tagged PF, win, expectancy, historic P75, daily raw-R9 deltas, raw market-state context and tick counts. Unlike the historic P75 claim, January real-quote V1 131E has one loss day, **Jan 8**. Days beating R9 net: **13/21**; not every day. Sum checks passed.

## 4. Weekly scorecard

| ISO week | Raw 131E net | Raw trades | R9 net | R9 trades | Raw excess |
| --- | --- | --- | --- | --- | --- |
| 2026-W01 | $1,147.42 | 95 | $1,027.95 | 1083 | $119.47 |
| 2026-W02 | $6,576.51 | 2517 | $5,332.33 | 5828 | $1,244.18 |
| 2026-W03 | $16,989.72 | 2639 | $5,817.38 | 6095 | $11,172.34 |
| 2026-W04 | $19,548.27 | 7025 | $7,692.42 | 6587 | $11,855.85 |
| 2026-W05 | $49,163.39 | 35235 | $21,650.74 | 8387 | $27,512.65 |


**January 30 alone (raw):** net $26,901.67, 32,301 trades, loss -$27,693.96. Shares: **28.8%** of month net and **68.0%** of all trades. Do not deploy Jan30-specific if-statements.

## 5. Actual-quote tick and trade quality assurance

- Exact normalized-P75 original source rerun matched `L35_C640` historic **+$194,425.92 / 80,929 trades / PF54.3718 / -$57,139.20 floating DD** (same model-data source and normalized spread).
- Raw-quote entry/exit ledger contains **47,511** records; **13,087** unique entry tick indices. **34,424** entries reuse an observed tick; maximum recorded multiplicity **640 positions on one tick**. Original Watchdog's authorized synchronized renewal scaling causes same-tick multiplicity, but it must be backed by actual broker order fills and global margin; passing reconciliation alone does not certify execution.
- Maximum individual-trade side P&L reconciliation discrepancy: `7.105e-15` USD; no negative/zero elapsed-position chronology violations. All 21 daily and five weekly scorecard sums reconcile to monthly total.
- Original 131E candidate generation constructs parent child outcomes and applies a cap downstream. Admission can be influenced by potential winning children that never become physical positions after cap. **This is the blocking funded-genealogy certification gap.**
- Its Watchdog `C` cap is **not identical to total account position cap**: `L35_C240` still registers max 512 combined open positions because supplementation uses an independent cap512 path. Must enforce one account-wide physical governor before marketing or demo deployment.

## 6. Whole-source, January-only mechanical refinement experiments

### 6A. Existing allowed source cap and renewal-layer parameter sensitivity (20 variants)

`JAN032_RAW_131E_CAP_LAYER_SENSITIVITY.json`: original session/HTF/Watchdog source paths, actual Bid/Ask, no new signal. Depth25 at WD cap640 returned **+$93,815.99** vs depth35 **+$93,425.31**. The higher depth therefore **did not improve January real-quote quality**. Reducing Watchdog cap from 640 to 240 reduced recorded equity heat from ~$56.9K to ~$21.3K at substantial net/velocity cost; note combined max open remained 512. All this is **January selection only, NOT a recommendation to choose depth25 as globally optimal**.

### 6B. Unmodified original per-child renewal quantum, adjusted as a static source parameter

| Candidate | Real-quote net | Trades | Gross loss | PF | Win | Equity DD |
| --- | --- | --- | --- | --- | --- | --- |
| R9 SYNTH canonical | $41,520.82 | 27980 | -$2,071.61 | 21.04 | 87.13% | Not comparable |
| Original 131E P75 | $194,425.92 | 80929 | -$3,642.86 | 54.37 | 98.03% | $57,139.20 |
| Original 131E RAW | $93,425.31 | 47511 | -$31,946.45 | 3.92 | 90.49% | $56,921.60 |
| Existing quantum $1.80 | $109,342.01 | 37644 | -$22,620.35 | 5.83 | 91.17% | $57,360.40 |
| Existing quantum $2.80 | $112,662.67 | 33385 | -$25,854.21 | 5.36 | 89.83% | $57,744.24 |
| Entry-spread quantum floor 1.0x | $95,563.92 | 42083 | -$28,632.31 | 4.34 | 89.87% | $57,764.20 |
| Entry-spread quantum floor 1.5x | $112,744.19 | 41882 | -$28,039.22 | 5.02 | 89.40% | $57,674.65 |
| Entry-spread quantum floor 2.0x | $109,678.83 | 31598 | -$20,098.92 | 6.46 | 89.62% | $56,987.21 |


### 6C. One-line experimental quote-aware renewal quantum floor

Original 131E `q=int(QMAP[b10])` was replaced **only** in isolated research by `q=max(original_q, k × first-parent observed Ask–Bid spread)`. It uses *the first candidate's already-known quote*, not future MFE, price path, market closure outcome or month identity. Exact textual diff is `JAN032_PROPOSED_ONE_LINE_SPREAD_QUANTUM_PATCH.diff`; rerun script refuses to patch if the original line changes. All other original source helpers stay unchanged. This is not promoted or merged to production.

`k=1.5`: net **$112,744.19**, **41,882** trades, gross loss **-$28,039.22**, PF **5.021**, win **89.40%**, floating equity DD **$57,674.65**, 20/21 positive days and 5/5 weeks ahead of R9 net.

`k=2.0`: net **$109,678.83**, **31,598** trades, gross loss **-$20,098.92**, PF **6.457**, win **89.62%**, balance DD **$6,874.35** and floating DD **$56,987.21**. Less volume and not a universal win.

**Verdict:** the first-parent spread-aware quantum is a **reconstructible Jan-positive hypothesis** to test unchanged in later chronological development. Neither variant beats every R9 SYNTH metric and neither corrects the original funded-child-credit flaw. The original system remains the fallback and these parameter modifications are isolated, NOT approved replacements.

## 7. Jan–July causal market-state correlation and implementation blueprint

January descriptive daily Pearson correlations:

- Actual raw-quote replay daily net vs R9 SYNTH daily net: **r=0.673** across all 21 days, **r=0.235** excluding January 30.
- Daily realized median completed M5 candle range vs raw net: **r=0.779** (all), **r=0.197** (without Jan30).
- Correlation is DESCRIPTIVE; same-day future observations and `observed_next_hour_opportunity_rate` are **forbidden at entry**. Only *prior completed* bars, prior closed results and quote-observed microstate are eligible causal execution inputs.

Save `JANJUL_REGIME_CORRELATION_AND_V1_IMPLEMENTATION_SCHEMA_032.json` as the common contract for upcoming 2026 February–July month-by-month comparison. It requires source hash/commit, layer and campaign ownership, session/hour/subphase, H4/H1/M15/M5 distinct roles, spread and quote-known supply, real funded first-parent/child genealogy, previous completed child P/L and hold, wrong-direction recovery causal evidence, account floating heat and physical per-session margin. All dates are **evaluation partitions only**, never strategy conditions. Future months are explicitly **NOT executed in this 032 unit**; no invented forward results.

Creative carry-forward hypotheses, NOT proven: (a) per-parent quote-friction renewal quantum, (b) true funded child transition/relock, (c) hourly first-passage session geometry and separately owned Asia, (d) HTF direction-inside-M5 transfer/retest native routing, (e) actual state-conditioned wrong-direction recovery, (f) global budget with shadow candidate intelligence. These must **interact through original whitepaper L0–L7**, never flatten into independent sleeve ensembles.

## 8. Deployment readiness, source conservation and next acceptance gate

**January 1, 2026 as-of start is historical**, not pristine blind. First actual market quote is near Jan 1 23:00 UTC; initial quote ~$4.204 spread. Jan 1 5-minute operational readiness is not certified because December completed HTF history is unavailable; first original 131E funded entry in replay occurs Jan 2 12:45 UTC. The five-minute contract means ready to accept a fully qualified trade when valid quote/history/broker state exists, **never forced five-minute profit**.

**Do not publish any claim that this unit is the complete funded whitepaper EA.** Original Gamma131E predates later February/March/April enhancements and does not certify the complete L5 trend-within-trend native engine, L6 physical recovery, or account-wide L7 funded capital/margin. The correct follow-up is reconstruct full original L0–L7 economics using the pinned 131E/134K/135/136 sources and verify funded-accepted genealogy on a single tick ledger; then rerun January with real Bid/Ask and compare all dates/metrics before September/August future holdouts are considered.

**Artifacts:** Scoreboard XLSX with Daily, Weekly, Monthly Frontier, Risk Sensitivity, Jan–Jul Register and Methodology sheets; complete quote-ledger CSV, day/week/month CSVs, 20-case cap/depth sweep and causal-quantum comparison JSONs, original-source helper chain, SHA256 manifests. Raw 9.1M-quote gzip is referenced by SHA256 and deliberately not repackaged. Production MT5 and owner-protected August dataset unmodified.

## 9. NEW original-component attribution: the missing high-volume layer is recovered

The restored ORIGINAL 131E helper chain was run once more with the original supplement de-duplication and cap logic, and each funded research ticket was tagged with the source part that actually supplied it. This is a faithful *component diagnostic*, not an independent optimizer and not proof of full L0–L7 V1 MT5 parity. Full `JAN032_ORIGINAL_SOURCE_COMPONENT_ATTRIBUTION.json` and `JAN032_COMPONENT_DAILY.csv` are included.

| Original component | Actual-quote January net | Research tickets | Gross loss | Source PF |
|---|---:|---:|---:|---:|
| **L3 hourly coverage / original 131D** | **+$60,197.33** | **8,470** | **−$1,177.07** | **52.14** |
| L3 hourly cold-start | +$1,472.88 | 380 | −$733.83 | 3.01 |
| L3 original LEAN4 separate session/Asia cells combined | +$1,487.74 | 2,156 | −$2,442.84 | ~1.61 |
| L4 Watchdog 131E | +$30,267.35 | 36,505 | −$27,592.71 | 2.10 |
| **All accepted source contributions** | **+$93,425.31** | **47,511** | **−$31,946.45** | **3.92** |

**This identifies the hidden original-system dependency:** hourly L3 source coverage contributed **64.4% of month net with 17.8% of tickets**, **no positions on January 30**, and profitable net on each of the 14 days it traded. By contrast, Watchdog was active on only three dates and contributed $26,413.86 of its total $30,267.35 net on January 30 (with 32,011 of its 36,505 tickets). The original London/NY hourly coverage rules must be recovered by exact source, not replaced with a generic high-frequency trend stream.

January 8's **−$2.84** entire combined loss is attributable to the original `LONDON10_ROTATE_LONG` source (130 trades). The data does NOT justify disabling London wholesale; diagnose that particular completed-HTF/grid failure state with other months, along with session-owned recovery semantics and genuine account funding.

**Important limitation:** these source labels do not make the January 131E helper a complete later Delta-A-Alpha whitepaper V1: the original full native trend-within-trend engine and conditional physically funded recovery were not certified in 131E. The owner L0–L7 whitepaper still governs the final integration.

## 10. Refinement rejection: quote-aware quantum's apparent gain is entirely January 30

The k=1.5 first-parent spread floor improves the January real-quote net by +$19,318.88 **entirely on January 30**. Its other **20 days are unchanged** from the raw baseline. For k=2, January 30 contributes +$20,083.79 but the other 20 days collectively lose −$3,830.27 versus baseline. This is a market-regime diagnostic, **not evidence of robust multi-day/cross-month alpha**, and is **NOT PROMOTED**. Any genuine adaptive renewal geometry must preserve ordinary-day performance, trade velocity and all whitepaper layer interactions as well as special late-January volatility.

Source original ordered-tick execution can admit up to **640 research children at the identical single tick price** in the `L35_C640` frontier. It is an explicitly simulated same-tick scaling mechanism; it must be declared and tested against broker-side acceptance rates, rate limits, actual margin, slippage, commission and portfolio profit credit. This behavior could materially reduce achievable broker performance.