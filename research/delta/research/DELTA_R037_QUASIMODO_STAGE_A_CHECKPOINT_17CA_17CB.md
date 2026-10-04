# DELTA R037 — Source-Default Quasimodo Stage-A Screen — Checkpoint 17CA–17CB

**Status:** COMPLETE / NO STAGE-A SURVIVOR  
**Family:** R037-QM-v1  
**Parent:** R037_SWEEP_IFVG_INDEPENDENT_LATER_JAN_VALIDATION_CHECKPOINT_17BZ  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Source basis

The entry grammar was reconstructed from MetaQuotes' July 2026 Part-49 Quasimodo article rather than from retrospective chart interpretation.

Frozen source defaults:
- swing pivot lookback: 5 bars each side;
- alternating zig-zag, merging same-type pivots to the more extreme pivot;
- bearish QM: H-L-H-L with Head > Shoulder and final low < Leg; bullish mirror;
- skip shared left shoulder;
- require prior trend with TrendPivots=2;
- QM entry line at the left shoulder;
- EntryBufferPoints=0;
- WaitForRejectionClose=false;
- MaxWaitBars=30;
- close beyond the Head invalidates.

M5 and M15 were fixed as DELTA screening lanes before compute. Source EA stop/TP/risk logic was not imported; entries were evaluated using the same frozen DELTA P75 30-second execution economics used across R037.

Prereg commit: `15155390a68b3e3eb53147737f735b34083d0030`

Producer commit: `16c22423a84902b6560078191220cd129b9c6646`

Producer blob: `67650280824c36c280d3596714c2b68161fe05f4`

Producer SHA-256: `8d5b88dd408680fd60a93f7a6a9060346ad87bcc2e30d24c4c906f575b2f4fed`

Official result SHA-256: `113775153bcc7975ecf2c2a17fee7a54c23d9e5664417f65b557f292054921c1`

The exact committed producer blob was verified locally and executed under the crash-contained 120-second runner. Runtime was approximately 5.5 seconds.

## Results

| Lane | Trades | Days | Wins | Net | Gate |
|---|---:|---:|---:|---:|---|
| 17CA M5 | 6 | 3 | 4 | **+$0.41** | FAIL — supply |
| 17CB M15 | 1 | 1 | 0 | **-$0.76** | FAIL |

M5 produced a small positive sample but failed both the minimum-20-trade and minimum-5-day activity gates. It is therefore not an acceptable DELTA candidate.

## Interpretation

Quasimodo's multi-leg geometry improved apparent selectivity/quality, but the MetaQuotes source-default structure is too sparse for the Gold MUWHAHA Miner activity requirement. This is not grounds to weaken the activity gate or tune swing lookback/rejection settings after seeing the result.

## Decision

**RETIRE R037-QM-v1 SOURCE-DEFAULT PATH.**

Do not rescue through:
- reduced swing lookback;
- longer wait window;
- rejection-toggle changes;
- session/side filtering;
- M1 substitution;
- exit tuning;
- August.

Next:
`R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST`
