# DELTA R037 — DH05 Probe-Attempt Counter Provenance Decision — Checkpoint 10F

**Status:** COMPLETE PROVENANCE-LIMITATION FREEZE  
**Unit:** R037_DH05_PROBE_RESIDUAL_ATTEMPT_COUNTER_PROVENANCE_DECISION  
**Parent:** R037_DH05_PROBE_ATTEMPT_TOUCH_RESET_CHECKPOINT_10E  
**Surface:** provenance-only / no raw-tick access  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Question

After Checkpoints 10D and 10E causally bracketed universal probe-attempt opening/reset semantics around the 09Z reconstruction, does any independent surviving historical source justify another universal DH05 attempt-counter rule?

No market data, thresholds, ownership router, acceptance, failure, reversal, execution rule, or frozen vector was changed.

## Independent evidence

The surviving original DH-05 white paper defines:

- PROBE as midpoint trading beyond the boundary in the original break direction;
- ProbeAge as elapsed time since the first cross;
- a single causal PROBE branch that routes either to BREAK_ACCEPTED or FAILURE_CANDIDATE;
- expired probes to EXPIRED.

It does **not** document an explicit repeated same-boundary attempt counter, boundary-touch reset, or strict-prebreak reset rule.

The preserved R003 white-paper summary, R006 result report, and R032 authoritative basket report preserve the DH05 state grammar and historical fixture, but none independently encode an exact repeated-attempt counter/reset implementation.

Checkpoint 09A already established that the authoritative historical producer bytes were not recovered after GitHub, Drive, Library, and runtime-cache searches.

## Causal bracket

09Z remains the strongest reconstructible non-promoting surrogate:

- probe absolute error: **449**
- total funnel absolute error: **782**
- aggregate trade-count absolute error: **335**
- promoted: **NO**

Checkpoint 10D tested stricter attempt opening. Every strict-beyond candidate worsened probe parity.

Checkpoint 10E tested looser boundary-touch attempt completion/rearm. Every candidate worsened probe parity and triggered the S06 veto.

Therefore the surviving evidence brackets the contact edge but does not identify the missing historical helper's exact counter implementation.

## Decision

**Do not run another same-sample universal attempt-counter recut.**

Freeze the 09Z attempt counter as the strongest reconstructible **non-promoting** DH05 surrogate.

Record the remaining **449-probe absolute error** as a historical-source/provenance limitation.

Do **not** claim exact historical DH05 parity.

This is a deliberate anti-overfit stop: another semantic selected only because it reduces the preserved six-vector residual would be retrospective fitting, not source reconstruction.

## Crash / timeout safety

The 10F producer and its compact provenance-evidence ledger were committed before official execution.

The official decision used exact committed blobs:

- producer commit: `f38608af271c39c5ab5981113c9e772ff3c4cc04`
- producer blob: `38c0010a6ccc910afa167679639d1a3736db589a`
- evidence commit: `29fdac465320d92f40c4b580f0e9e5edf9f23e9c`
- evidence blob: `d65b2cca32fa386b11ef3c153bf44374d04d81aa`
- hardened bounded runner blob: `a78a8fe7550bd02433ce8a7d3fdae563fcd953e8`

The container's direct raw-GitHub DNS path was unavailable during preparation. No scientific producer ran during that failed download attempt and no result was written. The official unit therefore used connector-fetched committed bytes, verified by Git blob identity before execution.

Official result SHA-256:
`d4add41152a75982eb6b21c987fbb7767a3390821550855a47f351a0901ca47b`

## Disposition

DH05 stream status:

`PROVENANCE_LIMITED_BEST_RECONSTRUCTION_09Z_NON_PROMOTING`

This preserves the useful reconstructed specialist without falsely manufacturing missing historical semantics.

## Next bounded unit

`R037_DH02_S11_CLEANROOM_PARITY_RECONSTRUCTION`

Reconstruct the next frozen R032 specialist stream from its original white-paper grammar, immutable vector, preserved historical fixture, and canonical Stage-A tick surface. No threshold tuning.
