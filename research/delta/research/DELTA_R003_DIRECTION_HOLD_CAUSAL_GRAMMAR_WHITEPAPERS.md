# DELTA R003 — Direction + Hold Causal Grammar White Papers

**Date:** 2026-10-02  
**Status:** RESEARCH_ONLY / NO TESTING  
**Active parent:** `DELTA_004_COINEXX_LIKE_DUKASCOPY_RESEARCH_SURFACE`  
**Scope:** ENTRY + INITIAL-HOLD  
**August 2026:** SEALED  
**MQL5:** NOT AUTHORIZED

## Stage folder

Google Drive folder:

`DELTA R001 Direction-Hold Candidate Harvest — Research Only`

https://drive.google.com/drive/folders/1iCg7Ptl8zRQ-5QUFGSuB7sPTqsNKzxiX

The working GOV-014 harvest workbook and pre-backtest shortlist document were moved into this stage folder. Seven candidate/component white papers were created there.

## Frozen v0 timeframe-role grammar

DELTA's full tick-rooted hierarchy remains authoritative.

For R001 v0 direction/hold research, the documented role bundles are:

- Micro observation: TICKS, S0.25, S1
- Fast execution context: S5, S15, S30, S45
- Execution structure: M1, M5
- Intermediate structure: M15, M30
- Higher structural context: H1, H4

Other DELTA timeframes remain available but are not part of the R001 v0 feature grammar unless a later research unit explicitly adds them.

## Candidate/component white papers

### DH-01 — Nested Direction State
Role: shared context infrastructure.
Drive:
https://docs.google.com/document/d/1WrDPUavWb-bbv7gmxnnlEAFjT1NA9wYbPAwl-ayREAw/edit

Frozen grammar includes:
- midpoint signal features;
- NetMove, Path, SignedEfficiency, DirectionalDisplacement;
- causal confirmed swing structure;
- trend-within-trend state taxonomy;
- completed-bar/right-edge anti-lookahead rules.

### DH-02 — Breakout Retest Rebreak Specialist
Role: standalone entry specialist.
Drive:
https://docs.google.com/document/d/18KpLADXCt-MlIQgZ4j6papHdE7SUtrl8kVTbn0x1XNc/edit

Frozen state chain:
`IDLE -> ARMED -> BROKEN -> ACCEPTED_BREAK -> RETESTING -> RETEST_HELD -> REBREAK_CONFIRMED -> ENTRY_ELIGIBLE`
with explicit FAILED / EXPIRED branches.

### DH-03 — Pullback Continuation Specialist
Role: standalone entry specialist.
Drive:
https://docs.google.com/document/d/13pa0KSxVy93yajDEGAIkeY4V8Z3egMDIPxPV0nM3ia8/edit

Frozen logic separates:
- parent trend validity;
- fast countertrend pullback;
- exhaustion candidate;
- local reclaim;
- reacceleration;
- specialist-specific early invalidation.

### DH-04 — Compression Expansion Continuation Specialist
Role: standalone entry specialist.
Drive:
https://docs.google.com/document/d/1S9VYfq3DrDqabMaHHqq6BB2ueB-CPBw9OLYnFOZlQDg/edit

Frozen features include:
- causal compression box;
- ATR/true-range-normalized compression;
- frozen box at arm time;
- expansion probe/acceptance/quality;
- initial invalidation on accepted re-entry into the box.

### DH-05 — Failed-Break Reversal Specialist
Role: standalone reversal specialist.
Drive:
https://docs.google.com/document/d/1mIcrUUeK0lGwfR6L_26O47DQxQV7xygbnFcnkvE4s6k/edit

Frozen state chain:
`IDLE -> PROBE -> FAILURE_CANDIDATE -> REENTRY -> RECLAIM_CONFIRMED -> FAILED_BREAK_CONFIRMED -> REVERSAL_REBREAK -> ENTRY_ELIGIBLE`.

An accepted original breakout is explicitly routed away from DH-05.

### DH-06 — Quote-Pressure Initial-Hold Persistence
Role: shared initial-hold component.
Drive:
https://docs.google.com/document/d/1MAkyDsu1TK7VC8Rlx4ahlIxznPFEJKy_uX4k31heIhc/edit

Frozen deterministic tick-derived features:
- FavDisplacement
- Path
- DirectionalEfficiency
- StepBalance
- BidAskImpulse
- RetreatFraction
- SpreadStress
- TickRate / TickRateRatio

Observation windows:
250 ms, 1 s, 3 s, 5 s.

The component is explicitly a quote-pressure proxy, not true centralized limit-order-book OFI.

### DH-07 — Specialist-Aware Initial-Hold State Machine
Role: shared initial-hold state machine.
Drive:
https://docs.google.com/document/d/1CyZ-WBMpBCfQfz_dnfbOAfCktDgbC7uPlW-72NGM7ww/edit

Frozen checkpoints:
fill, 250 ms, 1 s, 3 s, 5 s, 10 s, 15 s.

Frozen high-level states:
`FILLED_VULNERABLE -> MICRO_ASSESSMENT -> DEVELOPING / UNCERTAIN_HYSTERESIS -> ESTABLISHING -> INITIAL_HOLD_SURVIVED`
with EARLY_INVALIDATE and HARD_STOP_EXIT branches.

Mature hold, profit exit, and high-profit logic remain deferred.

## Working workbook index

The R001 working workbook now contains a new tab:

`11 White Papers`

It records each white paper, role, stage, grammar status, threshold status, testing status, and Drive link.

Working workbook:
https://docs.google.com/spreadsheets/d/1C2EOJ2WDZgVMcGG8s1WPY46-Q4U8QQXUhZytqPJVsY0/edit

## Threshold policy

The white papers freeze:
- feature identity;
- formula meaning;
- timeframe ownership;
- state-transition order;
- causal visibility;
- specialist thesis/invalidation semantics.

They intentionally do **not** freeze optimized numeric thresholds.

Thresholds remain parameter slots for later preregistration before Stage-A Dukascopy replay.

## Testing state

- empirical event harvesting from Dukascopy: NOT STARTED
- Stage-A preregistration: NOT STARTED
- Python/tick replay: NOT STARTED
- promoted candidate: NONE
- metric locks: NONE
- GOV-018 heavy synthesis: DORMANT
- August: SEALED
- MQL5: NOT AUTHORIZED
