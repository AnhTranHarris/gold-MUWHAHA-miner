# BETA071 — Structural Acceptance, Sweep/Reclaim and Compression Opportunity Clocks

**Date:** 2026-10-01  
**Parent:** BETA063 safe causal base  
**Status:** PREREGISTERED / NOT TESTED  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose

BETA065–070 repeatedly showed that dense micro/retest proposal clocks have predictable friction but insufficiently predictable 30-second direction. BETA071 changes the **opportunity generator** rather than adding another classifier or looser threshold.

Four standalone causal families are screened on one original Dukascopy January ledger:

1. **FAST_ACCEPTANCE** — confirmed structural boundary, completed close beyond it, breakout quality measured continuously.
2. **FIRST_RETEST** — first return to a broken frozen boundary within a bounded window, then completed close back on the break side.
3. **SWEEP_RECLAIM** — excursion beyond a confirmed boundary followed by a completed close back inside; direction is opposite the failed break.
4. **COMPRESSION_RELEASE** — completed 20-bar M1 compression box followed by a completed close outside the frozen box.

No mechanism must confirm another. They are competing opportunity clocks.

## Structural causality

M1 and M5 pivots use left2/right2 completed bars. A pivot centered on bar i is not available until bars i+1 and i+2 have closed. Its confirmation timestamp is the RIGHT edge of bar i+2. It may influence events only after that timestamp.

No historical pivot is backdated. No future extrema enter features.

## Execution causality

An event is visible only at a completed M1 right edge. The simulated order executes on the first source tick **strictly after** that event timestamp. BUY uses Ask; SELL uses Bid. Markout exits use the opposite executable quote at 30/60/120 seconds plus the established $0.02 round-trip research fee.

## Bounded variants

Break displacement / ATR: 0.0, 0.10, 0.20, 0.30.  
Retest tolerance / ATR: 0.10, 0.20, 0.30.  
Compression width / ATR: 2.0, 3.0, 4.0.

These are transparent neighborhoods, not one optimized magic threshold.

## Selection

Standalone mechanisms are compared first. CAL may identify a mechanism/parameter/horizon candidate only if:
- >= 50 one-position trades;
- positive after-cost net;
- PF > 1;
- positive average trade;
- positive result at a neighboring parameter or neighboring horizon;
- no DIAGNOSTIC data used for selection.

A qualifying policy is serialized before DIAGNOSTIC is opened.

## Human QA contract

A surviving event must be explainable as:
`confirmed level -> state transition -> event time -> entry quote -> reason features -> selected horizon -> result`.

The review packet will expose setup ID, mechanism, side, level/timeframe, pivot confirmation time, break/retest/sweep/compression measurements, spread, entry/exit quote, P&L and skip/ownership reason.

## Provenance

This reconstruction follows the project's BETA019 multilingual community research and the historical mechanism recovery map. Public community logic supplies only the mechanism definitions; original ordered Dukascopy replay determines whether any economic edge exists.
