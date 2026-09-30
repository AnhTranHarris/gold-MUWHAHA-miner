# BETA064 MAJOR CHECKPOINT 02 — ENTRY+HOLD MT5 PRODUCTION CONTRACT

**Purpose:** prevent future MT5 reconstruction drift. This is the authoritative coding contract for the frozen session-aware Entry→Hold checkpoint.  
**Scope:** Entry generation, session context, routing, position ownership, thesis packet and Hold-state evaluation.  
**Out of scope:** Hold→Exit / production trade liquidation policy.

## 1. Non-negotiable source order

Before writing MQL5, read in this order:

1. `CURRENT_STATE.json`
2. `research/BETA_064_MAJOR_CHECKPOINT_02_SESSION_AWARE_ENTRY_HOLD_FREEZE.md`
3. `research/artifacts/BETA_064_MAJOR_CHECKPOINT_02_MODEL_MANIFEST.json`
4. `research/experiments/BETA_064_R1B2_SPECIALIST_REGISTRY.py`
5. `research/experiments/BETA_064_C02_SESSION_GAPFILL_ROUTER.py`
6. `research/BETA_064_R1B2_ENTRY_HOLD_85_SURVIVABILITY_RESEARCH_RECORD.md`
7. `research/BETA_064_CHECKPOINT_02A_SESSION_GAPFILL_SPECIALIST.md`
8. `research/BETA_064_CHECKPOINT_02_DUAL_TICK_SYNTH_VS_DUKAS_ENTRY_HOLD_DIAGNOSTIC.md`

If these sources disagree, the Major Checkpoint 02 freeze and this production contract control unless the owner explicitly creates a later checkpoint.

## 2. Build status labels

Allowed future MT5 labels before Hold→Exit exists:

- `BETA_CKPT02_ENTRY_HOLD_INSTRUMENTATION`
- `BETA_CKPT02_ENTRY_HOLD_PARITY`
- `BETA_CKPT02_ENTRY_HOLD_TESTER_ONLY`

Forbidden labels before Hold→Exit certification:

- production
- live
- final
- release
- approved EA
- investor-ready

## 3. Required MT5 module boundaries

Do not implement the checkpoint as one giant OnTick function.

Required conceptual modules:

### A. TickChronologyEngine
- consumes every observable tick in stable order;
- reconciles missed/coalesced NewTick callbacks with `CopyTicksRange`;
- maintains source ordinal/timestamp identity where possible;
- never fabricates intermediate ticks.

### B. MultiScaleStateEngine
Builds the causal state used by the Python checkpoint.

Minimum state families:
- 5-second completed OHLC/mid/bid/ask/spread/tick-count buckets;
- r15/r30/r60/r300/r900/r3600/r14400;
- eff15/eff60/eff300/eff900/eff3600;
- vol60/vol300;
- atr60/atr300;
- tick_z;
- signed quote-pressure proxy;
- quote-volume imbalance proxy;
- day/session quote-activity-weighted value and normalized displacement;
- range ratio;
- confirmed prior structural highs/lows;
- completed-bar body/range.

Critical parity rule:
a 5-second bucket containing [t,t+5s) is not observable until t+5s.

### C. SessionAuthorityEngine
Timezone-aware local sessions:

- Australia/Sydney 08:00–17:00
- Asia/Tokyo 09:00–18:00
- Asia/Dubai 08:00–17:00
- Europe/Berlin 08:00–17:00
- Europe/London 08:00–17:00
- America/New_York 08:00–17:00

Must use calendar-aware DST conversion for Sydney, Berlin, London and New York.

Session-derived structures:
- first 15-minute ORB after local open;
- 30-minute pre-open high/low;
- running session high/low excluding current completed bucket;
- session-anchored quote-activity-weighted value;
- previous completed session high/low;
- relative minutes from local open.

### D. EntrySpecialistEngine
Implements the frozen E1–E12 candidate definitions exactly.

Do not collapse specialists into one rule set. Each proposal must carry:
- specialist id;
- side;
- timestamp;
- raw score;
- specialist horizon;
- Hold checkpoint age;
- session context;
- causal state snapshot.

### E. FrozenBaseRouter
Uses the exact frozen Checkpoint-01 learned Entry models and gates:
- `P_survive >= 0.88`
- `entry_score = P_survive × P_first_passage`
- `entry_score >= 0.30`

The learned model feature order is immutable and specified by the model manifest.

### F. SessionGapFillRouter
Runs only when the frozen base schedule has no active/reserved position.

Eligibility:
- candidate is not already a base trade;
- specialist is in E5/E6/E7/E9/E10/E11/E12;
- broad session survival score >= 0.89;
- broad session economic score >= 0.08;
- session-specific survival authority passes.

Thresholds:
- Australia 0.920
- Asia 0.900
- Middle East 0.915
- Europe 0.910
- UK 0.925
- New York 0.925

Base ownership always wins.

### G. PositionOwnershipEngine
One account / one open research position.

A session gap-fill trade must not overlap a reserved Checkpoint-01 interval.

Future live implementation must replace simulated horizon reservation with actual order/fill/position state while retaining the same priority rule.

### H. ThesisPacket
At fill, persist:
- origin specialist;
- origin router: BASE or SESSION_GAPFILL;
- session authority/overlap state;
- side;
- causal feature snapshot;
- predicted survival probability;
- predicted favorable-first-passage probability;
- economic score;
- raw specialist score;
- expected horizon;
- Hold checkpoint;
- structural/value invalidation references;
- entry Bid/Ask/spread;
- model/checkpoint version id.

This packet must remain attached to the position for the Hold layer.

### I. HoldStateEngine
Implements H1–H8 state variables:
- H1 Ignition Confirmation
- H2 Extension / Runner Persistence
- H3 Healthy Pullback
- H4 Reacceleration
- H5 Transient Scalp / Fragile Continuation
- H6 Stall / Chop
- H7 Failed Acceptance / Thesis Failure
- H8 Exhaustion / Climax

Required post-fill inputs include:
- MFE;
- MAE;
- current executable excursion;
- hold age;
- entry recross count;
- favorable/adverse excursion speed;
- path efficiency;
- new-extreme renewal;
- spread evolution;
- quote intensity;
- signed quote pressure;
- current cross-scale state;
- origin thesis packet.

### J. SharedContinuationArbiter
Current checkpoint role:
estimate continuation worthiness / post-checkpoint favorable first-passage probability.

It is not permitted to invent a production exit.

## 4. Exact path-label geometry used in research

For offline labels only:

- `spread = max(candidate_spread, 0.05)`
- `atr = max(atr60, spread)`
- favorable barrier = `max(0.35, 1.25*spread, 0.30*atr)`
- adverse barrier = `max(0.30, 1.00*spread, 0.22*atr)`

Survival label:
adverse barrier does not hit before the specialist Hold checkpoint.

First-passage win:
favorable barrier hits before adverse barrier within specialist horizon.

Research resolved value:
opposite executable quote at first favorable/adverse resolution, or last quote at horizon, minus $0.02.

These definitions are research labels, not the final Hold→Exit production policy.

## 5. Session candidate definitions

The session layer adds reconstructible proposals around:

### ORB_ACCEPT
- active local session;
- 15–120 minutes after local open;
- first-15-minute ORB completed;
- close/mid accepts above ORB high or below ORB low;
- prior open is on/inside the break boundary;
- body and r15 align with direction;
- horizon 300s;
- Hold checkpoint 30s.

### SWEEP_RECLAIM
- active local session;
- at least 15 minutes after open;
- boundary = max/min of session ORB and previous session range;
- wick/excursion crosses boundary;
- completed midpoint returns through the boundary;
- body confirms rejection;
- horizon 120s;
- checkpoint 15s.

### FAILED_BREAK
- active local session;
- 15–180 minutes after open;
- previous completed state outside ORB boundary;
- current completed state recrosses inside;
- body confirms failure;
- horizon 120s;
- checkpoint 15s.

### COMPRESSION_RELEASE
- pre-open 30-minute range exists;
- session is within first 90 local minutes;
- pre-open range < 0.75 × atr300;
- completed 5s range > 1.8 × rolling 5s range median;
- tick_z > 0.25;
- body determines direction;
- horizon 120s;
- checkpoint 15s.

### SVWAP_RECLAIM
- active session and at least 15 minutes after open;
- session quote-activity-weighted value exists;
- completed state crosses from one side of session value to the other;
- r15 confirms direction;
- horizon 120s;
- checkpoint 15s.

These session archetypes feed the six session-specific learned model pairs and then map into the allowed checkpoint specialists. Do not interpret the archetype names as standalone production strategies.

## 6. Learned-model parity is a hard gate

Current Python checkpoint uses LightGBM classifiers.

The exact model classes, feature orders, parameters and current artifact hashes are recorded in:
`research/artifacts/BETA_064_MAJOR_CHECKPOINT_02_MODEL_MANIFEST.json`

Exact frozen model artifacts are durably archived in the project Google Drive research folder. Verify the bundle SHA-256 before use.

MT5 production may proceed only by one of these verified routes:

1. exact deterministic translation of every frozen tree to MQL5 and parity check against Python probabilities; or
2. a separately owner-approved inference bridge with deterministic versioned model files.

Do not:
- retrain with new seeds;
- change LightGBM version and assume probabilities are equivalent;
- reorder features;
- omit one-hot specialist/archetype columns;
- normalize features differently;
- replace the model with hand-written thresholds;
- approximate the models and still call the result Major Checkpoint 02.

Before any official .mq5 build, generate a probability-parity corpus and require MQL5 vs Python agreement within an explicitly frozen tolerance.

## 7. Mandatory parity tests before Hold→Exit work

### State parity
For sampled ticks across all seven months:
- each feature must match Python at the same causal timestamp.

### Candidate parity
For each specialist:
- timestamp;
- side;
- raw score;
- horizon;
- Hold checkpoint;
- session authority
must match.

### Model parity
For each proposal:
- P_survive;
- P_first_passage;
- entry_score;
- session model outputs
must match the frozen Python checkpoint.

### Ownership parity
Chronological selected Entry trades must match the frozen Python sequence for the same input tick stream, subject only to explicitly documented broker/MT5 execution differences.

### Thesis packet parity
Every selected trade must log the same origin and causal state.

### Hold-state parity
At fixed post-fill ages, the Hold features/state labels must match Python.

No Hold→Exit coding should begin before these parity layers are proven.

## 8. Anti-Alpha/GAMMA safeguards

A future implementation is invalid if it:
- starts from an older R9/GAMMA EA and merely grafts a few filters onto it;
- treats historical Alpha/GAMMA rules as authoritative;
- substitutes a later convenience implementation for frozen Python behavior;
- silently omits a specialist because it is difficult to encode;
- silently changes session times to broker server time;
- uses forming 5s/M1/M5 bars where frozen research used completed state;
- uses a fixed UTC session table through DST;
- lets session additions steal a Checkpoint-01 slot;
- promotes an Entry+Hold parity build as a complete EA.

## 9. Known incomplete production items

These are explicit blockers, not invitations to guess:

- Hold→Exit production policy is not researched/frozen.
- Exact Entry, six-session Entry, and Hold model binaries plus deterministic LightGBM tree exports are now frozen in Google Drive bundle `BETA064_MAJOR_CHECKPOINT_02_ENTRY_HOLD_MODEL_FREEZE_BUNDLE.zip`, Drive file ID `1lDtCAJQfPlmiH-6Kneo4PyF_4FCFs3tm`, SHA-256 `b6980a4a7a0f771349837619e1c3c2eda1cd512a77fbd3e0c0ab8d6c8a1bd830`. The bundle hash must be verified before MT5 translation.
- Full BETA005 feature/cache parity remains an unresolved historical gate.
- Coinexx exact contract/tick-value/commission/slippage/stop-level parity remains to be certified.
- BETA015 funded exact-risk proof remains mandatory before any investor-facing claim.
- August is still sealed.

If any of these gaps are encountered during coding, stop and resolve the gap. Do not infer a replacement.

## 10. MT5 build sequence when owner authorizes coding

1. create a new BETA Checkpoint-02 MT5 branch from an explicitly chosen clean baseline;
2. implement TickChronologyEngine + logging only;
3. certify 5s/multi-scale feature parity;
4. implement session engine and certify local-time/DST parity;
5. implement E1–E12 proposal generation and certify candidate parity;
6. translate/load frozen Entry models and certify probability parity;
7. implement base router + ownership;
8. implement session gap-fill router;
9. implement thesis packet and Hold-state logging;
10. implement frozen Hold continuation model and certify parity;
11. run MT5 Strategy Tester real-tick parity against Python Entry→Hold selections;
12. only after parity is accepted, resume Hold→Exit research;
13. do not promote to live/demo final EA until Hold→Exit is separately frozen and certified.

This production sequence is mandatory unless the owner explicitly supersedes it.
