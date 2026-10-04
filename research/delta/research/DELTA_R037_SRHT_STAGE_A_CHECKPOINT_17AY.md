# DELTA R037 — Sweep/Reclaim/Retest Stage-A Screen — Checkpoint 17AY

**Status:** COMPLETE / NO EXECUTABLE SURVIVOR / RETIRED  
**Parent:** R037_LMJF_STAGE_A_SCREEN_CHECKPOINT_17AX  
**August:** SEALED | **MQL5:** NOT AUTHORIZED

## Test

One preregistered causal M1 Swing Failure / liquidity-sweep profile was tested:

1. a symmetric two-left/two-right M1 pivot must already be fully confirmed before the sweep bar begins;
2. price wicks beyond that known swing;
3. the completed sweep bar closes back inside the level;
4. the next completed M1 bar retests that same level and again closes on the reclaimed side;
5. entry occurs only at the first executable P75 tick after that retest-hold bar closes.

No pivot-width sweep, retest-window sweep, ATR threshold tuning, session/side rescue, order-flow overlay, or exit retuning was allowed.

## Result

- completed M1 bars: **15,180**
- signals: **435**
- trades: **435**
- distinct days: **14**
- long / short: **214 / 221**
- official wins: **172**
- gross profit: **+$38.78**
- gross loss: **-$145.02**
- direct net: **-$110.59**
- exits: **413 STOP / 22 MAX_HOLD / 0 END**
- median signal gap: **1,619.95 s**

The pattern has adequate supply and balanced directional participation, but the post-confirmation 30-second lifecycle is strongly negative under frozen P75 execution. Retest confirmation does not rescue the failed-breakout family.

## Integrity

- prereg commit: `7b1ad1caf90a72cd5f9593d1e18c57250d7b4202`
- producer commit: `6d2398a7de520138b65e27dc3af6daf26095a4e2`
- producer blob: `ab6608125ce075ecfdbe094e7a9355e6c6c1de78`
- producer SHA-256: `b412c3592bccc44568d8d05a20197bc50b92e73f0a29657d19a2c5c00aeec47c`
- official raw result SHA-256: `ebf35dddc603e44213afdeab7c3b0535bdd0cb5fbca5208f547fdd08e0a6272a`
- canonical January hash/tick count PASS
- exact Git-blob verification PASS
- Python compile PASS
- hard process timeout 120 s
- atomic result output PASS

## Decision

**RETIRE_SRHT_STAGE_A_NO_EXECUTABLE_SURVIVOR.**

Do not rescue with parameter or exit tuning.

**Next:** `R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`
