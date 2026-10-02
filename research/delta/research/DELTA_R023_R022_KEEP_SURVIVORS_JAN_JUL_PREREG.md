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

## Validation result

All seven P75 monthly jobs completed under the frozen R023 rules.

Aggregate controls:
- R9: 234,417 trades; 103,097 winners; gross loss -$78,244.86; net -$49,001.79.
- T06: 198,029 trades; 87,978 winners; gross loss -$65,816.57; net -$41,531.29; trade retention 84.4772%; winner retention 85.3352%.

R022-B-KEEP:
- 198,029 trades
- 87,991 winners
- gross loss -$65,804.40
- net -$41,510.24
- 171 subset hits
- +$21.05 versus T06
- +0.0507% incremental net-loss closure versus T06
- +0.0185% incremental gross-loss improvement versus T06
- 84.4772% trade retention
- 85.3478% winner retention
- positive versus T06 in all 7/7 months
- worst monthly net delta +$1.47

R022-C-KEEP:
- 198,028 trades
- 87,998 winners
- gross loss -$65,801.75
- net -$41,510.85
- 101 subset hits
- +$20.44 versus T06
- +0.0492% incremental net-loss closure versus T06
- +0.0225% incremental gross-loss improvement versus T06
- 84.4768% trade retention
- 85.3546% winner retention
- positive versus T06 in all 7/7 months
- worst monthly net delta +$0.47

Monthly B-KEEP net deltas versus T06:
Jan +$2.19; Feb +$4.23; Mar +$3.29; Apr +$6.58; May +$1.66; Jun +$1.47; Jul +$1.63.

Monthly C-KEEP net deltas versus T06:
Jan +$1.02; Feb +$0.47; Mar +$2.42; Apr +$3.95; May +$8.63; Jun +$2.14; Jul +$1.81.

## Decision

Both B-KEEP and C-KEEP are validated robust causal micro-edges and are retained as ownership components / future integration candidates.

Neither is promoted as a standalone DELTA candidate because the incremental effect is too small for a new primary metric lock or a GOV-007 breakthrough.

No thresholds were retuned and no B+C merge was inferred inside R023.

## Result provenance

- month 1: `0aff91a0930c71fd19c0df35a61a141f79d2ee6fcf583828a6859b5c6dc685b7`
- month 2: `f7dd5687c67731c883d092dfd36464be8f401d4b75d5e2cf4d5f25b39150e984`
- month 3: `e62e61723f4eb9674bd7a77191d1bf04f4ac0a5278b6193125b6354d1866a93d`
- month 4: `d72eba1f09b886e8678096b34843bb995f28100f8f966589976bda05f67e61ff`
- month 5: `10dd5974a91fdba3a7eadf2b0f002966dd03f27b97b03c934cb7d126a0e086f8`
- month 6: `740c358a75dc5366f87da459d947e42bda5a30a064deabfed7bbd0f920607e2b`
- month 7: `4f76466d935496b98c44712611da7f0be7ef93e9fa35954d8e8f3d53a5bd473e`

## Updated gate

- R023 monthly validation: COMPLETE
- promoted candidate: NONE
- metric locks: NONE
- validated micro-components: R022-B-KEEP, R022-C-KEEP
- next: creative escalation to higher-capacity ownership branch research
- August: SEALED
- MQL5: NOT AUTHORIZED
