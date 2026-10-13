# GRID0270 emergency source-exact analysis: 2026-04

> **Engineering forensic workpaper — NOT owner governance, NOT a promoted strategy, NOT live MT5 performance.** Original owner whitepaper, ratified full conversation, source code and chronological ledgers remain controlling. No March/April hindsight whitelist may be deployed.

## A. Provenance and comparison contract
- GRID0269 original Dukascopy input `XAUUSD_DUKAS_2026_04_ticks.csv(3).gz`; SHA256 `30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f`; **7,470,570 complete original Bid/Ask ticks**.
- Exact tested profile: `{"broker_session_confirmed": false, "commission_per_roundtrip_usd": 0.2, "contract_oz": 100.0, "global_max_open": 2, "latency_ms": 250, "leverage": 500, "lot": 0.01, "margin_reserve_fraction": 0.35, "require_all_htf": true, "starting_cash": 100000.0}`. Fresh $100,000 hypothetical account every month; fixed 0.01 lot; no Coinexx confirmed deals. No AUG ticks.
- All daily and ISO-week cash are attributed to **UTC exit time**. Week segments reset at month boundaries, not a single contiguous multi-month equity book.
- R9 SYNTH is the **ideal day/week/month ACCOUNT benchmark**; R9 OVERFIT is the *offline per-trade* preferred entry/hold/exit/profit/floating-DD/gross-loss teacher. Neither is an executable signal.
- Prior original mechanics: Original April 136T2 child state = rule, renewal depth, previous child realized P/L bucket, previous child realized hold bucket, and predecessor completed before child entry; April profitable cells chosen from April outcomes, not deployable month rule. Later source J0183 has 32,902 already predecessor-linked entries over 7 overlapping rule streams.

## B. Monthly performance: realized and risk
- Realized **−$2,569.05**, gross winners +$1,734.93, gross losers −$4,303.98; cash +$97,430.95 from $100,000; cash/closed-trade ledger residuals 0.0 / 1.1932570487260818e-09.
- **2,674** shadow closes, 32.16% win, PF 0.4031, average net/trade **−$0.96**, max tick-marked quote-equity DD **+$2,572.45**, max concurrent positions 2, end open 0.
- Calendar day positives 1, negatives 20; UTC week-segment positives 0, negatives 5.

## C. Frozen R9 SYNTH monthly 100% comparison (original prior research documentation)
- Reference from original `research/delta_a_alpha/monthly/april_2026/DAA_APRIL_CAUSAL_TRANSITION_BREAKTHROUGH_136T2.md`: ideal net **+$38,353.96**, trades **31,758**, gross loss **−$2,414.22**, PF 16.8867, win 86.76%.
- Current V1 **8.42% of R9 SYNTH trade count**. Trade shortfall **29,084**; observed count needs ~**11.88×** current executed velocity *without worsening economics*.
- Current V1 net is negative, so **net-performance completion ratio is not a meaningful attainment percentage**; the required absolute change to reach the positive target is **+$40,923.01**. This is a gap, not a prediction.
- R9 day/ISO-week exact targets must be retrieved from original frozen GRID0186 **already reconstructed reference tables**, then checked against corresponding UTC windows. No repeat audit of MT5 report is required. Missing aligned clock proof must not be substituted with a guessed shift.

## D. Exit-root economics, not merely headline P&L
| Exit reason | Trades | Net | Gross win | Gross loss | Avg/trade | Share |
|---|---:|---:|---:|---:|---:|---:|
| `L6_INVALIDATION` | 1,244 | −$3,726.32 | $0.00 | −$3,726.32 | −$3.00 | 46.52% |
| `L7_TIME_EXPIRY` | 817 | −$86.53 | +$461.62 | −$548.15 | −$0.11 | 30.55% |
| `L7_TRAILING_OR_HARD_STOP` | 341 | +$143.14 | +$172.65 | −$29.51 | +$0.42 | 12.75% |
| `L3_TARGET` | 272 | +$1,100.65 | +$1,100.65 | $0.00 | +$4.05 | 10.17% |
**Observed:** L6 invalidation alone caused **−$3,726.32 across 1,244 exits**, a major negative contribution. This proves the account loss is concentrated by exit label; it does **not** prove widening stops would improve causal profitability. Prior entry/adverse-path features and alternative holds require paired same-entry tick-path tests before changing policy.

## E. Session and direction contributions
| Session | Closes | Net | Win rate | Profit factor | Avg/trade |
|---|---:|---:|---:|---:|---:|
| NEW_YORK | 1,184 | −$1,180.51 | 33.61% | 0.397 | −$1.00 |
| LONDON | 1,157 | −$1,070.30 | 31.89% | 0.419 | −$0.93 |
| SYDNEY | 164 | −$161.94 | 28.05% | 0.370 | −$0.99 |
| TOKYO | 169 | −$156.30 | 27.81% | 0.374 | −$0.92 |

| Side | Trades | Net | Win | Per-trade net |
|---|---:|---:|---:|---:|
| BUY | 1,259 | −$1,225.47 | 31.37% | −$0.97 |
| SELL | 1,415 | −$1,343.59 | 32.86% | −$0.95 |

## F. Exact vertical-funnel diagnostics (COUNTER EMISSIONS, not unique ticket counts)
| Stage/counter | Value | Interpretation |
|---|---:|---|
| `prel1_creator_grid_raw` | 384,474 | L0 virtual price-event emissions |
| `l2_opportunity_windows` | 2,299,848 | L2 qualifying windows (can be repeated ticks) |
| `l3_no_creator_grid_crossing` | 2,231,219 | L2 permitted but G0 event not available |
| `l3_proposals` | 60,771 | Source + structure qualified L3 proposals |
| `qualified_quality_chain` | 47,412 | L1–L6 quality passes |
| `l7_spread_denied` | 23,006 | L7 observed original-spread denial |
| `l7_prequeue_global_capacity_denied` | 19,405 | L7 blocked at 2-position global cap |
| `l7_prequeue_desk_capacity_denied` | 1,140 | L7 blocked by per-desk cap |
| `l7_risk_eligible_requests` | 3,861 | L7 submitted queue requests |
| `expired_latency` | 47 | Stale pending after 250ms latency |
| `spread_drift` | 1,137 | Later quote spread drift |
| `filled` | 2,674 | Hypothetical quote fills |
| `l4_simulated_positive_close_NOT_PAID` | 16,044 | Prior positive shadow close logged, not paid renewal |
| `l4_broker_paid_parent_context` | 0 | Actual broker paid parent context |
| `l6_warning` | 1,667 | Position warning occurrences |
| `l6_bounded_recovery_watch` | 864 | Intent to reassess after invalidation |
| `l6_state_confirmed_recovery_candidate` | 0 | Reentry candidates completing L6 recovery logic |
| `l7_capital_halt` | 0 | Simulated risk halt |
- **Source proposal ID preserved on 3/2,674 closes (0.11%); 2,671 shadow closes have no numeric source ID.** The current `Opportunity` source string and G0 adapter are not the same as verified/earned parent→child identity. Missing optional IDs are an integration diagnostic, not proof of fabricated trades.
- Execution rate: 5.64% of *quality-pass event count* becomes a close; this is an approximate FUNNEL COUNTER ratio, not a unique-eligible-opportunity probability.
- **Current shadow execution cannot earn genuine paid parent close credit:** `V1BrokerEvidencePort` requires independently observed broker DEAL_ADD. For Python research, a separately labeled hypothetical funded/settled ledger needs to drive the causally modeled renewal experiment, while retaining the strict broker-only accounting boundary. This is a missing testable research path, NOT permission to fabricate broker deals.
- Simultaneous capacity 2 compared with original historical March/April frontiers often requiring hundreds of positions is a structural mismatch. **Do not blindly raise cap**: current negative expectancy would likely multiply losses. First reproduce causal positive source and cost model, then test graduated heat-limited capacity.

## G. Entry-hour attribution — UTC (close cash attributed back to entry cohort for diagnostic only)
| Entry UTC hour | Trades | Entry cohort net | Win rate | Avg/trade |
|---|---:|---:|---:|---:|
| 00:00 | 7 | −$12.39 | 14.29% | −$1.77 |
| 01:00 | 18 | −$17.55 | 27.78% | −$0.98 |
| 02:00 | 16 | +$0.01 | 43.75% | +$0.00 |
| 03:00 | 5 | −$0.12 | 60.00% | −$0.02 |
| 04:00 | 13 | −$13.13 | 23.08% | −$1.01 |
| 05:00 | 27 | −$11.89 | 33.33% | −$0.44 |
| 06:00 | 148 | −$166.93 | 24.32% | −$1.13 |
| 07:00 | 176 | −$145.03 | 30.68% | −$0.82 |
| 08:00 | 197 | −$225.10 | 27.41% | −$1.14 |
| 09:00 | 169 | −$153.57 | 33.14% | −$0.91 |
| 10:00 | 132 | −$80.24 | 36.36% | −$0.61 |
| 11:00 | 127 | −$140.63 | 27.56% | −$1.11 |
| 12:00 | 272 | −$312.41 | 31.62% | −$1.15 |
| 13:00 | 223 | −$262.22 | 32.74% | −$1.18 |
| 14:00 | 262 | −$238.39 | 35.50% | −$0.91 |
| 15:00 | 200 | −$193.86 | 34.00% | −$0.97 |
| 16:00 | 178 | −$171.55 | 33.15% | −$0.96 |
| 17:00 | 140 | −$117.29 | 34.29% | −$0.84 |
| 18:00 | 132 | −$118.83 | 31.82% | −$0.90 |
| 19:00 | 163 | −$132.88 | 38.04% | −$0.82 |
| 20:00 | 67 | −$53.09 | 25.37% | −$0.79 |
| 22:00 | 2 | −$1.95 | 50.00% | −$0.97 |

## H. Entry/hold/exit/profit/drawdown/gross-loss — 75% OVERFIT teacher program (NOT yet scored)
- Realized current hold seconds: p10 **20.46**, median **124.09**, p90 **240.05**, p99 **241.38**. Current desk planned expiry 180–240 seconds; observed holds depend on exit reasons and tick chronology.
- Observed realized net mean per trade: −$0.96; gross loss per trade −$1.61; monthly quote-equity DD +$2,572.45 (a different risk dimension than an individual trade MAE).
- **Missing for 75% objective:** explicit original R9 OVERFIT event universe, matched entry/hold/exit targets with time/price normalization, matched post-entry MAE/MFE paths, and a prespecified definition of “75% of preferred per-trade performance” for metrics where lower is better (drawdown/gross loss). No OVERFIT labels were joined to these V1 trades; therefore attainment is UNMEASURED, not 0% or passed.
- Build offline teacher matching only AFTER settling both event populations, retaining nonmatched rows. Runtime may use only entry-time information, not optimal future exits, best trade outcome or oracle direction.

## I. Complete UTC daily close-time settled performance (including zero-trade dates)
| UTC day | Closes | Net USD | Gross loss USD | PF | Win % | Quote-equity DD USD | Quality passes | Funded requests |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-04-01 | 40 | −$45.75 | −$79.32 | 0.42 | 30.00% | 48.06 | 683 | 60 |
| 2026-04-02 | 31 | −$44.55 | −$59.81 | 0.26 | 32.26% | 55.31 | 703 | 49 |
| 2026-04-03 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-04-04 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-04-05 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-04-06 | 18 | −$30.65 | −$40.50 | 0.24 | 22.22% | 30.65 | 2,719 | 112 |
| 2026-04-07 | 12 | +$0.13 | −$13.28 | 1.01 | 58.33% | 15.40 | 2,580 | 109 |
| 2026-04-08 | 56 | −$88.93 | −$116.77 | 0.24 | 21.43% | 92.51 | 2,829 | 168 |
| 2026-04-09 | 104 | −$141.06 | −$206.77 | 0.32 | 31.73% | 149.06 | 3,713 | 247 |
| 2026-04-10 | 92 | −$64.11 | −$137.97 | 0.54 | 39.13% | 64.11 | 3,041 | 237 |
| 2026-04-11 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-04-12 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-04-13 | 99 | −$122.20 | −$172.57 | 0.29 | 26.26% | 128.28 | 1,583 | 153 |
| 2026-04-14 | 109 | −$136.52 | −$192.78 | 0.29 | 27.52% | 137.30 | 1,081 | 147 |
| 2026-04-15 | 163 | −$170.36 | −$261.19 | 0.35 | 32.52% | 187.76 | 2,016 | 213 |
| 2026-04-16 | 77 | −$92.21 | −$125.11 | 0.26 | 29.87% | 102.24 | 945 | 94 |
| 2026-04-17 | 154 | −$145.80 | −$260.65 | 0.44 | 28.57% | 169.93 | 3,077 | 245 |
| 2026-04-18 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-04-19 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-04-20 | 62 | −$34.17 | −$86.91 | 0.61 | 37.10% | 43.96 | 2,004 | 139 |
| 2026-04-21 | 213 | −$205.64 | −$347.78 | 0.41 | 32.86% | 214.60 | 2,711 | 267 |
| 2026-04-22 | 186 | −$173.59 | −$253.40 | 0.31 | 34.41% | 183.77 | 1,635 | 200 |
| 2026-04-23 | 80 | −$60.37 | −$120.33 | 0.50 | 32.50% | 62.07 | 922 | 95 |
| 2026-04-24 | 219 | −$193.57 | −$321.49 | 0.40 | 29.22% | 208.99 | 3,443 | 282 |
| 2026-04-25 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-04-26 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-04-27 | 194 | −$96.58 | −$233.10 | 0.59 | 41.24% | 97.32 | 2,145 | 198 |
| 2026-04-28 | 312 | −$237.80 | −$506.51 | 0.53 | 34.29% | 240.89 | 3,741 | 325 |
| 2026-04-29 | 209 | −$227.63 | −$357.11 | 0.36 | 30.62% | 233.55 | 2,728 | 247 |
| 2026-04-30 | 244 | −$257.69 | −$410.63 | 0.37 | 29.51% | 258.96 | 3,113 | 274 |

## J. Complete UTC ISO-week closed-trade performance (month-scoped ISO week segments)
| UTC ISO week | Closes | Net USD | Gross loss USD | PF | Win % | Quote-equity DD USD |
|---|---:|---:|---:|---:|---:|---:|
| 2026-W14 | 71 | −$90.30 | −$139.13 | 0.35 | 30.99% | 94.11 |
| 2026-W15 | 282 | −$324.63 | −$515.30 | 0.37 | 32.62% | 324.63 |
| 2026-W16 | 602 | −$667.10 | −$1,012.29 | 0.34 | 29.24% | 690.26 |
| 2026-W17 | 760 | −$667.33 | −$1,129.91 | 0.41 | 32.50% | 686.89 |
| 2026-W18 | 959 | −$819.70 | −$1,507.35 | 0.46 | 33.68% | 820.78 |

## K. Month-specific root-cause hypothesis / missing original behavior
1. **SOURCE-EXACT OWNER MECHANISM:** April: prior-child realized hold and P/L bucket plus depth/rule lineage is specified in original 136T2 but absent from current operative shadow parent/child promotion path.
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
- Local source: `GRID0269_SEVEN_MONTH_FULL_TICK/2026-04/month_full_qa.json`, `/all_completed_shadow_trades.csv`, `/daily_performance.csv`, `/weekly_performance.csv`, `/run_config.json`.
- No new full-tick strategy replay was performed for this forensic diagnostic; numeric breakdown is rederived from 57.5m-tick completed GRID0269 original execution ledgers and exact current implementation source.
- Full-tick replay market P&L is modeled quote/cash economics, not Coinexx broker fill certification; end-of-month positions all closed, month transitions independently reset; metrics do not by themselves validate 100% R9 SYNTH or 75% R9 OVERFIT.
- This report is a research workpaper for the developer, not the governing law. Frozen owner instructions, archived successful source and original primary data outrank this diagnosis. Original GRID0258 ledger, J0183 official cursor, and August seal remain unchanged.
