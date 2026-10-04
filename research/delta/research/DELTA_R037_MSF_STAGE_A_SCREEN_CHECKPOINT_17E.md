# DELTA R037 — Market Structure + Fair Value Gap Retest Stage-A Screen — Checkpoint 17E

**Status:** COMPLETE / ORDINARY SCREEN CLUE / NO STRONG SCREEN SURVIVOR  
**Family:** R037-MSF-v1  
**Parent:** R037_STX_STAGE_A_SCREEN_CHECKPOINT_17D  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Source-grounded frozen hypothesis

This family tests a causal price-action transition rather than another oscillator/channel state:

- symmetric two-bar confirmed swing highs/lows, revealed only after two completed right-side bars;
- completed Bid-bar close beyond the latest revealed swing;
- initial break establishes state; same-direction later break = BOS; opposite-direction break = CHOCH;
- standard same-direction three-candle FVG must form on the same completed structure-break bar;
- first later completed bar that overlaps the gap and closes back through its 50% midpoint in the structure direction confirms the retest;
- entry is the first executable tick at/after that retest-bar edge.

The four preregistered variants are M1/M5 crossed with CHOCH/BOS. No swing width, FVG definition, midpoint, timeframe, side, session, or exit was altered after results.

Public reconstructible logic was taken from MetaQuotes MQL5 Article 18669, MetaQuotes Code Base 74575, TradingView's open-source FVG+BOS implementation, and ForexFactory implementation discussion. Performance claims were ignored.

## Crash/timeout controls

Preregistration commit:
`2739d418ad694f701a551743c2ff1561c5af0c37`

Producer commit:
`f700029a41abda79c775327c5f8497d6b69c0404`

Producer Git blob:
`29ccec103226f3044a9fdb7f7213731ab1428dee`

Verified producer SHA-256:
`4fbea383767200331138722bd27d0c83f3ee404a81468a26dbe2277c5521d7b4`

Recovery gate:
run **37177106978 PASS**.

A stale precompute SHA pointer was detected because the recovery snapshot's Git blob matched the live committed GitHub blob but not the stale SHA metadata. The pointer was corrected before scientific compute.

The first process launch failed during Python import with `ModuleNotFoundError: research` before data loading/replay and wrote no result. The launch environment was corrected by setting `PYTHONPATH` to the commit-bound recovery root. Producer bytes were unchanged.

The actual official Stage-A replay then exited **0** in approximately **20.026 seconds** under the bounded runner.

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**

Official raw result SHA-256:
`f9f2b66f012dc9e6548d6bd031b0729f27a1ce6a52d4185b80e936a9cc425891`

## Results

Parent control: **14,034 trades / 6,349 official wins / -$2,944.94 net / $2,946.43 max equity DD**.

- **C01 M1 CHOCH+FVG retest:** 136 proposals / 127 accepted; +124 trades / +46 official wins / **-$34.91 net delta**; direct MSF **-$31.99**; equity-DD +1.21%. FAIL.
- **C02 M1 BOS+FVG retest:** 86 / 84; +84 / +34 / **-$22.01**; direct **-$22.85**; equity-DD +0.75%. FAIL.
- **C03 M5 CHOCH+FVG retest:** 21 / 20; +19 / +7 / **-$4.79**; direct **-$5.77**; equity-DD +0.16%. FAIL.
- **C04 M5 BOS+FVG retest:** 20 / 16; +16 / +11 / **-$0.05**; direct **-$1.12**; equity-DD approximately **+0.0017%**. **Ordinary screen PASS; strong screen FAIL.**

C04 increased gross profit by **+$3.54** and gross loss magnitude by **-$3.59**, leaving the combined net only five cents below the strong nonnegative-net gate.

## Interpretation

This is the strongest independent entry-source clue in the 17A-17E harvest, but it is not a promotion candidate under the preregistered strong gate.

The important structural signal is the cross-family progression:

- M1 CHOCH is poor;
- M1 BOS is less poor;
- M5 CHOCH improves again;
- **M5 BOS + same-break-bar FVG + confirmed midpoint retest is nearly neutral while adding 11 official wins from 16 incremental trades.**

That supports preserving the exact C04 fingerprint as a forensic/combination clue. It does **not** authorize posthoc swing/FVG/session/side tuning or a later-January validation, because the preregistration reserved that validation only for a strong-screen survivor.

## Decision

**Checkpoint 17E = NO STRONG SCREEN SURVIVOR.**

- Do not promote MSF.
- Do not retune MSF.
- Preserve **C04 M5 BOS+FVG retest** as the leading price-action structural clue for future preregistered recombination work.
- Continue independent source harvesting.

Next:
`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

August remains SEALED. MQL5 remains unauthorized.
