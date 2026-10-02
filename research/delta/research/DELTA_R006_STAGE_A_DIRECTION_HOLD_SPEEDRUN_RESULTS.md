# DELTA R006 — Stage-A Direction-Hold Speed-Run Results and Refinement Decisions

**Status:** COMPLETE — FAMILY TRIAGE / NO PROMOTED CANDIDATE  
**Active parent:** `DELTA_004_COINEXX_LIKE_DUKASCOPY_RESEARCH_SURFACE`  
**Scope:** ENTRY + INITIAL-HOLD  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Execution fixture

`R005-EXEC-FIXTURE-01` was frozen before the first candidate result:

- SignedEfficiency lookback: 4 completed bars for S5/S15/S30/S45/M1/M5.
- SignedEfficiency lookback: 3 completed bars for M15/M30/H1/H4.
- ATR period: 14 completed bars.
- Surface: DELTA_004 P75.

## Stage-A control

- ticks: 4,205,709
- R9 trades: 16,801
- winners: 7,351
- win rate: 43.7533%
- gross profit: +$1,574.77
- gross loss: -$5,343.02
- net: -$3,768.25
- max balance DD: $3,769.83
- max equity DD: $3,770.33
- average hold: 6.712 seconds
- net expectancy: -$0.224287/trade

## R005 completion

All **76 / 76** immutable R005 vectors were evaluated.

The tested universe remains preserved in the canonical working Sheet tabs:
- `18 Stage-A Results`
- `19 Family Decisions`
- `20 Refinement Queue`

## Family decisions

### DH-06 — REFINE NOW / HOLD FOR INTEGRATION

Strongest current causal observer signal.

Representative vectors:
- S08: PnL separation favorable-vs-retreat ~$0.686/trade; favorable coverage 8.18%; favorable-state WR 87.6%; retreat coverage 31.7%.
- S06: separation ~$0.747; favorable coverage 3.68%; favorable-state WR 91.7%.
- A04: separation ~$0.657; favorable coverage 9.33%; favorable-state WR 84.9%.
- S03: separation ~$0.693; favorable coverage 5.34%; favorable-state WR 87.6%.
- S04: largest separation ~$0.774 but only 0.44% favorable coverage; retain as strict-signal research anchor.

This was observer-only and is **not** a realized PnL improvement claim.

**Decision:** advance S08/S06/A04/S03 into bounded active-modifier refinement.

### DH-02 — RESTRUCTURE AS CONDITIONAL SPECIALIST

Standalone Breakout-Retest-Rebreak fails activity preservation.

Quality anchors:
- S11: 75 trades; 0.446% R9 activity retention; WR 54.67%; expectancy -$0.1095/trade, ~51.2% less negative than R9 control expectancy.
- S08: 75 trades; 0.446% retention; WR 56%; expectancy -$0.1185/trade.
- S03: 20 trades; 0.119% retention; WR 65%; expectancy -$0.1255/trade.

Density anchor:
- A01: 684 trades; 4.07% retention; expectancy -$0.2121/trade.

**Decision:** current standalone/global replacement architecture fails. Preserve DH-02 for conditional event ownership while unrelated R9 opportunities remain available.

### DH-03 — RESTRUCTURE AS CONDITIONAL SPECIALIST

Standalone Pullback Continuation also remains activity-starved.

- A04 quality anchor: 485 trades; 2.89% retention; WR 48.25%; expectancy -$0.1850/trade, ~17.5% less negative than R9.
- S06 density/quality anchor: 1,563 trades; 9.30% retention; expectancy -$0.2168/trade, ~3.32% less negative.
- S01 secondary density anchor: 867 trades; 5.16% retention; expectancy -$0.2198/trade.
- A01 highest activity: 2,327 trades; 13.85% retention, but expectancy worsened to -$0.2340/trade.

**Decision:** no standalone promotion. Preserve A04 and S06/S01 for conditional pullback-specialist ownership research.

### DH-01 — MORE RESEARCH / CONTEXT ONLY

Nested-direction labels produced measurable but modest outcome separation (state-average PnL spread roughly $0.007–$0.032/trade), but the categorical semantics were not monotonic. In multiple vectors, CONFLICT_CHOP or LOCAL_REVERSAL_ATTEMPT was less negative than ALIGNED_CONTINUATION/PULLBACK.

**Decision:** retain as context vocabulary/features. Do not use v0 categorical state as a global hard gate. Research continuous signed-efficiency/displacement/structure descriptors.

### DH-07 — FAIL CURRENT ADAPTER / REDESIGN LATER

Best counterfactual savings under the current R9-boundary adapter were +$37.39, less than 1% of Stage-A control loss magnitude, while that same vector falsely flagged ~42.2% of winning trades.

**Decision:** stop local tuning of the current generic adapter. Specialist-aware initial hold remains conceptually open but should be rebuilt around a viable specialist/DH-06 state.

### DH-04 — PREREGISTER AND TEST NEXT

Not part of frozen R005 vector library. No empirical result is inferred.

### DH-05 — PREREGISTER AND TEST NEXT

Not part of frozen R005 vector library. No empirical result is inferred.

## Refinement queue

1. **P0 — DH-06:** active persistence modifier refinement using S08/S06/A04/S03.
2. **P1 — DH-02:** conditional breakout/retest ownership restructure; use S11/S08/S03 quality anchors + A01 density anchor.
3. **P1 — DH-03:** conditional pullback ownership restructure; use A04 quality anchor + S06/S01 density anchors.
4. **P2 — DH-01:** continuous-context redesign.
5. **P2 — DH-04/DH-05:** create immutable preregistered vector extensions before testing.
6. **P3 — DH-07 current adapter:** STOP; redesign only after specialist-specific thesis boundaries exist.

## Architectural conclusion

R006 does not support replacing R9's entire opportunity engine with a strict specialist grammar.

It supports:
- preserving the high-density R9 opportunity surface;
- using narrow specialists as conditional owners of particular event classes;
- refining first-seconds quote-pressure persistence because it produced the strongest discrimination;
- keeping initial-hold adaptation downstream of specialist thesis and causal persistence.

## Provenance

R005 vector-library SHA-256:

`9dfcdcd83bae9452291b2b249d41ac4f19751e23f1ff91ae6e1d581707528b52`

R005 run-sheet SHA-256:

`3e2728bb1a0db7e2423892d4756591e246ddb646c9f2a2a0a82618e983e5275a`

Execution sources:
- `r005_speedrun.py`: `43adbc79bbe95188e3d9ccd452519da6a23a9e58bffa425dc177285cdf054b5a`
- `r005_observers.py`: `c1e1b331d1acdff222cbe469d65abf326f89120cefc7de91ec771883506ddb71`
- `r005_specialists.py`: `fe1ccb8112f5bf37c83e7ce9e9dd82f782397a7710029716a61c159e4005afe0`

Result artifacts:
- `observer_results.json`: `381775ad047ad57d33389b16a3cc641364c67778381f75e549e098d463c95e36`
- `dh02_results.jsonl`: `4147397ec47a78a9af8478771d5279f3419929867d1b38bdb1650ba75161479f`
- `dh03_results.jsonl`: `3095a170efcd7cd644e6d2a371bec7723efab12a2c5c8921eba853bde4a4eb34`

## Current gate

- Stage-A R005 speed run: COMPLETE
- active promoted candidate: NONE
- primary metric locks: NONE
- DH-06 refinement: QUEUED / NOT YET EXECUTED
- DH-02/DH-03 restructuring: QUEUED / NOT YET EXECUTED
- DH-04/DH-05: UNTESTED / PREREGISTRATION REQUIRED
- DH-07 current adapter: STOPPED
- August: SEALED
- MQL5: NOT AUTHORIZED

## Post-timeout durability QA

The message-delivery timeout did not invalidate or restart R006.

Recovery QA confirmed:
- all 76 immutable vector results remain present;
- all 78 Stage-A run-sheet jobs are `COMPLETE_STAGE_A_SPEEDRUN`;
- persisted result artifacts still match their recorded SHA-256 hashes exactly;
- no candidate result was recomputed, edited, or promoted during recovery;
- stale `NOT_STARTED` / `NOT_EXECUTED` fields in `CURRENT_STATE.json` were reconciled;
- DH-04 and DH-05 remain explicitly untested.

