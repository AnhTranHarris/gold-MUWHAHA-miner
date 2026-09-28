# gold-MUWHAHA-miner

Clean-room MT5 research project to reproduce the **observable trading behavior** of Gold Hunter V8 from Strategy Tester evidence and public performance records.

## Current baseline

Development branch: `carson/v8-cleanroom-baseline`

EA source:

- `Experts/GoldMuwahahaMiner_V8_Baseline.mq5`

Research notes:

- `docs/V8_RECONSTRUCTION.md`

The current baseline implements the report-derived M1 state machine:

- fixed 0.01 lot default
- two stop orders separated by a 50-Hunter-pip band
- 50-Hunter-pip initial stop
- 20-Hunter-pip trailing stop
- opposite pending order canceled after a fill
- after a position closes inside the same minute, only the **opposite original boundary** is re-armed
- each new M1 bar resets the old boundary and creates a fresh two-sided bracket
- broker tick-size, volume-step, stop-level, filling-mode and trade-retcode handling

## Status

This is **v0.20, behavioral baseline**, not yet claimed as an exact clone. The next gate is MetaEditor compilation followed by an MT5 Strategy Tester order-sequence comparison against the supplied Gold Hunter V8 report. We should compare order fingerprints before optimizing profitability.
