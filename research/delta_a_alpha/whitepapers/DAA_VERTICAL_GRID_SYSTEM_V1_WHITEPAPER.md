# Delta-A-alpha — Vertical Grid System V1 Whitepaper

**Version:** V1  
**Status:** FROZEN PERMANENT SPINE  
**Symbol:** XAUUSD  
**Execution root:** ordered executable ticks  
**Default lot:** fixed 0.01  
**Martingale:** prohibited  
**Loss-dependent sizing:** prohibited  
**August 2026:** SEALED  

## 1. Canonical vertical order

```text
ordered ticks
→ session-specific grid geometry
→ completed H4/H1/M15/M5 structure
→ London/overlap/NY hourly high-volume harvesting + separate Asia geometry
→ Watchdog/regime renewal
→ trend-within-trend native routing
→ wrong-direction recovery
→ portfolio heat/capital governor
```

Every V1 implementation and descendant must preserve these responsibilities even when a layer is in observe-only mode.

## 2. Layer contracts

### L0 — Ordered tick root

Ticks own:
- event identity;
- crossing/first-touch chronology;
- fills;
- protective exits;
- reclaims/retests;
- renewal/rearm;
- lifecycle;
- full-equity/heat replay.

No future tick, incomplete bar, future MFE/MAE, future P/L, or retrospective label may influence an entry-time decision.

### L1 — Session-specific grid geometry

Session is a causal system state.

Required distinct families:
- Asia;
- London;
- London/New York overlap;
- New York;
- late New York / transition when supported.

No universal gap/cadence/lifecycle is assumed.

Asia is explicitly separate from London/overlap/New York.

### L2 — Completed H4/H1/M15/M5 structure

No naive timeframe voting.

Roles:
- H4: environment / long-horizon drift-volatility context;
- H1: structural location / parent direction;
- M15: phase / pullback / continuation / transition;
- M5: transfer/opportunity state;
- ticks: event timing/execution.

Derived timeframes are context only; execution remains tick-rooted.

### L3 — London/overlap/New York hourly high-volume harvesting

High-volume sessions may own:
- hour/subphase-specific event cadence;
- grid spacing;
- displacement thresholds;
- lifecycle;
- capacity;
- slot priority.

Supplemental default: at most one new physical ticket per market tick unless an explicit named scaling mechanism owns same-tick multiplicity.

### L4 — Asia geometry

Asia may use:
- quieter/rotational geometry;
- activity filters;
- subphase filters;
- different continuation/reversion semantics;
- different caps/horizons.

Do not force London/NY cadence into Asia.

### L5 — Watchdog / regime renewal

Watchdog owns:
- scout/first-parent logic;
- earned admission from already-realized exits;
- renewal children;
- relock;
- layer depth;
- campaign ownership;
- interaction with global capacity.

Watchdog is a layer, not the whole system.

### L6 — Trend-within-trend native routing

Routing may depend on entry-known:
- completed H4/H1/M15/M5 state;
- direction;
- realized displacement;
- session/hour/subphase;
- activity regime;
- state age;
- causal renewal behavior;
- already-realized specialist evidence if explicitly enabled.

Forbidden:
- month/date identity;
- future outcome;
- hindsight regime labels.

### L7 — Wrong-direction recovery

Recovery is mandatory as a system capability but conditional in activation.

Permitted triggers include:
- failed ignition after an already-elapsed bounded window;
- failed continuation quantum;
- failed break plus reclaim;
- state-conditioned reversal evidence.

Recovery must:
- remain fixed 0.01 under V1 research/build policy;
- never use Martingale;
- never increase size because the original trade lost;
- never become DCA rescue;
- have its own cap/lifecycle/invalidation;
- remain independently measurable.

### L8 — Portfolio heat / capital governor

The governor owns:
- global max open;
- per-layer/session capacity;
- physical slot allocation;
- reduce-only behavior;
- duplicate/collision handling;
- equity/heat limits;
- future small-account overlays.

Signal intelligence and physical funding are distinct: a layer may remain active in shadow with zero funded slots.

## 3. Permanent V1 invariants

1. XAUUSD only unless owner changes scope.
2. Ordered tick chronology is authoritative.
3. Fixed 0.01 lot default.
4. Martingale prohibited.
5. Loss-dependent sizing prohibited.
6. Unbounded averaging prohibited.
7. Calendar month/week/date are evaluation partitions only.
8. Session awareness mandatory.
9. H4/H1/M15/M5 role separation mandatory.
10. Asia geometry remains separate.
11. High-volume hourly harvesting remains part of the primary spine.
12. Watchdog/regime renewal remains a layer.
13. Trend-within-trend routing remains causal.
14. Wrong-direction recovery remains bounded and state-conditioned.
15. Global heat/capital governor has final authority over new physical risk.
16. Daily/weekly/monthly/cumulative scorecards are required.
17. Net, velocity, expectancy, win rate, gross loss, balance DD, equity DD, max-open and survivability are reported together.
18. R9 SYNTH is a benchmark, never an execution oracle.
19. Durable artifacts outrank chat memory.
20. Every accepted version preserves a rollback branch.

## 4. V1 evidence anchors

### January
Balanced frontier:
- net about +$194.43K;
- 21/21 positive trading days;
- 5/5 ISO weeks beat time-matched R9 SYNTH.

Aggressive frontier:
- net about +$203.53K.

### February
High-quality vertical frontier:
- net about +$189.96K;
- 32,054 trades;
- PF about 14.70;
- win about 88.91%;
- 20/20 positive days;
- 4/4 weeks beat time-matched R9 SYNTH.

Near-all-metrics frontier:
- net about +$200.16K;
- 33,850 trades;
- win about 88.22%;
- expectancy about +$5.91/trade;
- 20/20 positive days;
- 4/4 weeks beat R9 SYNTH.

These numbers justify freezing the architecture. They do not constitute MT5 broker certification or live-performance claims.

## 5. Versioning

V1 freezes the spine.

V2+ may refine any layer’s mechanics while preserving interfaces and causal ordering.

Before replacing V1, a descendant must:
- preserve a V1 fallback branch;
- replay accepted prior months;
- document changed layers;
- show daily/weekly/monthly effects;
- reject calendar/future leakage;
- pass owner review.

Small-capital survival belongs to later versions above the V1 capital governor.

## 6. Engineering and MT5 implementation contract

The owner has authorized a faithful MT5 V1 port after this documentation freeze.

Required modules:
1. tick ingestion/execution;
2. session/DST clock;
3. completed H4/H1/M15/M5 state;
4. session geometry;
5. London/overlap/NY hourly harvester;
6. Asia geometry;
7. Watchdog/renewal;
8. trend-within-trend router;
9. bounded recovery;
10. global heat/capital governor;
11. deterministic diagnostics/logger.

The first implementation is an engineering port, not permission to redesign strategy logic.

Certification:
- compile cleanly;
- static QA;
- Python parity by layer;
- month-scoped MT5 Every tick based on real ticks;
- cumulative real-tick review;
- small-capital versions only afterward.

## 7. Human record

Whitepaper:
https://docs.google.com/document/d/1-PiyhfhulLl1garjwtSYOysPGOgBTgV_apnQmCKoCTc/edit?usp=drivesdk
