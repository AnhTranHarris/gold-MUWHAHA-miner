# R9 GAMMA-01 — STMR XMonth Grid Integration

**Status:** IMPLEMENTED — MetaEditor compile and Coinexx certification pending  
**Branch:** `carson/r9-gamma-01-stmr-xmonth-grid`  
**EA:** `Experts/GoldMuwahahaMiner_R9_GAMMA_01_STMRGrid.mq5`

## 1. Lineage

This build is based on the actual R9 GAMMA baseline:

- parent branch: `carson/r9-gamma-00-baseline`
- parent commit: `5883b014f93ddf4c6ec2d2f6f28916fb9f175fbb`
- parent EA: `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`
- parent EA Git blob: `7eecb5f1947017a01ce85b2520725de54749e523`

The behavior-bearing R9 functions are preserved byte-for-byte and checked in CI.

A previously-created standalone branch,
`r9-stmr-xmonth-subphase-001-mt5-cert-20261006`, is **not** the Gamma build. It has no common ancestor with the Gamma baseline and is retained only as forensic implementation reference.

## 2. What was integrated

The EA contains two independently switchable engines.

### R9 core

The existing HybridGate engine remains intact:

- R5-style minute bracket;
- causal S1 velocity / efficiency / range gate;
- M5 ATR regime gate;
- existing session-adaptive ATR minimums;
- 0.01 default lot;
- 30-pip stop;
- 3-pip trailing gap;
- 10-pip trailing activation;
- 30-second maximum hold;
- same-minute opposite rearm behavior;
- core magic `5559`.

### STMR grid sidecar

The clean-room Jan-Jul child `STMR_XMONTH_SUBPHASE_001` is added as an independent hedge-mode sleeve:

- fixed 0.01 lot;
- grid magic `5593001`;
- maximum 3 grid-owned positions;
- fixed UTC session segmentation;
- completed custom H4/H1/M15/M5 bars;
- EMA(8/21) state per timeframe;
- H4 environment -> H1 structure -> M15 phase -> M5 transfer semantics;
- session-local lattice reset;
- sleeve-local first-touch genealogy;
- one landing-cell event per ordered tick;
- no timer rearm;
- fixed sleeve-specific TP/SL;
- hard 300-second age exit;
- no Martingale;
- no loss-dependent sizing.

The grid uses its own `CTrade gridTrade`. It cannot read the R9 core `CTrade trade` result code or core magic number.

## 3. A/B controls

The build deliberately supports three modes without requiring another source edit:

### Exact R9 regression

```
InpCoreEnabled = true
InpGridEnabled = false
```

This is the first certification gate. It must reproduce the Gamma parent R9 behavior in the same Strategy Tester environment.

### Grid-only Python-to-Coinexx certification

```
InpCoreEnabled = false
InpGridEnabled = true
```

This isolates STMR from the R9 core so broker-native divergence can be measured cleanly.

### Cumulative Gamma build

```
InpCoreEnabled = true
InpGridEnabled = true
```

This is the default and the actual cumulative R9 GAMMA-01 candidate.

The deterministic tick call order is:

1. R9 core;
2. STMR grid.

The engines are isolated by magic number on a hedging account.

## 4. Frozen STMR session/timeframe mechanics

### Fixed UTC sessions

| Code | Session | UTC | Gap |
|---:|---|---|---:|
| 0 | Asia | 23:00-07:00 | $0.75 |
| 1 | London Open | 07:00-09:00 | observe-only |
| 2 | London | 09:00-13:30 | $1.00 |
| 3 | Overlap | 13:30-16:00 | $0.75 |
| 4 | New York | 16:00-20:00 | $1.50 |
| 5 | Late New York | 20:00-22:00 | $0.50 |
| 6 | Rollover | 22:00-23:00 | observe-only |

### Funded sleeves

| Sleeve | Allowed subphase | TP | SL |
|---|---|---:|---:|
| ASIA_LOWER_TAKEOVER | 23:00-00:00 | $4.00 | $1.00 |
| LONDON_M5_TAKEOVER | 11:00-12:00 | $4.00 | $0.75 |
| OVERLAP_LOWER_TAKEOVER | 15:00-16:00 | $4.00 | $1.50 |
| LATE_ALIGNED_MOMENTUM | 20:00-22:00 | $4.00 | $1.50 |
| LATE_MACRO_SPLIT_TRANSFER | 20:00-22:00 | $4.00 | $1.50 |
| LATE_LOWER_TAKEOVER | 21:00-22:00 | $2.50 | $1.25 |

The remaining six semantic sleeves are classified but observe-only.

## 5. Python comparator

The clean-room Jan-Jul research child produced:

- net: **+$829.71**
- gross profit: **+$3,625.77**
- gross loss: **-$2,796.06**
- PF: **1.2967426**
- trades: **2,675**
- expected payoff: **+$0.31017/trade**
- maximum grid positions: **3**
- forced final liquidations: **0**

Monthly net:

`+$641.58 / +$43.95 / +$4.55 / -$34.51 / -$19.89 / +$213.13 / -$19.10`

This is a **clean-room cross-month comparator**, not the authoritative January floor. The January authority remains `STMR_SLEEVE_PHASE_001` at +$877.78 because its exact portable replay helper bytes were not recoverable.

## 6. Important warmup difference

The Python Jan-Jul aggregate was assembled from month-scoped runs. For February-July, each month loaded the prior ten calendar days solely to seed completed-bar EMA state.

A single continuous MT5 Jan-Jul run naturally carries EMA state continuously from January. That is legitimate broker certification, but it is not a bit-identical state initialization to the month-scoped Python aggregate.

Therefore certification has two distinct jobs:

1. **month-by-month parity runs** for closest Python state initialization;
2. **continuous Jan-Jul runs** for the realistic cumulative EA behavior.

Do not tune the EA merely because those two modes differ.

## 7. Required MetaEditor compile

Compile:

`Experts/GoldMuwahahaMiner_R9_GAMMA_01_STMRGrid.mq5`

Required:

- 0 errors;
- every warning reviewed;
- do not run the economic test if a warning implies type conversion, array bounds, trade overload ambiguity, or unreachable logic.

The current environment cannot run MetaEditor, so GitHub CI is static integration QA, not a compiler substitute.

## 8. Coinexx test sequence

Use the same Coinexx-Demo environment as the historical R9 report whenever possible.

### Test A — R9 core regression

- mode: **Every tick based on real ticks**
- XAUUSD / M1 host chart
- 2026-01-01 through 2026-07-31
- initial deposit: $100,000
- leverage: 1:500
- `InpCoreEnabled=true`
- `InpGridEnabled=false`
- all R9 inputs at their existing defaults

Historical orientation:
- R9 REAL: -$50,285.28
- 236,647 trades
- PF 0.37507

A meaningful unexplained regression here blocks all later conclusions.

### Test B — grid-only month parity

For each month, set `InpCoreEnabled=false`, `InpGridEnabled=true`.

| Target month | Tester From | Grid Entry Start | Grid Entry End |
|---|---|---|---|
| Jan | 2026-01-01 | 2026-01-05 00:00 | 2026-02-01 00:00 |
| Feb | 2026-01-22 | 2026-02-01 00:00 | 2026-03-01 00:00 |
| Mar | 2026-02-19 | 2026-03-01 00:00 | 2026-04-01 00:00 |
| Apr | 2026-03-22 | 2026-04-01 00:00 | 2026-05-01 00:00 |
| May | 2026-04-21 | 2026-05-01 00:00 | 2026-06-01 00:00 |
| Jun | 2026-05-22 | 2026-06-01 00:00 | 2026-07-01 00:00 |
| Jul | 2026-06-21 | 2026-07-01 00:00 | 2026-08-01 00:00 |

For each run set `InpGridWarmupStartUtc` equal to Tester From.

Primary comparison is trade count, sleeve/hour distribution, PF, and direction of monthly net—not exact dollars.

### Test C — grid-only continuous Jan-Jul

- `InpCoreEnabled=false`
- `InpGridEnabled=true`
- warmup 2026-01-01
- entry start 2026-01-05
- entry end 2026-08-01
- Every tick based on real ticks

This measures the continuous-state Coinexx form of the grid.

### Test D — cumulative Gamma real ticks

- `InpCoreEnabled=true`
- `InpGridEnabled=true`
- same Jan-Jul dates
- Every tick based on real ticks

This is the key cumulative result.

### Test E — cumulative Gamma synthetic orientation

Repeat Test D with **Every tick**.

This is not a substitute for REAL certification. It tells us whether the integrated build retains the historical REAL/SYNTH asymmetry and whether the grid adds value to one or both surfaces.

## 9. Decision logger

When grid diagnostics are enabled, the EA writes:

`GoldMuwahaha_R9_GAMMA01_STMR_TESTER_<timestamp>.csv`

to MT5 `Common\Files`.

Fields include:

- server and UTC millisecond time;
- session;
- H4/H1/M15/M5 states;
- sleeve;
- expected and actual crossing direction;
- lattice cell/key;
- anchor;
- Bid/Ask;
- seen-before flag;
- subphase gate;
- grid position count;
- final action.

If MT5 and Python diverge, investigate in this order:

1. quote-time-to-UTC mapping;
2. completed timeframe states;
3. session reset/anchor;
4. first-touch cell genealogy;
5. sleeve/subphase admission;
6. broker fill / commission / stops / slippage.

Do **not** start by changing TP/SL.

## 10. Future-edit map inside the EA

Search these tags:

- `[CORE-00]` — original R9 logic;
- `[GRID-01]` — fixed session clock/test envelope;
- `[GRID-02]` — completed timeframe state;
- `[GRID-03]` — lattice/genealogy;
- `[GRID-04]` — sleeve admission;
- `[GRID-05]` — lifecycle;
- `[GRID-06]` — execution/tickets;
- `[GRID-07]` — diagnostics;
- `[INTEGRATION]` — core/grid orchestration.

Any scientific edit to GRID-02 through GRID-05 should first be reproduced in the Python ordered-tick harness.

## 11. Promotion rule

This branch is a **certification candidate**, not yet a promoted Gamma parent.

Do not merge it into `carson/r9-gamma-00-baseline` and do not branch GAMMA-02 from it until:

1. MetaEditor compiles cleanly;
2. core-only R9 regression is accepted;
3. grid-only Coinexx behavior is reconciled;
4. cumulative REAL result is reviewed;
5. cumulative SYNTH result is reviewed;
6. low-balance survivability is checked after the $100,000 research comparison.

August remains sealed.
