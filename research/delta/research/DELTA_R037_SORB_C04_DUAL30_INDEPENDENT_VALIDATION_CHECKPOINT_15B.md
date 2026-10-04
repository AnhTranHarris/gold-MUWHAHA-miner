# DELTA R037 — SORB C04 Dual30 Independent Validation — Checkpoint 15B

**Status:** COMPLETE — INDEPENDENT VALIDATION FAIL / C04 RETIRED  
**Unit:** R037_SORB_C04_DUAL30_INDEPENDENT_VALIDATION  
**Parent:** R037_SORB_SURROGATE_PARENT_STAGE_A_SCREEN_CHECKPOINT_15A  
**Candidate:** R037-C04_DUAL_30  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Preregistered validation

C04 was frozen exactly after the 15A strong Stage-A screen:
- London + COMEX Gold;
- 30-minute opening range;
- one completed-S5 confirmation;
- 120-minute expiry;
- first confirmation consumes the session;
- spread <= 25 points;
- frozen R9 stop/trail/max-hold lifecycle;
- no deferred blocked events;
- no SORB rearm;
- no numeric retuning.

The independent validation followed the established DELTA later-January OOS convention:

- warmup only: **2026-01-14 00:00 UTC -> 2026-01-18 12:00 UTC**;
- economic holdout: **2026-01-18 12:00 UTC -> final observed January tick**.

No economic entry was permitted during warmup.

## Crash/timeout controls

Before compute:
- preregistration was committed;
- producer was committed;
- CURRENT_INFLIGHT and the timeout-recovery pointer were advanced to 15B.

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Committed producer:
- commit `10bd1f16f3f4757b652cfe50bc90dab920f134cf`
- blob `87787466855efb1bc5a0602b195299380037e700`
- SHA-256 `560a7e2c8802ab9a14891d2f008efb0fbb9da0c6f68abee02791a708329ac8bd`

The canonical-data validation was repeated locally under the frozen DELTA helper semantics and produced byte-identical result JSON both times:

`334cc40a6a121acfc002bedeb4e7bf5401b92a14b1912cc3185719ca2b8488cb`

Both parent and candidate were flat at the final observed tick.

## Holdout supply

C04 still produced adequate independent activity:

- proposals: **20**
- source eligible: **19**
- distinct days: **10**
- accepted SORB entries after parent interaction: **15**
- London proposals: 10
- COMEX proposals: 10

Therefore this is not a “no opportunity” failure.

## Parent control

Later-January surrogate-parent control:

- trades: **13,630**
- official wins: **5,912**
- gross profit: **+$1,877.63**
- gross loss: **-$4,734.64**
- net: **-$2,857.01**
- max balance DD: **$2,861.05**
- max equity DD: **$2,862.00**

Holdout specialist signals:

- DH03-S06: **1,524**
- DH05-S06: **537**
- DH02-S11: **75**
- DH02-S08: **81**

## C04 OOS result

Combined C04 result:

- trades: **13,645**
- official wins: **5,916**
- gross profit: **+$1,878.60**
- gross loss: **-$4,740.86**
- net: **-$2,862.26**
- max balance DD: **$2,866.30**
- max equity DD: **$2,867.25**

Incremental deltas versus the same holdout parent:

- trades: **+15**
- official wins: **+4**
- gross profit: **+$0.97**
- gross loss: **-$6.22**
- net: **-$5.25**
- max balance DD: **+0.1835%**
- max equity DD: **+0.1834%**
- incremental net / SORB entry: **-$0.35**

Direct SORB contribution:
- 15 entries
- 4 official wins
- net **-$4.72**
- London: 7 entries / 2 wins / **-$2.66**
- COMEX: 8 entries / 2 wins / **-$2.06**

## Decision

C04 fails the preregistered independent-validation rule because net worsens by **$5.25**, exceeding the maximum allowed **$2.00** deterioration, and it does not achieve the required strong-screen nonnegative incremental net.

**R037-C04_DUAL_30 is RETIRED.**

Do not:
- alter the 30-minute range after seeing this holdout;
- change confirmation count;
- split London/COMEX to rescue the same candidate;
- search holdout thresholds;
- reopen Stage-A C01/C02/C03/C05 as descendants of this failed validation.

The 15A Stage-A improvement is treated as discovery-sample behavior that did not generalize.

## Next bounded research direction

`HARVEST_NEXT_INDEPENDENT_ENTRY_SOURCE`

The next source must be structurally independent of the failed SORB C04 threshold family and must be preregistered before another canonical tick replay.
