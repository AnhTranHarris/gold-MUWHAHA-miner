# GRID0270 emergency source-exact analysis: 2026-02

> **Engineering forensic workpaper — NOT owner governance, NOT a promoted strategy, NOT live MT5 performance.** Original owner whitepaper, ratified full conversation, source code and chronological ledgers remain controlling. No March/April hindsight whitelist may be deployed.

## A. Provenance and comparison contract
- GRID0269 original Dukascopy input `XAUUSD_DUKAS_2026_02_ticks.csv(3).gz`; SHA256 `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`; **7,538,339 complete original Bid/Ask ticks**.
- Exact tested profile: `{"broker_session_confirmed": false, "commission_per_roundtrip_usd": 0.2, "contract_oz": 100.0, "global_max_open": 2, "latency_ms": 250, "leverage": 500, "lot": 0.01, "margin_reserve_fraction": 0.35, "require_all_htf": true, "starting_cash": 100000.0}`. Fresh $100,000 hypothetical account every month; fixed 0.01 lot; no Coinexx confirmed deals. No AUG ticks.
- All daily and ISO-week cash are attributed to **UTC exit time**. Week segments reset at month boundaries, not a single contiguous multi-month equity book.
- R9 SYNTH is the **ideal day/week/month ACCOUNT benchmark**; R9 OVERFIT is the *offline per-trade* preferred entry/hold/exit/profit/floating-DD/gross-loss teacher. Neither is an executable signal.
- Prior original mechanics: Whitepaper §5 original February 134E approximately +$117k; 134K approximately +$189.96k and +$200.16k frontiers. Original accepted source/config must be read before parity claim.

## B. Monthly performance: realized and risk
- Realized **−$1,082.65**, gross winners +$1,239.82, gross losers −$2,322.47; cash +$98,917.35 from $100,000; cash/closed-trade ledger residuals 0.0 / 8.196820999728516e-10.
- **1,384** shadow closes, 35.33% win, PF 0.5338, average net/trade **−$0.78**, max tick-marked quote-equity DD **+$1,099.92**, max concurrent positions 2, end open 0.
- Calendar day positives 1, negatives 19; UTC week-segment positives 0, negatives 4.

## C. R9 SYNTH 100% comparison — NOT YET NUMERICALLY JOINED
- The original GRID0186 **already reconstructed** full hour/day/week/month reference tables are known to exist in its preserved archive. Their exact month-matched reference rows have not been loaded into THIS forensic workpaper. **No target number or percent completion has been invented for this month.**
- Required action is reference-table reuse, *not* re-auditing reports or recreating validated Dukascopy tick candles. Apply verified UTC mapping to period keys only.

## D. Exit-root economics, not merely headline P&L
| Exit reason | Trades | Net | Gross win | Gross loss | Avg/trade | Share |
|---|---:|---:|---:|---:|---:|---:|
| `L6_INVALIDATION` | 649 | −$2,092.56 | $0.00 | −$2,092.56 | −$3.22 | 46.89% |
| `L7_TIME_EXPIRY` | 347 | +$10.01 | +$221.98 | −$211.97 | +$0.03 | 25.07% |
| `L7_TRAILING_OR_HARD_STOP` | 184 | +$78.35 | +$96.29 | −$17.95 | +$0.43 | 13.29% |
| `L3_TARGET` | 204 | +$921.55 | +$921.55 | $0.00 | +$4.52 | 14.74% |
**Observed:** L6 invalidation alone caused **−$2,092.56 across 649 exits**, a major negative contribution. This proves the account loss is concentrated by exit label; it does **not** prove widening stops would improve causal profitability. Prior entry/adverse-path features and alternative holds require paired same-entry tick-path tests before changing policy.

## E. Session and direction contributions
| Session | Closes | Net | Win rate | Profit factor | Avg/trade |
|---|---:|---:|---:|---:|---:|
| NEW_YORK | 913 | −$716.48 | 36.25% | 0.538 | −$0.78 |
| LONDON | 432 | −$332.96 | 32.87% | 0.534 | −$0.77 |
| SYDNEY | 28 | −$29.16 | 35.71% | 0.366 | −$1.04 |
| TOKYO | 11 | −$4.05 | 54.55% | 0.667 | −$0.37 |

| Side | Trades | Net | Win | Per-trade net |
|---|---:|---:|---:|---:|
| BUY | 698 | −$668.19 | 33.52% | −$0.96 |
| SELL | 686 | −$414.46 | 37.17% | −$0.60 |

## F. Exact vertical-funnel diagnostics (COUNTER EMISSIONS, not unique ticket counts)
| Stage/counter | Value | Interpretation |
|---|---:|---|
| `prel1_creator_grid_raw` | 371,251 | L0 virtual price-event emissions |
| `l2_opportunity_windows` | 2,200,815 | L2 qualifying windows (can be repeated ticks) |
| `l3_no_creator_grid_crossing` | 2,132,856 | L2 permitted but G0 event not available |
| `l3_proposals` | 61,902 | Source + structure qualified L3 proposals |
| `qualified_quality_chain` | 44,303 | L1–L6 quality passes |
| `l7_spread_denied` | 36,223 | L7 observed original-spread denial |
| `l7_prequeue_global_capacity_denied` | 5,069 | L7 blocked at 2-position global cap |
| `l7_prequeue_desk_capacity_denied` | 44 | L7 blocked by per-desk cap |
| `l7_risk_eligible_requests` | 2,967 | L7 submitted queue requests |
| `expired_latency` | 59 | Stale pending after 250ms latency |
| `spread_drift` | 1,519 | Later quote spread drift |
| `filled` | 1,384 | Hypothetical quote fills |
| `l4_simulated_positive_close_NOT_PAID` | 22,547 | Prior positive shadow close logged, not paid renewal |
| `l4_broker_paid_parent_context` | 0 | Actual broker paid parent context |
| `l6_warning` | 867 | Position warning occurrences |
| `l6_bounded_recovery_watch` | 469 | Intent to reassess after invalidation |
| `l6_state_confirmed_recovery_candidate` | 0 | Reentry candidates completing L6 recovery logic |
| `l7_capital_halt` | 0 | Simulated risk halt |
- **Source proposal ID preserved on 3/1,384 closes (0.22%); 1,381 shadow closes have no numeric source ID.** The current `Opportunity` source string and G0 adapter are not the same as verified/earned parent→child identity. Missing optional IDs are an integration diagnostic, not proof of fabricated trades.
- Execution rate: 3.12% of *quality-pass event count* becomes a close; this is an approximate FUNNEL COUNTER ratio, not a unique-eligible-opportunity probability.
- **Current shadow execution cannot earn genuine paid parent close credit:** `V1BrokerEvidencePort` requires independently observed broker DEAL_ADD. For Python research, a separately labeled hypothetical funded/settled ledger needs to drive the causally modeled renewal experiment, while retaining the strict broker-only accounting boundary. This is a missing testable research path, NOT permission to fabricate broker deals.
- Simultaneous capacity 2 compared with original historical March/April frontiers often requiring hundreds of positions is a structural mismatch. **Do not blindly raise cap**: current negative expectancy would likely multiply losses. First reproduce causal positive source and cost model, then test graduated heat-limited capacity.

## G. Entry-hour attribution — UTC (close cash attributed back to entry cohort for diagnostic only)
| Entry UTC hour | Trades | Entry cohort net | Win rate | Avg/trade |
|---|---:|---:|---:|---:|
| 00:00 | 4 | −$6.44 | 25.00% | −$1.61 |
| 01:00 | 1 | −$2.43 | 0.00% | −$2.43 |
| 02:00 | 4 | −$2.17 | 25.00% | −$0.54 |
| 03:00 | 6 | −$14.30 | 16.67% | −$2.38 |
| 04:00 | 2 | −$1.74 | 50.00% | −$0.87 |
| 05:00 | 4 | +$0.25 | 50.00% | +$0.06 |
| 06:00 | 1 | +$0.73 | 100.00% | +$0.73 |
| 07:00 | 6 | +$1.64 | 66.67% | +$0.27 |
| 08:00 | 71 | −$65.85 | 32.39% | −$0.93 |
| 09:00 | 61 | −$58.88 | 31.15% | −$0.97 |
| 10:00 | 72 | +$0.93 | 43.06% | +$0.01 |
| 11:00 | 65 | −$49.60 | 30.77% | −$0.76 |
| 12:00 | 20 | −$33.05 | 15.00% | −$1.65 |
| 13:00 | 98 | −$148.59 | 32.65% | −$1.52 |
| 14:00 | 123 | −$92.43 | 38.21% | −$0.75 |
| 15:00 | 67 | −$29.43 | 43.28% | −$0.44 |
| 16:00 | 198 | −$156.91 | 34.85% | −$0.79 |
| 17:00 | 114 | −$72.19 | 36.84% | −$0.63 |
| 18:00 | 155 | −$93.98 | 36.13% | −$0.61 |
| 19:00 | 118 | −$49.21 | 37.29% | −$0.42 |
| 20:00 | 115 | −$105.60 | 33.91% | −$0.92 |
| 21:00 | 78 | −$106.06 | 29.49% | −$1.36 |
| 23:00 | 1 | +$2.67 | 100.00% | +$2.67 |

## H. Entry/hold/exit/profit/drawdown/gross-loss — 75% OVERFIT teacher program (NOT yet scored)
- Realized current hold seconds: p10 **15.76**, median **99.34**, p90 **211.23**, p99 **241.72**. Current desk planned expiry 180–240 seconds; observed holds depend on exit reasons and tick chronology.
- Observed realized net mean per trade: −$0.78; gross loss per trade −$1.68; monthly quote-equity DD +$1,099.92 (a different risk dimension than an individual trade MAE).
- **Missing for 75% objective:** explicit original R9 OVERFIT event universe, matched entry/hold/exit targets with time/price normalization, matched post-entry MAE/MFE paths, and a prespecified definition of “75% of preferred per-trade performance” for metrics where lower is better (drawdown/gross loss). No OVERFIT labels were joined to these V1 trades; therefore attainment is UNMEASURED, not 0% or passed.
- Build offline teacher matching only AFTER settling both event populations, retaining nonmatched rows. Runtime may use only entry-time information, not optimal future exits, best trade outcome or oracle direction.

## I. Complete UTC daily close-time settled performance (including zero-trade dates)
| UTC day | Closes | Net USD | Gross loss USD | PF | Win % | Quote-equity DD USD | Quality passes | Funded requests |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-02-01 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-02-02 | 4 | −$9.62 | −$9.71 | 0.01 | 25.00% | 10.61 | 1,159 | 12 |
| 2026-02-03 | 28 | −$21.44 | −$54.23 | 0.60 | 35.71% | 28.86 | 441 | 41 |
| 2026-02-04 | 96 | −$57.73 | −$167.73 | 0.66 | 43.75% | 73.39 | 4,367 | 226 |
| 2026-02-05 | 46 | +$31.89 | −$62.98 | 1.51 | 52.17% | 25.04 | 3,981 | 106 |
| 2026-02-06 | 113 | −$101.23 | −$211.01 | 0.52 | 31.86% | 105.77 | 2,087 | 181 |
| 2026-02-07 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-02-08 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-02-09 | 89 | −$57.53 | −$150.09 | 0.62 | 34.83% | 68.56 | 1,249 | 122 |
| 2026-02-10 | 49 | −$73.95 | −$104.27 | 0.29 | 24.49% | 74.87 | 3,129 | 161 |
| 2026-02-11 | 98 | −$103.50 | −$174.58 | 0.41 | 28.57% | 112.43 | 3,140 | 189 |
| 2026-02-12 | 10 | −$7.41 | −$18.82 | 0.61 | 40.00% | 19.28 | 936 | 35 |
| 2026-02-13 | 42 | −$0.03 | −$67.92 | 1.00 | 45.24% | 19.33 | 2,971 | 226 |
| 2026-02-14 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-02-15 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-02-16 | 48 | −$33.05 | −$70.70 | 0.53 | 35.42% | 35.79 | 1,430 | 95 |
| 2026-02-17 | 11 | −$12.46 | −$23.15 | 0.46 | 27.27% | 19.00 | 2,132 | 97 |
| 2026-02-18 | 147 | −$49.74 | −$198.18 | 0.75 | 38.78% | 68.71 | 1,459 | 188 |
| 2026-02-19 | 60 | −$58.80 | −$98.36 | 0.40 | 30.00% | 67.74 | 1,561 | 165 |
| 2026-02-20 | 48 | −$43.49 | −$78.06 | 0.44 | 35.42% | 60.41 | 2,081 | 150 |
| 2026-02-21 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-02-22 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-02-23 | 160 | −$131.32 | −$258.20 | 0.49 | 37.50% | 149.30 | 2,431 | 267 |
| 2026-02-24 | 114 | −$118.36 | −$189.62 | 0.38 | 32.46% | 118.59 | 2,493 | 187 |
| 2026-02-25 | 35 | −$31.16 | −$61.91 | 0.50 | 34.29% | 50.61 | 1,162 | 49 |
| 2026-02-26 | 139 | −$171.63 | −$250.70 | 0.32 | 31.65% | 173.63 | 2,867 | 207 |
| 2026-02-27 | 47 | −$32.08 | −$72.23 | 0.56 | 36.17% | 48.51 | 3,227 | 263 |
| 2026-02-28 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |

## J. Complete UTC ISO-week closed-trade performance (month-scoped ISO week segments)
| UTC ISO week | Closes | Net USD | Gross loss USD | PF | Win % | Quote-equity DD USD |
|---|---:|---:|---:|---:|---:|---:|
| 2026-W05 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 |
| 2026-W06 | 287 | −$158.13 | −$505.67 | 0.69 | 39.37% | 163.66 |
| 2026-W07 | 288 | −$242.43 | −$515.68 | 0.53 | 32.64% | 260.07 |
| 2026-W08 | 314 | −$197.54 | −$468.45 | 0.58 | 35.67% | 209.38 |
| 2026-W09 | 495 | −$484.55 | −$832.67 | 0.42 | 34.34% | 515.27 |

## K. Month-specific root-cause hypothesis / missing original behavior
1. **SOURCE-EXACT OWNER MECHANISM:** February: 36,223 spread rejections vs only 1,384 closes; cost/spread eligibility and timing demand counterfactual audit on the *same rejected eligible signals*, not guessed tighter spread or lowered guard.
2. **GATE EVIDENCE:** High spread friction during this month is a strong *observed candidate-gating cause*, with spread denials exceeding some other months.
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
- Local source: `GRID0269_SEVEN_MONTH_FULL_TICK/2026-02/month_full_qa.json`, `/all_completed_shadow_trades.csv`, `/daily_performance.csv`, `/weekly_performance.csv`, `/run_config.json`.
- No new full-tick strategy replay was performed for this forensic diagnostic; numeric breakdown is rederived from 57.5m-tick completed GRID0269 original execution ledgers and exact current implementation source.
- Full-tick replay market P&L is modeled quote/cash economics, not Coinexx broker fill certification; end-of-month positions all closed, month transitions independently reset; metrics do not by themselves validate 100% R9 SYNTH or 75% R9 OVERFIT.
- This report is a research workpaper for the developer, not the governing law. Frozen owner instructions, archived successful source and original primary data outrank this diagnosis. Original GRID0258 ledger, J0183 official cursor, and August seal remain unchanged.
