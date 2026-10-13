# GRID0270 emergency source-exact analysis: 2026-01

> **Engineering forensic workpaper — NOT owner governance, NOT a promoted strategy, NOT live MT5 performance.** Original owner whitepaper, ratified full conversation, source code and chronological ledgers remain controlling. No March/April hindsight whitelist may be deployed.

## A. Provenance and comparison contract
- GRID0269 original Dukascopy input `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`; SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`; **9,135,062 complete original Bid/Ask ticks**.
- Exact tested profile: `{"broker_session_confirmed": false, "commission_per_roundtrip_usd": 0.2, "contract_oz": 100.0, "global_max_open": 2, "latency_ms": 250, "leverage": 500, "lot": 0.01, "margin_reserve_fraction": 0.35, "require_all_htf": true, "starting_cash": 100000.0}`. Fresh $100,000 hypothetical account every month; fixed 0.01 lot; no Coinexx confirmed deals. No AUG ticks.
- All daily and ISO-week cash are attributed to **UTC exit time**. Week segments reset at month boundaries, not a single contiguous multi-month equity book.
- R9 SYNTH is the **ideal day/week/month ACCOUNT benchmark**; R9 OVERFIT is the *offline per-trade* preferred entry/hold/exit/profit/floating-DD/gross-loss teacher. Neither is an executable signal.
- Prior original mechanics: Whitepaper §5 original January balanced approximately +$194.4k, aggressive approximately +$203.5k; original code/config not recovered in this diagnostic. Do not import deleted derived Jan/Feb artifacts.

## B. Monthly performance: realized and risk
- Realized **−$3,015.32**, gross winners +$2,118.41, gross losers −$5,133.73; cash +$96,984.68 from $100,000; cash/closed-trade ledger residuals 0.0 / 1.4397301129065454e-09.
- **3,258** shadow closes, 33.30% win, PF 0.4126, average net/trade **−$0.93**, max tick-marked quote-equity DD **+$3,030.15**, max concurrent positions 2, end open 0.
- Calendar day positives 0, negatives 21; UTC week-segment positives 0, negatives 5.

## C. R9 SYNTH 100% comparison — NOT YET NUMERICALLY JOINED
- The original GRID0186 **already reconstructed** full hour/day/week/month reference tables are known to exist in its preserved archive. Their exact month-matched reference rows have not been loaded into THIS forensic workpaper. **No target number or percent completion has been invented for this month.**
- Required action is reference-table reuse, *not* re-auditing reports or recreating validated Dukascopy tick candles. Apply verified UTC mapping to period keys only.

## D. Exit-root economics, not merely headline P&L
| Exit reason | Trades | Net | Gross win | Gross loss | Avg/trade | Share |
|---|---:|---:|---:|---:|---:|---:|
| `L6_INVALIDATION` | 1,463 | −$4,437.14 | $0.00 | −$4,437.14 | −$3.03 | 44.90% |
| `L7_TIME_EXPIRY` | 1,076 | −$124.63 | +$546.60 | −$671.23 | −$0.12 | 33.03% |
| `L7_TRAILING_OR_HARD_STOP` | 390 | +$187.81 | +$213.17 | −$25.35 | +$0.48 | 11.97% |
| `L3_TARGET` | 329 | +$1,358.64 | +$1,358.64 | $0.00 | +$4.13 | 10.10% |
**Observed:** L6 invalidation alone caused **−$4,437.14 across 1,463 exits**, a major negative contribution. This proves the account loss is concentrated by exit label; it does **not** prove widening stops would improve causal profitability. Prior entry/adverse-path features and alternative holds require paired same-entry tick-path tests before changing policy.

## E. Session and direction contributions
| Session | Closes | Net | Win rate | Profit factor | Avg/trade |
|---|---:|---:|---:|---:|---:|
| LONDON | 1,430 | −$1,397.71 | 30.63% | 0.385 | −$0.98 |
| NEW_YORK | 1,470 | −$1,346.31 | 35.78% | 0.434 | −$0.92 |
| SYDNEY | 181 | −$141.31 | 32.60% | 0.432 | −$0.78 |
| TOKYO | 177 | −$129.99 | 33.90% | 0.448 | −$0.73 |

| Side | Trades | Net | Win | Per-trade net |
|---|---:|---:|---:|---:|
| BUY | 1,670 | −$1,557.07 | 33.41% | −$0.93 |
| SELL | 1,588 | −$1,458.25 | 33.06% | −$0.92 |

## F. Exact vertical-funnel diagnostics (COUNTER EMISSIONS, not unique ticket counts)
| Stage/counter | Value | Interpretation |
|---|---:|---|
| `prel1_creator_grid_raw` | 456,468 | L0 virtual price-event emissions |
| `l2_opportunity_windows` | 2,599,027 | L2 qualifying windows (can be repeated ticks) |
| `l3_no_creator_grid_crossing` | 2,521,871 | L2 permitted but G0 event not available |
| `l3_proposals` | 68,615 | Source + structure qualified L3 proposals |
| `qualified_quality_chain` | 46,056 | L1–L6 quality passes |
| `l7_spread_denied` | 19,657 | L7 observed original-spread denial |
| `l7_prequeue_global_capacity_denied` | 20,857 | L7 blocked at 2-position global cap |
| `l7_prequeue_desk_capacity_denied` | 1,207 | L7 blocked by per-desk cap |
| `l7_risk_eligible_requests` | 4,335 | L7 submitted queue requests |
| `expired_latency` | 53 | Stale pending after 250ms latency |
| `spread_drift` | 1,013 | Later quote spread drift |
| `filled` | 3,258 | Hypothetical quote fills |
| `l4_simulated_positive_close_NOT_PAID` | 22,331 | Prior positive shadow close logged, not paid renewal |
| `l4_broker_paid_parent_context` | 0 | Actual broker paid parent context |
| `l6_warning` | 1,970 | Position warning occurrences |
| `l6_bounded_recovery_watch` | 1,006 | Intent to reassess after invalidation |
| `l6_state_confirmed_recovery_candidate` | 2 | Reentry candidates completing L6 recovery logic |
| `l7_capital_halt` | 0 | Simulated risk halt |
- **Source proposal ID preserved on 13/3,258 closes (0.40%); 3,245 shadow closes have no numeric source ID.** The current `Opportunity` source string and G0 adapter are not the same as verified/earned parent→child identity. Missing optional IDs are an integration diagnostic, not proof of fabricated trades.
- Execution rate: 7.07% of *quality-pass event count* becomes a close; this is an approximate FUNNEL COUNTER ratio, not a unique-eligible-opportunity probability.
- **Current shadow execution cannot earn genuine paid parent close credit:** `V1BrokerEvidencePort` requires independently observed broker DEAL_ADD. For Python research, a separately labeled hypothetical funded/settled ledger needs to drive the causally modeled renewal experiment, while retaining the strict broker-only accounting boundary. This is a missing testable research path, NOT permission to fabricate broker deals.
- Simultaneous capacity 2 compared with original historical March/April frontiers often requiring hundreds of positions is a structural mismatch. **Do not blindly raise cap**: current negative expectancy would likely multiply losses. First reproduce causal positive source and cost model, then test graduated heat-limited capacity.

## G. Entry-hour attribution — UTC (close cash attributed back to entry cohort for diagnostic only)
| Entry UTC hour | Trades | Entry cohort net | Win rate | Avg/trade |
|---|---:|---:|---:|---:|
| 00:00 | 45 | −$42.33 | 28.89% | −$0.94 |
| 01:00 | 40 | −$39.95 | 30.00% | −$1.00 |
| 02:00 | 46 | −$46.37 | 23.91% | −$1.01 |
| 03:00 | 41 | −$42.97 | 29.27% | −$1.05 |
| 04:00 | 49 | −$34.28 | 34.69% | −$0.70 |
| 05:00 | 45 | −$48.89 | 24.44% | −$1.09 |
| 06:00 | 26 | −$10.99 | 50.00% | −$0.42 |
| 07:00 | 17 | −$5.44 | 47.06% | −$0.32 |
| 08:00 | 162 | −$149.25 | 30.25% | −$0.92 |
| 09:00 | 178 | −$144.33 | 32.58% | −$0.81 |
| 10:00 | 193 | −$235.84 | 26.42% | −$1.22 |
| 11:00 | 147 | −$140.72 | 29.93% | −$0.96 |
| 12:00 | 175 | −$167.82 | 29.14% | −$0.96 |
| 13:00 | 280 | −$298.30 | 35.36% | −$1.07 |
| 14:00 | 394 | −$362.17 | 34.52% | −$0.92 |
| 15:00 | 279 | −$265.00 | 35.84% | −$0.95 |
| 16:00 | 269 | −$266.35 | 32.71% | −$0.99 |
| 17:00 | 234 | −$164.16 | 35.47% | −$0.70 |
| 18:00 | 171 | −$156.51 | 39.77% | −$0.92 |
| 19:00 | 195 | −$151.96 | 33.85% | −$0.78 |
| 20:00 | 139 | −$164.01 | 31.65% | −$1.18 |
| 21:00 | 128 | −$80.25 | 36.72% | −$0.63 |
| 23:00 | 5 | +$2.57 | 40.00% | +$0.51 |

## H. Entry/hold/exit/profit/drawdown/gross-loss — 75% OVERFIT teacher program (NOT yet scored)
- Realized current hold seconds: p10 **19.26**, median **120.67**, p90 **240.17**, p99 **242.29**. Current desk planned expiry 180–240 seconds; observed holds depend on exit reasons and tick chronology.
- Observed realized net mean per trade: −$0.93; gross loss per trade −$1.58; monthly quote-equity DD +$3,030.15 (a different risk dimension than an individual trade MAE).
- **Missing for 75% objective:** explicit original R9 OVERFIT event universe, matched entry/hold/exit targets with time/price normalization, matched post-entry MAE/MFE paths, and a prespecified definition of “75% of preferred per-trade performance” for metrics where lower is better (drawdown/gross loss). No OVERFIT labels were joined to these V1 trades; therefore attainment is UNMEASURED, not 0% or passed.
- Build offline teacher matching only AFTER settling both event populations, retaining nonmatched rows. Runtime may use only entry-time information, not optimal future exits, best trade outcome or oracle direction.

## I. Complete UTC daily close-time settled performance (including zero-trade dates)
| UTC day | Closes | Net USD | Gross loss USD | PF | Win % | Quote-equity DD USD | Quality passes | Funded requests |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-01-01 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-01-02 | 31 | −$16.89 | −$35.56 | 0.53 | 32.26% | 29.76 | 528 | 32 |
| 2026-01-03 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-01-04 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-01-05 | 74 | −$93.50 | −$112.34 | 0.17 | 29.73% | 96.04 | 711 | 80 |
| 2026-01-06 | 90 | −$79.66 | −$122.66 | 0.35 | 36.67% | 85.68 | 2,712 | 211 |
| 2026-01-07 | 141 | −$104.47 | −$209.65 | 0.50 | 34.75% | 114.65 | 1,693 | 156 |
| 2026-01-08 | 165 | −$135.49 | −$247.66 | 0.45 | 34.55% | 146.79 | 2,359 | 211 |
| 2026-01-09 | 136 | −$100.22 | −$206.76 | 0.52 | 36.03% | 100.68 | 2,152 | 239 |
| 2026-01-10 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-01-11 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-01-12 | 200 | −$197.10 | −$305.83 | 0.36 | 34.50% | 197.46 | 2,450 | 250 |
| 2026-01-13 | 121 | −$67.67 | −$167.94 | 0.60 | 37.19% | 76.39 | 2,749 | 244 |
| 2026-01-14 | 245 | −$222.66 | −$388.24 | 0.43 | 33.88% | 231.04 | 2,646 | 256 |
| 2026-01-15 | 111 | −$113.46 | −$162.43 | 0.30 | 32.43% | 113.58 | 1,074 | 142 |
| 2026-01-16 | 198 | −$237.92 | −$315.05 | 0.24 | 25.76% | 238.93 | 1,900 | 238 |
| 2026-01-17 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-01-18 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-01-19 | 136 | −$120.82 | −$164.34 | 0.26 | 29.41% | 123.42 | 1,096 | 158 |
| 2026-01-20 | 177 | −$191.93 | −$274.69 | 0.30 | 27.12% | 194.26 | 2,115 | 241 |
| 2026-01-21 | 259 | −$303.15 | −$476.56 | 0.36 | 33.98% | 303.63 | 2,936 | 323 |
| 2026-01-22 | 112 | −$42.72 | −$119.19 | 0.64 | 44.64% | 59.92 | 1,583 | 139 |
| 2026-01-23 | 216 | −$152.55 | −$316.14 | 0.52 | 36.11% | 153.67 | 2,625 | 281 |
| 2026-01-24 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-01-25 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-01-26 | 203 | −$118.19 | −$312.33 | 0.62 | 35.47% | 119.97 | 2,173 | 211 |
| 2026-01-27 | 250 | −$277.79 | −$440.27 | 0.37 | 32.00% | 294.49 | 2,883 | 299 |
| 2026-01-28 | 256 | −$278.45 | −$482.60 | 0.42 | 30.47% | 293.57 | 2,920 | 345 |
| 2026-01-29 | 128 | −$155.15 | −$258.08 | 0.40 | 32.03% | 156.19 | 3,288 | 218 |
| 2026-01-30 | 9 | −$5.53 | −$15.42 | 0.64 | 44.44% | 17.73 | 3,463 | 61 |
| 2026-01-31 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |

## J. Complete UTC ISO-week closed-trade performance (month-scoped ISO week segments)
| UTC ISO week | Closes | Net USD | Gross loss USD | PF | Win % | Quote-equity DD USD |
|---|---:|---:|---:|---:|---:|---:|
| 2026-W01 | 31 | −$16.89 | −$35.56 | 0.53 | 32.26% | 29.76 |
| 2026-W02 | 606 | −$513.34 | −$899.07 | 0.43 | 34.65% | 513.99 |
| 2026-W03 | 875 | −$838.81 | −$1,339.48 | 0.37 | 32.46% | 839.32 |
| 2026-W04 | 900 | −$811.17 | −$1,350.92 | 0.40 | 33.78% | 812.29 |
| 2026-W05 | 846 | −$835.11 | −$1,508.69 | 0.45 | 32.51% | 845.81 |

## K. Month-specific root-cause hypothesis / missing original behavior
1. **SOURCE-EXACT OWNER MECHANISM:** January: original whitepaper January Watchdog and asymmetric session ownership source must be read/reused; current shadow paid-chain is not equivalent and current loss invalidations dominate. Do not mistake 2-slot stress replay for reproduction of original January discovery.
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
- Local source: `GRID0269_SEVEN_MONTH_FULL_TICK/2026-01/month_full_qa.json`, `/all_completed_shadow_trades.csv`, `/daily_performance.csv`, `/weekly_performance.csv`, `/run_config.json`.
- No new full-tick strategy replay was performed for this forensic diagnostic; numeric breakdown is rederived from 57.5m-tick completed GRID0269 original execution ledgers and exact current implementation source.
- Full-tick replay market P&L is modeled quote/cash economics, not Coinexx broker fill certification; end-of-month positions all closed, month transitions independently reset; metrics do not by themselves validate 100% R9 SYNTH or 75% R9 OVERFIT.
- This report is a research workpaper for the developer, not the governing law. Frozen owner instructions, archived successful source and original primary data outrank this diagnosis. Original GRID0258 ledger, J0183 official cursor, and August seal remain unchanged.
