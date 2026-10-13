# GRID0270 emergency source-exact analysis: 2026-07

> **Engineering forensic workpaper — NOT owner governance, NOT a promoted strategy, NOT live MT5 performance.** Original owner whitepaper, ratified full conversation, source code and chronological ledgers remain controlling. No March/April hindsight whitelist may be deployed.

## A. Provenance and comparison contract
- GRID0269 original Dukascopy input `XAUUSD_DUKAS_2026_07_ticks.csv(2).gz`; SHA256 `e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7`; **7,415,841 complete original Bid/Ask ticks**.
- Exact tested profile: `{"broker_session_confirmed": false, "commission_per_roundtrip_usd": 0.2, "contract_oz": 100.0, "global_max_open": 2, "latency_ms": 250, "leverage": 500, "lot": 0.01, "margin_reserve_fraction": 0.35, "require_all_htf": true, "starting_cash": 100000.0}`. Fresh $100,000 hypothetical account every month; fixed 0.01 lot; no Coinexx confirmed deals. No AUG ticks.
- All daily and ISO-week cash are attributed to **UTC exit time**. Week segments reset at month boundaries, not a single contiguous multi-month equity book.
- R9 SYNTH is the **ideal day/week/month ACCOUNT benchmark**; R9 OVERFIT is the *offline per-trade* preferred entry/hold/exit/profit/floating-DD/gross-loss teacher. Neither is an executable signal.
- Prior original mechanics: Original July accepted causal cross-month candidate needs direct original archive retrieval; current repo has no july_2026 original accepted monthly directory. August remains sealed.

## B. Monthly performance: realized and risk
- Realized **−$2,991.25**, gross winners +$2,051.92, gross losers −$5,043.16; cash +$97,008.75 from $100,000; cash/closed-trade ledger residuals 0.0 / 4.320099833421409e-10.
- **3,583** shadow closes, 33.16% win, PF 0.4069, average net/trade **−$0.83**, max tick-marked quote-equity DD **+$3,006.36**, max concurrent positions 2, end open 0.
- Calendar day positives 0, negatives 23; UTC week-segment positives 0, negatives 5.

## C. R9 SYNTH 100% comparison — NOT YET NUMERICALLY JOINED
- The original GRID0186 **already reconstructed** full hour/day/week/month reference tables are known to exist in its preserved archive. Their exact month-matched reference rows have not been loaded into THIS forensic workpaper. **No target number or percent completion has been invented for this month.**
- Required action is reference-table reuse, *not* re-auditing reports or recreating validated Dukascopy tick candles. Apply verified UTC mapping to period keys only.

## D. Exit-root economics, not merely headline P&L
| Exit reason | Trades | Net | Gross win | Gross loss | Avg/trade | Share |
|---|---:|---:|---:|---:|---:|---:|
| `L6_INVALIDATION` | 1,288 | −$3,865.95 | $0.00 | −$3,865.95 | −$3.00 | 35.95% |
| `L7_TIME_EXPIRY` | 1,721 | −$340.27 | +$818.55 | −$1,158.81 | −$0.20 | 48.03% |
| `L7_TRAILING_OR_HARD_STOP` | 313 | +$144.36 | +$162.76 | −$18.40 | +$0.46 | 8.74% |
| `L3_TARGET` | 261 | +$1,070.61 | +$1,070.61 | $0.00 | +$4.10 | 7.28% |
**Observed:** L6 invalidation alone caused **−$3,865.95 across 1,288 exits**, a major negative contribution. This proves the account loss is concentrated by exit label; it does **not** prove widening stops would improve causal profitability. Prior entry/adverse-path features and alternative holds require paired same-entry tick-path tests before changing policy.

## E. Session and direction contributions
| Session | Closes | Net | Win rate | Profit factor | Avg/trade |
|---|---:|---:|---:|---:|---:|
| NEW_YORK | 1,602 | −$1,510.92 | 31.34% | 0.355 | −$0.94 |
| LONDON | 1,664 | −$1,226.10 | 35.22% | 0.466 | −$0.74 |
| SYDNEY | 181 | −$156.67 | 31.49% | 0.360 | −$0.87 |
| TOKYO | 136 | −$97.56 | 30.15% | 0.394 | −$0.72 |

| Side | Trades | Net | Win | Per-trade net |
|---|---:|---:|---:|---:|
| SELL | 1,880 | −$1,421.68 | 34.31% | −$0.76 |
| BUY | 1,703 | −$1,569.57 | 31.77% | −$0.92 |

## F. Exact vertical-funnel diagnostics (COUNTER EMISSIONS, not unique ticket counts)
| Stage/counter | Value | Interpretation |
|---|---:|---|
| `prel1_creator_grid_raw` | 326,944 | L0 virtual price-event emissions |
| `l2_opportunity_windows` | 2,359,363 | L2 qualifying windows (can be repeated ticks) |
| `l3_no_creator_grid_crossing` | 2,297,208 | L2 permitted but G0 event not available |
| `l3_proposals` | 55,261 | Source + structure qualified L3 proposals |
| `qualified_quality_chain` | 44,094 | L1–L6 quality passes |
| `l7_spread_denied` | 13,151 | L7 observed original-spread denial |
| `l7_prequeue_global_capacity_denied` | 25,901 | L7 blocked at 2-position global cap |
| `l7_prequeue_desk_capacity_denied` | 765 | L7 blocked by per-desk cap |
| `l7_risk_eligible_requests` | 4,277 | L7 submitted queue requests |
| `expired_latency` | 74 | Stale pending after 250ms latency |
| `spread_drift` | 618 | Later quote spread drift |
| `filled` | 3,583 | Hypothetical quote fills |
| `l4_simulated_positive_close_NOT_PAID` | 16,062 | Prior positive shadow close logged, not paid renewal |
| `l4_broker_paid_parent_context` | 0 | Actual broker paid parent context |
| `l6_warning` | 1,963 | Position warning occurrences |
| `l6_bounded_recovery_watch` | 885 | Intent to reassess after invalidation |
| `l6_state_confirmed_recovery_candidate` | 0 | Reentry candidates completing L6 recovery logic |
| `l7_capital_halt` | 0 | Simulated risk halt |
- **Source proposal ID preserved on 5/3,583 closes (0.14%); 3,578 shadow closes have no numeric source ID.** The current `Opportunity` source string and G0 adapter are not the same as verified/earned parent→child identity. Missing optional IDs are an integration diagnostic, not proof of fabricated trades.
- Execution rate: 8.13% of *quality-pass event count* becomes a close; this is an approximate FUNNEL COUNTER ratio, not a unique-eligible-opportunity probability.
- **Current shadow execution cannot earn genuine paid parent close credit:** `V1BrokerEvidencePort` requires independently observed broker DEAL_ADD. For Python research, a separately labeled hypothetical funded/settled ledger needs to drive the causally modeled renewal experiment, while retaining the strict broker-only accounting boundary. This is a missing testable research path, NOT permission to fabricate broker deals.
- Simultaneous capacity 2 compared with original historical March/April frontiers often requiring hundreds of positions is a structural mismatch. **Do not blindly raise cap**: current negative expectancy would likely multiply losses. First reproduce causal positive source and cost model, then test graduated heat-limited capacity.

## G. Entry-hour attribution — UTC (close cash attributed back to entry cohort for diagnostic only)
| Entry UTC hour | Trades | Entry cohort net | Win rate | Avg/trade |
|---|---:|---:|---:|---:|
| 00:00 | 5 | −$5.50 | 20.00% | −$1.10 |
| 01:00 | 31 | −$9.50 | 45.16% | −$0.31 |
| 02:00 | 39 | −$37.20 | 28.21% | −$0.95 |
| 03:00 | 33 | −$23.78 | 24.24% | −$0.72 |
| 04:00 | 27 | −$15.00 | 29.63% | −$0.56 |
| 05:00 | 30 | −$32.89 | 33.33% | −$1.10 |
| 06:00 | 80 | −$64.85 | 33.75% | −$0.81 |
| 07:00 | 268 | −$174.30 | 39.55% | −$0.65 |
| 08:00 | 162 | −$99.20 | 37.65% | −$0.61 |
| 09:00 | 236 | −$175.74 | 35.59% | −$0.74 |
| 10:00 | 213 | −$158.09 | 30.52% | −$0.74 |
| 11:00 | 139 | −$154.12 | 22.30% | −$1.11 |
| 12:00 | 243 | −$130.96 | 40.74% | −$0.54 |
| 13:00 | 390 | −$337.02 | 36.41% | −$0.86 |
| 14:00 | 400 | −$402.18 | 33.50% | −$1.01 |
| 15:00 | 292 | −$260.33 | 32.53% | −$0.89 |
| 16:00 | 206 | −$225.68 | 25.73% | −$1.10 |
| 17:00 | 202 | −$153.43 | 27.23% | −$0.76 |
| 18:00 | 186 | −$176.10 | 27.96% | −$0.95 |
| 19:00 | 270 | −$269.04 | 33.33% | −$1.00 |
| 20:00 | 130 | −$85.81 | 30.77% | −$0.66 |
| 22:00 | 1 | −$0.53 | 0.00% | −$0.53 |

## H. Entry/hold/exit/profit/drawdown/gross-loss — 75% OVERFIT teacher program (NOT yet scored)
- Realized current hold seconds: p10 **36.33**, median **198.56**, p90 **240.32**, p99 **242.26**. Current desk planned expiry 180–240 seconds; observed holds depend on exit reasons and tick chronology.
- Observed realized net mean per trade: −$0.83; gross loss per trade −$1.41; monthly quote-equity DD +$3,006.36 (a different risk dimension than an individual trade MAE).
- **Missing for 75% objective:** explicit original R9 OVERFIT event universe, matched entry/hold/exit targets with time/price normalization, matched post-entry MAE/MFE paths, and a prespecified definition of “75% of preferred per-trade performance” for metrics where lower is better (drawdown/gross loss). No OVERFIT labels were joined to these V1 trades; therefore attainment is UNMEASURED, not 0% or passed.
- Build offline teacher matching only AFTER settling both event populations, retaining nonmatched rows. Runtime may use only entry-time information, not optimal future exits, best trade outcome or oracle direction.

## I. Complete UTC daily close-time settled performance (including zero-trade dates)
| UTC day | Closes | Net USD | Gross loss USD | PF | Win % | Quote-equity DD USD | Quality passes | Funded requests |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-07-01 | 73 | −$59.25 | −$125.85 | 0.53 | 41.10% | 73.88 | 1,172 | 89 |
| 2026-07-02 | 59 | −$43.65 | −$80.73 | 0.46 | 37.29% | 56.09 | 462 | 66 |
| 2026-07-03 | 35 | −$42.90 | −$55.63 | 0.23 | 20.00% | 43.94 | 416 | 66 |
| 2026-07-04 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-07-05 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-07-06 | 220 | −$192.18 | −$313.12 | 0.39 | 35.00% | 201.11 | 2,944 | 278 |
| 2026-07-07 | 187 | −$98.39 | −$232.72 | 0.58 | 35.29% | 100.26 | 1,818 | 211 |
| 2026-07-08 | 178 | −$139.51 | −$273.31 | 0.49 | 36.52% | 151.79 | 1,962 | 244 |
| 2026-07-09 | 138 | −$146.14 | −$199.73 | 0.27 | 23.91% | 151.60 | 1,277 | 212 |
| 2026-07-10 | 164 | −$118.32 | −$207.59 | 0.43 | 36.59% | 130.39 | 2,726 | 187 |
| 2026-07-11 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-07-12 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-07-13 | 148 | −$143.66 | −$201.48 | 0.29 | 29.05% | 151.75 | 2,453 | 192 |
| 2026-07-14 | 229 | −$245.39 | −$375.89 | 0.35 | 32.75% | 251.08 | 3,667 | 272 |
| 2026-07-15 | 182 | −$107.81 | −$232.25 | 0.54 | 37.91% | 123.87 | 2,788 | 206 |
| 2026-07-16 | 225 | −$210.86 | −$343.81 | 0.39 | 32.89% | 216.16 | 2,157 | 241 |
| 2026-07-17 | 103 | −$86.67 | −$130.86 | 0.34 | 33.98% | 90.17 | 1,554 | 133 |
| 2026-07-18 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-07-19 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-07-20 | 176 | −$198.74 | −$256.38 | 0.22 | 27.27% | 199.65 | 1,788 | 185 |
| 2026-07-21 | 140 | −$142.41 | −$197.66 | 0.28 | 30.00% | 145.24 | 1,892 | 166 |
| 2026-07-22 | 158 | −$127.52 | −$205.57 | 0.38 | 33.54% | 146.68 | 1,907 | 177 |
| 2026-07-23 | 198 | −$203.49 | −$306.11 | 0.34 | 29.80% | 209.99 | 2,605 | 239 |
| 2026-07-24 | 154 | −$84.82 | −$167.94 | 0.49 | 37.01% | 99.97 | 1,374 | 165 |
| 2026-07-25 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-07-26 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-07-27 | 108 | −$68.79 | −$128.87 | 0.47 | 34.26% | 73.51 | 1,655 | 145 |
| 2026-07-28 | 162 | −$138.58 | −$237.25 | 0.42 | 32.72% | 147.05 | 1,215 | 184 |
| 2026-07-29 | 172 | −$162.11 | −$260.46 | 0.38 | 30.81% | 164.85 | 2,485 | 205 |
| 2026-07-30 | 195 | −$99.61 | −$280.54 | 0.64 | 38.97% | 144.61 | 1,691 | 201 |
| 2026-07-31 | 179 | −$130.45 | −$229.41 | 0.43 | 29.05% | 131.46 | 2,086 | 213 |

## J. Complete UTC ISO-week closed-trade performance (month-scoped ISO week segments)
| UTC ISO week | Closes | Net USD | Gross loss USD | PF | Win % | Quote-equity DD USD |
|---|---:|---:|---:|---:|---:|---:|
| 2026-W27 | 167 | −$145.80 | −$262.21 | 0.44 | 35.33% | 160.94 |
| 2026-W28 | 887 | −$694.53 | −$1,226.47 | 0.43 | 33.93% | 706.18 |
| 2026-W29 | 887 | −$794.39 | −$1,284.29 | 0.38 | 33.37% | 800.51 |
| 2026-W30 | 826 | −$756.98 | −$1,133.66 | 0.33 | 31.36% | 758.29 |
| 2026-W31 | 816 | −$599.54 | −$1,136.53 | 0.47 | 33.21% | 603.17 |

## K. Month-specific root-cause hypothesis / missing original behavior
1. **SOURCE-EXACT OWNER MECHANISM:** July: time-expiry volume and its net are especially poor; restore per-specialist duration classification before any blanket extension. Fourth-party session transfer must remain evaluated on UTC original ticks.
2. **GATE EVIDENCE:** Spread filtering is material but does not explain the independently negative expectancy of trades that executed.
3. **PAID GENEALOGY:** No complete shadow-only paid-closed chain with predecessor trade ID, strict settlement and realized hold bucket is fed back into source gate. Required for causal shadow research, not actual broker-claim conversion.
4. **CREDIT ROUTING:** Current source ID attribute mostly None; trace originating G0 family→quality veto→position→exit and require explicit parent-child chain for source promotions. Do not synthesize ID from a source string.
5. **LOSS-FIRST:** Invalidation and stop/expiry sub-populations must be analyzed with entry-time features and held-out month guardrail. Paired same-entry counterfactual exits use actual later Dukascopy ticks and *only for offline evaluation*.
6. **CAPACITY:** Two-position research choke point is not comparable with original high-throughput session/Watchdog research. Relax only after passing positive after-cost expected-return/risk conditions, graduate with cap4/8/16/32 not unbounded or Martingale.

## L. Executable prioritized engineering plan, pass/fail conditions
- **P0 / Source-reuse:** retrieve accepted original January/February code and historical March135/April136T2 source artifacts; provenance SHA + config + cash-unit audit; do not rebuild from summaries or overwrite original evidence.
- **P0 / Exact ancestry test:** every accepted hypothetical trade must carry unique immutable G0 source family/event ID, cross timestamp, signal-known time, barrier/expiry and distinct shadow-funded actual-book result; no backdated credit. Differentiate virtual proposer event from funded ticket.
- **P0 / Parent-child shadow parity:** settled entry→exit→paid-after-cost predecessor history drives only later candidate renewals; rejected/never-filled/no actual close gives zero credit. Keep broker contract default UNKNOWN; never call broker-confirmed methods from quote replay.
- **P1 / Direction+L6 ablation:** compare same entry set to current L6, fixed stop, state-matured invalidation and short-harvest/runner dynamic trailing using the same ordered original opposing Bid/Ask ticks; report out-of-period gross loss and DD, not only best-case gains.
- **P1 / Session specialist completeness:** restore separate Asia and London/overlap/NY dense opportunities under one L1–L7 governor; a time label alone does not produce high probability entry. No month-name runtime switches.
- **P2 / Capacity/velocity:** evaluate rising caps under shared margin/heat and real funded life without losing positive signed expectancy; target monthly, weekly and each UTC trading day jointly.
- **P2 / R9 comparison:** join preserved R9 SYNTH daily/week/month ledger without new MT5 report audit; join R9 OVERFIT per-trade teacher by event and score six distinct dimensions with owner-approved matching thresholds. No lookahead and no fabricated shortfall percentages.

## M. Recovery evidence and limitations
- Local source: `GRID0269_SEVEN_MONTH_FULL_TICK/2026-07/month_full_qa.json`, `/all_completed_shadow_trades.csv`, `/daily_performance.csv`, `/weekly_performance.csv`, `/run_config.json`.
- No new full-tick strategy replay was performed for this forensic diagnostic; numeric breakdown is rederived from 57.5m-tick completed GRID0269 original execution ledgers and exact current implementation source.
- Full-tick replay market P&L is modeled quote/cash economics, not Coinexx broker fill certification; end-of-month positions all closed, month transitions independently reset; metrics do not by themselves validate 100% R9 SYNTH or 75% R9 OVERFIT.
- This report is a research workpaper for the developer, not the governing law. Frozen owner instructions, archived successful source and original primary data outrank this diagnosis. Original GRID0258 ledger, J0183 official cursor, and August seal remain unchanged.
