# Gamma_2 Source-Equivalence Recovery — Timestamp Semantics Checkpoint

**Status:** VERIFIED_DURABLE_DIAGNOSTIC / SOURCE EQUIVALENCE UNRESOLVED

The certified January target remains **30,943 trades / 25,368 winners / 81.983001% / +$5,131.051 / -$6,091.2065 gross loss**. The certified Jan–Jul 81.19% build remains the historical benchmark. The 67–69% reconstruction family remains rejected source-equivalence archaeology.

## What was preserved
All current recovery helper sources are now committed under `research/R9_Rebuild/source_equiv/recovery/`, with SHA-256 identities bound in the companion manifest. This includes the base January engine, retrospective-timestamp diagnostic, break-lag diagnostic, same-second-OHLC diagnostic, timestamp/alignment diagnostic, alignment-mapping diagnostic, and the discrete timestamp semantics unit.

## New bounded result
The discrete timestamp unit tested only historically plausible/source-like timestamps: break tick, first/last tick of the break second, next-second variants, reclaim tick/first/last, confirmation tick/first/last, and next-confirmation-second variants. It also compared alignment at signal versus confirmation.

Every genuinely causal entry timestamp tested remains near the failed ~68% family and negative. The strongest causal example is 27,149 trades / 18,513 winners / 68.190% / -$4,236.75 net / -$11,006.27 gross loss.

The closest density candidate is 30,923 trades / 25,812 winners / 83.472% / +$3,495.23 / -$5,779.15 gross loss, but **95.88% of accepted entries occur before the later confirmation that selected the event**, averaging about 4.49 seconds early. Other high-conversion candidates have the same retrospective property.

## Current interpretation
The missing `r8_sweep_lifecycle_screen.sweep_signals` helper remains the fault boundary. The preserved wrapper executes directly from `X[:,0]`; therefore an event generator that selected a sweep after later confirmation but stored an earlier break/reclaim timestamp would cause replay to enter before the deciding information existed.

This has enough leverage to explain the scale of the 68%→82% gap. It is **not yet proof** that the formal Gamma_2 benchmark was contaminated because the exact certified fingerprint has not been reproduced and the original helper body remains missing.

## Hard gate
Do not promote any numerical near-match obtained through retrospective scheduling. A recovered Gamma_2 implementation must:
1. derive its event semantics from historical source lineage rather than target-fitting;
2. reproduce the exact January fingerprint;
3. pass a strict no-future/no-backdating causality audit;
4. freeze source and helper code;
5. then reproduce the full Jan–Jul monthly contract.

**Next unit:** `R9B_GAMMA2_SOURCE_EQUIV_TIMESTAMP_ORIGIN_010` — January only. Recover the historical timestamp/event origin from older R8/S1 Python lineage or other durable pre-promotion artifacts. No arbitrary lag fitting. August remains sealed.