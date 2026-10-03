# DELTA R037 — DH05 Decoupled Probe Generator / Failure Episode — Checkpoint 09H

**Status:** COMPLETE NEGATIVE QA / FULL DECOUPLING REJECTED / PARTIAL-DECOUPLING CLUE  
**Unit:** R037_DH05_DECOUPLED_PROBE_GENERATOR_AND_FAILURE_EPISODE_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_POSTQUAL_STATE_REFRESH_CHECKPOINT_09G  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Bounded architecture test

Historical Checkpoint-09 explicitly distinguished:
- failed-break episode state;
- generator signal events;
- duplicate/repeated signal eligibility;
- executable admission.

This unit therefore tested whether the probe generator should be released immediately when a qualified probe becomes FAILURE_CANDIDATE while the failed-break episode continues independently toward reentry/reclaim/reversal.

Both frozen 09E acceptance and the 09F post-qualification acceptance chronology were tested.

No numeric vector changed.

## Producer

Path:
`research/delta/experiments/delta_r037_dh05_decoupled_generator_failure_episode_parity.py`

Final corrected producer commit:
`17add311ec3429aee46f1399b4d52cb74fdbb3c7`

Blob:
`776359c884d4404aeead23eec81eb11292569e49`

File SHA-256:
`033aab5c4aa006eae9ac790dda8e9e555f7d23e5edec4e966b79b1f5ba920f48`

Official runtime output SHA-256:
`4eb7d86721f6b8d2b696d06d34a0364fd2ece2352b03945dbfc296dee8b4c705`

Stage-A ticks: **4,205,709**.

Before compute, the byte-parity gate caught and repaired a source-generation defect that had dropped the serial re-attempt `probe += 1` / `attempt_start = tm` lines. No result was generated from the bad draft.

## Result

Full failure-candidate decoupling is decisively rejected:

- CONTROL_09E total error: **1,064**
- POST_QUAL_BASE: **978**
- DECOUPLED_09E: **14,285**
- DECOUPLED_POST_QUAL: **14,260**

The decoupled implementation had:
- maximum concurrent failure episodes: **8**
- episode overflow: **0**

Therefore the rejection is not caused by the bounded episode-array capacity.

## Important partial clue

Although global immediate decoupling fails, three historically sparse vectors become strikingly close under DECOUPLED_POST_QUAL:

- S05 target 7875/318/28/290/51/15/9/9; actual **7818/315/34/281/56/20/9/9**
- S09 target 7748/208/40/168/61/40/9/9; actual **7856/219/44/175/65/41/11/11**
- S16 target 7870/135/43/92/37/18/8/8; actual **7778/134/53/81/33/19/8/8**

But S06 and S10 overproduce badly:

- S06 target 3470/1606/245/1358/1211/683/617/617; actual **7373/3117/370/2747/2412/1372/1281/1281**
- S10 target 6496/1316/202/1106/623/294/206/206; actual **7778/1536/223/1313/772/373/283/283**

This pattern is too structured to dismiss as noise. It strongly suggests that generator/downstream ownership is partly decoupled, but **FAILURE_CANDIDATE is too early a release point**.

## Decision

**Reject full immediate decoupling. Preserve partial-decoupling evidence.**

Next test only later causal release points:
- release generator at **REENTRY**;
- release generator at **RECLAIM**;
- keep downstream episode alive through reversal;
- retain serial POST_QUAL control;
- no threshold retuning.

## Next bounded unit

`R037_DH05_PARTIAL_DECOUPLING_RELEASE_AT_REENTRY_OR_RECLAIM_PARITY_RECONSTRUCTION`

No SORB. No August. No MQL5.
