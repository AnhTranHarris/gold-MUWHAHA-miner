# GRID0270 emergency source-exact analysis: 2026-03

> **Engineering forensic workpaper — NOT owner governance, NOT a promoted strategy, NOT live MT5 performance.** Original owner whitepaper, ratified full conversation, source code and chronological ledgers remain controlling. No March/April hindsight whitelist may be deployed.

## A. Provenance and comparison contract
- GRID0269 original Dukascopy input `XAUUSD_DUKAS_2026_03_ticks.csv(3).gz`; SHA256 `814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177`; **9,433,179 complete original Bid/Ask ticks**.
- Exact tested profile: `{"broker_session_confirmed": false, "commission_per_roundtrip_usd": 0.2, "contract_oz": 100.0, "global_max_open": 2, "latency_ms": 250, "leverage": 500, "lot": 0.01, "margin_reserve_fraction": 0.35, "require_all_htf": true, "starting_cash": 100000.0}`. Fresh $100,000 hypothetical account every month; fixed 0.01 lot; no Coinexx confirmed deals. No AUG ticks.
- All daily and ISO-week cash are attributed to **UTC exit time**. Week segments reset at month boundaries, not a single contiguous multi-month equity book.
- R9 SYNTH is the **ideal day/week/month ACCOUNT benchmark**; R9 OVERFIT is the *offline per-trade* preferred entry/hold/exit/profit/floating-DD/gross-loss teacher. Neither is an executable signal.
- Prior original mechanics: Original March 135 source has 7 specialized streams: NATIVE/HIGHVOL/ASIA/WATCHDOG/RECOVERY plus route context; original model-selected QUAL 15,988 positions +$125,792.74, but March-outcome-selected cells are RETROSPECTIVE and not live-valid. J0183 quotes reprice source-selected E/X, not a reconstructed causal funded strategy.

## B. Monthly performance: realized and risk
- Realized **−$2,382.16**, gross winners +$2,498.06, gross losers −$4,880.23; cash +$97,617.84 from $100,000; cash/closed-trade ledger residuals 0.0 / 1.3574208423960954e-09.
- **2,839** shadow closes, 35.19% win, PF 0.5119, average net/trade **−$0.84**, max tick-marked quote-equity DD **+$2,418.74**, max concurrent positions 2, end open 0.
- Calendar day positives 0, negatives 22; UTC week-segment positives 0, negatives 5.

## C. Frozen R9 SYNTH monthly 100% comparison (original prior research documentation)
- Reference from original `research/delta_a_alpha/monthly/march_2026/DAA_MARCH_VERTICAL_GRID_DISCOVERY_135.md`: ideal net **+$75,698.63**, trades **40,985**, gross loss **−$2,024.86**, PF 38.3846, win 90.01%.
- Current V1 **6.93% of R9 SYNTH trade count**. Trade shortfall **38,146**; observed count needs ~**14.44×** current executed velocity *without worsening economics*.
- Current V1 net is negative, so **net-performance completion ratio is not a meaningful attainment percentage**; the required absolute change to reach the positive target is **+$78,080.79**. This is a gap, not a prediction.
- R9 day/ISO-week exact targets must be retrieved from original frozen GRID0186 **already reconstructed reference tables**, then checked against corresponding UTC windows. No repeat audit of MT5 report is required. Missing aligned clock proof must not be substituted with a guessed shift.

## D. Exit-root economics, not merely headline P&L
| Exit reason | Trades | Net | Gross win | Gross loss | Avg/trade | Share |
|---|---:|---:|---:|---:|---:|---:|
| `L6_INVALIDATION` | 1,478 | −$4,610.26 | $0.00 | −$4,610.26 | −$3.12 | 52.06% |
| `L7_TIME_EXPIRY` | 389 | +$73.21 | +$295.97 | −$222.76 | +$0.19 | 13.70% |
| `L7_TRAILING_OR_HARD_STOP` | 530 | +$241.65 | +$288.85 | −$47.20 | +$0.46 | 18.67% |
| `L3_TARGET` | 442 | +$1,913.24 | +$1,913.24 | $0.00 | +$4.33 | 15.57% |
**Observed:** L6 invalidation alone caused **−$4,610.26 across 1,478 exits**, a major negative contribution. This proves the account loss is concentrated by exit label; it does **not** prove widening stops would improve causal profitability. Prior entry/adverse-path features and alternative holds require paired same-entry tick-path tests before changing policy.

## E. Session and direction contributions
| Session | Closes | Net | Win rate | Profit factor | Avg/trade |
|---|---:|---:|---:|---:|---:|
| NEW_YORK | 1,581 | −$1,317.07 | 37.00% | 0.529 | −$0.83 |
| LONDON | 1,089 | −$890.35 | 33.79% | 0.508 | −$0.82 |
| SYDNEY | 146 | −$168.12 | 26.03% | 0.315 | −$1.15 |
| TOKYO | 23 | −$6.62 | 34.78% | 0.752 | −$0.29 |

| Side | Trades | Net | Win | Per-trade net |
|---|---:|---:|---:|---:|
| BUY | 1,267 | −$1,177.34 | 33.54% | −$0.93 |
| SELL | 1,572 | −$1,204.82 | 36.51% | −$0.77 |

## F. Exact vertical-funnel diagnostics (COUNTER EMISSIONS, not unique ticket counts)
| Stage/counter | Value | Interpretation |
|---|---:|---|
| `prel1_creator_grid_raw` | 617,873 | L0 virtual price-event emissions |
| `l2_opportunity_windows` | 3,089,208 | L2 qualifying windows (can be repeated ticks) |
| `l3_no_creator_grid_crossing` | 2,972,393 | L2 permitted but G0 event not available |
| `l3_proposals` | 103,737 | Source + structure qualified L3 proposals |
| `qualified_quality_chain` | 68,787 | L1–L6 quality passes |
| `l7_spread_denied` | 47,326 | L7 observed original-spread denial |
| `l7_prequeue_global_capacity_denied` | 15,916 | L7 blocked at 2-position global cap |
| `l7_prequeue_desk_capacity_denied` | 297 | L7 blocked by per-desk cap |
| `l7_risk_eligible_requests` | 5,248 | L7 submitted queue requests |
| `expired_latency` | 46 | Stale pending after 250ms latency |
| `spread_drift` | 2,355 | Later quote spread drift |
| `filled` | 2,839 | Hypothetical quote fills |
| `l4_simulated_positive_close_NOT_PAID` | 32,015 | Prior positive shadow close logged, not paid renewal |
| `l4_broker_paid_parent_context` | 0 | Actual broker paid parent context |
| `l6_warning` | 1,853 | Position warning occurrences |
| `l6_bounded_recovery_watch` | 1,054 | Intent to reassess after invalidation |
| `l6_state_confirmed_recovery_candidate` | 2 | Reentry candidates completing L6 recovery logic |
| `l7_capital_halt` | 0 | Simulated risk halt |
- **Source proposal ID preserved on 9/2,839 closes (0.32%); 2,830 shadow closes have no numeric source ID.** The current `Opportunity` source string and G0 adapter are not the same as verified/earned parent→child identity. Missing optional IDs are an integration diagnostic, not proof of fabricated trades.
- Execution rate: 4.13% of *quality-pass event count* becomes a close; this is an approximate FUNNEL COUNTER ratio, not a unique-eligible-opportunity probability.
- **Current shadow execution cannot earn genuine paid parent close credit:** `V1BrokerEvidencePort` requires independently observed broker DEAL_ADD. For Python research, a separately labeled hypothetical funded/settled ledger needs to drive the causally modeled renewal experiment, while retaining the strict broker-only accounting boundary. This is a missing testable research path, NOT permission to fabricate broker deals.
- Simultaneous capacity 2 compared with original historical March/April frontiers often requiring hundreds of positions is a structural mismatch. **Do not blindly raise cap**: current negative expectancy would likely multiply losses. First reproduce causal positive source and cost model, then test graduated heat-limited capacity.

## G. Entry-hour attribution — UTC (close cash attributed back to entry cohort for diagnostic only)
| Entry UTC hour | Trades | Entry cohort net | Win rate | Avg/trade |
|---|---:|---:|---:|---:|
| 00:00 | 18 | −$28.00 | 16.67% | −$1.56 |
| 01:00 | 32 | −$46.62 | 21.88% | −$1.46 |
| 02:00 | 16 | −$10.36 | 31.25% | −$0.65 |
| 03:00 | 30 | −$32.82 | 23.33% | −$1.09 |
| 04:00 | 20 | −$14.85 | 30.00% | −$0.74 |
| 05:00 | 27 | −$25.27 | 29.63% | −$0.94 |
| 06:00 | 1 | −$2.36 | 0.00% | −$2.36 |
| 07:00 | 11 | +$7.69 | 54.55% | +$0.70 |
| 08:00 | 157 | −$140.27 | 35.03% | −$0.89 |
| 09:00 | 152 | −$157.09 | 30.26% | −$1.03 |
| 10:00 | 160 | −$138.57 | 32.50% | −$0.87 |
| 11:00 | 89 | −$58.70 | 34.83% | −$0.66 |
| 12:00 | 140 | −$81.92 | 40.00% | −$0.59 |
| 13:00 | 288 | −$351.36 | 30.21% | −$1.22 |
| 14:00 | 331 | −$280.09 | 36.56% | −$0.85 |
| 15:00 | 259 | −$184.17 | 38.22% | −$0.71 |
| 16:00 | 332 | −$286.44 | 37.65% | −$0.86 |
| 17:00 | 214 | −$94.00 | 39.25% | −$0.44 |
| 18:00 | 221 | −$157.25 | 38.46% | −$0.71 |
| 19:00 | 173 | −$156.88 | 32.37% | −$0.91 |
| 20:00 | 147 | −$113.76 | 37.41% | −$0.77 |
| 21:00 | 6 | −$14.25 | 0.00% | −$2.37 |
| 22:00 | 1 | −$2.61 | 0.00% | −$2.61 |
| 23:00 | 14 | −$12.24 | 35.71% | −$0.87 |

## H. Entry/hold/exit/profit/drawdown/gross-loss — 75% OVERFIT teacher program (NOT yet scored)
- Realized current hold seconds: p10 **10.32**, median **66.31**, p90 **210.26**, p99 **241.21**. Current desk planned expiry 180–240 seconds; observed holds depend on exit reasons and tick chronology.
- Observed realized net mean per trade: −$0.84; gross loss per trade −$1.72; monthly quote-equity DD +$2,418.74 (a different risk dimension than an individual trade MAE).
- **Missing for 75% objective:** explicit original R9 OVERFIT event universe, matched entry/hold/exit targets with time/price normalization, matched post-entry MAE/MFE paths, and a prespecified definition of “75% of preferred per-trade performance” for metrics where lower is better (drawdown/gross loss). No OVERFIT labels were joined to these V1 trades; therefore attainment is UNMEASURED, not 0% or passed.
- Build offline teacher matching only AFTER settling both event populations, retaining nonmatched rows. Runtime may use only entry-time information, not optimal future exits, best trade outcome or oracle direction.

## I. Complete UTC daily close-time settled performance (including zero-trade dates)
| UTC day | Closes | Net USD | Gross loss USD | PF | Win % | Quote-equity DD USD | Quality passes | Funded requests |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-03-01 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-03-02 | 16 | −$15.40 | −$31.23 | 0.51 | 31.25% | 34.28 | 1,373 | 46 |
| 2026-03-03 | 11 | −$14.65 | −$19.54 | 0.25 | 18.18% | 15.65 | 1,162 | 30 |
| 2026-03-04 | 110 | −$60.00 | −$187.83 | 0.68 | 39.09% | 87.28 | 2,835 | 211 |
| 2026-03-05 | 27 | −$36.98 | −$57.72 | 0.36 | 25.93% | 38.58 | 2,367 | 170 |
| 2026-03-06 | 31 | −$43.90 | −$56.51 | 0.22 | 29.03% | 43.90 | 3,640 | 231 |
| 2026-03-07 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-03-08 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-03-09 | 79 | −$109.47 | −$155.13 | 0.29 | 29.11% | 122.36 | 3,072 | 219 |
| 2026-03-10 | 106 | −$100.40 | −$180.70 | 0.44 | 32.08% | 112.48 | 2,189 | 230 |
| 2026-03-11 | 146 | −$124.42 | −$230.36 | 0.46 | 36.30% | 127.82 | 3,074 | 281 |
| 2026-03-12 | 200 | −$135.01 | −$306.80 | 0.56 | 37.00% | 181.48 | 2,206 | 218 |
| 2026-03-13 | 229 | −$203.39 | −$415.98 | 0.51 | 31.88% | 215.14 | 2,612 | 253 |
| 2026-03-14 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-03-15 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-03-16 | 117 | −$17.48 | −$145.16 | 0.88 | 41.03% | 56.76 | 1,684 | 145 |
| 2026-03-17 | 241 | −$206.64 | −$358.07 | 0.42 | 35.68% | 206.64 | 2,701 | 283 |
| 2026-03-18 | 104 | −$87.05 | −$188.35 | 0.54 | 34.62% | 117.31 | 2,534 | 217 |
| 2026-03-19 | 263 | −$184.91 | −$462.33 | 0.60 | 38.40% | 188.28 | 5,074 | 413 |
| 2026-03-20 | 120 | −$204.31 | −$262.67 | 0.22 | 17.50% | 204.61 | 3,720 | 298 |
| 2026-03-21 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-03-22 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-03-23 | 264 | −$167.50 | −$470.15 | 0.64 | 38.64% | 178.15 | 4,754 | 456 |
| 2026-03-24 | 27 | −$43.13 | −$53.49 | 0.19 | 25.93% | 44.93 | 4,071 | 140 |
| 2026-03-25 | 365 | −$265.51 | −$616.56 | 0.57 | 38.90% | 284.80 | 5,825 | 418 |
| 2026-03-26 | 59 | −$31.37 | −$90.81 | 0.65 | 38.98% | 46.19 | 4,264 | 244 |
| 2026-03-27 | 32 | −$52.23 | −$64.90 | 0.20 | 31.25% | 54.28 | 2,726 | 192 |
| 2026-03-28 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-03-29 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 | 0 | 0 |
| 2026-03-30 | 239 | −$257.86 | −$436.46 | 0.41 | 32.64% | 267.29 | 3,216 | 297 |
| 2026-03-31 | 53 | −$20.57 | −$89.46 | 0.77 | 41.51% | 50.47 | 3,688 | 256 |

## J. Complete UTC ISO-week closed-trade performance (month-scoped ISO week segments)
| UTC ISO week | Closes | Net USD | Gross loss USD | PF | Win % | Quote-equity DD USD |
|---|---:|---:|---:|---:|---:|---:|
| 2026-W09 | 0 | $0.00 | $0.00 | — | 0.00% | 0.00 |
| 2026-W10 | 195 | −$170.92 | −$352.84 | 0.52 | 33.85% | 181.70 |
| 2026-W11 | 760 | −$672.70 | −$1,288.96 | 0.48 | 33.82% | 693.17 |
| 2026-W12 | 845 | −$700.39 | −$1,416.58 | 0.51 | 34.56% | 734.03 |
| 2026-W13 | 747 | −$559.73 | −$1,295.92 | 0.57 | 38.02% | 562.07 |
| 2026-W14 | 292 | −$278.43 | −$525.92 | 0.47 | 34.25% | 305.29 |

## K. Month-specific root-cause hypothesis / missing original behavior
1. **SOURCE-EXACT OWNER MECHANISM:** March: highest available original March source fidelity comparator is historical 135 full 7-family native/HV/Asia/Watchdog/Recovery, including retrospective selection. Reconstruct causal pre-entry source logic; do not port successful hindsight cells.
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
- Local source: `GRID0269_SEVEN_MONTH_FULL_TICK/2026-03/month_full_qa.json`, `/all_completed_shadow_trades.csv`, `/daily_performance.csv`, `/weekly_performance.csv`, `/run_config.json`.
- No new full-tick strategy replay was performed for this forensic diagnostic; numeric breakdown is rederived from 57.5m-tick completed GRID0269 original execution ledgers and exact current implementation source.
- Full-tick replay market P&L is modeled quote/cash economics, not Coinexx broker fill certification; end-of-month positions all closed, month transitions independently reset; metrics do not by themselves validate 100% R9 SYNTH or 75% R9 OVERFIT.
- This report is a research workpaper for the developer, not the governing law. Frozen owner instructions, archived successful source and original primary data outrank this diagnosis. Original GRID0258 ledger, J0183 official cursor, and August seal remain unchanged.
