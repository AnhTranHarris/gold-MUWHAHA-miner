# GRID0251 — Original R9-cycle stateful grid economics and teacher/OVERFIT decomposition

**Governing research principle:** "r9 syth as perfomance goals, r9 overfit shows optimal trades". R9 SYNTH is performance benchmark, R9 OVERFIT reveals *retrospective* favorable trades, never causal signals. Original R9 REAL and original Dukascopy Bid/Ask tick path are controls. No fixed month used to authorize entries. All Jan–Jul months have been inspected historically and are NOT blind OOS. August SEALED. Trading disabled. Scientific J0183 preserved.

## New scientific finding
Genuinely observed, sequential grid crossings can supply plenty of volume without sustainable net edge. An R9-inspired 0.01 lot one-ounce **research shadow** with 250ms delayed actual Bid/Ask entries, post-close reset/rearm (at most three within a minute), one concurrent slot, 30–60s quote-observed trailing/exit, and explicit $0.20 round-trip fee produces **252,048 trades**, more than R9 SYNTH 219,342 Jan–Jul, but **all 7 monthly quote-proxy net results are NEGATIVE**. The 7-month returns are hypothetical unconstrained continuous research totals: not a capital-feasible 100k account or broker fills. Engine does not enforce margin or bankruptcy; applying even the active engine's 35%-capital-drop hard-stop to realized close cash alone triggers around Feb 4, 2026 (37,866 closes, $64,998.878). Full floating real risk could halt earlier. This cannot be promoted.

## Ground-truth seven-month monthly diagnostic (one-ounce source USD, not Coinexx broker account USD)
| Month | Fast rearm closes | Fast rearm net | Fast rearm gross loss | Monthly fast-run maximum floating+realized DD | Completed M1 longer-runner closes | Longer-runner net | 30s perfect oracle net ceiling | 90s perfect oracle net ceiling |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-01 | 33,714 | -30,379.14 | -36,554.94 | 30,379.14 | 13,190 | -12,333.13 | 42,109.13 | 94,782.64 |
| 2026-02 | 33,032 | -34,401.50 | -42,254.74 | 34,401.50 | 13,702 | -14,629.21 | 49,820.20 | 110,430.82 |
| 2026-03 | 53,947 | -51,985.16 | -65,265.29 | 51,987.10 | 23,664 | -22,773.06 | 95,028.84 | 207,869.16 |
| 2026-04 | 35,475 | -32,835.04 | -38,758.45 | 32,836.37 | 13,919 | -13,802.74 | 36,959.26 | 85,684.56 |
| 2026-05 | 31,941 | -26,884.64 | -31,627.84 | 26,886.96 | 12,092 | -10,271.79 | 28,710.65 | 66,717.56 |
| 2026-06 | 36,523 | -30,256.34 | -36,261.99 | 30,256.34 | 14,043 | -12,031.41 | 36,176.81 | 83,565.42 |
| 2026-07 | 27,416 | -24,397.68 | -27,687.47 | 24,397.68 | 10,118 | -9,333.73 | 18,662.62 | 46,189.49 |

### Exact trading economics identity, seven months; all source USD/oz
| Component | Fast rearm source | Completed-M1 longer runner |
|---|---:|---:|
| Completed hypothetical closes | 252,048 | 100,728 |
| Signed midpoint move (prior to two-sided spread/fee) | +$2,886.00 | $-499.13 |
| Full two-sided spread drag | -$183,615.90 | -$74,530.34 |
| Flat research $0.20 fee per close | -$50,409.60 | -$20,145.60 |
| Net | $-231,139.50 | $-95,175.07 |
The identity reconciles to reported P&L exactly to two decimal places. Signed midpoint effect is slightly POSITIVE for fast rearm (+$2,886), but actual spread (~$183,616) plus fee (~$50,410) overwhelms it. This is the dominant obstacle, not raw signal shortage. The slower specialist has negative midpoint edge (~-$499). Source UTC weeks are NOT verified MT5 broker-server ISO week partitions; 0/36 source weeks positive in each model, whereas R9 benchmark source has 31 populated MT5-server weeks. No claimed period-to-period matched broker comparison.

## Sequential tested cycles
1. **GRID0250 prior control:** eight previous as-of 136B source hypotheses all Apr+May weekly negative. GRID0250 paper and local archive are immutable predecessor; do not re-run ledger harvest as if never done.
2. **GRID0251 true bounded rearm source:** four as-of price-crossing cycle policies (follow, observed failed-break fade, observed 2s continuation, prior completed minute+5s efficiency). All four April+May portfolios negative in 9/9 observed source weeks. Fast policy had 67,417 closes net -59,719.48 USD/oz. Outputs: GRID0251_R9_CYCLE_SOURCE_ECONOMICS.json.
3. **GRID0251 six exit/quality expansions:** profit-target, 120s runner, cost-payback trail, early failure-risk cut across inherited 4 source states; six variants negative in all 9 weeks, see GRID0251_SECOND_CREATIVE_CYCLE_RESULTS.json. These are independent portfolios, NOT additive.
4. **Full seven-month frozen representative test:** fast rearm + completed-minute long-runner independently January→July negative 7/7 months, 0/36 UTC source weeks positive; 57,527,562 exact ORIGINAL tick rows read and scored, never August.
5. **Causal state prediction vs teacher:** train on original April1–16, calibrate Apr17–30 with zero future event labels available in decisions, chronologically evaluate May only if calibration positive and n>=20. ALL nine score thresholds failed April calibration (one threshold-level trade at −2.38, otherwise none). Therefore FAIL-CLOSED, zero May trades: no model positive net or valid 31-week evidence, no May threshold optimization.
6. **OVERFIT-style oracle ceiling on EXACT physically simulated entry timestamps:** 30/90s hindsight choose best of buy/sell, best future-exit quote, omit losers, NO portfolio interaction or executable source claims. Source event population 252k demonstrates big *retrospective* movement potential but no causal choice. In April/May/July the 30s **both-sides** maximum optimistic sum is even less than numerical R9 monthly account net (units/feeds not economically comparable). At 90s hindsight ceiling grows sharply—this identifies a research hypothesis about long survival/selection, NOT profit. Best side is roughly 50/50 versus observed crossing sign. Reusing the oracle score or future prices to approve orders is prohibited.
7. **Research capital loss lock:** with frozen $100k theory starting cash and 35% starting-balance drop stop on realized closes only, earliest breach under fast policy at 2026-02-04T12:34:46.836Z after 37,866 closes and cumulative +$7,542.64 gross gains, −$42,543.76 gross losses. Portfolio beyond stop is a research shadow. Always preserve hard-risk constraint during actual funded verification.

## Why earlier successful mechanisms still matter
- GRID0185 original J179F T1/T2 + conditional M5 energy 30m harvest/90m runner: 558 Apr–Jul source quote positions, +2202.527/oz, four positive historical monthly totals but six losing weekly partitions, never 50% volume. This is separately RECONSTRUCTIBLE positive source heritage, NOT to be replaced by generic rearm.
- April136 native + real paid renewal genealogy and March135 native structures are preserved original prior successes but many historical best cells were selected after examining outcome. Do not directly import hindsight parameters. Restore actual event generators and parent id as-of and test ONE shared funded portfolio.
- Original paired REAL/SYNTH/OVERFIT corpus (PERSONAL Drive): https://drive.google.com/drive/folders/1ES78vXb2mFsOsa50BiwCLsT6BXgLe-Oe; BETA024 and original 165630 matched pair labels. OVERFIT optimal trade locations/horizon are retrospective optimization targets only.

## Next four creative, falsifiable non-hindsight research hypotheses (unproven)
1. **Economically valid R9-style executable bracket** with actual broker stop/freeze/point min and dynamically verified spread/latency. Use Coinexx original tester as a separate lower-spread comparator; do NOT assume Dukascopy and Coinexx have identical fills or inject artificially lower spread into Dukascopy paths.
2. **Post-entry information-event time and 1–2s realized survival state** from original teacher correlation, no future known. Try correct side and cost-normalized 30/90s continuation decision after already-funded scout survives real BidAsk, not one arbitrary pre-entry filter.
3. **Strong accepted March135/April136/J179F source restoration** with last completed HTF roles, original observable structural location and paid parent-child genealogy. Recover missing J179F original offer files rather than inventing financial success from its exit rule.
4. **Alternative broker-legitimate entry geometry:** limit-style or stop-limit mechanisms only if actual Coinexx order support and conservative price-through + latency + spread/fill uncertainty are verified. No fictitious spread capture. Preserve one account shared capital/margin and three-stage original grid ownership.

## Audit and constraints
- Original raw tick sources Jan–Jul unchanged, August sealed. All experiments already-inspected months, NO honest new untouched holdout.
- SOURCE price drag can be decomposed for each side by: signed midpoint movement − 1/2(entry observed spread + exit observed spread) − $0.20/oz fee; equality was tested.
- Broker symbol contract, leverage, commissions, bid/ask slippage, broker response, market-impact and actual cash remain unverified; no MT5 EA activation.
- Official MQL5: https://www.mql5.com/en/book/automation/symbols/symbols_spreads_levels; buy-stop conditions use Ask, sell-stop Bid, minimum stops/freeze constraints and dynamic spread must be honored. External sources supply mechanics, NEVER validated XAUUSD performance numbers.
- Potential R9 SYNTH 100% performance: Jan–Jul +$309,122.85, 219,342 trades, seven positive months and 31 positive MT5-server reporting weeks. Actual latest GRID0251 gate FAIL. Gross loss and drawdown safety always recorded even when net category prioritized.
- Program paths in this ZIP: grid0251_paid_grid_cycles_profiles.py, grid0251_seven_month_holdout_diagnostic.py, grid0251_original_cycle_overfit_oracle.py, grid0251_causal_teacher_state_probe.py, grid0251_second_cycle.py and regression tests. Research-only modules, NOT a certified original EA port.
