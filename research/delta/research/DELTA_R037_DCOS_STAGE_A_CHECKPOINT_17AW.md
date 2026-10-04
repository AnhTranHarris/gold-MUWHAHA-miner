# DELTA R037 — Directional-Change / Overshoot Stage-A Screen — Checkpoint 17AW

**Status:** COMPLETE / NO EXECUTABLE SURVIVOR / RETIRED  
**Parent:** R037_QRBM_STAGE_A_SCREEN_CHECKPOINT_17AV  
**August:** SEALED | **MQL5:** NOT AUTHORIZED

## Why this family

The prior microstructure families repeatedly failed because their predictive displacement was too small relative to P75 execution cost. Directional-change intrinsic time was selected because published FX work defines sparse events by a completed reversal threshold and documents post-confirmation overshoot behavior. The preregistered threshold was fixed at **0.05%**, matching a published BRACIL FX research sample; no threshold sweep was allowed.

## Official Stage-A result

- signals/trades: **5,729**
- distinct days: **14**
- official wins: **2,471**
- gross profit: **+$618.04**
- gross loss: **-$1,800.48**
- direct net: **-$1,239.73**
- exits: **5,663 STOP / 66 MAX_HOLD**
- median confirmation move: **4,670 mid2 raw**
- median inter-event gap: **87.411 s**

The intrinsic-time event is much larger and sparser than raw queue imbalance or spread shocks, but same-direction post-confirmation continuation still does not survive the frozen 30-second P75 lifecycle.

## Integrity

- prereg commit: `fdc3ec8d81d9183ebd9f8985e513ac128797ec99`
- producer commit: `02e016d5acce736ee9695cf2a4ad3c67cc902b1b`
- producer blob: `3ab76ce6a215da928132de02a30d5da135e4dd8b`
- producer SHA-256: `fb8378a2c62943b878e24eef01f1f6adffe99db2157a1d2eb7f0970f4e1007d0`
- official result SHA-256: `09aa6915f7cc22ca95a15415ebe8cd3a50f8659af49c05c9215b2af9950317c9`
- canonical January SHA/tick count PASS
- exact local Git blob verification PASS
- Python compile PASS
- hard process timeout 120 s
- atomic result output PASS

## Decision

**RETIRE_DCOS_STAGE_A_NO_EXECUTABLE_SURVIVOR.**

Do not rescue with threshold calibration, session/side filters, microstructure overlays, or exit tuning.

**Next:** `R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`
