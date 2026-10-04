# DELTA R037 — HTAR H1 Independent Later-January Validation — Checkpoint 17AJ

**Status:** COMPLETE — INDEPENDENT HOLDOUT PASS  
**Candidate:** R037-HTAR-C01_H1_ANCHOR  
**Parent:** R037_HTAR_STAGE_A_SCREEN_CHECKPOINT_17AI  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Frozen candidate

Causally confirmed H1 swing liquidity anchor → S5 sweep/reclaim → CISD through sweep-bar open → post-CISD reversal FVG → midpoint retrace/rejection → first executable P75 tick.

No parameter, side, session, weekday, stop, trail, or hold-time retuning.

## Holdout

Warm-up/context begins **2026-01-14 00:00 UTC**.  
Independent economics begin **2026-01-18 12:00 UTC** and end at **2026-02-01 00:00 UTC exclusive**.

Warm-up-loaded ticks: **6,076,533**.  
Economic holdout ticks: **4,929,353**.

The first pre-existing 17AJ helper was rejected before official compute because it still used Stage-A gates and allowed warm-up decisions into economics. Corrected producer commit:
`2054a0fc0cd7f003802dffaf056592cef765b603`
blob:
`a7ea2330ae0df805bc32780ce40eb0d22f60b694`
SHA-256:
`07ba9e2afae146a746a854258d850c7517a992690948e311332c7e0bc756da70`

## Result

- proposals: **7**
- trades: **7**
- distinct days: **7**
- long / short: **5 / 2**
- official wins: **3 / 7**
- gross profit: **+$1.92**
- gross loss: **-$1.27**
- direct net: **+$0.65**
- exits: 7 STOP / 0 MAX_HOLD

Every preregistered holdout gate passed:
- proposals >= 6
- trades >= 5
- distinct days >= 4
- direct net >= $0

Official raw-result SHA-256:
`0ab1b6c36cd3cdadd8add8d7dbb73d2604cc3da3b87c78682f417280abdf96a6`

## Interpretation

The H1-anchored source is now positive in **two non-overlapping January economic windows**:
- Stage-A: 8 trades / +$0.94
- later-January holdout: 7 trades / +$0.65

The sample remains small, so this is a validated candidate, not a promoted DELTA strategy.

## Decision

**FREEZE H1 UNCHANGED AND ADVANCE TO FEBRUARY–JULY MONTH-BY-MONTH ROBUSTNESS.**

Next:
`R037_HTAR_H1_FEB_JUL_ROBUSTNESS_VALIDATION`

No August and no rescue tuning if a month fails.
