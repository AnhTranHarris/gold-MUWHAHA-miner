# DELTA R037 — DH05 Post-Signal Intrabar Rearm Edge Parity — Checkpoint 09L

**Status:** COMPLETE BOUNDED QA / WEAK INTRABAR BOUNDARY-EDGE CLUE / NO FREEZE  
**Unit:** R037_DH05_POST_SIGNAL_INTRABAR_REARM_EDGE_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_POST_SIGNAL_PERSISTENCE_CHECKPOINT_09K  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Recovery / provenance

The producer was already durable before result promotion.

- producer commit: `a712fe238b437d1e1b07bdd4100359c59a07f03f`
- producer blob: `4b7bf08ebb0437ee02cf8c8aa48ed6987db10f9c`
- producer SHA-256: `eea81f2f78c338dcaede1d73c8129e7ec54f7a6714139c699d16bfdd5dc6b63e`
- runtime result SHA-256: `bbbe7bfbdfe616af25bae4a3d6e7d9bf0002c0251579959606e3289311356685`
- canonical January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Stage-A ticks: **4,205,709**

No August access and no frozen numeric-vector retune occurred.

## Bounded question

Can a causal tick-level rearm edge inside the still-frozen max-failure lifetime improve historical executable-trade density without extending episode lifetime?

The actual repeated signal remains completed-bar based. Only the **rearm edge** is allowed to occur intrabar.

## Result

The best candidate is:

`ORIGINAL_BOUNDARY_TICK_EDGE__ONE_POSITION_ONLY`

It lowers aggregate six-vector executable-trade-count absolute error:

**324 -> 304**, a **6.17%** improvement over the 09J/09K boundary-recycle control.

S06 changes:
- signals: **648 -> 638** against 672 target;
- trades: **647 -> 623** against 615 target;
- wins: **275 -> 260** against 307 target;
- net: **-$149.42 -> -$148.05** against -$101.08.

Thus S06 trade-count parity improves substantially, but signal and win parity deteriorate.

Sparse-vector trade density remains unresolved:
- A03: **208 vs 306**
- S05: **9 vs 51**
- S09: **11 vs 119**
- S16: **7 vs 24**

The reclaim-threshold tick edge is worse than the frozen boundary-recycle control:
**342** aggregate error.

## Interpretation

The original-boundary tick edge is a real architectural clue, but not strong enough to freeze. It mostly redistributes signal timing in the already-dense S06/S10 populations and does not generate the missing historical trade density in sparse vectors.

The stronger structural mismatch is now at the **signal-to-execution mapping**. The preserved Checkpoint-03 fingerprints contain cases where historical trades exceed preserved signal-stage counts. A one-signal/one-entry replay cannot reproduce those fingerprints by construction.

Therefore the next bounded question should test whether a causal generator signal creates an execution-side mandate that may admit more than one trade while valid, rather than forcing the generator itself to manufacture additional signals.

## Decision

**Checkpoint 09L = QA PASS / WEAK CLUE / NO NEW SEMANTIC FREEZE.**

Preserve only as diagnostic clue:
- original-boundary tick edge.

Keep frozen:
- 09C boundary + attempt ledger;
- 09D acceptance semantics;
- 09E per-attempt probe lifecycle clock;
- 09F post-qualification acceptance chronology as diagnostic branch;
- serial pre-reversal ownership;
- frozen max-failure lifetime;
- R9/Coinexx execution model.

Do not:
- retune numeric vectors;
- extend failure lifetime;
- integrate SORB;
- access August;
- optimize mature exits;
- begin MQL5.

## Next bounded unit

`R037_DH05_SIGNAL_TO_EXECUTION_MANDATE_PERSISTENCE_PARITY_RECONSTRUCTION`

Test only whether one causal DH05 generator signal can authorize multiple executable admissions under a separate causal execution mandate while preserving generator counts and frozen R9 execution semantics.
