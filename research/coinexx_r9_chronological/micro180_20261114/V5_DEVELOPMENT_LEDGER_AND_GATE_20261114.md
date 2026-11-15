# Micro180 V5 — development-log consolidation and source-exact provisional gate
**2026-11-14. RESEARCH ONLY — NOT PROFITABLE, NOT MT5 CERTIFIED.**
GitHub parent branch: `carson/r9-micro180-v3-quant-objective-audit-20261114`, source commit `639e635b71664e2c3c90310679620bcc33b71865`. This does not replace the production source or freeze a new baseline yet.

## Avoid duplicating already completed research
- Original R9 60-second entry Jan–Sep 2026: **303,934 trades; -$120,212.46** modeled net.
- Four-lane 5s/15s OR dual entry Jan–Sep: **419,389 trades; -$162,656.05**. 15s basket/15s breakout present in 99.62% of accepted trades.
- Existing Micro180 source-native millisecond/Bid-Ask engine Jan–Sep: **61,258 trades; -$24,158.30**; **0/9 positive months**. A reduced TOTAL loss with an ~80% fall in trading frequency does not prove a better edge. Existing full-month original files/receipt were already verified. Do not rebuild them.
- Predeclared January Micro180 moderate and strict-persistence profiles, earlier high-volume relaxations, price-improvement V4 deferred fills, and reversal/fade probe had **negative net**. The V4 deferred 150k example: fast un-deferred 969 trades / -$358.25 versus deferred 742 / -$295.61, worse per filled trade. Do not rerun merely to recover those negative outcomes.
- Old R9 v2 failures: a 250ms teacher inverted the SELL return sign; the retired Bayesian action selector evaluated eligibility after choosing direction; order-dependent trajectories once collided into identical 102-feature representations; old AUC pertains to old entry ordinals only. V5 avoids all four by executable-side, ordered quote-state tests and never loading old AUC.
- The historical Coinexx source CSV has millisecond timestamps and source ordinal. From the first 1M quote inspection, `last` and `volume` were all zero; no real-volume or order-book claim is possible. Source-native quote-update count, coherent Bid/Ask updates, median spread, completed M1 price indicators and past subminute candles are permitted **proxies**.

## V5 implementation — new code and MT5 shadow fork
- **Reuse** existing source-native rolling 180-second `RollingThreeMinute`, actual closed 1s bars and 5s/15s/30s candles, M1 completed-bar Wilder DI14/EMA20/ATR14.
- 5s recognizes candidate. Existing 15s structural confirmation and 15/30s Bid/Ask executable-side breakout veto decide whether an entry is even considered. V5 then computes a **distinct chronology-sensitive score**, with signed completed-second 15s efficiency, **last-three-step direction**, adverse reversal fraction, simultaneous favorable Bid+Ask changes, median relative spread, 5s-versus-180s *quote-arrival* intensity, and completed-M1 indicator context. Different BUY/SELL coefficients are test hypotheses, **not fitted profits**.
- BUY scores current **Bid** relative to prior Bid closes. SELL scores current **Ask** relative to prior Ask closes. No current incomplete second bar highs enter historical breakouts; no future labels.
- Existing cash executable-side test, protective SL, 30s timeout, modeled **-$2 first-available emergency exit**, **+$0.10 net harvest**, **+$1.75 preferred maximum** remain. V5 early-adverse cut and protected runner are **independent optional** research arms. Runner may hold only after legal tighter stop protecting +$0.10 modeled net, else harvest; stop fills/price gaps are not guaranteed.
- Research MQL5 fork: `Experts/GoldMuwahahaMiner_R9_Micro180_V5_Research.mq5`, **demo execution OFF** and no production permission. It reuses native M1 `iADXWilder` and EMA, M1/M5 ATR, exact-ms `CopyTicks` quote history; V5 quote-count/spread/ordered-path logic is opt-in. No native MetaEditor compile, no Python/MQL5 millisecond parity, broker cash K/C, slippage, multi-terminal equity synchronization or profitability certification yet.
- The original `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5` and previous `Experts/GoldMuwahahaMiner_R9_Micro180_Research.mq5` are unchanged.

## First bounded causal pilot (historical source rows, NOT full month or OOS)

Original files reused read-only from prior source-verified Coinexx Jan/Sep 2026 monthly gzip. Same first **200,000 quotes per month** and K=$1 per $1 XAUUSD price move at 0.01 lot; C=$0.20 *additional cash beyond the observed spread*. No commissioned fills. Test uses `--profile fast`, a preexisting permissive structural setup; **governor OFF for isolated economics**, so it does not satisfy the 25%-account-cap deployment gate. Open at slice boundary positions are NOT booked as completed trades. Python source exact remains unchanged.

| Arm | Jan trades | Jan modeled net | Sep trades | Sep modeled net |
|---|---:|---:|---:|---:|
| Original R9 with original exits | 938 | -$343.74 | 835 | -$343.98 |
| Preexisting fast Micro180 cash harvest | 1,316 | -$491.09 | 1,682 | -$673.05 |
| V5 ordered path + first $0.10 NET harvest | 912 | -$350.04 | 1,116 | -$453.51 |
| V5 ordered path + experimental adverse cut | 917 | -$355.07 | 1,120 | -$455.34 |
| V5 ordered path + conditional protected hold | 881 | -$330.31 | 1,093 | -$449.60 |

**Neither examined sample has positive modeled net.** The V5 entry throughput is ~97% of original on January and ~134% on September *within these slices*, but the **full nine-month trade-throughput gate is NOT passed**. Early-adverse exit worsened Jan and Sep; do not promote it. Protected hold lowers Jan modeled total losses by $13.43 relative to original, yet loses $105.62 more on Sep; not a stable edge. This is evidence AGAINST broad parameter chasing.

## Acceptance criteria (must be jointly satisfied, not post-hoc retrofitted)
1. Historical source and lane/account parity: originals untouched; deterministic quote sequence and milliseconds; same-ms records preserved, no incomplete future OHLC.
2. High-volume operational target: at least **303,934 comparable filled trades** over the identical nine months, subject to spread, margin, allowed lot and 4-trades/source-minute cap; report monthly/session BUY-vs-SELL, not just total. A low-trade positive subset alone fails the owner's combined specification.
3. Economics: **positive NET after observed Bid/Ask, commission and conservative slippage**, preferably profitable by month and not driven by a rare month/session. Separate true OOS frozen windows and bootstrap intervals. Never call a negative number positive.
4. Risk: $2 per-trade intended cash loss checked at actual order creation; quote gap/SL slippage can violate realized limit. 25% from persistent start equity **and stricter prior 10% peak and 4-12% daily gross controls** across the whole account; stage at $100/$500 capital, not just ungoverned $100k research assumptions.
5. Exit test: entry-matched minimum +$0.10 NET harvest vs conditional +$1.75 runner with paired first-passage labels, Bid liquidation/Ask cover, bounded 30s risk and protective stop legality; never evaluate an old-model AUC on new entry times.
6. MQL5: MetaEditor compile + zero warnings, exact broker margin/stops/freeze/lot constraints, CopyTicks catch-up/equal-ms test, on-quote race/transaction latency, demo-only test and source-parity reports. Existing GitHub Actions Python tests **are not a MetaEditor compile**.

**Disposition: V5 engineering fork created; research pilot FAILS positive-net gate. No live/demo deployment promotion; a large in-sample threshold search would make the evidence less trustworthy.**


## 250ms chronology repair, same-source re-evaluation (2026-11-14)

**Why:** Completed 1s-close sequences alone hide intrasecond quote path order; prior R9 v2 feature collisions make this a specific known failure mode. `v5_ms_path.py` now accumulates exact source-order same-millisecond Bid and Ask movements into **at most 720 finished quarter-second bins plus an active bin**, producing an observed 5s quote-path efficiency and simultaneous-quote-direction coherence. No synthetic 250ms bars for no-update intervals; gaps >2500ms invalidate the 250ms path signal. A 180-second lookback remains available from the original `RollingThreeMinute` and the 250ms ring. The BUY/SELL path score adds **+0.12 quote-path efficiency +0.08 × (quote coherence − 0.50)** to the previous separately weighted BUY and SELL scores. Coefficients are explicit **unfitted hypotheses**.

A new `GoldMuwahahaR9Micro250.mqh` source-exact bounded ring is wired into the demo-disabled `GoldMuwahahaMiner_R9_Micro180_V5_Research.mq5` fork using `CopyTicks` source-order update. The old production R9 EA and previous Micro180 research fork are untouched. The MQL5 250ms implementation is **NOT MetaEditor compiled**, and cross-implementation indicator/structural-gate parity remains unverified; differences are expected, not concealed.

The original first 200,000 Coinexx January and first 200,000 September source quotes were replayed **without rereading or reconstructing historical tick files**. Exact same profile/assumed cost model as prior pilot. Independent 250ms cash-first and runner arms:

| Model arm | January completed trades | January modeled NET | September completed trades | September modeled NET |
|---|---:|---:|---:|---:|
| Existing fast Micro180 with cash-first exits | 1,316 | -$491.09 | 1,682 | -$673.05 |
| V5 250ms ordered-path cash-first harvest | 912 | -$350.04 | 1,116 | -$453.51 |
| V5 250ms ordered-path early-adverse cut | 923 | -$358.60 | 1,123 | -$456.40 |
| V5 250ms ordered-path optional protected runner | 884 | -$330.62 | 1,093 | -$450.24 |

A comparable prior R9 first-200k source replay completed **938 / -$343.74** January, **835 / -$343.98** September, original 30s exits. Neither V5 configuration reaches **positive** modeled net in either inspected slice. Optional early-adverse cut **worsens** both; this optional exit stays OFF. At least the research runner must later prove **>=303,934 completed trades over identical January–September** *and* positive full-system after-cost net **jointly** before calling high-volume profitability achieved. The two slices cannot certify that.

**Scope limitations:** Exposed January/September snapshots are not out-of-sample, the result is not a nine-month replay, no binding account governor was enabled in these cash-economics pilots, `K=1/C=$0.20` remain broker-unverified, and quotes are not fills. A requested $2 hard first-available exit or 25% equity governor is an **intended risk-control objective**, not an actual realized loss guarantee in gaps. New old-AUC training remains excluded.

**Verification:** local original/V5/ms source contract tests **9/9 PASS**; latest GitHub Actions original/V3/V5/250ms workflow **SUCCESS**. This is not an MT5 compile or profitability test.
