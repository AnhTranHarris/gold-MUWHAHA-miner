# R9 HybridGate January R04 — source-cost-corrected tick-ordinal exits, quote-event cohort and input-causal meta admissions

**2026-11-22 | JANUARY 2026 DELIBERATE IN-SAMPLE | NO R9 SUCCESSOR ACCEPTED | NO LIVE STRATEGY**

## Decision — do not misclassify this round

The only counterfactual R04 route with a positive **net booked-equivalent** quote cash result uses a selective, in-sample-trained risk model and generates **1,556 completed trades, 981 profitable AFTER the recorded fee, +$113.18 over January at original 0.01 lot**. However, it jointly matches only **205 of the 27,980** immutable original R9 entry/exit trade references within the prior interim ±2s tolerance and matches **zero** complete protected recovered two-leg cycles. It FAILS owner whole-system coverage, original exit-match, profitable-exit and recovered-cycle gates. It is not an approved EA improvement. All other tested full-January R04 alternatives have negative after-fee cash results.

**The correct reading: one useful in-sample filtering/scoring mechanism, no passing reconstructed R9 strategy.** The source or model must not be promoted to production, or used to describe a broker-live account. No frozen January capital policy, approved July R8, RB3, S100 V2 or February model was modified.

## W0 — source and cost-accounting custody

1. Frozen original R9 HybridGate v1.90 `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5` Git blob `7eecb5f1947017a01ce85b2520725de54749e523` remains unmodified.
2. Frozen original Coinexx January REAL TickLogger gzip `XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz` SHA256 `1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8`; **7,699,274 source-ordered Bid/Ask rows**, including **413 same-millisecond adjacent rows**, never deduplicated or modified. The existing R03 C++ source reader, models, and January original R9 manifest are external retained dependencies; no raw tick copy or 107MB feature table is packed here.
3. Frozen 272,352 original synthetic R9 leg marks SHA256 `9c9ebf5889c309a10e4370e355b99d75ae54cf5ccfdaa5ebab9042206f3f8cc5`. The read-only January 27,980 reference manifest has **24,368 original booked profitable trade legs, 2,147 protected negative-first/positive-completed two-leg recovered cycles, +$41,520.82 original booked net, $100 tester starting balance → $41,620.82 original tester closing balance**.
4. PRIMARY Drive R9 historical audited source explicitly states the original R9 XAUUSD **0.01 lot = one XAU/ounce** and **$0.02 total original entry+exit trading fee per completed 0.01-lot trade**, previously included in original R9 mapped quote `quote_net` where available: [original SYNTH winners and complete REAL quote-path R9 forensic source](https://drive.google.com/file/d/1SaJfm8bdVC01yyoCcdd1iw5HCFK6Mpnw/view). The ORIGINAL source MT5 tester XLSX is identified at `https://drive.google.com/file/d/18FRnz7k__Pu5C0LOHMdEFXEz5Ln_bMMG/view` (98,625,766 bytes), but direct raw retrieval was not available in this session. Thus the roundtrip fee is validated by the **original source-linked audit**, not independently read back from the XLSX in R04. No further assumptions, user-unapproved friction charges or fictitious 20-cent fee were applied.
5. Counterfactual **source-quote CASH** for one completed 0.01-lot-equivalent position is:
   - BUY = `real_Bid_exit - real_Ask_entry - 0.02 USD`;
   - SELL = `real_Bid_entry - real_Ask_exit - 0.02 USD`.
   Observed Bid/Ask spread is already in these price-side differences and must never be debited twice. The source tester's already booked `original_booked_net_usd` is **never debited a second 0.02**. No execution slippage, latency, rejections, broker stop levels, margin liquidation, deposit FX or dynamic fee overrides are asserted. Quote simulation is not actual filled-account performance.

## W1–W2 — precisely selected original Atlas and independent REAL quote witnesses

The immutable target population remains all **27,980** original January R9 trade IDs. The narrow witness cohort is sourced from the previously preserved, explicitly **hindsight-optimistic** R03 `±5 seconds` chronological quote teacher, used ONLY for offline research: 27,974 original trades have at least one correctly ordered observed source quote pair. After the verified **2-cent** original R9 fee, **26,188** have a nonzero retrospective best-case mark. Of these, **2,660** become nonpositive if their hindsight-selected entry/exit SECONDS are executed at the first actual quote of each selected second; **2,006** of these 2,660 were originally SYNTH-booked profitable. **23,475** are fee-positive even at that first quote of each independently hindsight-selected second; **21,117** were originally SYNTH winners. An additional 53 ordered teacher references cannot be graded using first-of-chosen-second quotes under the required strict source ordering; 6 have no ordered teacher pair. These are UNKNOWN, not strategic losses.

Matched witness/control contrasts (original entry-of-second REAL causal features only): entry median spread **19 cents both cohorts**, exit median spread **19 cents both**; completed recent 10s quote count median 51 versus 49; recent 10-second directional efficiency median **0.354 vs 0.366**. Spread magnitude alone cannot discriminate the 2,660 difficult cases. Their intrasecond quote-selection path is materially different. Teacher-selected quotes are never available in the independent trading process.

There are **2,147** frozen originally recovered positive two-leg cycles. Each is a mandatory protected outcome CONTROL; a different simulated first/second schedule is not accepted as having preserved an original recovery unless both fixed source identities jointly align and the independently executed new complete-cycle outcome is positive after recorded costs.

## W3 — external mechanism and MT5 implementation research, post-observation only

- MetaQuotes official [Strategy Tester and MQL5 book](https://www.mql5.com/files/book/mql5book.pdf): every-tick tester-generated intraminute paths may differ from recorded real-tick paths. Historical synthetic seconds remain retrospective labels, not data to inject into a REAL-tick router.
- MetaQuotes [DEAL_COMMISSION, DEAL_FEE and DEAL_SWAP](https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties) distinguish actual broker accounting. [SYMBOL_TRADE_CONTRACT_SIZE and SYMBOL_TRADE_TICK_VALUE](https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants) and [`OrderCalcProfit`](https://www.mql5.com/en/docs/trading/ordercalcprofit) identify correct terminal-side instrument economics for an MQL5 port. An account-sized port must read the broker's symbol and trading history, rather than hardcoding a universal XAUUSD 0.01 lot assumption for other brokers.
- MetaQuotes [`CopyBuffer` and completed MTF bars](https://www.mql5.com/en/docs/series/copybuffer) support shift-1 completed-bar computation; current M1 and tick features remain explicitly as-of. Existing R03 completed M1/M5/M15/H1 quote-derived indicators were reused.
- Event-based first-passage and competing risk modeling, including R9 first/second conditional recovery context, are research hypotheses, not positive-performance claims. No real order-book imbalance, signed transaction volume or true L2 queue is available in the original Coinexx TickLogger; signed quote-update movement is named as a **proxy** only.

## W4 — pre-registered scientifically different actions

A. **Fee-positive observed first passage:** existing January-trained R03 first/second BUY/SELL/WAIT hazard, and a source-quote-confirmed favorable liquidation condition on current Bid/Ask. The 30-cent liquidation-side adverse bound is an experimental limit near the earlier R9 30-point stop parameter, NOT identical original R9 broker stop placement. Includes online quote reversal, phase conditional and smoothed pressure variants. Fixed source `0.01 lot` cash fee 2 cents; no 20-cent or other extra fee.

B. **Causal entry meta-label:** full January R03 independently generated V02 lifecycle, **37,052 entries**, each labelled net of exact 2-cent source fee. LightGBM binary fitted fee-profit meta-label and Huber expected-cash head on the **current/past only** completed M1/M5/M15/H1, as-of quote, spread, minute phase and signed quote-change proxy. Historical realized outcomes enter *training labels only*. The entry-score code never sees original fixed R9 manifest or retrospective teacher chosen quote. Fee-positive AUC in January TRAINING = **0.72384**, while fitted expected-cash correlation = **0.05483**. The latter is an important limit: the model distinguishes fee-positive frequency moderately but does not forecast large negative payoff severity. No out-of-sample claims.

C. **Bounded source-economic exit adaptation:** for risk-selected positions only, compare original R03 14-cent probe with **56 cents** (original January R9 winning-position REAL observed median MFE) and **98 cents** (original R9 median booked net leg). These are **historical evidence anchors for research**, not universal stop recommendations. A phase-favorable adapter uses the original observed R9 learned minute-exit phase for completed REAL quote checks, never reads original trade labels inside execution. All price stops and timeout changes legitimately update next position availability.

## W5 — efficient implementation, no new massive source library

A C++17 zlib direct replay scans the exact 7.699m source ticks and rejects source/score quote mismatches. Existing R03 as-of entry hazard estimates are generated from the original replay source. The R04 Python scorer streams **1,323,041 original source observed seconds**, with each of the two meta probabilities computed from as-of features in chunks. No raw tick copy. No new full-month duplicate OHLC or quote store uploaded. All R04 price/account grade outputs are local, while only bounded selected ledgers/models/scripts are preserved.

The `r04_meta_replay` **meta=0 full January ledger is byte-for-byte equal** to the frozen R03 V02 original `r03_repro_profit_v02.csv`, before the separate exact fee accounting. This is an executable noninterference receipt.

## W6 — complete January real-tick, original-fee-corrected results

All alternatives rerun the **entire January 7,699,274 ordered Coinexx quotes**, with independently generated counterfactual trade inventory and recorded 2-cent per-trade fee. `Cash P&L` is the aggregate observed Bid/Ask quote-book net for **one XAU-equivalent 0.01 lot** after the original source-documented fee, before any unverified slippage; NOT the original R9 tester balance or a broker-filled MT5 report. `Joint ±2s` is one-to-one same-side original R9 trade ID match of both entry/exit timestamp seconds. It is the prior interim R01–R03 clock proxy, not a redefinition of the user's exact 5% requested tolerance.

| January full-source candidate | Completed | Fee-profitable exits | Net CASH quote simulation | Original joint ±2s | Protected recovered cycles, BOTH legs matched ±2s |
|---|---:|---:|---:|---:|---:|
| R03 V02 original replay, exact original fee | 37,052 | 24,529 | **−$9,067.88** | 1,501 | 5 |
| R04 fee-profit meta admit 0.65, original R03 exit | 25,475 | 19,091 | −$4,466.38 | 1,234 | 3 |
| R04 fee-profit meta admit 0.75, original R03 exit | 10,215 | 8,491 | −$621.05 | 573 | 1 |
| R04 original-R9-proximate loss bound, observable first-passage | 39,379 | 14,152 | −$9,194.55 | 671 | 0 |
| R04 observed pullback hazard | 39,303 | 10,258 | −$8,596.55 | 1,014 | 1 |
| R04 phase plus tick-ordinal giveback | 39,283 | 10,248 | −$8,609.39 | 1,420 | 3 |
| R04 rolling-pressure competing exit | 39,279 | 9,598 | −$8,562.85 | 1,222 | 1 |
| R04 meta=0.75, 56-cent target, phase-adapted exit | 9,626 | 5,783 | −$151.76 | 1,256 | 6 |
| **R04 meta=0.80, 56-cent target, phase-adapted exit** | **1,556** | **981** | **+$113.18** | **205 (0.73%)** | **0** |

The more restricted positive experimental policy has **11 positive UTC exit dates, 10 negative dates**, an **exit-to-exit marked cash drawdown of $32.36**, and an arithmetic final cash of $213.18 if simply adding net changes to the original $100 starting point. **That arithmetic is NOT a tradeable broker account equity/margin or a surviving funded balance claim**, because the current replay has no margin constraints and assumes every quoted fill is attainable. Only **178** of its 205 matched original trades are BOTH originally SYNTH winners and independently fee-positive, and **none** of the 2,147 originally recovered winning cycles was fully preserved as a two-leg counterpart. No result is promoted.

For completeness, the source-anchored 98-cent target and alternative phase/threshold configurations are in `r04_graded_trials.csv` and JSON, including ALL counts, exact signed cash, 2s/5s original matches, preserved profitable identities and recovered controls. This is a bounded scientific mechanistic screen, not a general 25× hyperparameter sweep.

## W6 regression and source integrity

**5/5 PASS**: original January raw gzip SHA + original R9 book count/account arithmetic; R03 V02 ledger exact byte equality at meta=0; all full-month independently produced net-after-fee grade arithmetic; original R03-as-of prediction quote alignment and bounded meta score validity; altered FUTURE price suffix must not change any earlier already-closed trade when the frozen predictor/scored quotes are changed consistently only after the cutoff. Strict C++17 `-O3 -Wall -Wextra -Werror` compilation of both C++ engines passes. No R9 original EA, tick data, booked trade IDs, entry or exit history or approved account policy changed. February and later data have not been used for R04 fitting.

## W7 — mandated next research cycle, NOT implicit approval

**R04 combined contract FAILS.** The positive high-confidence portfolio is not sufficiently close to original fixed R9 entry/exit timing, does not reconstruct its protected second legs, and lacks owner trade count/winner count. Filtering R03's retrospectively profitable model cases alone destroys high-volume R9 lifecycle coverage. Moreover, meta-LGB is fitted on January itself and has a weak monetary severity head, so its positive subset has no demonstrated prospective reliability.

**NEXT R05 narrow mechanism (do not repeat R04 filtering):** Train a **joint episode-level causal first/second/recovery event model** that treats original fixed R9 complete two-leg minute cycles as protected **offline teacher identities**, and uses only independent Coinexx REAL source-event ordinals and completed M1/M5/M15/H1 structure at runtime. At each original reference episode compare three independent, matched cohorts: (a) protected original first-only profitable exits, (b) protected negative-first → positive-second recovered cycles (all 2,147), (c) original negative complete cycles, alongside the narrow 2,660 price-selection failures. Derive conditional first-passage *cash after documented R9 fee* vs adverse slippage/gap **without inserting teacher-optimal quote timestamps as runtime rules**. Build event-specific BUY/SELL/WAIT, HOLD/EXIT, and conditional REARM policies **together**, not a profitability-only gate. The fixed R9 original historical entry/exit outcome net and exact tester balance remain untouched; newly replayed REAL fills get separate side-specific cash ledgers. Re-assess EVERY original January entry and exit identity and whole-account economic continuity before another fitting stage. No additional policy or EA acceptance without one single executable model clearing all owner's January gates.

### Preservation

Compact R04 ZIP includes source C++ and Python, frozen fitted meta models, 27,980 original-reference *derivative* witness states (without source raw ticks), selected full-month candidate ledgers, 12-trial complete signed cash and matched-profit/recovery scoring receipts, source integrity manifest, and this report. R03 parent source and pretrained hazard scores are external protected inputs, not regenerated or packed as massive libraries. All other months remain untouched.


Verified R04 source kit, trained weights and full receipts: https://drive.google.com/file/d/1Mj4ufUJWeSGfaRovqUjVhO6764YUkj0L/view
