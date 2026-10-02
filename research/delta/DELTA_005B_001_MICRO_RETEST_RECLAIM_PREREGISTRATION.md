# DELTA 005B-001 — Micro-Retest / Reclaim Continuation

**Recovery status:** RECOVERED 2026-10-02 FROM DURABLE MANIFEST + MASTER RESEARCH LEDGER  
**Original scientific status:** PREREGISTERED BEFORE COMPUTE  
**Mode:** historical Python simulation only  
**Focus:** ENTRY + INITIAL-HOLD  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Stage-A:** [2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)  
**August:** SEALED

This markdown was reconstructed after a chat-delivery interruption. The original preregistration facts were already frozen in:
- `research/delta/artifacts/DELTA_005B_001_MANIFEST.json`
- DELTA_005 master Google research ledger
- committed source `research/delta/experiments/DELTA_005B_MICRO_RETEST.py`

## Parent finding

DELTA_005A showed that tick-flow confirmation improved loss/drawdown mainly by deleting activity. 005B therefore tested whether opportunities rejected by immediate continuation could be recovered through a causal break -> retest -> reclaim sequence.

## Ownership

005A direct continuation owner:
- 250ms and 1000ms flow sign aligned with original R9 break.

If that direct owner did not take the first-touch opportunity, ownership transferred exclusively to 005B.

## Causal sequence

1. R9-style first-touch break exists.
2. Price establishes the break.
3. Price returns toward the broken virtual boundary.
4. Price reclaims in the original direction.
5. 250ms and 1000ms flow agree at reclaim.
6. R9 regime/spread state and completed-S1 direction remain valid.
7. Simulated entry occurs at executable Ask/Bid.

## Frozen grid

Retest band:
- $0.00
- $0.02
- $0.05

Reclaim buffer:
- $0.00
- $0.02
- $0.05

Break-to-reclaim timeout:
- 1000 ms
- 3000 ms
- 5000 ms

Total configurations: 27.

No mature Holding-Trade / Exit / High-Profit optimization was allowed.

## Public reconstructible provenance

- TradingView open breakout/retest examples
- MetaQuotes/MQL5 breakout/retest community examples
- Exact URLs remain preserved in the DELTA_005 master research ledger.

## Recovery integrity

No result or threshold was changed during this recovery. The recovered document exists solely to restore the missing preregistration narrative required by the DELTA durable-artifact contract.
