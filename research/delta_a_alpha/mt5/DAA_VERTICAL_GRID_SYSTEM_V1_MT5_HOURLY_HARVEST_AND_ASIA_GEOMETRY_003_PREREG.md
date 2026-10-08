# Delta-A-alpha — Vertical Grid System V1 MT5 Unit 003
## Hourly Harvest and Asia Geometry

**Status:** IMPLEMENTATION CONTRACT  
**Parent:** unit 002 session lattice + genealogy  
**Execution:** observe-only; route proposals only

## Objective

Translate unit-002 first-touch events into causal session/MTF route proposals while preserving the permanent V1 distinction between:

- Asia geometry; and
- London / overlap / New York / late-New-York high-volume harvesting.

No funded order may be sent in this unit.

## Source authority

The route semantics are ported from the durable Delta-A-alpha BUILD-02 session/timeframe router and sleeve refinement, not re-invented in MQL5.

## Required route families

Asia:
- ASIA_LOWER_TAKEOVER
- ASIA_M15_DIVERGE_M5_RECLAIM

London:
- LONDON_M5_TAKEOVER
- LONDON_M5_RECLAIM

Overlap:
- OVERLAP_LOWER_TAKEOVER
- OVERLAP_ALIGNED_COUNTERCROSS

New York:
- NY_LOWER_TRANSFER
- NY_LOWER_COUNTERCROSS

Late New York:
- LATE_ALIGNED_MOMENTUM
- LATE_MACRO_SPLIT_TRANSFER
- LATE_M5_REJECTION
- LATE_LOWER_TAKEOVER

London-open and rollover remain observe-only.

## Hour/subphase ownership

Every route proposal records:
- UTC hour;
- 10-minute UTC subphase.

The durable BUILD-02 targeted gates remain:
- ASIA_LOWER_TAKEOVER: 23:00-00:00 UTC only;
- LONDON_M5_TAKEOVER: 11:00-12:00 UTC only.

Other unit-003 route families remain broad within their session pending later V2+ refinement.

## Birth-state contract

A valid proposal may only attach to the current event ID and is written back into the event genealogy. Later Watchdog/native/recovery layers consume this owned event record.

## Acceptance

- exact route families present;
- session/MTF logic matches BUILD-02 reference cases;
- hour gates match the durable Python semantics;
- no route exists without a fresh unit-002 event;
- route metadata is attached to the same event ID;
- no order-send path exists;
- CI deterministic QA passes.

## Next unit

`DAA_VERTICAL_GRID_SYSTEM_V1_MT5_WATCHDOG_REGIME_RENEWAL_004`
