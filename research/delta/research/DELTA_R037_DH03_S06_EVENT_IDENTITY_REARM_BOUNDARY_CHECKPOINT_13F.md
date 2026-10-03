# DELTA R037 — DH03-S06 Event Identity / Rearm Boundary — Checkpoint 13F

**Status:** COMPLETE LOCALIZATION BREAKTHROUGH / FULL HISTORICAL PARITY NOT ACHIEVED  
**Unit:** R037_DH03_S06_PENDING_EVENT_IDENTITY_AND_REARM_BOUNDARY_PARITY_RECONSTRUCTION  
**Parent:** R037_DH03_S06_PENDING_VALIDITY_CHECKPOINT_13E  
**Vector:** DH03-S06 / `a3a086b7344c`  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Bounded question

The DH-03 white paper requires LOCAL_RECLAIM to be a completed S5 close through a **causally known** fast pivot/reclaim level, but it does not require that pivot to have been revealed after the original pullback began.

13F therefore tested only causal **pivot ownership and rearm-boundary semantics**. No numeric threshold, pending TTL, generator threshold, exit rule, lot size, SORB rule, or August data changed.

## Crash-safe official replay

Evidence, engine, and producer were committed before compute. GitHub Actions run **37159514446** passed and supplied the exact recovery snapshot used for execution.

- producer commit: `5d36e2c6ed3f3968a20f804f85e75dcb5eaef479`
- producer blob: `1e8c3f0462313604f18f26c00b0df4d7abcd9db0`
- engine commit: `e3fa78116d50fcac409d49c8d47b31e85a423402`
- engine blob: `02bd7b3c26585392171c8a5bebb8520df47aa59d`
- canonical January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Stage-A ticks: **4,205,709**
- runtime: **10.15 s**
- peak RSS: **698,480 KB**
- raw result SHA-256: `210b275d8134a5619dcfd129e2210bdd6f4310776bac703f7a686eb2dbe77308`

Both frozen 13C controls reproduced exactly:
- strict post-original-pullback: **1,586 signals / 1,513 trades / 674 raw-positive / net -339.14**
- unrestricted any-causal: **1,748 signals / 1,672 trades / 749 raw-positive / net -371.64**

## Results

Historical target:
**1,563 trades / 690 raw-positive wins / GP +151.82 / GL -490.75 / net -338.93 / DD 339.25**

| Pivot ownership profile | Signals | Trades | Raw+ | Net |
|---|---:|---:|---:|---:|
| strict post-original pullback control | 1,586 | 1,513 | 674 | -339.14 |
| any causal diagnostic | 1,748 | 1,672 | 749 | -371.64 |
| **inherited first attempt only** | **1,683** | **1,610** | **716** | **-362.29** |
| inherited first, then post-rearm pivot | 1,083 | 1,083 | 488 | -238.30 |
| start-latched first attempt | 767 | 747 | 342 | -159.06 |

The inherited-first profile is the only new rule near the historical activity range, but it **crosses past** the target: trade gap changes from -50 to +47, raw-positive gap from -16 to +26, while net deteriorates from a near-exact -339.14 to -362.29.

Its mechanism is clear: it adds **102 inherited-pivot reclaims** and produces 97 additional executed trades over the strict control. That is too much.

The stronger rearm-freshness interpretation collapses to 1,083 trades. Freezing the pullback-start pivot collapses to 747 trades. Therefore neither “always inherit old pivot” nor “require a new pivot after every rearm” matches the preserved fixture.

## 13E interaction

Applying the 13E full-event pending rule does not rescue the inherited-first profile:
- strict + full-event pending: **1,584 trades / 702 raw-positive / net -357.71**
- inherited-first + full-event pending: **1,681 trades / 744 raw-positive / net -380.86**

This confirms the remaining mismatch is not pending TTL/lifetime.

## Interpretation

13F is a **localization breakthrough**, not a candidate promotion.

The historical fixture sits between:
- strict post-pullback reclaim ownership, and
- one-time inherited reclaim permission.

The likely missing state variable is therefore whether a reclaim level is **consumed by a successful attempt**, whether the same pivot may be reused by later fresh-exhaustion attempts, and what causal event identity owns that pivot after a signal.

That is narrower than generic pivot age, pending validity, or rearm timing.

## Decision

**Do not promote any 13F profile.**

Freeze all prior 13C/13D/13E semantics. Preserve 13F as evidence that inherited-pivot eligibility is relevant but too permissive when unconditional for the first attempt.

Do not retune thresholds, add a TTL, alter exits, integrate SORB, access August, or begin MQL5.

## Next bounded unit

`R037_DH03_S06_RECLAIM_LEVEL_CONSUMPTION_AND_PIVOT_REUSE_PARITY_RECONSTRUCTION`

Test only source-compatible reclaim-level consumption/reuse rules inside the still-valid original pullback, with the frozen S5 reclaim timing and fresh-exhaustion rearm.
