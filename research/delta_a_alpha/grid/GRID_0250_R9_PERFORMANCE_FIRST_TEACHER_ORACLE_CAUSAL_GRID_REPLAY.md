# GRID0250 — R9 SYNTH goals, R9 OVERFIT optimal-trade roadmap, cumulative GRID research

**FIRST AND CONTROLLING RULE:** R9 SYNTH is the performance goal. R9 OVERFIT shows retrospectively optimal trades, not causally executable instructions. R9 REAL is the historical failure control. Independent Dukascopy Bid/Ask quotes are the research execution path. Do not use any OVERFIT future-outcome score during grid order decisions. No calendar month runtime features.

**Governance:** `delta-A-alpha` only, J0183 unchanged, trading disabled; original frozen Vertical V1 remains unaffected. Fixed 0.01 lot research hypothesis; no Martingale, no loss-dependent scaling. August 2026 sealed. Historical Jan–Jul is previously inspected, not blind out-of-sample. This checkpoint RESEARCH ONLY, no strategy promotion, no R9 financial parity certification.

## Locked-category progression

1. **NET PROFIT FIRST.** Require chronological real Bid/Ask fully executed trade ledger with positive net in every observed week and month, then progressively climb to the original R9 SYNTH **FULL monthly and weekly net** using frozen `GRID0250_R9_SYNTH_FULL_MONTHLY_WEEKLY_NET_TARGETS.csv` (7 MT5-server calendar months + 31 MT5-server ISO weeks, total +$309,122.85, 219,342 completed trades). Newly discovered settings must be causal, reconstructible, not month-aware, and carried forward cumulatively. Volume is monitored as a viability constraint because hypothetical 12 winners do not reproduce R9 trading throughput.
2. **GROSS LOSS SECOND.** Once net thresholds are met on a common, economically valid execution basis, reduce gross loss without sacrificing the net-profit lock or minimum velocity. Do not change lot sizes after losses. 
3. **MAX DRAWDOWN THIRD.** After net/gross-loss locks, reduce full-tick cash/equity drawdown without regressing prior locked gates. **Safety/margin/liquidation guardrails remain binding at every stage**, not deferred until drawdown optimization.

Original R9 REAL tested Jan–Jul −$50,285.28 despite 236,647 trades: synthetic teacher's path cannot be assumed broker-executable.

## Original source provenance

Original teacher corpus root: https://drive.google.com/drive/folders/1ES78vXb2mFsOsa50BiwCLsT6BXgLe-Oe (PERSONAL Drive). Real/synth paired teachers, causal preentry features, in-sample overfit scores, original native quotes, original analysis, hashes all preserved; see `research/delta_a_alpha/grid/R9_SYNTH_OVERFIT_CORRELATION_CYCLE_ROADMAP_RECOVERED_20261012.md`. R9 MQL5 original source: `carson/mt5-r9-hybrid-gate-certification/Experts/GoldMuwahahaMiner_R9_HybridGate.mq5` (gap 0.30, SL0.30, trail activation0.10, trail gap0.03, hold30s, max 3 rearm/minute, 10s efficiency and volatility gate and spread cap, point/digits broker dependent). The original source was inspected, **not** copied verbatim into our reconstructed raw-price G0.

Original correlated pairs: 165,630 SAME minute, side, ordinal RESEARCH SELECTED pairs, not exact same fill. SYNTH 17.73s median hold vs REAL 2.995s; at 20sec 43.14% vs4.73%; REAL 3.1× internal movement per identical M1 envelope; OVERFIT model AUC in-sample, not validated. OVERFIT teacher score alone left REAL net negative; selected positive path conditions were small retrospective subsets, not tradable net proof.

## Experiments — full 15,803,735 April+May original Dukascopy quotes

**Scope:** Original 136B first-touch price-grid source, highvol/Asia as-of; fixed 0.01 lot→1oz RESEARCH assumption, 250ms latency with observed actual quote and at most 1s stale, bid/ask execution and 0.20 vs0.52 per close fee stress, separate hypothetical cap16 accounts, 1 order/s, actual observed stop0.30/trail activation0.10/trail gap0.03/hold30s. April+May continuous quote files, UTC grouping (NOT VERIFIED R9 MT5 SERVER). Distinct new variants do not share a balance; not a deployed integrated active V1, and no additively combined profits. This is NOT the original source's full faithful executed R9 EA replication.

### Cycle 1 (causal side/entry features, R9 fixed stops)

| Hypothesis | Closed at cost $0.20/oz | Net source USD/oz at $0.20 | Profit-positive UTC weeks |
|---|---:|---:|---:|
| A: 136B crossing in original direction | 17,686 | −15,376.503 | 0/9 |
| B: preentry compact 15s path (`range<=0.76` contaminated oracle-inspired boundary: NOT PROMOTABLE) | 1,073 | −897.497 | 0/9 |
| C: preentry path efficiency ≥0.35 and compactness | 3,350 | −2,792.844 | 0/9 |
| D: actual observed 2s acceptance, original direction | 8,966 | −7,783.313 | 0/9 |

### Cycle 2 (observable auction failure, corrected spread lifecycle)

| Hypothesis | Closed at cost $0.20/oz | Net source USD/oz at $0.20 | Profit-positive UTC weeks |
|---|---:|---:|---:|
| E: 2s actual failed break, fade | 8,704 | −7,600.413 | 0/9 |
| F: 2s directional acceptance >spread+0.10; stop/trail adapted to observed entry spread, 60s | 2,424 | −2,173.170 | 0/9 |
| G: low-efficiency failed auction fade | 970 | −854.117 | 0/9 |
| H: completed H1/M15/M5 directional state + 2s accepted crossing + spread-aware stop/trail | 1,497 | −1,344.225 | 0/9 |

All 8 remain negative at cost $0.52 too. These studies use already-inspected months and hand-picked mechanistic hypotheses; no OOS claims. Their failure does NOT refute historically selected positive March135/April136G mechanisms which have not been faithfully reconstituted as original as-of source+parent genealogy.

### Cycle 3 (TRUE hindsight oracle upper bound, NOT causal trading)

For 25,953 candidate delayed entries (distinct when both 5s/15s preentry observations available), choose favorable direction and best possible Bid/Ask 30-second exit AFTER seeing future, let every profitable event trade with unlimited capacity and ignore losers. This is **our separate research oracle**, NOT the actual historical R9 OVERFIT model or original R9 strategy. It yielded: April +24,022.63, May +17,397.56 USD/oz as positive-excursion fantasy ceilings, below R9 SYNTH original April +38,353.96 and May +29,545.35 account USD. **Those prices/currencies/feeds are not directly comparable.** Within this narrow 136B source, 30s horizon and 1oz scenario, even perfect foresight does not approach the 100% economic target. More independent actual campaign-generated opportunities and feasible exits are essential. Raw 26,278 candidate sources Apr+May cannot reach full R9 60,671 completed Apr+May trades by at most one trade per source event.

### Cycle 4 (mathematical stop/spread incompatibility)

Across the 25,953 executable-delay events, median original DUKA spread=$0.63; **98.98%** entry spreads exceed R9 nominal $0.30 stop; **98.3%** stop within 2 seconds in this literal simulated stop lifecycle; median holding time=0.101s. None of the reconstructed fixed-stop variants can reproduce R9 SYNTH's 17.73s median hold while such spreads dominate. The archived original Coinexx R9 feed had much lower typical entry spreads (~$0.18–0.19), and original MQL5 had broker-stops and spread gates; blindly transplanting price distances to DUKA is NOT faithful execution parity. F/H spread-adapted experiments were also negative; widening stops alone fails.

### Direct ORIGINAL R9 OVERFIT crosswalk (April SOURCE ONLY)

Downloaded exact original archived April `R9_REAL_TO_SYNTH_TEACHER_PAIRS_2026-04.csv.gz` and `...TEACHER_SCORES_2026-04.csv.gz` from PERSONAL Drive. One-to-one match of independent original 136B event and original *selected R9 REAL teacher pair* based on same side and ±5s found **900** preliminary pairs (6.46% of 136B events, 3.76% of selected R9 teacher pairs); **877** support fresh entry-quote simulation. In those 877, original R9 SYNTH historical win label 91.79%, original R9 REAL original win 47.32%, reconstructed DUKA R9-geometry G0 win .68%. Original teacher best-trade OVERFIT win-score correlation to DUKA reconstruct G0 PnL **−0.0111**, effectively none. Strong same-time/same-side count constraints and independent feed, clock and original strategy differences prohibit treating these as same trades or transferring any classifier. This IS a recovered teacher-correlation audit, not old generic price-grid sweep.

## Real engine integrations (completed)

`v1_r9_cycle_fingerprint.py` now in existing GitHub `delta-A-alpha/research/delta_a_alpha/implementation`: O(1) per-tick ring buffer update of preceding 30s observations, as-of 5-second path efficiency/turn count, 15-second range, true observed spread to original stop ratio, and no teacher scores. `v1_grid_strategy_source_router.py` now attaches this read-only `cycle_fingerprint` to each G0 event AT ITS CONFIRMED AVAILABLE TICK (including any pending event released later); never backdates the fingerprint. It cannot authorize or fund an order. **Existing executable `FourSessionV1` still separately instantiates `CooperativeGridGenesis`; this research router is not claimed to be the whole-funded execution engine.** Local grid stage full 63-test suite PASS. A fast 2.4m-token full source quote replay with new feature is not yet performed; unit tests alone do not establish full performance parity or speed under extremely dense quote feed.

## Scientific rejection decisions and next reconstructible work

1. **Reject blind literal $0.30 R9 stop on $0.63 spread**; do not fabricate prices. Recover exact original Coinexx stop/freeze/point/broker-rejection details and map original historical SYNTH/REAL clock + Bid/Ask. Expose execution quote spread and spread floor to causal source stage with explicit broker validity.
2. **Recover ORIGINAL R9 parent bracket + true physical rearm cycles** (same-minute max3, OCO, close->rearm) and surviving March135/April136 native session/high-volume source, instead of treating one virtual 136B first-touch as an entire R9 trade cycle. An accepted G0 signal is NOT a funded entry. Include true 1–2sec state management and 15–30sec harvest conditional on real continued favorable movement.
3. **Run real teacher crosswalk on entire 149-day non-selected ORIGINAL SYNTH+REAL ledger** (not only side/minute selected teacher pairs); train only on PAST months, try successive walk-forward, no month labels or in-sample OVERFIT gates. Offline label 3/5/15/20/30s first-passage, survival, favorable MFE and reversal, but no oracle state at execution.
4. **R9 REAL / DUKA feed mismatch is not an alpha indicator.** Evaluate cross-feed portability via same sampled price regimes and effective cost-to-achievable-excursion metric before any strategy promotion. Independently test structural state from last completed H4/H1/M15/M5, real tick entry paths, and physical campaign ownership; selected historical research positive streams remain controls, not code imports.
5. **Next opportunity generation hypotheses:** (i) spread-safe broker-realized bracket and real recross paid-rearm; (ii) completed-HTF/high-volume session plus 250ms/1–2s cost-normalized auction acceptance; (iii) micro-auction failed-break with 5–30s path improvements and first-pass reward; (iv) shift to genuine event-time directional-change state to separate REAL churn from SYNTH clean path, rather than adjusting R9 teacher score. All must be tested against matched baseline positions with real Bid/Ask after costs. Directional-change event-time research: https://link.springer.com/article/10.1007/s10462-022-10307-0 . MT5 OnTick tick-coalescing document: https://www.mql5.com/en/docs/event_handlers/ontick (a Python replay of every logged tick is not automatic parity to MT5 OnTick handlers).

**NOT ACHIEVED:** 7/7 positive REAL-executable months, 31/31 positive R9-benchmark weeks, or each period net ≥100% of R9 SYNTH. No broker-funded realistic Coinexx ledger; no proven small-capital survivor; no source promotion. New code is a *causal observability* improvement, not an edge. Do not claim recurring research happens automatically after this response.

## GRID0251 — 57.5m tick stateful-cycle economic result (not promoted)

**Read first before any further R9-cycle hypothesis optimization:** [GRID0251 seven-month economic research](./GRID_0251_R9_OVERFIT_STATEFUL_REARM_TRUE_COST_RESEARCH.md) and [complete executable code/test/evidence ZIP](https://drive.google.com/file/d/1hNfYj5OS8XUizSgSXwJoExYoxoiWgbGQ/view?usp=drivesdk). Original R9 SYNTH is performance benchmark and R9 OVERFIT is retrospective optimal-trade teacher, never a causal entry feature. Newly reconstructed causal single-position three-rearm-per-minute true BidAsk stream produced 252,048 Jan–Jul source-quote positions vs R9 SYNTH 219,342, but **−$231,139.50** hypothetical 1oz result (signed midpoint +$2,886.00, two-sided spread −$183,615.90, modeled $0.20 fees −$50,409.60); **0/7 source months and 0/36 represented UTC weeks profitable**. Capital-funding assumption INVALID past protective stop threshold. Distinct as-of completed-minute long-runner −$95,175.07 /100,728 closes; no profitable months. OVERFIT-perfect-future 30/90s exit/direction oracle is a hindsight upper bound, not alpha. The current G0 source/cycle cannot be promoted. Scientific J0183, original March/April positive sources, and August sealed unchanged.
