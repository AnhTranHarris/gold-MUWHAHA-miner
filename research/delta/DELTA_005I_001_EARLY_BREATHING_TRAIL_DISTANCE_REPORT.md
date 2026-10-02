# DELTA 005I-001 — Early Breathing Trail Distance Report

**Recovery status:** RECOVERED 2026-10-02 FROM DURABLE CHECKPOINT + MASTER RESEARCH LEDGER  
**Scientific status:** COMPLETE — NOT PROMOTED  
**Mode:** historical Python simulation only  
**Focus:** ENTRY + INITIAL-HOLD  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Stage-A ticks:** 4,205,709  
**Variants:** 20  
**August:** not accessed

Canonical checkpoint:
`research/delta/checkpoints/DELTA_005I_001_RESULTS.json`

Temporary analysis Sheet:
https://docs.google.com/spreadsheets/d/1Q0QvgdOX5Nx96YdnLeS9XaAosz7U_kBwx4hMXYdk2Ck/edit?usp=drivesdk

## Purpose

005I followed the 005H discovery that R9's early trailing protection is an Initial-Hold bottleneck.

It kept:
- original R9-style entries;
- $0.30 hard stop;
- +$0.10 trail activation;
- mature $0.03 trail;
- 30-second max hold.

Only the trail distance during a short initial breathing window was changed.

## High-retention cell

5-second early window / $0.05 early trail:
- trades: 16,791
- wins: 7,208
- winner retention: 98.0547%
- net: -$3,759.73
- gross loss: -$5,355.44
- max balance DD: $3,761.31
- net-loss improvement: 0.2261%
- gross-loss change: -0.2325% (worse)
- 5s survival: +0.9783pp
- 10s survival: +0.0189pp

## High-survival cell

10-second early window / $0.20 early trail:
- trades: 16,698
- wins: 5,613
- winner retention: 76.357%
- net: -$3,691.60
- gross loss: -$5,539.30
- max balance DD: $3,693.06
- net-loss improvement: 2.0341%
- gross-loss change: -3.6736% (worse)
- 5s survival: +9.4502pp
- 10s survival: +8.0451pp
- average hold: 7.6298 seconds

## Leverage conclusion

Early trail **distance** is lower leverage than trail **activation timing**.

Global widening requires long/wide settings to create substantial persistence and those settings destroy too many eventual winners.

## Decision

005I was not promoted.

Next change class:
`SPECIALIST_RECOMBINATION`

Next unit:
`DELTA_005J_STATE_CONDITIONED_INITIAL_PROTECTION`

## Source-identity warning

The checkpoint records result-producing source blob:
`8f22b1ff287cfce3d745587e981ec77e839a60d0`

That blob remains retrievable from GitHub object storage. The current branch source file has since changed and must **not** be assumed to be the exact result-producing version without verification.

This recovered report preserves that distinction for later Python->MQL5 audit.
