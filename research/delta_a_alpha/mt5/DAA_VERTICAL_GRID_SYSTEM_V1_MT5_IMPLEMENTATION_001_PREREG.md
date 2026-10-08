# Delta-A-alpha — Vertical Grid System V1 MT5 Implementation 001

**Status:** IMPLEMENTATION UNIT 001  
**Purpose:** compile-oriented architecture shell and deterministic diagnostics  
**Economic status:** NO PROFIT CLAIM / NO ORDER-SEND PATH  
**Execution default:** observe-only  
**V1 fallback:** `delta-A-alpha-v1-vertical-grid-spine`

## Objective

Establish the permanent V1 layer order in MQL5 before porting profit-bearing mechanics.

Required source-order contract:

1. ordered tick and server→UTC normalization;
2. session-specific geometry;
3. completed H4/H1/M15/M5 state;
4. London/overlap/NY hourly harvesting + separate Asia geometry interface;
5. Watchdog/regime renewal interface;
6. trend-within-trend routing interface;
7. wrong-direction recovery interface;
8. global heat/capital governor;
9. deterministic diagnostics.

## Safety

- fixed 0.01 lot enforced at initialization;
- no Martingale;
- no loss-dependent sizing;
- no order-send path in unit 001;
- `InpExecutionEnabled=false` by default and cannot create a trade in this unit;
- global max-position governor interface exists before later execution code;
- completed timeframe state uses shift 1 only.

## Clock

The shell includes the already-validated historical Coinexx server-to-UTC convention:
- UTC+2 standard;
- UTC+3 during US DST;
- fixed/raw diagnostic alternatives.

## Session geometry shell

Base V1 gaps are encoded as architecture defaults:
- Asia: $0.75;
- London: $1.00;
- overlap: $0.75;
- New York: $1.50;
- late NY: $0.50;
- London open / rollover: observe-only base geometry.

These are interface defaults, not a claim that every later V2+ parameter is frozen.

## Next engineering unit

`DAA_VERTICAL_GRID_SYSTEM_V1_MT5_SESSION_GEOMETRY_AND_EVENT_GENEALOGY_002`

That unit will port first-touch lattice/event ownership and session-specific event genealogy before any high-volume or recovery layer is allowed to send orders.
