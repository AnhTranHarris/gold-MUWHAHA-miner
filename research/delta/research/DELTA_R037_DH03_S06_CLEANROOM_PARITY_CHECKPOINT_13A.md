# DELTA R037 — DH03-S06 Clean-Room Parity Reconstruction — Checkpoint 13A

**Status:** COMPLETE CLEAN-ROOM PARITY FAIL / STATE-FUNNEL MISMATCH LOCALIZED  
**Unit:** R037_DH03_S06_CLEANROOM_PARITY_RECONSTRUCTION  
**Parent:** R037_DH02_S08_PARENT_DIRECTION_PROVENANCE_DECISION_CHECKPOINT_12C  
**Vector:** DH03-S06 / `a3a086b7344c`  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Historical fixture

The preserved R006 Stage-A fixture is:
- trades **1,563**
- raw-positive wins **690**
- win rate **44.145873%**
- gross profit **+151.82**
- gross loss **-490.75**
- net **-338.93**
- max balance DD **339.25**

Frozen S06 vector:
`counter_eff=.6468, exhaustion_decline=.4533, invalidation_buffer_atr=.3242, max_pullback_age_s=513.6575, no_new_extreme_count=1, parent_bundle=M15/M30, parent_policy=structural-priority, pullback_depth_atr=.4743, pullback_start_tf=S15, reaccel_eff_min=.2854, reaccel_tf=S5, reclaim_source=S15 pivot`.

The R006 report preserves the historical `r005_specialists.py` SHA-256 `fe1ccb8112f5bf37c83e7ce9e9dd82f782397a7710029716a61c159e4005afe0` and `dh03_results.jsonl` SHA-256 `3095a170efcd7cd644e6d2a371bec7723efab12a2c5c8921eba853bde4a4eb34`, but the original bytes were not recovered from GitHub, Drive, or Project/Library search.

## Crash-safe producer

The producer was split into three small committed modules after large GitHub contents writes repeatedly timed out:
- structure helper: `9fd75852690003d8e6d65cfdb9bb67198264fcae`
- Numba event engine: `e7f11325e26bf84491693ff84dae374e33bf48ab`
- thin producer, corrected before official compute: `6679c155cf923c7ee52dadc2f605c49377308319`

The first execution failed closed in **0.85 s** before any result write because a local variable name shadowed the imported pandas alias. The source defect was corrected and committed before the successful official run.

Local Git-blob verification exactly matched GitHub for all three source modules plus the 13A evidence file.

Official replay:
- canonical January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Stage-A ticks: **4,205,709**
- elapsed: **7.73 s**
- peak RSS: approximately **697 MB**
- result SHA-256: `179a1434f4b36dfeecc3655e34f23b3afcaaf06bd0c9d617c1eefab1a539e17d`

## Bounded semantic results

The strongest source-grounded interpretation is:
`STRUCTURAL_PRIORITY_SWING_PARENT_S15_EITHER_DECLINE`.

It produces:
- **709 trades**
- **302 raw-positive wins**
- GP **+64.43**
- GL **-229.79**
- net **-165.36**
- DD **165.36**
- 1,369 pullbacks
- 906 exhaustion candidates
- 722 reclaims
- 709 reacceleration signals.

Other profiles:
- strict S15+S30 exhaustion decline: **359 trades / 157 wins / -81.05**
- directional-confluence parent: **235 / 104 / -53.08**
- structural parent + previously known S15 pivot reclaim: **373 / 164 / -84.40**

## Interpretation

The historical target is **1,563 trades / 690 wins**. The 13A leader reaches only **709 / 302**.

This is important because the leader's raw win fraction is approximately **42.6%**, reasonably close to the historical **44.15%**, while its activity is only about **45.4%** of target. Economics are also broadly proportional to the missing population.

Therefore the dominant residual is **upstream state/event multiplicity**, not a license to tune numeric thresholds.

The most informative 13A clue is exhaustion semantics:
- requiring both S15 and S30 decline is far too sparse;
- permitting either source-grounded decline nearly doubles the signal population;
- changing parent direction or reclaim-pivot timing does not close the activity gap.

## Decision

**Checkpoint 13A = QA PASS / CLEAN-ROOM PARITY FAIL / EVENT-DENSITY MISMATCH LOCALIZED.**

Do not retune S06 numeric parameters.

Carry forward for the next parity diagnostic:
- frozen S06 vector and causal timeframe contract;
- structural-priority M15/M30 parent as the leading parent interpretation;
- exhaustion may be triggered by either S15 or S30 causal weakening as the leading 13A hypothesis;
- frozen S15-pivot reclaim and S5 reacceleration grammar.

## Next bounded unit

`R037_DH03_S06_STATE_FUNNEL_SEMANTICS_PARITY_RECONSTRUCTION`

Goal: explain the remaining 709 → 1,563 activity gap by source-grounded event reset/multiplicity semantics: whether pullback episodes may generate multiple exhaustion/reclaim/reacceleration attempts while parent structure and the original pullback remain valid, and whether impulse-extreme/event consumption is being reset too aggressively. No numeric threshold retuning.
