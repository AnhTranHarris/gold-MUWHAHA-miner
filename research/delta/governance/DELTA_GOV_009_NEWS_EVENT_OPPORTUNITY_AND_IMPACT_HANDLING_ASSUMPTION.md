# DELTA GOV-009 — News/Event Opportunity and Medium-High Impact Handling Assumption

**Effective:** 2026-10-01  
**Branch:** `delta`  
**Status:** MANDATORY / HUMAN-REVISABLE  
**Evidence loading:** NOT AUTHORIZED

## 1. Owner-defined assumption

DELTA assumes that major monetary-policy, macro-financial, market, and gold-specific news can create exploitable XAUUSD opportunity.

Medium- and high-impact news periods are therefore not treated as automatic exclusion zones.

The eventual DELTA system must contain one or more specialists, routing rules, or protective mechanisms capable of handling these periods causally.

This is an owner-defined DELTA architecture/research assumption. It is not evidence imported from any prior internal research lineage.

## 2. Required news domains

DELTA research must be capable of covering at least:

### United States / Federal Reserve
- Federal Reserve decisions and communications;
- major US macroeconomic releases;
- US rates, inflation, labor, growth, liquidity, fiscal, and financial-market news that materially affects gold.

### Europe
- major European monetary-policy and macro-financial news;
- major European rates, inflation, growth, liquidity, banking, and market events that materially affect gold.

### Asia
- major Asian monetary-policy, macro-financial, currency, growth, liquidity, and market news that materially affects gold.

### Gold-specific
- material gold-market news;
- bullion/liquidity developments;
- major supply/demand or reserve-related developments;
- material geopolitical/financial developments whose primary observed transmission is through gold.

This list defines research coverage, not a fixed external feed specification.

## 3. News is an opportunity regime

DELTA must not assume that medium/high-impact news should always disable trading.

Research may produce:
- pre-event specialists;
- release-reaction specialists;
- post-release continuation specialists;
- reversal specialists;
- spread/liquidity protection specialists;
- volatility-expansion specialists;
- no-trade/stand-down logic for specific event classes where evidence shows trading is unfavorable.

The decision to trade or stand down must be evidence-based and event-class specific.

## 4. Medium/high-impact handling requirement

A candidate or composite intended for full-system coverage must demonstrate that it can handle medium/high-impact event windows by at least one of these mechanisms:

1. trade them profitably under a dedicated specialist;
2. route them to a specialist designed for the event regime;
3. reduce or alter execution/risk in a predefined causal manner;
4. deliberately stand down when that event class is shown to be structurally adverse.

A generic unconditional news blackout is not the default DELTA assumption.

## 5. Event-aware specialist scope

A news-aware specialist manifest must declare:
- event domain;
- event class;
- impact level;
- applicable region/session;
- activation window;
- pre-event window;
- release timestamp semantics;
- post-event window;
- feature inputs available before the decision;
- spread/liquidity assumptions;
- intended primary metric contribution;
- interaction with other specialists and the router.

A specialist may be designed for one specific event class or for a family of events.

## 6. Causality and timestamp discipline

News/event research must obey strict as-of timing.

No event feature may use:
- a release value before its publication timestamp;
- a revised value before the revision became public;
- a headline before its timestamp;
- a later interpretation before it existed;
- future price response;
- future classification of whether an event was "good" or "bad."

For scheduled releases, DELTA must preserve:
- scheduled timestamp;
- actual publication timestamp when available;
- source timezone;
- normalized UTC timestamp;
- impact label known before the event;
- actual/revised values only from the time each became public.

For unscheduled news, the earliest trustworthy timestamp available to the research system is the earliest time the event may influence a causal feature.

## 7. Event-window market-state reconstruction

All event research remains tick-rooted under GOV-002.

DELTA may study:
- sub-second impulse;
- spread expansion;
- quote density;
- directional efficiency;
- rapid reversals;
- continuation persistence;
- volatility expansion;
- liquidity vacuum;
- slippage/execution sensitivity;
- recovery/normalization after the event.

These may be observed across the nested timeframe hierarchy while preserving tick chronology and right-edge visibility.

## 8. Interaction with session-aware architecture

News handling is part of the multi-specialist architecture in GOV-008.

Event specialists may:
- override a normal session specialist;
- coexist with a normal session specialist;
- temporarily own the opportunity;
- block another specialist;
- transfer ownership after the event impulse;
- hand back control after a defined normalization condition.

All ownership transitions must be explicit, deterministic, and causal.

## 9. Interaction with creative refinement

GOV-007 applies fully.

If a normal-session candidate performs poorly during medium/high-impact events, DELTA is encouraged to:
- split news periods into their own specialist;
- build separate pre/release/post-event specialists;
- change timeframe combinations;
- redesign hold/exit behavior;
- add spread/liquidity state;
- create event-specific routing;
- test multiple event-window configurations.

The system is not required to force a normal-session mechanism to solve a fundamentally different event regime.

## 10. Evaluation

News-aware specialists and composites must report, where supported:
- event count;
- event-class trade count;
- winning trade count;
- net profit;
- gross loss;
- maximum drawdown;
- average profit/trade;
- pre-event versus release versus post-event performance;
- spread/slippage sensitivity;
- contribution to aggregate composite metrics.

News performance must not be hidden inside a whole-month aggregate if event-specific behavior materially affects the result.

## 11. Feed/taxonomy contract is still pending

This assumption does not yet freeze:
- specific news providers;
- exact calendar provider;
- exact impact taxonomy;
- exact event identifiers;
- timestamp reconciliation rules across providers;
- handling of revised releases;
- unscheduled-news source hierarchy;
- exact pre/post-event window lengths.

Those details require a later dedicated event-data contract before any news feature is used in promotion-grade research or MT5 translation.

## 12. Human-review authority

The owner may later:
- add or remove event domains;
- redefine impact levels;
- require dedicated specialists for certain releases;
- define mandatory stand-down classes;
- alter event windows;
- change routing precedence.

## 13. No evidence-load authorization

This contract defines architecture and research assumptions only.

It does **not** authorize loading R9 REAL, R9 SYNTH, R9 OVERFIT, Coinexx reports, R9 ticklogs, Dukascopy tick files, or external news/event datasets. Existing owner evidence-loading restrictions remain active.
