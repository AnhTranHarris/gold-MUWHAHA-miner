# GRID0270 — EMERGENCY JAN–JUL V1 Python engine source-exact diagnostic and repair guide

> **Scientific status: FORENSIC DIAGNOSTIC ONLY.** All seven original Dukascopy complete month replays were performed previously in GRID0269. This guide derives secondary economic/engineering evidence from those exact trade/period ledgers and reads original source. It **does not** promote a candidate, recertify MT5, supersede the original frozen V1 owner whitepaper, or justify restarting research.

## The owner-defined target roles (no reference environment substitution)
- **R9 SYNTH** = ideal performance at *every* UTC day, ISO week and month for net cash, trade velocity, gross loss, drawdown and quality; no trading from SYNTH-generated prices.
- **R9 OVERFIT** = offline **per-trade** preferred entry / hold / exit / profit / drawdown / gross loss; no future optimal label in causal live features.
- **Dukascopy** = full original tick-level Python execution and derived candle research/refinement; established, do not re-audit source validity or MT5 reports.
- **One adaptive system** = L0 ordered ticks, L1 session-specific opportunity, L2 completed H4/H1/M15/M5, L3 dense high-volume + distinct Asia, L4 paid-close earned Watchdog, L5 causal trend-within-trend, L6 bounded wrong-direction, L7 shared heat/cash governor. Month names evaluation partitions only.
- Engine source at `research/delta_a_alpha/implementation/v1_four_session_architecture.py`, cumulative G0 `v1_grid_cumulative_source_adapter_0264.py`, `v1_grid_strategy_source_router.py`, and broker-only `v1_grid_broker_evidence_port_0265.py`. Original March `monthly/march_2026/daa_march_vertical_grid_replay_135.py`, April `monthly/april_2026/apr_campaign_transition_map_136t0_fast.py` / original 136T2. Read ORIGINAL full whitepaper and raw exact code before modifying.

## Severity matrix — observed FULL seven-month baseline
| Month | Completed | Current net | PF | Win % | Max floating DD | L6 exits | L6 total net | Source IDs present | L7 cap denials |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-01 | 3,258 | −$3,015.32 | 0.413 | 33.30% | +$3,030.15 | 1,463 | −$4,437.14 | 13/3,258 | 20,857 |
| 2026-02 | 1,384 | −$1,082.65 | 0.534 | 35.33% | +$1,099.92 | 649 | −$2,092.56 | 3/1,384 | 5,069 |
| 2026-03 | 2,839 | −$2,382.16 | 0.512 | 35.19% | +$2,418.74 | 1,478 | −$4,610.26 | 9/2,839 | 15,916 |
| 2026-04 | 2,674 | −$2,569.05 | 0.403 | 32.16% | +$2,572.45 | 1,244 | −$3,726.32 | 3/2,674 | 19,405 |
| 2026-05 | 3,504 | −$2,774.65 | 0.464 | 35.07% | +$2,797.47 | 1,510 | −$4,415.07 | 5/3,504 | 29,851 |
| 2026-06 | 4,240 | −$3,356.50 | 0.488 | 33.82% | +$3,360.69 | 1,933 | −$5,718.05 | 8/4,240 | 31,662 |
| 2026-07 | 3,583 | −$2,991.24 | 0.407 | 33.16% | +$3,006.36 | 1,288 | −$3,865.95 | 5/3,583 | 25,901 |

**Aggregate:** 57,527,562 raw quote ticks; 21,482 shadow closes; combined independent-month net −$18,171.58; L6 9,565 exits / −$28,865.35; numerical source IDs 46/21,482 (0.21%). **Each month resets capital and warmup, so pooled totals are not a continuous account.**

## R9 SYNTH exact period-level acceptance (existing original GRID0186 reference, NOT rebuilt)
| Month | Known original R9 SYNTH monthly account net | Original trades | Current V1 net | V1 trades | Net gap to positive ideal | Completed trades deficit |
|---|---:|---:|---:|---:|---:|---:|
| 2026-01 | **not imported (original GRID0186 required)** | **not imported** | −$3,015.32 | 3,258 | **unmeasured** | **unmeasured** |
| 2026-02 | **not imported (original GRID0186 required)** | **not imported** | −$1,082.65 | 1,384 | **unmeasured** | **unmeasured** |
| 2026-03 | +$75,698.63 | 40,985 | −$2,382.16 | 2,839 | +$78,080.79 | 38,146 |
| 2026-04 | +$38,353.96 | 31,758 | −$2,569.05 | 2,674 | +$40,923.01 | 29,084 |
| 2026-05 | **not imported (original GRID0186 required)** | **not imported** | −$2,774.65 | 3,504 | **unmeasured** | **unmeasured** |
| 2026-06 | **not imported (original GRID0186 required)** | **not imported** | −$3,356.50 | 4,240 | **unmeasured** | **unmeasured** |
| 2026-07 | **not imported (original GRID0186 required)** | **not imported** | −$2,991.24 | 3,583 | **unmeasured** | **unmeasured** |

- Original GitHub March135 and April136T2 docs provide March/April exact original R9 monthly account figures (with labels; not recomputed or re-audited). This run **does not independently load original GRID0186 period-table rows**. No fabricated Jan/Feb/May/Jun/Jul R9 per-month figures or daily/week deltas. Existing archive: https://drive.google.com/file/d/1j80BzC7nFkKCGlMKkvauWJJxhGxvJnmr/view
- Full 100% R9 SYNTH criterion requires **all corresponding days, weeks, months** in the same time mapping and cash units, same distinct closed-trade universe; prevent a positive month masking negative days. Separate per-period profit, gross losses, float DD, win, PF, expectancy and velocity rather than one combined score.
- **75% R9 OVERFIT per-trade is NOT YET MEASURABLE:** no exact per-trade matched OVERFIT labels were loaded with GRID0269 V1 trades. The objective requires a predeclared normalization for entry-time/price error, hold-time, exit-time/price error, retained realized profit, MAE/drawdown containment and gross loss; cannot advertise 75% from aggregate win rates.

## P0 engineering root cause — exact code evidence, not a performance story
1. **L6 invalidation adverse-selection/lifecycle:** `_life` marks warnings when adverse excursion breaches 45% of desk stop and closes on 65% adverse excursion, before hard stop. Across seven months this exit class alone books the largest negative contribution. A causal same-entry-counterfactual rerun is needed; just disabling it, raising stops, or picking hindsight winners is prohibited.
2. **Two-position global funded cap versus preserved original high-density source research:** `global_max_open=2` in GRID0269 profile and `DESKS` 1–2 caps, plus per-timestamp `last_order_tick` and grid arbiter are actual bottlenecks. Original March135 QUAL historical cap448 and April136T2 cap512 refer to *retrospective research-selected* source populations, not a valid mandate to trade hundreds of live positions. Do not solve negative PF by adding size/cap first.
3. **Missing shadow paid-parent→child mechanism:** `V1BrokerEvidencePort` correctly refuses to invent true broker DEAL_ADD. However shadow `_complete_close` only updates `watchdog_closed` and a soft positive flag; no full original April136T2 rule→depth→previous realized-child P/L+hold bucket→next child admission receives paid *shadow* settlements. Dedicated isolated simulated-funded chronology path is required for original *Python research*, without falsely asserting broker confirmation.
4. **Source IDs missing:** `Opportunity.paid_proposal_id` and `Position.source_proposal_id` are optional. Source family string may exist without a numeric creator paid proposal; only 46/21,482 observed shadow trades have such IDs. Ensure immutable genuine source chain distinct from optional broker ticket and pass it through all veto/queue paths, then credit only actual settled shadow entries.
5. **Incomplete original session specialist fidelity:** Current fixed `DeskSpec` per-session gap/spread/stop/target/180–240s timeout plus `_structure` H4/H1/M15/M5 veto is not source-exact March135 NAT/HV/ASIA/WDQ/REC1 nor April136T2 renewal. Labels on current desk are not proof those original accepted causal mechanisms survived. Original successful historical cells were selected using own month outcomes, so do not code their whitelist.
6. **Economics not explained by flat commission:** fee $0.20/trade totals $4,296.40 across 21,482 trades. Even mathematically removing all booked commissions would leave independent-month net around −$13,875.18. Spread is already in actual opposite-side quotes; dropping cost cannot recover the high-performance frontier.

## Progressive emergency repair priorities — source-first, cumulative, no strategy reset
**R0 — Reconcile originals and stop evidence drift.** Preserve existing success, read full source and original accepted configs, direct January/February original owner frontier archives, March135 original helper+stream, April136T2 predecessor source and J0183 caution. Map each layer to current implementation lines. Classify exact vs equivalent vs absent. No old Jan/Feb contaminated derived artifacts are reactivated. No generic MT5-report audits.
**R1 — Restore chronological unique ancestry and shadow-funded paid credit.** G0 unique IDs (source family and event), T1 known timestamp, T2 pending, observed Bid/Ask fill, actual in-Python parent entry, close net and hold time, and previous-child next permission, all in an ISOLATED shadow funding ledger. Broker evidence still independent/zero. Replay Jan only first, then carry code unchanged to Feb–Jul; verify exact causality.
**R2 — Repair L6 winner/loser asymmetry.** Tag pre-entry structural state, adverse excursion and exit reason. On same *original* entry set, test causal completion/short-harvest/runner alternatives with genuine later Bid/Ask; require gross loss and max floating DD nonregression out of discovery segment. No future-overfit features.
**R3 — Restore authentic L1-L3 session-aware rapid opportunity pathways.** Source-exact native/high-volume/Asia supply and signed direction + completed MTF permissions, with selectable geometry from causal market state not month. Measure sourced qualified opportunities by day/hour and entire Jan-Jul, not G0 repeated raw event counts.
**R4 — Scale only after positive expectancy.** Gradually test shared cap2/4/8/16/32 and longer runner small sleeve, margin/heat total exposure and realistic 0.01 lot. Risk-first hard ceiling; never loss-dependent lots, Martingale or copying historical cap 448/512 blindly.
**R5 — Paired monthly/week/day and six-dimensional per-trade acceptance.** Import previously reconstructed R9 SYNTH periods from GRID0186 and original R9 OVERFIT matched teacher labels, preserving ORIGINAL source file hashes. Monthly net/velocity alone insufficient; per-day and ISO-week 100% + gross loss/DD constraints, and matched per-trade 75% target with approved score definitions; no undeclared hindsight matching.
**R6 — Deployment only after separately requested owner approval.** Current engine negative and not ready. Evidence reproducibility, across-month robustness, broker contract capture / MQL5 parity after Python positive. Keep J0183, trading disabled, August sealed.

## Month action dossiers
- **2026-01:** [full daily/week/exit/session/gate/root evidence](GRID0270_2026-01_EMERGENCY_DETAILED_CATEGORY_DIAGNOSIS.md); current net −$3,015.32, L6 −$4,437.14, source IDs 13/3258.
- **2026-02:** [full daily/week/exit/session/gate/root evidence](GRID0270_2026-02_EMERGENCY_DETAILED_CATEGORY_DIAGNOSIS.md); current net −$1,082.65, L6 −$2,092.56, source IDs 3/1384.
- **2026-03:** [full daily/week/exit/session/gate/root evidence](GRID0270_2026-03_EMERGENCY_DETAILED_CATEGORY_DIAGNOSIS.md); current net −$2,382.16, L6 −$4,610.26, source IDs 9/2839.
- **2026-04:** [full daily/week/exit/session/gate/root evidence](GRID0270_2026-04_EMERGENCY_DETAILED_CATEGORY_DIAGNOSIS.md); current net −$2,569.05, L6 −$3,726.32, source IDs 3/2674.
- **2026-05:** [full daily/week/exit/session/gate/root evidence](GRID0270_2026-05_EMERGENCY_DETAILED_CATEGORY_DIAGNOSIS.md); current net −$2,774.65, L6 −$4,415.07, source IDs 5/3504.
- **2026-06:** [full daily/week/exit/session/gate/root evidence](GRID0270_2026-06_EMERGENCY_DETAILED_CATEGORY_DIAGNOSIS.md); current net −$3,356.50, L6 −$5,718.05, source IDs 8/4240.
- **2026-07:** [full daily/week/exit/session/gate/root evidence](GRID0270_2026-07_EMERGENCY_DETAILED_CATEGORY_DIAGNOSIS.md); current net −$2,991.24, L6 −$3,865.95, source IDs 5/3583.

## Provenance and valid/invalid conclusions
- Original source: owner frozen whitepaper SHA Git blob `1b92b3c89159681a7181508de158af685cf5780c`, full owner-ratified governing conversation; read originals, not this workpaper as replacement.
- Original GitHub March135 replay blob `2ee6be008a058288fd5a6fddacf9851d684bbc4c`, discovery doc `4f27451063a00bd4fb726a88a46d85f8553a9ef9`; April136T2 doc `cfe124225ae9d8ee3dfa8a4c82e9c802af72e947`; archived GRID0183 true-price revalidation.
- GRID0269 original first-party monthly results `month_full_qa.json`, `all_completed_shadow_trades.csv`, daily and weekly cash ledgers for all seven months. No new full-tick rerun here and no new profit breakthrough, no active code/strategy change.
- Historical accepted modeled account results are not necessarily deployable because profitable trade-cell selection may include hindsight, original modeling cash unit differs from independently priced USD/oz, and source has short subsecond life spans. No backtest can promise 100% of R9 SYNTH.
- No numerical R9 OVERFIT alignment or per-trade teacher matching has been measured yet; any claim otherwise is invalid.
- No release, no EA conversion, no August 2026 opening, no old successful research overwrite.
