# DAA GRID-001 — Gross-Loss / Drawdown Mechanism Hunt 001

**Unit:** `DAA_GRID_001_GROSS_LOSS_DRAWDOWN_MECHANISM_HUNT_001`  
**Status:** PRE-SEARCH MUTATION MAP PERSISTED — SOURCE HUNT IN PROGRESS  
**Target system:** `R9_DELTA_A_ALPHA_GRID_SYSTEM`  
**Research scope:** narrow first pass on gross loss and drawdown only  
**Coding:** none in this unit  
**Testing:** none until mechanism shortlist is frozen

## Starting evidence

The YouTube/source grid supplied valuable **event density**, but the physical inventory mechanism failed.

Forensic source-style replay:
- 20,678 Stage-A trades;
- 98.87% closed win rate;
- +$3,755.85 net;
- PF ~1.20;
- ~2,068 trades/active day;
- 250 simultaneous positions;
- ~$20,078 max equity drawdown;
- failed $100/$200/$300 survivability.

Bounded physical-grid screen:
- 12 preregistered cap/stop variants;
- every variant negative;
- best variant: -$2,301.82, PF ~0.782;
- physical averaging inventory retired.

Therefore the redesign should **retain the grid as a sensing/event lattice while removing its assumption that every lattice crossing deserves contrarian physical inventory.**

## Original mutation hypotheses — not externally validated

The following are **HYPOTHESIS / ORIGINAL MUTATION** ideas. They are intentionally aggressive. They become research candidates only after source comparison and causal testing.

### H1 — Virtual grid / event-only lattice

Grid levels become **sensors**, not automatic positions.

A level crossing emits an event with:
- parent lattice location;
- direction of arrival;
- crossing speed;
- displacement;
- local volatility;
- spread/friction;
- recent event history;
- session/event context later in the program.

No trade is mandatory.

Purpose:
- preserve opportunity density;
- eliminate warehoused inventory;
- let downstream logic decide mean reversion, continuation, or abstention.

### H2 — Single-owner event state machine

Every event receives an identity and can have at most one active grid-owned 0.01 position.

State sketch:

`NEW -> CLASSIFY -> LONG / SHORT / ABSTAIN -> HEALTHY / DEGRADED -> EXIT -> RECOVERY_WAIT -> RECLASSIFY / RETIRE`

A failed thesis cannot immediately spawn another same-direction trade from the same event identity.

Purpose:
- prevent repeated wrong-direction entries;
- make opportunity recovery explicit;
- separate event persistence from position persistence.

### H3 — One-shot recovery / causal flip

A stopped or rapidly degrading trade does **not** trigger averaging.

Instead it enters a recovery state.

A reversal is allowed only when causal post-entry evidence shows that the original event was misclassified rather than merely noisy.

Candidate evidence later to test:
- failed reclaim;
- adverse crossing speed;
- directional persistence;
- new lattice-cell acceptance;
- microstructure imbalance;
- lack of expected MFE;
- path-shape change.

Initial research rule: maximum one recovery flip per event unless later evidence strongly supports a different bounded policy.

Purpose:
- recover valuable opportunities;
- avoid serial same-direction losses;
- cap path-dependent loss chains.

### H4 — Elastic lattice spacing

The source fixed 100-point/$1 grid is likely too rigid.

Candidate formula family:

`gap = max(noise_floor, spread_floor, k_vol * local_volatility, k_parent * parent_cell_scale)`

Alternative: causal quantile spacing from recent absolute returns/range rather than ATR alone.

The gap may expand during high noise/turbulence and contract during stable liquid conditions.

Purpose:
- reduce false crossings;
- preserve event density where the market can support it;
- avoid treating a $1 move as equivalent under every volatility regime.

### H5 — Parent/child lattice rather than flat grid

Use coarse structural cells and fast child cells with different jobs.

Parent lattice:
- determines location/structural ownership;
- identifies whether the fast event is occurring at an extreme, interior, transition, breakout, or reclaim region.

Child lattice:
- generates fast event timing;
- measures path geometry;
- supplies high-density candidates.

This is **not timeframe voting**.

Purpose:
- reduce low-quality contrarian trades in strong directional states;
- preserve scalping density without ignoring larger structure.

### H6 — Path-shape classification at the crossing

The important feature may not be *that* price crossed a grid level, but *how* it crossed.

Candidate causal descriptors:
- approach velocity;
- acceleration;
- time spent near level;
- penetration depth;
- number of recrossings;
- retrace fraction;
- one-sided tick persistence;
- recent MFE/MAE of similar events;
- distance from parent lattice boundary;
- spread expansion/contraction.

Output:
`MEAN_REVERSION / CONTINUATION / ABSTAIN`.

Purpose:
- attack wrong-direction gross loss directly.

### H7 — Event-health / regret memory

Each lattice region maintains a causal health score.

Conceptual update:

`health_t = decay * health_(t-1) + reward_or_regret_t`

Repeated same-type failures lower authority for that interpretation without permanently disabling the region.

Possible separate memories:
- mean-reversion health;
- continuation health;
- recovery success;
- adverse excursion;
- recent friction.

Purpose:
- prevent the system from repeatedly making the same mistake in a temporarily changed market.

### H8 — Early thesis-failure exit

The source grid waits for TP or effectively infinite recovery; the bounded grid waits for a fixed stop.

Both may be too crude.

Candidate early-failure mechanisms:
- no expected MFE within a causal time budget;
- adverse velocity beyond a state-conditioned threshold;
- accepted move into the next lattice cell;
- loss of reclaim;
- microstructure persistence against the position;
- parent-state invalidation.

Purpose:
- reduce gross loss *before* the full hard stop is consumed.

Hard stop remains a final safety bound, not the primary decision mechanism.

### H9 — Re-arm on new information, not elapsed cooldown alone

After an exit/loss, a new trade requires a meaningful state transition:
- new cell;
- reclaim;
- breakout acceptance;
- direction-state change;
- parent-lattice transition;
- sufficiently different event fingerprint.

Purpose:
- suppress churn and repeated wrong-direction trades while retaining genuine new opportunities.

### H10 — System-wide routing contract

The grid should ultimately output a compact opportunity object rather than own every trade:

`{event_id, location, proposed_direction, alternative_direction, confidence/state, recovery_state, horizon, risk_budget, context}`

Future specialists can accept, reject, or reinterpret the opportunity.

Purpose:
- make the grid a shared infrastructure layer for the eventual 6–16 specialists;
- reduce duplicated entry machinery across specialists;
- make opportunity recovery reusable system-wide.

## What the source hunt must answer

This research pass should search for reconstructible public mechanisms that can materially improve:
1. gross-loss containment;
2. drawdown containment;
3. wrong-direction detection;
4. bounded recovery/reversal;
5. dynamic grid spacing;
6. event/state identity and re-arm logic.

Priority is **mechanism quality**, not finding systems with high advertised win rates.

Useful public code or formulas should be mapped to the mutation hypotheses above or added as new mechanism families.

## Explicit anti-goals

Do not promote:
- Martingale;
- loss-dependent size escalation;
- uncapped averaging;
- grid rescue baskets;
- “no stop because price returns eventually”;
- opaque commercial claims;
- trivial threshold micro-tuning;
- trade-count destruction masquerading as drawdown improvement.

## Research success for this unit

A successful source hunt should finish with a small set of **structural mechanism families** strong enough to justify January tick-level mutation tests.

The desired next step is not “optimize the grid.”

It is:

**redesign the meaning of a grid event.**
