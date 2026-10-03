# DELTA R037 — Fresh Independent Session-Transition Auction Source
Status: PREREGISTERED / NOT YET REPLAYED
Date: 2026-10-02
Parent: R032-C03_PLUS_DH02_S11_S08
Default surface: DUKAS_COINEXX_LIKE_P75
August 2026: SEALED
MQL5: NOT AUTHORIZED

## Purpose

R037 must recover genuinely independent first-entry opportunity supply without reopening generic same-minute rearm, post-exit recentering, DH02-A01 late-January recutting, or the retired DH-04 late-January density-addition family.

Fresh public-source research converged on a distinct mechanism: a completed pre-London/Asian range becomes a time-anchored market structure boundary, and the first London transition interaction can resolve as either acceptance beyond the range or a sweep followed by reclaim. This source does not require a prior R9/R032 trade, a just-closed position, or an R9 minute bracket.

## Source provenance and reconstruction

Public reconstructible anchors:

1. MetaQuotes CodeBase, GoldLondonBreakout (2026-09-01):
   https://www.mql5.com/en/code/75586
   Mechanism: measure the Asian-session range, then trade the London expansion from that locked range. The published description uses a 00:00-06:00 range and London breakout logic on XAUUSD.

2. MetaQuotes article, London Session Breakout System:
   https://www.mql5.com/en/articles/18867
   Mechanism: identify the pre-London range, lock it, then trade a London-session breakout.

3. TradingView open-source, ICT Session Sweep 25% Reclaim:
   https://www.tradingview.com/script/s7iHOQm8-ICT-Session-Sweep-25-Reclaim-Julz-Gatsby/
   Mechanism: complete the Asian range, allow London to sweep one boundary, then require a material reclaim back into the range before reversal entry.

4. TradingView open-source, Session Sweep System:
   https://www.tradingview.com/script/RY1SZR8x-Session-Sweep-System-WarRoomXYZ-V1/
   Mechanism: explicit Asia/London/New York session liquidity mapping and sweep detection.

The published performance claims from these sources are not imported as evidence. Only reconstructible market logic is used.

## Why this is independent

This is not DH-04 compression-expansion. DH-04 explicitly arms from local S30/S45/M1 compression and expands from a frozen compression box. R037 uses a time-defined completed session range regardless of whether that range is statistically compressed.

This is not the retired R035/R036 DH-04 density recut. No DH04-A01/S03/S07 vector, threshold, or late-January pocket is reused.

This is not generic R9 rearm. The event can occur when no prior DELTA trade has occurred that day.

This is not a post-exit recentered bracket. The reference range is fixed from market time before the London transition and never depends on an exit.

The sweep/reclaim branch is structurally related to failed-break logic, but its boundary source is distinct: a completed session range, not an R9 trade or generic M1 structure. It is therefore treated as a new independent opportunity source, not as a DH-05 threshold recut.

## Frozen market clock

Timezone: Europe/London.

Reference range:
- [00:00:00, 06:00:00) Europe/London.
- RangeHigh = maximum tick midpoint during the interval.
- RangeLow = minimum tick midpoint during the interval.
- RangeWidth = RangeHigh - RangeLow.
- The range freezes at 06:00:00 local and never redraws.

London transition eligibility:
- [07:00:00, 10:00:00) Europe/London.
- No entry outside this window.
- DST is handled by the Europe/London timezone, not by fixed UTC month-specific edits.

If the reference interval contains no valid range or RangeWidth <= 0, that date is ineligible.

## Common execution contract

- Ordered raw ticks remain authoritative.
- Midpoint = (Bid + Ask) / 2 is used only for structural range/event detection.
- Entry is executable: BUY at Ask, SELL at Bid.
- Confirmation is evaluated only after a completed S5 bar becomes visible at its right edge.
- Entry occurs on the first subsequent executable tick after the confirming S5 right edge.
- R9/R032 max-spread gate remains unchanged.
- One position at a time.
- R032-C03 proposals retain priority on the same timestamp.
- If a position is already open, the R037 proposal is skipped rather than queued.
- A skipped proposal is not replayed later.
- Maximum one accepted R037 entry per London transition per date.
- Global NO_REARM remains unchanged.
- R037 exits do not create a generic rearm.
- Downstream lifecycle remains frozen to the parent/R9 research lifecycle: $0.30 hard stop, +$0.10 trail activation, $0.03 trail distance, 30 s max hold.
- No mature-exit optimization is introduced.

## Frozen vectors

### R037-ST01 — LONDON_RANGE_ACCEPTANCE

Economic thesis:
A materially confirmed break of a completed pre-London range at the London transition may represent fresh session participation rather than the noisy same-minute R9 opportunity stream.

Rules:
1. Build and freeze the reference range.
2. During the London transition, detect the first boundary whose tick midpoint reaches at least 5% of RangeWidth beyond the boundary.
3. Require a completed S5 close at least 5% of RangeWidth beyond the same boundary.
4. If upper boundary: propose BUY.
5. If lower boundary: propose SELL.
6. Enter on the first executable tick after the confirming S5 right edge.
7. If price crosses the opposite boundary before confirmation, invalidate the current probe and allow the opposite side to become the first resolved boundary.
8. One accepted ST01 entry maximum per date.

No MTF trend filter, ATR filter, weekday filter, or range-width optimization is allowed in the first replay.

### R037-ST02 — LONDON_SWEEP_RECLAIM_25

Economic thesis:
A London probe beyond a completed session boundary followed by a deep reclaim may identify a separate reversal auction state rather than a continuation failure caused by a just-closed DELTA trade.

Rules:
1. Build and freeze the same reference range.
2. During the London transition, a sweep requires midpoint excursion at least 5% of RangeWidth beyond RangeHigh or RangeLow.
3. No continuation trade is taken by this vector.
4. After the sweep, require a completed S5 close back inside the range by at least 25% of RangeWidth measured from the swept boundary toward the range interior.
5. Upper-boundary sweep + deep reclaim proposes SELL.
6. Lower-boundary sweep + deep reclaim proposes BUY.
7. Entry is the first executable tick after the confirming S5 right edge.
8. The reclaim must occur before 10:00 local; otherwise the event expires.
9. One accepted ST02 entry maximum per date.

The 5% sweep and 25% reclaim are theory anchors from public session-sweep logic, not fitted DELTA thresholds.

## Parent interaction and collision policy

Control remains R032-C03_PLUS_DH02_S11_S08.

For each vector, replay:
PARENT_ONLY
versus
PARENT_PLUS_R037_VECTOR

Precedence:
1. existing-position management;
2. R032-C03 proposal;
3. R037 proposal if no position/proposal was accepted;
4. otherwise no trade.

R037 may not cancel, flip, suppress, or modify an unrelated R032-C03 proposal. This preserves attribution and prevents apparent improvement through deletion of parent opportunities.

## Stage-A replay contract

Window:
[2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)

Surface:
DUKAS_COINEXX_LIKE_P75

January cold start.
No August data loaded.
No later-January holdout is used to tune these rules.

The two frozen vectors are evaluated independently first. A combined ACCEPTANCE/RECLAIM router is not authorized in the first replay.

## Stage-A advancement criteria

A vector advances to cross-surface replay only if all are true:
1. At least 6 incremental executed entries across at least 4 distinct dates.
2. Net versus R032-C03 does not worsen: delta net >= $0.00.
3. Gross loss does not worsen by more than 1% versus parent.
4. Maximum drawdown does not worsen by more than 1% versus parent.
5. Incremental winner count is nonzero.
6. No parent opportunity is deleted except unavoidable one-position collision where parent already has priority.
7. Event reconstruction and timestamp ordering pass QA.

If neither vector clears these gates, the session-transition family is stopped in its present form without threshold recutting on the same Stage-A sample.

## Cross-surface advancement criteria

If a Stage-A vector advances, replay the exact frozen vector on P50, P75, P90, and DUKAS_NATIVE.

Modeled-surface promotion toward a new near-gate parent requires the existing R032 discipline:
- >=80% trade retention versus corresponding R9 control;
- >=80% winner retention where supported by the existing gate;
- positive net headroom versus the ordinary opposite-rearm control;
- no >5% unacceptable gross-loss/drawdown deterioration;
- materially distinct incremental opportunity contribution.

The approximately nine-trade P90 shortfall is a diagnostic target only. No rule may be fitted to manufacture exactly nine hindsight trades.

## Failure/stop rules

Stop this family if:
- its incremental trades are economically toxic;
- it clears activity only by consuming net headroom;
- the signal depends materially on tuning the session window after seeing Stage-A results;
- the acceptance and reclaim vectors both require additional filters to become nonnegative on the same sample;
- cross-surface sign flips indicate the effect is execution-surface specific;
- overlap with R032-C03 is so high that the source is not truly incremental.

## Deferred ideas

Not part of R037 first replay:
- New York-session analogues;
- Asia-range width filters;
- ATR regime filters;
- H1/H4 trend confirmation;
- day-of-week filters;
- news filters;
- multiple entries per session;
- combined acceptance/reclaim router;
- custom lifecycle;
- capital sizing.

Any of these requires a new preregistered research unit.

## Current gate

Research harvest: COMPLETE.
Preregistration: FROZEN.
Replay: NOT STARTED.
Promoted candidate: NONE.
Metric locks: NONE.
August: SEALED.
MQL5: NOT AUTHORIZED.
Next bounded unit: implement/replay R037-ST01 on Stage-A P75 only, persist result, stop.
