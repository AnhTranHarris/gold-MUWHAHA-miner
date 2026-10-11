# GRID0177 A–K — timeout recovery, source-corrected fixed-grid supply and experimental economics

**Research date:** 2026-10-11. **Branch:** `delta-A-alpha`. **Source:** original January–July Dukascopy quotes, April–July **only** examined in this stage (31,420,982 original sorted Bid/Ask quotes). **August SEALED.** Governing sources: full original V1 whitepaper (SHA git blob `1b92b3c89159681a7181508de158af685cf5780c`), full owner-ratified governing conversation and the accepted March135 / April136G/136T2 source. This report summarizes empirical research without replacing any of those documents.

## Recovery inspection after message delivery timeout

- Inspected 90 research working files under `/mnt/data/grid0177_work`, original recovered Library source under `/mnt/data/grid0173_accepted_originals`, raw original quotes (read-only), pre-registered J177 A–K research files already posted to GitHub and actual script/log/output timestamps.
- GRID0177K `j177_true_range.py` **had already finished successfully** and generated all four correct month outcomes, exact source event stamps and full eligible-hour CSV ledgers. No need to rerun 31.4m tick decoding merely because frontend delivery timed out. Scientific logs and month JSON were complete.
- Independently reran existing `test_j177.py`: **14/14 PASS**; added `test_j177k.py`: **4/4 PASS** for gap-inclusive previous-close true range, time-prefix invariance under future appended ticks, absence of spread-only rung crossings, and exact all-month 57,578 true quote-event / 1,917 hourly reference data parity.
- A genuine **difference in exact event membership** between earlier completed M5 high–low range and new true range exists. Earlier static levels and new static levels have the **same total eligible-hour coverage 803/819**, but changed approximately a few dozen entry times due to gap treatment. Never claim exact event-by-event parity.

## Formally correct J177K frozen-hour source geometry

At the **first observed actual source quote** of each UTC hour, take source midpoint `anchor` and current actual spread. From last **fully completed** source M5, compute Wilder *single-bar true range* (not Average True Range / smoothed ATR):

`TR_m5 = max(H - L, abs(H - C_previous), abs(L - C_previous))`.

Then freeze for the entire hour

`G_hour = 2 * max(USD 1.5, 1.5 * quoted_spread_at_anchor, 0.15 * TR_last_completed_M5)`.

Issue a candidate source proposal only on an observed source quote crossing an integer static rung relative to `anchor`, with at least 60 seconds since last emitted proposal. One proposal max per quote; this does **not** presume any trade was entered or executed. The factor `2` is the **step multiplier**, while the gap-normalizer max is as defined. No moving levels, artificial bar fills, current unfinished M5 data, or future quote prices.

The original eligible-hour cohort reports **K4-unsigned movement-capacity nonimprovement**, NOT actual losing broker-funded hours. Original April 26 archived alternative source variants have 100 zero-proposal hours in the 179 K4-weak April-hour subset.

| 2026 month | Original raw quote rows | Original K4 unsigned weak hours | New native static-source hours ≥5 proposals | New real quote crossings | Positive signed research hours | Losing signed research hours | Under-served signed research hours | H4/M5 quoted net after extra $0.50 research cost (USD/oz-equivalent sums) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 04 | 7,470,570 | 179 | 173 | 14,965 | 77 | 83 | 19 | -6,444.52 |
| 05 | 8,333,165 | 210 | 204 | 13,834 | 90 | 101 | 19 | -1,516.70 |
| 06 | 8,201,406 | 195 | 193 | 15,253 | 87 | 94 | 14 | -11,635.55 |
| 07 | 7,415,841 | 235 | 233 | 13,526 | 90 | 121 | 24 | -5,630.17 |
| **Total** | **31,420,982** | **819** | **803** | **57,578** | **344** | **399** | **76** | **−25,226.94** |

**Upstream supply:** 803 / 819 original unsigned K4 weak hours (**98.046%**). April old 100 original no-proposal hours: **95 / 100** now receive ≥5 observed fixed-rung price crossing proposals. The **April original 26 variants + new actual true-range source** union meets ≥5 proposals in **174 / 179** hours, not 179/179. These were data-inspected historical months (not blind OOS). All 1,917 original eligible UTC hours are retained including no event, no trade and negative trade cells.

**Actual source quote signed economic control:** a fixed **H4 environment / completed M5 opposing pullback** rule, real first source quote after the event+250ms priced at Buy Ask/Sell Bid, genuine first source opposite-side quote at +1800sec, an original research fee $0.02 and an additional hypothetical cost $0.50, with one global cap16. 26,785 hypothetical selected quotes: summed signed USD/oz quote markouts **−25,226.94**, aggregate gross negative contributions approximately **−109,504.99**. Full positive / negative / under-served source 819 cohort: **344 / 399 / 76**. These are research quote-side outcomes, **not account USD cash**, not actual broker filled positions or validated Coinexx tradeability/margin/equity.

The frozen generator successfully addresses missing **source proposals**, but currently fails the entire economic target. No claim of a 75% **funded losing-hour** reduction, broker profit, R9 SYNTH qualified closed trade parity, or $100–$300 startup survival.

## All prior GRID0177 experiments retained, not overwritten

- **J177A/B (April supply):** 26 original alternative streams 162,025 raw event records / 34,601 distinct timestamps, 100 previously empty April quote-active weak hours; dynamic hourly source gap 4 variants initially generated ≥5 proposals in all 179/179. But dynamic rung changes induced by live spread/TR changes were identified; not treated as fixed-price crossing evidence.
- **J177C (source first passage):** 192 actual original quote-side stop/target scenarios, all negative after costs. No synthetic fill at barrier price.
- **J177D (nested momentum):** 96 causal directional variants, none positive; best source research subset reaches 22 unsigned weak hours positive.
- **J177E (completed H4/H1/M15/M5 transfer):** 84 structural side/horizon configurations, none source quote net-positive; longest H4/M5 pullback positive in up to 81 old April K4-weak research hours but negative total economics.
- **J177F (freeze earlier dynamic generator April→May–July):** original dynamic geometry old K4 weak supply: 179/179, 210/210, 194/195, 235/235; this is a moving-grid *source-state trigger*, not the stronger static crossing result.
- **J177G (later genuine quote spread recovery):** 32 multi-parameter settings scored across 4 months, none positive in all full four-month stressed quote sums; some filter variants improve conditional average by dropping many opportunities.
- **J177H (archived accepted April source USD/oz quote parity):** genuinely positive April source-side markouts for preselected original native/session families even after entry delay and hypothetical cost, with source-model correlation >.99 in selected comparisons. **Historical winning cells/thresholds in original April code were selected using realized same-April P&L**; don't transfer those hindsight winner lists as if earned prior to entry.
- **J177I (matured shadow economic context at 4h/day/week):** 36 configurations negative in all April–July monthly aftercost aggregate sums; shadow reference outcomes cannot credit funded Watchdog genealogy.
- **J177J (fully STATIC H-L prior bar range source):** 803/819 old weak-hours with ≥5 sources, 95/100 April originally empty, but note high–low range is not the preregistered Wilder true range.
- **J177K (genuine TR correction):** all 31,420,982 quote rows, **803/819** exact correct formula source-hour coverage with direct source-side economic control negative in all four months, verified extra regression tests.

## Reproducibility, falsifiable follow-up and governance

1. The complete source, raw-original-derived immutable expected original 470+466+489+492=1,917 hour reference and new event lists, recovered original April accepted research scripts/stream copies, tests and individual stage logs are in the attached scientific ZIP. Original monthly Dukascopy raw ticks are **NOT** repacked or modified; exact external raw compressed source paths and SHAs are referenced in the manifest.
2. Scientific next step: **GRID0178** must preserve original March native/hourly/high-volume/Asia and April original paid-funded previous-child genealogy while designing causally *earned* prior-regime/cell admissions. Recover original code and cell fields from protected original sources before new application. Test live-equivalent candidates using frozen state and separately measured actual source quote outcomes across months; no use of April future outcome-selected cells as predictor. Session-specific distinct geometry must be incorporated in a **single event-time V1 engine**, not eight stand-alone P&L lists.
3. Acceptance is FULL signed account net/PF, source actual Bid/Ask, broker contract/margin feasible no after-loss lot increase, real floating equity/drawdown, whole 1,917 eligible-hour results with no silently hidden zero trade cells, and independent truly sealed validation when owner permits. 
4. MetaQuotes source references: [real ticks and historical spread for strategy testing](https://www.mql5.com/en/docs/runtime/testing), [MQL5 iATR reference](https://www.mql5.com/en/docs/indicators/IATR) (note iATR is a **smoothed indicator**, whereas here only a **single bar TR** is used); [completed session range breakout coding example](https://www.mql5.com/en/articles/16135); and [purged/embargoed labels background](https://ppuertos.github.io/financial-ml-core/reference/model_selection/split/). These references inform reconstructible methods, NOT XAUUSD profitability.

**Final status at report creation:** GRID0177A–K completed original source research, J177K formula gap reconciled and local QA rerun; no EA or owner whitepaper mutation; August source SEALED; result **research-only**. Next GRID0178 is future research, not a proven new trading edge.
