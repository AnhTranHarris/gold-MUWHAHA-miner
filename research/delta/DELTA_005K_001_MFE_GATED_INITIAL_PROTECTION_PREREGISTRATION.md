# DELTA 005K-001 — MFE-Gated Initial Protection Before Delayed Trail

**Status:** PREREGISTERED
**Mode:** historical Python simulation only
**Focus:** ENTRY + INITIAL-HOLD
**Mature Holding-Trade + Exit + High-Profit:** frozen / out of scope
**Stage-A:** [2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)
**Surface:** DUKAS_COINEXX_LIKE_P75
**August:** SEALED

## Derivation

DELTA_005H found the first strong Initial-Hold lever: delaying tight R9 trailing activation from +$0.10 toward +$0.30 produced a broad persistence gain, including about +11pp at 5 seconds and +10.7pp at 10 seconds.

The cost was worse gross loss because positions receiving more breathing room could still fall back toward the original -$0.30 hard stop before the frozen downstream lifecycle harvested them.

DELTA_005I showed that globally widening trail distance is low leverage.

DELTA_005J showed that one static one-second state snapshot is insufficient for routing protection.

005K therefore conditions protection on **favorable excursion actually achieved by the trade**.

## Reconstructible public mechanics

MQL5 breakeven/trailing references separate:
- activation profit/price;
- the new stop level;
- continuous trailing after activation.

References:
- https://www.mql5.com/en/articles/3621
- https://www.mql5.com/en/articles/23882
- https://www.mql5.com/en/articles/22855

DELTA uses only reconstructible mechanics, not public performance claims.

## Parent / fixed behavior

All original R9-style entries remain unchanged.

Initial hard stop remains $0.30.

Continuous tight trail:
- activation fixed at +$0.30, based on the 005H high-leverage region;
- trail distance fixed at $0.03.

Max hold remains 30 seconds.

## One-time initial protection

Before continuous trailing activates, track causal MFE from entry.

When MFE first reaches `protect_trigger_price`, make one stop adjustment to:

BUY:
`entry + protect_lock_price`

SELL:
`entry - protect_lock_price`

The new stop may never loosen the existing stop.

This one-time protection occurs at most once per trade.

Afterward, continuous R9-style $0.03 trailing still waits until favorable excursion reaches +$0.30.

## Frozen 9-cell grid

MFE protection trigger:
- +$0.15
- +$0.20
- +$0.25

One-time lock relative to entry:
- -$0.10
- $0.00
- +$0.05

Continuous trail activation:
- fixed +$0.30

Trail distance:
- fixed $0.03

Total variants: 9.

Control references:
- original R9 Stage-A parent (+$0.10 / $0.03 trail);
- 005H +$0.30 activation with no one-time MFE lock.

## Required diagnostics

For every configuration:
- trades;
- winners;
- gross profit/loss;
- net;
- max balance drawdown;
- average hold;
- one-time protection count;
- protection-triggered exit count where observable;
- hard-stop / trail-stop / max-hold exits;
- 1/3/5/10/15s survival;
- winner retention vs R9 and 005H;
- gross-loss change vs R9 and 005H.

## Desired shape

The desired region preserves most of the 005H survival gain while reducing the gross-loss penalty.

This unit is not allowed to optimize mature trade harvesting.

If successful, 005K becomes an Initial-Hold protection component only.

August remains sealed.
