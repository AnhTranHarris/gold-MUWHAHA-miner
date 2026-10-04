# DELTA R037 — Rolling Liquidity Sweep Follow-Through Guard Stage-A — Checkpoint 17AO

**Status:** COMPLETE / NO SCREEN SURVIVOR / FAMILY RETIRED WITHOUT RETUNING  
**Family:** R037-RLSFG-v1  
**Parent:** R037_VSBR_STAGE_A_SCREEN_CHECKPOINT_17AN  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Reconstructed source logic

This unit tested a fully disclosed rolling-liquidity sweep/follow-through grammar:
- highest high / lowest low of previous 20 completed bars;
- sweep depth at least 0.10 previous-bar ATR20;
- close back inside the frozen level;
- rejection-side wick at least 35% of sweep-bar range;
- next two closes remain on the reclaimed side;
- reversal extension at least 0.30 frozen ATR;
- directional progress / cumulative close path at least 45%;
- entry at first P75 tick after the second confirmation bar.

M1 and M5 were preregistered. No threshold sweep or rescue filter was permitted.

## Integrity

Prereg commit: `b13e98eccf79d4394a6e47f7c79a073ec0b66727`

Producer:
`research/delta/experiments/delta_r037_rlsfg_stage_a_17ao.py`

Producer commit:
`819638dcb2a9fd47e2251ce0aec3a987930e1df4`

Producer blob:
`0943415d608187b626c60a70cbb2b8585638d095`

Producer file SHA-256:
`1d592a367a404b46039f171909b61712d05ad44b63424763bb48c998c72e515a`

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**

Official result SHA-256:
`fb9cb6a8464d76b5843ec3182a4169053f341accb6b5fb9511cb56bb27913c6d`

A transfer-copy corruption was rejected before official compute. The executable was not run until it matched the committed Git blob exactly and compiled successfully.

## Results

| Profile | Sweep candidates | Confirmations | Trades | Days | Wins | Net |
|---|---:|---:|---:|---:|---:|---:|
| C01_M1 | 729 | 238 | 238 | 13 | 91 | **-$61.40** |
| C02_M5 | 160 | 50 | 50 | 11 | 27 | **-$6.17** |

The structural filters materially reduced raw sweep events, but the confirmed entries still failed the preregistered economic floor.

C01 exit distribution: 230 stop / 8 max-hold.  
C02 exit distribution: 49 stop / 1 max-hold.

## Decision

**RETIRE R037-RLSFG-v1 WITHOUT RETUNING.**

The failure is not signal scarcity. Both profiles provide adequate density and multi-day coverage but remain economically negative under the frozen 30-second lifecycle.

Do not:
- change 20-bar lookback;
- change 0.10 ATR pierce;
- change 35% wick rejection;
- change 0.30 ATR extension;
- change 45% path efficiency;
- add session/weekday/side filters;
- tune exits;
- access August;
- begin MQL5.

Next:
`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`
