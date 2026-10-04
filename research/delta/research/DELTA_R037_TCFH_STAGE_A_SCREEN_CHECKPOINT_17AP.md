# DELTA R037 — Tick-Count Flow Hysteresis Stage-A Screen — Checkpoint 17AP

**Status:** COMPLETE / FAMILY RETIRED / NO RETUNE  
**Unit:** R037_TICK_COUNT_FLOW_HYSTERESIS_STAGE_A_SCREEN  
**Parent durable checkpoint:** R037_RLSFG_STAGE_A_SCREEN_CHECKPOINT_17AO  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Source-grounded question

Can a broker-portable tick-count directional-flow proxy, using MetaQuotes' published default 30-second window, +/-0.30 flow trigger, 0.80 hysteresis reset and 2-second decision cadence, create a viable short-horizon XAUUSD entry source under the frozen DELTA execution lifecycle?

Public reconstruction basis:
- MetaQuotes/MQL5 article: *Price Action Analysis Toolkit Development (Part 38): Tick Buffer VWAP and Short-Window Imbalance Engine*.
- Formula: `(upticks - downticks) / (upticks + downticks)`.
- This is explicitly treated as a tick-count pressure proxy, **not** true exchange order-flow imbalance or DOM.

No threshold search, session filter, side filter, exit tuning, August access or MQL5 build was used.

## Integrity

Preregistration:
`research/delta/reference/DELTA_R037_TCFH_STAGE_A_PREREG_17AP.json`

Prereg commit:
`3e61506898ca72ebc537e99029176f238187aaa0`

Producer:
`research/delta/experiments/delta_r037_tcfh_stage_a_17ap.py`

Producer commit:
`d42f125b5dde1fc2313a6b8f1123470b6436212e`

Producer blob:
`2a5d8f4c9bc21d1be5b7a52ec5bfb2eb25ca84e5`

Producer SHA-256:
`e8f4ac9120c66481062de27a8dc01b725dcd2fad0df167817b3f9afa3078d783`

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**

The exact committed Git blob was verified locally before official compute. The official producer was compiled, executed under a 120-second hard timeout, and wrote output atomically using a temporary file + flush + fsync + os.replace.

Official raw result SHA-256:
`5b2da282a6218951ff8d063d05a086362f8f241c4613eb46b302dcdfdf0b089c`

## Official Stage-A result

Published-default flow generated:
- **1,707** eligible proposals
- **1,598** non-overlapping trades
- **14** distinct days
- **799 long / 799 short**
- **677** official wins
- gross profit **+$156.70**
- gross loss **-$488.69**
- direct net **-$331.99**
- STOP exits **1,445**
- MAX_HOLD exits **153**

Activity supply is more than adequate, but the economic gate fails decisively.

## Interpretation

This family answers an important microstructure question: raw short-window directional tick pressure is **not selective enough** for the frozen 30-second XAUUSD lifecycle. The failure is not caused by insufficient events. It is caused by poor post-trigger continuation quality after spread and commission.

The result also argues against spending a refinement cycle merely changing the flow threshold or lookback after seeing the loss. That would be a classic rescue sweep, and the family missed the economic floor by far too much.

## Decision

**RETIRE R037-TCFH-v1 WITHOUT RETUNING.**

Do not rescue with:
- 10/20/60-second window sweeps;
- threshold or hysteresis fitting;
- side/session/weekday filters;
- VWAP/EMA/RSI add-ons after the result;
- exit tuning;
- August inspection;
- MQL5.

The next family should remain structurally independent and should add information not already represented by recent range/sweep/volatility/tick-flow families.

**Next:** `R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`.
