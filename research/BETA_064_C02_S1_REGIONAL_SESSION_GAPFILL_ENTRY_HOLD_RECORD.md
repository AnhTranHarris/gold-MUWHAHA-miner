# BETA064-C02-S1 — Regional Session Authority / Gap-Fill Entry→Hold Research Record

**Date:** 2026-09-30  
**Branch:** `beta`  
**Parent:** BETA064 Major Checkpoint 01  
**Status:** PROMISING RESEARCH CHILD — NOT A NEW MAJOR CHECKPOINT — NO MQL5 PROMOTION — AUGUST SEALED

## Objective

Add regional session specialization without changing the frozen Checkpoint-01 Entry→Hold architecture.

Regional desks:

- Australia / Sydney
- Asia / Tokyo
- Middle East / Dubai
- Europe / Frankfurt/Berlin clock
- UK / London
- New York

The four major FX sessions are supported by public OANDA/IG session documentation. The Dubai desk is explicitly an engineered regional-liquidity research window, not a claim that the FX market has a universally standardized fifth session.

Method references:

- https://www.oanda.com/us-en/skills-and-insights/education/trading-asset-classes/forex/when-is-the-best-time-for-forex-trading/
- https://www.ig.com/uk/trading-strategies/when-is-the-forex-market-open-and-when-should-you-trading-in-the-191106

## Architecture

Sessions are multi-hot and overlap-aware.

A candidate may simultaneously belong to Europe + UK, or UK + NY, etc. The active session authority with the strongest economic opinion is allowed to contribute a regional survival/first-passage adjustment.

The frozen Checkpoint-01 model remains the base opinion.

`P_blend = 0.25 × P_base + 0.75 × P_session`

The session layer may only ADD a trade that the frozen router rejected.

It may never modify, cancel, replace, or retune a frozen Checkpoint-01 trade.

## Session clocks

Local civil-time windows:

| Desk | IANA timezone | Research window |
|---|---|---|
| Australia | Australia/Sydney | 08:00–17:00 local |
| Asia | Asia/Tokyo | 09:00–18:00 local |
| Middle East | Asia/Dubai | 08:00–17:00 local |
| Europe | Europe/Berlin | 08:00–17:00 local |
| UK | Europe/London | 08:00–17:00 local |
| NY | America/New_York | 08:00–17:00 local |

Using IANA local clocks automatically carries the relevant DST transitions into UTC.

## Initial diagnostic

The frozen specialists exhibit material session dependence.

Examples from Jan-Jul candidate populations:

- E11 Kinetic Ignition survivability was about 72–73% in Europe/UK/NY but only about 66% in Australia.
- E9 Level Break had stronger first-passage/economic behavior in UK/NY than in several earlier sessions.
- opening-window behavior differs substantially from full-session behavior.

Therefore session is not merely a cosmetic timestamp feature.

## First learned session router — rejected as too permissive

A January-FIT session meta-router was trained for all six regional desks.

A calibration-maximizing configuration expanded activity dramatically:

- 10,823 one-position trades
- weighted survivability 82.35%

This FAILED the >=85% survivability lock.

The result was not promoted.

## Conservative universal session router

Tightening the shared regional authority recovered only a small amount of activity:

- 2,180 trades
- 90.87% weighted survivability
- every month >89%

Useful but insufficient coverage improvement.

## Raw session-specific new-entry generators

Separate session ORB, session sweep/reclaim, session VWAP reclaim, failed-break, and opening compression-release generators were reconstructed and tested directly on Dukascopy raw tick paths.

The broad raw generators did NOT find a January calibration subset that simultaneously met:

- >=85% survivability
- positive economics
- adequate sample

Therefore these raw new-entry generators are REJECTED for this child.

Europe/UK opening compression-release remains an interesting research subfamily, but it is not promoted.

## Successful design: additive regional authority over frozen E1–E12

The useful session mechanism is not a second universal Entry system.

It is an additive regional authority that re-evaluates frozen Checkpoint-01 candidates that the base router rejected.

Session override is permitted only for:

- E5 VWAP Reclaim
- E6 Value Reversion
- E7 Sweep/Reclaim
- E9 Level Break
- E10 Compression Release
- E11 Kinetic Ignition
- E12 Failed Expansion

E1/E3/E4/E8 session overrides were pruned because their session-added evidence was weak or too sparse.

## Critical portfolio correction

An early additive replay allowed a session trade entered before a future frozen baseline trade to occupy the account and suppress the later baseline position.

That violates the Major Checkpoint-01 freeze.

The final replay corrects this:

1. select and reserve all 2,097 frozen Checkpoint-01 positions first;
2. construct their full entry→horizon reserved intervals;
3. allow a session trade only when its entire lifecycle fits inside an otherwise-idle gap;
4. session additions may compete only with other session additions inside that gap.

Thus all Checkpoint-01 trades remain intact.

## Final fixed regional authority floors

Using the 75% session / 25% base blend:

| Desk | Blended survival floor |
|---|---:|
| Australia | 0.920 |
| Asia | 0.900 |
| Middle East | 0.915 |
| Europe | 0.910 |
| UK | 0.925 |
| NY | 0.925 |

Session economic-score floor: 0.08.

These are research-optimized thresholds, not fresh blind-certified parameters.

## Final corrected gap-fill results

| Month | Frozen+Session trades | Survivability | First-passage success | Diagnostic path value | Session additions |
|---|---:|---:|---:|---:|---:|
| Jan | 726 | **87.60%** | 62.40% | +$894.48 | 448 |
| Feb | 910 | **87.36%** | 58.24% | +$1,081.53 | 573 |
| Mar | 1,463 | **87.29%** | 58.92% | +$1,640.56 | 895 |
| Apr | 589 | **90.15%** | 61.46% | +$711.29 | 315 |
| May | 509 | **91.94%** | 63.85% | +$576.06 | 260 |
| Jun | 585 | **88.21%** | 61.88% | +$623.69 | 324 |
| Jul | 288 | **90.63%** | 60.76% | +$254.46 | 158 |
| **Total** | **5,070** | **88.44% weighted** | **60.53%** | **+$5,782.07** | **2,973** |

Frozen Major Checkpoint-01:

- 2,097 trades
- 90.56% survivability
- +$2,781.99 diagnostic path-resolution value

Session child:

- +2,973 truly gap-filled Entry→Hold trades
- total activity **+141.8%** relative to frozen trade count
- session additions alone: 86.95% survivability
- combined: 88.44% survivability
- combined diagnostic PF approximately 2.42
- every month remains above the 87% research safety margin

The dollar values are first-passage research values, not production EA profit.

## Session contribution

Incremental gap-fill trades are concentrated in:

- UK: 1,032
- NY: 759
- Asia: 505
- Europe: 236
- Middle East: 235
- Australia: 206

The strongest incremental specialist families include:

- E11 Kinetic Ignition: 967 additions, ~92.66% survivability
- E6 Value Reversion: 1,083 additions
- E9 Level Break: 301 additions
- E7 Sweep/Reclaim: 210 additions, ~86.67% survivability
- E12 Failed Expansion: 210 additions, ~92.38% survivability
- E5 VWAP Reclaim: 124 additions, ~87.90% survivability
- E10 Compression Release: 78 additions, ~97.44% survivability

Some large subfamilies such as added E6/E9 are below 85% in isolation, so they are not standalone authorities. They remain permitted only inside the routed portfolio, which preserves the required monthly survivability lock.

## Leave-one-month-out robustness

For each month:

1. omit that month;
2. re-optimize regional floors on the other six months subject to >=87% survival in each training month;
3. apply those floors to the held-out month.

Held-out survivability:

- Jan: 87.60%
- Feb: 86.36%
- Mar: 87.29%
- Apr: 90.15%
- May: 91.94%
- Jun: 88.21%
- Jul: 90.63%

Result:

- **7 / 7 held-out months >=85%**
- weighted held-out survivability ~88.24%

This materially strengthens the case that regional session conditioning is not merely a seven-month threshold fit.

## Quant interpretation

The session layer is a genuine BETA improvement.

It demonstrates that many candidates rejected by the universal frozen router are conditionally viable when the same market mechanism is interpreted through its regional liquidity clock.

The correct architecture is now:

`Frozen Entry specialists → frozen router → reserve Checkpoint-01 positions`

plus, only in idle gaps:

`active regional session desk(s) → session-conditioned authority → permitted E5/E6/E7/E9/E10/E11/E12 candidate → Entry→Hold`

No Hold+Exit optimization has been introduced.

## Relationship to Checkpoint-02 SYNTH coverage

This child increases observed real Entry→Hold activity from 2,097 to 5,070 trades.

That raises the crude activity ratio versus the 71,810 SYNTH Entry→Hold-surviving benchmark from about 2.9% to about 7.1%.

This is NOT yet the authoritative condition-matched SYNTH coverage ratio because the dual SYNTH/Dukascopy replay must be rerun using the new session-gap-fill selections.

That dual replay is the next coverage diagnostic.

## Status

**Regional session specialist concept:** PASS as a promising research child.

**Major Checkpoint-01:** unchanged and still authoritative.

**85% monthly Entry→Hold survivability:** PASS.

**Hold+Exit:** deferred.

**August:** sealed.

**MQL5 promotion:** NO.
