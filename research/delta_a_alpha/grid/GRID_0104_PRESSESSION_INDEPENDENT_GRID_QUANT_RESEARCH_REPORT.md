# GRID-0104 — PRE-SESSION GRID GENESIS: REPEATED JANUARY–FEBRUARY MECHANISM REFUTATION

**2026-10-10 | OWNER RESEARCH STAGE**. **DO NOT ACTIVATE L1–L7. NO STRATEGY PROMOTED.** This is a successor to the clean GRID-0103 shadow-event project, not to any deleted legacy Jan/Feb strategy. Source basis: `research/delta_a_alpha/governance/OWNER_GRID_GENESIS_NO_MARTINGALE_100K_DISCOVERY_20261010.md`.

## Purpose

User requires independent optimization of the original OmegaFX/MegaJoctan Python grid *as a master virtual opportunity generator*, before the session-aware/MTF/quality layers are allowed to act. The "creative hallucination" step is hypothesis synthesis, not fabricated success or nonexistent source logic. Preserve zero automatic inventory, fixed-lot/no-Martingale policy, no standalone filled orders, and the later $100k discovery-account default. R9 SYNTH is a performance/velocity ceiling, not BUY/SELL ground truth.

## Independent untouched source data

- Jan 2026 original Dukascopy: **9,135,062** ordered XAUUSD Bid/Ask ticks; verified original gz SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`.
- Feb 2026 original Dukascopy: **7,538,339** ordered XAUUSD Bid/Ask ticks; verified original gz SHA256 `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5`.
- January 1–15 UTC directional training only; January 16–31 UTC held-out comparison; untouched February cross-month frozen-model test. No venue/session clock, broker offset, H4/H1/M15/M5, Watchdog, actual capital pool or trading execution was used as an input.

## Independent original pre-layer hypotheses actually tested

1. **Fixed-price virtual grid** $0.75 / 15s: Jan **54,210** and Feb **60,603** unique shadow signals (event baseline, no actual orders).
2. **Completed-M1 causal volatility gap**: coefficient 0.15 produced **70,101 / 70,431**; 0.25 produced **62,969 / 61,067**; 0.35 produced **53,845 / 51,706** Jan/Feb.
3. **Virtual reversal/retest after initial crossed grid**, stamped at later confirming quote. $0.75 +0.20 retracement: **53,162 / 58,521** Jan/Feb; stronger +0.65 retrace **44,732 / 51,092**; +1.50 retrace **25,566 / 33,915**. Both $0.75 and $1.00 geometries examined at 0.65,1.00,1.50.
4. **Two-stage continuation, more price travel before event**: $0.75 +0.20 crossed-grid confirmation **39,873 / 45,853**; +1.00 confirmation **23,242 / 29,635** Jan/Feb. Four confirmation distances × two grid gaps each tested on Jan and Feb. All 30/120s continuation mean quote-side markouts remain negative.
5. **20 causal candidate attributes × two directions** on eight January generators, at 30/120/300-second price horizons = **320 feature/direction/variant cells per horizon**. Includes historical signed price travel in 5/15/30/60/180s, spread/gap, virtual rung, momentum speed/reversal; tested without session context.
6. **Frozen January-trained constrained directional model** evaluated on held-out late January and then independent February (no refitting on February). Synthetic out-of-sample positive subgroups must NOT be cherry-picked as success.
7. **Hindsight directional oracle** measures the upper bound of whether the market *eventually* moved enough to pay quote-side costs. It is explicitly FUTURE-LOOKING, forbidden for deployment, and NOT evidence of an actionable entry or achievement of the 75% R9 daily qualified opportunity floor.

## Critical empirical findings

**Crossing geometry produces high throughput but no causal stand-alone direction edge.** The baseline Jan candidate median `(Ask−Bid)/$0.75` ≈ **0.928**, so native source spread is about **93% of one grid step** at entry observation. At +30s, the fixed $0.75 generator reversal mean was **−$0.7114** on Jan 1–15 and **−$0.9234** on Jan 16–31; full-Feb +30s reversal **−$1.0742**. All tested generator variants' quote-side 30/120-second reversal/continuation mean markouts were negative across months. These are hypothetical 250ms-delayed quote-side comparisons, **not physical trades or account P/L**.

**Waiting for a stronger move was not a reliable solution.** On $0.75 grid, 0.65× reversal confirmation Jan/Feb 30s reversion **−$0.8460 / −$1.0945**; 1.50× **−$0.9690 / −$1.1905**. The $0.75 +0.20 continuation confirmation Jan/Feb +30s continuation **−$0.8089 / −$1.0501**; +1.00 continuation confirmation **−$0.8927 / −$1.1564**. Event counts decreased without a positive average markout.

**Direction model failed independent replication.** Jan16–31 30s future price-direction accuracy **50.42%**, average hypothetical after $0.02 round-trip comm **−$0.9669**; 120s accuracy **51.32%**, mean **−$0.9579**; 300s accuracy **52.45%**, mean **−$1.0026**. A tiny 381-case late-Jan high-conviction 300s subgroup appeared positive at **+$0.7012**, but SAME frozen model + threshold produced 438 February cases at **−$0.2421**. **REJECT January-only apparent edge**.

**Future-lookahead oracle explicitly nondeployable.** On Jan16–31 the best-of-two-direction **+120s oracle** found a positive after-cost *eventual* markout in ~**81.3%** of events; causal real model achieved nowhere near that. Under only a provisional UTC+2 R9 report-clock hypothesis the impossible future oracle exceeded 75% of R9 daily entries on 21/21 Jan benchmark days, but this is **NOT qualified/feasible-entry coverage**. It reflects sufficient *future amplitude*, not predictability.

## Correct owner-domain interpretation

- **KEEP as research infrastructure**: bounded virtual price-crossing/rung clock, price-step genealogy, quote age, cost/step ratio, two possible directions, one source-tick ordinal per emitted event. Don't simulate additional losing inventory or Martingale.
- **DO NOT PROMOTE**: blind countertrend BUY/SELL, blind continuation, wider required bounces, late breakout confirmation, grid-gap shrinking as an inherent alpha, January model subgroups, theoretical hindsight-oracle profitability, raw count as a qualified trade.
- **What is missing**: reliable pre-session event-time directional information; after-cost conditional movement forecast; non-redundant grid event genealogy; robust price excursion/arrival hazard state; latency and skipped-rung accounting. Better gap shape alone is insufficient.
- **NEXT creative hypothesis families (not yet tested)**: causal first-passage/barrier probability and time-to-failure; virtual-rung renewal/hazard (no lot progression); intrinsic-time directional-change sampling instead of arbitrary 15s cooldown; quote-arrival/price-impact persistence based only on historical original source ticks; stale quote and spike rejection; probability of achievable excursion strictly greater than observed executable bid/ask costs.
- **Do not unlock session layer** until an accepted pre-session generator produces evidence of transferable, non-cherry-picked directional information across chronological Jan and original Feb (or the owner explicitly resets that quant gate). $100,000 is a later hypothetical discovery-account allowance, NOT a reason to relabel negative shadow markouts as a profitable strategy.

## Reproducibility

The following source and exact outputs were created and locally tested during the current turn:
`pre_session_cycle0104.py`, `directional_oracle_audit.py`, `frozen_february_validation.py`, `swing_hysteresis_falsification.py`, `breakout_confirmation.py`, `breakout_scanner.py`, `test_grid0104_invariants.py`, scenario summary JSON, original 320-row per-feature CSV, first-passage prediction and event tape excerpts. 12/12 deterministic tests passed. They were packaged as `GRID0104_REPRODUCIBLE_PRESESSION_GRID_RESEARCH.zip`, SHA256 `0002706a77d45a58f2a7d756ca31216fcfd7ec4fda130288e6dde7824d328af1` in the current conversation; NO protected market inputs embedded. This GitHub report is self-contained but is not a claim that the ZIP is stored in GitHub.

External sources to reproduce hypotheses (not evidence of strategy profits): https://github.com/MegaJoctan/omegafx-youtube-shared-files/tree/main/Python%20Grid%20Bot , https://www.mql5.com/ja/articles/8390 , https://www.mql5.com/ja/articles/7013 , https://www.mql5.com/en/articles/13845 , https://www.reddit.com/r/algotrading/comments/1gkv4th/grid_bot/ , https://www.reddit.com/r/algotrading/comments/1mpxpq6 .


## Additional hypothesis 8 — first-passage price direction, independently falsified

A standalone $0.75 virtual-grid **first-passage prediction** was implemented and evaluated on original tick-level Jan/Feb Mid paths: label which *future* symmetric ±$0.75 barrier is crossed first within predeclared 30s/120s. Predictor receives only prior 1/2/5/15/60/180s bid/ask displacements, source spread change, prior quote-update intensity, virtual rung and initial grid direction. No future barrier label enters a predictor. January 1–15 trained, January 16–31 held out, February independent frozen application. No sessions, no funded order, no profit ledger.

| Time to first ±$0.75 source-mid barrier | Jan later model | Feb frozen model | Feb naive continuation | Feb majority direction |
|---|---:|---:|---:|---:|
| 30 seconds | 51.31% | 51.23% | **52.05%** | 50.57% |
| 120 seconds | 51.56% | 51.01% | **51.60%** | 50.52% |

February 30s has 54,037 resolved labels, median passage time 4,104ms; 120s 60,242 labels, median 5,044.5ms. **The more complex causal predictor performs WORSE than simple grid continuation in independent February**, so it does not justify promotion. First passage on future midpoint is not an executable entry profit, and may not cover ~$0.70 native event spread. Only $0.75 barriers were completed; wider-barrier jobs were not completed and have no certified result. Exact Python `grid0104_first_passage.py` and JSON `GRID0104_FIRST_PASSAGE_JAN_FEB.json` are in the revised 19-file conversation ZIP, SHA256 `0002706a77d45a58f2a7d756ca31216fcfd7ec4fda130288e6dde7824d328af1`. Full revised conversation report SHA256 `48aeddd89b7d432d7f62a05c45c6ed05f4a2bfbfc0fe49eb56d3b861cadb4964`.
