# GRID0270 emergency source-exact analysis: 2026-06

> **Engineering forensic workpaper — NOT owner governance, NOT a promoted strategy, NOT live MT5 performance.** Original owner whitepaper, ratified full conversation, source code and chronological ledgers remain controlling. No March/April hindsight whitelist may be deployed.

## A. Provenance and comparison contract
- GRID0269 original Dukascopy input `XAUUSD_DUKAS_2026_06_ticks.csv(3).gz`; SHA256 `34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2`; **8,201,406 complete original Bid/Ask ticks**.
- Exact tested profile: `{"broker_session_confirmed": false, "commission_per_roundtrip_usd": 0.2, "contract_oz": 100.0, "global_max_open": 2, "latency_ms": 250, "leverage": 500, "lot": 0.01, "margin_reserve_fraction": 0.35, "require_all_htf": true, "starting_cash": 100000.0}`. Fresh $100,000 hypothetical account every month; fixed 0.01 lot; no Coinexx confirmed deals. No AUG ticks.
- All daily and ISO-week cash are attributed to **UTC exit time**. Week segments reset at month boundaries, not a single contiguous multi-month equity book.
- R9 SYNTH is the **ideal day/week/month ACCOUNT benchmark**; R9 OVERFIT is the *offline per-trade* preferred entry/hold/exit/profit/floating-DD/gross-loss teacher. Neither is an executable signal.
- Prior original mechanics: Original June accepted causal cross-month candidate needs direct original archive retrieval; current repo has no june_2026 original accepted monthly directory. Cannot assert June mechanism absent merely from directory list.

## B. Monthly performance: realized and risk
- Realized **−$3,356.50**, gross winners +$3,201.22, gross losers −$6,557.72; cash +$96,643.50 from $100,000; cash/closed-trade ledger residuals 0.0 / 1.1564225133042783e-09.
- **4,240** shadow closes, 33.82% win, PF 0.4882, average net/trade **−$0.79**, max tick-marked quote-equity DD **+$3,360.69**, max concurrent positions 2, end open 0.
- Calendar day positives 0, negatives 22; UTC week-segment positives 0, negatives 5.

## C. R9 SYNTH 100% comparison — NOT YET NUMERICALLY JOINED
- The original GRID0186 **already reconstructed** full hour/day/week/month reference tables are known to exist in its preserved archive. Their exact month-matched reference rows have not been loaded into THIS forensic workpaper. **No target number or percent completion has been invented for this month.**
- Required action is reference-table reuse, *not* re-auditing reports or recreating validated Dukascopy tick candles. Apply verified UTC mapping to period keys only.

## D. Exit-root economics, not merely headline P&L
| Exit reason | Trades | Net | Gross win | Gross loss | Avg/trade | Share |
|---|---:|---:|---:|---:|---:|---:|
| `L6_INVALIDATION` | 1,933 | −$5,718.05 | $0.00 | −$5,718.05 | −$2.96 | 45.59% |
| `L7_TIME_EXPIRY` | 1,296 | −$61.77 | +$748.89 | −$810.65 | −$0.05 | 30.57% |
| `L7_TRAILING_OR_HARD_STOP` | 470 | +$216.65 | +$245.67 | −$29.02 | +$0.46 | 11.08% |
| `L3_TARGET` | 541 | +$2,206.67 | +$2,206.67 | $0.00 | +$4.08 | 12.76% |
**Observed:** L6 invalidation alone caused **−$5,718.05 across 1,933 exits**, a major negative contribution. This proves the account loss is concentrated by exit label; it does **not** prove widening stops would improve causal profitability. Prior entry/adverse-path features and alternative holds require paired same-entry tick-path tests before changing policy.

## E. Session and direction contributions
| Session | Closes | Net | Win rate | Profit factor | Avg/trade |
|---|---:|---:|---:|---:|---:|
| LONDON | 1,775 | −$1,482.48 | 32.85% | 0.469 | −$0.84 |
| NEW_YORK | 1,797 | −$1,313.17 | 35.17% | 0.530 | −$0.73 |
| SYDNEY | 382 | −$381.89 | 30.37% | 0.365 | −$1.00 |
| TOKYO | 286 | −$178.96 | 35.66% | 0.520 | −$0.63 |

| Side | Trades | Net | Win | Per-trade net |
|---|---:|---:|---:|---:|
| SELL | 2,157 | −$1,536.92 | 35.37% | −$0.71 |
| BUY | 2,083 | −$1,819.58 | 32.17% | −$0.87 |

## F. Exact vertical-funnel diagnostics (COUNTER EMISSIONS, not unique ticket counts)
| Stage/counter | Value | Interpretation |
|---|---:|---|
| `prel1_creator_grid_raw` | 459,984 | L0 virtual price-event emissions |
| `l2_opportunity_windows` | 2,620,208 | L2 qualifying windows (can be repeated ticks) |
| `l3_no_creator_grid_crossing` | 2,535,016 | L2 permitted but G0 event not available |
| `l3_proposals` | 74,059 | Source + structure qualified L3 proposals |
| `qualified_quality_chain` | 52,808 | L1–L6 quality passes |
| `l7_spread_denied` | 13,163 | L7 observed original-spread denial |
| `l7_prequeue_global_capacity_denied` | 31,662 | L7 blocked at 2-position global cap |
| `l7_prequeue_desk_capacity_denied` | 2,657 | L7 blocked by per-desk cap |
| `l7_risk_eligible_requests` | 5,326 | L7 submitted queue requests |
| `expired_latency` | 38 | Stale pending after 250ms latency |
| `spread_drift` | 1,043 | Later quote spread drift |
| `filled` | 4,240 | Hypothetical quote fills |
| `l4_simulated_positive_close_NOT_PAID` | 20,194 | Prior positive shadow close logged, not paid renewal |
| `l4_broker_paid_parent_context` | 0 | Actual broker paid parent context |
| `l6_warning` | 2,595 | Position warning occurrences |
| `l6_bounded_recovery_watch` | 1,365 | Intent to reassess after invalidation |
| `l6_state_confirmed_recovery_candidate` | 0 | Reentry candidates completing L6 recovery logic |
| `l7_capital_halt` | 0 | Simulated risk halt |
- **Source proposal ID preserved on 8/4,240 closes (0.19%); 4,232 shadow closes have no numeric source ID.** The current `Opportunity` source string and G0 adapter are not the same as verified/earned parent→child identity. Missing optional IDs are an integration diagnostic, not proof of fabricated trades.
- Execution rate: 8.03% of *quality-pass event count* becomes a close; this is an approximate FUNNEL COUNTER ratio, not a unique-eligible-opportunity probability.
- **Current shadow execution cannot earn genuine paid parent close credit:** `V1BrokerEvidencePort` requires independently observed broker DEAL_ADD. For Python research, a separately labeled hypothetical funded/settled ledger needs to drive the causally modeled renewal experiment, while retaining the strict broker-only accounting boundary. This is a missing testable research path, NOT permission to fabricate broker deals.
- Simultaneous capacity 2 compared with original historical March/April frontiers often requiring hundreds of positions is a structural mismatch. **Do not blindly raise cap**: current negative expectancy would likely multiply losses. First reproduce causal positive source and cost model, then test graduated heat-limited capacity.

## G. Entry-hour attribution — UTC (close cash attributed back to entry cohort for diagnostic only)
| Entry UTC hour | Trades | Entry cohort net | Win rate | Avg/trade |
|---|---:|---:|---:|---:|
| 00:00 | 26 | −$9.96 | 46.15% | −$0.38 |
| 01:00 | 85 | −$88.38 | 30.59% | −$1.04 |
| 02:00 | 105 | −$115.54 | 28.57% | −$1.10 |
| 03:00 | 80 | −$81.92 | 30.00% | −$1.02 |
| 04:00 | 71 | −$63.37 | 30.99% | −$0.89 |
| 05:00 | 72 | −$72.51 | 29.17% | −$1.01 |
| 06:00 | 104 | −$30.53 | 41.35% | −$0.29 |
| 07:00 | 300 | −$264.71 | 32.67% | −$0.88 |
| 08:00 | 203 | −$177.04 | 31.03% | −$0.87 |
| 09:00 | 199 | −$172.39 | 32.16% | −$0.87 |
| 10:00 | 201 | −$149.23 | 32.84% | −$0.74 |
| 11:00 | 150 | −$92.96 | 34.67% | −$0.62 |
| 12:00 | 406 | −$247.00 | 37.93% | −$0.61 |
| 13:00 | 491 | −$480.04 | 32.38% | −$0.98 |
| 14:00 | 413 | −$366.56 | 34.38% | −$0.89 |
| 15:00 | 372 | −$261.19 | 34.95% | −$0.70 |
| 16:00 | 233 | −$128.86 | 35.19% | −$0.55 |
| 17:00 | 220 | −$208.67 | 30.91% | −$0.95 |
| 18:00 | 215 | −$134.24 | 35.35% | −$0.62 |
| 19:00 | 184 | −$91.72 | 40.22% | −$0.50 |
| 20:00 | 94 | −$100.03 | 24.47% | −$1.06 |
| 22:00 | 10 | −$7.96 | 30.00% | −$0.80 |
| 23:00 | 6 | −$11.68 | 16.67% | −$1.95 |

## H. Entry/hold/exit/profit/drawdown/gross-loss — 75% OVERFIT teacher program (NOT yet scored)
- Realized current hold seconds: p10 **21.62**, median **121.61**, p90 **240.09**, p99 **241.68**. Current desk planned expiry 180–240 seconds; observed holds depend on exit reasons and tick chronology.
- Observed realized net mean per trade: −$0.79; gross loss per trade −$1.55; monthly quote-equity DD +$3,360.69 (a different risk dimension than an individual trade MAE).
- **Missing for 75% objective:** explicit original R9 OVERFIT event universe, matched entry/hold/exit targets with time/price normalization, matched post-entry MAE/MFE paths, and a prespecified definition of “75% of preferred per-trade performance” for metrics where lower is better (drawdown/gross loss). No OVERFIT labels were joined to these V1 trades; therefore attainment is UNMEASURED, not 0% or passed.
- Build offline teacher matching only AFTER settling both event populations, retaining nonmatched rows. Runtime may use only entry-time information, not optimal future exits, best trade outcome or oracle direction.

## I. Complete UTC daily close-time settled performance (including zero-trade dates)
| UTC day | Closes | Net USD | Gross loss USD | PF | Win % | Quote-equity DD USD | Quality passes | Funded requests |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-06-01 | 77 | −$58.08 | −$106.35 | 0.45 | 32.47% | 64.40 | 842 | 83 |
| 2026-06-02 | 85 | −$55.59 | −$108.91 | 0.49 | 32.94% | 62.67 | 548 | 88 |
| 2026-06-03 | 247 | −$201.93 | −$370.14 | 0.45 | 34.41% | 214.88 | 2,815 | 294 |
| 2026-06-04 | 210 | −$209.12 | −$330.60 | 0.37 | 31.43% | 213.17 | 2,591 | 246 |
| 2026-06-05 | 222 | −$97.80 | −$291.85 | 0.66 | 41.44% | 120.50 | 2,416 | 234 |
| 2026-06-06 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-06-07 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-06-08 | 280 | −$100.98 | −$384.30 | 0.74 | 40.71% | 106.42 | 3,275 | 352 |
| 2026-06-09 | 231 | −$188.40 | −$361.97 | 0.48 | 32.90% | 190.42 | 3,011 | 294 |
| 2026-06-10 | 194 | −$102.42 | −$326.66 | 0.69 | 39.18% | 146.63 | 2,649 | 246 |
| 2026-06-11 | 239 | −$176.83 | −$389.97 | 0.55 | 35.15% | 188.85 | 3,047 | 262 |
| 2026-06-12 | 311 | −$159.63 | −$481.13 | 0.67 | 39.55% | 177.17 | 3,610 | 353 |
| 2026-06-13 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-06-14 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-06-15 | 123 | −$90.59 | −$194.08 | 0.53 | 31.71% | 100.81 | 2,251 | 168 |
| 2026-06-16 | 164 | −$168.63 | −$238.64 | 0.29 | 26.83% | 175.83 | 1,993 | 203 |
| 2026-06-17 | 199 | −$169.93 | −$268.99 | 0.37 | 25.63% | 171.94 | 1,764 | 214 |
| 2026-06-18 | 185 | −$141.49 | −$293.08 | 0.52 | 38.38% | 152.99 | 2,172 | 198 |
| 2026-06-19 | 113 | −$105.74 | −$183.05 | 0.42 | 31.86% | 115.12 | 1,236 | 124 |
| 2026-06-20 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-06-21 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-06-22 | 241 | −$224.51 | −$361.18 | 0.38 | 29.46% | 232.09 | 2,797 | 296 |
| 2026-06-23 | 190 | −$183.89 | −$317.19 | 0.42 | 31.58% | 202.41 | 2,791 | 292 |
| 2026-06-24 | 255 | −$291.12 | −$475.58 | 0.39 | 31.76% | 292.07 | 3,113 | 331 |
| 2026-06-25 | 252 | −$219.41 | −$427.33 | 0.49 | 34.13% | 230.49 | 2,930 | 325 |
| 2026-06-26 | 183 | −$175.28 | −$291.48 | 0.40 | 30.05% | 182.67 | 2,930 | 266 |
| 2026-06-27 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-06-28 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-06-29 | 175 | −$141.65 | −$240.76 | 0.41 | 31.43% | 146.63 | 2,825 | 298 |
| 2026-06-30 | 64 | −$93.48 | −$114.49 | 0.18 | 23.44% | 96.64 | 1,202 | 159 |

## J. Complete UTC ISO-week closed-trade performance (month-scoped ISO week segments)
| UTC ISO week | Closes | Net USD | Gross loss USD | PF | Win % | Quote-equity DD USD |
|---|---:|---:|---:|---:|---:|---:|
| 2026-W23 | 841 | −$622.52 | −$1,207.85 | 0.48 | 35.20% | 632.64 |
| 2026-W24 | 1,255 | −$728.27 | −$1,944.03 | 0.63 | 37.69% | 735.70 |
| 2026-W25 | 784 | −$676.38 | −$1,177.84 | 0.43 | 30.74% | 679.84 |
| 2026-W26 | 1,121 | −$1,094.21 | −$1,872.76 | 0.42 | 31.49% | 1,104.30 |
| 2026-W27 | 239 | −$235.13 | −$355.25 | 0.34 | 29.29% | 243.23 |

## K. Month-specific root-cause hypothesis / missing original behavior
1. **SOURCE-EXACT OWNER MECHANISM:** June: greatest monthly count and gross loss of seven-month V1 trial; L6 negative concentration dominates. Out-of-month original source must be recovered, and first restore causal signed positive trade expectancy before relaxing position throughput.
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
- Local source: `GRID0269_SEVEN_MONTH_FULL_TICK/2026-06/month_full_qa.json`, `/all_completed_shadow_trades.csv`, `/daily_performance.csv`, `/weekly_performance.csv`, `/run_config.json`.
- No new full-tick strategy replay was performed for this forensic diagnostic; numeric breakdown is rederived from 57.5m-tick completed GRID0269 original execution ledgers and exact current implementation source.
- Full-tick replay market P&L is modeled quote/cash economics, not Coinexx broker fill certification; end-of-month positions all closed, month transitions independently reset; metrics do not by themselves validate 100% R9 SYNTH or 75% R9 OVERFIT.
- This report is a research workpaper for the developer, not the governing law. Frozen owner instructions, archived successful source and original primary data outrank this diagnosis. Original GRID0258 ledger, J0183 official cursor, and August seal remain unchanged.
