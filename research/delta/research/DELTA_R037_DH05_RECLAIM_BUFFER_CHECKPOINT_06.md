# DELTA R037 — DH05 Reclaim-Buffer Semantics QA — Checkpoint 06

**Status:** COMPLETE NEGATIVE QA / BUFFER ALONE INSUFFICIENT  
**Unit:** R037_DH05_PARITY_RECLAIM_BUFFER_EXCURSION_VS_CLOSE_SEMANTICS  
**Parent:** R032-C03_PLUS_DH02_S11_S08  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Fixed conditions
Vector reclaim clock, M5 ATR, six frozen M5-swing vectors, same-boundary re-eligibility, separate probe/failure clocks and the current reversal feature interpretation remained fixed.

## Tested causal reclaim-buffer meanings
0. completed reclaim close itself exceeds the buffer on the pre-break side;
1. causal tick excursion reaches the buffer, followed by a completed close merely back on the pre-break side;
2. completed reclaim-bar extreme reaches the buffer, followed by a close back on the pre-break side.

## Trade counts

Historical targets: A03 306 / S05 51 / S06 615 / S09 119 / S10 206 / S16 24.

Close-buffer baseline:
187 / 9 / 617 / 9 / 206 / 8.

Tick-excursion-buffer:
209 / 14 / 653 / 9 / 228 / 9.

Completed-bar-extreme-buffer:
208 / 14 / 645 / 9 / 222 / 9.

## QA conclusion
- Excursion/extreme buffer semantics modestly increase A03/S05/S16.
- S09 remains **9 vs historical 119** under all three rules.
- S06 and S10 move materially above their already-near/exact targets under the looser buffer semantics.
- Therefore reclaim-buffer interpretation alone cannot reproduce the historical family fingerprint.

## Decision
Keep the original close-buffer interpretation as the neutral clean-room baseline. The next high-value layer is reversal displacement/efficiency semantics plus explicit generator-signal vs executable-trade admission.

## Next bounded substep
`R037_DH05_PARITY_REVERSAL_DISPLACEMENT_EFFICIENCY_SEMANTICS_FINGERPRINT`

Test only reconstructible causal feature definitions:
- displacement from reversal-bar open;
- displacement from original boundary L;
- displacement from reclaim close;
- directional efficiency on the completed reversal bar;
- directional efficiency over a short completed-bar path after reclaim.

Use six-vector stage counts first. Preserve all numeric vector thresholds.

## Diagnostic hashes
- source `b1bf54fcd7ddf444abfc3acd4599874aa5620289e6f842124ee4106697ecf270`
- output `d5dd089c08c0d65ba713f2c4f6f102841b0af287c29846e8cb13163403f39d1a`
