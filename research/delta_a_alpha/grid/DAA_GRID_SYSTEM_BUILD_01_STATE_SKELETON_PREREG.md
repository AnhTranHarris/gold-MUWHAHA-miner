# Delta-A-alpha — BUILD-01 State/Lifecycle Skeleton Preregistration

**Unit:** `DAA_GRID_SYSTEM_BUILD_01_STATE_SKELETON`  
**Status:** PREREGISTERED / ARCHITECTURE ONLY  
**Parent:** `DAA_GRID_SYSTEM_CLEAN_RESET_003`  
**System role:** whole-grid infrastructure before category-specific alpha refinement.

## Purpose

Create one deterministic, serialization-friendly state contract capable of representing every whole-system category required by the owner before any category is optimized.

BUILD-01 does **not** attempt to improve PnL. It is a sidecar state engine and diagnostic substrate.

## Immutable constraints

- XAUUSD only.
- Fixed lot = 0.01.
- Martingale prohibited.
- Loss-dependent sizing prohibited.
- Main `delta` read-only.
- August 2026 sealed.
- MQL5 translation unauthorized.
- Ordered right-edge causal timestamps only.
- No future-bar structure labels.
- No category may become a hidden stacked-confirmation vote.

## Required dimensions

The state object must represent:

1. session state;
2. volatility/drift regime;
3. timeframe-role state;
4. market-structure state;
5. trend/phase state;
6. scheduled-news/event state;
7. grid geometry state;
8. event genealogy;
9. execution/friction state;
10. risk-admission state;
11. specialist-routing state.

Each dimension initially supports neutral/unknown behavior.

## Required lifecycle

The skeleton must implement finite cycles and deterministic event identity:

- cycle creation;
- cycle ACTIVE state;
- event birth inside a cycle;
- event aging;
- event expiration;
- explicit cycle restart;
- restart reason;
- new cycle generation after restart;
- previous cycle/event identity never reused.

A restart is new information/state, never a rescue trade.

## Timeframe-role rule

No majority voting.

Roles are metadata only in BUILD-01:
- D1/H4 = environment;
- H1/M15 = structural location / parent lattice;
- M5/M1 = opportunity phase;
- ordered ticks = event/execution path.

Future builds may populate these states; BUILD-01 may not infer alpha from them.

## Neutrality requirement

When attached as a sidecar to an existing replay:
- it must not create orders;
- it must not modify prices;
- it must not alter lot size;
- it must not change stop/TP;
- it must not veto or authorize a legacy trade.

It records state only.

## Risk contract

Risk state enum must distinguish at least:
- OBSERVE_ONLY;
- OPEN_NEW_RISK;
- HOLD_EXISTING;
- REDUCE_ONLY;
- EXIT;
- HALT.

Default is OBSERVE_ONLY.

The skeleton itself has no authority to move from OBSERVE_ONLY to OPEN_NEW_RISK based on alpha.

## News/event contract

Represent at least:
- NORMAL;
- PRE_EVENT;
- RELEASE_WINDOW;
- POST_EVENT_SHOCK;
- POST_EVENT_DISCOVERY;
- NORMALIZED.

BUILD-01 stores state only; historical-event data is not introduced until BUILD-06.

## Geometry contract

Store, without optimizing:
- parent anchor;
- child gap;
- min/max gap;
- long/short asymmetry multiplier;
- last geometry update;
- geometry reason;
- cycle center/recenter marker.

Neutral defaults must be valid.

## Event genealogy contract

Each event must retain:
- event ID;
- cycle ID;
- sequence within cycle;
- birth timestamp;
- last update timestamp;
- parent/child cell;
- crossing direction;
- recross count;
- penetration;
- source state snapshot;
- physical ownership flag;
- re-arm eligibility.

## Specialist routing contract

The future-facing output object must be able to carry:
- event ID;
- current session/regime/structure/trend/news state;
- geometry;
- primary direction hypothesis;
- alternative direction;
- horizon;
- friction;
- risk state;
- recovery state.

BUILD-01 leaves hypotheses UNCLASSIFIED/ABSTAIN.

## Category-ledger hooks

Provide deterministic counters/accumulators so future builds can report economics by:
- session;
- regime;
- timeframe-role state;
- structure state;
- trend phase;
- news/event state.

At BUILD-01 these hooks are validated with synthetic fixtures only.

## QA gates

BUILD-01 passes only if:
1. module imports/compiles;
2. default state is neutral and fixed-lot 0.01;
3. deterministic cycle/event IDs reproduce exactly;
4. cycle restart produces a new identity;
5. timestamps cannot move backwards;
6. event sequence cannot collide inside a cycle;
7. serialization is deterministic JSON-safe data;
8. category ledger accumulates without changing trading authority;
9. no alpha/trading signal is emitted;
10. no reference to deleted legacy January refinement is required.

## Promotion result

A passing BUILD-01 becomes the **architecture floor**, not a profit milestone.

Next unit after parity is:
`DAA_GRID_SYSTEM_BUILD_02_ELASTIC_GEOMETRY_PREREG`

BUILD-02 will be the first post-reset component allowed to test an economically meaningful system mechanic.
