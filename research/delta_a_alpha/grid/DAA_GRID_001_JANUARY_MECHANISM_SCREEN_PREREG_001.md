# DAA GRID-001 — January Mechanism Screen Preregistration 001

**Unit:** `DAA_GRID_001_JANUARY_MECHANISM_SCREEN_PREREG_001`  
**Status:** FROZEN BEFORE COMPUTE  
**Dataset:** full January 2026 canonical Dukascopy XAUUSD ordered ticks  
**Execution surface:** `DUKAS_COINEXX_LIKE_P75`  
**Purpose:** discover structural event-direction mechanisms before building another physical grid.

## Research discipline

January is the hyper-fast discovery battleground, not the promotion set.

This unit will first build an event-label laboratory. A grid event is evaluated in shadow as both:
- mean reversion;
- continuation.

The goal is to identify causal pre-event features that distinguish which interpretation owns the next move.

No Martingale. No lot escalation. No multi-position averaging.

## Event clock J1

Source-inspired virtual chain:
- H1 rolling high/low context from completed/cached bars;
- source gap initially retained at $1.00 for comparability;
- downward chain event after one gap of displacement from rolling-high / prior downward event anchor;
- upward chain event after one gap of displacement from rolling-low / prior upward event anchor;
- event anchors are virtual, not physical positions;
- same event family cannot emit duplicate events at the same lattice coordinate.

This is an event generator only.

## Counterfactual labels

At each event, evaluate two shadow interpretations using executable Bid/Ask:
- MR: trade back toward the prior cell;
- CONT: trade in the crossing direction.

Initial first-passage label:
- target = 1 grid gap;
- adverse bound = 1 grid gap;
- maximum horizon = 5 minutes;
- unresolved events are labeled TIMEOUT.

Secondary diagnostics may use 30s / 60s / 120s horizons, but the 5-minute first-passage label is primary.

## Causal feature families allowed in Screen 001

Only compact path/regime features, all computed from data available at or before the event:
- signed return / displacement over 1s, 5s, 15s, 30s, 60s, 5m;
- path length over the same windows;
- directional efficiency ratio `abs(net displacement) / path length`;
- realized short-horizon volatility;
- crossing velocity;
- rolling H1 range position;
- distance from rolling H1 high/low;
- spread state on the modeled P75 surface.

No session, news, specialist, or macro categories yet.

## Structural hypotheses

H-A: high directional efficiency should favor continuation over mean reversion.

H-B: low directional efficiency / high path churn should favor mean reversion.

H-C: very high short-horizon volatility without directional efficiency should favor abstention rather than either side.

H-D: a simple causal regime router can materially reduce gross loss relative to always-contrarian source semantics without deleting most event velocity.

H-E: events where the initially chosen side loses quickly may support one bounded recovery flip when the opposite shadow path remains valid.

## Anti-overfit protocol

January will be split chronologically:
- discovery segment: first ~2/3 of January available ticks;
- internal validation segment: final ~1/3.

A mechanism is interesting only if its qualitative advantage survives both segments.

No exhaustive threshold optimizer is authorized.

Thresholds may be screened coarsely only to identify robust knees.

## Success criteria for advancing beyond event-label research

A mechanism family should show:
- clear reduction in wrong-direction loss frequency or gross-loss magnitude;
- preserved substantial event count;
- similar directional behavior in discovery and validation segments;
- no dependence on a single knife-edge threshold;
- a plausible path to fixed-0.01 bounded physical execution.

Only then build a physical single-owner simulator.

## Planned bounded sequence

J1 — virtual event clock + dual shadow labels.  
J2 — fixed-gap baseline: always-MR vs always-CONT.  
J3 — efficiency/range router.  
J4 — elastic spacing mutation.  
J5 — early thesis failure + information re-arm.  
J6 — one-shot recovery flip.  
J7 — shadow-regret memory if earlier stages justify it.

Each stage must persist its result before the next stage begins.

August remains sealed. Main `delta` remains read-only. MQL5 remains unauthorized.
