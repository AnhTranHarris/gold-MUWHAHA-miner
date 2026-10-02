# DELTA R031 — Durable Quality-Topup Preregistration

**Status:** PREREGISTERED / NOT EXECUTED  
**Parent:** R025 + GLOBAL NO_REARM + independent first-entry specialists  
**Script SHA-256:** `6a896836ffee956dba6b02480755874a631ceaf8ba108e176f277c9ed1f5c7b9`

## Frozen configurations
- R031-C00: DH03-S06 + DH05-S06
- R031-C01: C00 + DH02-S11
- R031-C02: C00 + DH02-S08
- R031-C03: C00 + DH02-S11 + DH02-S08
- R031-C04: C00 + DH02-A01

## Exact replay
Modeled surfaces: P50, P75, P90.
Stage-A window remains Jan 1 00:00 UTC through Jan 18 12:00 UTC exclusive.
No post-exit signal is permitted; all specialist events are generated independently from market state.

## Advancement gates
Each modeled surface must simultaneously satisfy:
- trade retention vs surface R9 >=80%;
- winner retention >=80%;
- net better than ordinary opposite-rearm control;
- gross-loss and drawdown deterioration vs control <5%.

A configuration survives only if all three modeled surfaces pass.
Among survivors use worst-surface net delta first, then loss/DD, then activity.
No new R031 configuration may be invented after results.

Workbook: tab `58 R031 Prereg`.
