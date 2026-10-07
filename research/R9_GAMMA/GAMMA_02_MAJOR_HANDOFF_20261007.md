# GAMMA-02 — MAJOR HANDOFF 2026-10-07

**Purpose:** clean transfer after repeated ChatGPT delivery timeouts / imminent chat-length exhaustion.  
**Status:** IDLE ATOMIC BOUNDARY — NO WORKER RUNNING  
**Branch:** `carson/r9-gamma-02-velocity-geometry-research`  
**Latest scientific checkpoint before handoff packaging:** `820c5c215e25b55600fc7c3dc273dbdfebc9fa34`  
**Latest completed scientific unit:** `GAMMA_02_MARCH_NATIVE_BREAKTHROUGH_130`  
**First incomplete unit:** `GAMMA_02_APRIL_NATIVE_STATE_DISCOVERY_131`  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED for GAMMA-02 yet.

## Read order in a new chat

1. `research/R9_GAMMA/GAMMA_02_CURRENT_RESEARCH_CURSOR.json`
2. this handoff
3. `research/R9_GAMMA/GAMMA_02_MARCH_NATIVE_BREAKTHROUGH_130.md`
4. `research/R9_GAMMA/GAMMA_02_FEBRUARY_ROUTER_TRANSFER_QA_127.md`
5. `research/R9_GAMMA/GAMMA_02_ROUTER_122_WARMUP_LEAKAGE_QA_001.md`
6. `research/R9_GAMMA/GAMMA_02_TIMEOUT_RECOVERY_CHECKPOINT_006.md`
7. only then resume April-native discovery 131.

Do **not** rebuild or rerun completed units <=130.

## Durable handoff Drive

https://drive.google.com/drive/folders/1EOfZ7E3E4nkzgRJgw-RRONq6yo_xs-EI

This Drive folder supersedes the earlier same-day fresh-chat handoff folder for current state.

## Foundation that must remain intact

### GAMMA-01 validated MT5 foundation
The current deployable/reproducible foundation remains the ClockFix STMR grid:
- Coinexx grid-only Jan-Jul REAL: +$579.60 / 2,582 trades / PF ~1.205;
- Dukascopy clean-room comparator: +$829.71 / 2,675 / PF ~1.2967;
- branch: `carson/r9-gamma-01-stmr-clockfix`.
Do not replace this foundation with unvalidated GAMMA-02 Python discoveries.

### Hard R9 SYNTH target
Canonical January R9 SYNTH:
- +$41,520.82 net
- 27,980 trades
- PF 23.7154
- 87.09% win rate
- +$1.483946/trade
- average hold 16.4627s

Canonical Jan-Jul R9 SYNTH:
- +$309,122.85 net
- 219,342 trades

The user requires GAMMA-02 improvements to close this gap materially, not accept endless sub-1% polishing.

## Critical GAMMA-02 chronology

### January
The research found several extreme January discovery frontiers, including watchdog/renewal architectures that exceeded the January SYNTH dollar target. Those results are discovery evidence, not universal cross-month authority.

The latest frozen watchdog 119 January result:
- +$133,046.74
- 75,001 trades
- PF 29.9038
- 99.21% wins
- +$1.7739 expectancy
- ~27.23s average hold

But watchdog 119 degrades badly after March and is **not** a universal router.

### Cross-month specialist phase
Specialists 109/114/115/116 and watchdog 119 were explored. A causal meta-router 122 was attempted.

Critical QA then found that 103/104 February results were contaminated by **warmup-entry leakage**. Their prior February +$43.9K claim is invalid as cross-month authority. Preserve the artifacts, but do not reuse their contaminated February result.

The old +$225,741 / 199,547 trade oracle that depended on contaminated 103/104 is therefore invalidated pending clean recomputation.

### Clean February-native research
After explicit target-month entry gating:
- fixed-horizon native portfolio 124: +$40,163.27 / 12,543 / PF 2.3006;
- lifecycle max-net 125: +$71,149.91 / 12,543 / PF 3.143;
- strict-quality 125: +$59,294.35 / 9,985 / PF 3.672;
- PF10 conviction 126 at cap 320: +$55,807.60 / 4,319 / PF 19.53 / 88.59% wins / +$12.92 expectancy.

Frozen February PF10 rules fail January and only partially transfer to March, proving they are not a universal static router.

### Clean March-native research
March-native pipeline uses:
- target-month entries only;
- completed HTF state;
- one unique favorable M1 extension per market tick;
- exact H4/H1/M15/M5 state signature;
- state-specific lifecycle;
- causal UTC 10-minute subphase and already-realized favorable displacement routing.

March frontiers:
- fixed native: +$64,393.12 / 26,043 / PF 1.96;
- lifecycle max-net: +$113,062.92 / 24,908 / PF 2.58;
- PF5 conviction: +$80,040.77 / 9,392 / PF 9.18;
- Win80 conviction: +$68,918.02 / 7,046 / PF 14.23 / 85.14%;
- PF10 conviction: +$67,574.54 / 6,746 / PF 16.36 / 85.93% / +$10.02 expectancy.

This is the latest completed science.

## First incomplete unit — April native 131

Resume only:
`GAMMA_02_APRIL_NATIVE_STATE_DISCOVERY_131`

Use the same legal causal pipeline as February/March:
1. load April with warmup for indicators only;
2. explicitly gate **entry timestamps** to April;
3. completed H4/H1/M15/M5 state only;
4. one unique favorable M1 extension per market tick;
5. discover exact state/hour cells;
6. test executable fixed-horizon markout;
7. state-specific TP/SL/hold;
8. causal 10-minute-subphase/displacement conviction routing;
9. persist April immediately before May.

Month is a dataset partition, **not** a deployable input feature.

After April:
- May native discovery;
- June native discovery;
- July native discovery;
- only after all are durable, synthesize a causal cross-month regime router;
- August stays sealed.

## Permanent QA/invalidation rules

Do not resurrect:
1. hour-slice tail-entry artifacts from early Stage 2/3;
2. same-tick multi-level ladder fills as independent opportunity count — they are pyramiding/scaling;
3. 103/104 cross-month February authority before target-month gating rebuild;
4. the old oracle that used contaminated 103/104;
5. standalone STMR MT5 lineage that had no Gamma ancestor;
6. pre-ClockFix MT5 UTC/session mapping.

Every future monthly helper must explicitly assert:
`start <= entry_timestamp < end`.

## Durable code/data locations

### GitHub
Repository: `AnhTranHarris/gold-MUWHAHA-miner`
Branch: `carson/r9-gamma-02-velocity-geometry-research`
Key directories:
- `research/R9_GAMMA/`
- `research/R9_GAMMA/helpers/`
- `research/R9_GAMMA/artifacts/`
- `research/R9_GAMMA/replay083_deps/`

### Persistent Library
Do not rebuild these from chat:
- `/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/`
- `/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/watchdog-119/`
- `/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/post-crossover-recovery/`
- `/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/meta-router-122/`
- `/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/february-repair-123/`

The meta-router 122 folder contains all seven raw/absolute-time stream caches. Use them instead of rebuilding when relevant.

### Raw market sources
Jan-Jul Dukascopy XAUUSD tick files are available in Project sources / mounted attachments.
Canonical SHA-256:
- Jan d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5
- Feb ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d
- Mar 814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177
- Apr 30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f
- May 3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d
- Jun 34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2
- Jul e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7

August exists but remains SEALED.

## Timeout/recovery protocol

After any timeout:
1. inspect GitHub HEAD;
2. read CURRENT_RESEARCH_CURSOR;
3. inspect Library for artifacts newer than cursor;
4. check for a surviving worker;
5. completed result + helper beats chat text;
6. a timeout with no final artifact is not evidence;
7. checkpoint helper + result + summary before the next sweep.

## Handoff completion statement

At handoff creation there is no active worker and no partially accepted scientific result.
The project is intentionally stopped at:
- latest complete = March Native Breakthrough 130;
- next = April Native State Discovery 131.

No April result has been silently assumed.
