# DELTA R037 — DH05 Reversal-Displacement Semantics QA — Checkpoint 07

**Status:** COMPLETE NEGATIVE QA / DISPLACEMENT ORIGIN ALONE INSUFFICIENT  
**Unit:** R037_DH05_PARITY_REVERSAL_DISPLACEMENT_SEMANTICS  
**Parent:** R032-C03_PLUS_DH02_S11_S08  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Fixed conditions
Close-buffer reclaim, vector reclaim/reversal clock, M5 ATR normalization for all current stages, same-boundary re-eligibility, separate probe/failure clocks and all frozen numeric vectors remained fixed. Directional efficiency stayed on the completed reversal bar. Only reversal displacement origin changed.

## Historical targets
A03 306 / S05 51 / S06 615 / S09 119 / S10 206 / S16 24.

## Trade counts
Bar-body displacement (baseline):
187 / 9 / 617 / 9 / 206 / 8.

Displacement from original boundary L:
206 / 8 / 681 / 22 / 236 / 12.

Displacement from reclaim close:
90 / 0 / 430 / 9 / 65 / 5.

## QA conclusion
- Boundary displacement improves A03/S09/S16, but remains far below A03/S09 targets and materially overshoots S06/S10.
- Reclaim-close displacement sharply under-produces most of the family.
- The baseline bar-body definition remains the least-distorting single universal displacement origin, but is not historical parity.
- Therefore the next plausible class is not another displacement origin; it is reversal efficiency / stage-normalization semantics.

## Next bounded substep
`R037_DH05_PARITY_REVERSAL_EFFICIENCY_AND_STAGE_NORMALIZATION_FINGERPRINT`

Test only reconstructible causal definitions:
- completed reversal-bar directional efficiency;
- short completed-bar path directional efficiency;
- reversal-stage ATR tied to reversal timeframe versus the current M5 event ATR, while leaving probe/boundary normalization fixed.

Do not perform a universal ATR substitution and do not retune vector thresholds.

## Diagnostic hashes
- source: `70477085c2471873b6bb197066aafd775dcd115d0026886b87ad1197a84a7a22`
- output: `a9fb2df8b477eb833fdce4f60bc51051ec46b1b9d8485f4a4babf6a6ab1afb9c`
