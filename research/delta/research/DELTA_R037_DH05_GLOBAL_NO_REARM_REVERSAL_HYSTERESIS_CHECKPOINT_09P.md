# DELTA R037 — DH05 GLOBAL NO_REARM + Reversal Hysteresis — Checkpoint 09P

**Status:** COMPLETE NEGATIVE QA / HYSTERESIS REJECTED / STRUCTURAL SIGNAL→TRADE GAP LOCALIZED  
**Unit:** R037_DH05_GLOBAL_NO_REARM_REVERSAL_HYSTERESIS_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_STATE_PERSISTENT_GLOBAL_NO_REARM_CHECKPOINT_09O  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Bounded question

Can the existing frozen `revdisp_atr` quantity act as a symmetric reversal-state hysteresis band while preserving exact R032 GLOBAL NO_REARM?

Semantics tested:
- directional body displacement >= +revdisp_atr × M5 ATR: confirm/reconfirm;
- opposite displacement <= -revdisp_atr × M5 ATR: explicit invalidation;
- neutral completed reversal bars: preserve mandate;
- no downstream re-entry in the same UTC minute as prior exit.

A stricter branch additionally required a neutral reset bar before later positive reconfirmation. Max-failure-capped and uncapped diagnostic variants were both observed. No numeric threshold was introduced or retuned.

## Provenance

- producer commit: `2dfb3532d991e74f7143d7f9c2de8b247aa1a40f`
- producer blob: `8b1dd2b54a916cd181cde6235d5e23bb14e9ba38`
- producer SHA-256: `8e196a1909f0a82fa992cc7e4a2bb19388e22b49b107d297d1f2ceccd4d7991a`
- official result SHA-256: `e269eeb481649f33010fbcdc38240e813f82986ca4384462e9347cfb5ef213e8`
- runtime: **11.06 s**
- max RSS: **698,076 KB**
- exit status: **0**
- fresh per-unit Numba cache used.

## Result

The one-shot control remains aggregate trade-count absolute error **336**.
The best durable clue remains 09L at **304**.

No 09P candidate beats either.

| Profile | Aggregate error | S06 trades | S06 wins | S06 reentries |
|---|---:|---:|---:|---:|
| NEUTRAL_RESET_RECONFIRM | **354** | 696 | 294 | 47 |
| SYMMETRIC_HYSTERESIS | 359 | 700 | 294 | 51 |
| NEUTRAL_RESET_RECONFIRM_MAXFAIL | 368 | 689 | 291 | 40 |
| SYMMETRIC_HYSTERESIS_MAXFAIL | 374 | 693 | 291 | 44 |

The leading profile improves S06 win parity to **294 vs 307**, only 13 low, but overtrades S06 by **81** and S10 by **94**.

Leading six-vector trade counts:
- A03 **286 / 306**
- S05 **11 / 51**
- S06 **696 / 615**
- S09 **15 / 119**
- S10 **300 / 206**
- S16 **9 / 24**

## Structural localization

This closes another execution-state branch.

S05 has only **9** frozen POST_QUAL generator signals against **51** preserved historical trades.
S09 has only **11** frozen generator signals against **119** preserved historical trades.

The state-reconfirmation branches still produce only **2** S05 and **4** S09 execution reentries. The sparse deficit therefore cannot be explained by:
- same-minute rearming;
- simple positive reversal persistence;
- neutral-preserving symmetric hysteresis;
- a short-lived max-failure-age mandate.

The next causal candidate is a separate **post-signal execution mandate** whose lifetime is governed by the original failed-break boundary rather than the pre-signal failure clock. It remains distinct from the generator and must retain GLOBAL NO_REARM.

This is materially different from 09K: 09K extended/recycled generator behavior and catastrophically manufactured signals. The proposed next unit keeps the generator singular and extends only downstream execution authorization while the original boundary continues to validate the reversal thesis.

## Decision

**Checkpoint 09P = QA PASS / NEGATIVE RESULT / NO NEW SEMANTIC FREEZE.**

Reject:
- symmetric reversal hysteresis as the universal parity solution;
- neutral-reset reconfirmation as sufficient sparse-density mechanism.

Preserve:
- exact GLOBAL NO_REARM as parent execution constraint;
- singular frozen 09F POST_QUAL generator;
- original-boundary validity as the next bounded downstream-lifetime question.

Do not retune vectors, alter generator counts, access August, integrate SORB, optimize mature exits, or begin MQL5.

## Next bounded unit

`R037_DH05_BOUNDARY_VALID_EXECUTION_MANDATE_WITH_GLOBAL_NO_REARM_PARITY_RECONSTRUCTION`

Test whether a singular generator signal creates a downstream execution mandate that remains valid while price stays on the reversal side of the original breakout boundary, with GLOBAL NO_REARM controlling repeat admissions. No generator multiplication and no new numeric threshold.
