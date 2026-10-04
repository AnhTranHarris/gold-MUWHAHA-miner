# DELTA R037 — SORB Surrogate-Parent Stage-A Screen — Checkpoint 15A

**Status:** COMPLETE / STRONG SURROGATE SCREEN PASS / NON-PROMOTING  
**Unit:** R037_SORB_SURROGATE_PARENT_STAGE_A_SCREEN  
**Parent:** R037_R032_SPECIALIST_PARENT_PROVENANCE_SORB_READINESS_CHECKPOINT_14B  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Why this unit ran

Checkpoint 14B blocked the exact-parent SORB lane because exact historical R032-C03 specialist ownership parity remains provenance-limited, but explicitly authorized one non-promoting SORB screen on the frozen 14A surrogate parent.

The five SORB configurations were frozen before compute. No numeric retuning occurred.

## Timeout-safe recovery

The active chat experienced repeated message-delivery timeouts. Live durable state showed that the science had already progressed through 14B. The only current inconsistency found was a stale in-flight pointer referencing the pre-hotfix SORB producer. The corrected producer was already committed at:

- producer commit: `d1c5a36f502bf2ec59ce81388472963a4d4a71c1`
- producer blob: `4dd2209c161d555cb814e3875553219373ad1f9b`
- producer SHA-256: `0e0db32717636e54a160fbca34dac4a112712fb401b1f011f66e60361c2306b5`

The recovery cursor was reconciled before official compute. A delivery timeout is therefore treated as transport failure, not proof that compute failed.

## Hard pre-compute gates

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**

All four frozen specialist signal fingerprints reproduced exactly:
- DH03-S06: **1,586**
- DH05-S06: **651**
- DH02-S11: **103**
- DH02-S08: **104**

The 14A surrogate parent control also reproduced exactly:
- trades **14,034**
- raw-positive wins **6,422**
- official wins **6,349**
- ordinary entries **11,916**
- parent-specialist entries **2,118**
- gross profit **+$1,357.26**
- gross loss **-$4,302.20**
- net **-$2,944.94**
- max balance DD **$2,945.93**
- max equity DD **$2,946.43**

## Breakthrough

The leading frozen configuration is **R037-C04_DUAL_30**.

Against the exact surrogate-parent control it produced:
- SORB proposals: **22**
- source-eligible proposals: **21**
- distinct days: **11**
- accepted SORB entries: **17**
- total trade delta: **+17**
- official-win delta: **+12**
- gross-profit delta: **+$4.54**
- gross-loss delta: **-$3.02**
- combined net delta: **+$1.52**
- max balance DD delta: **-0.0516%**
- max equity DD delta: **-0.0516%**

The SORB entries themselves contributed **+$0.84**, with:
- London: 7 entries / 5 official wins / **+$0.14**
- COMEX Gold: 10 entries / 6 official wins / **+$0.70**

C04 passes every ordinary screen rule and the strong-screen rule requiring nonnegative incremental net.

## Other frozen configurations

- C01 LONDON_15: ordinary screen PASS, strong FAIL, net delta **-$0.50**
- C02 COMEX_15: ordinary screen PASS, strong FAIL, net delta **-$1.52**
- C03 DUAL_15: FAIL, net delta **-$2.02**
- C05 DUAL_15_CONFIRM2: FAIL, net delta **-$2.31**

The 30-minute dual-session opening range is therefore the only frozen SORB candidate that both improves net outcome and avoids drawdown deterioration on Stage-A.

## Scientific interpretation

This is a **candidate breakthrough**, not a DELTA promotion.

The result suggests that the longer 30-minute opening range is filtering enough early-session noise to improve the parent interaction surface. Both London and COMEX contribute positively in the winning configuration, which is preferable to a one-session artifact.

However:
- the parent is still the provenance-limited 14A surrogate;
- this is one Stage-A surface;
- no independent validation has yet been performed;
- no exact historical R032-C03 claim is made;
- no final DELTA candidate is promoted.

## Decision

**Checkpoint 15A = STRONG SCREEN PASS / CARRY C04 ONLY.**

Freeze:
`R037-C04_DUAL_30`

Retire from immediate validation:
C01, C02, C03, C05.

Official local raw result SHA-256:
`7a9033a544cd7b6969b842bd84c868d4fcd63ed063129821c69255f05f1ebcf8`

Committed result:
`research/delta/reference/DELTA_R037_SORB_SURROGATE_PARENT_STAGE_A_SCREEN_CHECKPOINT_15A.json`

## Next bounded unit

`R037_SORB_C04_DUAL30_INDEPENDENT_VALIDATION`

Validate the frozen C04 semantics independently without retuning before any promotion discussion.
