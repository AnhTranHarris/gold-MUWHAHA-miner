# DAA GRID — Community Source Hunt 002 — Whole-System Layers

**Unit:** `DAA_GRID_COMMUNITY_SOURCE_HUNT_002_SYSTEM_LAYERS`  
**Status:** COMPLETE — SYSTEM-LAYER MECHANISM MAP FROZEN  
**Lineage:** Delta-A-alpha only  
**Main `delta`:** READ ONLY  
**August 2026:** SEALED  
**Lot policy:** fixed 0.01 only  
**Martingale / loss-dependent sizing:** PROHIBITED

## Objective

Expand the first GRID-001 mechanism hunt into the whole-system categories required by the owner:

- multi-session;
- multi-regime;
- multi-timeframe;
- market structure;
- multi-trend / trend phase;
- scheduled news and event state;
- execution/friction;
- finite lifecycle / restart;
- risk admission;
- future 6–16 specialist routing.

GitHub is a first-class community source. Public code is inspected for reconstructible mechanisms, not copied blindly. Missing-license repositories are treated as conceptual evidence and clean-room logic sources only.

## Public GitHub sources inspected

### 1. bnzr-team/grinder

Inspected commit already frozen in Source Hunt 001:
`f216435c9549795edd12886d755f114b42b819fc`

Useful mechanisms retained as research leads:
- volatility-aware adaptive step;
- min/max clamps;
- hysteresis;
- geometry cooldown;
- deterministic regime state;
- range-vs-directional path score;
- hostile/toxic risk modes;
- drawdown latch;
- reduce-only semantics;
- adverse-grid threshold;
- stateful risk transitions.

No top-level license found at inspected commit. Use clean-room reconstruction.

### 2. aycfundteam/ayc-bybit-competition-2026

Inspected public strategy:
`strategy/atr_grid_strategy.py`
blob:
`df5d865c2b756512d108acaab0f91d757f11832a`

Useful architecture:
- ATR-adaptive spacing;
- EMA directional bias;
- ADX + ATR-ratio four-quadrant regime:
  - stable trend;
  - volatile trend;
  - sideways quiet;
  - sideways chop;
- regime-specific parameter object;
- persistent grid state;
- trailing risk state.

Important limitation:
production thresholds/parameters are intentionally hidden. Therefore only the disclosed architecture/formulas are usable. No license found.

### 3. vuyelwadr/pulsechainTraderUniversal

Inspected commit:
`a5383c6bb396ef30bf707cb67228b5118c68f3a1`

Relevant files:
- `strategies/grid_trading_strategy_v2.py`
- `strategies/grid_trading_strategy_v2_pro_2.py`
- `newstrats/local_pro2.md`

Useful mechanics:
- ATR/volatility adaptive grid spacing and range;
- higher-timeframe regime anchor;
- trend-aware asymmetric grid skew;
- ATR-distance recentering;
- post-fill cooldown;
- maximum active ladder levels;
- fee/edge gating:
  `minimum required edge > estimated round-trip friction * safety multiplier`;
- conservative cost fallback when exact friction is unknown;
- segment/worst-drawdown robustness checks.

No license found. Use conceptual clean-room reconstruction only.

### 4. joshyattridge/smart-money-concepts

Inspected commit:
`1b62fd6c41e1f508e7ed76831a039fa4c82d42f6`

License:
MIT.

Useful deterministic structure primitives:
- swing highs/lows;
- BOS / CHoCH;
- liquidity levels and sweeps;
- previous high/low by selected timeframe;
- explicit sessions;
- retracement percentage.

Research implication:
the grid can be anchored to structural locations rather than a flat rolling high/low only.

### 5. gammarinaldi/mql5

Inspected commit:
`e63ffbec5647403552106ed63accb31a1e9ec2ed`

Relevant source:
`Grid_BB_RSI_News_EA/Grid_BB_RSI_News_EA.mq5`

Useful mechanism:
- MQL5 built-in economic calendar query;
- high-impact importance check;
- currency/country relevance;
- event-window trading suspension.

No license found. Use architecture only.

### 6. thales1020/QuantumTrader-MT5

Inspected commit:
`1b46f488d502bdf540c67f00eeb910c0c5a05568`

License:
MIT.

Relevant source:
`docs/examples/news_filter.py`

Useful mechanisms:
- explicit high-impact event list;
- symbol-affect mapping;
- configurable minutes-before / minutes-after event windows;
- deterministic event-window query.

### 7. BlamzKunG/CFD-Trading-ML

Inspected commit:
`6d896c67df54dae9fd8fd73d4816b3e3364500fc`

Relevant XAUUSD experiment:
`projects/xauusd_trading_policy/scripts/run_exp75_cross_regime_adaptive_confluence.py`

Useful inspectable ideas:
- explicit London / NY / transition session masks;
- volatility-conditioned horizons;
- multi-horizon trend state;
- swing sweep / rejection concepts;
- order-flow persistence;
- prime-session vs transition behavior.

Not adopted:
- opaque pre-trained model outputs;
- variable risk sizing;
- weighted confluence stacks as authority.

Use deterministic components only.

## Community / official cross-checks

MetaQuotes economic calendar API is suitable for live/demo event state, but its calendar functions do not operate natively in Strategy Tester. Historical event testing therefore requires a frozen CSV/binary/resource dataset exported ahead of time.

The 2026 MQL5 research-grounded grid article reinforces:
- unconstrained indefinite grid cycles are structurally dangerous;
- volatility and drift dominate grid behavior;
- finite/restartable cycles matter;
- D1 volatility can answer a different question from H4 regime state;
- range, trend, and post-trend states should not share one grid interpretation;
- CUSUM/change-point logic is useful for structural transitions.

Community discussions repeatedly converge on the same warning: regime classification is useful, but a single regime filter can itself overfit. This supports role separation and multiple specialist modes rather than one global yes/no filter.

## System-level source conclusions

### A. Geometry must be elastic but stable

Adopt as a mechanism family:
- volatility-scaled gap;
- spread/noise floor;
- min/max clamp;
- hysteresis;
- update cooldown;
- recenter only on a meaningful state/cycle boundary.

Do not let grid spacing oscillate every tick.

### B. Regime changes semantics, not only permission

Candidate high-level states:
- RANGE_QUIET;
- RANGE_ACTIVE;
- TREND_QUIET;
- TREND_VOLATILE;
- TRANSITION;
- EVENT_SHOCK;
- TOXIC / REDUCE_ONLY.

A crossing may mean:
- mean reversion;
- continuation;
- observe-only;
- no new risk.

### C. Timeframes need assigned jobs, not votes

Proposed role hierarchy:
- D1/H4: environment, volatility/drift, structural regime;
- H1/M15: swing structure, prior highs/lows, BOS/CHoCH, parent cells;
- M5/M1: opportunity phase, reclaim/acceptance, fast trend state;
- ordered ticks: crossing identity, execution, path shape, spread.

No majority-vote confluence.

### D. Structure should shape the grid

High-impact structural anchors to test:
- prior session high/low;
- prior day high/low;
- confirmed swing high/low;
- BOS/CHoCH transition;
- liquidity sweep/reclaim;
- retracement depth.

Grid cells become spatial coordinates around structure rather than arbitrary equal lines detached from context.

### E. Session state is a prior, not a hard filter

Session classes:
- Asia;
- London open / London;
- London–NY overlap;
- NY;
- late NY / rollover;
- transition windows.

Session may change:
- expected event density;
- gap multiplier;
- horizon;
- mean-reversion vs continuation prior;
- risk admission strictness.

The same price move is not assumed equivalent in every session.

### F. News/events need a state machine

Do not implement news as only “block ±N minutes.”

Proposed states:
- NORMAL;
- PRE_EVENT;
- RELEASE_WINDOW;
- POST_EVENT_SHOCK;
- POST_EVENT_DISCOVERY;
- NORMALIZED.

For XAUUSD, high-impact USD events are the first priority.

Potential behavior:
- PRE_EVENT: block new grid risk; reduce/exit remains allowed;
- RELEASE_WINDOW: observation / reduce-only;
- POST_EVENT_SHOCK: wider/frozen geometry; no naive mean reversion;
- POST_EVENT_DISCOVERY: allow trend/structure classification after executable evidence;
- NORMALIZED: return to ordinary regime logic.

Historical tester implementation must use a frozen event dataset; live/demo may use MQL5 calendar APIs.

### G. Cost/edge admission belongs before execution

Each event should estimate whether its plausible state-conditioned excursion is large enough to overcome:
- spread;
- commission;
- any modeled slippage margin.

No trade merely because a geometric level was touched.

### H. Finite cycles / restart are structural

A grid state may not remain valid indefinitely.

Cycle expiry/restart triggers may include:
- structural break;
- session transition;
- news-event state transition;
- regime transition;
- parent-cell change;
- age limit;
- explicit lifecycle completion.

Restart means new information, not Martingale rescue.

## Original Delta-A-alpha mutations to research

These are hypotheses, not source claims.

### O1 — Morphing lattice

One grid object changes geometry and interpretation by state while preserving event genealogy.

### O2 — Asymmetric directional elasticity

Spacing may be different toward and against a confirmed structural trend, without changing lot size.

### O3 — Structural magnetic grid

Parent levels are attracted to high-information anchors:
previous session/day extremes, confirmed swing levels, and structural breaks.

### O4 — Event shock handoff

A scheduled event temporarily suspends ordinary grid semantics. After release, the first accepted structural state owns the next grid cycle.

### O5 — State-conditioned expectancy floor

The required edge is not one global dollar threshold. Each state family maintains a causal estimate of expected MFE/MAE and friction; new risk is admitted only when expected excursion clears cost plus safety margin.

### O6 — Category health map

Track performance by:
- session;
- regime;
- timeframe-role state;
- structure state;
- trend phase;
- event/news state.

This allows research to identify exactly which category is limiting system performance rather than globally retuning the grid.

## Source Hunt 002 decision

The next rebuild should not add another indicator filter.

It should create a stable system state contract containing all major dimensions first, with neutral/default behavior available for dimensions not yet activated.

Then improvements are enabled vertically and accepted only when they beat the current floor under the frozen R9 comparison framework.

