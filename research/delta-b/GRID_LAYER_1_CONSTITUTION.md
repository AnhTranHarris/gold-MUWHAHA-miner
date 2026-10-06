# DELTA-B Grid Layer 1 Constitution

Status: **RESEARCH SPECIFICATION — NOT AN EA, NOT MQL5-AUTHORIZED**

## 1. Layer Mission

Grid Layer 1 must answer only:

> Has economically meaningful XAUUSD movement occurred, at what intrinsic scale, and is that movement behaving like transit, rotation, escape, failed escape/reclaim, or churn/shock?

It must not try to answer auction-location questions reserved for Volume Profile, momentum-topology questions reserved for RSI, or specialist ownership questions reserved for later layers.

## 2. Core Architecture

The canonical grid is an **Intrinsic-Time Executable Lattice**, not a conventional fixed-price order grid.

Define a causal movement quantum:

```
Q_t = max(Q_cost,t, Q_noise,t, Q_floor)
```

with:

```
Q_cost,t  = k_cost  * estimated_round_trip_friction_t
Q_noise,t = k_noise * robust_micro_noise_t
```

The exact estimators and coefficients must be predeclared by each bounded experiment and selected from broad stable neighborhoods rather than single fitted optima.

Nested event scales:

- L0 = 1Q
- L1 = 2Q
- L2 = 4Q
- L3 = 8Q

No layer may create actual trade orders merely because a lattice boundary is touched.

## 3. State Price vs Execution Price

State detection:

```
mid_t = (Bid_t + Ask_t) / 2
```

Execution and realized PnL:

- BUY enters at executable Ask and exits at executable Bid.
- SELL enters at executable Bid and exits at executable Ask.
- Commission/slippage assumptions must be explicit.
- Midpoint is never treated as an executable fill.

This separation prevents spread changes from being mistaken for directional alpha.

## 4. O(1)-Style Tick State

Each tick updates only compact rolling state:

- Bid / Ask / midpoint
- current spread and spread percentile
- micro-noise estimator
- tick-arrival rate
- short-horizon directional efficiency
- active extrema for L0-L3
- event age in milliseconds/ticks
- session state
- scheduled event state
- shock state

Heavier calculations should run only on state transitions or scheduled bounded refreshes.

## 5. Five Primary Grid States

Exactly five primary classes are permitted in Grid Layer 1:

### TRANSIT
Clean directional travel through intrinsic cells with high displacement relative to reversal/churn.

### ROTATION
High local movement but low higher-scale displacement, repeated crossings/reclaims, or long residence.

### ESCAPE
Smaller scales initiate movement and progressively larger intrinsic scales confirm the same direction.

### FAILED_ESCAPE_RECLAIM
A smaller-scale escape fails higher-scale acceptance and returns through the originating intrinsic boundary.

### CHURN_SHOCK
Economically hostile boundary oscillation, abnormal spread/tick-rate transition, or violent state change not safely classifiable as ordinary transit/rotation.

Substates may be diagnostic, but no experiment may silently proliferate primary regimes to fit history.

## 6. Cross-Scale Coherence

For each active scale:

```
d_k ∈ {-1, 0, +1}
```

Define causal coherence:

```
coherence = abs(sum(d_k)) / active_scale_count
```

Grid Layer 1 may use cross-scale coherence for state classification and confirmation strength. It may not use future continuation outcome to set coherence.

## 7. Directional-Change Hysteresis

Grid boundaries are event thresholds, not instant trade triggers.

A boundary transition requires causal confirmation from one or more predeclared conditions such as:

- displacement beyond threshold
- minimum residence time
- directional efficiency
- low reversal count
- cost-adjusted movement surplus

Confirmation may be fast in clean movement and slow or absent in noisy movement.

The engine must explicitly reject rapid line-cross oscillation that would otherwise create repeated false breaks.

## 8. Overshoot Survival and Event Half-Life

For every confirmed directional-change event, maintain lagged historical estimates of:

```
P(overshoot >= xQ | scale, context)
P(continue | event_age, scale, context)
```

These estimates must use only prior completed events. The current event's future path cannot enter its own decision state.

Grid Layer 1 may use these surfaces as diagnostics and, after independent validation, as causal state inputs.

## 9. Session-Adaptive Grid

Session is first-class state, not a binary filter.

Initial canonical session labels should be clock-defined and DST-safe:

- ASIA
- LONDON_OPEN_TRANSITION
- LONDON
- LONDON_NY_OVERLAP
- NEW_YORK
- ROLLOVER_OFFSESSION

Session adaptation may affect:

- Q floor/multiplier
- micro-noise horizon
- hysteresis width
- confirmation displacement
- confirmation time
- cost buffer
- cooldown
- shock threshold
- favorable-only pyramid authority later

Session logic may not encode hindsight such as "London was profitable today."

## 10. Medium/High News and Event Adaptation

Scheduled economic events with importance **MEDIUM or HIGH** are first-class causal state.

Canonical event phases:

- NORMAL
- PRE_EVENT_MEDIUM
- PRE_EVENT_HIGH
- EVENT_RELEASE_WINDOW
- POST_EVENT_DISCOVERY
- POST_EVENT_STABILIZATION

The exact pre/post windows are research parameters, not assumed truths.

The grid may react by:

- expanding Q when friction/noise expands
- widening hysteresis
- increasing required cost surplus
- reducing or blocking new entry authority
- shortening stale-event half-life
- raising shock sensitivity
- extending cooldown after violent release behavior
- preserving existing risk controls

The system must not assume news direction from the calendar event itself unless a later reconstructible specialist explicitly and causally receives released values at/after their observable timestamp.

### Unscheduled Events

Unscheduled headlines cannot be reliably preclassified by the MT5 economic calendar. Grid Layer 1 therefore uses a separate causal **market-shock detector** based only on observable quote behavior such as:

- spread percentile jump
- tick-arrival jump
- micro-volatility jump
- abnormal 1Q/2Q event burst
- abrupt directional efficiency transition

A shock detector is not a news classifier. It only changes grid operating state.

## 11. Adaptive Q Must Not Become Parameter Chaos

Q is allowed to self-adjust, but only through a small transparent causal function.

Forbidden:

- dozens of independently fitted multipliers by month
- per-day hidden optimization
- parameters chosen using current-event future outcome
- dynamic rules that cannot be translated deterministically to MQL5 later

Preferred:

- robust rolling quantiles/medians
- bounded multipliers
- coarse session/event regimes
- broad stable parameter neighborhoods
- explicit minimum/maximum Q clamps

## 12. Martingale Prohibition

Hard failures:

- adding because price moved against an open position
- increasing lot size after a realized loss
- recovery baskets
- geometric adverse-position accumulation
- moving stops farther away to make room for another grid order

Permitted later only after separate validation:

- favorable-direction pyramiding after verified MFE
- decreasing or bounded add sizes
- unified stop advancement
- post-add worst-case basket risk that does not increase beyond the declared cap

## 13. Breakthrough Test

Grid Layer 1 is successful only if it creates a material whole-system improvement, not merely prettier states.

Internal research hurdle:

- target at least ~30% reduction in R9 REAL gross loss
- target at least ~30% reduction in R9 REAL max drawdown
- preserve meaningful high-frequency/scalping opportunity density
- improve or materially de-risk the seven-month realized result
- no hidden leverage increase
- no survival improvement created by simply refusing to trade

These are research hurdles, not automatic promotion criteria. DELTA governance remains controlling.

## 14. Layer Freeze Rule

Once Grid Layer 1 passes a robust freeze checkpoint, later layers may consume its outputs but may not silently rewrite its core semantics.

A later layer is allowed only when it answers a new question Grid cannot answer well:

- Volume Profile: **where in accepted/disaccepted value is this grid event occurring?**
- RSI: **is directional energy strengthening, propagating, exhausting, or diverging?**
- Specialist layer: **which mechanism owns the state?**

This is the vertical-stack rule that prevents permanent "what if" research loops.
