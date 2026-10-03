# DELTA R037 — DH02-S11 Event Ownership / Context-State Parity — Checkpoint 11C

**Status:** COMPLETE MATERIAL STATE-PLACEMENT CLUE / SELECTION-RULE FAIL / EXACT PARITY NOT ACHIEVED  
**Unit:** R037_DH02_S11_EVENT_OWNERSHIP_AND_CONTEXT_STATE_PARITY_RECONSTRUCTION  
**Parent:** R037_DH02_S11_TICK_PERSISTENCE_CONTEXT_CHECKPOINT_11B  
**Vector:** DH02-S11 / `50d1bb2e656e`  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Source-grounded question

The DH-02 state grammar says ARMED requires both a causally known eligible boundary and parent context that permits breakout research. Checkpoint 11B rejected hidden 2/3-tick persistence and simple post-break continuous conflict invalidation.

This checkpoint therefore tested whether `parent_context = conflict-only veto` belongs in **boundary eligibility / ARMED state ownership before BROKEN**.

No numeric S11 parameter was changed.

## Preregistered profiles

1. **CONTROL_BREAK_REBREAK_CONTEXT** — 11B control.
2. **BOUNDARY_REVEAL_ELIGIBILITY** — a newly revealed boundary is eligible only if parent context is non-conflict at causal reveal.
3. **PREBREAK_DISARM_ON_CONFLICT** — a known idle boundary is permanently disarmed/consumed if CONFLICT_CHOP appears before break.
4. **REVEAL_ELIGIBILITY_PLUS_PREBREAK_DISARM** — both rules.

Evidence:
`research/delta/reference/DELTA_R037_DH02_S11_EVENT_OWNERSHIP_CONTEXT_STATE_EVIDENCE_11C.json`

Evidence commit: `7a3fefc87367d14a1dbec4a46883eae0c78a31a4`

Producer:
`research/delta/experiments/delta_r037_dh02_s11_event_ownership_context_state_parity.py`

Producer commit: `1cd4ecb115f6f056d3adc04db4a5007baf41f99a`  
Producer blob: `edeb71fff1428d45d7475f7f6bceef2a993938b2`  
Producer SHA-256: `dbf61cf572e0740e09e662f75ce7a5b878c18d0117d35dec4a27000f8bf6e513`

The committed recovery snapshot and canonical January source were hash-verified before official replay. The 11B control fingerprint reproduced exactly. Official execution completed in approximately **9.17 seconds** under the hardened bounded runner.

## Result

Historical target: **75 trades / 41 raw-positive wins / GP +9.39 / GL -17.60 / net -8.21**

| Profile | Trades | Raw+ wins | GP | GL | Net |
|---|---:|---:|---:|---:|---:|
| Control | 106 | 42 | +7.80 | -35.10 | -27.30 |
| Boundary reveal eligibility | 92 | 34 | +7.00 | -31.45 | -24.45 |
| **Pre-break disarm on conflict** | **91** | **33** | **+6.83** | **-31.44** | **-24.61** |
| Reveal + pre-break disarm | 91 | 33 | +6.83 | -31.44 | -24.61 |

The activity effect is large:
- control trade-count error: **31**
- leading trade-count error: **16**

But the winner fingerprint deteriorates:
- control win error: **1**
- leading win error: **8**

Gross loss also remains far from historical:
- target GL: **-$17.60**
- control GL: **-$35.10**
- leading GL: **-$31.44**

## Interpretation

This is a meaningful **state-placement clue**, but it fails the preregistered carry-forward rule.

Moving CONFLICT_CHOP into the ARMED/pre-break ownership state proves that boundary-lifecycle context can remove a large fraction of the excess event population. However, **permanent consumption** removes too many historical winners. It is therefore too destructive to promote as the historical semantic.

The equality of the two pre-break-disarm profiles is also informative: once conflict permanently consumes an armed boundary before break, a separate reveal-time eligibility veto adds no executable effect.

The next question is no longer whether context belongs upstream—it clearly has leverage there. The question is **what happens to the same boundary when context becomes conflicted and later clears**:
- consume forever;
- suspend while conflict is active then re-arm;
- require a fresh non-conflict transition;
- preserve boundary identity but restart its armed lifetime.

Those are categorical state-machine choices, not threshold tuning.

## Decision

**Checkpoint 11C = QA PASS / MATERIAL STATE-PLACEMENT CLUE / SELECTION-RULE FAIL / HISTORICAL PARITY FAIL.**

Do not freeze permanent pre-break boundary consumption as historical truth.

Carry forward only the localization:
- ARMED/boundary-context placement is high leverage;
- permanent boundary consumption is too destructive;
- next-tick persistence remains frozen;
- S11 numeric vector remains frozen.

Compact result:
`research/delta/reference/DELTA_R037_DH02_S11_EVENT_OWNERSHIP_CONTEXT_STATE_CHECKPOINT_11C.json`

Committed result blob:
`8c4b50a8ae94c1d62d8cb149d17d7643ffff94c3`

Committed result SHA-256:
`34e62a5284e37bb59b667c4ab79454d1820f642d5ce162fbff20d246b5bcadcb`

## Next bounded unit

`R037_DH02_S11_ARMED_BOUNDARY_LIFETIME_AND_REARM_PARITY_FINGERPRINT`

Goal: test source-grounded **suspend/re-arm semantics** for an already known boundary across transient CONFLICT_CHOP periods before BROKEN. No numeric retuning.
