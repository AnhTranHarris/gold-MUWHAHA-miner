# GRID0271 — January repeat-hypothesis research checkpoint (NOT PROMOTED)

**Status:** RESEARCH_IN_PROGRESS / NO_POSITIVE_CANDIDATE / OWNER_QC_PENDING. This index is a locator, not the owner law or executable source.

Read first: [full owner frozen V1 whitepaper](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt), [January governing anti-summary document](https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit), full ratified owner conversation, and the exact original [January rollback research branch](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/carson/r9-gamma-02-jan-grid-milestone/research/R9_GAMMA). Do not reconstruct original signal logic from this index.

- [Detailed original-source research findings](GRID0271_JANUARY_SOURCE_EXACT_RESEARCH_REPORT.md) — technical outcomes, falsified hypotheses and limits.
- [Exact static counterfactual source](j0271_jan_counterfactual_cycles.py), [exact causal-asof/oracle diagnostic source](j0271_asof_entry_cycles.py), [exact raw native grid variant source](j0271_native_tick_grid_experiments.py), [report/QA builder source](build_j0271_report.py).
- [Complete January research experimental ZIP on Google Drive](https://drive.google.com/file/d/1qxtyjpeQ8c0CEn8uAxm0gSoF6HmvIqoY/view) — SHA-256 `f8a37efdfac850afceaae927c6d05c6a03ad4dc37dcaf2e037058f352e57908c`. Actual CSV/JSON logs for 11 same-entry exits, 43 as-of screens/oracle sensitivity, 9 unique full 9,135,062-tick source-only grid variants (10 recordings, one exact duplicate). RAW original data referenced by SHA, never duplicated into this compact archive.
- [Readable original-source trial report on Google Drive](https://docs.google.com/document/d/1iTrims7t7fCnaVEST4gRO6RbPlTxkOzQ0HBf5262BDE/edit).
- [Baseline unchanged full V1 original January replay](https://drive.google.com/file/d/1djy0tXU9x3xGP7uQ66ISQAVxol2F3Jve/view) — 3,258 closes, net -$3,015.318, PF .413; original raw Dukascopy ticks SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`.
- Original January R9 SYNTH 100% month net **+$41,520.82** / 27,980 trades; original complete [R9 day/week/month reference JSON](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/r9-gamma-02-jan-grid-milestone/research/R9_GAMMA/artifacts/r9_synth_jan_daily_weekly.json). Offline R9 OVERFIT 75% teacher **NOT MATCHED / NOT SCORED**.

## Original January mechanics: use exact source, not historical headline P&L

- [119 original executable helper](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/r9-gamma-02-jan-grid-milestone/research/R9_GAMMA/helpers/gamma02_dynamic_watchdog_router_119.py) blob `b201ed9e805784f041da004d61c25fb1181e5f8b`.
- [131A original helper](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/r9-gamma-02-jan-grid-milestone/research/R9_GAMMA/helpers/gamma02_jan_watchdog119_grid_layer_refinement_131a.py) blob `edcc9b8c2352aca1a333631210fcc8f4b03d4dab`.
- [131D original session portfolio helper](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/r9-gamma-02-jan-grid-milestone/research/R9_GAMMA/helpers/jan_session_portfolio_131d.py) blob `45d0446be7a9f7ee08c0a9f8ca2a8d38a354ffc0`.
- [131E original profit/heat helper](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/r9-gamma-02-jan-grid-milestone/research/R9_GAMMA/helpers/jan_profit_per_heat_atomic_131e.py) blob `f8c78b11213e6beccd0c4ebd3f07206b2f731065`.

**Critical historical surface mismatch:** Original GAMMA-02 accepted January frontier uses frozen session-P75 normalized quote spread around Dukascopy midpoint, physically up to 640 same-timestamp child positions with ~$57,139 floating quote DD. It is NOT certified original *raw* Bid/Ask / broker-queue matching. Preserve accepted mechanisms, reprice source-exact, do not paste favorable January hindsight-selected cells as deployable signals.

## Current January screening findings

- All 11 fixed V1-entry TP/SL/hold/side counterfactuals negative after modeled costs; best -$2,512.66.
- 43 as-of screens and/oracle diagnostics: tiny 32-trade sample can appear profitable but not robust; impossible hindsight best direction+exit within 240s on old entry cohort still only +$13,594 vs R9 +$41,521. Illegal oracle never feeds runtime.
- Nine unique full-month raw Bid/Ask native-grid controls (10 run-records) **all negative**; least-negative -$8,946.90 for 11,565 closes. More capacity on negative expectancy increased drawdown/loss. These toy sources are NOT genuine original Watchdog-119.
- **Primary P0:** source-exact 119/131A/131D/131E lineage restore with original helper code, source-event IDs, paid previous-child proof and source-exact raw Bid/Ask 250ms fill sensitivity. Only then run full month-blind FourSessionV1 integration and performance regressions.

**Acceptance:** January not QC passed, zero candidates integrated; monthly 100% R9 SYNTH net/day/week and per-trade 75% R9 OVERFIT **not met**. No code modified inside production `implementation/`, no J0183 promotion, trading disabled, August sealed.
