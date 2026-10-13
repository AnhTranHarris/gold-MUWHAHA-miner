# GRID0270 emergency source-exact analysis: 2026-05

> **Engineering forensic workpaper — NOT owner governance, NOT a promoted strategy, NOT live MT5 performance.** Original owner whitepaper, ratified full conversation, source code and chronological ledgers remain controlling. No March/April hindsight whitelist may be deployed.

## A. Provenance and comparison contract
- GRID0269 original Dukascopy input `XAUUSD_DUKAS_2026_05_ticks.csv(3).gz`; SHA256 `3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d`; **8,333,165 complete original Bid/Ask ticks**.
- Exact tested profile: `{"broker_session_confirmed": false, "commission_per_roundtrip_usd": 0.2, "contract_oz": 100.0, "global_max_open": 2, "latency_ms": 250, "leverage": 500, "lot": 0.01, "margin_reserve_fraction": 0.35, "require_all_htf": true, "starting_cash": 100000.0}`. Fresh $100,000 hypothetical account every month; fixed 0.01 lot; no Coinexx confirmed deals. No AUG ticks.
- All daily and ISO-week cash are attributed to **UTC exit time**. Week segments reset at month boundaries, not a single contiguous multi-month equity book.
- R9 SYNTH is the **ideal day/week/month ACCOUNT benchmark**; R9 OVERFIT is the *offline per-trade* preferred entry/hold/exit/profit/floating-DD/gross-loss teacher. Neither is an executable signal.
- Prior original mechanics: Original May accepted causal cross-month candidate needs direct original archive retrieval; current repo has no may_2026 original accepted monthly directory. Cannot assert May mechanism absent merely from directory list.

## B. Monthly performance: realized and risk
- Realized **−$2,774.65**, gross winners +$2,403.71, gross losers −$5,178.36; cash +$97,225.35 from $100,000; cash/closed-trade ledger residuals 0.0 / 1.8385435396339744e-09.
- **3,504** shadow closes, 35.07% win, PF 0.4642, average net/trade **−$0.79**, max tick-marked quote-equity DD **+$2,797.47**, max concurrent positions 2, end open 0.
- Calendar day positives 0, negatives 21; UTC week-segment positives 0, negatives 5.

## C. R9 SYNTH 100% comparison — NOT YET NUMERICALLY JOINED
- The original GRID0186 **already reconstructed** full hour/day/week/month reference tables are known to exist in its preserved archive. Their exact month-matched reference rows have not been loaded into THIS forensic workpaper. **No target number or percent completion has been invented for this month.**
- Required action is reference-table reuse, *not* re-auditing reports or recreating validated Dukascopy tick candles. Apply verified UTC mapping to period keys only.

## D. Exit-root economics, not merely headline P&L
| Exit reason | Trades | Net | Gross win | Gross loss | Avg/trade | Share |
|---|---:|---:|---:|---:|---:|---:|
| `L6_INVALIDATION` | 1,510 | −$4,415.07 | $0.00 | −$4,415.07 | −$2.92 | 43.09% |
| `L7_TIME_EXPIRY` | 1,215 | −$40.59 | +$700.33 | −$740.92 | −$0.03 | 34.67% |
| `L7_TRAILING_OR_HARD_STOP` | 388 | +$164.63 | +$187.00 | −$22.37 | +$0.42 | 11.07% |
| `L3_TARGET` | 391 | +$1,516.38 | +$1,516.38 | $0.00 | +$3.88 | 11.16% |
**Observed:** L6 invalidation alone caused **−$4,415.07 across 1,510 exits**, a major negative contribution. This proves the account loss is concentrated by exit label; it does **not** prove widening stops would improve causal profitability. Prior entry/adverse-path features and alternative holds require paired same-entry tick-path tests before changing policy.

## E. Session and direction contributions
| Session | Closes | Net | Win rate | Profit factor | Avg/trade |
|---|---:|---:|---:|---:|---:|
| LONDON | 1,824 | −$1,525.00 | 34.27% | 0.461 | −$0.84 |
| NEW_YORK | 1,115 | −$844.86 | 36.50% | 0.466 | −$0.76 |
| SYDNEY | 307 | −$224.83 | 36.16% | 0.487 | −$0.73 |
| TOKYO | 258 | −$179.96 | 33.33% | 0.451 | −$0.70 |

| Side | Trades | Net | Win | Per-trade net |
|---|---:|---:|---:|---:|
| SELL | 1,926 | −$1,493.48 | 35.31% | −$0.78 |
| BUY | 1,578 | −$1,281.17 | 34.79% | −$0.81 |

## F. Exact vertical-funnel diagnostics (COUNTER EMISSIONS, not unique ticket counts)
| Stage/counter | Value | Interpretation |
|---|---:|---|
| `prel1_creator_grid_raw` | 407,778 | L0 virtual price-event emissions |
| `l2_opportunity_windows` | 2,388,351 | L2 qualifying windows (can be repeated ticks) |
| `l3_no_creator_grid_crossing` | 2,318,709 | L2 permitted but G0 event not available |
| `l3_proposals` | 61,265 | Source + structure qualified L3 proposals |
| `qualified_quality_chain` | 46,038 | L1–L6 quality passes |
| `l7_spread_denied` | 9,899 | L7 observed original-spread denial |
| `l7_prequeue_global_capacity_denied` | 29,851 | L7 blocked at 2-position global cap |
| `l7_prequeue_desk_capacity_denied` | 1,993 | L7 blocked by per-desk cap |
| `l7_risk_eligible_requests` | 4,295 | L7 submitted queue requests |
| `expired_latency` | 35 | Stale pending after 250ms latency |
| `spread_drift` | 749 | Later quote spread drift |
| `filled` | 3,504 | Hypothetical quote fills |
| `l4_simulated_positive_close_NOT_PAID` | 18,716 | Prior positive shadow close logged, not paid renewal |
| `l4_broker_paid_parent_context` | 0 | Actual broker paid parent context |
| `l6_warning` | 2,068 | Position warning occurrences |
| `l6_bounded_recovery_watch` | 1,057 | Intent to reassess after invalidation |
| `l6_state_confirmed_recovery_candidate` | 1 | Reentry candidates completing L6 recovery logic |
| `l7_capital_halt` | 0 | Simulated risk halt |
- **Source proposal ID preserved on 5/3,504 closes (0.14%); 3,499 shadow closes have no numeric source ID.** The current `Opportunity` source string and G0 adapter are not the same as verified/earned parent→child identity. Missing optional IDs are an integration diagnostic, not proof of fabricated trades.
- Execution rate: 7.61% of *quality-pass event count* becomes a close; this is an approximate FUNNEL COUNTER ratio, not a unique-eligible-opportunity probability.
- **Current shadow execution cannot earn genuine paid parent close credit:** `V1BrokerEvidencePort` requires independently observed broker DEAL_ADD. For Python research, a separately labeled hypothetical funded/settled ledger needs to drive the causally modeled renewal experiment, while retaining the strict broker-only accounting boundary. This is a missing testable research path, NOT permission to fabricate broker deals.
- Simultaneous capacity 2 compared with original historical March/April frontiers often requiring hundreds of positions is a structural mismatch. **Do not blindly raise cap**: current negative expectancy would likely multiply losses. First reproduce causal positive source and cost model, then test graduated heat-limited capacity.

## G. Entry-hour attribution — UTC (close cash attributed back to entry cohort for diagnostic only)
| Entry UTC hour | Trades | Entry cohort net | Win rate | Avg/trade |
|---|---:|---:|---:|---:|
| 00:00 | 27 | −$30.99 | 29.63% | −$1.15 |
| 01:00 | 68 | −$92.73 | 23.53% | −$1.36 |
| 02:00 | 80 | −$35.85 | 40.00% | −$0.45 |
| 03:00 | 57 | −$44.67 | 26.32% | −$0.78 |
| 04:00 | 40 | −$1.24 | 52.50% | −$0.03 |
| 05:00 | 42 | −$23.50 | 40.48% | −$0.56 |
| 06:00 | 124 | −$85.55 | 38.71% | −$0.69 |
| 07:00 | 261 | −$199.73 | 33.72% | −$0.77 |
| 08:00 | 294 | −$364.63 | 24.15% | −$1.24 |
| 09:00 | 276 | −$241.94 | 33.70% | −$0.88 |
| 10:00 | 193 | −$56.95 | 43.01% | −$0.30 |
| 11:00 | 247 | −$242.49 | 34.01% | −$0.98 |
| 12:00 | 303 | −$205.21 | 37.95% | −$0.68 |
| 13:00 | 222 | −$39.09 | 46.85% | −$0.18 |
| 14:00 | 358 | −$337.84 | 34.92% | −$0.94 |
| 15:00 | 260 | −$282.23 | 33.08% | −$1.09 |
| 16:00 | 159 | −$132.32 | 37.11% | −$0.83 |
| 17:00 | 147 | −$128.52 | 29.25% | −$0.87 |
| 18:00 | 111 | −$73.31 | 34.23% | −$0.66 |
| 19:00 | 122 | −$88.96 | 35.25% | −$0.73 |
| 20:00 | 102 | −$58.67 | 35.29% | −$0.58 |
| 22:00 | 3 | −$3.93 | 33.33% | −$1.31 |
| 23:00 | 8 | −$4.29 | 37.50% | −$0.54 |

## H. Entry/hold/exit/profit/drawdown/gross-loss — 75% OVERFIT teacher program (NOT yet scored)
- Realized current hold seconds: p10 **26.81**, median **143.22**, p90 **240.12**, p99 **241.37**. Current desk planned expiry 180–240 seconds; observed holds depend on exit reasons and tick chronology.
- Observed realized net mean per trade: −$0.79; gross loss per trade −$1.48; monthly quote-equity DD +$2,797.47 (a different risk dimension than an individual trade MAE).
- **Missing for 75% objective:** explicit original R9 OVERFIT event universe, matched entry/hold/exit targets with time/price normalization, matched post-entry MAE/MFE paths, and a prespecified definition of “75% of preferred per-trade performance” for metrics where lower is better (drawdown/gross loss). No OVERFIT labels were joined to these V1 trades; therefore attainment is UNMEASURED, not 0% or passed.
- Build offline teacher matching only AFTER settling both event populations, retaining nonmatched rows. Runtime may use only entry-time information, not optimal future exits, best trade outcome or oracle direction.

## I. Complete UTC daily close-time settled performance (including zero-trade dates)
| UTC day | Closes | Net USD | Gross loss USD | PF | Win % | Quote-equity DD USD | Quality passes | Funded requests |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-05-01 | 33 | −$26.78 | −$52.99 | 0.49 | 30.30% | 32.30 | 329 | 39 |
| 2026-05-02 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-05-03 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-05-04 | 117 | −$56.65 | −$176.23 | 0.68 | 42.73% | 67.97 | 1,268 | 119 |
| 2026-05-05 | 193 | −$181.14 | −$280.67 | 0.35 | 31.61% | 183.70 | 2,382 | 207 |
| 2026-05-06 | 156 | −$122.80 | −$236.87 | 0.48 | 38.46% | 133.48 | 2,124 | 165 |
| 2026-05-07 | 192 | −$126.52 | −$281.37 | 0.55 | 39.06% | 154.47 | 2,248 | 245 |
| 2026-05-08 | 206 | −$190.39 | −$310.91 | 0.39 | 32.04% | 193.73 | 2,713 | 227 |
| 2026-05-09 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-05-10 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-05-11 | 204 | −$212.87 | −$311.84 | 0.32 | 30.39% | 215.01 | 3,141 | 278 |
| 2026-05-12 | 223 | −$107.21 | −$333.09 | 0.68 | 40.36% | 113.16 | 2,533 | 242 |
| 2026-05-13 | 193 | −$126.97 | −$260.46 | 0.51 | 37.31% | 141.09 | 2,963 | 226 |
| 2026-05-14 | 100 | −$87.35 | −$145.40 | 0.40 | 31.00% | 89.69 | 1,150 | 132 |
| 2026-05-15 | 247 | −$188.43 | −$388.72 | 0.52 | 34.82% | 209.44 | 3,237 | 279 |
| 2026-05-16 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-05-17 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-05-18 | 225 | −$148.91 | −$314.71 | 0.53 | 39.56% | 161.98 | 3,316 | 312 |
| 2026-05-19 | 251 | −$261.75 | −$415.42 | 0.37 | 31.47% | 268.52 | 3,206 | 269 |
| 2026-05-20 | 191 | −$141.58 | −$263.00 | 0.46 | 36.13% | 142.76 | 2,272 | 242 |
| 2026-05-21 | 203 | −$156.93 | −$303.51 | 0.48 | 36.45% | 159.53 | 3,528 | 267 |
| 2026-05-22 | 59 | −$56.15 | −$80.45 | 0.30 | 22.03% | 58.90 | 674 | 83 |
| 2026-05-23 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-05-24 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-05-25 | 108 | −$105.32 | −$149.27 | 0.29 | 29.63% | 109.29 | 891 | 131 |
| 2026-05-26 | 176 | −$141.50 | −$271.02 | 0.48 | 34.66% | 147.65 | 1,968 | 210 |
| 2026-05-27 | 193 | −$147.43 | −$265.63 | 0.44 | 34.72% | 149.85 | 2,593 | 220 |
| 2026-05-28 | 110 | −$100.42 | −$158.65 | 0.37 | 30.91% | 102.64 | 1,570 | 233 |
| 2026-05-29 | 124 | −$87.54 | −$178.16 | 0.51 | 38.71% | 110.37 | 1,932 | 169 |
| 2026-05-30 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-05-31 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |

## J. Complete UTC ISO-week closed-trade performance (month-scoped ISO week segments)
| UTC ISO week | Closes | Net USD | Gross loss USD | PF | Win % | Quote-equity DD USD |
|---|---:|---:|---:|---:|---:|---:|
| 2026-W18 | 33 | −$26.78 | −$52.99 | 0.49 | 30.30% | 32.30 |
| 2026-W19 | 864 | −$677.50 | −$1,286.05 | 0.47 | 36.11% | 688.05 |
| 2026-W20 | 967 | −$722.83 | −$1,439.50 | 0.50 | 35.26% | 743.58 |
| 2026-W21 | 929 | −$765.32 | −$1,377.09 | 0.44 | 34.88% | 779.26 |
| 2026-W22 | 711 | −$582.22 | −$1,022.72 | 0.43 | 34.04% | 605.04 |

## K. Month-specific root-cause hypothesis / missing original behavior
1. **SOURCE-EXACT OWNER MECHANISM:** May: after-source original May science is not verified in this workpaper. Avoid using March-only/April-only profitable-cell selectors as May runtime switches; test genuinely portable mechanics while tracking late-session loss concentration.
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
- Local source: `GRID0269_SEVEN_MONTH_FULL_TICK/2026-05/month_full_qa.json`, `/all_completed_shadow_trades.csv`, `/daily_performance.csv`, `/weekly_performance.csv`, `/run_config.json`.
- No new full-tick strategy replay was performed for this forensic diagnostic; numeric breakdown is rederived from 57.5m-tick completed GRID0269 original execution ledgers and exact current implementation source.
- Full-tick replay market P&L is modeled quote/cash economics, not Coinexx broker fill certification; end-of-month positions all closed, month transitions independently reset; metrics do not by themselves validate 100% R9 SYNTH or 75% R9 OVERFIT.
- This report is a research workpaper for the developer, not the governing law. Frozen owner instructions, archived successful source and original primary data outrank this diagnosis. Original GRID0258 ledger, J0183 official cursor, and August seal remain unchanged.
