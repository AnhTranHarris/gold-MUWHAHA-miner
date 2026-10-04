# DELTA R037 — Sweep IFVG M5 Independent Later-January Validation — Checkpoint 17BZ

**Status:** COMPLETE / INDEPENDENT HOLDOUT FAIL / FAMILY RETIRED  
**Candidate:** 17BY_M5_SWEEP_IFVG_RETEST  
**Parent:** R037_SWEEP_IFVG_RETEST_STAGE_A_SCREEN_CHECKPOINT_17BX_17BY  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Validation contract

The Stage-A M5 survivor was replayed unchanged on later-January entries.

- warmup start: 2026-01-14 00:00 UTC
- economics start: 2026-01-18 12:00 UTC
- end exclusive: 2026-02-01 00:00 UTC
- warmup may establish eligible confirmed swings only
- no sweep/event sequence may originate before the economics start
- no parameter, session, side, weekday, gap-size, lifecycle, stop, trail or exit changes

Preregistration:
`research/delta/reference/DELTA_R037_SWEEP_IFVG_LATER_JAN_PREREG_17BZ.json`

Prereg commit:
`49191b02efcd60df5cceec67ad434d0cce649c87`

Producer:
`research/delta/experiments/delta_r037_sweep_ifvg_later_jan_17bz.py`

Producer commit:
`417a25888204f00188a7673e7e32f46bf926e753`

Producer blob:
`f76872542d0261e6eb7c3431ba6f43abdcf982ca`

Producer SHA-256:
`ab8e2e295434793a6e4bb5dcab46f3389c5ca6abab0c29dd789b2a0bc5a36bc1`

Official result SHA-256:
`9723855c9a07b65847a625dc0b49270cba977e3ef0b29de0270808f5e95d4bb8`

The exact committed producer blob was verified locally before execution. The replay used the crash-contained 120-second runner and completed normally in approximately 5.7 seconds.

## Holdout result

- proposals: **27**
- trades: **27**
- distinct days: **10**
- long / short: **21 / 6**
- official wins: **9**
- gross profit: **+$4.73**
- gross loss: **-$11.76**
- direct net: **-$7.30**

Supply gates all passed; the economics gate failed.

Stage-A had produced 24 trades / 10 days / 17 wins / +$1.35. The later-January result therefore rejects the hypothesis that the unchanged M5 sequence has stable positive 30-second expectancy.

## Decision

**RETIRE R037-SIFVG-v1 FROM THE ACTIVE PROMOTION PATH.**

Do not rescue with:
- M1;
- session/side/weekday filters;
- gap-size changes;
- lifecycle-window changes;
- exit/stop/trail tuning;
- August.

The result remains useful as a high-information negative: adding a displacement-gap inversion/retest sequence improved Stage-A selectivity enough to create a positive sample, but the edge did not persist independently.

## Next

`R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST`

Resume the completed R037 meta-harvest and select a materially distinct, source-grounded mechanism. Prefer designs with naturally selective event context and independent evidence; do not return to retired generic VWAP/profile/Fibonacci/sweep-IFVG rescue paths.
