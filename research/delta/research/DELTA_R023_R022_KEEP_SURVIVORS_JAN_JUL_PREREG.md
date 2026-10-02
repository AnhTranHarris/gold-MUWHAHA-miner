# DELTA R023 — Exact R022 KEEP Survivors Jan–Jul P75 Validation

**Status:** PREREGISTERED / MONTHLY REPLAY NOT YET STARTED  
**Parent:** R022-B-KEEP and R022-C-KEEP / R016-T06  
**Scope:** ENTRY + INITIAL-HOLD / DUAL OWNERSHIP  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Accounting-QC accepted R022 survivors

R022 execution behavior was unchanged, but winner/GP/GL classification was normalized to the canonical post-exit-commission convention before accepting survivors.

Accounting-QC script SHA-256:

`93ebf8d83bcc168425ca11f02a6283c13373581a60c3b569dd27404e34922759`

Accepted R022 result hashes:
- P50 `c7e72a5420596896a1e7b47b3cc5c9fd4dc2703da6055eb298d757da0d5d463a`
- P75 `e17483569b6b8bab1d3beaab8f86ba23a7841cee31543057311848e263dd3ea2`
- P90 `af1b3f14cfc6e0152a81aee2f6646b72fc7fc153480e71b5ec418503ba6b5466`
- Native `514af4f01b301953948ef00e971ef52ca148c879a0387672ee5cacffa9d13855`

Only R022-B-KEEP and R022-C-KEEP pass every P50/P75/P90 preregistered gate.

## R022-B-KEEP

On non-extreme DUAL events only:

`abs(S15NetATR) > 1.75 AND abs(M30NetATR) > 1.30`

Action:
KEEP original R9 intended side, owned, generic same-minute rearm suppressed.

## R022-C-KEEP

On non-extreme DUAL events only:

`M30NetATR <= -0.35 AND H1NetATR > 0.75`

Action:
KEEP original R9 intended side, owned, generic same-minute rearm suppressed.

## Monthly validation contract

- January: cold start.
- February–July: 90-minute prior-month state warmup only.
- Scoring begins exactly at calendar month start.
- P75 only.
- One month per crash-safe job.
- R9 and T06 are replayed in every month as exact controls.
- No rule merging.
- No threshold/action change after observing monthly results.
- August remains sealed.

## Advancement

A survivor must:
- retain >=80% aggregate R9 trades;
- retain >=80% aggregate R9 winners;
- improve T06 aggregate net loss;
- avoid >5% aggregate gross-loss or drawdown deterioration versus T06.

Monthly sign consistency is recorded. Aggregate improvement with unstable monthly behavior remains research-only.

## Execution source

`r023_keep_survivors_month_validate.py`

SHA-256:

`f7ed37f205997f8505d43359d622f6a44b26e6f952d28c10cd9cff393ed4273d`

## Drive

Prereg doc:

https://docs.google.com/document/d/1XaYp0QQrQ952My5DUxOW4VrMMln8ojGOZsz24mEdsqU/edit

Workbook tabs:
- `41 R023 Prereg`
- `42 R023 Monthly Results`

## Current gate

- monthly replay: NOT STARTED
- promoted candidate: NONE
- metric locks: NONE
- August: SEALED
- MQL5: NOT AUTHORIZED
