# DELTA GOV-010 — High-Opportunity-Density and Candidate Trade-Contribution Assumption

**Effective:** 2026-10-01  
**Branch:** `delta`  
**Status:** MANDATORY / HUMAN-REVISABLE  
**Evidence loading:** NOT AUTHORIZED

## 1. Owner-defined architectural assumption

DELTA assumes that a core edge of the intended XAUUSD system is **high daily opportunity density and high realized trade activity**.

For DELTA, "high-frequency" means a system that repeatedly identifies and acts on many causal XAUUSD opportunities across the trading day. It does **not** imply institutional latency-arbitrage, exchange co-location, or microsecond HFT.

This is an owner-defined DELTA design assumption based on the intended system heritage. No prior internal research lineage is imported or consulted by this contract.

## 2. Trade activity is part of the edge

DELTA must not treat trade count as a cosmetic output.

The system is expected to create its performance through a large number of qualified opportunities distributed across:
- sessions;
- regimes;
- event/news states;
- specialist scopes;
- intraday periods.

A candidate that improves headline metrics only by eliminating most trading opportunities is not aligned with the intended DELTA edge.

## 3. Candidate contribution requirement

Every trading **SPECIALIST** or **SPECIALIST_BUNDLE** must be designed to contribute positive incremental opportunity capacity within its declared scope.

Its evaluation must show:
- opportunities detected in scope;
- unique opportunities added versus its parent/reference;
- trades proposed;
- trades executed after routing;
- winning trades contributed;
- opportunities displaced or cannibalized from other specialists;
- net contribution to composite opportunity count;
- net contribution to composite executed trade count.

The preferred direction is positive incremental contribution.

A candidate that contributes no unique opportunities and merely duplicates another specialist must justify why it improves routing, execution, persistence, loss control, or another protected system property.

## 4. Router/protective components

A pure **ROUTER_ORCHESTRATOR** or protective mechanism may not directly create trades.

Its contribution is measured by whether it:
- increases opportunity capture;
- improves conversion of qualified opportunities into executed trades;
- reduces destructive conflicts that suppress otherwise valid trades;
- preserves more qualified trade opportunities under risk/execution constraints;
- enables complementary specialists to operate safely in parallel.

A router that only suppresses activity must demonstrate that the suppression creates a net system benefit under the active primary metrics and does not violate the intended high-opportunity-density architecture.

## 5. Unique-opportunity accounting

DELTA must not inflate frequency by counting duplicate proposals as separate opportunities.

The research framework must maintain a deterministic opportunity ledger capable of identifying:
- specialist source;
- timestamp;
- direction;
- instrument;
- event/session/regime context;
- candidate/version;
- ownership result;
- duplicate/overlap relationship;
- final executed-trade linkage.

When two specialists identify essentially the same underlying opportunity, the composite must distinguish:
- one unique market opportunity;
- multiple specialist proposals;
- one or more permitted executions according to the router contract.

Exact deduplication tolerances may be frozen later, but duplicate proposals must never silently become fake opportunity growth.

## 6. Daily-frequency reporting

Because the assumed edge is daily opportunity density, aggregate monthly totals are insufficient.

Every promotion-grade specialist and composite scorecard must report, when supported:
- total opportunities;
- unique opportunities;
- total proposed trades;
- executed trades;
- winning trades;
- losing trades;
- opportunities per trading day;
- executed trades per trading day;
- winning trades per trading day;
- median daily opportunity count;
- median daily executed trade count;
- low-activity/zero-trade days;
- session contribution;
- event/news contribution;
- opportunity-to-trade conversion rate.

Additional distribution statistics may be added during research.

## 7. No-starvation principle

DELTA must explicitly detect "success by starvation."

A candidate is suspect when improved net profit, gross loss, drawdown, or win quality is primarily explained by a collapse in opportunity/trade activity.

The candidate report must state whether:
- activity increased;
- activity was retained;
- activity materially declined;
- gains came from better selection/holding/exits;
- gains came mainly from simply not trading.

No candidate may hide trade-count collapse behind percentage-based headline improvements.

## 8. Specialist scope and additive composition

Under GOV-008, a specialist may operate only in a narrow session/regime/event scope.

Within that scope, it should seek to add qualified opportunities that the existing composite does not already exploit effectively.

The composite research process should prefer complementary specialists that expand coverage into:
- different sessions;
- different volatility regimes;
- different trend/range states;
- different news/event states;
- different entry/hold/exit opportunity classes.

This allows the system to accumulate opportunity capacity without forcing one universal strategy to trade every condition.

## 9. Interaction with GOV-005 primary metrics

Winning trade count remains a primary human metric.

GOV-010 makes the activity context around that metric mandatory.

A higher winning-trade count is stronger when it comes from:
- more qualified opportunities;
- higher opportunity capture;
- retained or increased executed trade count;
- improved win conversion;

rather than from denominator manipulation or scope changes.

Net profit, gross loss, and maximum drawdown remain co-equal primary metrics under GOV-005.

High activity does not excuse failure of those protections.

## 10. Interaction with GOV-006 locks

A composite-level metric lock does not freeze trade activity unless the owner separately locks an activity metric.

However, future descendants must report whether preserving a locked primary metric caused opportunity/trade-count degradation.

A candidate that preserves a metric lock only by starving the system should be flagged for creative refinement under GOV-007.

## 11. Interaction with GOV-007 creative refinement

Creative authority explicitly includes searching for ways to increase qualified opportunity density.

DELTA may:
- create new specialists for uncovered periods;
- split broad specialists into more productive narrow specialists;
- recover opportunities suppressed by overly restrictive gates;
- redesign router ownership;
- change multi-timeframe interactions;
- improve re-entry/rearm logic;
- add event/news specialists;
- improve hold/exit logic so capital becomes available for more valid opportunities;
- test parallel specialist combinations when causally and operationally valid.

If a candidate achieves good quality but insufficient opportunity contribution, DELTA should treat opportunity generation/capture as a refinement target rather than accepting low activity by default.

## 12. Interaction with GOV-009 news/event handling

Medium/high-impact news is a potential source of additional opportunity density.

News-aware specialists must report how many unique opportunities and executed trades they add to the composite, separately from ordinary session activity.

A news stand-down rule may be valid for a specific event class, but systematic event avoidance must be evaluated for the opportunity capacity it removes.

## 13. Future numeric activity thresholds

This contract does not yet invent a minimum trades-per-day number.

Exact hard/soft thresholds for:
- opportunities/day;
- trades/day;
- winning trades/day;
- trade-count retention;
- acceptable zero-trade-day frequency;

remain subject to owner definition and later human review of the actual baseline/reference data.

Until those thresholds are frozen, DELTA must preserve and report the activity surface rather than optimize it away.

## 14. Human-review authority

The owner may later:
- define hard daily trade floors;
- define soft preferred trade-frequency targets;
- set per-session opportunity floors;
- set minimum additive contribution for a specialist;
- define acceptable duplicate/overlap tolerances;
- lock an activity metric in addition to primary metrics;
- exempt a narrowly protective component from direct opportunity generation.

## 15. No evidence-load authorization

This contract defines architecture and evaluation semantics only.

It does **not** authorize loading R9 REAL, R9 SYNTH, R9 OVERFIT, Coinexx reports, R9 ticklogs, Dukascopy tick files, or external news/event datasets. Existing owner evidence-loading restrictions remain active.
