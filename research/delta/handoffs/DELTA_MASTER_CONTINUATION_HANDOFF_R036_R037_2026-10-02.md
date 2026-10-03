# DELTA Master Continuation Handoff — R036 Complete / R037 Next — 2026-10-02

**Status:** CURRENT READ-FIRST HANDOFF  
**Project:** Gold MUWHAHA Miner — XAUUSD  
**Branch:** `delta`  
**Current phase:** `R036_COMPLETE_INDEPENDENT_DENSITY_TOPUPS_EXHAUSTED_NEXT_SOURCE_REQUIRED`  
**Active science parent:** `DELTA_004_COINEXX_LIKE_DUKASCOPY_RESEARCH_SURFACE`  
**Operational research parent:** `R032-C03_PLUS_DH02_S11_S08`  
**Promoted candidate:** NONE  
**Primary metric locks:** NONE  
**August 2026:** SEALED  
**MQL5:** NOT AUTHORIZED  
**MT5 translation ready:** FALSE  

## Authority

Use:
1. current owner instruction;
2. live `delta/CURRENT_STATE.json`;
3. DELTA governance through GOV-018;
4. this handoff;
5. R037 restart contract;
6. current workbook / R-series reports.

Separate-lineage-only material in the master protocol belongs to a different repository and does not supersede DELTA.

## Startup

A new chat must:
1. read live `CURRENT_STATE.json`;
2. read the Drive READ-FIRST handoff pack;
3. read stage-index current-frontier override;
4. read R032-R036;
5. inspect workbook tabs 60-68;
6. read R025 if ownership/no-rearm reconstruction is needed;
7. read R018 only for completed GOV-018 Cycle-1 provenance;
8. resume R037 only.

Do not restart completed R001-R036 after a UI timeout.

## Current architecture lineage

### R010 / R014
P01:
`I250 <= -0.55 OR H1NetATR > 0.35`

True:
- flip intended R9 side;
- assign ownership;
- suppress generic same-minute rearm after owned exit;
- reset ownership next M1.

Exact R010 Jan-Jul P75:
- R9: 234,417 trades / 103,097 wins / net -$49,001.79 / GL -$78,244.86.
- R010: 203,864 trades / 90,751 wins / net -$42,668.19 / GL -$67,676.50.
- net-loss improvement 12.93%;
- GL improvement 13.51%;
- trade retention 86.97%;
- winner retention 88.02%.

### R025 robust M30 KEEP-owned component

P01 condition:
`H1NetATR > 0.35 OR micro250 impulse <= -0.55`

M30-only:
`M30NetATR > 0.35 AND NOT(P01)`

M30-only action:
KEEP intended R9 side + assign ownership + suppress generic same-minute rearm.

Jan-Jul P75:
- 195,990 trades;
- 87,214 wins;
- net -$41,045.86;
- GL -$65,076.38;
- trade retention 83.6074%;
- winner retention 84.5941%;
- net-loss reduction 16.2360%;
- GL reduction 16.8298%.

R025 is a validated component, not a promoted total system.

### R028/R029

Generic same-minute rearm repair and post-exit recentered brackets are closed. NO_REARM improves losses but starves activity. Restoring activity with same-minute rearm/recenter variants worsens net.

### R032 current operational parent

R032-C03 =
R025 ownership
+ GLOBAL NO_REARM for ordinary generic rearms
+ DH03-S06
+ DH05-S06
+ DH02-S11
+ DH02-S08

P50/P75 pass.
P90:
- 2,388 trades;
- 1,050 wins;
- trade retention 79.706275%;
- winner retention 83.267248%;
- net -$554.14;
- +$4.00 net vs ordinary opposite-rearm control;
- about nine trades short of 80% trade floor.

Not promoted. No lock.

### R033-R036 closed top-up paths

DH02-A01:
broad incremental stream is toxic; later-January frozen pockets all failed OOS. Do not recut.

DH-04:
A01 restores activity but worsens net. S03 worsens net. S07 tiny P90 +$0.23 edge failed P50/P75 (-$2.78/-$3.19). Current DH-04 density-addition role retired.

## Family disposition

- DH-01: context only; no old categorical global gate.
- DH-02: conditional specialist; A01 late-Jan density recut closed.
- DH-03: conditional specialist; S06 already in R032-C03.
- DH-04: current density role retired.
- DH-05: conditional specialist; S06 in R032-C03.
- DH-06: observer/context retained; R007 generic post-entry action mapping stopped.
- DH-07: current generic adapter stopped.
- GOV-018: capability ACTIVE; Cycle 1 COMPLETE, not to be rerun.

## R037

Next unit:
`R037_FRESH_INDEPENDENT_OPPORTUNITY_SOURCE_RESEARCH_AND_PREREGISTRATION`

First deliverable is research/preregistration, not a replay.

The new opportunity source must:
- be independent of the just-closed trade;
- not be generic same-minute rearm;
- not be post-exit recentered bracket logic;
- not be DH02-A01 late-Jan recutting;
- not be current DH-04 density recutting;
- use causal/right-edge-known inputs;
- be reconstructible;
- define ownership/collision behavior with R032-C03;
- preserve activity as co-primary.

## MT5

Do not code MQL5 yet.

Before `mt5_translation_ready=true`, DELTA still needs:
- a promoted/frozen final candidate;
- frozen formulas/state precedence/ownership;
- P50/P75/P90/native sensitivity;
- Python↔MT5 tick/candle/feature/lifecycle parity fixtures;
- trade-count reconciliation;
- session/DST parity;
- resolved or isolated broker properties;
- human QA;
- owner approval.

Unresolved broker properties from DELTA_003:
- StopsLevel;
- FreezeLevel;
- filling-mode enum;
- margin stopout mode/level;
- commission scaling outside 0.01 lot.

## Execution contract

- BUY entry Ask / exit Bid.
- SELL entry Bid / exit Ask.
- stop fill first executable quote after cross.
- 0.01 lot.
- $0.02 round-trip commission at 0.01.
- tick-rooted candles; left-closed/right-open.
- completed bars visible only at right edge.
- position-observation latch required before rearm.
- August sealed.

## Timeout recovery

Persist each material step before the next:
prereg -> code -> compute -> result -> decision -> CURRENT_STATE last.

After timeout:
1. read live CURRENT_STATE;
2. read this handoff;
3. inspect exact interrupted artifact;
4. resume first missing durability step only.

## Drive pack

Folder:
https://drive.google.com/drive/folders/1n4hRXXEyQlPJuLKICPVFBjc2MxW2Jagg

READ FIRST:
https://docs.google.com/document/d/1EvyYTzyafViJE7XBcDYNes8MV07ralIvFgwe8bDzb2U/edit

R037 contract:
https://docs.google.com/document/d/1yfAl6mANMqu__OB-dRM_8yoBa3XbX7day12-_r_Kn0c/edit

MT5 readiness:
https://docs.google.com/document/d/1a4bSQAbk1mQCUN1h088A2okVnTuKuohJlOsigDDjOn4/edit

Artifact map:
https://docs.google.com/document/d/1Ux1w4pZRUaAc9GNmNP9clbjZc3tLg05to7TGZ73BgCk/edit

## Current gate

R036 COMPLETE.  
R037 NEXT.  
Promoted candidate NONE.  
Metric locks NONE.  
August SEALED.  
MQL5 NOT AUTHORIZED.
