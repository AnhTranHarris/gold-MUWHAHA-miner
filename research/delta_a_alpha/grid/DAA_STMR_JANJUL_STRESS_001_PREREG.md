# Delta-A-alpha — STMR Jan–Jul Session/Timeframe Stress 001 — Preregistration

**Status:** IN PROGRESS — owner authorized 2026-10-06  
**Parent scientific floor:** `STMR_SLEEVE_PHASE_001`  
**Parent authority:** journal 0024; journal 0025 is administrative handoff only.

## Objective

Stress the accepted session/timeframe layer across January through July 2026 before any new whole-system dimension is added. Fine-tuning in this campaign is limited to session and timeframe mechanics.

## Frozen constraints

- XAUUSD only.
- Fixed 0.01 lot.
- No Martingale or loss-dependent sizing.
- Maximum grid-owned positions remains 3 unless explicitly tested as a diagnostic and not promoted.
- Ordered Bid/Ask tick execution.
- Completed-bar-only H4/H1/M15/M5 state.
- No future-bar visibility or retrospective scheduling.
- Main `delta` remains read-only.
- August 2026 remains sealed and must not be inspected.
- No MQL5 implementation.
- No volatility/regime, market-structure, trend-phase, news/event, execution-friction, risk-admission, or specialist-routing layer is introduced in this campaign.

## Parent control

`STMR_SLEEVE_PHASE_001` authoritative January result:
- net +$877.78
- trades 1,518
- PF 1.602933
- expected payoff +$0.578248
- max equity DD $61.22
- forced final liquidations 0

The parent result is not replaced by a reconstruction until parity is proven or explicitly reconciled.

## Recovery state after message timeout

The runtime preserved the incomplete clean-room parity reconstruction. A recovery bundle was created and persisted to the user's Library:
`/xauusd-trading-bot/delta-A-alpha/recovery/2026-10-06/STMR_JANJUL_TIMEOUT_RECOVERY_20261006.zip`

Bundle SHA-256:
`55606ab92d81f7409133c7b2193d5a8fa7f352c73d212be4843e18c383d83897`

Latest completed diagnostic before this checkpoint:
- `stmr_fullsim.py` bounded January diagnostic completed.
- closest tested configuration: fixed UTC + shared physical single-cell genealogy + targeted subphase gates.
- result: 1,507 trades / +$791.37 net.
- authoritative control: 1,518 trades / +$877.78.
- exact January parity: **NOT YET ACHIEVED**.

A broad parity-search job exceeded the bounded execution timeout and produced no completed result. It is not evidence.

## Raw-source hashes verified

January:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

February:
`ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`

March:
`814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177`

April:
`30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f`

May:
`3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d`

June:
`34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2`

July:
`e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7`

## Atomic sequence

1. Recover exact January replay parity from durable semantics and retained timeout artifacts.
2. Persist the parity-capable helper and parity result.
3. Run frozen parent month-by-month Jan–Jul with no tuning.
4. Diagnose session/timeframe instability, including DST translation.
5. Preregister a bounded set of session/timeframe-only mutations.
6. Evaluate mutations month-by-month and on cumulative Jan–Jul.
7. Promote only a child that materially improves robustness/economics without silent calendar fitting.
8. Persist accepted and meaningful rejected results before any new whole-system dimension.

