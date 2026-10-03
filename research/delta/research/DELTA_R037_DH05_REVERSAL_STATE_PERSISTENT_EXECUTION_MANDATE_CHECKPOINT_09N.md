# DELTA R037 — DH05 Reversal-State Persistent Execution Mandate — Checkpoint 09N

**Status:** COMPLETE NEGATIVE QA / SIMPLE REVERSAL-STATE PERSISTENCE REJECTED / HYSTERESIS CLUE  
**Unit:** R037_DH05_REVERSAL_STATE_PERSISTENT_EXECUTION_MANDATE_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_SIGNAL_TO_EXECUTION_MANDATE_CHECKPOINT_09M  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Timeout recovery

The chat interruption did not erase the bounded compute. The 09N producer had already been committed, and the official local Stage-A replay had completed before message delivery stopped.

Recovery verified:
- producer commit: `d6b7186fed5ec4d5442703f26de1ea2e967dd647`
- producer blob: `2c37baf5c1ac3cc94de131c16185bdc8a4fcaa98`
- local producer git blob: exact match
- producer SHA-256: `63cace57bbd90d48beb56ceb4b546c90eafdd32ef3268119dc5f38cb92d3fc36`
- runtime result SHA-256: `5d73747be66b05658c7ea601473ace2dbae87f301b4da5c205405a62be2218b2`
- runtime: **7.51 s**
- max RSS: **698,036 KB**
- exit status: **0**
- canonical January ticks: **4,205,709**

The completed result was promoted instead of rerunning the same compute.

## Bounded question

Can a singular frozen POST_QUAL generator signal create a downstream execution mandate that survives only while causal reversal state remains valid or is reconfirmed?

Generator counts were frozen exactly. No threshold was retuned.

Profiles:
- BODY_SIGN_CHAIN
- BODY_SIGN_CHAIN_MAXFAIL
- REV_DISP_CHAIN
- REV_DISP_CHAIN_MAXFAIL

The max-failure variants reuse the existing vector max_failure_age; they do not extend it.

## Result

The one-shot control remains:
- aggregate six-vector trade-count absolute error: **336**
- S06: **651 signals / 649 trades / 274 wins / -$150.35**

No tested state-persistent profile beats the control, and none beats the weaker 09L original-boundary tick-edge clue at **304** aggregate error.

| Profile | Aggregate trade error | S06 trades | S06 wins | S06 net |
|---|---:|---:|---:|---:|
| REV_DISP_CHAIN_MAXFAIL | **412** | 707 | 295 | -$164.88 |
| REV_DISP_CHAIN | 413 | 707 | 295 | -$164.88 |
| BODY_SIGN_CHAIN_MAXFAIL | 484 | 781 | 330 | -$178.83 |
| BODY_SIGN_CHAIN | 485 | 781 | 330 | -$178.83 |

## Important clue

The negative result still localizes the next mechanism.

BODY_SIGN_CHAIN trade counts:
- A03 **306 / 306 exact**
- S05 **16 / 51**
- S06 **781 / 615**
- S09 **14 / 119**
- S10 **377 / 206**
- S16 **16 / 24**

So simple directional persistence can reconstruct A03 exactly, but it overfills dense S06/S10 while still leaving S05/S09/S16 sparse.

REV_DISP_CHAIN_MAXFAIL gives:
- S06 **707 trades / 295 wins** against **615 / 307**
- only **12 wins off target**, but trade count remains 92 high;
- sparse-vector deficits remain large.

This pattern argues against either:
1. blanket execution persistence; or
2. invalidating the mandate on the first weak/non-confirming reversal bar.

The next reconstructible hypothesis should reuse an existing parent execution invariant rather than invent a new state threshold. R032 already freezes a **GLOBAL NO_REARM** rule for ordinary same-minute rearms. Applying that exact causal execution constraint to the 09N state-persistent mandate may suppress dense S06/S10 repetition while preserving the useful A03/S06 state clues.

## Decision

**Checkpoint 09N = QA PASS / NEGATIVE RESULT / NO NEW SEMANTIC FREEZE.**

Reject as universal mechanisms:
- simple body-sign persistence;
- simple positive reversal-displacement persistence;
- first-nonconfirming-bar invalidation.

Preserve only the diagnostic clue that A03 is exact under body-sign persistence and S06 win parity improves under displacement reconfirmation.

Do not:
- retune frozen vectors;
- extend max_failure_age;
- integrate SORB;
- access August;
- optimize mature exits;
- begin MQL5.

## Next bounded unit

`R037_DH05_STATE_PERSISTENT_EXECUTION_WITH_GLOBAL_NO_REARM_PARITY_RECONSTRUCTION`

Test the 09N state-persistent execution mandate with the exact frozen R032 GLOBAL NO_REARM rule: suppress downstream re-entry during the same UTC minute after an exit. No numeric retuning.
