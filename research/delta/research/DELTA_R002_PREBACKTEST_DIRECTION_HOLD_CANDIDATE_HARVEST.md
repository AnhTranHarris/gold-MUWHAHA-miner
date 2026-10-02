# DELTA R002 — Pre-Backtest Direction + Hold Candidate Harvest

**Date:** 2026-10-02  
**Status:** RESEARCH_ONLY / NO_TESTING  
**Active parent:** `DELTA_004_COINEXX_LIKE_DUKASCOPY_RESEARCH_SURFACE`  
**Scope:** ENTRY + INITIAL-HOLD  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose

Convert the fresh R001 public/community scan into a bounded GOV-014 working harvest and a durable shortlist before any Dukascopy tick-level testing.

## Working workbook

Google Sheet:
`DELTA R001 Direction-Hold Candidate Harvest — Research Only`

https://docs.google.com/spreadsheets/d/1C2EOJ2WDZgVMcGG8s1WPY46-Q4U8QQXUhZytqPJVsY0/edit

The canonical reusable GOV-014 template was not edited for candidate-specific research. A copy was created.

## Candidate shortlist document

Google Doc:
`DELTA R001 — Pre-Backtest Direction + Hold Candidate Shortlist`

https://docs.google.com/document/d/1E-c8RQylJEdQJsdAxmfN6HKfYl2hDq1vZ32ErqW7idQ/edit

## Harvested research families

### Shared context / infrastructure
- DH-01 Nested Direction State
- DH-06 Quote-Pressure Initial-Hold Persistence
- DH-07 Specialist-Aware Initial-Hold State Machine

### Standalone entry specialists
- DH-02 Breakout Retest Rebreak
- DH-03 Pullback Continuation
- DH-04 Compression Expansion Continuation
- DH-05 Failed-Break Reversal

### Deferred orchestrator
- DH-08 Context Router / Specialist Ownership

The router is intentionally deferred until component evidence exists. GOV-018 heavy synthesis remains dormant.

## Pre-backtest priority

Highest research-priority items for later preparation:
1. DH-02 Breakout Retest Rebreak
2. DH-03 Pullback Continuation
3. DH-06 Quote-Pressure Initial-Hold Persistence
4. DH-07 Specialist-Aware Initial-Hold State Machine
5. DH-04 Compression Expansion Continuation
6. DH-05 Failed-Break Reversal

DH-01 is mandatory shared context infrastructure rather than a competing standalone strategy.

## Causal vocabulary frozen for later preregistration

Research definitions were written for:
- break
- acceptance
- retest
- rebreak/rejection
- pullback
- reversal
- compression
- expansion
- persistence
- retreat
- initial-hold invalidation
- conflict state
- specialist ownership

Exact formulas and thresholds remain research-pending and are not authorized by this unit.

## Public research anchors

The working shortlist is grounded in reconstructible public mechanisms including:
- MQL5 trend-line breakout/reversal EA logic;
- MQL5 breakout-and-retest implementation;
- MQL5 market regime detection / adaptive strategy selection;
- MQL5 volatility-adaptive trailing concepts;
- open-source TradingView breakout/retest and MTF trend mechanisms;
- hierarchical HMM research distinguishing short- and long-horizon regimes;
- order-flow imbalance literature motivating short-horizon quote-pressure research, with the explicit limitation that DELTA's quote proxy is not true centralized LOB OFI.

## Testing state

- empirical candidate metrics: NONE
- GOV-014 event harvest from tick replay: NOT STARTED
- Stage-A preregistration: NOT STARTED
- Dukascopy Python testing: NOT STARTED
- active promoted candidate: NONE
- metric locks: NONE
- heavy GOV-018 synthesis: DORMANT
