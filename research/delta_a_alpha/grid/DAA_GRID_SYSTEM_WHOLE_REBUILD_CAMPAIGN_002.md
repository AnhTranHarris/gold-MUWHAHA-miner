# Delta-A-alpha — Whole-Grid System Rebuild Campaign 002

**Status:** FROZEN CAMPAIGN CONTRACT  
**Owner direction:** Improve the grid as a whole before returning to narrow refinement.  
**System role:** R9 REAL support infrastructure for a future portfolio of roughly 6–16 specialists.  
**Primary objective:** Close a material share of the R9 REAL -> R9 SYNTH performance gap before specialists are asked to carry the remainder.

## Immutable constraints

- XAUUSD only.
- Fixed 0.01 lot only.
- Martingale prohibited.
- Loss-dependent sizing prohibited.
- Uncapped averaging prohibited.
- Main `delta` branch is read-only.
- August 2026 remains sealed.
- MQL5 implementation remains unauthorized.
- Ordered executable Bid/Ask accounting is mandatory.
- Future data / completed-bar leakage is prohibited.
- New mechanics must be reconstructible from public logic or explicitly marked as original Delta-A-alpha hypotheses.

## Why the campaign order changed

The narrow proof/admission lane produced a strong selectivity diagnostic, but owner direction now requires the **grid system architecture itself** to be strengthened first.

The completed proof work is retained and may later be plugged into the rebuilt grid. It is paused, not discarded.

This campaign therefore moves from:

`local signal refinement -> more local signal refinement`

to:

`stable whole-system state model -> high-impact system mechanics -> category diagnostics -> later local refinement`

## Canonical performance reference

Canonical Jan-Jul R9 account-level benchmark:

R9 REAL:
- net: **-$50,285.28**
- trades: **236,647**
- PF: **0.37507**
- win rate: **43.2649%**
- trades/active day: **1,588.23**

R9 SYNTH:
- net: **+$309,122.85**
- trades: **219,342**
- PF: **20.0362**
- win rate: **87.1406%**
- trades/active day: **1,472.09**

Net performance gap:
**$359,408.13**

## Human milestone ladders

Two scoreboards are maintained so the project does not confuse "closing the REAL deficit" with "reaching the SYNTH frontier."

### Primary — R9 SYNTH attainment

`synth_attainment = candidate_JanJul_net / R9_SYNTH_JanJul_net`

Net references:
- **30%:** +$92,736.86
- **60%:** +$185,473.71
- **90%:** +$278,210.57
- **100%:** +$309,122.85
- **120%:** +$370,947.42

This is the owner's human-facing 30%-interval progress ladder.

### Secondary — REAL -> SYNTH gap closure

`gap_closure = (candidate_net - R9_REAL_net) / (R9_SYNTH_net - R9_REAL_net)`

Net references:
- **30%:** +$57,537.16
- **60%:** +$165,359.60
- **90%:** +$273,182.04
- **100%:** +$309,122.85

Gap closure answers how much of the original REAL deficit has been removed.

Neither score can promote a build by itself. Velocity, monthly consistency, executable economics, gross loss, equity drawdown, $100/$200/$300 survivability, and residual inventory remain mandatory.

## Milestones are soft, not single-metric promotion gates

Net gap closure is the headline human metric.

A build cannot be accepted merely because net rises while it:
- destroys trade velocity;
- worsens equity drawdown catastrophically;
- fails $100/$200/$300 survivability;
- concentrates all improvement in one month;
- hides residual inventory;
- relies on event/news look-ahead;
- increases lot size;
- introduces Martingale;
- degrades execution realism.

The 30% bands are navigation markers, not permission to game one number.

## Floor-lock rule

Every accepted system build becomes the new research floor.

A child build may replace its parent only if one of these is true:

1. it improves gap closure while preserving core risk/velocity behavior; or
2. it materially improves survivability / gross-loss / drawdown behavior while keeping headline economics close enough to the parent to justify the trade-off.

A failed child is recorded but does not replace the floor.

No later experiment silently retunes or mutates an accepted parent.

## Whole-system state contract

Every grid event will eventually carry these state dimensions even if a dimension initially has neutral behavior:

### 1. Session state

Examples:
- ASIA;
- LONDON_OPEN;
- LONDON;
- OVERLAP;
- NEW_YORK;
- LATE_NY;
- ROLLOVER / TRANSITION.

Role:
sets priors for geometry, expected event density, horizon, and interpretation.

### 2. Volatility / drift regime

Examples:
- RANGE_QUIET;
- RANGE_ACTIVE;
- TREND_QUIET;
- TREND_VOLATILE;
- TRANSITION;
- EVENT_SHOCK;
- TOXIC.

Role:
changes grid semantics and geometry.

### 3. Timeframe-role state

No timeframe voting.

Proposed roles:
- D1/H4: environment / long-horizon volatility-drift;
- H1/M15: structural location / parent lattice;
- M5/M1: opportunity phase;
- ticks: event identity and executable path.

### 4. Market-structure state

Candidate primitives:
- confirmed swing high / low;
- previous session/day high / low;
- BOS;
- CHoCH;
- sweep / reclaim;
- retracement depth;
- structure transition.

Role:
anchors the lattice and provides invalidation / cycle restart information.

### 5. Trend / phase state

At minimum:
- directional continuation;
- pullback;
- exhaustion;
- post-trend reversion;
- compression / balance.

Role:
decides whether a crossing is interpreted as continuation, reversion, or observe-only.

### 6. News / scheduled-event state

States:
- NORMAL;
- PRE_EVENT;
- RELEASE_WINDOW;
- POST_EVENT_SHOCK;
- POST_EVENT_DISCOVERY;
- NORMALIZED.

Initial scope:
high-impact USD events relevant to XAUUSD.

### 7. Geometry state

Contains:
- parent anchor;
- child gap;
- directional asymmetry;
- min/max bounds;
- last geometry update;
- hysteresis state;
- recenter/restart reason.

### 8. Event genealogy

Contains:
- event ID;
- parent/child cell;
- first crossing;
- recrosses;
- penetration;
- approach velocity;
- structural state at birth;
- regime/session/news state at birth;
- re-arm eligibility;
- prior physical ownership.

### 9. Risk-admission state

Actions:
- OPEN_NEW_RISK;
- HOLD_EXISTING;
- REDUCE_ONLY;
- EXIT;
- OBSERVE_ONLY.

No category gets to override account safety.

### 10. Specialist-routing state

Future output contract:

`{event_id, session, regime, structure, trend_phase, news_state, geometry, direction_hypothesis, alt_direction, horizon, friction, risk_state, recovery_state}`

The grid infrastructure may later hand this to 6–16 specialists.

## Critical design rule — no stacked-confirmation soup

The categories above do not all cast votes.

Each category owns a different question:

- session: **when / what prior?**
- volatility/drift regime: **what market process?**
- timeframe hierarchy: **what scale owns what decision?**
- structure: **where are we?**
- trend phase: **what direction/behavior is plausible?**
- news/event: **is ordinary market semantics temporarily invalid?**
- geometry: **where are the event coordinates?**
- execution/friction: **is the opportunity economically tradable?**
- risk state: **may new risk be added?**

This avoids repeated filters that simply destroy trade count.

## Whole-system rebuild sequence

### BUILD-00 — Clean evidence floor

Active floor contains only:
- canonical R9 REAL/SYNTH Jan-Jul benchmark;
- exact creator-code/source reconstruction;
- source-style forensic grid result;
- bounded physical-grid negative screen;
- whole-system public-source mechanism hunt;
- this system-first campaign.

Owner-directed cleanup `DAA_GRID_SYSTEM_CLEAN_RESET_003` removed the out-of-order January-specific refinement stack from the active lineage. The deleted work remains recoverable on named rollback branches but is **not active evidence**.

A legacy idea may return only after the whole-system parent layer it depends on exists and the mechanism is freshly preregistered/retested in the new order.

### BUILD-01 — Stable state skeleton + finite cycles

Implement the state object and cycle/restart lifecycle with neutral defaults.

No alpha claim.

Required:
- event genealogy;
- finite event/cycle age;
- restart reasons;
- reduce-only risk state;
- cost accounting hooks;
- category diagnostics.

### BUILD-02 — Elastic geometry

Add:
- volatility/spread/noise floor;
- min/max gap;
- hysteresis;
- cooldown;
- structural recenter trigger.

Accept only if event quality improves without unacceptable velocity loss.

### BUILD-03 — Regime semantic morphing

Add:
- range vs trend;
- quiet vs volatile;
- transition/shock;
- range -> mean-reversion interpretation;
- trend -> continuation interpretation;
- transition/shock -> observe/reduce-only as evidence dictates.

### BUILD-04 — Session morphing

Add explicit session priors and category diagnostics.

No hard blanket session veto unless evidence supports it.

### BUILD-05 — MTF structural lattice

Add:
- role-separated D1/H4/H1/M15/M5/M1/tick context;
- swing structure;
- previous session/day extrema;
- BOS/CHoCH;
- sweep/reclaim;
- structural anchors and invalidations.

### BUILD-06 — News/event state

Add deterministic historical event dataset for research and live/demo MQL5-calendar compatibility design.

No backtest may query future event outcomes.

### BUILD-07 — State-conditioned cost/expectancy admission

Estimate:
- expected MFE;
- expected MAE;
- expected horizon;
- friction.

Event becomes tradable only if expected excursion clears cost plus safety margin.

### BUILD-08 — Event memory / recovery

Add:
- category health;
- shadow counterfactual;
- information-based re-arm;
- bounded one-shot recovery if evidence supports it.

### BUILD-09 — Whole-system January integration

Run the accepted mechanisms together.

Diagnose:
- which categories still account for gross loss;
- which destroy velocity;
- which improve opportunity recovery.

### BUILD-10 — Jan-Jul validation

Only after January architecture is stable.

Report:
- monthly ledger;
- aggregate gap closure;
- category health;
- small-account survivability;
- velocity;
- gross loss;
- equity drawdown.

## Research categories must become measurable

For every accepted build, produce a category ledger by:
- session;
- regime;
- timeframe-role state;
- structure state;
- trend phase;
- news/event state.

The purpose is to answer:

**Which category still prevents the grid system from reaching the next 30% milestone?**

This replaces broad retuning with targeted refinement.

## High-impact source-backed mechanics approved for testing

Approved research families:
- adaptive spacing with hysteresis/cooldown;
- finite/restartable cycles;
- regime-dependent grid mode;
- quiet-trend continuation inversion;
- explicit session states;
- MTF role separation;
- swing/BOS/CHoCH/previous-high-low structural anchors;
- liquidity sweep/reclaim state;
- deterministic economic-event state;
- cost/edge gate;
- event genealogy;
- reduce-only latches.

Not approved as evidence:
- advertised win rate;
- hidden production thresholds;
- opaque pretrained models;
- variable lot sizing;
- Martingale;
- DCA rescue logic;
- unbounded grids;
- optimization without causal/OOS controls.

## Immediate next scientific unit

`DAA_GRID_SYSTEM_BUILD_01_STATE_SKELETON_PREREG`

Goal:
define and implement the neutral state/lifecycle skeleton without attempting to optimize entries.

This is deliberately architectural. Refinement resumes only after the system can represent every required category coherently.

