# GRID0255 — causal H4 confirmed-sniper bounded two-slot upgrade, 57.5m-tick portfolio result

**Governing rule (verbatim):** “r9 syth as perfomance goals, r9 overfit shows optimal trades, each month's market conditions are mostly unique, the grid trading strategy trading edge is a high trading volume trading bot, the grid trading strategy is a near HTF, the grid trading strategy is a near scalping trading bot, the grid trading strategy is a near sniper trading bot”.

## Accepted result: net AND physical completed research-trade volume increase

This work starts from the original, already-preserved GRID0254 `delta-A-alpha` portfolio. It retains original GRID0185 J179F conditional harvester, H4 completed structural breakout, H1 source, completed-H4 pullback re-cross and original GRID0254 H4 two-completed-M1 sniper signal. No new branches, no loss multiplier, no hindsight known at runtime, no Vertical L1-L7 calls, no EA enabled, and sealed August never read.

**Structural upgrade:** rather than let GRID0254's H4 sniper use one research position, up to **two concurrently existing, independently fixed 1oz (0.01 lot at 100oz/lot assumption)** are allowed only when genuinely distinct confirmed finished-H4 owner opportunities arrive. Original quote spread <=$1.00/oz; original offer must be observed no later than +1 second, no retro-entry. Stop is `max($1.50, 1.5*completed-H4 ATR14, 3*entry-spread)`, high-water trail `max($1.00,1.75*completed-H4 ATR14)`, 24-hour max hold, roundtrip research cost **$0.52 per settled one-ounce position**. This is the same transparent original P5 lifecycle with slightly wider trailing room: not a position-size or cost trick. Every source admission and stop update uses real observed Bid/Ask quotes; no unobserved bar path fills.

| Same Jan–Jul 2026 source-quote accounting | GRID0254 original | GRID0255 two-source-slot |
| --- | ---: | ---: |
| Seven-month source-quote net USD/oz | +$5,052.041 | **+$6,152.697** |
| Unique closed one-ounce research positions | 1,032 | **1,053** |
| Quote-profitable months | 7/7 | **7/7** |
| Quote-profitable represented ISO weeks | 23/31 | **23/31** |
| Source-quote gross loss USD/oz | -$7,766.928 | -$8,727.613 |
| Every-tick floating maximum drawdown USD/oz | $863.195 | $940.945 |
| Maximum simultaneous positions in one 16-cap research book | 11 | 12 |

**Verified increment:** **+$1,100.656 (21.79%) and +21 (2.03%) completed research trades, seven positive months preserved**. The improvement is not explained by summing uncoordinated sleeve profits. The actual single chronological book was replayed across **57,527,562** original January–July Dukascopy quotes. Every one of the **1,053** settled entry/exit pairs and resulting cash was reconciled against original observed Bid/Ask, with **0 source fill mismatches, 0 unfilled leftovers, and 0 16-slot capacity denials**. Gross loss and marked drawdown increased; they are not locked.

The original 162 H4 sniper confirmed source invitations, all produced from original completed H4/M1 reference, produced 125 new genuinely executable research closes with the bounded 2-slot 1.75x-ATR rule; earlier one-slot original 1.0x-ATR produced 104 closes. These 125 closes alone are not claimed 7/7 monthly profitable: the **cooperative full portfolio** retains 7/7 positive months.

**Alternative cost/fragility study (research-only, not promoted):** require completed invitation M1 tick count >=300 instead of importing an OVERFIT oracle. Exact 57.5m-quote shared 16-capacity research replay: **1,028 trades, +$6,094.549 net, 7/7 monthly, 23/31 weekly, $843.395 maximum marked DD, 0 quote/funding-cap mismatches**. It preserves a larger July profit cushion ($124.034 versus $23.754 for max-throughput), and lowers DD relative to GRID0254, at the cost of four completed trades relative to original. The `300` cutoff is a *fixed candidate setting discovered on previously studied data*, not a per-month retrospectively switched rule or certified transferable default. No positive-week claim beyond 23/31.

## Scientific restrictions and next true bottleneck

1. **NO weekly net-profit lock:** 8 of the 31 originally benchmarked UTC ISO weeks still fail. R9 SYNTH's original full historical account benchmark remains **219,342 closes / +$309,122.85** January–July; the current grid's 1,053 quote positions are a tiny fraction of its scale. Profit and volume gains here are genuine **within the source-quote research model**, but the ultimate high-velocity near-scalping engine is still missing.
2. **NO broker funded-net certification:** The model used true Dukascopy Bid/Ask and research cost of $0.52 per close for an assumed 1oz exposure, not the independently verified Coinexx spread, tick value, stop-level / freeze minimum, margin, commission and latency on a $100–300 account. Recorded full-tick DD up to $940.945 does not establish starting-capital feasibility. The higher-velocity case's +$23.754 July cushion is especially vulnerable to extra execution costs. Do not imply real-cash gains or a verified performance lock.
3. January–July have been repeatedly inspected in previous GRID experiments and in this nine-trailing-setting/several-concurrency-design cycle. The 1.75x ATR multiplier and two slots are **in-sample historically researched configurations**, not unseen out-of-sample performance. No hidden H4 labels, future scores, calendar-month switches, or GRID0185 future-child payouts were added to decision features. Future truly sealed August is NOT opened without owner authorization.
4. The new `v1_grid_h4_bounded_sniper_campaign_0255.py` is an **optional G0-near-sniper downstream shadow executor** connected by a type-safe adapter to the original `v1_grid_h4_second_acceptance_0254.py` source, **not** a replacement for main `FourSessionV1`, production broker-order code or a bypass of the Vertical Grid System. No new branch, no scheduled task.

## Traceable reproducibility

- Source: `research/delta_a_alpha/implementation/v1_grid_h4_second_acceptance_0254.py` (existing), `v1_grid_strategy_source_router.py` (existing optional G0 admission), `v1_grid_h4_bounded_sniper_campaign_0255.py` (new optional research executor).
- Causal protocol tests: `test_v1_grid_h4_bounded_sniper_campaign_0255.py`, **11/11 passed** locally; not full repository CI or MT5 tester.
- Original-tick numerical experiment: `grid0255_rung_sniper_parallel_campaign.py`; one-book settlement verification: `grid0255_verified_shared_book.py`; two as-of selection research alternatives: `grid0255_filtered_sniper_4_hypotheses.py` and `grid0255_verified_filtered_books.py`.
- Full results: `GRID0255_SHARED_2SLOT_TRAIL1750_FULL_TICK_SCORE.json`; reconciled 1053 closed positions CSV; `GRID0255_SHARED_BOOK_CNT300_RESULT.json` and original candidate tapes. Archived baseline: `GRID0254_STRICT_SHARED_BOOK_GAP1000.json` plus earlier valid J179F/H4/H1/H4r exact-source ledgers, original Dukascopy Jan–Jul compressed tick files which remain in the owner's research corpus, NOT repacked into ZIP.
- Local inexact or rejected trials retained **only** in `GRID0255_INTERNAL_NONPROMOTED_HYPOTHESIS_JOURNAL.md` and supplementary manifests/scripts.

**Research verdict:** A **real, independently recomputed historical quote-portfolio profit-and-velocity improvement** over accepted GRID0254; retain as a non-promoted successor candidate. Weekly positivity, source strategy net parity to R9 SYNTH, broker solvency, and true independent OOS all remain open.
