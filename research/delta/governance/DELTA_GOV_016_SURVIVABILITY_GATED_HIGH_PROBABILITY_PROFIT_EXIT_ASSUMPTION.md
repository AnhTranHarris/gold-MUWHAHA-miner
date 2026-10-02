# DELTA GOV-016 — Survivability-Gated High-Probability Profit Exit Assumption

**Effective:** 2026-10-02  
**Branch:** `delta`  
**Status:** MANDATORY / HUMAN-REVISABLE ASSUMPTION  
**Layer:** PROFITABILITY / EXIT ARCHITECTURE  
**Research metrics:** NOT DEFINED BY THIS CONTRACT  
**Candidate research:** NOT AUTHORIZED BY THIS CONTRACT

## 1. Purpose

DELTA assumes that profitable exit logic should ultimately aim to capture the **highest-probability safely attainable profit level** for a trade.

This objective is downstream of trade survivability.

DELTA must not attempt to optimize for aggressive profit capture until the survivability architecture is sufficiently mature and reliable to keep trades alive through normal adverse movement, retracement, session transitions, news conditions, and nested multi-timeframe structure without exposing the trade to avoidable structural failure.

This is an architecture assumption only. It does not define an exit candidate, target distance, hold time, probability threshold, optimization metric, or promotion gate.

## 2. Survivability precedes profit optimization

The dependency order is:

`CONTEXT AWARENESS -> TRADE SURVIVABILITY -> TRADE MATURITY -> PROFIT EXIT OPTIMIZATION`

Profitability logic must not outrun survivability logic.

A system that cannot reliably distinguish normal trade development from structural invalidation is not considered mature enough to pursue farther or more ambitious profit exits.

## 3. Highest-probability profit level

The phrase **highest-probability profit level** means the profit zone that, using only causally available information, has the strongest combination of:

- probability of being reached;
- probability of being realized without unacceptable structural failure first;
- compatibility with the trade's current maturity;
- compatibility with session state;
- compatibility with news/event state;
- compatibility with trend-within-trend structure;
- compatibility with the owning specialist's lifecycle;
- compatibility with spread, execution cost, and current market conditions.

It does **not** mean:

- the historical maximum favorable excursion;
- the highest price later visible in hindsight;
- the farthest mathematically possible target;
- a static fixed take-profit applied universally;
- holding a trade longer merely because a larger theoretical profit exists;
- sacrificing survivability to chase a larger payoff.

## 4. Profit exit is conditional and adaptive

The eventual system should be capable of recognizing that the best exit may differ across otherwise similar trades.

For example, the highest-probability attainable profit zone may move closer or farther depending on:

- whether the trade is aligned or countertrend within the multi-timeframe hierarchy;
- whether the move is continuation, pullback, breakout, reversal, or transition;
- whether the trade has matured cleanly or has shown repeated structural weakness;
- whether expected continuation is strengthening or degrading;
- whether session liquidity is increasing or decaying;
- whether news/event context changes the probability distribution of continuation;
- whether spread or execution quality materially changes;
- whether the owning specialist's original thesis remains intact.

No specific implementation is selected by this contract.

## 5. Survivability veto

Survivability has veto authority over profit pursuit.

If causal evidence indicates that:

- the trade thesis is structurally invalidated;
- the trade has entered a materially less survivable state;
- the expected path to the farther profit zone now requires exposure inconsistent with the survivability model;
- the trade's specialist ownership is no longer valid;
- the context has transitioned into a different regime;

then the system must be free to exit before the previously expected higher profit zone.

A larger hypothetical profit target must never force the system to ignore a meaningful survivability failure.

## 6. Trade maturity gate

A trade should not be treated as eligible for advanced profit-target optimization merely because it is currently profitable.

Future research must distinguish trade maturity from simple positive PnL.

Possible maturity dimensions may later include, subject to research:

- structural confirmation after entry;
- persistence through the initial-hold phase;
- favorable development relative to expected path;
- reduction in invalidation risk;
- confirmation across relevant nested timeframes;
- specialist-specific state progression;
- transition from vulnerable entry state to established trade state.

This list is illustrative only.

## 7. Highest probability, not highest absolute profit

The eventual exit objective should prefer a smaller profit with materially higher safe-realization probability over a larger profit whose realization probability is substantially lower or whose path materially compromises survivability.

DELTA therefore rejects the assumption that profitability is equivalent to maximizing raw favorable excursion.

The desired behavior is **probability-weighted profit capture under survivability constraints**.

## 8. Multi-layer context

The future profitability/exit layer should eventually be able to consume, without automatically being dominated by any one input:

- session context;
- news/event context;
- trend-within-trend context under GOV-015;
- specialist ownership;
- trade maturity;
- price structure;
- volatility state;
- spread/execution state;
- causal opportunity structure.

The exact hierarchy and precedence remain subjects for later research.

## 9. No hindsight exits

Any future exit mechanism must be causal.

It may not select an exit because later price action proves that point was optimal.

Forbidden examples include:

- choosing the local maximum after observing the subsequent decline;
- labeling an exit as high-probability using future bars;
- using the future maximum favorable excursion as a live target selector;
- using a future regime label to justify an earlier exit.

Future probability estimates must be based only on information available at the decision time.

## 10. Specialist-specific profit logic

Different specialists may require different high-probability profit models.

Examples may eventually include:

- continuation specialist;
- pullback specialist;
- reversal specialist;
- breakout specialist;
- countertrend specialist;
- event/news specialist.

A universal static exit is not assumed.

The final architecture may contain specialist-specific profit zones, shared exit components, or a causal exit router, subject to later evidence.

## 11. Relationship to current DELTA phase

Current DELTA research remains focused on:

`ENTRY + INITIAL-HOLD`

This assumption does not reopen:

- mature holding-trade logic;
- exit research;
- high-profit research.

Those remain deferred until the owner authorizes that research phase.

## 12. No metric or threshold authorization

This contract does not define:

- minimum profit per trade;
- take-profit distance;
- probability threshold;
- required hit rate;
- expected-value formula;
- hold-time threshold;
- maturity score;
- survivability score;
- exit confidence score;
- MFE capture ratio;
- candidate formula;
- optimization grid.

Those must be discovered later through the established spreadsheet-first quant harvesting and causal Dukascopy tick-replay workflow.

## 13. Future research requirement

When exit research is eventually authorized, candidate logic must answer three separate questions:

1. **Can this trade survive long enough to mature?**
2. **What profit zones are causally reachable from the current mature state?**
3. **Which reachable zone has the highest probability of safe realization after costs and before structural invalidation?**

Only then should the system decide whether to continue holding or exit.

## 14. Future MT5 reconstruction

If a successful future candidate implements this assumption, the final MT5 handoff must explicitly document:

- trade-maturity state machine;
- survivability veto conditions;
- candidate profit-zone generation;
- probability or ranking logic;
- selected exit decision rule;
- session/news/trend context inputs;
- specialist ownership;
- exact causal update timing;
- execution-price semantics;
- formulas and parameters;
- parity fixtures.

MQL5 coding remains owner-authorized only under existing governance.

## 15. August

August 2026 remains sealed.

This contract does not authorize August access.
