# DELTA R022 — Robust DUAL Action Subsets Preregistration

**Status:** PREREGISTERED / RAW REPLAY NOT STARTED  
**Parent:** R021 / R016-T06  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

Seven exact configurations are frozen:

- A-SKIP / A-KEEP: H1NetATR > 0.75 AND abs(H4NetATR) <= 0.45.
- B-SKIP / B-KEEP: abs(S15NetATR) > 1.75 AND abs(M30NetATR) > 1.30.
- C-SKIP / C-KEEP: M30NetATR <= -0.35 AND H1NetATR > 0.75.
- D-SKIP: micro250 > -1.0 AND milliseconds_into_minute <= 6000.

SKIP suppresses current M1. KEEP retains original R9 side with owned no-rearm. Everything else remains exact T06.

Stage-A surfaces P50/P75/P90; Native diagnostic. Trade/winner floors 80%. Must improve T06 net on all three modeled surfaces and avoid >5% GL/DD deterioration.

No post-result threshold/action invention.

Execution script SHA-256:
`6cdac1fae6c0c4135e6ccbbc8cf534fbf7a6be1baa2b79c081b7ad7671461efa`
