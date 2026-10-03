# DELTA R037 — DH02-S08 Parent-Context Placement — Checkpoint 12B

**Status:** COMPLETE CONTEXT-PLACEMENT LOCALIZATION / FULL PARITY NOT ACHIEVED  
**Unit:** R037_DH02_S08_STATE_FUNNEL_AND_PROVENANCE_LOCALIZATION  
**Parent:** R037_DH02_S08_CLEANROOM_PARITY_CHECKPOINT_12A  
**Vector:** DH02-S08 / `7c70b5304ff7`  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Bounded question

Could the remaining S08 population mismatch be caused primarily by where the already-frozen DH01 parent-direction condition is applied during the DH02 event lifecycle?

No numeric parameter changed. 12B changes only parent-context placement.

## Crash-safe control

12B imports the committed 12A producer as a verified helper. Before accepting any result it requires exact reproduction of the 12A leading signal fingerprint:

- signal SHA-256: `0f64c1f727c9fef6f9ee3676b1aa8d8a3df874b5a1c381d4a3bd6e6fe8657841`
- trades: **105**
- raw-positive wins: **37**
- GP: **+8.75**
- GL: **-37.73**
- net: **-28.98**

That control reproduced exactly.

Producer:
`research/delta/experiments/delta_r037_dh02_s08_context_placement_parity.py`

Producer commit:
`a2bb9c1a321c0edb8de4390c40911e32e9206d13`

Producer blob:
`1abb2f9078f995a2bd12e9d5a4c0d7e37f9082c1`

Producer SHA-256:
`cccd58263dc0a8988f8cfd992b6a93c74fdbbcbfc0f575b9b86b9e1d0ee4db6f`

Evidence commit:
`28eae44224d4251851cb9c0991d17b22627f5210`

Evidence blob:
`7465882cb0bf90633c55d4cadde43ebc9132f570`

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**

Official bounded replay completed in **14.46 seconds** under a hard 120-second process limit, unbuffered Python, faulthandler, and isolated Numba cache.

Official result SHA-256:

`48819841756342315c10c5a16e0f8c558b7f893b5cd43448bb0bab1e444596af`

## Profiles

| Context placement | Trades | Raw wins | GP | GL | Net | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| Historical target | **75** | **42** | **+9.93** | **-18.82** | **-8.89** | **9.66** |
| Break + rebreak control | 105 | 37 | +8.75 | -37.73 | -28.98 | 29.08 |
| Break only | 107 | 37 | +8.75 | -38.80 | -30.05 | 30.15 |
| **Rebreak only** | **104** | **37** | **+8.75** | **-37.21** | **-28.46** | **28.56** |
| Continuous active context | 105 | 37 | +8.75 | -37.73 | -28.98 | 29.08 |

The best profile is `REBREAK_ONLY`, but the improvement is trivial relative to the historical gap.

## Key localization

Every bounded context-placement interpretation retains only **37 winners**.

The historical S08 fixture contains **42 winners**.

Therefore context placement is not the missing mechanism. Moving the same parent-direction condition between break/rebreak/continuous lifecycle can alter a few losing events but **does not recover the missing historical winner population**.

The historical R032 ownership ledger supplies an independent later-stage fingerprint:

- C00 specialist entries: 1,947
- C02 (+S08): 2,018
- incremental S08 ownership: **71**
- C01 (+S11): 2,012
- C03 (+S11+S08): 2,083
- incremental S08 ownership with S11 present: **71**

That 71-entry ownership increment should be preserved for later integrated parity, but it does not justify fitting the standalone 12B population.

## Decision

**Checkpoint 12B = context-placement branch rejected as the residual explanation.**

Do not:
- retune S08 thresholds;
- keep permuting break/rebreak placement;
- invent parent-direction thresholds;
- claim `REBREAK_ONLY` is historical truth.

The residual now points to the exact historical definition of **DH01 parent direction / context aggregation**, whose producing bytes were not preserved.

## Next bounded unit

`R037_DH02_S08_PARENT_DIRECTION_PROVENANCE_DECISION`

Determine whether surviving DH01/DH02 material independently encodes an exact S08 parent-direction algorithm. If it does not, freeze the best source-compatible S08 surrogate as non-promoting and move to DH03-S06 rather than fitting more same-sample context variants.
