# DELTA R037 — Sweep / CISD / FVG / Retrace Stage-A Screen — Checkpoint 17AH

**Status:** COMPLETE / FAMILY RETIRED / NO RETUNE  
**Unit:** R037_SWEEP_CISD_FVG_RETRACE_STAGE_A_SCREEN  
**Parent:** R037_PRN_STAGE_A_SCREEN_CHECKPOINT_17AG  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Question

Can a fully causal liquidity sequence — confirmed S5 swing sweep, completed-bar CISD/state shift, post-sweep FVG, then retrace/rejection — remove enough naked-sweep noise to create viable 30-second XAUUSD economics?

The logic was preregistered before official compute and reconstructed only from public/reproducible rules.

## Integrity

Preregistration commit:
`9e6e204e2fbf657a5cf3729e919b2ec25fa86c94`

Producer:
`research/delta/experiments/delta_r037_scfr_stage_a_17ah.py`

Producer commit:
`0b34e4b28566d3976ba888d992f5ebb333a21837`

Producer blob:
`a4f65ba5d89fb27b559b277e5746515f2666a8fd`

Producer SHA-256:
`b20df5826f380b20927f60202838b2ff70d3b073e72f13045791db3434027271`

Canonical January source SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**

Official raw-result SHA-256:
`1d7958a7512d99dc76b82da83634db0e360d954a8e027707d6ea32f74163f51e`

## Funnel

- confirmed-swing sweeps: **8,141**
- CISD/state shifts: **7,500**
- qualifying post-sweep FVGs: **3,137**
- causal retrace/rejection executions: **947**

The sequence removes a large amount of raw sweep noise, but not enough.

## Economics

- proposals: **964**
- eligible: **947**
- trades: **947**
- distinct days: **14**
- official wins: **431**
- gross profit: **+$97.46**
- gross loss: **-$285.20**
- direct net: **-$187.74**
- STOP exits: **907**
- MAX_HOLD exits: **40**

Activity gates pass. The preregistered direct-net gate fails decisively.

## Scientific interpretation

17AH is materially stricter than naked sweep/reclaim families, but the **S5-local liquidity pool itself remains too dense**. The failure therefore does not justify tuning CISD windows, FVG size, retrace depth, sessions, sides, or exits after seeing the result.

The next independent source should change the causal anchor rather than refine 17AH numerically: use a naturally sparse higher-order liquidity reference and then apply lower-timeframe displacement/retest confirmation.

## Decision

**RETIRE R037-SCFR-v1 WITHOUT RETUNING.**

Do not rescue through:
- post-hoc CISD/FVG timing changes;
- minimum FVG-size fitting;
- side/session/weekday filtering;
- exit tuning;
- August inspection;
- MQL5.

Next:
`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

Search bias:
**higher-order sparse liquidity anchor -> sweep -> causal displacement/state shift -> retrace**, with sufficient natural event supply.
