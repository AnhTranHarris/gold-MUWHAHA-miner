# GRID0330–GRID0333 | January 2026 capital-capacity and causal risk frontier — UNPROMOTED

**Scientific status:** Original-source January in-sample experimentation only. Owner QC pending; `CURRENT_STATE.json` J0183; live `FourSessionV1` unchanged, August sealed, trading OFF. No claims of R9 OVERFIT 75%, R9 SYNTH full daily/weekly/velocity parity or $100-to-$10,000 in a week.

## Governing original sources (read complete, not summarized)
- [Owner January–July unabridged roadmap](https://docs.google.com/document/d/1PcaksxuiayFXVW3QtKfzitARvQj6NyL4IIbGhG8K9z4/edit)
- [Owner anti-drift/anti-summary law](https://docs.google.com/document/d/1eG5F76uvm9M-1JXs4LvAaTzPEurU5l4Pgj2sUUelc1o/edit)
- [January original-source evidence law](https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit)
- [Original owner-ratified governing conversation](https://docs.google.com/document/d/1J9d_P4ooCnNmcxPwG1F178aE4ktpkLrFclcyQPaQJ8k/edit)
- [Frozen V1 owner whitepaper](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt)
- [Original source selection and L0–L7 implementation](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/delta-A-alpha/research/delta_a_alpha/implementation)

## Immutable source and experimental contract
- January raw original Bid/Ask tick gzip `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`, **9,135,062 chronologically ordered quotes**, SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`, locally verified afresh during this experiment.
- Research accounts: **10 deterministic sampled January days** `2026-01-05, 08, 09, 12, 15, 19, 20, 21, 22, 23`; each independently starts at **$100** at 00:00 UTC and has exactly seven calendar days of January ticks. Seed 20261014 inherited without reselecting days after seeing outcomes.
- One ticket = fixed **0.01 lot** = research-assumed **1 XAU oz**, original quote-side bid/ask, $0.20 round trip, 500:1 *hypothetical*, 20% of marked equity admission margin, 50% hypothetical stop-out. Real Coinexx rules remain unverified.
- Prior five-second displacement screen measured at an observed quote at least **one full second before modeled fill**; source-specific previous GRID0325 screen preserved. The true historical request timestamp is not present in inherited candidates, so this is a hypothesis screen, not a certified market order protocol.
- Source parents/children, previous closed-profit renewal, online pause, earned capacity, forced liquidation and quote chronology from the **unmodified GRID0320–0329 predecessor archive**. No month/date identity, future outcomes, balance-target scoring or R9 teacher enters entry permission.

## Four trial configurations plus inherited control
- **GRID0325 control:** baseline source-specific screen, initial 2 slots and prior earned tiers; frozen predecessor outcome, no new tuning.
- **GRID0330 INIT4:** as control, 4 physically funded initial 0.01-lot slots; 20% new-position margin admission; rerun on all 10 dates.
- **GRID0330 INIT8:** as control, 8 physically funded initial 0.01-lot slots; rerun on all 10 dates. No position lot scaling or martingale.
- **GRID0331:** begin with 2 slots; only after previously **closed booked balance >= $150** and pre-request five-second absolute movement >= $1.00 can eight capacity slots become available, in addition to original earned tiers. No future outcome in permission.
- **GRID0332:** same as GRID0331 except the early eight-slot permission is permitted only to `coverage_gc0` or `coverage_gc2`, not parent/child or other desks.

## Result: all 10 original-tick seven-day episodes, same cohort

| Variant | Profitable | No simulated stopout | Ten-episode mean final $ | Final min–max $ | Total closes | Worst single UTC-hour equity DD $ | $10,000 within 7d |
|---|---:|---:|---:|---:|---:|---:|---:|
| GRID0325_CONTROL | 10/10 | 10/10 | 313.28 | 243.14–396.04 | 711 | 82.36 | 0/10 |
| GRID0330_INIT4 | 10/10 | 10/10 | 330.66 | 238.19–414.09 | 769 | 144.13 | 0/10 |
| GRID0330_INIT8 | 10/10 | 10/10 | 352.02 | 238.19–494.60 | 828 | 144.13 | 0/10 |
| GRID0331_EARNED_ALL | 10/10 | 10/10 | 327.96 | 243.14–444.77 | 752 | 123.54 | 0/10 |
| GRID0332_EARNED_COVERAGE | 10/10 | 10/10 | 327.43 | 243.14–442.48 | 744 | 123.54 | 0/10 |

**Interpretation:** Eight slots increase trade throughput and average in-sample cash but lift worst-hour drawdown sharply. The prior 2-slot control remains the lower-hourly-risk point. Closed-cash-conditioned slot increases recover a smaller portion of throughput with intermediate drawdown. None meets the hard $10,000/week target. No preferred mechanism or owner QC certification is claimed.

**Risk trade-off:** $144.13 worst hourly DD across the ten accounts is severe relative to a $100 starting balance even though it can occur after profits have accrued. Minimum equity was $78.45 across the broader cap tests. This is not proof of a 100%-safe system.

## Original-source audit: unresolved scientific leakage and execution boundaries
1. `ORIGINAL/jan_session_portfolio_131d.py` defines *`RESCUE_RULES` as 'recurrent, all-positive across observed days in discovery'*. The formulas can be evaluated as-of market data, but **choosing the rules from January outcomes is retrospective selection**. All present results are January in-sample and not month-blind until candidate source generation is reconstructed and retested on unopened months.
2. Original event candidates and **scheduled exit indices** were generated in prior January research. The executor does not inspect future close cash to approve trades, and its cash closes use observed quote sides, but independently regenerated source opportunities and runtime adaptive exit decisions are not yet proven for a unified L0–L7 engine.
3. R9 OVERFIT trade teacher and its alleged $100 survivability have **not** been separately reconstructed to a 75% six-dimensional accepted score. The R9 SYNTH reference is an offline scorer, not a trading signal. Do not substitute these original January historical candidates for the OVERFIT teacher.
4. Broker-specific margin, stop-out and XAUUSD contract value are research assumptions; all ten *historical modeled* survival passes cannot guarantee future or Coinexx survivability. A raw bid/ask gap can overshoot the liquidation trigger.
5. The **full R9 SYNTH** January target remains +$41,520.82 and 27,980 closed trades across 21 days and five ISO weeks; prior large-capital candidate portfolios met only partial daily/week reference counts. This experiment tests **$100 seven-day survival only**, not monthly parity.

## Independent, read-only booked-deal source QC
`GRID0333` reran the full **GRID0331** test, independently repriced all booked 752 closes at original opposing Bid/Ask quote, checked entry fill side, chronological entry <= close, 0.01 lot / $0.20 after-cost cash, unique funding, sum(booked cash)+$100 = final account, prior run values, no forced event, exact original tick SHA and locked day list. **1,604 checks passed**. The full 752-deal entry/exit/source/quote/price/cash ledger is preserved in `QC/grid0333_independent_full_booked_trade_ledger.json.gz`, with no hidden favorable fills. All actual closes in this configuration were previously scheduled exits; no broker stop-out branch fired in these ten selected histories. Existing independent GRID0319 synthetic gap tests remain the adverse-stopout evidence.

## Not promoted / next technical objective
- Audit and reconstruct R9 OVERFIT's actual entry/hold/exit teacher and $100 trajectory independently; compute separate 75% comparisons without signal leakage.
- Replace historically selected 131D/GRID0272 opportunity lists with continuously as-of L0–L7 native signal generator and source-specific lifecycle state; test the exact 10 starting windows, full January daily/week/month and untouched February onwards.
- Generate more after-cost positive quick-cycle opportunities without borrowing future trade success, scaling lots after a loss, changing the calendar target at runtime or circumventing margin.
- Calibrate actual Coinexx account currency, contract-size/tick-value, leverage tiers, stop-out/margin mode, commission, swap, execution conditions and forced close priority before claiming broker survival.

**State unchanged:** `delta-A-alpha`, official J0183, owner QC PENDING, August SEALED, live trading OFF, no MQL5 authoring or promotion.


---
**Unmodified complete source, original parent archive, all trial JSON, 752 booked original-side trade rows and SHA manifest:** https://drive.google.com/file/d/1rJPThaw74a7IbIhjxh6xfcGKcIoLrfDP/view
**Exact archive SHA-256** `ad65e70a93595e24863012b83fc056be4d69ebf2bf918fbe7cdfbd63f3284113`
**Same original trial report:** https://drive.google.com/file/d/1cYqD5Fc7QiSEoxpcYkk9XvqHJCFotgrG/view
**Four exact source files:** https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/delta-A-alpha/research/delta_a_alpha/monthly_progressive_roadmap_20261013/2026-01_JANUARY/experiments/GRID0330_0333_SOURCE_CODE
**Transfer copy** https://drive.google.com/file/d/1DTMStbWHSzJXNyk8wZfS6SYdIzsj6k2v/view
No accepted production code change, no scientific cursor advancement.
