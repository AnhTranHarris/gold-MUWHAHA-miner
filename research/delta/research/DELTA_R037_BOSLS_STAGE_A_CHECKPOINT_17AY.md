# DELTA R037 — BOS Liquidity-Sweep Reclaim — Checkpoint 17AY

**Status:** COMPLETE / NEARER QUALITY BUT NO EXECUTABLE SURVIVOR / RETIRED  
**Parent:** R037_LMJF_STAGE_A_SCREEN_CHECKPOINT_17AX  
**August:** SEALED | **MQL5:** NOT AUTHORIZED

## Test

The source-faithful structural screen used completed **M5** bars, MetaQuotes Part 46 default **SwingLength=5**, symmetric confirmed pivots, bullish BOS from a higher high / bearish BOS from a lower low, and only a completed rejection bar that wicked through the opposing confirmed swing, closed back inside, and closed in the reversal direction.

No swing-length/timeframe sweep, wick-depth filter, added confirmation, session/side filter, overlay, or exit tuning was allowed.

## Result

- signals/trades: **113**
- distinct days: **11**
- official wins: **62 (54.9%)**
- gross profit: **+$15.72**
- gross loss: **-$26.69**
- direct net: **-$12.10**
- exits: **109 STOP / 4 MAX_HOLD**

This is substantially closer to executable quality than raw DC/jump families, confirming that causal rejection/reclaim structure matters. It still fails the frozen economic gate, so it is not a valid survivor.

## Integrity

- prereg commit: `34ef5741861a41f52807986260b86847005c759f`
- producer commit: `79d7bab327d1d032072df36806aa4c02793db10f`
- producer blob: `82ef4ba1a8e270d48a4eed515167bd41f07ac5f8`
- producer SHA-256: `ca4366126dabca257bd9f5d7f82688c0d74d9283e7a4968c6f5fd8250428fc21`
- official result SHA-256: `92e3a745908252ae5b80712a90602523bb7aa01d8d653fc77169b654f6b4d232`
- exact Git blob / canonical January / chronology / hard timeout / atomic output: PASS

## Decision

**RETIRE_BOSLS_STAGE_A_NO_EXECUTABLE_SURVIVOR.**

Do not rescue this result with post-result filters.

**Next:** `R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`
