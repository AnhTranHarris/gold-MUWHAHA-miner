# DELTA 003 — Coinexx MT5 R9 Execution-Parity Calibration

**Status:** PREREGISTERED  
**Parent:** DELTA_002_DUKASCOPY_TICK_LAB  
**Strategy optimization:** PROHIBITED  
**Purpose:** Calibrate the verified DELTA tick laboratory to reproduce the preserved R9 Coinexx MT5 REAL execution/state-machine surface before new candidate research.  
**August 2026:** SEALED

## Authority hierarchy

1. R9 REAL Coinexx Strategy Tester report is the accounting/execution aggregate authority.
2. Validated R9 REAL TickLogger daily files are the per-tick state/event parity oracle.
3. DELTA-owned R9 functional summary is the state-machine specification.
4. Dukascopy remains the independent research market chronology and is not altered to force Coinexx results.

No prior internal lineage is consulted.

## Calibration phases

### A — deterministic state parity
On actual R9 REAL Coinexx ticklogger tape reproduce:
- minute-cycle start and frozen buy/sell virtual boundaries;
- completed-S1 state;
- displacement, directional efficiency, range and turns;
- completed M5 ATR(14);
- London / overlap / New York / off-session state including DST;
- spread/ATR gate;
- BUY/SELL entry eligibility;
- position lifecycle ordering;
- trail activation/movement;
- 30-second max-hold behavior;
- same-minute opposite-side rearm count/state.

### B — execution/economics parity
Freeze or infer from MT5 evidence:
- price digits / point / tick-size behavior;
- fixed lot = 0.01;
- USD account;
- leverage = 1:500;
- XAUUSD value-per-price-unit at 0.01 lot;
- entry/exit executable quote side;
- transaction-cost accounting;
- stop/trail fill semantics;
- broker minimum-stop behavior where observable;
- balance/equity accounting.

### C — cross-broker adapter
Apply the frozen Coinexx execution model to Dukascopy without changing Dukascopy Bid/Ask chronology. Report differences as market-path/feed differences, not calibration errors.

## Initial calibration tapes

- Coinexx R9 REAL 2026-01-02 daily TickLogger file, Drive ID `1mF9oUa1sbWj8ack8KRq0iGC17X_kxZJY`.
- Additional January days are permitted as needed for stable calibration.
- At least one summer/DST-period day must be checked before closure.
- R9 REAL aggregate/monthly metrics from the compact authoritative reference.

## Pass hierarchy

DELTA_003 distinguishes:
- `STATE_PARITY` — deterministic R9 feature/state/event reproduction.
- `EXECUTION_PARITY` — trade/open/close and accounting reproduction on Coinexx tape.
- `REPORT_PARITY` — aggregate comparison to MT5 REAL report.

A field unavailable from preserved evidence is not invented. It is marked `UNRESOLVED_BROKER_PROPERTY` and calibrated empirically only when the observed Coinexx ledger constrains it.

## Hard failures

- future tick use;
- midpoint fills;
- reordering same-time ticks;
- using Dukascopy outcomes to alter Coinexx state-machine logic;
- hidden parameter fitting to SYNTH;
- reading August;
- changing R9 behavior while calling the result parity.

## Output

DELTA_003 will create a versioned Coinexx broker/execution configuration, parity runner, QA report, and explicit residual mismatch ledger. It does not produce a new trading candidate.
