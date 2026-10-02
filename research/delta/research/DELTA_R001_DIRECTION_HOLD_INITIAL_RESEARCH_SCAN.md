# DELTA R001 — Direction + Initial-Hold Initial Research Scan

**Date:** 2026-10-02  
**Branch:** `delta`  
**Status:** RESEARCH_ONLY / NO_TESTING / NO_ACTIVE_CANDIDATE  
**Active science parent:** `DELTA_004_COINEXX_LIKE_DUKASCOPY_RESEARCH_SURFACE`  
**Scope:** ENTRY + INITIAL-HOLD only  
**Deferred:** HOLDING-TRADE + EXIT + HIGH-PROFIT  
**August 2026:** SEALED  
**MQL5:** NOT AUTHORIZED

## 1. Owner research assumption

R9 already produces very high trade volume. The central research problem is not a shortage of entries but weak conversion of those opportunities into correctly directed, survivable trades.

Working assumption:

> R9's largest defect is the coupling of a single high-frequency bracket entry engine to a generic downstream stop/trail/max-hold lifecycle. Direction classification and the first seconds of trade persistence are insufficiently specialized for the variety of regimes, structures, and nested timeframes present in XAUUSD.

This is a research assumption, not a result.

## 2. DELTA R9 baseline anchors

From the current DELTA clean-restart quick references:

### R9 REAL, Jan–Jul 2026
- 236,647 trades
- 102,385 winning trades
- net profit -$50,285.28
- gross loss -$80,465.51
- 149/149 trading days negative
- 31/31 ISO weeks negative

### R9 SYNTH, Jan–Jul 2026
- 219,342 trades
- 191,136 winning trades
- net profit +$309,122.85
- gross loss -$16,238.66
- 149/149 trading days positive
- 31/31 ISO weeks positive

The REAL run executes more trades than SYNTH, so raw opportunity volume is not the obvious limiting variable.

### R9 functional chain
`new M1 minute -> frozen midpoint +/- $0.15 virtual bracket -> spread + completed-M5 ATR session gate -> completed-S1 displacement/efficiency/range/turn gate -> market entry -> hard SL / trail / max-hold -> opposite-side same-minute rearm -> next-minute reset`

Behavior-critical lifecycle:
- hard stop $0.30
- trail activation +$0.10
- trail distance $0.03
- max hold 30 seconds
- same-minute rearm up to 3
- S1 directional efficiency >0.70
- completed-bar/right-edge timing only

R9 has no multi-specialist router.

## 3. Research interpretation

The initial clean-room scan suggests that the direction+hold problem should be decomposed into four distinct layers:

1. **Regime / nested-direction state** — what directional state does the market occupy across relevant time horizons?
2. **Entry-event specialist** — what specific event justifies entering now?
3. **Initial-hold persistence state** — after fill, is the intended move actually persisting or was the trigger false/early?
4. **Ownership / routing** — which specialist is allowed to own this event, and when should ownership change?

This architecture is more promising for research than adding another global filter to the existing R9 bracket.

## 4. Fresh public-source findings

### 4.1 Multi-timeframe regime/direction classification is common, but strict all-timeframe agreement is not automatically desirable

Reconstructible/open-source examples combine:
- directional indicators such as +DI/-DI or moving-average relationships;
- trend strength via ADX;
- higher-timeframe direction;
- immediate breakout/momentum confirmation.

Examples:
- TradingView open-source Supertrend [TradingConToto]: ADX/DI, short/long EMA context, prior-high breakout.
  https://www.tradingview.com/script/cK5NVkdF/
- TradingView open-source Supertrend + ADX + MTF MA Filter.
  https://www.tradingview.com/script/VsOh0ffz/
- TradingView open-source MTF ADX.
  https://www.tradingview.com/script/E5uYlnA5/

A hierarchical HMM paper explicitly notes that a basic single-scale HMM can mistake short-term fluctuations for long-term trend switches, motivating hierarchical short/long trend state.
https://arxiv.org/abs/2007.14874

**Research implication:** DELTA should explore trend-within-trend state rather than a single trend bit. GOV-015 already assumes this conceptually. The candidate should likely expose direction at several nested horizons and allow states such as:
- aligned continuation;
- higher-timeframe trend + lower-timeframe pullback;
- transition;
- conflict/chop;
- local reversal inside higher-timeframe trend.

Strict all-timeframe consensus risks trade starvation and should not be assumed.

### 4.2 Breakout -> observation -> retest -> reconfirmation is a reconstructible alternative to R9's immediate bracket entry

MQL5 articles provide explicit breakout/retest state logic:
- identify structural breakout;
- do not enter immediately;
- wait for a retest of the broken level;
- require directional confirmation after the retest;
- then enter.

Sources:
https://www.mql5.com/en/articles/19968
https://www.mql5.com/en/articles/18259

**Research implication:** a `BREAKOUT_RETEST_REBREAK` specialist is a strong first entry-engine research family. It directly targets false/early breakouts without suppressing all breakout opportunity.

### 4.3 Pullback continuation is a distinct entry problem from breakout continuation

ForexFactory's Trend Channel / ADXVMA / Supply-Demand MTF system describes:
- higher-timeframe trend confluence;
- pullback into a trend zone;
- momentum recovery;
- enter on re-entry into the directional state;
- exit early if the directional state immediately degrades.

Source:
https://www.forexfactory.com/thread/1350785-trend-channel-adxvma-supply-demand-mtf-system

Recent Chinese XAUUSD community material independently separates direction, location/pullback, and momentum rather than treating direction alone as sufficient:
https://www.eahub.cn/thread-184874-1-1.html

**Research implication:** a `PULLBACK_CONTINUATION` specialist should be researched separately from a breakout specialist. The higher-timeframe trend may remain intact while the lower timeframe intentionally points against it during the pullback.

### 4.4 Volatility compression -> directional expansion is a plausible third continuation specialist

Recent algorithmic-trading community discussion reports a preference for entering when short-term realized volatility expands relative to longer-term volatility inside an already confirmed trend, rather than requiring a perfect pullback.

Source:
https://www.reddit.com/r/algotrading/comments/1uv4wzj/conditions_for_pullback_algo_trading/

A recent ForexFactory NR7 opening-range system likewise frames volatility compression resolving into a directional breakout as the mechanical event.
https://www.forexfactory.com/thread/1406504-nr7-opening-range-breakout-ea

**Research implication:** a `COMPRESSION_EXPANSION_CONTINUATION` specialist is reconstructible and may preserve R9-like activity better than pullback-only logic.

### 4.5 Failed-break / sweep reversal should be treated as a specialist, not as generic opposite-side rearm

The MQL5 trend-line reversal/breakout article explicitly distinguishes:
- continuation breakout + retest;
- structural rejection/reversal at a trend line.

Source:
https://www.mql5.com/en/articles/18259

**Research implication:** R9's same-minute opposite-side rearm is architecture-light. A future `FAILED_BREAK_REVERSAL` specialist could require a causal failure signature before taking the opposite direction instead of treating every exit as permission to reverse.

### 4.6 High-frequency order-flow / quote-pressure information is relevant to the first seconds after entry

Cont, Kukanov & Stoikov find that short-interval price changes are strongly related to order-flow imbalance at the best bid/ask and more robustly than raw traded volume in their data.
https://arxiv.org/abs/1011.6402

FX research also finds strong high-frequency relationships between order flow and exchange-rate returns. Ito & Hashimoto report forecast significance at very short 1- and 5-minute horizons that fades by 30 minutes.
https://www.nber.org/papers/w12682

Evans & Lyons and later EBS research support order flow as an important price-discovery variable in FX:
https://www.journals.uchicago.edu/doi/10.1086/324391
https://www.federalreserve.gov/econres/ifdp/order-flow-and-exchange-rate-dynamics-in-electronic-brokerage-system-data.htm

**Important DELTA limitation:** the Dukascopy source surface does not give DELTA a full centralized limit-order-book event stream. Therefore DELTA must not label a top-of-book quote-motion proxy as true OFI.

**Research implication:** explore a reconstructible `QUOTE_PRESSURE_PERSISTENCE` initial-hold component using only available causal fields, such as:
- bid/ask direction counts;
- midpoint displacement;
- quote-change asymmetry;
- spread behavior;
- directional efficiency;
- tick-arrival intensity;
- short-window continuation versus retreat.

This should be described as a quote-pressure proxy, not true order-flow imbalance.

### 4.7 The initial-hold layer should be volatility/structure aware rather than one universal tight trailing behavior

Recent MQL5 material explicitly warns that different trade types need different trailing behavior; a strong breakout needs room to breathe while a tight scalp may need a narrower trail.
https://www.mql5.com/en/articles/23618

MQL5 also describes ATR trailing as adapting stop distance to changing volatility rather than using a fixed point distance:
https://www.mql5.com/en/articles/23882

Open-source Chandelier Exit implementations are explicitly designed to keep a trade in a trend and avoid early exits by placing the stop a volatility-scaled distance from the favorable extreme.
https://www.tradingview.com/script/IoGxHkzt-Chandelier-Exit-by-fr3762-KIVAN%C3%87/

**Current-phase boundary:** DELTA is not reopening mature exit research. The relevant idea is only that the **first-seconds protection state should not automatically use the same fixed trail behavior for every entry specialist**.

## 5. Multi-specialist entry architecture is research-justified

MQL5 public articles explicitly support:
- regime classification followed by different strategy selection;
- multiple strategies living inside one EA;
- independent ownership of each strategy's contributions.

Sources:
https://www.mql5.com/en/articles/17781
https://www.mql5.com/en/articles/217
https://www.mql5.com/en/articles/14026
https://www.mql5.com/en/articles/18471

This architecture is directly relevant to R9 because R9 has one bracket-entry concept applied globally.

### Proposed research architecture, not yet a candidate

`CONTEXT ROUTER`
-> nested trend/regime state
-> session/news state
-> volatility state
-> structure state

then route to one of several entry specialists:
- `BREAKOUT_RETEST_REBREAK`
- `PULLBACK_CONTINUATION`
- `COMPRESSION_EXPANSION_CONTINUATION`
- `FAILED_BREAK_REVERSAL`

then use a specialist-aware:
- `INITIAL_HOLD_PERSISTENCE`
  - quote-pressure proxy
  - fast structural continuation/retreat
  - volatility-normalized breathing room
  - causal invalidation
  - hysteresis / anti-flip state

No specialist is promoted or selected by this scan.

## 6. Research candidate families for GOV-014 later

These are **research families**, not test candidates.

### DH-01 — Nested Direction State
Purpose: encode trend-within-trend context across fast, execution, structural, and regime horizons.

Possible reconstructible ingredients:
- return/slope sign;
- EMA or channel state;
- DI sign;
- ADX/trend-strength state;
- completed-bar structure highs/lows;
- volatility-normalized separation;
- state persistence/hysteresis.

### DH-02 — Breakout Retest Rebreak Specialist
Purpose: replace immediate breakout entry with a finite-state sequence:
`break -> observe -> retest -> directional rejection/rebreak -> enter`.

### DH-03 — Pullback Continuation Specialist
Purpose: allow lower-timeframe counter-move while higher-timeframe trend remains intact; enter only on causal re-acceleration.

### DH-04 — Compression Expansion Specialist
Purpose: identify directional expansion from a compressed state inside an allowed trend/regime.

### DH-05 — Failed Break Reversal Specialist
Purpose: identify a genuine failed breakout / structural rejection before taking the opposite direction.

### DH-06 — Quote-Pressure Initial-Hold Persistence
Purpose: decide whether the first seconds after entry confirm continuation, stall, or retreat using only causal top-of-book/tick information actually available to DELTA.

### DH-07 — Specialist-Aware Initial-Hold State Machine
Purpose: give each entry type an initial protection policy suitable to its expected path instead of applying one fixed trail immediately.

## 7. Key architecture hypothesis

The most important research hypothesis produced by this scan is:

> DELTA may need to preserve R9's opportunity-generation density while replacing the monolithic `one bracket entry -> one hold lifecycle` with `context router -> entry specialist -> specialist-aware initial-hold state`.

This would allow the system to distinguish:
- breakout continuation;
- trend pullback continuation;
- volatility expansion;
- failed-break reversal;
rather than forcing all opportunities through the same directional interpretation.

## 8. What should NOT be assumed

Do not assume:
- all timeframes must agree;
- more filters are automatically better;
- higher-timeframe trend must always veto countertrend specialists;
- strict MTF consensus is acceptable if it starves R9's activity;
- true OFI is available from Dukascopy top-of-book ticks;
- ATR trailing or Chandelier logic is automatically correct for XAUUSD;
- any commercial EA's claimed performance is evidence;
- the initial research scan has found a viable candidate.

Commercial/current XAUUSD products found in Chinese/Japanese MQL5 search frequently describe MTF trend + pullback/retest + adaptive management, but their exact internals are opaque. They are architecture clues only, not candidate logic or evidence.

## 9. Research priority before testing

No testing is authorized in this unit.

The next research-only work should refine the candidate grammar and feature definitions for:
1. nested direction state;
2. entry specialist ownership;
3. first-seconds persistence/invalidation;
4. conflict handling when timeframes disagree;
5. activity preservation.

Only after this research layer is sufficiently specified should selected families enter the GOV-014 spreadsheet harvesting/preregistration workflow.

## 10. Current state

- research phase started: YES
- testing started: NO
- spreadsheet candidate harvesting started: NO
- active candidate: NONE
- active candidate version: NONE
- metric locks: NONE
- heavy GOV-018 synthesis: DORMANT
- August: SEALED
- MQL5: NOT AUTHORIZED
