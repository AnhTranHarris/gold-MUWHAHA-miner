# DELTA R037 — DH03-S06 State-Funnel Semantics — Checkpoint 13B

**Status:** COMPLETE MATERIAL TIMING REPAIR / FULL HISTORICAL PARITY NOT ACHIEVED  
**Unit:** R037_DH03_S06_STATE_FUNNEL_SEMANTICS_PARITY_RECONSTRUCTION  
**Parent:** R037_DH03_S06_CLEANROOM_PARITY_CHECKPOINT_13A  
**Vector:** DH03-S06 / `a3a086b7344c`  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Timeout recovery context

The prior ChatGPT message-delivery interruption occurred after the 13A producer/result/report/workbook had been committed but before its full rebuild manifest and durable state pointer were advanced. The existing 13A science was audited rather than rerun. A complete 13A manifest was added, `CURRENT_STATE.json` advanced to 13A, the dedicated timeout-recovery pointer synchronized, and DELTA rebuild-gate run **37157416382** passed.

13B therefore started from the recovered durable 13A cursor.

## Source-grounded defect

The canonical DH-03 white paper states:

- `LOCAL_RECLAIM` is a **completed S5 close** back through a causally known fast pivot/reclaim level in parent direction.
- The S06 vector freezes the reclaim-level source as an **S15 pivot**.
- `REACCELERATION` occurs only after LOCAL_RECLAIM and is also evaluated on completed S5 information.

The 13A clean-room engine used an S15 close itself to test the reclaim crossing. That sampled the reclaim transition only once per 15-second bar and was inconsistent with the white-paper timing grammar.

## Bounded preregistration

No threshold changed.

13B tested:
1. the exact 13A control;
2. S5 reclaim through a causally known S15 pivot revealed after pullback start;
3. S5 reclaim through any already-causal S15 pivot;
4. an S15 pivot frozen at exhaustion and then crossed by S5.

Evidence was committed before compute:
`research/delta/reference/DELTA_R037_DH03_S06_STATE_FUNNEL_EVIDENCE_13B.json`

Producer commit:
`a81f9f63221c5333b6617dd9bff95ecb7ab9026d`

Engine commit:
`13aac682d133a656896fb7828c6fc33f90950ef9`

The producer, engine, evidence, 13A engine, structural helper, and canonical January file were blob/hash verified before official execution.

## Official replay

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**  
Elapsed: **13.49 s**  
Peak RSS: approximately **697,928 KB**  
Official raw result SHA-256:
`0c1d244c72173f488686758ea483fa4c423587d93f1544c0a10ac0ad3c41f707`

The 13A control reproduced exactly:
**709 trades / 302 raw-positive wins / 1,369 pullbacks / 906 exhaustion / 722 reclaim** with the exact historical 13A signal fingerprint.

## Results

Historical target:
**1,563 trades / 690 raw-positive wins / GP +151.82 / GL -490.75 / net -338.93 / DD 339.25**

| Profile | Trades | Raw+ wins | GP | GL | Net | Reclaims |
|---|---:|---:|---:|---:|---:|---:|
| 13A S15-close control | 709 | 302 | +64.43 | -229.79 | -165.36 | 722 |
| S5 reclaim, post-pullback pivot | **783** | **363** | +73.90 | -237.34 | -163.44 | 790 |
| S5 reclaim, any causal pivot | **860** | **388** | +77.54 | -264.84 | -187.30 | 868 |
| S5 reclaim, pivot frozen at exhaustion | 427 | 188 | +35.15 | -133.25 | -98.10 | 429 |

The literal S5 timing repair adds **74 trades and 61 raw-positive wins** relative to 13A. The broader already-causal pivot interpretation adds **151 trades and 86 wins**, closing about **17.68%** of the original 13A activity deficit.

## Interpretation

The S5 reclaim timing mismatch is real and materially important, but it does not explain the full 709 → 1,563 historical population gap.

The strongest scalar fit is the any-causal-pivot profile, but 13B does **not** promote that pivot-age choice as historical truth merely because it scores better. What is source-grounded enough to freeze is the **S5 reclaim timing** itself.

The remaining gap is now more sharply localized to pullback-event multiplicity/reset semantics:
- whether one still-valid pullback can produce more than one exhaustion/reclaim/reacceleration attempt;
- whether the impulse extreme is reset too aggressively after a signal;
- whether an unsuccessful reclaim/reacceleration attempt should return to EXHAUSTION_CANDIDATE rather than destroy the pullback episode;
- whether event lifetime remains attached to the original pullback while attempts recycle causally inside it.

These are state-machine questions, not threshold questions.

## Decision

**Checkpoint 13B = QA PASS / MATERIAL SOURCE-GROUNDED TIMING REPAIR / FULL PARITY FAIL.**

Freeze:
- the 13A structural-priority M15/M30 parent hypothesis;
- either-S15-or-S30 exhaustion weakening as the leading bounded exhaustion interpretation;
- S15 pivot as the S06 reclaim-level source;
- **LOCAL_RECLAIM evaluation on completed S5 closes**;
- later completed-S5 reacceleration;
- every frozen S06 numeric value.

Do not:
- retune thresholds;
- claim historical DH03-S06 parity;
- select a pivot-age variant solely by Stage-A fit;
- integrate SORB;
- access August;
- begin MQL5.

## Next bounded unit

`R037_DH03_S06_PULLBACK_EVENT_MULTIPLICITY_AND_RESET_PARITY_RECONSTRUCTION`

Goal: test source-compatible event persistence and repeated exhaustion/reclaim/reacceleration attempts inside one causally valid pullback, while preserving the 13B S5 reclaim timing repair and all frozen numeric thresholds.
