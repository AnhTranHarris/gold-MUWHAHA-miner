# DELTA R025 — Exact M30 KEEP-Owned Jan–Jul P75 Validation

**Status:** PREREGISTERED / NOT EXECUTED  
**Parent:** R024 M30_KEEP_OWNED sole modeled-surface survivor  
**Surface:** DELTA_004 P75  
**Months:** January–July 2026  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Frozen event and action

P01 condition:

`H1NetATR > 0.35 OR micro250 impulse <= -0.55`

M30-only condition:

`M30NetATR > 0.35 AND NOT(P01 condition)`

R024 survivor action on the M30-only branch:

**KEEP intended R9 side + assign ownership + suppress generic same-minute rearm.**

Everything else remains exact P01.

## Monthly execution contract

- January: cold start.
- February–July: prepend 90 minutes of prior-month ticks for state only.
- Score only the target calendar month.
- Each month is an atomic compute/checkpoint unit.
- No August.
- No threshold retuning or action invention.

Configs:
- R9
- P01_CONTROL
- M30_KEEP_OWNED

Metrics include trades, wins, gross profit/loss, net, drawdown, hold time, activity/winner retention vs R9, and incremental improvement vs P01.

## Execution source

`r025_m30_keep_month_validate.py`

SHA-256:

`5f60ab95ffb91609b12a1a43f1004d65b21350f18fcc9c6856912e44637cf885`

## Drive artifacts

Doc:
https://docs.google.com/document/d/1--WukgAAozEO1HYgwr2LqDhqVw5JR7DNyBrgRn0hZUw/edit

Workbook tabs:
- `45 R025 Prereg`
- `46 R025 Monthly Results`

## Gate

R025 supplies exact month-by-month validation evidence only. It does not promote a candidate or create metric locks by itself.
