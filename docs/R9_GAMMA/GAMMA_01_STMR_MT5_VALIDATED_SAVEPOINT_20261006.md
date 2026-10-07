# R9 GAMMA-01 STMR MT5-Validated Major Savepoint — 2026-10-06

## Status

**MAJOR CERTIFICATION CHECKPOINT. FREEZE BEFORE NEXT GRID RESEARCH LAYER.**

This checkpoint records the first STMR/grid foundation that is positive in both the Dukascopy ordered-tick Python environment and Coinexx MT5 `Every tick based on real ticks`, with matching month-sign structure and closely aligned trade counts.

## Validated MT5 baseline

EA: `Experts/GoldMuwahahaMiner_R9_GAMMA_01_STMRGrid_ClockFix.mq5`

Required baseline mode for all next grid descendants:

- `InpCoreEnabled = false`
- `InpGridEnabled = true`
- `InpGridClockMode = STMR_GRID_CLOCK_COINEXX_AUTO`
- Coinexx historical clock normalization: UTC+2 standard / UTC+3 US DST
- XAUUSD only
- M1 host chart
- fixed 0.01 lot
- maximum 3 grid-owned positions
- hedging account
- broker certification with `Every tick based on real ticks`

These settings are no longer discretionary tester settings for the next grid lineage. The next MT5 build must hard-code them unless a later preregistered experiment explicitly reopens one.

## Coinexx grid-only certification

Source report: `ReportTester-871471_grid_clock_2.xlsx`

SHA-256: `01a8cea2a19e15203447ea2ab68107ea1902f7760331d480e661521fdd82e229`

Jan-Jul 2026:

- net: **+$579.60**
- gross profit: **+$3,406.99**
- gross loss: **-$2,827.39**
- PF: **~1.2050**
- trades: **2,582**
- expected payoff: **~+$0.2245/trade**
- win rate: **~31.25%**

## Dukascopy Python comparator

`STMR_XMONTH_SUBPHASE_001`:

- net: **+$829.71**
- gross profit: **+$3,625.77**
- gross loss: **-$2,796.06**
- PF: **1.2967426**
- trades: **2,675**
- expected payoff: **+$0.31017/trade**
- win rate: **32.79%**

Both environments produce the same monthly sign sequence:

`Jan + / Feb + / Mar + / Apr - / May - / Jun + / Jul -`

This is sufficient to freeze the current session/timeframe layer as a validated foundation.

## Hard north-star: R9 SYNTH

R9 SYNTH is the **hard objective**, not a soft reference.

Canonical Jan-Jul 2026 target vector:

- net profit: **+$309,122.85**
- gross profit: **+$325,361.51**
- gross loss: **-$16,238.66**
- PF: **20.036229**
- expected payoff: **+$1.409319/trade**
- trades: **219,342**
- win rate: **87.14063%**
- active trading days: **149**
- trades/active day: **1,472.09396**
- average hold: **17.315443 sec**
- median hold: **17 sec**

The current +$579.60 Coinexx grid is therefore a trustworthy base, **not remotely the final performance objective**.

## Hard promotion rules for every next layer

1. Preserve what is already working and compound improvements on top of it.
2. Every accepted layer must materially close the cumulative gap toward the R9 SYNTH target vector.
3. Sub-1% cosmetic improvements are not an acceptable endless optimization path.
4. Evaluate the system as a whole: net, gross profit/loss, PF, expectancy, win rate, trade velocity, holding-time behavior, drawdown/survivability, and hostile-month persistence.
5. A local win that damages the total system is not a promotion.
6. Rejected ideas remain negative evidence and are not silently recycled.
7. Do not destroy the newly validated Coinexx/Dukascopy cross-environment alignment without extraordinary evidence.
8. April, May, and July are shared real weaknesses and must be repaired with causal state, not calendar labels.
9. August remains sealed until explicit authorization.

## Rollback rule

If future work fails, return here. Do not reconstruct this checkpoint from conversation memory.

Durable cloud backup:

- Drive folder: `04_MAJOR_SAVEPOINT_STMR_MT5_VALIDATED_2026-10-06`
- raw certified report stored unchanged in that folder
- Drive read-first document records the same hard rules and target vector
