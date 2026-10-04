# DELTA R037 — SMOR + FVG Confluence Stage-A Screen — Checkpoint 17I

**Status:** COMPLETE / NO SCREEN SURVIVOR / SUPPLY TOO SPARSE  
**Family:** R037-SFOC-v1  
**Parent:** R037_SMOR_STAGE_A_SCREEN_CHECKPOINT_17H  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

17I preserved the exact 17H C02 sweep→MSS→OB-midpoint lifecycle and added only preregistered same-direction classic three-candle FVG context.

Producer commit `1daf3647c7ebf42d1987612ef18b3ad9b31e975c`; blob `fc9c4615b056b0ad6e5400be8582c3fafb933b6c`; SHA-256 `88b6ad3cefbc9763b6d9aa5bc793007d2b4bceeeeaf28aafbb207c6502bfd93d`. Precompute recovery gate **37178752110 PASS**. Official bounded replay: **20.625s / exit 0**. Raw result SHA `9d47120a2612c078ea8ee40ab8d570c01beb284e6431abc1f219195d362e0399`.

Results:
- C01 any active same-direction FVG: 5 accepted / +5 trades / +3 wins / **-$0.56**. Supply FAIL.
- C02 FVG on MSS or next bar: 0 accepted. FAIL.
- C03 OB/FVG overlap: 1 accepted / +1 trade / +1 win / **+$0.19**. Positive but far below supply floor.
- C04 retest touches active FVG: 0 accepted. FAIL.

The result is scientifically useful but not promotable: adding FVG context improves selectivity enough to produce a positive one-trade subset, but collapses the event population below the frozen minimum. One winning trade is not evidence of a valid candidate and will not be used for post-hoc rescue tuning.

**Decision:** RETIRE R037-SFOC-v1 / NO RETUNE.

Next research direction: preserve the 17H timing insight but restore event supply using a stronger external liquidity anchor. The next family will preregister previous-day high/low sweep → local MSS → order-block retest, using both PDH and PDL without post-hoc level splitting.

August remains SEALED. MQL5 remains unauthorized.
