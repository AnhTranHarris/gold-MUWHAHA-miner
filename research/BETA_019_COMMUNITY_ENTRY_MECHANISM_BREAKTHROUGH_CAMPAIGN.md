# BETA 019 — Multi-pass community research for reproducible high-accuracy/high-count entry mechanisms

**Date:** 2026-09-29  
**Lineage:** BETA only.  
**Status:** COMMUNITY SOURCE RESEARCH + PREREGISTERED ENTRY EXPERIMENTS. **No BETA019 market backtest has yet been executed; no breakthrough, MQL5 candidate, or approved EA is claimed.**  
**Owner priority:** ENTRY accuracy and correctly captured trade count dominate for this phase. HOLD and EXIT remain lower-weight/frozen controls under BETA018. Profit is a safety/diagnostic metric rather than the optimization target, but after-cost and BETA015 account integrity remain mandatory. August 2026 remains SEALED.

## 1. Research method

Four independent web-research passes were conducted across:
- MetaQuotes/MQL5 articles and forums;
- TradingView open-source scripts;
- Reddit algo/Forex/day-trading discussions;
- ForexFactory/Myfxbook;
- Chinese, Japanese, Korean language materials where the logic is publicly reconstructible.

Opaque/protected scripts, seller claims, unverifiable win rates and proprietary "institutional" labels are **not candidate mechanisms**. Their marketing claims are excluded. A mechanism enters BETA only when its decision sequence can be independently reconstructed in Python and later MQL5 using causal data.

The repeated cross-source observation is not "one magic indicator." The strongest recurring **entry sequences** are:
1. confirmed level/structure -> decisive break -> **first retest** -> re-acceleration;
2. confirmed level -> **sweep/failure/reclaim** -> structural shift -> immediate or retest entry;
3. genuine consolidation -> **compression/asymmetry** -> body-quality breakout -> fresh momentum;
4. higher-timeframe structural ownership -> lower-timeframe setup -> **tick-level timing**, rather than using a global regime filter that simply deletes trades.

Community warnings are equally important: filters can improve apparent win rate merely by reducing trades; waiting for every retest misses genuine runners; and breakout systems are damaged by chop/fees. BETA therefore tests **dual-path routers** (fast acceptance OR first-retest) instead of automatically requiring a retest on every signal.

## 2. Reconstructible source mechanisms

### A. Confirmed fractal / swing structure

MetaQuotes' September 2026 "First Fractal Breakout" provides exact MQL5 logic:
- five-bar Bill Williams fractal, central bar greater/less than two bars each side;
- query at shift 3 to avoid the two-bar confirmation/repainting window;
- first confirmed up/down fractals after a session start define adaptive structural boundaries;
- current tick breaks a confirmed level; one attempt per direction in the source design.
Source: https://www.mql5.com/en/articles/23575

**BETA adaptation:** do not inherit its low-frequency "one trade per direction/day" restriction. Use confirmed fractals as **structural anchors** at H1/M15/M5 and let independently qualified lower-timeframe entry events reuse the anchor until it invalidates. This preserves trade count while preventing future-bar pivot leakage.

### B. Structural validity engine rather than every swing

MetaQuotes "Swing Extremes and Pullbacks Part 3" makes a swing candidate valid via one or more of:
- momentum break of structure;
- displacement/impulse strength;
- liquidity sweep;
- time-based respect;
then tracks structural state.
Source: https://www.mql5.com/en/articles/21888

**BETA adaptation:** validate a structural level using only completed bars, but **ablate each validation flag independently**. Do not require all flags. A multi-flag score can be tested only after each flag's incremental entry precision and retained count is known. "Liquidity" is operationally a prior-price-level sweep/reclaim, not an assertion about hidden institutional orders.

### C. Break -> first retest -> reaction

Reconstructible sources converge on state-machine implementation:
- MQL5 Chart Objects EA: completed breakout close -> later retest touch -> confirming directional candle.
  https://www.mql5.com/en/articles/19968
- Chinese MQL5 ORB article: Capture -> breakout confirmation -> support/resistance retest -> cycle end, implemented as a persistent OnTick state machine.
  https://www.mql5.com/zh/articles/18486
- TradingView open source break/retest and retest-quality scripts: confirmed swing -> ATR-adjusted break -> volatility-scaled retest zone -> reject/accept.
  https://www.tradingview.com/script/0qXYzowp-Break-Retest-Liquidity-Sweep-Entry/
  https://www.tradingview.com/script/rFaVrkiK-Breakout-Retest-Signals-algotim/
- Reddit algotrading discussions repeatedly identify **first clean retest** as a way to reject chop, while also warning that mandatory retests reduce opportunity capture.
  https://www.reddit.com/r/algotrading/comments/1pze3km/
  https://www.reddit.com/r/algotrading/comments/1ub7zuc/

**BETA candidate:** FAST_OR_RETEST router:
- frozen confirmed level L;
- branch FAST when a completed M1/S15 body accepts outside L with adequate body/range and tick ignition;
- branch RETEST only if FAST did not fire or did not qualify: first return into ATR-scaled level zone, shallow penetration, then S1/S250 re-acceleration away from L;
- event expires after a predeclared time/bars or structural reclaim.
This explicitly tackles the owner's accuracy **and trade-count** objective.

### D. Sweep -> reclaim -> structural shift

Open-source TradingView and community Gold setups converge on a deterministic sequence:
- wick/trade beyond prior confirmed high/low;
- close/reclaim back across level;
- later structure break/CHoCH in reversal direction;
- either immediate entry after shift or first pullback to broken structure.
Sources:
https://www.tradingview.com/script/EwYuNAx2-Liq-Sweep-CHoCH-OB-Instant/
https://www.tradingview.com/script/HCXJM3dW-CHOCH-Liquidity-Sweep-Detector/
https://www.tradingview.com/script/uTcKcZmL-false-breakouts/
https://www.myfxbook.com/community/experienced-traders/1-gold-setup-you-should/3369671%2C1
https://www.reddit.com/r/Forex/comments/1tvp1wh/
https://www.reddit.com/r/Daytrading/comments/1v8x7tl/

**BETA candidate:** SWEEP_RECLAIM_SHIFT:
- confirmed M15/M5 level from past data;
- tick or M1 high/low exceeds L by minimum absolute/ATR fraction;
- same or later completed M1/S15 closes back inside;
- post-reclaim micro swing breaks in reversal direction;
- S1/S250 displacement confirms;
- optional first retest branch versus immediate-shift branch.
Never treat "sweep" as evidence of actual stop orders; it is purely price geometry.

### E. Consolidation geometry / asymmetry breakout

MetaQuotes GA Breakout explicitly measures **internal swing-leg distance, slope and duration asymmetry** within a locked consolidation, then waits for a decisive buffered close beyond the boundary.
Source: https://www.mql5.com/en/articles/21197

**BETA candidate:** GA_COMPRESSION_IGNITION:
- identify a closed M5/M1 consolidation with confirmed swings;
- compute each alternating leg's distance, duration, slope and range location;
- create directional asymmetry vector from **past completed legs only**;
- require breakout body close beyond frozen range plus ATR/absolute buffer;
- require fresh S5/S1/S250 displacement on the executable tick;
- compare to identical box breakout without GA features.

This is more promising than simply saying "ATR high" because it predicts which side of a compression is becoming structurally dominant before the boundary break, while remaining deterministic.

### F. Breakout body/wick quality

Japanese and open-source English materials repeatedly require a breakout to be more than a wick:
- adaptive-channel MQL5: close outside boundary, optional volatility and retest confirmation;
- MQL5 fractal consolidation: buffer beyond range;
- open-source ATR Body: pivot break + ATR-scaled body + wick/body quality;
- XAUUSD ForexFactory NY ORB specifies body/range and body/ATR thresholds (its reported win rates are **not accepted as evidence**).
Sources:
https://www.mql5.com/ja/articles/21443
https://www.tradingview.com/script/mLpKebfD-Break-Confirm-ATR-Body/
https://www.forexfactory.com/thread/post/15609751

**BETA candidate feature vector:** breakout distance / ATR, body / full range, close location within bar, opposite-wick / body, prior-box penetration, spread / body, and immediate 250ms/1s/5s follow-through. Test as continuous bins first, not one fitted magic threshold.

### G. Breakout -> controlled pullback with momentum still intact

Chinese MQL5 Wizard article describes envelope breakout -> shallow return that remains outside/at the broken envelope -> AO momentum stays directionally strong.
Source: https://www.mql5.com/zh/articles/18842

**BETA candidate:** MOMENTUM_PRESERVED_PULLBACK:
- use causal envelope/Keltner/confirmed structural level;
- displacement break;
- pullback depth measured in prior ATR, not fixed dollars;
- momentum persistence using reproducible AO and/or direct price ROC (test separately);
- lower-timeframe re-acceleration entry.
This can capture runners missed by deep-retest logic without buying the initial spike.

### H. Compression -> expansion

Open-source squeeze/cluster breakout systems use:
- shrinking high-low / ATR or Bollinger inside Keltner;
- locked compression range;
- breakout close outside the range;
- strong close location/body quality;
- momentum/trend qualification.
Sources:
https://www.tradingview.com/script/DkDNMQsn-Cluster-Breakout-Strategy-v6-Robust/
https://www.tradingview.com/script/bN8jxMy5-Momentum-Squeeze-Breakout-Engine/
https://www.mql5.com/ja/articles/19459

**BETA candidate:** NR_COMPRESSION_RELEASE:
- normalized range and ATR percentile from prior completed M1/M5;
- contraction sequence, not one small candle;
- frozen box;
- break with body-quality;
- S1/S250 direction;
- immediate and first-retest branches evaluated independently.

### I. Activity / quote-direction imbalance timing

MetaQuotes "Beyond the Clock" implements tick/activity/imbalance bars in both Python and MQL5 and explicitly warns about tick-index parity and one-tick boundary drift.
Source: https://www.mql5.com/en/articles/22063

The article's **trade** tick imbalance cannot be copied literally to Dukascopy quote-only data. BETA can reconstruct a different, properly named metric:
- sign each source quote update from midpoint change (carry previous sign on exact ties only if preregistered);
- cumulative signed quote count;
- EWM expected quote count and expected imbalance;
- close a QUOTE_IMBALANCE event when the causal threshold is crossed;
- record quote frequency, price efficiency and spread at boundary.

**BETA candidate:** QUOTE_IMBALANCE_IGNITION as a timing qualifier, **not order flow**. It may supply a faster trigger than waiting for an S1 close while preserving exact MT5 OnTick implementability.

### J. Multi-timeframe swing state machine

MetaQuotes' September 2026 MTF swing engine explicitly requires prerequisite higher-timeframe trend before evaluating lower-timeframe continuation/reversal structures.
Source: https://www.mql5.com/en/articles/23538

**BETA adaptation:** H1/H4 is a *structural owner*, not a hard global trade/no-trade filter:
- classify last confirmed higher-TF structural direction and age;
- lower-TF specialists receive it as context;
- route TREND-continuation, SWEEP-reversal or RANGE-compression family based on their own prerequisites;
- permit a specialist to abstain rather than force every event through the same trend rule.

Reddit disagreement on regime filters is important: some users report them valuable; others find they merely reduce trading frequency or overfit. BETA must therefore compare **specialist routing** to a global regime gate.
Sources:
https://www.reddit.com/r/algotrading/comments/1v42762/
https://www.reddit.com/r/algotrading/comments/1skdizm/
https://www.reddit.com/r/algotrading/comments/1se1rof/
https://www.reddit.com/r/algotrading/comments/1rvfy12/

## 3. Proposed BETA019 breakthrough search — entry-first, count-preserving

### Tier 1: highest-priority independent experiments

**E19-1 FAST_OR_FIRST_RETEST_STRUCTURE**
- anchor: confirmed M15/M5 fractal swing or validated structure;
- break qualification: body close beyond level, body/range, distance/ATR;
- FAST branch: S250/S1/S5 aligned acceleration with spread budget;
- RETEST branch: first ATR-scaled return, no deep reclaim, fresh S250/S1 re-acceleration;
- dedupe one structural event; compare FAST, RETEST, and dual router.
**Why:** directly addresses the tradeoff seen in community discussions: immediate breakout retains runners; retest rejects fakeouts.

**E19-2 SWEEP_RECLAIM_SHIFT_DUAL**
- prior confirmed structure;
- sweep beyond level;
- causal reclaim;
- micro CHoCH/break of local swing;
- immediate shift branch vs first retest branch.
**Why:** source convergence is unusually high across MetaQuotes/TradingView/Gold communities, and every element is price-only and reconstructible.

**E19-3 GA_COMPRESSION_RELEASE**
- M1/M5 closed consolidation;
- internal leg asymmetry vector;
- body-quality buffered release;
- tick ignition.
**Why:** introduces information about *inside the range* rather than adding another lagging direction filter, potentially raising accuracy without destroying count.

**E19-4 QUOTE_IMBALANCE_MICROTIMING**
- no new strategic direction by itself;
- use quote-direction imbalance, quote rate, efficiency, and spread to choose the **execution tick** inside an already valid structural setup.
**Why:** closest causal mechanism to the owner's goal of approximating the teacher's precise entries tick by tick without future information.

### Tier 2: specialist expansions after Tier 1 ablation

**E19-5 MOMENTUM_PRESERVED_PULLBACK** — shallow ATR pullback after strong break with AO/ROC still aligned.  
**E19-6 NR_COMPRESSION_RELEASE** — contraction sequence -> strong body release; compare direct vs retest.  
**E19-7 FIRST_FRACTAL_SESSION_ANCHOR** — use first confirmed session M5 fractals as level source, but allow multiple independently deduped lower-TF setups so it does not inherit the source's 2-trade/day cap.  
**E19-8 RANGE_EDGE_FALSE_BREAK** — specifically for neutral/low-efficiency states: confirmed range edge -> single/two/multi-bar false-break reclaim -> micro reversal; do not combine with trend-continuation rules on same tick.

## 4. Test design centered on ENTRY accuracy and count

Before profit, every independent event gets an offline, noncausal **teacher/evaluation label only**:
- side-correct executable markout at +1s, +3s, +5s, +15s, +30s;
- true tick-order first hit of favorable/adverse thresholds;
- MFE/MAE through fixed horizons;
- spread paid at signal;
- timestamp and price delay from earliest causally eligible state;
- whether an R9 teacher event exists in a compatible source-defined neighborhood, **only when cross-feed alignment is scientifically defensible**.

Live candidate features never receive these future labels.

Primary scorecard:
1. **Entry precision** = correctly directed independently deduped events / all candidate entries.
2. **Opportunity recall** = independently defined correct opportunities captured / eligible opportunity population.
3. **Absolute correct-entry count** and entries/day.
4. **False-entry count** and false-entry rate.
5. 1s/3s/5s/15s/30s after-cost executable markout distribution.
6. Entry timing and price displacement.
7. Opportunity retention versus parent/unfiltered signal population.
8. Session/regime/spread stability.
9. BETA015 funded termination date / gross loss / marked DD remain safety constraints, but **are not the objective optimizer at this phase**.

A filter/router is scientifically interesting when it improves precision while preserving a substantial fraction of correct opportunities. A 5-point precision increase that destroys 80% of correct entries is not automatically preferred. Exact owner threshold for "desirable" entry maturity remains an owner decision; do not invent one.

## 5. Experiment sequencing and anti-overfit

1. Finish the pending BETA005 materialized feature/cache parity audit before calling a full multiscale result production-grade.
2. January = discovery and causal label engineering.
3. Test E19-1..E19-4 **standalone** first with frozen R9-style Hold/Exit.
4. Ablate every subcondition: level, body, retest, S250/S1/S5, quote-imbalance, structural context.
5. Only after independent evidence, test paired routers:
   - STRUCTURE FAST/RETEST + SWEEP/RECLAIM;
   - GA compression + FAST/RETEST;
   - structural event + quote-imbalance execution timing.
6. Never add sleeve profits; one chronological account/one 0.01-lot position.
7. February–July have already been consulted historically; they are reuse validation, not pristine OOS.
8. Freeze all mechanics and parameters before requesting owner authorization to unseal August. One blind evaluation; no tuning and re-calling it blind.
9. Owner approval before any candidate MQL5. After authorized MT5 build, use same state-machine semantics and confirmed-bar timestamps; owner local Coinexx M1 "Every tick based on real ticks" determines broker evidence.

## 6. Exclusions

Do not use:
- protected TradingView scripts whose source logic is not reconstructible;
- MQL5 Market products with proprietary undisclosed logic;
- centralized-volume/order-book assumptions not present in Dukascopy quote data;
- repainting pivots used before right-hand confirmation;
- "institutional" motives as a feature;
- future MFE/MAE/optimal-entry labels in live feature calculations;
- a universal regime gate solely because it raises win rate by deleting most trades;
- HOLD/EXIT optimization to make an entry candidate look more accurate.

## 7. Research conclusion

The strongest **new direction is not a larger stack of indicators**. It is an account-exclusive state-machine router combining a *small number of independent causal mechanisms*:
1. **validated structure / locked range**;
2. **event type**: continuation break, failed break/reclaim, or compression release;
3. **fast-vs-first-retest dual path** to preserve opportunity count;
4. **quote-level microtiming** to improve the exact executable entry tick.

This architecture is fully reproducible in Python and MQL5 and is directly aligned with BETA018: improve entry precision **without collapsing correct-entry count**. It remains a hypothesis until original-tick testing is executed.
