# GAMMA-02 — Timeout Recovery Checkpoint 005

**Status:** DURABLE / IDLE AT ATOMIC BOUNDARY
**Date:** 2026-10-07
**August:** SEALED
**MQL5:** NOT AUTHORIZED

## Current scientific base

Hour-specific unique-tick heartbeat opportunity engine:
- cap 128
- +$94,897.31
- 16,927 trades
- PF 3.74289
- +$5.60627 expectancy
- realized balance DD ~$3,167.52

Heartbeat cadence: 07=1000ms, 08=500ms, 09=250ms, 11=1000ms, 12=250ms, 13=250ms, 14=1000ms, 15=1000ms; NY18=250ms; NY17/NY16 heartbeat OFF.

Opportunity counts remain governed by: **maximum one new ticket per source per market tick.**

## Major new breakthrough — profit-funded capacity

Primary funded-cap result:
- start cap 64
- +64 slots per $2,500 realized net profit
- max cap 256
- **+$154,538.37 / 24,646 trades / PF 4.09110 / +$6.27032 expectancy**
- realized balance DD ~$4,179.75

This captures ~97.94% of the static cap-256 net while starting at cap 64.

Extreme research heat frontier:
- start cap 64
- +64 slots per $1,000 realized profit
- max cap 512
- **+$230,080.51 / 35,491 trades / PF 4.52936**
- static cap-512 control: +$239,248.19 / 41,147 / PF 4.18045

The funded cap-512 variant captures ~96.17% of static net with ~13.75% fewer trades and ~21.55% lower realized balance DD.

High caps are research heat only, not deployment recommendations.

## Supporting/rejected units completed after recovery

- heartbeat lifecycle specialist 023: supporting efficiency only; +~$96 net versus parent.
- intrinsic CUSUM pulse 024: London rejected; NY17 rejected; NY18 small positive velocity add-on only.
- directional-change partial-recovery 025: London rejected; NY17 rejected; full-reclaim rebreak remains superior.
- phase-headroom reservation 027 diagnostic: corrected source/reason ordering and rejected; leaving capacity empty reduces total net.

## Durability

Persistent Library root:
/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/

Key files: gamma02_hour_specific_heartbeat_022.py, gamma02_profit_funded_capacity_026.py, gamma02_profit_funded_capacity_026b.json, gamma02_profit_funded_capacity_026c_max512.json, gamma02_heartbeat_lifecycle_specialist_023.py, gamma02_intrinsic_cusum_pulse_024.py, gamma02_directional_change_recovery_025.py, gamma02_phase_headroom_027.py.

## Timeout discipline

All new sweeps must run one bounded unit, write partial/result JSON after each chunk, persist exact helper/result to Library, and add a GitHub checkpoint before changing the scientific base. A timed-out job without a completed artifact is NO EVIDENCE.

## First incomplete unit

**GAMMA_02_FUNDED_CAP_UTILIZATION_027**

Required: record exact cap-unlock chronology and time spent at 64/128/192/256, then full ordered-tick equity-DD certification of lower-cap funded finalists.

R9 SYNTH remains the hard target.