# DAA GRID-001 — Gross-Loss / Drawdown Mechanism Hunt 001

**Unit:** `DAA_GRID_001_GROSS_LOSS_DRAWDOWN_MECHANISM_HUNT_001`  
**Status:** COMPLETE — FIRST STRUCTURAL MECHANISM SHORTLIST FROZEN  
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


# Source hunt findings

## S1 — Exact YouTube creator code located

Author repository:
`MegaJoctan/omegafx-youtube-shared-files`

Inspected commit:
`fc232fb4ffa9ed854d8c398e6e7a6de28c5dc51f`

Authoritative tutorial files:
- `Python Grid Bot/grid_bot.py` — blob `1d5efa140b363941e7360bd0ae85ac7e04d0ecaa`
- `Python Grid Bot/grid_bot_backtest.py` — blob `3d4f66a2e57397c15876df795a629488b6278a7c`
- `Python Grid Bot/grid_bot_optimization.py` — blob `fd69caaa878643fcbe26070ae120e213d67b44ff`

This supersedes transcript-only reconstruction for source semantics.

### Exact source mechanics confirmed

- H1 timeframe.
- Rolling high/low window.
- Default source window = 48 bars.
- Fixed grid-gap parameter.
- BUY if current Ask falls below the high/last-BUY anchor by one gap.
- SELL if the same current Ask rises above the low/last-SELL anchor by one gap.
- BUY executes at Ask; SELL executes at Bid.
- TP = one grid gap.
- No intrinsic stop in source grid logic.
- Open-position anchoring means the latest still-open same-side position becomes the next anchor.
- Backtest variant adds a maximum position count.
- Backtest/optimization variant adds loss-dependent lot multiplication. Delta-A-alpha rejects this.
- Optimization searches grid gap/window/max orders but maximizes net profit only.
- Tutorial backtest modelling is 1-minute OHLC, not ordered real ticks.

### Source-code defects / research cautions

The live `grid_bot.py` should not be treated as production-quality reference code:
- its calls to `count_positions` / `last_position` omit the required terminal argument;
- `rates_cache` is initialized to the DataFrame class rather than a DataFrame instance/None;
- new-bar refresh depends on receiving a tick at an exact timeframe-second boundary.

The backtest file corrects some call-site issues, but the strategy semantics remain simplistic.

No LICENSE file was found in the inspected shared-files repository. Delta-A-alpha therefore treats it as an inspectable research source and performs clean-room reimplementation rather than copying substantial source.

### Scientific implication

The creator's strongest transferable idea is the **dense chained grid-event geometry**, not its position-management logic.

The largest weaknesses are:
- every crossing is interpreted contrarian;
- spacing is static;
- no regime distinction;
- no adverse-path thesis failure;
- no event identity/re-arm state;
- no recovery classification;
- risk optimization is outcome-first rather than risk-first.

---

## S2 — GridMaster Pro public MT5 implementation

Repository:
`sajidmahamud835/grid-master-pro-mt5-ea`

Inspected commit:
`c87474c1cf1d46cc13e0dc4b6508958a0b43eaba`

License: MIT.

Useful implemented mechanisms:
- ATR-based grid distance;
- explicit bullish / bearish / neutral grid mode;
- hard maximum orders;
- per-trade SL/TP;
- trailing stop;
- equity drawdown circuit breaker;
- pause after drawdown breach;
- broker stop-distance awareness;
- duplicate-price suppression.

Not adopted:
- dynamic lot sizing, because Delta-A-alpha is fixed 0.01;
- physical multi-position grid as the core architecture;
- automatic resume logic without independent evidence.

### Scientific implication

ATR spacing is reconstructible and immediately testable, but a drawdown kill switch is only a **last-line guard**. It does not repair wrong direction.

This supports H4 but does not solve H2/H3/H6.

---

## S3 — GRINDER adaptive smart-grid/risk architecture

Repository:
`bnzr-team/grinder`

Inspected commit:
`f216435c9549795edd12886d755f114b42b819fc`

No top-level LICENSE file was found at the inspected commit. Use as conceptual/public research evidence and clean-room reconstruct logic unless licensing is later clarified.

Useful reconstructible mechanisms:

### Volatility-aware adaptive step

`src/grinder/risk/adaptive_step.py`

Core pattern:
- derive candidate spacing from current volatility relative to a reference;
- clamp between min/max spacing;
- apply hysteresis so tiny changes do not churn geometry;
- apply cooldown so spacing does not oscillate tick-by-tick;
- on missing volatility, freeze last known geometry or fall back to base.

This materially improves H4 over naive `gap = k*ATR`.

### Deterministic regime state

`src/grinder/controller/regime.py`

States include:
- RANGE;
- TREND_UP / TREND_DOWN;
- VOL_SHOCK;
- THIN_BOOK;
- TOXIC;
- EMERGENCY.

Trend detection combines net displacement with a choppiness/range score rather than volatility alone.

### Range score

From the smart-grid specification:

`range_score = sum_abs_returns / (abs(net_return) + eps)`

Interpretation:
- high value = much path movement but little net displacement = chop/range;
- low value with meaningful net displacement = directional/trending path.

This is highly relevant to deciding whether a grid crossing should mean-revert or continue.

### Adds-off / reduce-only state

In hostile states:
- new risk can be blocked;
- existing risk can remain reducible/closable;
- toxic/shock states do not simply keep adding grid levels.

This is a stronger architecture than an all-or-nothing stop because it distinguishes **increase-risk** from **reduce-risk** intent.

### Drawdown latch

`src/grinder/risk/drawdown_guard_v1.py`

When a drawdown budget is breached:
- state latches into DRAWDOWN;
- new/increase-risk intents are blocked;
- close/reduce-risk and cancel actions remain allowed;
- no automatic flapping back to normal.

### Consecutive-loss state

`src/grinder/risk/consecutive_loss_guard.py`

A deterministic loss streak counter can move the system into PAUSE/DEGRADED state.

Delta-A-alpha should mutate this idea from a crude global streak counter into **event-family / interpretation-specific regret memory** rather than simply stopping all trading.

### Adverse grid threshold

`src/grinder/risk/adverse_trigger.py`

Computes the Nth adverse grid level from the same quantized grid geometry and exposes a deterministic breach test.

This is useful for defining event degradation in **lattice units**, not arbitrary dollars.

### Scientific implication

This source strongly supports the architecture:

`grid geometry -> features -> regime -> risk admission -> execution`

rather than:

`grid crossing -> automatic trade`.

---

## S4 — MetaQuotes/MQL5 research-grounded grid article + Taranto/Khan academic work

Public MQL5 article:
`Building a Research-Grounded Grid EA in MQL5: Why Most Grid EAs Fail and What Taranto Proved`

Relevant mechanisms:
- volatility/drift regime measurement;
- ATR-dynamic spacing;
- CUSUM structural-break detection;
- finite/restartable grid cycles;
- age-based cycle expiry;
- equity drawdown kill switch;
- separate range/trend/post-trend behavior.

The article attributes the mathematical foundation to Aldo Taranto and Shahjahan Khan's work on Bi-Directional Grid Constrained stochastic processes.

Academic papers located:
- Taranto & Khan (2020), `Gambler's ruin problem and bi-directional grid constrained trading and investment strategies`;
- Taranto & Khan (2020), `Drawdown and Drawup of Bi-Directional Grid Constrained Stochastic Processes`;
- Taranto & Khan (2021), `Application of Bi-Directional Grid Constrained Stochastic Processes to Algorithmic Trading`.

The academic work supports a critical principle: an unconstrained grid can have attractive short-run harvesting behavior while long-run ruin risk remains structural.

### Dominant-variable insight

The MQL5 implementation emphasizes volatility `sigma` and drift `mu` as more important structural variables than simply optimizing gap width.

A useful operational proxy proposed in the article is a volatility-to-drift relationship plus structural-break detection.

### Scientific implication

For Delta-A-alpha, this points toward a potentially large mutation:

**the same lattice crossing should not have the same directional meaning in a quiet trend, noisy trend, range, or volatility shock.**

Spacing adapts geometry; **regime changes interpretation**.

---

# First mechanism shortlist

The source hunt is intentionally stopped here to avoid category sprawl.

## M1 — Elastic spacing with hysteresis and cooldown

Source-backed:
- ATR/NATR dynamic spacing;
- min/max clamps;
- change hysteresis;
- geometry update cooldown.

Original mutation:
- include spread/noise floor;
- later include parent-lattice scale;
- avoid recentering existing event identities when the gap changes.

Priority: HIGH.

## M2 — Range/trend interpretation router

Source-backed:
- range score from path length vs net displacement;
- directional net-return state;
- volatility/drift relationship;
- explicit range/trend/shock/toxic states.

Original mutation:
- the event itself remains the same, but its **semantic direction** changes:
  - RANGE -> mean-reversion hypothesis;
  - TREND -> continuation hypothesis;
  - TRANSITION/uncertain -> abstain or shadow-only;
  - VOL_SHOCK/TOXIC -> adds off / observe / reduce-only.

Priority: VERY HIGH.

## M3 — Structural-break / transition detector

Source-backed:
- CUSUM change-point logic in the MQL5 research-grounded design;
- regime state precedence in GRINDER.

Original mutation:
- event fingerprints created before a detected break become stale and may not re-arm without reclassification.

Priority: HIGH.

## M4 — Early adverse-path thesis failure

Source-backed:
- adverse grid-level threshold;
- drawdown/risk-admission state;
- trailing/protective exits.

Original mutation:
- combine lattice adverse level with path evidence:
  - next-cell acceptance;
  - no expected MFE by a causal time budget;
  - adverse velocity/persistence;
  - failed reclaim.

Exit before a large fixed stop when the thesis has failed.

Priority: VERY HIGH.

## M5 — Stateful opportunity recovery

Source-backed:
- deterministic state machines;
- loss-streak degraded/pause state;
- increase-risk vs reduce-risk separation.

Original mutation:
- a loss changes the **event interpretation state**, not lot size;
- one bounded recovery flip can be authorized only after new causal evidence;
- no immediate same-event same-direction re-entry.

Priority: VERY HIGH.

## M6 — Event-local regret / health memory

Source inspiration:
- consecutive-loss guard;
- deterministic persisted risk state.

Original mutation:
track separate decayed performance for:
- mean-reversion interpretation;
- continuation interpretation;
- recovery flips;
- event family / lattice region.

This avoids shutting down the entire system because one interpretation is temporarily failing.

Priority: HIGH, but after M2/M4 are measurable.

## M7 — Risk-admission latch / reduce-only mode

Source-backed:
- drawdown state blocks new risk while preserving reduce-only actions;
- toxic/shock states disable adds.

Original mutation:
- use multiple scopes:
  - event;
  - lattice region;
  - grid system;
  - account.

Priority: REQUIRED SAFETY LAYER, but not alpha by itself.

## M8 — Counterfactual shadow twin

**ORIGINAL MUTATION.**

At each grid event, simulate both causal interpretations in shadow:
- mean-reversion;
- continuation.

Only one or neither is executed physically.

The unexecuted interpretation is tracked without risk for a bounded horizon.

After the outcome, compute **directional regret**:

`regret = shadow_counterfactual_value - executed_value`

Use decayed regret as input to event-family health and future classification.

This creates an online opportunity-recovery memory without paying for two real positions.

Priority: HIGH-POTENTIAL BREAKTHROUGH.

## M9 — Quiet-trend inversion

**ORIGINAL MUTATION inspired by Taranto/Khan regime risk.**

The source YouTube rule does:
- fall from high -> BUY;
- rise from low -> SELL.

In a drift-dominant quiet trend, this is precisely the dangerous interpretation.

Mutation:
- when drift dominates oscillation, the same event may invert:
  - fall-through / failed reclaim -> SHORT continuation;
  - rise-through / failed rejection -> LONG continuation.

The grid becomes a **direction-neutral coordinate system**, not a permanently contrarian strategy.

Priority: VERY HIGH-POTENTIAL BREAKTHROUGH.

## M10 — Event genealogy and information-based re-arm

**ORIGINAL MUTATION.**

Repeated crossings of the same cell belong to one event family until a true state transition occurs.

A new physical trade requires new information:
- different cell;
- reclaim/acceptance transition;
- regime transition;
- structural break;
- materially changed path fingerprint.

Elapsed time alone is insufficient.

Priority: VERY HIGH for gross-loss containment.

---

# First-pass architectural conclusion

The first research hunt does **not** support spending time optimizing the original YouTube grid.

The stronger direction is:

**KEEP**
- grid geometry;
- high-density crossings;
- chained spatial information;
- simple reconstructible structure.

**REMOVE**
- automatic contrarian trade on every crossing;
- uncapped/open-ended physical inventory;
- loss-dependent sizing;
- one universal directional interpretation;
- net-profit-only optimization.

**ADD**
- elastic geometry;
- explicit regime semantics;
- event identity;
- adverse-path failure;
- information-based re-arm;
- opportunity recovery;
- shadow counterfactuals;
- latching risk admission;
- future specialist routing.

This is sufficient to define the initial `R9 Delta-A-alpha Grid System` redesign without launching broader session/news/specialist category research.

## Status

**SOURCE HUNT 001 COMPLETE.**

Next durable unit should convert this shortlist into a small January mechanism-screen sequence. No code/testing was performed in this unit.
