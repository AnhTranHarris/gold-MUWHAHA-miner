# DELTA 005L-001 — Multi-Stage Initial Protection

**Status:** PREREGISTERED
**Mode:** historical Python simulation only
**Focus:** ENTRY + INITIAL-HOLD
**Mature Holding-Trade + Exit + High-Profit:** frozen / out of scope
**Stage-A:** [2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)
**Surface:** DUKAS_COINEXX_LIKE_P75
**August:** SEALED

## Derivation

005H proved that delaying tight trailing from +$0.10 to around +$0.30 materially improves initial-hold persistence.

005K proved that one MFE-triggered protective lock can recover some gross-loss damage without necessarily reducing 005H winner count, but no single trigger/lock dominates 005H on net.

The next structural hypothesis is that **protection should progress in stages** as favorable excursion develops.

This is reconstructible from public MQL5 breakeven/trailing workflows that separate one-time protection transitions from later continuous trailing:
- https://www.mql5.com/en/articles/3621
- https://www.mql5.com/en/articles/19911
- https://www.mql5.com/en/articles/22614

## Fixed behavior

All original R9-style entries remain unchanged.

Initial hard stop remains $0.30.

Max hold remains 30 seconds.

Trail distance remains $0.03 whenever continuous trailing is active.

A protection stage may only tighten the stop and may fire once.

## Explicit architectures

### A — H_CONTROL
- no staged lock;
- continuous trail activation +$0.30.

### B — K_LATE_LOCK
- at MFE +$0.25: stop -> entry +$0.05;
- continuous trail activation +$0.30.

### C — BALANCED_TWO_STAGE
- at MFE +$0.20: stop -> entry -$0.10;
- at MFE +$0.25: stop -> entry +$0.05;
- continuous trail activation +$0.30.

### D — FAST_TWO_STAGE
- at MFE +$0.15: stop -> entry -$0.10;
- at MFE +$0.20: stop -> entry +$0.05;
- continuous trail activation +$0.30.

### E — EXTENDED_BALANCED
- at MFE +$0.20: stop -> entry -$0.10;
- at MFE +$0.30: stop -> entry +$0.05;
- continuous trail activation +$0.40.

### F — EXTENDED_PROTECTIVE
- at MFE +$0.20: stop -> entry +$0.00;
- at MFE +$0.30: stop -> entry +$0.05;
- continuous trail activation +$0.40.

### G — EXTENDED_BREATH
- at MFE +$0.20: stop -> entry -$0.10;
- at MFE +$0.30: stop -> entry +$0.05;
- continuous trail activation +$0.50.

Total architectures: 7.

## Required diagnostics

For each architecture:
- trades;
- winners;
- gross profit/loss;
- net;
- max balance drawdown;
- average hold;
- stage-1 moves;
- stage-2 moves;
- protection-stop exits;
- hard-stop / trail-stop / max-hold exits;
- 1/3/5/10/15s survival;
- winner retention vs R9 and 005H;
- gross-loss change vs R9 and 005H;
- net change vs R9 and 005H.

## Desired shape

A useful ladder should retain most of the 005H survival breakthrough while recovering materially more gross loss than 005K, without materially reducing winner count.

The test should identify architecture shape, not an optimized numerical setting.

## Phase boundary

No mature trade harvest/exit/profit-target logic is changed.

Holding-Trade + Exit + High-Profit remains a later campaign.

August remains sealed.
