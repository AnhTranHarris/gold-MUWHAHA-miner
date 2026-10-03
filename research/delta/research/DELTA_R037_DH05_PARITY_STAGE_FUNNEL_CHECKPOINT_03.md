# DELTA R037 — DH05 Parity Stage-Funnel Diagnostic — Checkpoint 03

**Status:** COMPLETE BOUNDED QA / PARITY STILL BLOCKED  
**Parent:** R032-C03_PLUS_DH02_S11_S08  
**Prior checkpoint:** DELTA_R037_DH05_S06_PARITY_CHECKPOINT_02  
**Unit:** R037_DH05_PARITY_STAGE_FUNNEL_DIAGNOSTIC_M5_SWING_SIX_VECTOR  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Window:** Stage-A [2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose

Instrument the frozen six-vector M5-swing DH05 family under the strongest currently reconstructible causal state machine and identify the stage at which the clean-room implementation diverges from the historical R006 fixture. This is a diagnostic only; no frozen numeric parameter is retuned and no R037-SORB integration is run.

## Source/QC

- January canonical Dukascopy source SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`.
- Stage-A P75 input rows: **4,205,709**.
- M5 ATR normalization remains fixed from Checkpoint 01.
- Causal same-boundary re-eligibility remains fixed from Checkpoint 01.
- Separate probe and failure clocks remain fixed from Checkpoint 02.
- Qualified-but-unaccepted probes may transition to failure candidate under the bounded Checkpoint-02 interpretation.
- No future-confirmed pivot is introduced.
- No August data is loaded.

## Funnel invariants

For every vector the diagnostic satisfies:

`PROBE >= QUALIFIED >= FAILURE_CANDIDATE >= REENTRY >= RECLAIM >= REVERSAL >= SIGNAL >= TRADE`

with accepted original breaks routed away from DH05. Counts are nonnegative and chronological. No duplicate writer or restarted completed R037 unit was used.

## Historical executed-trade fingerprint

| Vector | Historical trades |
|---|---:|
| DH05-A03 | 306 |
| DH05-S05 | 51 |
| DH05-S06 | 615 |
| DH05-S09 | 119 |
| DH05-S10 | 206 |
| DH05-S16 | 24 |

## Current stage funnel

| Vector | Probe | Qualified | Accepted | Failure | Reentry | Reclaim | Reversal/Signal | Trades | Wins | Net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A03 | 6,731 | 1,009 | 207 | 797 | 432 | 266 | 187 | 187 | 79 | -$43.03 |
| S05 | 7,875 | 318 | 28 | 290 | 51 | 15 | 9 | 9 | 5 | -$1.25 |
| S06 | 3,470 | 1,606 | 245 | 1,358 | 1,211 | 683 | 617 | 617 | 258 | -$152.88 |
| S09 | 7,748 | 208 | 40 | 168 | 61 | 40 | 9 | 9 | 6 | -$0.61 |
| S10 | 6,496 | 1,316 | 202 | 1,106 | 623 | 294 | **206** | **206** | 90 | -$46.87 |
| S16 | 7,870 | 135 | 43 | 92 | 37 | 18 | 8 | 8 | 3 | -$2.60 |

## QA interpretation

The stage funnel materially narrows the remaining reconstruction error.

1. **Probe supply is not the universal bottleneck.** Every frozen vector has thousands of causal boundary probes.
2. **S05/S09 collapse after a valid failure population already exists.** S05 has 290 failure candidates but only 51 reentries, 15 reclaims and 9 reversals; S09 has 168 failures but only 61 reentries, 40 reclaims and 9 reversals.
3. **S10 exactly reproduces its historical trade density: 206 trades.** This independently supports the repaired separate-clock chronology.
4. **S06 is nearly exact on trade density (617 vs 615), but not on economics.** Historical S06 is 307 wins / -$101.08; this diagnostic is 258 wins / -$152.88. Density agreement therefore is not parity.
5. **A03 and S16 remain too sparse.**
6. In this standalone diagnostic, executable signals and trades are identical. The historical authoritative S06 fixture is **672 generator signals -> 615 executed trades**. Therefore the historical generator/execution contract contains an additional causal admission/overlap/position-state distinction that is not yet reconstructed. It must not be replaced by the already-rejected full R9 S1 quality gate.

## Decision

The funnel diagnostic is **QA PASS as a localization experiment** and **parity FAIL as a historical reconstruction**.

The remaining high-value mismatch is localized to:
- causal REENTRY/RECLAIM semantics;
- reversal displacement/efficiency measurement after reclaim;
- and the separate generator-signal -> executable-trade admission/overlap contract.

Do not retune the frozen DH05 vectors. Do not reopen ATR substitution, permanent-boundary consumption, full-R9 S1 quality gating, or future-confirmed pivots.

## Next bounded unit

`R037_DH05_PARITY_REENTRY_RECLAIM_REVERSAL_FEATURE_SEMANTICS_FINGERPRINT`

Required scope:
1. keep M5 ATR, same-boundary re-eligibility and separate clocks fixed;
2. test only reconstructible causal meanings of REENTRY, RECLAIM_CONFIRMED, reversal displacement and reversal efficiency;
3. use all six M5-swing vectors as the fingerprint;
4. stage-count every candidate before economics;
5. separately instrument generator signals versus executable trades;
6. stop as soon as one semantic layer is falsified or a family-level parity candidate is found;
7. do not run R037-SORB integration until exact DH05-S06 parity passes.

## Durable diagnostic hashes

- stage-funnel source SHA-256: `127ac5ea402d0b52a659c29be46b676549b6d8a060ac25045afe31d0570c324b`
- stage-funnel output SHA-256: `b43ee892ef5e71a4ed6b5fb03119288ed74bee949109227c84d003bd712a2d25`

These hashes identify the bounded QA diagnostic; they are not a promotion artifact.
