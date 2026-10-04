# DELTA R037 — PDHSR C02 Month-by-Month Validation — Checkpoint 17AF

**Status:** COMPLETE ROBUSTNESS FAIL / CANDIDATE RETIRED  
**Unit:** R037_PDHSR_C02_MONTH_BY_MONTH_VALIDATION  
**Candidate:** R037-PDHSR-C02_S5_CLOSE_RECLAIM  
**Parent:** R037_PDHSR_C02_INDEPENDENT_LATER_JAN_VALIDATION_CHECKPOINT_17AE  
**Months:** February–July 2026  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Recovery note

The foreground command transport timed out, but the producer's atomic output completed successfully. Recovery checked process state and the atomic result file before any rerun. No rerun was needed.

A pre-compute source-integrity gate also caught a one-character July SHA typo in the committed producer. No result existed from that failed attempt. The canonical July hash was verified against `DUKASCOPY_JAN_JUL_SOURCE_MANIFEST.json`, the source was corrected in commit `9d258a9fcda5f79cf9f4895d0aa43313bde4a74b`, and the local producer matched Git blob `d5a754817e95819ba867726ec0ac55c19a3f1389` exactly before official compute.

Official atomic raw-result SHA-256:
`c46262eb9e5d9ef7ea4ce1c0d48c4553230ee0834e215dca29df62ff968dea97`

## Frozen logic

No retuning and no post-hoc PDH/PDL split:
- prior UTC trading-day high/low;
- first strict PDH/PDL sweep;
- first completed S5 close reclaim;
- execution quote must still be reclaimed;
- maximum spread 25 points;
- stop 300 raw;
- trail activation 100 raw;
- trail distance 30 raw;
- maximum hold 30 seconds;
- one trade per day.

## Monthly results

| Month | Trades | Official wins | Direct net |
|---|---:|---:|---:|
| 2026-02 | 17 | 4 | -$9.14 |
| 2026-03 | 21 | 9 | -$5.35 |
| 2026-04 | 19 | 8 | -$5.02 |
| 2026-05 | 17 | 8 | -$4.15 |
| 2026-06 | 17 | 8 | -$2.69 |
| 2026-07 | 18 | 7 | -$4.12 |

Aggregate:
- **109 trades**
- **44 official wins**
- gross profit **+$12.68**
- gross loss **-$43.15**
- direct net **-$30.47**
- **0/6 nonnegative months**

## Preregistered robustness gate

- total trades >= 24: **PASS**
- nonnegative months >= 4: **FAIL**
- aggregate direct net >= $0: **FAIL**
- overall robustness: **FAIL**

## Decision

The independent later-January result was real but not robust across February–July. C02 is therefore **retired from the active promotion path without retuning**.

Do not salvage it through:
- post-hoc PDH/PDL filtering;
- side/session/weekday filtering;
- threshold retuning;
- August inspection.

Next:
`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

This negative result remains useful as a forensic clue: prior-day sweep/reclaim can produce sharp local windows, but the raw one-trade/day formulation does not generalize across months.
