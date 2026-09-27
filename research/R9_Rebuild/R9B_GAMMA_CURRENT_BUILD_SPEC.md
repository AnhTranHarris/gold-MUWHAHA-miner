# R9B GAMMA — FULL CURRENT BUILD SPECIFICATION

## Canonical identity

Canonical build ID: `R9B_Gamma_2_Structure_Aware_Sweep_Reclaim`

Role: current formal profitable high-density Gamma build used by the current Dukascopy ROI report.

This file is a build/reproduction specification, not a research handoff. It describes only the currently certified Gamma_2 build, its immutable inputs/results, the exact known implementation semantics, the source-equivalence blocker that remains unresolved, and the rules a fresh chat must follow before translating the build into MT5.

Current formal result commit: `e32ddfd25cfd412188376732d8dc61bf0ac71ea3`

Current formal whitepaper commit: `22facb69e4efa01a4459cad8d901b8953bcc64be`

Formal result path:
`research/R9_Rebuild/results/R9B_Gamma_2_Structure_Aware_Sweep_Reclaim.json`

Formal whitepaper path:
`research/R9_Rebuild/whitepapers/R9B_Gamma_2_Structure_Aware_Sweep_Reclaim_WHITEPAPER.md`

ROI Google Doc:
`https://docs.google.com/document/d/1Pv4ydRjg1Iek7e_JIuwlFSH5FdJMxMOe_9ci5-wneDA/edit`

## Non-negotiable truth about reproducibility

The formal Jan-Jul Gamma_2 result is certified and durable. However, the original runtime helper(s) that generated the exact promoted event population were not preserved in GitHub. Later source-equivalence reconstruction using the public shorthand formula produced approximately 68% winners rather than the certified approximately 82%.

Therefore:

1. The metrics below are the authoritative Gamma_2 result contract.
2. The R8 event/lifecycle mechanics below are authoritative source lineage.
3. The five-scale lifecycle rule below is authoritative.
4. Some exact event-population/source-helper semantics remain unresolved.
5. A fresh chat MUST NOT claim it has reproduced Gamma_2 merely because it implemented this document's public state-machine shorthand.
6. Before an MT5 EA is built, the fresh Python implementation must first reproduce the January equivalence target exactly, then the complete Jan-Jul monthly table.
7. If it does not, stop and resume source-equivalence archaeology. Do not tune parameters toward the target and call that reproduction.

This warning is part of the current build specification.

## Canonical data corpus

Dukascopy XAUUSD ticks, Jan-Jul only. August is sealed.

Schema:

`timestamp_ms_utc, ask_raw, bid_raw, ask_volume, bid_volume`

Raw prices are integers scaled by 1000:

`ask = ask_raw / 1000.0`

`bid = bid_raw / 1000.0`

If midpoint arithmetic is required, preserve floating-point operation order:

`ask0 = ask_raw / 1000.0`

`bid0 = bid_raw / 1000.0`

`mid = (ask0 + bid0) * 0.5`

Do NOT replace this with `(ask_raw + bid_raw) / 2000.0`. Source-equivalence work proved the mathematically equivalent expression can flip threshold events because of floating-point evaluation order.

Current mounted file hashes:

- Jan: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Feb: `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`
- Mar: `814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177`
- Apr: `30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f`
- May: `3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d`
- Jun: `34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2`
- Jul: `e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7`

Do not use August for reconstruction, fitting, debugging, or verification.

## Price/execution model

Formal baseline modeled half-spread:

`H = 0.10`

The later source-equivalence scripts reconstruct the formal execution surface as:

`mid = (ask0 + bid0) / 2`

`modeled_bid = mid - H`

`modeled_ask = mid + H`

For a long:
- entry price = Ask
- favorable/exit mark = Bid
- initial stop reference = entry-tick Bid minus stop distance
- realized exit = Bid

For a short:
- entry price = Bid
- favorable/exit mark = Ask
- initial stop reference = entry-tick Ask plus stop distance
- realized exit = Ask

Equivalent realized trade PnL is the side-adjusted price difference with the modeled spread embedded by bid/ask execution. For 0.01 XAUUSD lot economics, the Python research treats a $1 XAU move as approximately $1 PnL.

No extra commission term is included in the certified formal result.

## Exact chronological ownership

The design is tick-driven and causal.

Single-position ownership:
- only one Gamma position can own the account interval;
- while a position is live, no new Gamma entry may execute;
- chronological replay is mandatory;
- a signal at or before the close tick of the previous trade is not a new non-overlapping entry.

R8 source chronology:
1. update minute counter;
2. update current/finished one-second bucket;
3. locate live position;
4. if live, manage position and RETURN;
5. if a position just closed, set cooldown, reset micro-state and RETURN;
6. otherwise process a new signal.

The closure tick itself is not reused as a fresh entry tick.

Cooldown:
- 1 second after close in the R8 lineage.

Trade-rate ceiling:
- maximum 5 entries per minute.

Minute change:
- resets per-minute trade count;
- resets the R8 micro-event state.

The precise way CONT events affected sweep quota/cooldown in the original promoted Gamma helper is part of the unresolved source-equivalence lineage. Do not invent it.

## Internal completed-second bars

Source lineage builds internal one-second OHLC from Bid ticks.

On the first tick of a new second:
- push the prior second bucket into the completed ring;
- initialize the new bucket from the current Bid.

Within a second:
- open = first Bid;
- high = max Bid;
- low = min Bid;
- close = latest Bid.

Only completed seconds are used by the rolling liquidity and velocity context. A current unfinished bucket is not part of the historical lookback.

## Session-adaptive completed-M5 ATR gate

ATR timeframe: completed M5.

ATR period: 14.

Use the completed ATR bar (MT5 CopyBuffer shift 1 semantics), never the forming M5 ATR.

Session definitions are DST-aware and derived from UTC:
- London local session: 08:00 through 16:30;
- New York local session: 08:00 through 17:00;
- overlap = both true;
- otherwise OFF session.

R8 session ATR minimums:
- London: 2.00
- London/NY overlap: 1.75
- New York: 1.75
- Off session: 2.50

Entry permission requires completed M5 ATR >= the current session minimum.

R8 source also has a max-spread permission of 25 symbol points and fail-closed behavior when ATR is unavailable. The exact promoted Python helper's interaction between this source spread gate and the formal modeled H=0.10 execution surface is part of unresolved source lineage. Do not silently add/remove this rule during equivalence reconstruction; test it only as a source-equivalence hypothesis.

## R8 microstructure base state

Parameters:
- liquidity lookback = 20 completed seconds
- velocity lookback = 5 seconds
- state persistence = 2 seconds
- state expiry = 20 seconds
- break buffer = $0.10
- reclaim distance = $0.15
- continuation confirm buffer = $0.08
- minimum directional displacement = $0.15
- minimum directional efficiency = 0.30
- cooldown = 1 second
- max entries/minute = 5

### Rolling liquidity

Using the most recent 20 completed one-second Bid bars:

`upper = max(high_i)`

`lower = min(low_i)`

### Velocity/displacement

Let the start be the oldest close in the 5-second velocity window. Walk the completed closes forward and then to current Bid.

`displacement = current_bid - start`

`travel = sum(abs(price_k - price_(k-1)))`

including the final move from newest completed close to current Bid.

`efficiency = abs(displacement) / (travel + 1e-9)`

## R8 event state machine

States:
- IDLE
- UPPER_BREAK
- LOWER_BREAK
- UPPER_RECLAIM
- LOWER_RECLAIM

IDLE:
- if Ask >= upper + 0.10 -> UPPER_BREAK; level = upper
- else if Bid <= lower - 0.10 -> LOWER_BREAK; level = lower

UPPER_BREAK:
- if Ask <= level - 0.15 -> UPPER_RECLAIM and reset state-start time
- else after at least 2 seconds, if Ask >= level + 0.08 AND displacement >= +0.15 AND efficiency >= 0.30 -> R8 CONT_UP

LOWER_BREAK:
- if Bid >= level + 0.15 -> LOWER_RECLAIM and reset state-start time
- else after at least 2 seconds, if Bid <= level - 0.08 AND displacement <= -0.15 AND efficiency >= 0.30 -> R8 CONT_DN

UPPER_RECLAIM:
- if displacement <= -0.15 AND efficiency >= 0.30 -> SWEEP_UP -> SHORT

LOWER_RECLAIM:
- if displacement >= +0.15 AND efficiency >= 0.30 -> SWEEP_DN -> LONG

State expiry:
- if active state age > 20 seconds -> IDLE.

Gamma_2's active directional owner is the sweep/reclaim family:
- upper sweep/reclaim -> SHORT
- lower sweep/reclaim -> LONG

Market structure does not reverse or vote the entry direction. It owns lifecycle geometry.

IMPORTANT: the exact promoted Gamma_2 event population is not reproduced by simply taking all R8 sweep events or by any of the tested simple CONT side-effect variants. This is the known source-equivalence blocker.

## Completed multi-timeframe structure

Lifecycle context uses completed:
- 1 minute
- 3 minute
- 5 minute
- 10 minute
- 20 minute

For each trade direction, derive a directional alignment count from completed structure only.

The frozen January causal cache contains:
- `align_long`
- `align_short`
- completed-M5 ATR
- completed second OHLC and microstructure fields

Frozen alignment cache SHA-256:
`71fc132e208589857dfe5dd6b8b1a204bd626d65c249890e842b6d5647ba65a5`

The recovered cache builder uses completed calendar bars and a directional return-sign vote across 60/180/300/600/1200-second scales. Event seconds map only to bars that have already ended.

Source-equivalence testing proved that reconstructed alignment is numerically near-identical to the frozen cache and is NOT the source of the 68% vs 82% reconstruction gap.

When available, prefer the frozen cache for exact January archaeology.

## Gamma_2 lifecycle ownership

Alignment threshold:

`alignment_count >= 3`

ALIGNED lifecycle:
- initial stop distance = $1.00
- trail activation = $0.10 favorable excursion
- trailing distance = $0.04
- maximum hold = 60 seconds

WEAK lifecycle:
- initial stop distance = $3.00
- trail activation = $0.18 favorable excursion
- trailing distance = $0.05
- maximum hold = 60 seconds

No fixed profit target.

### Tick-by-tick lifecycle order

At each later tick:
1. compute favorable and adverse excursion using executable Bid/Ask;
2. update MFE/MAE diagnostics;
3. check whether current price hit the existing stop;
4. check max hold >= 60,000 ms;
5. if either condition closes the trade, exit at current executable Bid/Ask and stop processing;
6. otherwise, if favorable excursion >= activation, compute a new trailing stop;
7. move the stop only in the favorable direction.

This order matters. A trailing level created by the current tick is not used retroactively to stop on that same tick before it is created.

Long trailing candidate:
`candidate_stop = current_bid - trail_distance`

Short trailing candidate:
`candidate_stop = current_ask + trail_distance`

Stops only ratchet; they never loosen.

## Current certified Jan-Jul result contract

Aggregate:
- trades: 215,725
- winners: 175,143
- win rate: 81.1880866844%
- net: +$29,583.1165
- gross profit: +$75,039.3055
- gross loss: -$45,456.1890
- profit factor: 1.650805
- max drawdown: $217.29
- R9 SYNTH trade density: 98.350977%
- R9 SYNTH winner-count ratio: 91.632659%
- R9 SYNTH net ratio: 9.570019%
- certified R9 REAL -> SYNTH bridge closed: 22.222201%

Monthly exact contract:

| Month | Trades | Winners | Win % | Net | Gross Loss | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| Jan | 30,943 | 25,368 | 81.9830 | +5,131.0510 | -6,091.2065 | 40.7975 |
| Feb | 31,072 | 25,556 | 82.2480 | +9,545.0915 | -6,886.7000 | 29.0535 |
| Mar | 39,690 | 32,778 | 82.5850 | +8,076.7335 | -8,347.9205 | 28.7200 |
| Apr | 29,320 | 23,554 | 80.3340 | +2,683.3625 | -6,403.3060 | 48.3275 |
| May | 27,964 | 22,795 | 81.5160 | +2,109.4835 | -5,781.2580 | 47.5310 |
| Jun | 30,023 | 24,342 | 81.0780 | +1,969.9155 | -6,261.3860 | 37.4755 |
| Jul | 26,713 | 20,750 | 77.6780 | +67.4790 | -5,684.4120 | 217.2900 |

Any fresh reconstruction must match January first, then the entire monthly table.

## Metric definitions

Trade winner:
`realized_pnl > 0`

Gross profit:
sum of positive realized PnL.

Gross loss:
sum of negative realized PnL.

Net:
`gross_profit + gross_loss`

Profit factor:
`gross_profit / abs(gross_loss)`

Realized max drawdown:
maximum difference between prior peak cumulative realized PnL and current cumulative realized PnL in chronological trade order.

## Robustness contract

Aligned trail neighborhood at H=0.10:
- trail 0.03 -> 215,741 trades; +$29,376.9555; PF 1.64787; max DD $219.075; every month positive
- trail 0.04 -> 215,725 trades; +$29,583.1165; PF 1.65081; max DD $217.290; every month positive
- trail 0.05 -> 215,702 trades; +$29,712.2350; PF 1.65165; max DD $220.635; every month positive

Alignment threshold neighbor:
- threshold 4
- H=0.10
- trail 0.04
- 210,596 trades
- 172,845 winners
- +$29,510.9185
- PF 1.62556
- max DD $183.426
- every month positive

Spread stress:
- H=0.11 -> 214,480 trades; +$25,522.9455; PF 1.53434; max DD $535.481; July negative
- H=0.125 -> 212,255 trades; +$19,691.9115; PF 1.38135; max DD $1,212.603; July negative

## Explicitly NOT integrated into the current build

The following are research history, not current Gamma_2 executable logic. They must remain OFF if reproducing the ROI report:

- Gamma_1 automatic stacking
- Gamma_1 + Gamma_2 single-slot integration
- Gamma_1 + Gamma_2 two-sleeve integration
- 010 reconstructed ~68-72% shadow event router
- 011 identity-conditioned early loss exit
- 012 regime-gated shadow filter
- 013 generic mixture-of-regime experts
- P4 raw rotation transplant
- P6 raw expansion transplant
- P7 compression-release
- P5 H1 structural sleeve
- P5 H4 structural sleeve
- 016 native-R9 meta ownership router
- 017 confidence specialist router
- 018 delayed first-touch proof
- proof -> pullback -> reacceleration
- blanket scheduled-news blackout
- leading-tick microstructure 019 (research not yet executed/promoted)
- MUWHAHAHA lot ladder
- percentage-risk position sizing

These may be future research inputs, but they are not part of the current formal build used in the ROI report.

## Source-equivalence blocker and diagnostic history

Certified January target:
- 30,943 trades
- 25,368 winners
- 81.9830%
- +$5,131.051 net
- -$6,091.2065 GL

Simple reconstructions fail:

SEMANTICS_004:
- quota-only: 27,756 trades / 68.41% / negative
- cooldown-only: 34,174 trades / 68.32% / negative

ALIGNMENT_005:
- replacing reconstructed alignment with exact frozen alignment changes only single-digit counts;
- win profile remains about 68%.

OWNERSHIP_006:
- full R8 position ownership yields only 16,215 observable sweeps;
- 68.30% wins;
- negative.

SWEEPGEN_007:
- close-break/close-reclaim, wick-break/close-reclaim, same-bar, and no-minute-reset variants all remain around 67.7-68.0%.

STATE_CONTEXT_008:
- richer static context gates do not recover source equivalence;
- best substantial-density win rate only about 69.5%.

Therefore the missing promoted source semantics are deeper than:
- sweep timing alone;
- quota/cooldown alone;
- simple five-scale alignment;
- full original-R8 occupancy;
- static context filtering.

Likely unresolved class:
- exact event-population identity and/or state-transition/lifecycle ownership from runtime-local helpers.

Runtime-local helper names remembered by the project:
- `r9b_screen.py`
- `r9b_r8_recert.py`
- `r8_sweep_lifecycle_screen.py`

Do not pretend these files are preserved if they cannot be found.

## Mandatory fresh-chat reproduction gate

A fresh chat asked to rebuild Gamma must:

1. Read this specification.
2. Read the formal result JSON and whitepaper at the exact commits.
3. Verify all Jan-Jul data hashes.
4. Keep August sealed.
5. Reconstruct price arithmetic exactly.
6. Reconstruct completed-second bars and completed-M5 ATR.
7. Reconstruct five-scale completed structural context.
8. Reconstruct sweep/reclaim event semantics.
9. Run January only.
10. Require exact or numerically negligible equivalence to:
   - 30,943 trades
   - 25,368 winners
   - +$5,131.051 net
   - -$6,091.2065 gross loss
11. If January fails, STOP. Resume source-equivalence archaeology; do not run Jan-Jul optimization and do not build MT5.
12. Once January passes, freeze all logic.
13. Run Jan-Jul.
14. Require the exact monthly table above.
15. Only after full equivalence may the build be labeled `R9B_Gamma_2_Structure_Aware_Sweep_Reclaim`.
16. Only after that may an MQL5 translation be attempted.
17. MT5 real-tick certification remains mandatory before deployment claims.

## MT5 translation blueprint after Python equivalence

Do not code the EA until the equivalence gate passes.

Translation requirements:
- OnTick is the single state-machine driver.
- Build internal completed 1-second Bid OHLC from live ticks; do not require an S1 chart.
- M5 ATR(14) uses completed bars only.
- Implement DST-aware London/New York session gate.
- Maintain the 20-second liquidity ring and 5-second velocity/efficiency calculation.
- Preserve ask/bid asymmetry for upper/lower breaks, reclaims, entries, stops and trailing.
- Maintain one live Gamma position at a time.
- Preserve close-tick return semantics and one-second cooldown.
- Preserve five-entry-per-minute quota.
- Build 1m/3m/5m/10m/20m structural context from completed bars only.
- Structure selects lifecycle geometry; it does not vote entry direction.
- ALIGNED: $1.00 stop / $0.10 activation / $0.04 trail / 60s.
- WEAK: $3.00 stop / $0.18 activation / $0.05 trail / 60s.
- No fixed take-profit.
- Trailing stops ratchet only.
- Add deterministic logging sufficient to compare every signal, entry, lifecycle branch, stop update and exit against Python.
- Run MT5 "Every tick based on real ticks" certification before any live/demo deployment conclusion.

## Current ROI contract

Current formal Gamma_2 ROI report is based ONLY on the certified build above:
- +$29,583.12 fixed-0.01-lot Jan-Jul net
- 215,725 trades
- 175,143 winners
- 81.19% success
- PF 1.6508
- max DD $217.29

On a $100,000 normalization balance this is 29.58% backtest-implied return, not a live expected return.

Tested wider modeled half-spread reduces the same normalized Jan-Jul return:
- H=0.11 -> 25.52%
- H=0.125 -> 19.69%

Do not annualize or present these as guaranteed future returns.

## Fresh-chat command

Use this exact intent:

"Carson, read the R9B GAMMA — FULL CURRENT BUILD SPECIFICATION first. Treat it as the authoritative current Gamma build contract. Verify the Jan-Jul Dukascopy hashes and the formal Gamma_2 GitHub result/whitepaper commits. Reproduce January source equivalence before running the full Jan-Jul Python backtest. Do not integrate 010-019 research shadows, Gamma_1, lot ladder, or MT5 changes. If January does not match the certified target, stop and resume source-equivalence archaeology. Only after the complete monthly Gamma_2 table matches may you build an MT5 EA."

## Current research boundary

The current formal build ends here.

Latest research beyond the build:
- 017: improved research ownership frontier but negative -> NOT integrated.
- 018: delayed proof rejected -> NOT integrated.
- 019: leading tick microstructure is the next research unit -> NOT integrated.

This separation must remain explicit so the formal ROI cannot be contaminated by negative/rejected research branches.
