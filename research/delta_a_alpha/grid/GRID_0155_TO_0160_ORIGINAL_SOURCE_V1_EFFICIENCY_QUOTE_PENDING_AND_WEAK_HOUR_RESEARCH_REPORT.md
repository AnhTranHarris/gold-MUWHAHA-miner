# DELTA-A-ALPHA: GRID0155–GRID0160 ORIGINAL VERTICAL-GRID SCIENTIFIC RESEARCH

**Date:** October 11, 2026. **Active original branch:** `delta-A-alpha`. **Predecessor:** verified J0154. **Research scope:** *pre-L1 shadow source-quote research, no MT5 EA mutation, no funded trades, no Martingale; August 2026 remains sealed*. The original, complete V1 whitepaper, owner-ratified conversation and amendment remain controlling; **this derivative report never replaces those sources**.

## Original immutable evidence reused, never reconstructed

- Original Jan–Jul 2026 Dukascopy XAUUSD ordered Bid/Ask quotes: **57,527,562**, original J0111 GRID0108 K2/K4 source-event generation and **279,486** as-of source T1 observed entries, original Jan–Apr trained source forecast G600/R600/R120, original last *completed* H4/H1/M15/M5 structural tape, original GRID0109 **3,332** eligible weekday UTC hours and **1,389** historically weak/non-improved hours, complete months/days/ISO weeks/hours including unsupported zero cells.
- Existing full J0154 source/results: `https://drive.google.com/file/d/1mDRNK8BC_pGVeiSMXctJiP7TqQX3Pk1E/view`; J0142–0147 full completed-bar source `https://drive.google.com/file/d/1YqW0PV-mZcXfh7colUc38hULAaR7oU5h/view`; original GRID0109 source `https://drive.google.com/file/d/1f-5c6_tUOQelmJga2Yg6R1Tg-0llATeW/view`.
- All new code uses immutable original code/quote-tape dependencies in their existing working locations. It explicitly never reads the sealed August CSV. All Jan–Jul periods have been examined repeatedly and **none is an untouched holdout**.

## Newly measured cycles, every stage pre-registered before data scoring

### J0155 — Reconstructible historical quote-path efficiency (336 method-months)

Motivation: path shape might distinguish persistent movement from rotation better than a rigid H4/H1 vote. Define a *sparse four-snapshot proxy*, not a true full-tick Kaufman ER:

`ER900 = abs(delta900) / [abs(delta15) + abs(delta60-delta15) + abs(delta300-delta60) + abs(delta900-delta300)]`.

All deltas use only as-of original 15,60,300,900-second quote-history (historical quote ages <=5sec). Median ER900 = **0.6370**; 25th/75th percentiles **0.3092/0.9096** among **275,453** valid original events. Eight preregistered forecast/timeframe owners, 3 confidence levels, 2 globally shared virtual caps, Jan–Jul source T1 quote-side 120/600-second original label economics.

- Baseline original GMM five-state, confidence **0.5**, cap8: **5,585** valid quote labels, **117** originally weak hours with >=5 quotes, positive base-cost mean 7/7 historical months, but May and other stress margins thin.
- ER900>=0.35 causes R600/H600 else R120/H120 with same confidence/cap: **8,314** valid quotes, **162/1,389** old weak hours, **7/7** positive *base* monthly quote means; pool mean **+$1.963/oz**. **FAILS +$0.25 stress May** (+$0.0298 base) and June (+$0.1451 base). Gross-loss magnitude **$39,743 per-1oz marked sum** and worst quote **−$138.30/oz**; overlapping virtual marks are NOT actual account loss.
- A source code correction before final archiving repaired the `ER900_LOW25_GLOBAL600` fallback to retain the original base horizon on a nonqualifying event rather than always force H120; the final original J0155 outputs were rerun under that corrected rule. No history/engine modification.

### J0156 — Original real tick pending-source quote state with efficiency-adaptive request (84 method-months)

This is **full original Jan–Jul chronological source Bid/Ask T2 execution**, not the T1 shadow entry price. Frozen J0154 high-motion Jan-Apr model selects R600/H600 else R120/H120, strength >= source T1 spread +$0.02. A single global source-quote virtual governor cap4/8 admits PENDING source requests; first actual quote T2 no earlier than T1+1sec qualifies only if observed spread meets 0.8x/1.0x original spread before 5/10sec. When no quote qualifies, request expires and slot is released; when filled, holds until T2+horizon+10sec. Buy Ask, Sell Bid; close actual opposite side, $0.02 research fee once.

- Original frozen J0154 pending CAP8 spread<=0.8 within10sec **2,354** valid marks; **63** original weak hours; 7/7 positive monthly mean after additional modeled $0.50 per trade.
- Adaptive E: if as-of ER900>=0.65 use 1.0x spread for 10sec; else 1.0x within5sec: **2,909** valid source marks, **82** weak hours, **7/7** months positive after +$0.50 cost. Pooled hypothetical mean **+$4.247/oz** *before* extra cost. Mean and quote count are **not** broker PnL; gross negative marked sum rises to **$17,485/oz equivalents** and worst source quote **−$120.90/oz**.
- **Critical ablation:** the *simple static* cap8 original method 1.0x spread within10sec from earlier J0154 / replicated J0158 produces **2,956** marks, **82** old weak hours and mean **+$4.223/oz**. Thus the adaptation is **not shown to outperform the simpler static policy on meaningful density/support**, despite better results than the originally compared 0.8x policy. Do **not** promote the ER timeout as a new edge solely on that comparison.

### J0157 — Combine wider ER signal owner with actual T2 quote confirmation and one shared governor (84 method-months)

Three predeclared signal owners ×2 quote policies ×2 caps ×7 months; all causal Bid/Ask T2 entries and source opposite-side exits. The wider ER900>=0.35 at confidence0.5 + adaptive quote wait cap8 produces **7,491** completed quoted observations, **149** original weak hours and pooled mean **+$2.227/oz**, but **only 4/7 historical months remain positive after additional +$0.50 modeled execution cost**. April +$0.112 base, May **−$0.080** base, June +$0.395 base. Gross loss rises to **$36,074** per 1oz quote-summed units, worst −$138.95. Higher velocity is **NOT** qualified improvement.

Five-state confidence0.5 + static 0.8x quote wait cap8: **3,755** quoted observations, **83** weak hours and **7/7** +$0.50-positive months, but insufficient coverage / adverse concentration. The original source T1 forecasts were frozen; no R9 synthetic results supplied side or parameters.

### J0158 — Source-quote entry PRICE-LOCATION and wrong-direction T2 detection (336 method-months)

Frozen J0154 owner, real quote after1sec, source spread<=0.8x or1.0x, waits5/10sec, shared caps4/8. At first actual quote meeting spread, additional as-of price-location requirements test original-grid signed displacement: any, signed<=0, signed<=-0.25G, signed>=0, signed>=+0.25G, signed abs<=0.25G (6 categories). Chronological exact Ask/Bid T2 entry, future opposing quote at actual entry+horizon. No fictitious limit fills.

- The **unfiltered static** 1.0x spread/10sec/cap8 already produces **2,956**, **82** weak hours, **7/7** positive monthly means after +$0.50 cost; worst quote **−$120.90**.
- Requiring improved price (signed quote movement <=0) reduces to **2,514** valid, **72** weak hours, while improving mean from **+$4.223 to +$4.570/oz**. The apparent improvement comes with **−442 quoted opportunities** and **−10 weak hours**, and gross losses remain substantial. No demonstrable whole-system improvement. More restrictive retest/reacceleration is **not a major new breakthrough**.

### J0159 — H4/M5 transfer + frozen global/R600/Q120 forecast expert disagreements (140 actual method-months)

Five predeclared owners (GMM baseline, global vs role forecast agreement elect long, disagreement elect long, fully completed H4/M5 transfer as role switch, hierarchical global/role/original T1 sign agreement) ×2 source confidence ×2 spread ratios ×2 single global virtual caps ×7 months **= 140** combinations. Note: the original GitHub prereg prose miscounted its factorial combination as 280; experimental source and result contain all **140 actual** preregistered Cartesian settings, with no unregistered settings.

- Original five-state 1.0x confidence and source spread<=1.0x/10sec/cap8: **2,956** real quoted results and **82** weak hours, 7/7 months positive after +$0.50 cost.
- Completed H4/M5 transfer owner, same confidence/quote wait/global cap: **2,492** quoted results, **63** weak hours; quoted mean **+$5.025 vs +$4.223** and 7/7 positive after +$0.50, but worse opportunity coverage. The increase reflects restricting/altering selection, not proof of superior whole-system execution.
- Global/role sign agreement, confidence0.5, 1.0x/10sec/cap8: **6,202** quoted results, **120** weak hours, pooled **+$3.435/oz**, but only **6/7** months remain positive after +$0.50 and total gross losses **$34,922** with worst **−$135.01**. Again, expanded supply sacrifices month robustness.

### J0160 — As-of structural/regime/efficiency correlation research and denominator scope

Pure EXPLANATORY source cohort analysis, not trade rule or independent strategy proof. Compare frozen role600 bidask-quote label across existing causal Jan-Apr five-state motion regimes, completed H4/M5 agreement, DST-aware session, K2 vs K4, ER path buckets, forecast sign disagreement and original retrospectively marked weak-hour cohort. Source month/day/hour untouched.

- **Five-state high-motion regime** represents **18,622/279,486** source T1 events; frozen R600 source label mean **+$1.173/oz** *all months combined*, while the other **260,864** event labels average **−$0.331/oz**. Crucially, high-motion performance is **negative in April, May and June** by standalone month. Regime detection alone does not certify positive expectancy or replacement V1 Watchdog.
- Original previously weak-hour-mapped cohort **112,660** T1 events, mean observed T1 spread **$0.763/oz**, ER900 mean **0.5867**, frozen source R600 label mean **−$0.367/oz**. Other mapped eligible hours **163,196** T1 events, source spread **$0.789**, ER900 mean **0.5926**, R600 label mean **−$0.151**. **Weak-hour failures cannot be attributed to wider average spread or much lower ER alone.** The *combined* session/regime/structural interaction remains unresolved.
- Full source q contains **3,630 additional T1 entries outside original GRID0109 3,332-hour reference**, including **3,446 weekend-labelled source events**. These source observations are NOT deleted or declared untradeable; they are kept in raw research and the all-events quote markout, but **must not silently be counted as original weak-hour successes**. All 3,332 reference-hour ledgers were preserved separately. A derived benchmark-eligible-only re-score confirms the basic tradeoff: for J0156 adaptive E, **2,787** of **2,909** source marks fall into original eligible hours, and the seven after-+$0.50 original-reference monthly means remain positive; J0157 ER wider owner had **6,413** of **7,491** in reference hours and failed after-+$0.50 robustness in April/May/June. No destructive replay/rebuild required.
- Session and efficiency correlations are **descriptive, selection-biased, and based on overlapping event labels**; no causal advantage can be concluded from Pearson/Spearman or retrospective original weak-hour stratification.

## Stress/certification and reproducibility

- Original native source chronology used for J0156–J0159; *real source quotes* are not actual **Coinexx MT5 broker fills**. +$0.25/+0.50 are *hypothetical additional* per-quote execution-cost stresses, not measured Coinexx slippage. Source quote outcomes are in **USD per ounce equivalent**, not actual 0.01-lot account PnL.
- **10/10** locally rerun deterministic test assertions across new source quote side, 1-second timing, pending timeout, portfolio cap, original reference-hour invariance, and frozen prior J0154 source-quote parity; original J0154 method reproduces **exact per-month 2,354 marks and mean**, no quiet mutation of prior science. J0155 ER900 fallback-horizon correction rerun and output archived.
- **May–July day-block bootstrap** over **66 distinct original eligible weekday UTC reference days**, 2,500 seeded resamples of day clusters, NOT per-tick IID: adaptive J0156 E extra+$0.50 mean **+$0.857/oz** with quote-day interval **[−$2.399,+$3.727]**, crossing zero; broad J0157 E extra+$0.50 mean **−$0.027/oz**, interval **[−$1.506,+$1.333]**. Null not excluded. See `day_cluster_qa.json` for all predeclared comparisons and exact RNG seeds.
- No strategy under J0155–J0160 provides the owner's >=75% original R9 SYNTH **qualified executable CLOSED trades on same day**, robust hourly/weekly/monthly account economics, small-account $100–300 survival, protected capital heat, real Coinexx fill parity or independent unseen out-of-sample certification.
- All original experimental source Python, full per-month candidate panels, every original 3,332-hour weak/unsupported panel, UTC days and ISO weeks, source-quote path/cap tests and root-cause group results are included in the accompanying new archive. The upstream original frozen source quoted ticks and existing predecessor quote-tape files remain in their canonical artifacts; their exact dependencies are listed in `REPLAY_README.md`. August sealed.

## Constructive next question, based on measured failure rather than optimizer fantasies

**GRID0161**: An *entire V1 state-qualified opportunity owner* must simultaneously identify a regime where a structural forecast has defensible directional expectancy, create additional **independent** executable opportunities in otherwise unsupported hours, and limit gross adverse excursions and shared portfolio capital heat. Pure spread-threshold gating, Kaufman-style sparse path scores, and lone rigid H4/M5 permission increase either quote average or support but fail the complete constraint set. A Watchdog must identify *both* regime and as-of economic specialist reliability; regime labels alone were not stable profitable controllers by month. Do not open August without explicit owner authorization or activate the EA/L1-L7 outside owner governance.

## Reconstructible public research concepts (not proof of edge)

- MetaQuotes reconstructible adaptive regime grid, CUSUM/trend-vs-range: https://www.mql5.com/en/articles/21833 . **Its equity-based sizing is not imported because the owner prohibits loss-dependent sizing/martingale.**
- Public source Kaufman Efficiency Ratio illustration: https://www.tradingview.com/script/dneYi7kK-Efficiency-Ratio-Kaufman/ . Our sparse 15/60/300/900s proxy is NOT its source-exact full-bar or tick ER.
- Trading community risk of overstating bursty selected subsets and regime overfitting: https://www.reddit.com/r/algotrading/comments/1rgbu23/how_to_deoverfit_a_bursty_intraday_strategy_that/ . These provide research questions, not measured XAUUSD trade profits.
