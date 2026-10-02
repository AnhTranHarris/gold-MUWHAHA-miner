# DELTA 005B-001 — Micro-Retest / Reclaim Report

**Recovery status:** RECOVERED 2026-10-02 FROM DURABLE CHECKPOINT + MASTER RESEARCH LEDGER  
**Scientific status:** COMPLETE — NOT PROMOTED  
**Mode:** historical Python simulation only  
**Focus:** ENTRY + INITIAL-HOLD  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Stage-A ticks:** 4,205,709  
**Variants:** 27  
**August:** not accessed

Canonical machine checkpoint:
`research/delta/checkpoints/DELTA_005B_001_RESULTS.json`

Canonical source:
`research/delta/experiments/DELTA_005B_MICRO_RETEST.py`
blob: `4fcde1912a6011aa974525c45b7899778c72d424`

Temporary analysis Sheet:
https://docs.google.com/spreadsheets/d/1V-VHkj1jYPXebOtGcPVlhc81cvuqV4Q7pTl8ZzU37SM/edit?usp=drivesdk

## Highest-activity cell

- retest band: $0.05
- reclaim buffer: $0.00
- timeout: 1000 ms
- trades: 13,856
- winning trades: 6,280
- direct entries: 13,557
- retest entries: 299
- retest wins: 133
- retest sleeve win rate: 44.4816%
- gross profit: $1,352.95
- gross loss: -$4,280.15
- net: -$2,927.20
- max balance drawdown: $2,928.71
- average hold: 6.5979 seconds
- trade retention vs R9 Stage-A parent: 82.4713%
- winning-trade change vs parent: -14.5694%
- gross-loss improvement vs parent: 19.8927%
- drawdown improvement vs parent: 22.3119%

## Leverage conclusion

Exclusive retest continuation did not recover the opportunities removed by 005A.

Across the grid, retest-sleeve win rate stayed roughly 39–44.5%. Longer timeout mainly behaved as another exclusion mechanism rather than creating a superior continuation population.

The correct next structural question was whether the rejected break was better treated as a failed-break / sweep reversal.

## Decision

005B simple micro-retest/reclaim was not promoted.

Next unit:
`DELTA_005C_001_FAILED_BREAK_REVERSAL`

This report was reconstructed after the timeout from the immutable checkpoint and research ledger; no scientific values were altered.
