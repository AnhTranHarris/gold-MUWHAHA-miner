# GRID0320–GRID0329 — January 2026 original-tick research: as-of microstructure routing and $100 seven-day survivability

**Disposition: RESEARCH ONLY / UNPROMOTED / OWNER QC PENDING.** Not an accepted algorithm; not integrated into active `FourSessionV1`. The official `delta-A-alpha` scientific cursor remains J0183, August remains SEALED, trading remains OFF.

## Original authority (must read entire originals, not this report)

- Full owner V1 whitepaper (permanent L0–L7 spine): `research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt`, Git blob `1b92b3c89159681a7181508de158af685cf5780c`.
- Full owner-ratified governing conversation: https://docs.google.com/document/d/1J9d_P4ooCnNmcxPwG1F178aE4ktpkLrFclcyQPaQJ8k/edit
- Anti-summary, anti-drift, independent owner QC: https://docs.google.com/document/d/1eG5F76uvm9M-1JXs4LvAaTzPEurU5l4Pgj2sUUelc1o/edit
- January original source and complete ledger law: https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit
- Full Jan→Jul unabridged roadmap: https://docs.google.com/document/d/1PcaksxuiayFXVW3QtKfzitARvQj6NyL4IIbGhG8K9z4/edit
- Governing R9 reference roles: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/governance/OWNER_20261013_VERBATIM_DUKASCOPY_TICK_CANDLES_R9_REFERENCE_LOCK.md
- Immediately preceding original physically booked stopout source and results archive: https://drive.google.com/file/d/1AExwv8MeePcgaZYQ1TFI0xy_njUtUJ-l/view ; original GitHub source under `GRID0312_0319_SOURCE_CODE`.
- Current active Python baseline remains `research/delta_a_alpha/implementation/v1_four_session_architecture.py`, Git blob `64b75c39c41ff8ccd0d0e8b02e45bdf5b9ca54e2`; it was NOT changed.

## Frozen raw data and exact test scope

Original January Dukascopy XAUUSD Bid/Ask UTC CSV.GZ: `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`, **9,135,062 chronological original quotes**, file SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`. Use this raw source only; no synthetic/MT5 execution feed or month identity runtime routing. Each of 10 seeded dates runs a fresh $100 account with exactly 7 UTC calendar days of original quote path. Seed `20261014`, dates: `2026-01-05, 08, 09, 12, 15, 19, 20, 21, 22, 23`. These rolling episodes overlap in market chronology; do not imply 10 statistically independent market trials.

All tests use fixed **0.01 lots**, hypothetical **1 oz** contract exposure, USD cash mark-to-market, **500:1 hypothetical leverage**, **$0.20 modeled round-trip cost**, first original quote at inherited `250ms` latency, zero Martingale/loss-dependent sizing, source-native paid-closed parent→child gating, real open-count capacity, per-source risk controls. Only original raw Bid/Ask quotes price fills and forced closes. Additional modeled adverse closing cost is tested independently. The historical source candidate population and planned exit schedule are NOT from an endogenous month-blind signal engine; all profit claims remain exploratory despite quote-level exact arithmetic.

## Why these tests are materially new

- **GRID0320:** Pre-request quote quality feature uses the last original quote **at least 1 full second before the inherited candidate executable entry**, then causal five-second price displacement and contemporaneous Bid/Ask spread from that earlier quote. No future price or month/day name is a feature. The exact origin request timestamp is not preserved, so this is an earlier-than-entry proxy, NOT authenticated pre-order broker permission.
- **GRID0321:** Eight independent controls (tight spread thresholds, maximum/minimum observed five-second displacement, combinations) across all ten windows. Tight spread cap at $0.40 retained only 48/859 baseline booked closes, and cap $0.25 retained two. These variants are negative for throughput. Screening for **at least $0.50 previous 5s displacement** retained 666 closes and reduced worst hourly floating DD from $164.72 to $123.54, with 10/10 modeled positive end cash.
- **GRID0322:** Eleven combinations of the displacement proxy and fixed fundable admission budgets 20%, 25%, 30%; **none** reached $10,000 in seven days. Loosening margin budget can increase net, but may restore worst hourly DD.
- **GRID0323:** Independent quote-side read-only cross-check of 30 portfolio episodes, 190 exact assertions, reconciling Bid/Ask entry/exit, cash, trade count, original quote equity and hourly DD.
- **GRID0324/0325:** Orthogonal microstructure source router applies earlier-observed displacement veto **only to the ordinary L3/session source family**, preserving Watchdog parent/child proposals and their original paid admission path. This improves throughput and worst-hour exposure relative to blanket screens without using January date as routing feature.
- **GRID0326:** Eight source-conditioned shock/margin Pareto controls. A 0.50 shock floor at a 20% margin admission budget gives the most balanced proven frontier of this batch. Higher shock floors reduce throughput and do not materially improve the worst-hour beyond the threshold seen.
- **GRID0327:** Independently replayed 20 selected source-conditioned portfolio episodes, **140 exact accounting and hourly DD assertions**.
- **GRID0328:** Four adverse-closing-cost scenarios ($0, $0.10, $0.30, $0.50 additional each closed trade) on all ten sampled windows.
- **GRID0329:** Independently repriced all **2,664 booked trades** across **40 account portfolios**, preserving an original-quote original-index / entry / exit / direction / source / cost / cash chronological full deal ledger in `grid0329_full_40_portfolios_original_quote_booked_deal_ledger.ndjson.gz`; **240/240 independent reconciliations PASS**.

## Comparisons: $100, ten seeded seven-day historical windows

| Scenario | Modeled profitable endpoints | Modeled zero broker stopout | 7d closes (all ten) | Lowest final cash | Highest final cash | Worst hourly floating DD (max across ten) | Endpoints >= $10,000 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Prior GRID0316 control, 20% margin admission | 10/10 | 10/10 | **859** | **$185.41** | $444.94 | **$164.72** | 0/10 |
| Blanket min five-second displacement $0.50 | 10/10 | 10/10 | 666 | $243.14 | $395.13 | $123.54 | 0/10 |
| **Ordinary source only, min 5-sec displacement $0.50, 20% admission** | **10/10** | **10/10** | **711** | **$243.14** | **$396.04** | **$82.36** | **0/10** |
| Ordinary source only, min 5-sec displacement $0.35, 20% admission | 10/10 | 10/10 | 774 | $226.35 | $393.36 | $144.13 | 0/10 |
| Ordinary source only, min 5-sec displacement $0.75, 20% admission | 10/10 | 10/10 | 588 | $198.94 | $416.41 | $82.36 | 0/10 |
| Ordinary source only, min 5-sec displacement $0.50, 25% admission | 10/10 | 10/10 | 786 | $233.67 | $437.74 | $164.72 | 0/10 |
| Ordinary source only, min 5-sec displacement $0.50, 20% admission + **$0.10 adverse close** | 10/10 | 10/10 | 672 | $206.21 | $385.95 | $82.36 | 0/10 |
| Same + **$0.30 adverse close** | 10/10 | 10/10 | 651 | $193.32 | $338.42 | $82.36 | 0/10 |
| Same + **$0.50 adverse close** | 10/10 | 10/10 | 630 | $190.48 | $317.23 | $82.36 | 0/10 |

**Measured trade-off:** selected source-conditioned 0.50-USD displacement screen lowers maximum worst-hour mark DD by approximately **50.0%** relative to the previous control, while retaining approximately **82.8%** of its completed closes. The lowest ending cash across starts increases from $185.41 to $243.14 in this historical sample. Maximum ending cash and aggregate trade velocity both decline. A stronger 7-day money multiplier is *not* demonstrated.

**Interpretation:** The selection has the better observed **historical $100 survival + hourly DD vs throughput balance** among this small set. It is NOT an accepted or production-ready replacement and does NOT meet the owner's $100→$10,000 within seven days for all ten dates. All remaining 10/10 modeled success claims refer only to the exact observed ten quote paths under hypothetical execution assumptions; random adverse gaps can still bankrupt an account.

## Exactly what remains missing from the Python engine

1. **Endogenous event generation, not archived January-picked candidates.** Reproduce the original 131A/131D/Watchdog/coverage source events from contemporaneous complete original ticks *inside the active* `FourSessionV1`, with documented source event identity, original source logic, and correctly timestamped first-request→first-executable-fill semantics. Present January source candidates are historically selected; fresh month-blind generation remains unverified.
2. **Broker exact 0.01-lot funding/stopout.** Obtain actual Coinexx XAUUSD `SYMBOL_TRADE_CONTRACT_SIZE`, margin calculation mode, `SYMBOL_MARGIN_HEDGED`, actual account leverage, hedge margin treatment, `ACCOUNT_MARGIN_SO_MODE`, actual stopout level, spread, commissions, latency and worst-gap slippage. Current hard-coded 1oz, 500x and `price/leverage` cannot establish true $100 entry fundability.
3. **R9 OVERFIT six offline per-trade references.** Original complete teacher trade ledger with each reference entry, hold, exit, realized profit, MFE/MAE/drawdown and gross loss is required for six independently predefined 75% parity scores. We have NOT independently verified the assertion that R9 OVERFIT itself demonstrates fundable $100 survival on the actual 2026 Dukascopy Bid/Ask model. Do not treat an undocumented teacher claim as realized Python parity.
4. **Full January per-period performance parity.** R9 SYNTH January target is +$41,520.82/month and 27,980 completed trades with individual daily/weekly equality or better, risk containment and net; the selected **ten independent $100 seven-day scenarios are a separate stress test**, not proof of 21/21 daily benchmark or 5/5 weekly benchmark.
5. **Ultra-high throughput short-cycle profitable opportunities**, organically generated with fees, latency, and stop-out; all existing tested maturity/TP/SL shortcuts have been negative or insufficient. Profit-funding and microstructure screens reduce unearned or weak risk, but cannot by themselves create thousands of additional independent after-cost winners.
6. **Month-blind Feb–Jul regression** and later exact Python↔MT5 parity only with owner authorization; August SEALED. Retain current V1 fallback and state journal.

## Full independent QC nuance: pre-entry and post-entry on one tick

The initial `grid0315` independent equity reconstructor marks the portfolio **once per original tick after all booked events**; GRID0312 governor additionally observes equity **before an entry** and **after** that quote's admission/spread/fee debit. In the January 23 `+$0.30 adverse close` scenario, the once-per-quote method underestimated the worst-hour drawdown by **$0.06** ($44.51 rather than the governor's $44.57). This is NOT a P&L discrepancy. `GRID0329` independently reconstructed both pre-entry and post-entry original-quote marks and reconciled **all 240 checks exactly**; the standalone `grid0329_intratick_hourly_attribution.py` documents the measured distinction. All actual entry and exit prices are original side-appropriate executable quotes; no ghost future settlement.

## Community/public research inspirations (reconstructible only; not external validation)

- MetaQuotes official hedging margin treatment: https://www.mql5.com/en/articles/2299
- MetaQuotes official OrderCalcMargin (new-order margin only, not the complete existing portfolio): https://www.mql5.com/en/docs/trading/ordercalcmargin
- Japanese-language MetaQuotes article on adaptive spread sensitivity: https://www.mql5.com/ja/articles/20371
- Japanese-language MetaQuotes article on scalping and swing-state selection: https://www.mql5.com/ja/articles/19989
- Independent trader community on per-fill variable transaction cost: https://www.reddit.com/r/algotrading/comments/1vyeq3l/cost_model_in_backtesting_results/
- Myfxbook practitioner discussion warning that capital additions and undisclosed trades can mask drawdown: https://www.myfxbook.com/community/trading-systems/midaz-deo/1748029%2C2

Nothing in these sources independently proves an implementable $100 account can grow 100x risk-free; only their disclosed timing/cost/risk mechanisms were considered as reconstructible research hypotheses.

## Source custody

The companion ZIP contains **all 10 new Python experiment programs**, independent QC, every saved result JSON, every original-quote booked deal with actual entry and exit identities, original command logs, one exact prior GRID0312–0319 archived source/dependency chain, this full report, and a self-verifying per-file SHA-256 manifest. Original January raw quote gzip remains immutable in the user's source folder and is identified by exact ID/SHA rather than duplicating its 68.69MB bytes inside this trial archive. All negative variants are retained. Do not advance the official scientific cursor or promote before original owner independent QC.


---
## Full original evidence custody verified
- Complete runnable Python/JSON/NDJSON original quote-ledger ZIP (30 hashed internal files): https://drive.google.com/file/d/1gptbz4HcVutV7IBYzSEvAPK2pW4-5pBB/view
- Exact archive SHA-256: `d3db6672c1ba102ee57cf301a89a2cc3f1098a7843777048d514a5a90f31d142`
- Same human research report in January Google Drive: https://drive.google.com/file/d/11NkVK1ZOslGCiQgjg11qUcUOth5rbHia/view
- Original 11 Python files committed separately in [GRID0320_0329_SOURCE_CODE](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/delta-A-alpha/research/delta_a_alpha/monthly_progressive_roadmap_20261013/2026-01_JANUARY/experiments/GRID0320_0329_SOURCE_CODE)
- Original content transfer preserved in Drive: https://drive.google.com/file/d/1-ozY0FKB1Y_DNqBAcL_RMIS2karZYoox/view
- Scientific cursor J0183 NOT ADVANCED; live code unaffected; no MQL5 or owner QC promotion.
