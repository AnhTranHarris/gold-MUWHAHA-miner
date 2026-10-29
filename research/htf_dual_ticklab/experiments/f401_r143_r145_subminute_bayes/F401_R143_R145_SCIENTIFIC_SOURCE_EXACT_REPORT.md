# F401 — R143/R144/R145 SIX-CLOCK DIRECTIONAL MT5 GRID + ONLINE BAYESIAN RESEARCH

**Date:** 2026-10-29  | **Classification:** UNAPPROVED RESEARCH, no MT5 demo/live authority.

## Governing owner priority (non-negotiable)

**INCORRECT / OPPOSITE and NEUTRAL are the rejection population. CORRECT signals are a protected class with a hard false-veto budget.** No symmetric classification accuracy objective. The >400,000 originally incorrect+neutral rejected against <10,000 originally correct lost is an aspirational historical structural objective across the exact eight Coinexx/Dukascopy cells. All original G01–G09 whole-EA gates remain OPEN. M-DK-01 remains OPEN; owner research-stage historical 21/39 approvals are unchanged.

Research source-governor v1.4 and amendments 1.5-A1/A2/A3, full four-month original forensic log, original 39 objective checklist, active MT5_EXPAND continuation ledger and October 28 default human correction were reread this run. No original replay engine or immutable source was rebuilt, and the PRIMARY Drive was not written.

## Why this was not another slow-clock experiment

Decision features use native XAUUSD bid/ask and the existing **250ms / 500ms / 1s / 5s / 15s / 30s** source-exact 92-dimensional R120/R136 geometry. The evaluated reprice distance derives specifically from the **completed 250ms and 500ms candle high/low log-range** plus strictly prior bid/ask spread. Side +1=BUY, -1=SELL in both decisions and exit marks. **M1/M5/M15/H1 were not used for candidate inference.** MT5 custom subminute EMA8/21/55, Wilder ATR8/21, plus/minus DI/ADX proxy, Bollinger displacement, KAMA adaptive average, confirmed swings, and quote-arrival/intensity kernels are already present in the preserved R136 `.mq5` parent. Native `iATR`, `iMA`, `iADX`, `iBands`, `iAMA` handles cannot supply custom subminute periods via standard `ENUM_TIMEFRAMES` directly; the mathematical indicator kernels must update from the actual recorded subminute candles and later pass MQL5 numerical parity. Quoted bid/ask updates are NOT traded volume or true order book imbalance.

## Authentic source population and clocks

Source registry eight **verified original gzip compressed raw source SHA256** per original R136 source pins, source snapshots/quotes and original t0+30–32s class aligned to original F395 event masks. Original immutable totals: **2,574,251 source events** = **1,208,071 CORRECT**, **1,064,545 OPPOSITE**, **301,635 NEUTRAL**. Eight-cell R143 full masks recount with exact original event ID, t0 millisecond, direction, original label and F392 baseline equal to original source data, no differences. Coinexx Jan/Feb timestamp adjustment -120 min; June/July -180 min; Dukascopy UTC unchanged. No future-derived field in decision state.

## R143: actual native-quote delayed-intent and executable-side repricing test

A NEW never-sent original intent is observed at d=t0+15,000ms. Its price/grid are computed from strictly pre-d source quotes and the *existing original source* six-clock publisher, not a new replay. Quote staleness maximum 300ms, assumed order activation delay 150ms, passive-entry window seven seconds, time horizon 30 seconds after fill, close on first quote at/after expiry no more than 300ms late. BUY entry/liquidation sides ASK/BID, SELL BID/ASK respectively. Market benchmark entry at first native tick after 150ms; passive BUY is only eligible when future ASK <= fixed buy limit, passive SELL only when future BID >= fixed sell limit. The favorable quote crossing is still **not a verified order fill**: passive queue, MT5 broker state, execution throttles, slippage, market impact and portfolio capital are unknown. Gross/quoted net is per 1 XAU ounce; an explicit **assumed $0.20/oz charge** is subtracted from closed quote-crossing opportunities, but exchange/broker realized fee schedules are not certified. An additional uncalibrated sequential signed-Gaussian likelihood-ratio cancellation diagnostic was used (threshold 2.4) for passive policies; it is NOT a claimed Bayesian original-error filter.

Predeclared entry modes: P0 market at fresh post-latency quote; P1 half-spread improvement; P2 full-spread improvement; P3 full-spread plus 0.25×fast completed quote range; P4 full-spread plus 0.50×fast range, capped step $1.50. No June/July label-driven parameter tuning.

### Full eight original cell independent recount

| Mode | Quotes crossed (not fills) | Completed 30sec future bid/ask markouts | Closed trade quoted net after $0.20/oz |
|---|---:|---:|---|
| P0 market control | 1,801,981 | 1,384,226 | **Negative in 8/8 cells** |
| P1 half-spread | 986,361 | 806,743 | **Negative in 8/8 cells** |
| P2 full-spread | 684,494 | 577,990 | **Negative in 8/8 cells** |
| P3 quarter microgrid | 486,472 | 415,132 | **Negative in 8/8 cells** |
| P4 half microgrid | 353,142 | 303,303 | **Negative in 8/8 cells** |

For P0, mean quoted post-cost per completed event ranges **−$1.296/oz to −$0.198/oz** across eight cells. For P3 it ranges **−$1.735/oz to −$0.360/oz**. Among original t0 labels, merely treating P3 nonfills as vetoes would destroy **1,051,391 original correct** to suppress **1,036,388 original incorrect+neutral**—catastrophically violating correct protection. Therefore NO nonfill/reprice status is relabeled original wrong-veto success. This falsifies the naive unconditional passive-wider-grid hypothesis under the quote-cross proxy.

### Per-cell comparison P0 and P3 (mean net quoted $/oz per complete price path)

| Source | P0 valid markouts | P0 mean net | P3 valid markouts | P3 mean net |
|---|---:|---:|---:|---:|
| DK Jan | 163,879 | −0.7014 | 26,744 | −0.9088 |
| DK Feb | 129,562 | −1.2960 | 26,386 | −1.7347 |
| DK Jun | 131,422 | −0.8374 | 21,750 | −0.9924 |
| DK Jul | 121,877 | −0.8723 | 12,948 | −0.9849 |
| CX Jan | 217,569 | −0.1980 | 84,911 | −0.3605 |
| CX Feb | 200,740 | −0.4115 | 89,610 | −0.7188 |
| CX Jun | 222,178 | −0.4166 | 84,817 | −0.5450 |
| CX Jul | 196,999 | −0.3942 | 67,966 | −0.4965 |

This is a per-intent counterfactual diagnostic, NOT shared-account aggregated PnL: source opportunities overlap enormously, fill availability/queue effects missing, and large broker spreads/quote gaps matter. The hypothesis fails even under optimistic quote-cross semantics; do not promote.

## R144 distinct economic Bayesian feasibility screen: FAILED, parked

Jan first60% **FIT**: source-specific predecision 250/500ms/1s side-aligned directional state, bid/ask spread and quote activity, six-bit regimes, separate five passive/market policies; day-level clustered mean economic value receives a four-pseudo-day shrunk mean and 99% Student-t lower confidence boundary (Bayesian-inspired empirical-Bayes screen, **not** a rigorously calibrated posterior guarantee). Require >1,000 filled crosses, >10 training days and positive conservative net per original intent; independent Feb61–78% CAL further requires >=500 completed quote paths and positive economic mean. Freeze without using June/July. **0/10 source×policy families** found any qualifying January FIT regime and **0/10** passed independent Feb CAL. June/July candidate admissions consequently ZERO. No unapproved strategy re-optimization; failed subgroup family retained.

## R145: genuinely different online Bayesian directional regime mechanism

**Executable source implemented now:** bounded Gaussian mean-conjugate **Bayesian Online Change Point Detection** on actual quote-populated completed subminute candles, with 32 run-length states per clock and six independent clock publishers. This is NOT the earlier R139 categorical Dirichlet phase/renewal proxy; it maintains a posterior over **run length since latent change** for directional normalized midprice increments. Each real closed candle supplies a new signed innovation, with BUY/SELL inverted, quote-price range and spread robust normalization, Gaussian predictive likelihood, constant predeclared hazard prior 1/64, finite-state truncation, and normalized change/growth transition. Outputs are joint run-length, immediate adverse vs favorable next quote innovation (not original incorrect signal), quiet probability, and regime change probability. No fabricated volume, no synthetic empty candles, no future-price information in inference; prefix mutation and direction sign tests protect time causality. Class-calibration against original CORRECT/OPPOSITE/NEUTRAL and a frozen high-confidence correct guardian are **NOT completed**. No current original labels in the runtime kernel. No veto mask or claimed alpha yet.

**Code proof:** Python R143/R145 deterministic tests **10/10 PASS**. Research smoke on first **100,000 ACTUAL original June bid/ask native ticks** per broker, both directional sides: DK 2-side total 2.349 seconds ~85,148 quote/side updates/sec; Coinexx 2.294 seconds ~87,197 quote/side updates/sec. This is a Python runtime throughput proof on a local environment, not MT5 MetaEditor performance or sustained whole-bot HFT throughput. An independent MQL5 research-only include adapter with explicit Gaussian BOCPD state and six-clock entry point is supplied; **UNCOMPILED, Python/MQL5 numerical parity not proven**, no OrderSend.

Representative final-prefix conditional quote probabilities (NOT original wrong-signal probability): DK BUY adverse .3861, favorable .3462; DK SELL adverse .3462, favorable .3861. CX BUY adverse .3692, favorable .3628; CX SELL adverse .3628, favorable .3692.

## Next R146 scored research specification — genuinely different information and economics

1. Reuse original six-clock publisher, native quotes and 32×6 BOCPD state *from tick prefixes* at t0+250ms, +500ms, +1s, +2s, +3s, +5s, +8s, +10s, +12s, +15s, **fresh horizon-specific as-of state**. Do not recycle R139's +15s grid context at earlier horizons.
2. Estimate three explicitly separate targets: **OPPOSITE FIRST-PASSAGE** hazard, **NEUTRAL NO-TOUCH** hazard, and **CORRECT SUCCESS** survival; include 250/500ms ATR/EMA/KAMA/ADX/Bollinger, confirmed multi-bar SR/fractal and directional structural grid/phase-locking observations. Use source Jan early FIT, Feb later CAL, freeze JuneJuly historically exposed, then truly new G08 month before deployment. Correct guard is an inviolable budget, not a soft regularization weight.
3. Couple an **online continuation-vs-cancel-vs-enter limit** Bellman policy to both quote-touch fill probability and conditional post-fill adverse movement. A valid strategy must beat costs and broker spread separately per source, side, UTC session, and $100/$200 shared capital. Stop immediately if action-time net value and original correct-loss constraint cannot both be satisfied; no weak low-volume mechanism promotion.
4. Demand original full eight-cell masks including correct/opposite/neutral, incremental bad per correct, original R9 hour/day/week/month supply, MT5 native compile/prefix numeric parity, G05–G09 economics/risk/virgin data. Preserve exact original 2,574,251 denominator and R138 privileged benchmark **408,180 bad/9,974 correct** without calling it causal t0 or economically deployable.

## Source/technical references and hard limitations

Governor v1.4 + amendments 1.5 A1/A2/A3; original forensic log and checklist; October 28 default work directive; active MT5_EXPAND continuation ledger. Existing original eight raw source gzip tapes are **not** embedded in the portable package; exact SHA registry defined in included R143 source and checked on use. R120/R136 original source publishers remain untouched, dependencies reused. No native iMA/iATR handles on subminute ENUM_TIMEFRAMES: formulas custom on quote bars, MetaEditor parity gate open. Technical inspiration: Adams & MacKay BOCPD 2007; https://github.com/fiannai/bocd ; MetaQuotes official `CopyTicks`, `MqlTick.time_msc` https://www.mql5.com/en/docs/series/copyticks . No outside strategy/code imported. MT5_EXPAND `/02` and PRIMARY remain untouched. No self-approval, no owner checklist promotion.

## Local complete source package

Package includes all 40 complete original-event counterfactual policy NPZs, independent mask recount, all 8 source per-original-event receipts/feature hashes, R143 candidate Python and deterministic tests, R144 economic block guard negative results, R145 Python Gaussian BOCPD and both-source 100k-prefix smoke, research MQL5 header, and scientific report, plus member-level SHA256 manifest. The full raw source tapes and full precomputed 92D caches are excluded and SHA-pinned; no archive claims execution without those dependencies.
