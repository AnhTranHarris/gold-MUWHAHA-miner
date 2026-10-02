# DELTA R020 — Exact R019-C04 Jan–Jul P75 Validation

**Status:** PREREGISTERED / MONTHLY REPLAY NOT STARTED  
**Parent:** R019-C04  
**Scope:** ENTRY + INITIAL-HOLD / DIRECTION OWNERSHIP  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Exact frozen C04

Base owner trigger:
`micro250 <= -0.55 OR H1NetATR > 0.35`

Extreme DUAL:
`H1NetATR > 0.70 AND micro250 <= -0.90` -> SKIP current M1.

MICRO_ONLY / H1_ONLY:
FLIP intended R9 side, own trade, suppress generic same-minute rearm.

Non-extreme DUAL contextual KEEP:
`abs(H4NetATR) > 1.0 OR M30NetATR < -1.0`

Selected action:
KEEP original R9 side, remain owned, suppress generic same-minute rearm.

Other non-extreme DUAL:
FLIP owned/no-rearm.

No-trigger:
ordinary R9 behavior.

## Monthly contract

- January: cold start, full calendar month.
- February–July: 90-minute prior-month warmup for state only.
- P75 default modeled surface.
- Replay R9, T06, and C04 together in every month.
- One crash-safe month per job.
- no threshold/action/selector changes after results.
- August sealed.

Execution script frozen before first R020 result:

`r020_c04_month_validate.py`

SHA-256:
`d65250576063abfb6cea52dc35b1b25d284d78570c1a3bcaf0d38f62461c72b3`

Drive:
https://docs.google.com/document/d/1MsbSh1qX5CrzRgDfBi-77UtGXSYoygk2JwyEVSK8ugo/edit

Workbook:
- 34 R020 Prereg
- 35 R020 Monthly Results
