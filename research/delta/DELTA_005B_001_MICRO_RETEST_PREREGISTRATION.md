# DELTA 005B-001 — Micro-Retest / Reclaim Specialist

**Status:** PREREGISTERED  
**Mode:** historical Python simulation only  
**Campaign:** DELTA_005 Entry + Initial-Hold  
**Parent finding:** DELTA_005A-001  
**Mature Hold/Exit/High-Profit optimization:** prohibited  
**August 2026:** sealed

## Research question

Can a second specialist recover first-touch opportunities that do not belong to the mild-flow direct-continuation state by requiring a causal break -> retest -> reclaim sequence before entry?

DELTA_005A established that universal flow gating reduces losses mainly by removing activity. DELTA_005B therefore tests specialist ownership rather than stricter filtering.

## Public reconstructible provenance

Open-source breakout/retest logic:
https://www.tradingview.com/script/vRl3fSYC-Breakout-Retest-Strategy/

Open-source ORB breakout + wick retest:
https://www.tradingview.com/script/muLbjEdA-Casper-SMC-5m-ORB-Retest/

MQL5 Code Base — Daily Zone Recovery for Gold, which explicitly separates breakout-with-return, level-test-breakout, and test-pullback-retest scenarios:
https://www.mql5.com/en/code/75922

Multilingual XAUUSD session-breakout implementation reference:
https://www.mql5.com/zh/code/75586
https://www.mql5.com/ja/code/75586

Only reconstructible sequence concepts are used. No vendor performance claim is used.

## Ownership router

At the first causal R9-style opportunity tick:

### 005A direct-continuation owner
If:
- fast 250 ms tick flow has the trade sign; and
- slow 1,000 ms tick flow has the trade sign;

then enter through the direct continuation path.

Thresholds are sign-only:
- BUY: fast >= 0 and slow >= 0
- SELL: fast <= 0 and slow <= 0

### 005B retest owner
If direct flow is not aligned, the opportunity is handed to 005B.

005B requires:
1. the R9-style opportunity exists;
2. midpoint establishes a true break of the frozen virtual boundary;
3. midpoint returns toward that boundary within the retest band;
4. midpoint reclaims in the original direction by the reclaim buffer;
5. fast/slow sign flow agrees at reclaim;
6. R9 gate + completed-S1 quality still support the original direction.

No future tick participates in the decision.

## Midpoint sequence

The modeled Bid/Ask spread is not allowed to create a fake retest.

For sequence geometry:
midpoint2 = ask_raw + bid_raw

BUY break:
midpoint >= frozen BUY boundary

SELL break:
midpoint <= frozen SELL boundary

Retest and reclaim are evaluated on midpoint. Execution remains at modeled Ask/Bid.

## Frozen parameter grid

Retest band:
- $0.00
- $0.02
- $0.05

Reclaim buffer:
- $0.00
- $0.02
- $0.05

Maximum break-to-reclaim time:
- 1,000 ms
- 3,000 ms
- 5,000 ms

Total configurations: 27.

No new geometry is introduced until the completed grid is persisted and GOV-013 leverage analysis is performed.

## State rules

- retest must occur after break;
- reclaim must occur after retest;
- minute reset cancels unfinished retest state;
- timeout cancels unfinished retest state;
- once handed to 005B, the same break is not allowed to become a delayed 005A entry;
- a later independent opportunity may start a new ownership decision;
- one simulated position at a time.

## Downstream lifecycle

The preserved R9-style hard stop, trailing, maximum duration, accounting, and rearm lifecycle remain unchanged after entry.

## Required diagnostics

For every configuration:
- total trades and wins;
- direct 005A entries;
- 005B retest attempts;
- completed retests;
- 005B reclaim entries;
- 005B wins;
- gross positive/negative outcome;
- net outcome;
- balance drawdown;
- activity retention vs Stage-A parent;
- activity recovery vs 005A diagnostic anchor;
- 1/3/5/10/15-second survival;
- MFE/MAE horizons;
- timeout/cancel counts.

## Decision rule

The research target is not the numerically best net result in isolation.

The important question is whether 005B restores unique activity and winning trades while retaining a meaningful portion of 005A's loss/drawdown improvement.

If the retest specialist fails to recover activity or merely recreates the same loss distribution, the next structural branch is DELTA_005C failed-break / sweep reversal.
