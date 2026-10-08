# Delta-A-alpha — V1 MT5 Unit 003 Report
## Hourly Harvest and Asia Geometry

**Status:** COMPLETE / CI PASS / OBSERVE-ONLY  
**EA version:** 1.02  
**GitHub Actions run:** 37741203005 — SUCCESS  
**Order-send authority:** NONE

## Implemented

Unit 003 converts fresh unit-002 grid events into owned session/MTF route proposals.

It ports the durable BUILD-02 route families:
- Asia lower takeover / M15-diverge-M5-reclaim;
- London M5 takeover / reclaim;
- overlap lower takeover / aligned countercross;
- New York lower transfer / countercross;
- late-NY aligned momentum / macro-split transfer / M5 rejection / lower takeover.

Every proposal stores UTC hour and 10-minute subphase back into the event genealogy.

The durable targeted gates are preserved:
- Asia lower takeover: 23:00-00:00 UTC;
- London M5 takeover: 11:00-12:00 UTC.

London-open and rollover remain observe-only.

## Causality

Only fresh first-touch events can route.
MTF values are completed-bar values from the event birth tick.
No month/date label participates.
No future outcome participates.

## QA

GitHub Actions unit-003 deterministic route QA passed after correcting one QA vector: the New York countercross direction is the opposite of M5, matching the durable Python BUILD-02 rule.

## Compile status

MetaEditor compile remains pending.

## Next unit

`DAA_VERTICAL_GRID_SYSTEM_V1_MT5_WATCHDOG_REGIME_RENEWAL_004`
