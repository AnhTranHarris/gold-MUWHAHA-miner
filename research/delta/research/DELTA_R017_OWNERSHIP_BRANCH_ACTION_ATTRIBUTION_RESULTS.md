# DELTA R017 — Ownership Branch Action Attribution Results

**Status:** COMPLETE / R016-T06 RETAINED / DUAL-TOXICITY MINING NEXT  
**Parent:** R016-T06  
**Scope:** ENTRY + INITIAL-HOLD / DIRECTION OWNERSHIP  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Result

All 27 preregistered branch-action configurations were evaluated on P50/P75/P90, plus Native diagnostic.

R017-B14 (R016/T06 canonical):
- MICRO_ONLY = FLIP + owned no-rearm
- H1_ONLY = FLIP + owned no-rearm
- DUAL non-extreme = FLIP + owned no-rearm
- extreme dual = SKIP current M1

Worst P50/P75/P90:
- trade retention 80.0067%
- winner retention 82.7882%
- net-loss improvement vs R9 22.4485%
- GL improvement 19.3587%
- DD improvement 22.4547%

It is the highest-quality configuration that still clears all preregistered modeled-surface activity floors.

## Attribution

H1_ONLY:
- FLIP materially improves over KEEP.
- SKIP improves loss much further but destroys activity.

MICRO_ONLY:
- FLIP improves over KEEP.
- SKIP improves loss but generally destroys activity/winner retention.

DUAL non-extreme:
- B15 (FLIP / FLIP / SKIP) improves quality on all modeled surfaces.
- It fails the preregistered activity gate because worst-surface trade retention falls to 77.6368%.

Therefore blanket DUAL avoidance is rejected, but the DUAL branch contains a strong toxic-subset signal.

## Native diagnostic

Native remains sparse and unsupportive. R017-B14 is worse than the sparse R9 Native control. This remains a promotion blocker.

## Result hashes

- P50: `0409117e541086856a0746df6e43aa8c7d3090b7537c69e54b2758500e0b661e`
- P75: `fa35413e4294adc7c438e61d14b79310e949a2d29817c87e802739d0297e9118`
- P90: `0916ffd2398d8d7cb1c81693970324fed3890d45ee449fe668b82a29bdcdf233`
- Native: `54a4e955db04695fd6875c531b2fff6dd458692c48ea9c15c442760ffebf1bd5`

## Decision

Retain R016-T06. No promotion and no metric lock.

Next leverage target:
**causal DUAL-branch toxicity decomposition**.

Mine the DUAL non-extreme branch using causal/reconstructible context (M30/H4 structural position, micro-intensity, session and related continuous features). Outcome labels may be used only offline to form hypotheses. Any action rule must be preregistered and raw-tick replayed before acceptance.
