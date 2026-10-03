# DELTA R037 — DH02-S08 Clean-Room Parity — Checkpoint 12A

**Status:** COMPLETE CLEAN-ROOM PARITY FAIL / RESIDUAL LOCALIZED  
**Unit:** R037_DH02_S08_CLEANROOM_PARITY_RECONSTRUCTION  
**Parent:** R037_DH02_S11_FAILURE_STATE_MEMORY_PROVENANCE_DECISION_CHECKPOINT_11G  
**Vector:** DH02-S08 / `7c70b5304ff7`  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Question

Can the frozen DH02-S08 historical specialist be reconstructed from the original DH02 grammar, immutable S08 vector, fixed DH01-A02 context, canonical January P75 ticks, and frozen R9 downstream lifecycle without changing any numeric parameter?

## Frozen vector

- boundary source: M1 swing
- swing confirmation width: 2 from fixed DH01-A02
- break TF: completed S5
- BreakNorm minimum: 0.2233 ATR_S15
- acceptance dwell: 1 second
- failure acceptance: tick persistence
- maximum event age: 62.9664 s
- maximum retest age: 40.7704 s
- parent context: DH01 parent direction
- penetration buffer: 0.1271 ATR_S15
- rebreak TF: completed S1
- rebreak displacement: 0.153 ATR_S15
- rebreak efficiency: 0.6977
- retest half-width: 0.0675 ATR_S15

Historical Stage-A target:

**75 trades / 42 raw-positive wins / GP +9.93 / GL -18.82 / net -8.89 / max balance DD 9.66**

## Source-grounded ambiguity set

The producer tested only reconstructible categorical interpretations:

1. no-context continuous-dwell diagnostic;
2. raw M15/M30/H1 parent-majority direction + continuous 1-second dwell;
3. DH01-A02 hysteretic parent direction + continuous dwell;
4. DH01-A02 hysteretic parent direction + event-age/current-side dwell diagnostic.

No numeric parameter was retuned. The failure-persistence helper remained the same explicit two-adverse-tick clean-room surrogate already provenance-limited by S11/11G.

## Official replay

Producer:
`research/delta/experiments/delta_r037_dh02_s08_cleanroom_parity.py`

Producer commit:
`537ebafe35a6b4a023922bf63d44e1ec2e2e2b5d`

Producer blob:
`dcfca2f1ae61e45783de1bedc982d5434026dc29`

Producer file SHA-256:
`b5675413a094c36a619485fe299f59aa7840fc34f8c12b437fbcf0af71a26e26`

Evidence commit:
`dcfe13e175f96f2fdfa0ae2535c3d7fb7d5b64c9`

Evidence blob:
`12280df31b227e0037bc8bb718ce3aaa4d75505c`

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**

The committed producer/evidence Git blob IDs were reproduced locally before execution. The replay ran with a hard 120-second process limit, isolated Numba cache, `PYTHONFAULTHANDLER=1`, and unbuffered output. It completed successfully in approximately **15.3 seconds**.

Official result SHA-256:

`641f291af528d7d0aa023cd0a473c23877f3df2fa700be6392dcac57decf6b23`

## Results

| Profile | Trades | Raw wins | GP | GL | Net | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| Historical target | **75** | **42** | **+9.93** | **-18.82** | **-8.89** | **9.66** |
| Raw parent + continuous dwell | **105** | **37** | +8.75 | -37.73 | -28.98 | 29.08 |
| Hysteretic parent + continuous dwell | 169 | 70 | +16.03 | -54.37 | -38.34 | 38.69 |
| Hysteretic parent + event-age dwell | 172 | 72 | +16.55 | -54.91 | -38.36 | 38.71 |
| No context diagnostic | 358 | 168 | +33.71 | -106.11 | -72.40 | 72.56 |

The leading reconstruction is:

`RAW_PARENT_DIRECTION_CONTINUOUS_DWELL`

Its funnel is:

- breaks: 546
- accepted: 510
- retests: 313
- failed: 240
- expired: 201
- signals/trades: 105
- dwell resets: 50
- failure-pending starts/resets/confirms: 284 / 79 / 204

## Localization

This is **not** a simple overpopulation problem.

The leading reconstruction has **30 excess trades** but also only **37 winners versus the historical 42**. Therefore a merely stricter filter cannot reconstruct the preserved population: the current clean-room semantics are both admitting wrong events and excluding at least five historical winners.

The hysteretic parent reconstruction increases activity to 169 trades and is materially farther from the historical fixture. The event-age dwell diagnostic adds three more trades and is also worse. This strongly favors the literal **continuous breakout-side 1-second dwell** over the event-age interpretation.

The remaining mismatch is therefore concentrated in **event/context ownership and stage-transition population identity**, not in the frozen numeric vector.

## Decision

**Checkpoint 12A = bounded QA complete / historical parity fail / useful localization.**

Carry forward:
- M1 width-2 causal swing boundary;
- completed-S5 break;
- literal continuous one-second breakout-side dwell as the leading acceptance interpretation;
- frozen S08 numeric vector;
- raw parent-direction profile as the current closest clean-room context surrogate.

Do **not** claim the raw-parent implementation as historical truth.

Do **not** retune thresholds.

## Next bounded unit

`R037_DH02_S08_STATE_FUNNEL_AND_PROVENANCE_LOCALIZATION`

The next unit must determine which source-supported event/context ownership semantics can replace the wrong 105-trade population with the preserved 75/42 population. It must not simply delete trades until the count matches.
