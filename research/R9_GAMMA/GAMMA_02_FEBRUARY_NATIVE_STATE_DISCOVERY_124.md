# GAMMA-02 — February Native State Discovery 124

**Status:** MAJOR FEBRUARY DISCOVERY FRONTIER — TARGET-GATED, CONTINUOUS, UNIQUE-TICK  
**Parent:** GAMMA_02_FEBRUARY_TARGET_GATED_TRANSFER_REPAIR_123A.md  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Discovery method

February ordered Dukascopy Bid/Ask ticks were used with 10-day pre-roll for state warmup only.

Entry permission:
- target-month entry only;
- H4 == H1 != 0 owns direction;
- one new favorable M1 extension event per market tick;
- exact H4/H1/M15/M5 state signature + UTC hour retained;
- no month label is part of any prospective deployable rule.

Executable fixed-horizon markout was measured at 5/15/30/60/120/300 seconds.

## Key February-native state findings

Several medium/long continuation cells are materially stronger than inherited January fast-quantum transfer:

- 15 UTC short, H4/H1 short, M15 long, M5 short: ~+$8.42/event at 300s;
- 13 UTC fully aligned short: ~+$5.55/event at 300s;
- 17 UTC short with M5 counterphase: ~+$4.50/event at 300s, PF ~10 diagnostic markout;
- 14 UTC macro-short / M15+M5 long counterphase: ~+$4.18/event;
- 9/19 UTC short cells: roughly +$2.8-$3.2/event;
- 17 UTC long reclaim state: ~+$4.06/event, PF ~12 diagnostic markout.

## One-ledger fixed-horizon portfolio

The discovery cells were converted into executable one-event-per-tick portfolios with cell-specific best coarse horizon from 30/60/120/300 seconds.

### Broad frontier
13 cells, 12,543 candidate events.

| Cap | Net | Trades | PF | Win | Exp/trade | Max open |
|---:|---:|---:|---:|---:|---:|---:|
| 32 | +$13,203.56 | 5,372 | 2.1305 | 59.29% | +$2.458 | 32 |
| 64 | +$23,335.09 | 8,893 | 2.1894 | 60.95% | +$2.624 | 64 |
| 128 | +$36,666.93 | 11,734 | 2.4008 | 61.79% | +$3.125 | 128 |
| **256+** | **+$40,163.27** | **12,543** | **2.3006** | **61.99%** | **+$3.202** | **226** |

No additional entries are gained above cap 226.

### Quality frontier
8 cells:
- +$30,391.08 / 7,230 trades / PF 2.6067 / +$4.203 expectancy at uncapped effective frontier.

### Strong frontier
6 cells:
- +$24,580.61 / 4,804 trades / PF 2.5792 / +$5.117 expectancy.

## Significance

This is the first clean February-native result to move monthly net from the inherited-family ceiling of roughly +$8-9K into approximately +$40K.

It proves February has enough reconstructible causal opportunity to reach R9-scale monthly dollar capture, but its current PF/win-rate/lifecycle still differ materially from R9 SYNTH.

Therefore the next refinement target is **quality extraction**, not raw trade inflation:
- state-specific TP/SL;
- displacement-depth gating;
- lifecycle refinement inside the strongest cells;
- then backcast identical rules to January and forward-check March.

## Durable artifacts

Library root:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/february-repair-123/`

- gamma02_feb_native_markout_124.py/json
- gamma02_feb_native_portfolio_124.py/json

## Next unit

`GAMMA_02_FEBRUARY_NATIVE_LIFECYCLE_QUALITY_125`

R9 SYNTH remains the hard target.
