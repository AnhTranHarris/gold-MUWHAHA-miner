# DELTA R037 — DH05 Reclaim-Clock Semantics QA — Checkpoint 05

**Status:** COMPLETE NEGATIVE QA / CLOCK ALONE INSUFFICIENT  
**Parent:** R032-C03_PLUS_DH02_S11_S08  
**Unit:** R037_DH05_PARITY_RECLAIM_CONFIRMATION_CLOCK  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Fixed conditions
M5 ATR, frozen six M5-swing vectors, same-boundary causal re-eligibility, separate probe/failure clocks, close-based reclaim buffer, and the Checkpoint-03 reversal feature interpretation were held fixed. Only the completed clock used to confirm reclaim changed.

## Trade-count result

Historical targets: A03 306 / S05 51 / S06 615 / S09 119 / S10 206 / S16 24.

Vector reversal clock (baseline):
A03 187 / S05 9 / S06 617 / S09 9 / S10 206 / S16 8.

Universal S1 reclaim clock:
A03 195 / S05 13 / S06 617 / S09 9 / S10 213 / S16 9.

Universal S5 reclaim clock:
A03 187 / S05 9 / S06 437 / S09 3 / S10 206 / S16 8.

## QA conclusion

- S1 reclaim modestly increases A03/S05/S16, but remains far below their historical densities and moves S10 away from its exact target.
- S06/S09 already use S1 reversal clocks, so universal S1 cannot explain their remaining mismatch.
- Universal S5 severely under-produces S06 and S09.
- Therefore reclaim-clock selection alone is not the historical DH05 parity mechanism.

## Decision
Reject clock-only repair. Keep per-vector reversal clock as the current neutral baseline pending the next semantic test.

## Next bounded substep
`R037_DH05_PARITY_RECLAIM_BUFFER_EXCURSION_VS_CLOSE_SEMANTICS`

Test only:
1. current rule: completed reclaim close itself exceeds reclaim_buffer_atr on the pre-break side;
2. causal tick excursion reaches the reclaim buffer, followed by a completed S1/S5 close merely back on the pre-break side;
3. causal completed-bar extreme reaches the buffer, followed by close on pre-break side.

Stage counts first; six-vector fingerprint; no threshold retune.

## Diagnostic hashes
- source: `45b04ff222466918a6250682acb7adb0acde84153d831b22fb3c8c588bf9002d`
- output: `8d3beb935e34dda46683b15dac630d8d68dd91e8527a539c64a860e8837061b0`
