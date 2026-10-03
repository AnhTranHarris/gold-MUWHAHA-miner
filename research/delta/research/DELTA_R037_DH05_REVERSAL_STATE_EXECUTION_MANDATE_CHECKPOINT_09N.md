# DELTA R037 — DH05 Reversal-State Persistent Execution Mandate — Checkpoint 09N

**Status:** COMPLETE BOUNDED QA / MIXED STATE-PERSISTENCE CLUES / NO FREEZE  
**Unit:** R037_DH05_REVERSAL_STATE_PERSISTENT_EXECUTION_MANDATE_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_SIGNAL_TO_EXECUTION_MANDATE_CHECKPOINT_09M  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Bounded question

Can a singular POST_QUAL generator signal support conditional execution re-entry only after a **new completed reversal-timeframe bar** causally reconfirms the failed-break thesis?

Generator counts remained frozen. No automatic tick re-entry and no numeric retuning were allowed.

Profiles:
- BODY_SIGN_CHAIN
- BODY_SIGN_CHAIN_MAXFAIL
- REV_DISP_CHAIN
- REV_DISP_CHAIN_MAXFAIL

BODY_SIGN requires the new completed reversal bar body to remain in the mandate direction. REV_DISP reuses the frozen `revdisp_atr` threshold. MAXFAIL variants additionally retain the existing vector max-failure cap.

## Provenance

- producer: `research/delta/experiments/delta_r037_dh05_reversal_state_persistent_execution_mandate_parity.py`
- producer commit: `d6b7186fed5ec4d5442703f26de1ea2e967dd647`
- producer blob: `2c37baf5c1ac3cc94de131c16185bdc8a4fcaa98`
- producer SHA-256: `63cace57bbd90d48beb56ceb4b546c90eafdd32ef3268119dc5f38cb92d3fc36`
- result SHA-256: `5d73747be66b05658c7ea601473ace2dbae87f301b4da5c205405a62be2218b2`
- runtime: **7.51 s**
- max RSS: about **698 MB**
- exit status: **0**

Canonical January source and **4,205,709** Stage-A ticks reproduced.

## Result

The one-shot control remains aggregate trade-count error **336**.

No state-chain profile beats the best 09L aggregate clue (**304**), so no universal carry-forward is justified.

### REV_DISP_CHAIN_MAXFAIL

Aggregate trade-count error: **412**.

S06:
- trades **707 vs 615**
- wins **295 vs 307**
- net **-$164.88 vs -$101.08**
- execution reentries **58**

The S06 win error is only **12**, a major local quality clue, but population remains too large.

### BODY_SIGN_CHAIN

Aggregate trade-count error: **485**, but one fingerprint is striking:

- **A03 = 306 trades exactly vs 306 historical**
- S05 16 vs 51
- S06 781 vs 615
- S09 14 vs 119
- S10 377 vs 206
- S16 16 vs 24

The max-failure variant changes A03/S05/S10 slightly but does not resolve dense-family overproduction.

## Interpretation

09N proves that state-conditioned execution multiplicity is materially more plausible than the blanket time-based mandates rejected in 09M.

Two complementary clues survive:

1. **BODY_SIGN_CHAIN** can recreate A03 trade density exactly.
2. **REV_DISP_CHAIN** materially improves S06 win parity.

But both overproduce dense S06/S10 and still underfill sparse S05/S09/S16.

The next source-grounded interaction is the already-frozen R032 parent **GLOBAL NO_REARM** rule. The committed parent backbone shows that after an exit, `global_no_rearm=True` suppresses ordinary generic rearm for the rest of that UTC minute; the new minute resets the opportunity cycle. Testing that exact same-minute suppression on downstream state-mandate re-entry is therefore causal and reconstructible, not an invented cooldown.

## Decision

**Checkpoint 09N = QA PASS / MIXED LOCAL CLUES / NO NEW SEMANTIC FREEZE.**

Preserve as diagnostic clues:
- BODY_SIGN state persistence for A03 density;
- REV_DISP state persistence for S06 win quality.

Do not promote either profile universally.

## Next bounded unit

`R037_DH05_STATE_PERSISTENT_EXECUTION_WITH_GLOBAL_NO_REARM_PARITY_RECONSTRUCTION`

Apply the parent R032 GLOBAL NO_REARM semantics exactly: after a mandate trade exits, suppress downstream re-entry during that same UTC minute. A new completed qualifying reversal bar may admit again only after the minute changes while the mandate remains valid.

No vector retuning, no August, no SORB integration, no mature-exit optimization, and no MQL5.
