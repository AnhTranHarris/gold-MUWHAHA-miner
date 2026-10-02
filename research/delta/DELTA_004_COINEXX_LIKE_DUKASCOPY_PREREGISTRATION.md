# DELTA 004 — Coinexx-Like Dukascopy Research Surface

**Status:** PREREGISTERED  
**Parent:** DELTA_003_COINEXX_R9_PARITY_CALIBRATION  
**Strategy optimization:** PROHIBITED  
**August 2026:** SEALED

## Purpose

Create an explicitly modeled Coinexx-like quote/execution surface over the independent Dukascopy central price path without altering or replacing DUKAS_NATIVE.

This is a research execution surface, not raw market data and not a trading candidate.

## Evidence-derived spread profiles

From the full January R9 REAL Coinexx logger, spread distributions by R9 session are frozen in Coinexx points ($0.01/point):

| Session | P50 | P75 | P90 |
|---|---:|---:|---:|
| OFF | 19 | 20 | 35 |
| LONDON | 19 | 20 | 34 |
| OVERLAP | 19 | 21 | 23 |
| NEW_YORK | 19 | 21 | 37 |

The default research surface is **P75**. This is selected prospectively because it is a conservative empirical friction percentile rather than the median. P50 is the median sensitivity surface; P90 is the stress surface.

No SYNTH outcome is used to build these spreads.

## Quote transformation

For each Dukascopy tick:
1. preserve its timestamp and source ordinal;
2. compute the source central path from the original Dukascopy Bid/Ask midpoint;
3. choose the modeled spread from the frozen Coinexx session/profile table using only current timestamp/session;
4. place modeled Bid/Ask symmetrically around the source midpoint, rounded to the Coinexx $0.01 tick;
5. keep the modeled spread exact in Coinexx points.

DUKAS_NATIVE remains untouched and independently queryable.

## Execution economics

Use DELTA_003:
- 0.01 lot;
- $1 P/L per $1 XAUUSD move;
- -$0.01 entry commission;
- -$0.01 exit commission;
- BUY Ask/Bid;
- SELL Bid/Ask;
- first-executable-quote protective fills.

## Acceptance criteria — default P75

Aggregate Jan-Jul absolute relative error versus R9 REAL must be:
- total trades <= 7%;
- winning trades <= 7%;
- gross profit <= 10%;
- gross-loss magnitude <= 10%;
- net-loss magnitude <= 10%.

Every month must remain within:
- total trades <= 7%;
- winning trades <= 15%;
- gross profit <= 20%;
- gross-loss magnitude <= 15%;
- net-loss magnitude <= 20%.

These are execution-surface calibration tolerances, not candidate-performance gates.

## Hard failures

- modifying the original Dukascopy files/caches;
- using future ticks;
- using SYNTH outcomes to choose spread values;
- changing spread profile after the accepted rerun;
- unlabeled mixing of DUKAS_NATIVE and modeled quotes;
- August access.

## Output

The unit produces:
- a compact modeled-surface implementation;
- frozen spread profile reference;
- Jan-Jul P50/P75/P90 R9 control results;
- calibration QA/report.

No trading candidate is promoted by DELTA_004.
