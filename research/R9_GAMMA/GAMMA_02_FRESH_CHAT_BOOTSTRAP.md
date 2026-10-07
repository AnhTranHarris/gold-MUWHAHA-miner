# GAMMA-02 — FRESH CHAT BOOTSTRAP

**READ THIS FIRST. DO NOT REBUILD COMPLETED RESEARCH.**

## Authority

Repository: `AnhTranHarris/gold-MUWHAHA-miner`  
Branch: `carson/r9-gamma-02-velocity-geometry-research`  
Bootstrap generated from branch head: `1d60319c5d5b55f6e03604d9a07e87d2f85a2a31`

Machine cursor:
`research/R9_GAMMA/GAMMA_02_CURRENT_RESEARCH_CURSOR.json`

Latest completed scientific unit:
`GAMMA_02_LOW_ACTIVITY_MARCH_SPECIALIST_109`

Latest checkpoint:
`research/R9_GAMMA/GAMMA_02_LOW_ACTIVITY_MARCH_SPECIALIST_109.md`

**FIRST INCOMPLETE UNIT:** `GAMMA_02_APRIL_SPECIALIST_DISCOVERY_110`

## Hard rules

- R9 SYNTH remains the hard goal, not a loose inspiration.
- August 2026 is SEALED. Do not open it.
- No MQL5 build yet.
- Fixed 0.01 ticket sizing.
- No Martingale or loss-dependent sizing.
- Ordered executable Bid/Ask ticks.
- Completed-bar HTF state only.
- No future information.
- High-activity specialist 103/104 is FROZEN.
- March reverse specialist 109 is FROZEN.
- April is discovery only for a NEW specialist.
- Once April specialist freezes, May is its first chronological validation month.
- Never retune prior specialists simply to force inactive months to trade.

## Exact January R9-SYNTH target

- net +$41,520.82
- trades 27,980
- PF 23.7154119275
- win rate 87.0908%
- expectancy +$1.483946/trade
- average hold 16.4627 seconds

Jan-Jul R9 SYNTH total remains +$309,122.85 / PF ~20.036 / 219,342 trades / ~87.14% wins.

## Frozen specialist A — high-activity renewal regime 103/104

Causal router:
- early desk: 64-parent rolling mean of pre-entry tick count over prior 1 second >= **12.90**
- late desk: 64-parent rolling mean of pre-entry tick count over prior 5 seconds >= **64.93**
- child cap 703
- original 083 renewal geometry unchanged

January:
- +$43,959.75
- 28,119 trades
- PF 19,625.888
- win 99.9004%
- expectancy +$1.56335
- avg hold 14.930s
- exact equity DD $10,348.16
- ALL SIX exact January R9-SYNTH metrics crossed

February, frozen:
- +$43,937.72
- 28,221 trades
- PF 328.429
- win 99.8618%
- expectancy +$1.55692
- avg hold 15.553s
- exact equity DD $10,348.16
- ALL SIX crossed

Frozen later months:
- Mar $0 / 0
- Apr $0 / 0
- May $0 / 0
- Jun $0 / 0
- Jul +$16.19 / 28

This specialist is a protected high-activity engine. Do not weaken it.

GitHub:
- `research/R9_GAMMA/GAMMA_02_ROLLING_ACTIVITY_REGIME_103_104.md`
- `research/R9_GAMMA/GAMMA_02_ROLLING_ACTIVITY_JANJUL_VALIDATION_105.md`
- `research/R9_GAMMA/helpers/gamma02_083_rolling_activity_regime_103.py`
- `research/R9_GAMMA/helpers/gamma02_083_rolling_activity_equity_104.py`

## Frozen specialist B — March failed-ignition reverse renewal 109

Discovery:
Late NY17 parents that fail the normal +$1.25 continuation quantum within 2 seconds show strong reverse-direction mean reversion. Early failures do not.

Frozen March rule:
- trigger: qualified late parent fails +$1.25 within 2 seconds
- reverse direction
- 120-second reverse renewal campaign
- quantum $4.00
- rearm 0
- fixed 0.01
- cap 703

March:
- **+$2,067.33**
- 807 trades
- PF **24.4604**
- win **88.60%**
- expectancy **+$2.56175**
- avg hold 50.81s

April frozen:
- 0 qualifying failures
- $0 / 0

Thus 109 is a March-regime specialist, not an April engine.

GitHub:
- `research/R9_GAMMA/GAMMA_02_LOW_ACTIVITY_MARCH_SPECIALIST_109.md`
- `research/R9_GAMMA/helpers/gamma02_low_activity_failed_ignition_markout_108.py`
- `research/R9_GAMMA/helpers/gamma02_low_activity_reverse_renewal_109.py`

Persistent Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/post-crossover-recovery/low-activity-specialists/`

## Critical historical QA notes

1. Hour-slice tail-entry artifact was invalidated. Never trust sliced-hour results without continuous parity.
2. Same-market-tick multi-level ladder events are scaling/pyramiding, NOT independent chronological opportunities.
3. One-event-per-source-per-market-tick is the default opportunity-count rule unless multiplicity is explicitly labelled as scaling.
4. Child-cap 703 January crossover was margin-model feasible under research assumptions, but exact Coinexx symbol specs must later be confirmed in MT5.
5. Do not reconstruct 083 helper dependencies manually: they are durable in `research/R9_GAMMA/replay083_deps/` and the persistent Library/Drive backups referenced by the machine cursor.

## Resume command / task

Resume exactly:

> `GAMMA_02_APRIL_SPECIALIST_DISCOVERY_110`

Goal:
- leave 103/104 and 109 unchanged;
- find a causal April-only discovery specialist from public/reconstructible mechanics and ordered April Bid/Ask ticks;
- aggressively search for high opportunity count + high expectancy;
- separate hypothesis generation from evidence;
- checkpoint every bounded experiment;
- freeze the April specialist before opening May for validation.

Suggested first diagnostic:
1. characterize why April has no 103 activity-regime parents and no 109 failed-late parents;
2. scan alternative session/hour/state families (London/overlap/NY, exact H4/H1/M15/M5 signatures);
3. map causal favorable/reversal markout by horizon;
4. test unique-tick opportunity factories and renewal geometry only where markout supports them;
5. do NOT contaminate frozen specialists.

## Timeout recovery rule

If UI times out:
1. read `GAMMA_02_CURRENT_RESEARCH_CURSOR.json`;
2. read this bootstrap;
3. inspect Library/GitHub for artifacts newer than cursor;
4. never rerun a completed unit;
5. save helper + result + checkpoint before launching another long sweep.

This file is intentionally compact enough to bootstrap a fresh chat without rebuilding the research history.
