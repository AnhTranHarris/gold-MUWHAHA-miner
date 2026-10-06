# DELTA-B — Side Research Sandbox

## Purpose

DELTA-B is an isolated research branch and folder for vertical-stack XAUUSD experimentation that must not disturb the active `delta` lineage.

Parent lineage at fork: `delta`  
Research branch: `delta-b`  
Research folder: `research/delta-b/`

Nothing in DELTA-B is production-approved. Promotion back to `delta`, MQL5 translation, or EA release requires explicit owner authorization.

## Vertical Research Stack

DELTA-B develops one layer at a time and freezes each layer only after it answers its assigned question well enough for the next layer to inherit it.

1. **Grid Layer 1 — Intrinsic-Time Executable Lattice**
   - adaptive executable movement quantum `Q`
   - nested `Q / 2Q / 4Q / 8Q` event scales
   - midpoint state detection, executable Bid/Ask fills
   - directional-change / overshoot / reclaim / churn state
   - session-aware and medium/high-news-aware adaptation
   - no martingale, no adverse scaling

2. **Volume Profile Layer 2**
   - later layer only
   - answers location/auction questions the grid cannot answer

3. **MTF RSI Topology Layer 3**
   - later layer only
   - answers momentum propagation/exhaustion questions the lower layers cannot answer

4. **System-Wide Specialist Layer 4**
   - later layer only
   - specialists own distinct market mechanisms, not duplicated indicator votes

5. **Router / Profit Pyramid / Capital Governor Layer 5**
   - later layer only
   - favorable-only pyramiding; never loss chasing

## DELTA-B Research Constitution

- Tick-first and causal.
- Real ordered Bid/Ask chronology controls fills and PnL.
- Midpoint may be used for state detection to avoid interpreting spread movement as directional movement.
- August 2026 remains SEALED.
- Medium and high importance economic news/events are first-class causal state.
- Session state is first-class causal state.
- No future event outcome, future MFE/MAE, hindsight label, or favorable unknown intrabar ordering may enter inference.
- No martingale, recovery basket, adverse grid add, loss-based lot increase, or averaging into a losing thesis.
- New complexity must answer a question the current frozen layer cannot answer.
- No promotion because a backtest number is merely interesting.

## Restart Order

Read, in order:

1. `/CURRENT_STATE.json`
2. `research/delta-b/CURRENT_INFLIGHT.json`
3. `research/delta-b/GRID_LAYER_1_CONSTITUTION.md`
4. `research/delta-b/DB001_RESEARCH_PLAN.md`
5. `research/delta-b/MT5_PORT_CONTRACT.md`
6. `research/delta-b/SOURCE_PROVENANCE.md`

Resume only the first incomplete DELTA-B unit. Do not resume parent DELTA R037 work from this branch.

## Current Unit

`DB001A_EXECUTABLE_MOVEMENT_QUANTUM_AND_SESSION_EVENT_STATE_SPEC`

The first objective is not profitability optimization. It is to build and falsify a highly adaptive Grid Layer 1 whose state remains causal, fast, economically meaningful after costs, and stable enough for Volume Profile to inherit later.
