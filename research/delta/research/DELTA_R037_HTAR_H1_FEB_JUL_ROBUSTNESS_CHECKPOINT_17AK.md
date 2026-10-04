# DELTA R037 — HTAR H1 February–July Robustness — Checkpoint 17AK

**Status:** COMPLETE / ROBUSTNESS FAIL / FAMILY RETIRED WITHOUT RETUNING  
**Candidate:** R037-HTAR-C01_H1_ANCHOR  
**Parent:** R037_HTAR_H1_LATER_JAN_CHECKPOINT_17AJ  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Question

Does the frozen H1 structural-liquidity anchor that passed both January Stage-A and the independent later-January holdout remain robust month-by-month from February through July 2026?

No candidate parameter was changed.

## Integrity

Preregistration commit: `4731471b6fa4697552c28bbc3c8adaaff250a909`

Producer:
`research/delta/experiments/delta_r037_htar_h1_monthly_17ak.py`

Producer commit:
`a07834f819907cbf1bdd1f8439fede1479f9c631`

Producer blob:
`3577223d7be4b0ee6282fff34a17dfb366741e56`

The local executable copy was Git-blob verified against that committed producer before official compute. Each month ran under its own 120-second hard timeout and wrote through atomic temporary-file + fsync + os.replace semantics.

## Frozen candidate

- H1 confirmed swing anchor, width 1
- S5 wick sweep + close back inside
- S5 CISD through sweep-bar open
- reversal FVG within 2 bars
- FVG-mid retrace/rejection within 6 bars
- P75 first executable tick
- 25-point spread ceiling
- 300 raw stop
- 100 raw trail activation / 30 raw trail distance
- 30-second maximum hold

Every month used the final seven UTC calendar days of the immediately preceding canonical month as causal warm-up. Only current-month entries counted economically.

## Month-by-month result

| Month | Trades | Wins | Net |
|---|---:|---:|---:|
| Feb | 13 | 8 | -$1.22 |
| Mar | 8 | 4 | -$1.17 |
| Apr | 13 | 4 | -$4.51 |
| May | 7 | 4 | -$0.99 |
| Jun | 9 | 5 | -$0.16 |
| Jul | 15 | 4 | -$5.31 |

Aggregate:
- **65 trades**
- **29 official wins**
- gross profit **+$9.56**
- gross loss **-$22.92**
- direct net **-$13.36**
- nonnegative months: **0 / 6**

## Preregistered robustness gate

- total trades >= 24: **PASS**
- nonnegative months >= 4: **FAIL**
- aggregate direct net >= $0: **FAIL**

Robustness result: **FAIL**.

## Interpretation

The January H1 effect was real enough to reproduce across two non-overlapping January windows, but it did not persist across later months. The failure is not a supply problem: 65 trades comfortably clears the activity gate. It is an economic generalization failure.

Because every February–July month is negative, this is not a reasonable candidate for threshold rescue. The family is retired unchanged.

This negative result is useful: simply moving a sweep/CISD/FVG/retrace construction from dense S5-local liquidity to H1 structural liquidity is not sufficient for a durable XAUUSD edge under the frozen 30-second lifecycle.

## Decision

**RETIRE R037-HTAR-C01_H1_ANCHOR WITHOUT RETUNING.**

Do not:
- tune H1 swing width;
- fit CISD/FVG/retrace windows;
- add month/session/side filters;
- alter stop/trail/hold logic;
- access August;
- begin MQL5.

## Next bounded unit

`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

The next source must change the causal information source rather than rescue HTAR numerically.
