# DELTA-A R9 GRID — Small-Capital $500 Fallback Milestone V1

**Status:** MINOR FALLBACK MILESTONE / RESEARCH ONLY / NOT MT5 PRODUCTION AUTHORIZED

## Purpose

Preserve the first verified small-capital deployment architecture beneath R9 Grid Milestone 01. This milestone does **not** replace the main pre-August grid milestone.

## Capital model

- starting capital: **$500**
- physical XAUUSD lot: **0.01 fixed**
- Martingale: **forbidden**
- lot-size escalation: **none**
- full grid/specialist event engine remains virtual
- physical capital is admitted only to the strongest approved mature specialist: `CORE_H4_M1800`

## Capital-aware physical concurrency

- balance/equity < $750 -> max 1 physical position
- $750 to < $1,500 -> max 2
- $1,500 to < $3,000 -> max 3
- $3,000 to < $6,000 -> max 4
- >= $6,000 -> max 5

The purpose is to compound by **position-slot count**, not by lot size.

## Scheduled-market-gap guard

Do not start a physical trade when known time to the next trading break is <= planned lifecycle + 300 seconds.

Future MT5 translation must derive trading sessions from broker symbol/session metadata rather than hard-coded UTC assumptions.

## Margin semantics

Future MT5 must use broker-native account data and `OrderCalcMargin`. Research calculations using 1:500 are sensitivity checks only and must not be treated as guaranteed broker leverage.

## Feb-Jul tick-level research result

January remains virtual warm-up under the current research history.

- physical trades: **8,520**
- net: **+$13,754.29**
- ending research balance: **$14,254.29**
- minimum tick-level equity: **$469.82**
- maximum tick-level floating-equity DD: **$750.30**
- maximum simultaneous physical positions: **5**
- maximum estimated margin at 1:500: **$48.91**
- minimum estimated free margin at 1:500: **$459.59**
- all Feb-Jul months positive

## Interpretation

This is not a miniature 250-position portfolio. It is a **virtualized high-frequency specialist engine with a physical-capital admission controller**.

The virtual engine continues observing every candidate event even when the $500 account lacks a physical slot. This preserves state, routing, specialist evidence, and future expansion capability.

## Remaining gates

1. Coinexx broker-native margin/contract verification.
2. MT5 state pre-warm design.
3. Catastrophic account/equity circuit breaker.
4. August remains sealed.
5. Production MQL5 still requires separate explicit owner authorization.
6. Live-demo forward validation remains mandatory.

## Rollback role

If later $100 or other micro-capital research fails, this $500 adapter is the small-capital fallback milestone. The primary R9 Grid Milestone 01 remains the higher-level rollback target.
