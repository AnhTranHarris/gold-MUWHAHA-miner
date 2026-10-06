# R9 Delta-A-alpha Grid System — Initial Redesign 001

**Status:** CONCEPTUAL ARCHITECTURE FROZEN — NO CODE / NO TESTS YET

## Objective

Replace the YouTube grid's physical averaging logic with a system-wide XAUUSD opportunity lattice that can:
- preserve high event density;
- reduce wrong-direction trades;
- detect thesis failure early;
- recover still-valid opportunities without Martingale;
- support future routing to roughly 6–16 specialists;
- reduce the burden of bridging the R9 REAL -> SYNTH gap.

The grid layer is infrastructure, not a standalone specialist.

## Core shift

Old:
`GRID LEVEL -> AUTOMATIC CONTRARIAN TRADE`

New:
`GRID LEVEL -> EVENT -> REGIME/STATE -> MEAN REVERSION / CONTINUATION / ABSTAIN -> RISK ADMISSION -> BOUNDED 0.01 OWNERSHIP -> RECOVERY / ROUTING`

A grid crossing is information, not an order.

## Retain from the creator

- rolling high/low spatial reference;
- chained spatial information;
- simple reconstructible grid geometry;
- high opportunity density.

## Remove as defaults

- automatic contrarian entry on every crossing;
- open-ended physical averaging;
- no-stop inventory;
- loss-dependent sizing;
- fixed spacing in every condition;
- one directional interpretation for every regime;
- net-profit-only optimization.

## Architecture

### 1. Parent / child lattice

Parent lattice:
- slower structural location;
- range/trend ownership;
- extreme/interior/transition context.

Child lattice:
- fast event clock;
- crossing/path geometry;
- event identity.

The layers have different jobs; this is not timeframe voting.

### 2. Elastic spacing

Source-backed concepts:
- ATR/NATR scaling;
- min/max clamps;
- hysteresis;
- update cooldown.

Initial family:

`gap_t = clamp(max(noise_floor, spread_floor, k_vol*vol_t, k_parent*parent_scale), gap_min, gap_max)`

Exact formula remains unfrozen.

### 3. Event identity

Each crossing creates or updates an event object rather than automatically creating another trade.

Useful fields include:
- parent/child cell;
- crossing direction;
- velocity;
- penetration depth;
- recross count;
- volatility;
- spread;
- regime;
- interpretation state;
- recovery state.

### 4. Regime semantics

Candidate states:
- RANGE;
- TREND_UP;
- TREND_DOWN;
- VOL_SHOCK;
- TOXIC/HOSTILE;
- TRANSITION.

Useful public mechanism:

`range_score = sum_abs_returns / (abs(net_return) + eps)`

High score suggests chop; low score plus meaningful displacement suggests trend.

Regime changes the meaning of a crossing, not only whether trading is allowed.

### 5. Directional interpretation

Every event can become:
- MEAN_REVERSION;
- CONTINUATION;
- ABSTAIN.

**Original mutation — quiet-trend inversion:** when drift dominates oscillation, a source-style contrarian event may invert into continuation. A fall-through can become SHORT continuation; a rise-through can become LONG continuation.

### 6. Early thesis failure

A hard stop is the final safety bound, not the first indication of failure.

Potential causal failure evidence:
- next-cell acceptance;
- failed reclaim;
- no expected MFE within a bounded time;
- persistent adverse velocity;
- regime transition;
- structural-break signal.

### 7. Opportunity recovery

Loss means RECLASSIFY, not add size.

Initial state concept:

`NEW -> CLASSIFY -> ACTIVE -> DEGRADED -> EXIT -> RECOVERY_WAIT -> RECLASSIFY -> RECOVER / RETIRE`

**Original mutation:** maximum one physical recovery flip per event unless later research proves a different bounded rule.

### 8. Counterfactual shadow twin

**Original high-potential mutation.**

At each event:
- execute at most one direction physically, or abstain;
- track the opposite interpretation in shadow for a bounded horizon.

Compute:

`directional_regret = shadow_opposite_value - executed_value`

This can expose event classes that are systematically interpreted backwards without paying for two real positions.

### 9. Event-health memory

Use deterministic decayed memory for:
- mean-reversion outcomes;
- continuation outcomes;
- recovery outcomes;
- event families / lattice regions.

Concept:

`health_t = decay * health_(t-1) + signed_outcome_t`

This adapts interpretation without Martingale.

### 10. Information-based re-arm

Do not re-enter merely because time passed.

Require new information:
- new cell;
- reclaim/acceptance change;
- regime transition;
- parent transition;
- structural break;
- materially different event fingerprint.

### 11. Risk admission

Actions are classified as:
- increase risk;
- reduce risk;
- retire/cancel.

When risk state degrades, new risk can be blocked while exits remain allowed.

Potential scopes:
- event;
- lattice region;
- grid system;
- account.

Fixed 0.01 and $100/$200/$300 survivability remain mandatory.

### 12. Finite event age

Events and directional assumptions expire. No event is allowed to become an indefinitely valid excuse to wait for price to return.

### 13. Specialist routing

The grid should eventually emit a compact opportunity object:

`{event_id, location, regime, primary_direction, alternative_direction, recovery_state, horizon, risk_state, context}`

Future specialists may accept, reject, wait, or reinterpret it.

## Gross-loss attack hierarchy

1. **Prevent** wrong direction — regime semantics and path classification.
2. **Detect** wrong direction early — thesis-failure logic.
3. **Prevent repetition** — event identity and information-based re-arm.
4. **Recover** the opportunity — one-shot causal flip / shadow evidence.
5. **Contain residual loss** — hard stop and risk-admission state.

Hard stops alone are not considered a breakthrough.

## January conceptual sequence

No testing is authorized by this document.

When testing starts:
- J1: virtual grid/event clock;
- J2: elastic spacing;
- J3: range vs continuation interpretation;
- J4: early thesis failure;
- J5: information-based re-arm;
- J6: one-shot opportunity recovery;
- J7: counterfactual shadow twin.

The objective is structural breakthroughs, not threshold polishing.

## Research question

Can the creator's high-density grid geometry be transformed from a toxic averaging strategy into a state-aware opportunity/recovery engine that materially reduces gross loss and drawdown while preserving enough velocity to help close the R9 REAL -> SYNTH gap?
