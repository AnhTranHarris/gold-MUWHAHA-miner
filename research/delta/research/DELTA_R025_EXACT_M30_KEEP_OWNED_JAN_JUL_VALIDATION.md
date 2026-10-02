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

## Completion result

The exact frozen `M30_KEEP_OWNED` rule improved `P01_CONTROL` in **all seven months** January–July 2026.

Monthly incremental net versus P01:

- Jan: +$225.51
- Feb: +$217.54
- Mar: +$308.95
- Apr: +$208.56
- May: +$270.64
- Jun: +$197.44
- Jul: +$193.69

### Aggregate Jan–Jul

R9:
- trades 234,417
- wins 103,097
- gross profit +$29,243.07
- gross loss -$78,244.86
- net -$49,001.79

P01_CONTROL:
- trades 203,864
- wins 90,751
- gross profit +$25,008.31
- gross loss -$67,676.50
- net -$42,668.19

M30_KEEP_OWNED:
- trades 195,990
- wins 87,214
- gross profit +$24,030.52
- gross loss -$65,076.38
- net -$41,045.86
- M30-only owned events 25,961
- suppressed rearm count 112,657

Incremental versus P01:
- net +$1,622.33
- net-loss reduction 3.8022%
- gross-loss reduction 3.8420%

Versus R9:
- trade retention 83.6074%
- winner retention 84.5941%
- net-loss reduction 16.2360%
- gross-loss reduction 16.8298%

## Decision

R025 validates M30 KEEP-owned as a robust ownership component.

It is not a promoted full DELTA candidate and creates no primary metric lock.

The next leverage question is whether some of the activity lost by suppressing generic same-minute rearm can be causally recovered without surrendering the validated loss reduction. The next unit must therefore harvest the suppressed rearm descendants before testing any release-policy modification.

## Monthly result hashes

- Jan `db492af3e16986a8ffaea35d31ecdceebb25ed27622776c57e510b1949b3655c`
- Feb `c28faa381eb0ca45383ff8404d0b70e0cdc841dfdcd9784a4318114294734e07`
- Mar `6b4778e2000adfebd06eb18b0145d3aaab6919161c3021ae8c6796ea50221163`
- Apr `4ec31343d20f279cb04869a6a0e99183efc2f8b6377d1c4e4be09ec8ca10124c`
- May `52a0a7cd93b20dfe786e7c748beccd912f444ee86d60a5c52a6e20fe93c968d8`
- Jun `270c21776c58974d978a20106f62e31ec43076af31c92d18161a22648caeb4fe`
- Jul `e534dabaf4b82e5f952700485bedb754c9b3a717f6d3afa8d81d13fa050d1c83`

