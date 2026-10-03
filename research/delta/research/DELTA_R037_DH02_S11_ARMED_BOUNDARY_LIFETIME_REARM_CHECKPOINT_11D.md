# DELTA R037 — DH02-S11 ARMED Boundary Lifetime / Re-arm — Checkpoint 11D

**Status:** COMPLETE MATERIAL NON-PROMOTING CLUE / FULL PARITY NOT ACHIEVED  
**Unit:** R037_DH02_S11_ARMED_BOUNDARY_LIFETIME_AND_REARM_PARITY_FINGERPRINT  
**Parent:** R037_DH02_S11_EVENT_OWNERSHIP_CONTEXT_STATE_CHECKPOINT_11C  
**Vector:** DH02-S11 / `50d1bb2e656e`  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Question

If a qualifying completed-S1 boundary break occurs while parent context is CONFLICT_CHOP, should the same ARMED boundary remain immediately usable after context clears, become stale until a new boundary, or suspend until a causal price reset?

No numeric S11 threshold was changed.

## Result

Historical target: **75 trades / 41 raw-positive wins / GP +9.39 / GL -17.60 / net -8.21**

| Profile | Trades | Raw+ wins | GP | GL | Net |
|---|---:|---:|---:|---:|---:|
| Control: persist through conflict | 106 | 42 | +7.80 | -35.10 | -27.30 |
| **Conflict break consumes until new boundary** | **103** | **41** | **+7.71** | **-33.74** | **-26.03** |
| S1-reset re-arm | 109 | 45 | +8.13 | -35.13 | -27.00 |
| Tick-reset re-arm | 109 | 45 | +8.13 | -35.13 | -27.00 |

The leading profile preserves the historical winner count **exactly at 41** while removing three trades, all from the losing population.

Trade-count error improves **31 → 28**. Gross-loss error improves **17.50 → 16.14**. This satisfies the bounded directional selection rule, but the improvement is too small to claim historical parity.

There were **151 unique conflict-period qualifying breaks** in the consume profile. Therefore the state distinction is real, but only three of those boundaries later produced executable control trades that disappear under consumption.

The S1-reset and tick-reset profiles are decisively rejected: both increase the executable population to 109 trades / 45 winners and produce the same signal fingerprint.

## Interpretation

A conflict-period qualifying break is a plausible **boundary-staleness event**. Treating it as stale until a newly confirmed boundary arrives removes only losing trades in this Stage-A fixture and preserves the exact historical winner count.

However, the surviving DH-02/DH-01 text establishes that invalid context prevents normal ARMED/BROKEN progression; it does **not** explicitly preserve the historical post-invalid-break ownership action. The source bytes that could distinguish ignore vs consume are unavailable.

Therefore this is a **non-promoting semantic challenger** pending provenance decision. It must not be silently frozen as historical truth from same-sample fit alone.

Producer:
`research/delta/experiments/delta_r037_dh02_s11_armed_boundary_lifetime_rearm.py`  
Commit: `0e0cbe48fbbf07157b79e2bbcca26462cbc9ce3f`  
Blob: `49e5c91c41a56b84017a1d2f2dc8c4104ed9e12f`

Compact result:
`research/delta/reference/DELTA_R037_DH02_S11_ARMED_BOUNDARY_LIFETIME_REARM_CHECKPOINT_11D.json`  
Commit: `9049a89e00bba5e43cf02cd76f2a921965b4b1d7`  
Blob: `8cd5f8e0258713f37f39554c0d7cfed488bb5e9a`  
SHA-256: `f21725af690fa82d7877a6d66d32a715411c1063fb9067fa7147cfa524daa2b3`

Official replay completed in approximately **8.58 seconds** under the hardened bounded runner; the exact control fingerprint reproduced.

## Decision

**Checkpoint 11D = QA PASS / MATERIAL NON-PROMOTING CLUE / FULL PARITY FAIL.**

Preserve for provenance review:
`CONFLICT_BREAK_CONSUME_UNTIL_NEW_BOUNDARY`

Reject:
- S1 reset re-arm;
- tick reset re-arm.

Do not retune thresholds, open August, start S08/SORB, or begin MQL5.

## Next bounded unit

`R037_DH02_S11_CONTEXT_INVALID_BREAK_ADMISSION_PROVENANCE_DECISION`

Decide whether independent surviving source evidence is sufficient to freeze the conflict-invalid-break staleness rule, or whether it remains a non-promoting challenger while another event-state axis is reconstructed.
