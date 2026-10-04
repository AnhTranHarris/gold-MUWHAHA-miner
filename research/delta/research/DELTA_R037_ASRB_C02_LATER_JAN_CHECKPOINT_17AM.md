# DELTA R037 — ASRB C02 Independent Later-January Validation — Checkpoint 17AM

**Status:** COMPLETE — INDEPENDENT HOLDOUT FAIL / CANDIDATE RETIRED  
**Candidate:** R037-ASRB-C02_RETEST  
**Parent:** R037_ASRB_STAGE_A_SCREEN_CHECKPOINT_17AL  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

The frozen 17AL C02 rule was carried unchanged into the non-overlapping later-January window: 00:00–06:00 UTC Asian range, 07:00–10:00 trade window, completed S5 breakout, boundary touch/retest and directional close back outside within six S5 bars, then first executable P75 tick.

Preregistration commit: `c74f570569bb577ae66681733774cf4ccb8616a8`  
Producer commit: `62af4b69a31c2f3cbf9204f10d67c9b5ea8439c6`  
Producer blob: `f75655b2a955c056aed3b022aa926ce71c2cf5cf`  
Official result SHA-256: `781ceea8d424f4fa49545ce59bb5cfdef70f8d04898b1d68cf3dff729090dbb9`

The first local execution was rejected because the local Git blob differed only in docstring bytes. After restoring exact committed bytes, blob equality passed and the official replay was rerun.

## Holdout

- 7 proposals
- 6 eligible / 6 trades
- 6 distinct days
- 5 long / 1 short
- 3 official wins
- gross profit +$0.43
- gross loss -$1.93
- **direct net -$1.50**

Gate:
- trades >= 3: PASS
- distinct days >= 3: PASS
- direct net >= $0: **FAIL**

## Decision

**RETIRE R037-ASRB-C02_RETEST WITHOUT RETUNING.**

The Stage-A 4/4 +$0.93 result did not survive independent validation. Do not alter the range window, retest horizon, side/day filters, or exit logic to rescue it.

Next: `R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`.
