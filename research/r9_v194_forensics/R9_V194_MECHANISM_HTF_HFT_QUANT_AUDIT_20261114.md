# R9 v1.94 — Source-exact entry, holding, exit and AUC economics audit

2026-11-14. STATUS: FORENSIC AUDIT AND RESEARCH DESIGN, NOT AN EA UPGRADE AND NOT CERTIFIED PROFIT.

## Immutable source
Actual MetaEditor-compiled 1076-line standalone MQL5, Experts/Advisors/GWM_EA/r9_v1_94.mq5, Git blob 0186de6ff624294c617e3aea95cf9b0caa8202b2, original commit 813baf96f2b381be5fc7896aac8b08a966114948. Audit branch starts from that exact commit and adds only this document. Critical R9 v1.90 rollback commit 8729a6345655a7b4ea31facc81982004ee2b8921. None changed.

Original archived high-AUC model: LightGBM, 95 trees, 155 exact as-of Coinexx features = 14 original context +25 HFT +77 event-time +23 quote state +11 barrier analytics +5 action metadata. Mean May–Sep retrospective AUC **0.738513 for both action sides pooled** and **0.723175 for the ORIGINAL R9 entry direction**. Important distinction: the model label is a FIVE-SECOND hypothetical first-passage success event, not R9 realized after-cost net cash or probability of holding a runner profitably. Final Jan–Sep all-in-sample model SHA256 09e1f1b9514dd18bbf6966055e2c277da3695d43cd4c861f997f5ad2c5d75b2f. NO retrospective OOS metric for final all-month fit. Source: high-AUC model integration README on GitHub branch carson/r9-v194-m60-155-model-integration-20261113.

## Exact entry anatomy — source lines 869–946
A new minute creates a BUY and SELL threshold at midpoint plus/minus $.15 XAU quoted price; total bracket width $.30. Threshold BUY fires when ASK >=upper, SELL when BID <=lower. Gate requires completed M5 ATR(14) exceeding session-specific minima ($1.75–$2.50), quoted spread <=25 symbol points, and S1 causal Bid 10 observed-second quality: signed displacement >=$.15, path efficiency >=.70, observed range >=$.50, turns <=9. Completed seconds need NOT be consecutive wallclock seconds in source, so stale evidence is a plausible risk after quote droughts. M5 ATR is old regime; original bid path is short-term trigger.

OpenTrade defaults to .01 lots, market BUY Ask/SELL Bid, SL BUY from current Bid−$.30 or SELL current Ask+$.30; broker minimum may widen. No fixed take profit. This is a **one-minute threshold breakout + short impulse confirmation + same-minute opposite-rearm** mechanism, NOT passive bid-ask spread market making. InpR9M1RescueEnabled=false (shadow indicator observations only).

## Exact hold and exit anatomy — source lines 837–867, 1034–1057
At actual broker fill time+30sec, request market exit. Independent 1-second timer attempts overdue closes; neither timer nor market close assures execution at precisely 30sec on quote gaps. Original trailing activates after Bid−BUY fill >=$.10 or SELL fill−Ask >=$.10, then submits protective SL only $.03 behind liquidation Bid/Ask, broker stop-adjusted, only tightening existing SL.

Illustration: BUY net quoted favorable move +$.10 after current Bid is compared with actual entry Ask; following a $.03 reversal to protective SL gives gross quote-side +$.07. Under illustrative K=1 account-unit per $1 XAUUSD quote change and C=.20 extra commission/fee, actual modeled net is **−$.13**, despite activation of a so-called profit trail. At entry a $.30 bid-side stop plus $.19 entry spread and $.20 cost means a possible original stop cash loss ~−$.69 (before gaps), NOT simply $.30. Examples depend on exact quote geometry, not measured average fill statistics.

OnTick/OnTimer both can trigger close requests; OnTradeTransaction handles deals but g_hadPosition and rearm still depend on later Reconcile. OnTick tick-event coalescing, synchronous order handling, repeated stop amendments and default verbose prints may make terminal observed quotes differ from the exact Python full quote stream. ResultAccepted includes PLACED, DONE_PARTIAL and NO_CHANGES, so actual accepted request is not identical to full filled position. Stop freeze/reject, slippage and broker fee data are not in original quotes. StartMinuteCycle is invoked BEFORE position reconciliation; when a close is first detected at a new minute, rearm can be resolved relative to newly created cycle rather than original trade minute. This boundary case warrants a targeted event-ordinal test; it is not established as an observed loss driver.

## Risk budget and current model state
R9 v1.94 portfolio governor computes gross losing DEAL_PROFIT amounts + fees + account floating losing exposure against a daily budget; defaults 4% starting-equity baseline, 12% maximum, recycle 25% of gross winning deals, peak-equity drawdown halt 10%, margin/free-equity limits. Its persistent lock/peak globals apply to the SAME TERMINAL account key, not independent terminals. On halt it closes matching R9 magic/symbol, not every account strategy. Research Python original R9 baseline does NOT model that new governor, so the 9-month original-v1.90 core scores below cannot be called a literal v1.94 broker account performance.

InpR9M60Mode=1 is SHADOW by default; InpR9M60Mode=2 must explicitly unlock but lacks a certified live 155-feature producer and would fail CLOSED on nonmatching same-tick file packets. No classifier probability is used in ManagePosition. The aspirational +1.75 account cash input is used only in a shadow scenario log, NOT in actual entry/exit conditions. R9 is not yet benefiting economically from the model AUC.

## Original source-parity nine-month Coinexx modeled baseline and failed experiments
Previous exact original chronological Python R9 source, Jan–Sep 2026, 72,129,347 original quote rows, all 303,934 original frozen positions source-ordinal matched. Under explicitly illustrative K=1 account-currency cash per one XAU dollar movement at .01 lots and C=.20 additional per position beyond Bid/Ask spread: net −120,212.46, −0.39552 cash per position, −27.315 cash per active source-entry hour, 7.45sec mean hold, gross losing trades 138,113.97 cash. With C=0 baseline remains −59,425.66, because source quote-side trading is already negative. Those are NOT actual Coinexx fills or calibrated account earnings.

Five expanding chronological walk-forward adaptive exit selections (May–Sep) were 0/5 profitable and 0/5 above baseline. Best fixed cost trail made total loss only 590.86 smaller across nine months while increasing GROSS losses +17,316.50 and lowering volume to 298,625; no promotion. The previous five-round Python experiment trained deterministic exit geometry, NOT the 155-feature LightGBM. These negative trials must not be repeated as if new solutions. Report on prior research branch: research/coinexx_r9_chronological/adaptive_exit/results/R9_V194_FIVE_WALKFORWARD_JANSEP_SCORES_20261114.md.

At unchanged volume, baseline requires +0.39552 additional net cash per average completed position just to reach breakeven; the aspiration +1.75/trade implies an unproven +2.14552 lift per historical trade. AUC cannot supply this return by itself. This is a fundamental economic feasibility threshold.

## HTF/HFT literature mechanism mapping — NOT XAUUSD empirical certification
A. OPEN RANGE / THRESHOLD MOMENTUM: Holmberg, Lönnbark, Lundström (2013) Finance Research Letters on crude oil opening range breakouts shows threshold persistence as an analyzable mechanism; differs sharply in asset and day-scale horizon. https://www.sciencedirect.com/science/article/pii/S1544612312000438
B. CONDITIONAL INTRADAY MOMENTUM: Li, Sakkas, Urquhart (2022), Journal of Financial Markets; intraday momentum depends on liquidity, volatility and information timing. Does not imply 1–30sec profitable Coinexx gold. https://www.sciencedirect.com/science/article/pii/S138641812100001X
C. FX VENUE / CLOCK REGIME: Elaut, Frömmel, Lampaert (2018) JFM studies FX intraday momentum and liquidity provision; trading-hour and spread effects warrant testing, not importing coefficients. https://www.sciencedirect.com/science/article/pii/S1386418116300313
D. OPTIMAL STOPPING: Imkeller, Rogers, Trading to Stops; fixed costs, trailing stops and timing should be optimized jointly instead of blindly widening stops. https://epubs.siam.org/doi/10.1137/130911706
E. PREDICTIVE HIGH FREQUENCY DIRECTIONAL CONTROL: Guilbaud and Pham, 2012 arXiv, conditional execution and risk under predictive signals. Their pro-rata order-book market-making assumptions DO NOT match R9 OTC market orders. https://arxiv.org/abs/1205.3051
F. LATENCY / EXECUTION: Stoikov and Waeber 2016, dynamic programming shows value of high-frequency execution information can vanish with latency; their LOB depth predictor is UNOBSERVABLE to Coinexx source. https://www.tandfonline.com/doi/full/10.1080/14697688.2016.1151926
G. TRUE ORDER FLOW IMBALANCE: Cont, Kukanov, Stoikov (2014) depends on best-quote SIZE and order-book events. Coinexx Bid/Ask with zero true volume/Last cannot derive this. Quote movement and update counts are only PRICE/ACTIVITY PROXIES, never authentic depth/OFI/VPIN. https://academic.oup.com/jfec/article-abstract/12/1/47/816163
H. BACKTEST SELECTION BIAS: Bailey and López de Prado 2014 Deflated Sharpe, multiple testing bias; require a short, frozen list of hypotheses and disclose failed trials, not a thousand-indicator optimization. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551
MetaQuotes original docs: https://www.mql5.com/en/docs/event_handlers/ontick ; https://www.mql5.com/en/docs/event_handlers/ontradetransaction ; https://www.mql5.com/en/docs/trading/ordercalcprofit .

## Proposed single coherent quant upgrade: model-conditioned momentum life-cycle router

Do NOT train another broad AUC model and do NOT enable the current model entry veto. The approved model was trained on original R9 candidate action states and cannot correctly assign cash exit probability at every future quote. Research needs to separate its **entry-time ranking** from a newly calibrated **post-entry continuation value**.

Step 1: For each previous May–Sep chronological fold, score ONLY exact original-side candidate entries using its original 155-feature frozen model and exact as-of source-ordinal feature vector. Group score into FROZEN deciles and compute actual original trade net cash, MFE, MAE, spread, session, elapsed-to-stop and microstructural quote-path persistence. Test whether higher score discriminates executable net cash better within original R9 trades. Same-month final all-Jan–Sep fit cannot count as held-out. If score deciles do NOT separate after-cost economic outcomes, STOP: no justification to use AUC for more holding time.

Step 2: At each already-open position quote t create causal state:
- Frozen original-side entry p5 score, original R9 side and bracket overshoot, real filled entry and current liquidation quote
- Current modeled net-account cash Pi_t, realized max favorable/adverse excursion, distance to existing stop, elapsed hold 1/3/5/10/15/20/30 sec
- As-of original tick-stream spread level/shock, quote-arrival intensity, one-second midquote displacement/noise, quote efficiency, last quote freshness
- Existing completed M5 ATR; completed M1 ADX +DI/−DI, EMA20 and StdDev; optional completed M15/M30/H1 trend bias as a SOFT control only
- Account gross loss remaining budget and available margin (broker-calibrated separate layer)
All unavailable data remain missing. The historical source does NOT provide actual order-book depth, executed volume or fill rejection.

Entry-time score p5 is a ranking/confidence covariate only. The model has NOT estimated a transition probability for HOLD versus EXIT versus SL tighten.

Step 3: Three permitted interventions before the hard <=30sec lifecycle: **EXIT_NOW**, **HOLD_EXISTING_SL**, or **TIGHTEN_SL**. No loosening an already-installed protective stop. Instead of blindly taking profit, fit POLICY-SPECIFIC competing risks (next favorable cash continuation; adverse reversal/stop; timeout; quote-gap censor) from earlier chronologically replayed streams, and policy-specific conditional net payout distributions and downside losses. A changed stop changes future state/entries/rearming, so never train policy-changed PnL by relabeling original frozen exits.

Account quote-side net cash formula:
Pi_now(t) = K * side * (L_t - P_entry) - C,
BUY uses entry Ask and exit Bid, SELL entry Bid and exit Ask, spread counted ONCE, C is EXTRA verified fees/slippage. Prefer real broker OrderCalcProfit and trade transaction costs where available.

Finite-horizon liquidation utility at elapsed age t:
Q(a|z_t) =
   E[Pi_exit_NET | z_t, action=a, frozen policy]
   − lambda * CVaR95(negative tail of Pi_exit_NET | z_t,a)
   − eta * expected foregone R9 rearm-slot payoff (occupancy)
   − xi * epistemic/quote-freshness uncertainty.
For EXIT_NOW, Q≈Pi_now minus only incremental fees not yet included in C. Hold only if an earlier-trained conservative LOWER confidence bound for Q(HOLD)−Q(EXIT) is >0 and governor capacity is adequate. Otherwise EXIT or retain safe baseline if evidence unidentifiable. Stop only tightens: BUY SL_new=max(SL_old, Bid−d_t); SELL SL_new=min(SL_old, Ask+d_t), with d_t determined from causal conditional future cash-loss distribution, broker min/freeze and finite cash-loss cap.

Economic router:
- **PERSISTENT RUNNER:** only if entry score tier predicts real profitable 5–30s continuation after cost; choose a more patient early trail BEFORE it is installed, without increasing initial stop risk or holding beyond cap.
- **NEUTRAL BASELINE:** uncertain, stale score, or no measured utility uplift — default untouched R9.
- **FAILURE EARLY-EXIT:** if fresh as-of adverse reversal hazard economically dominates conditional hold, exit before the full initial SL if that improves future whole-system PnL under on-policy replay. Never trade solely to maximize number of rearms.
Maintaining original candidate flow avoids the large drop in throughput caused by naive entry AUC thresholds.

## Indicators admissible under Coinexx-only data
Existing native iATR M5 completed 14, M1 ADX and +DI/−DI completed 14, EMA20 completed M1, additional iStdDev(M1,10,MODE_SMA,PRICE_CLOSE) and optional completed M15/M30/H1 price-derived iMA/iATR: historically reconstructible from original Bid OHLC after appropriate as-of history and warm-up. Must compare direct matched policy with indicator ON versus OFF, and check Python-vs-native exact bar parity. iVolumes VOLUME_TICK is quote-update count proxy, NOT real trade volume. The PRIMARY features for 7.45sec average hold are signed quote revisions, spread/quote freshness, realized volatility, MFE/MAE and current cash; slow indicators should be context, not blanket trade vetoes.

## Throughput and economics requirements
For fixed period, total modeled net = N trades × average net/trade. To match an aspirational 100%-volume total at $1.75 per trade, retention r requires mean net >=1.75/r; r=.95 =>1.842, r=.90=>1.944, r=.80=>2.188. Pure target arithmetic, NOT forecast. Keep **>=95% trades per held-out month** as primary retention gate and 90% as separately disclosed Pareto frontier. Require positive after-cost modeled cash per active entry-hour, positive monthly net, mean hold<=30sec, and no worse gross losses, cash-tail CVaR, portfolio governor halts or drawdown under the SAME risk and execution assumptions. Extra score-computation overhead must not destroy live tick throughput.

## Small falsifiable testing program, not broad retuning
Gate A: historic 155-fold model original-side score-to-REAL net cash decile join and coverage / calibration, from EXISTING frozen feature and trade artifacts (not raw reconstruction). If no economically meaningful discrimination, do NOT build score-conditioned runner.
Gate B: conditional stop/horizon causal loss-versus-continuation modeling with strict censor, earlier-only fitting and max three predeclared action modes.
Gate C: one existing chronological Coinexx engine continuous run per frozen contender, strict original 303934-trade baseline source parity; all rearming independently recomputed; compact scorecard by session, day/hour, trade volume, after-cost net, gross losses, hold, maxDD and CVaR. No tick copies, no retraining entire 155 model.
Gate D: post-Sep previously unseen data, actual Coinexx OrderCalcProfit/cost calibration, full v1.94 account governor (not old Python-only baseline), stop/freeze/execution latency and MQL5 same-quote model inference parity before any MT5 implementation.

**Research decision:** no production EA updates, and no claim that high AUC already means a profitable R9. Quant-first next step is to prove the exact original-side high-AUC signal predicts *realizable marginal continuation cash* before allocating additional holding time.
