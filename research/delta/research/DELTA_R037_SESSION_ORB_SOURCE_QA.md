# DELTA R037 — Session-Owned ORB Source QA

**Status:** CODE_QA_SOURCE_SCREEN_ONLY_NOT_R037_REPLAY  
**Parent control:** R032-C03_PLUS_DH02_S11_S08  
**Official integrated replay:** NOT STARTED  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Durable identities

- Producing source blob: `3c701ec52b435b907a2f7d96a143f6a4460551a6`
- Config registry blob: `cdf401d6784f4187a81a9c625d58c1c18377b2aa`
- First-confirmation freeze commit: `7dc69b30aec7583fb80faa0d5a831c3ddb8325ce`
- January source: `XAUUSD_DUKAS_2026_01_ticks.csv.gz`
- January bytes: `68,690,420`
- January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Local compact QA result SHA-256: `36dabdccc21ae2d6f68fa26bdb9bd7fbcb0e8ad9b48f8b5557d7da3046d711e3`
- Stage-A ticks loaded: `4,205,709`
- Stage-A interval: `[2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)`
- Surface: `DUKAS_COINEXX_LIKE_P75`

The January source size/hash exactly match the canonical `DUKASCOPY_JAN_JUL_SOURCE_MANIFEST.json`.

## Code QA

- Python compile: PASS
- Single-confirmation S5 right-edge smoke: PASS
- Two-consecutive-S5 confirmation smoke: PASS
- First confirmation is evaluated only when a later tick makes the completed S5 bar visible.
- No August data was loaded.

A first local smoke invocation used a dynamic import harness that did not register the temporary module in `sys.modules`, causing Python dataclasses to fail before any strategy logic executed. The normal import path was rerun immediately and passed. This was a harness-only error with no research output and no parameter change.

## Stage-A source screen

These figures measure event supply and a standalone frozen-R9 lifecycle diagnostic. They are **not** integrated R037 results because R032-C03 collision/position-blocking parity has not yet been reconstructed.

| Config | Proposals | Eligible | Distinct days | Standalone trades | Wins | Net | Max balance DD |
|---|---:|---:|---:|---:|---:|---:|---:|
| C01 London 15 | 11 | 11 | 11 | 11 | 8 | -$0.41 | $1.02 |
| C02 COMEX 15 | 11 | 10 | 11 | 10 | 4 | -$1.68 | $1.96 |
| C03 Dual 15 | 22 | 21 | 11 | 21 | 12 | -$2.09 | $2.61 |
| C04 Dual 30 | 22 | 21 | 11 | 21 | 11 | -$1.35 | $3.88 |
| C05 Dual 15 Confirm2 | 22 | 22 | 11 | 22 | 13 | -$3.14 | $3.44 |

### Rejection audit

- C02: one COMEX event consumed by `REENTERED_RANGE`.
- C04: one London event consumed by `REENTERED_RANGE`.
- No Stage-A P75 event was rejected by the 25-point spread gate.
- C01/C03/C05 had no source-level execution rejection other than the C03 inherited one COMEX re-entry.

## Interpretation

The family passes only the **event-supply / causal-source** portion of the preregistration:
- every configuration has >=8 proposals;
- every configuration spans >=4 days;
- the event source is not sample-starved;
- the frozen first-confirmation rule produces deterministic events.

The standalone PnL is intentionally not a promotion criterion. It does not account for the exact R032-C03 parent, same-tick proposal collisions, or parent-position blocking.

## Decision

**SOURCE_QA_PASS / INTEGRATED_REPLAY_BLOCKED_ON_PARENT_PARITY**

Do not tune SORB.

Next unit:
1. recover the exact R032 producing source/fixture if available;
2. if unavailable, independently reconstruct R032-C03 from canonical R025 ownership and frozen DH03-S06 / DH05-S06 / DH02-S11 / DH02-S08 definitions;
3. reproduce the authoritative R032 Stage-A controls before introducing SORB;
4. only a parity-confirmed parent may be used for official R037 integrated Stage-A replay.
