# DELTA R037 — Full R032 Specialist-Parent Parity — Checkpoint 14A

**Status:** COMPLETE SCHEDULER LOCALIZATION / FULL HISTORICAL PARENT PARITY NOT ACHIEVED  
**Unit:** R037_R032_FULL_SPECIALIST_PARENT_PARITY_RECONSTRUCTION  
**Parent:** R037_DH03_S06_SIGNAL_GENERATOR_PROVENANCE_DECISION_CHECKPOINT_13H  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**SORB integrated replay:** NOT STARTED / BLOCKED  
**MQL5:** NOT AUTHORIZED

## Timeout-safe execution

The visible ChatGPT message-delivery timeout was treated as a delivery/recovery fault, not as proof of compute failure. Live GitHub state showed that the durable research chain had already advanced through Checkpoint 13H, with one previously reconciled duplicate-write race at 13G.

Before 14A compute, DELTA gained a durable in-flight cursor, a recovery guard, a process-group-aware bounded Python runner, serialized GitHub CI concurrency, and expanded recovery artifacts. The 14A producer was committed before official replay.

Producer:
`research/delta/experiments/delta_r037_r032_full_specialist_parent_parity.py`

Producer commit:
`07734bf76b6062e3840e8e6ad3b0fc27dca63870`

Producer blob:
`f100e5274466def8fc5aebf1a994c513d80ed3c3`

Producer SHA-256:
`5a409f0f9b0b32b6c557574c06171baab47f19c8b4668392f74338a26e04666e`

The local execution bytes matched that Git blob exactly. Official replay completed exit 0 in **27.819 seconds** under the bounded runner.

Runtime result SHA-256:
`900ab0dcc0fd56fe58abb73d97a8f0fefb7804bf9ad05d9e8fc8850f5eba0eed`

## Hard control gate

Before specialist scheduling was scored, the integrated engine reproduced the exact frozen non-specialist R032 backbone:

- trades **12,504**
- raw-positive wins **5,788**
- official wins **5,723**
- gross profit **+$1,225.76**
- gross loss **-$3,797.07**
- net **-$2,571.31**

Therefore the residual below is not a backbone reconstruction failure.

## Frozen specialist surrogate fingerprints

No generator or threshold was retuned.

- DH03-S06: **1,586** signals
- DH05-S06: **651** signals
- DH02-S11: **103** signals
- DH02-S08: **104** signals

All four match their preregistered provenance-limited surrogate counts.

## Scheduler localization

Two preregistered orderings were tested:

1. SPECIALIST_FIRST_FLAT_ONLY_CONFIG_ORDER
2. BACKBONE_FIRST_FLAT_ONLY_CONFIG_ORDER

The stronger joint historical match is:

**BACKBONE_FIRST_FLAT_ONLY_CONFIG_ORDER**

This means a fresh ordinary R9 opportunity is evaluated first while flat; an independent specialist signal is admitted only if the ordinary opportunity did not open a position. Specialist positions remain owned and GLOBAL NO_REARM remains frozen for ordinary opportunities.

The scheduler localization is useful, but it does **not** produce exact historical R032 parity.

## P75 configuration results — leading scheduler

| Config | Trades actual / target | Official wins actual / target | Net actual / target | Specialist entries actual / target | Specialist net actual / target |
|---|---:|---:|---:|---:|---:|
| C00 | 13,894 / 13,779 | 6,303 / 6,286 | -$2,903.62 / -$2,826.15 | 1,928 / 1,947 | -$440.00 / -$367.51 |
| C01 | 13,964 / 13,825 | 6,329 / 6,307 | -$2,923.15 / -$2,836.26 | 2,023 / 2,012 | -$463.61 / -$376.31 |
| C02 | 13,965 / 13,822 | 6,323 / 6,310 | -$2,925.95 / -$2,832.05 | 2,024 / 2,018 | -$468.37 / -$374.75 |
| C03 | 14,034 / 13,868 | 6,349 / 6,331 | -$2,944.94 / -$2,842.16 | 2,118 / 2,083 | -$491.44 / -$383.55 |

## Ownership breakthrough

The historical ownership increments are:

- S11 increment in C01: **65**
- S08 increment in C02: **71**
- S11+S08 increment in C03: **136**

The leading reconstructed scheduler produces:

- S11 increment: **95**
- S08 increment: **96**
- combined increment: **190**

This is highly diagnostic.

C00, which contains only DH03-S06 + DH05-S06, is already close on specialist ownership:
**1,928 actual vs 1,947 historical, only 19 low**.

By contrast, the provenance-limited S11/S08 surrogates materially over-admit:
- S11: **+30** incremental specialist entries
- S08: **+25**
- combined: **+54**

That mirrors their standalone provenance limitation: both current surrogates generate roughly 103–104 trades instead of the historical 75-trade standalone fixtures.

## Residual ordinary-parent clue

The leading scheduler's ordinary-entry counts are:

- C00: 11,966
- C01: 11,941
- C02: 11,941
- C03: 11,916

Historical total trades minus historical specialist entries imply ordinary-parent counts near:

- C00: 11,832
- C01: 11,813
- C02: 11,804
- C03: 11,785

The reconstructed ordinary population is therefore roughly **+128 to +137 high across all four configurations**.

Because the no-specialist backbone is exact, this stable excess can only arise after specialist timing/ownership is introduced. Scheduler order alone cannot repair it: both tested scheduler orders produce the same total trade counts. The residual is therefore localized to missing historical specialist timing/ownership provenance rather than the base R025 state machine.

## Decision

**Checkpoint 14A = QA PASS / SCHEDULER LOCALIZED / FULL PARENT PARITY FAIL.**

Carry forward:
- exact non-specialist R032 backbone;
- provenance-limited frozen specialist surrogates;
- BACKBONE_FIRST_FLAT_ONLY_CONFIG_ORDER as the leading scheduler interpretation.

Do not:
- retune specialist thresholds;
- manufacture 75-trade filters for S11/S08;
- claim exact R032-C03 historical parity;
- start official SORB integration;
- access August;
- begin MQL5.

Compact checkpoint:
`research/delta/reference/DELTA_R037_R032_FULL_SPECIALIST_PARENT_PARITY_CHECKPOINT_14A.json`

## Next bounded unit

`R037_R032_SPECIALIST_PARENT_RESIDUAL_PROVENANCE_AND_SORB_READINESS_DECISION`

Purpose: decide, from the now-localized integrated residual and prior provenance freezes, whether any reconstructible historical ownership semantic remains testable without overfitting; otherwise preserve the provenance-limited parent, keep official SORB integration blocked, and route research into a separately labeled non-promoting surrogate-parent path rather than falsifying historical parity.
