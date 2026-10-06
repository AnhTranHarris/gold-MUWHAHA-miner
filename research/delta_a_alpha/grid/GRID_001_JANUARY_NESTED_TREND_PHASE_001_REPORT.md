# GRID-001 January Nested Trend Phase 001

**Status:** COMPLETE / PHASE ROUTING DISCOVERY

## What changed

The nested trend model now tracks not only parent direction but how long that strong directional state has persisted.

Frozen phase bins:
- EARLY = 1–2 strong completed bars
- MATURE = 3–6
- EXTENDED = 7+

No age-bin tuning was performed.

## Main discovery

Trend phase changes **ownership**, not merely confidence.

### A15 — 15m aligned + extended -> child continuation

- 260 trades
- **+$81.04 / PF 1.1394**
- discovery **+$23.57 / PF 1.2815**
- validation **+$57.47 / PF 1.1155**

### A15 — 15m opposed + mature -> parent reclaim

- 410 trades
- **+$50.49 / PF 1.0543**
- discovery **+$9.59 / PF 1.0821**
- validation **+$40.90 / PF 1.0503**

### A10 — 15m aligned + extended -> child continuation

- 323 trades
- **+$28.97 / PF ~1.04**
- positive discovery and validation

### A10 — 5m opposed + mature -> parent reclaim

- 243 trades
- **+$32.33 / PF ~1.08**
- discovery **+$9.45**
- validation **+$22.88**

### A05 — 15m opposed + extended -> child continuation

- 331 trades
- **+$59.97 / PF 1.1346**
- discovery **+$15.02 / PF 1.1023**
- validation **+$44.95 / PF 1.1505**

This last case is particularly important: an extended parent trend that still opposes the child may be losing authority. The correct action can flip back to the child direction.

## Interpretation

The multi-state assumption is supported: direction alone is insufficient; direction × timeframe × phase changes the meaning of the same grid event.

This is not majority voting. A parent can own the event during one phase and lose ownership later.

## Breakthrough check

The phase routes are cleaner and chronologically compatible, but individually remain too sparse to satisfy the user's 50%-ish R9 REAL January system target.

Therefore the next step is the requested sandwich construction:

1. preserve the already-frozen volatility-expansion route;
2. add the robust phase-owned routes;
3. enforce a single grid-system physical owner;
4. measure the combined incremental January contribution and risk.

The resulting stack becomes the current grid floor if it improves the combined system.

August sealed. Main `delta` read-only. MQL5 unauthorized.
