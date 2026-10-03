# DELTA MT5 Translation Readiness and Blockers — 2026-10-02

**MT5 translation ready:** FALSE  
**MQL5 coding authorized:** FALSE  
**Promoted candidate:** NONE  

## Ready/frozen research engineering

- ordered Dukascopy Jan-Jul ticks;
- P50/P75/P90 Coinexx-like modeled surfaces;
- DUKAS_NATIVE preserved;
- BUY Ask / exit Bid;
- SELL Bid / exit Ask;
- protective stop fill = first executable quote after cross;
- fixed 0.01 lot;
- $0.02 RT commission at 0.01 lot;
- direct tick-rooted candles;
- left-closed/right-open boundaries;
- completed bars visible at right edge;
- same-timestamp deterministic ordering;
- position-observation latch.

## Validated architecture component

R025 M30_KEEP_OWNED is evidence-bearing but not a complete candidate.

P01:
`H1NetATR > 0.35 OR micro250 <= -0.55`
=> flip intended side + ownership + suppress generic same-minute rearm.

M30-only:
`M30NetATR > 0.35 AND NOT(P01)`
=> KEEP intended side + ownership + suppress generic same-minute rearm.

Jan-Jul P75:
195,990 trades / 87,214 wins / net -$41,045.86 / GL -$65,076.38.

## Current near-gate parent

R032-C03 =
R025 ownership
+ GLOBAL NO_REARM
+ DH03-S06
+ DH05-S06
+ DH02-S11
+ DH02-S08.

Not promoted.

## Build blockers

### Final candidate
No promoted/frozen total-system candidate exists.

### Ownership/concurrency
Final ordering must freeze:
- stop handling;
- bar/tick state updates;
- minute reset;
- position management;
- ownership release;
- specialist proposals;
- duplicate/collision priority;
- R9 proposal;
- GLOBAL NO_REARM;
- specialist expiry/reset.

### Native sensitivity
DUKAS_NATIVE must remain explicit. R010 native activity was sparse because R9's 25-point spread gate rejects most native ticks. Final promotion must define how native sensitivity is interpreted rather than silently omitting it.

### Python↔MT5 parity
Required:
- tick ordering;
- 250 ms bucketing;
- all used bar boundaries;
- Bid/Ask OHLC;
- completed-bar visibility;
- same-timestamp ordering;
- sparse/no-tick behavior;
- session/DST;
- I250;
- H1NetATR;
- M30NetATR;
- all final specialist features;
- ownership state;
- fill/stop/exit lifecycle;
- trade-count reconciliation.

### Broker properties unresolved
- SYMBOL_TRADE_STOPS_LEVEL;
- SYMBOL_TRADE_FREEZE_LEVEL;
- filling-mode enum;
- margin stopout mode/level;
- commission scaling beyond 0.01 lot.

### Human/owner
- human QA packet;
- owner approval before coding;
- owner approval after Coinexx Strategy Tester validation.

## Stopped mappings that must not leak into EA

- R007 generic DH-06 post-entry action mapping;
- current generic DH-07 initial-hold adapter;
- generic same-minute rearm repair;
- recentered post-exit bracket family;
- DH02-A01 late-Jan recuts;
- current DH-04 density recuts.

## Deferred

- mature exit/high-profit optimization;
- profit-zone selection;
- aggressive capital policy;
- lot ladder;
- small-account dynamic sizing;
- August holdout.

## MT5-ready definition

Set `mt5_translation_ready=true` only after:
- promoted frozen Python parent;
- rebuild-ready producing artifacts;
- exact formulas/order/timing;
- frozen ownership/concurrency;
- quote/fill semantics;
- session/DST;
- risk/lot semantics;
- parity fixtures;
- trade-count reconciliation;
- human QA;
- owner authorization.

## Drive

Full readiness document:
https://docs.google.com/document/d/1a4bSQAbk1mQCUN1h088A2okVnTuKuohJlOsigDDjOn4/edit
