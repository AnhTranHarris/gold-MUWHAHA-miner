# DELTA R037 — Session-Owned Opening-Range Breakout Preregistration

**Status:** PREREGISTERED / NO R037 REPLAY EXECUTED YET  
**Parent control:** `R032-C03_PLUS_DH02_S11_S08`  
**Research phase:** ENTRY + INITIAL-HOLD  
**Default replay surface:** `DUKAS_COINEXX_LIKE_P75`  
**Stage-A window:** `[2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)`  
**August 2026:** SEALED  
**MQL5:** NOT AUTHORIZED

## Research question

Can a session-owned opening-range breakout source add genuinely independent first-entry opportunities to R032-C03 without reopening the retired same-minute rearm/recenter families, DH02-A01 late-January recuts, or the retired DH-04 density-addition role?

## Fresh public-source harvest

The following public logic is reconstructible and was used only to define the event family, not to import performance claims:

1. MQL5, *Automating Trading Strategies in MQL5 (Part 42): Session-Based Opening Range Breakout (ORB) System* — configurable session start/duration, true range high/low, breakout direction, optional multi-bar close confirmation.
   https://www.mql5.com/en/articles/20339
2. MQL5, *Price Action Analysis Toolkit Development (Part 28): Opening Range Breakout Tool* — opening interval boundary, false-break concern, breakout/retest framework, ATR-aware context.
   https://www.mql5.com/en/articles/18486
3. TradingView open-source, *Gold ORB Strategy (15-min Range, 5-min Entry)* — XAUUSD New York opening-range construction and post-range breakout confirmation.
   https://www.tradingview.com/script/oYW9gdag-Gold-ORB-Strategy-15-min-Range-5-min-Entry/
4. TradingView open-source, *[Chrona] Opening Range Breakout* — explicit session-timezone handling and the note that continuously traded XAUUSD has no cash open; COMEX Gold's pit open is 08:20 New York time.
   https://www.tradingview.com/script/S1bnZOYx-Chrona-Opening-Range-Breakout/
5. TradingView open-source, *GOLD Asian Range Breakout Signals* — independently supports session-range levels as a Gold-specific event source rather than post-trade reentry.
   https://www.tradingview.com/script/rCMX1vGE-GOLD-Asian-Range-Breakout-Signals/

No vendor backtest, claimed win rate, or community profit number is treated as DELTA evidence.

## Why this is structurally independent

This family is **not** the closed DH-04 role.

DH-04 was a continuously evaluated generic compression -> expansion family using rolling compression windows, normalized box width, expansion ratios, and event ages.

R037-SORB is instead anchored to a predetermined civil-session transition:

- the range begins at a known session clock;
- the range freezes once its opening interval ends;
- the opportunity can arise without any earlier DELTA trade;
- it has no dependency on a just-closed position;
- it performs no generic same-minute rearm;
- it performs no post-exit bracket recentering;
- it is not a DH02-A01 or DH04 threshold/quartile recut;
- at most one first-entry event may be consumed per named session.

This is therefore a new `NEW_SPECIALIST` research unit.

## Candidate ID and grammar

Family: `R037-SORB-v1`

Grammar:

`SESSION_CLOCK -> BUILD_OPENING_RANGE -> FREEZE_RANGE -> WAIT_FOR_COMPLETED_S5_BREAK -> PROPOSE_ENTRY -> R9_INITIAL_LIFECYCLE -> EXPIRE`

The candidate does not optimize mature exit/high-profit behavior.

## Price and execution surfaces

Opening-range and confirmation geometry uses **BID** because MT5 chart bars are Bid-based and Bid candles are preserved in the DELTA tick-rooted contract.

Execution remains the frozen Coinexx contract:

- BUY fill at Ask;
- BUY mark/exit at Bid;
- SELL fill at Bid;
- SELL mark/exit at Ask;
- spread gate <= 25 points;
- $0.01 entry commission;
- $0.01 exit commission;
- fixed 0.01 lot;
- first executable quote after stop cross;
- price normalized to $0.01 Coinexx tick.

## Session definitions

All session clocks use civil-time/DST-aware IANA time zones.

### LONDON
- timezone: `Europe/London`
- opening-range start: `08:00:00` local
- 15-minute range ends: `08:15:00`
- 30-minute range ends: `08:30:00`
- proposal window expires two hours after the range end

### COMEX_GOLD
- timezone: `America/New_York`
- opening-range start: `08:20:00` local
- 15-minute range ends: `08:35:00`
- 30-minute range ends: `08:50:00`
- proposal window expires two hours after the range end

The COMEX anchor is a market-structure reference only. DELTA still trades the XAUUSD quote stream.

## Causal range construction

For each named session/day:

1. Begin with no range before the session start.
2. From first tick with `t >= range_start` until `t < range_end`, update:
   - `OR_HIGH = max(Bid)`
   - `OR_LOW = min(Bid)`
3. Freeze both boundaries at `range_end`.
4. No tick from `t >= range_end` may modify the range.
5. Empty opening range => no opportunity for that session.
6. Same-timestamp source order is preserved.
7. No synthetic ticks are invented.

## Causal breakout confirmation

After the range is frozen and before expiry:

- construct S5 Bid bars directly from authoritative ticks using `[bar_start, bar_end)`;
- a completed S5 bar becomes visible only at its right edge;
- LONG confirmation: completed S5 Bid close `> OR_HIGH`;
- SHORT confirmation: completed S5 Bid close `< OR_LOW`.

At the first tick on/after that S5 right edge:

- the candidate may propose LONG only if current Bid is still `> OR_HIGH`;
- the candidate may propose SHORT only if current Bid is still `< OR_LOW`;
- spread must pass the frozen 25-point gate;
- the candidate must be flat under the integrated one-position-at-a-time ledger.

No future candle high/low/close is used.

### First-confirmation consumption rule

The first causal breakout confirmation attempt consumes that named session whether it executes or is rejected.

For C01-C04, the first completed S5 close outside the frozen range is the confirmation attempt. For C05, the second consecutive completed S5 close outside the same side is the confirmation attempt.

If the first executable tick on/after that confirmation edge fails because current Bid has re-entered the range, spread exceeds 25 points, another position is open, or R032-C03 wins a same-tick collision, the SORB event is recorded with the exact rejection/block reason and expires for that session. It is never deferred to a later breakout. This prevents adaptive retry/cherry-picking.

## Immutable configurations

No configurations may be added after Stage-A results.

### R037-C01_LONDON_15
- London only
- 15-minute opening range
- one completed S5 close outside the frozen range
- first accepted proposal consumes the session

### R037-C02_COMEX_15
- COMEX Gold anchor only
- 15-minute opening range
- one completed S5 close outside the frozen range
- first accepted proposal consumes the session

### R037-C03_DUAL_15
- union of C01 + C02
- each session retains independent one-event ownership

### R037-C04_DUAL_30
- London + COMEX
- 30-minute opening ranges
- one completed S5 close outside

### R037-C05_DUAL_15_CONFIRM2
- London + COMEX
- 15-minute ranges
- requires two consecutive completed S5 closes outside the same side of the frozen range
- no threshold retuning

These five vectors are theory anchors, not a Cartesian optimization grid.

## Interaction with R032-C03

R032-C03 remains unchanged and has priority.

Integrated replay rules:

1. one position at a time;
2. ordinary GLOBAL NO_REARM remains unchanged;
3. SORB is an independent first-entry specialist;
4. SORB may trigger inside an M1 cycle because it does not depend on the R9 bracket;
5. if an R032-C03 proposal and SORB proposal occur on the same decision tick, R032-C03 wins and SORB is recorded as a collision;
6. if any position is already open when SORB confirms, that SORB event is recorded as blocked/consumed and is **not deferred**;
7. SORB exit suppresses no unrelated future R032-C03 opportunity;
8. no SORB post-exit rearm exists;
9. SORB ownership expires after its first accepted/blocked breakout event or at its session expiry, whichever comes first;
10. next session/day creates a fresh independent event state.

## Duplicate-event definition

A SORB proposal is a duplicate/conflict only when an R032-C03 proposal exists on the exact same decision tick. Nearby proposals at different timestamps remain distinct, subject to one-position-at-a-time blocking.

## Downstream lifecycle

For entry attribution, the accepted SORB trade uses the frozen R9 lifecycle:

- hard stop: $0.30;
- trail activation: +$0.10 MFE;
- trail distance: $0.03;
- max hold: 30 seconds;
- no generic same-minute rearm after SORB exit.

Mature exit/high-profit optimization remains deferred.

## Control fixture

R032-C03 is the only integration control.

Current durable Stage-A workbook control:

### P75
- trades: 13,868
- winners: 6,331
- trade retention: 82.542706%
- winner retention: 87.143840%
- net: -$2,842.16
- delta net vs ordinary opposite-rearm control: +$21.18

### P90 near-gate context
- trades: 2,388
- winners: 1,050
- trade retention: 79.706275%
- winner retention: 83.267248%
- net: -$554.14
- delta net vs ordinary opposite-rearm control: +$4.00
- approximately nine trades short of 80% trade retention

The nine-trade shortfall is context, not a fitting target.

## Stage-A advancement rules

A configuration may advance beyond Stage-A only if all applicable requirements hold:

1. candidate mechanism executes causally and exactly as frozen;
2. at least 8 unique SORB proposals occur across at least 4 distinct trading days;
3. at least 5 genuinely incremental accepted entries remain after R032-C03 collisions/position blocking;
4. R032-C03 opportunities are not deleted or rewritten;
5. combined trade count is not lower than the parent;
6. combined winner count is not lower than the parent unless combined net and gross loss both improve;
7. combined net may not worsen by more than $2.00 versus R032-C03;
8. max balance/equity drawdown may not deteriorate by more than 1%;
9. candidate incremental gross-loss contribution and net/trade must be reported;
10. candidate must not depend on one isolated day.

A **strong advance** requires non-negative incremental net in addition to the above.

If the sample is causally valid but below the activity floor, label `MORE_RESEARCH_SAMPLE_STARVED`, not PASS.

## Cross-surface rule

Only a Stage-A survivor may proceed to:
- P50
- P75
- P90
- DUKAS_NATIVE

No cross-surface threshold retuning is allowed.

## Fail/stop rules

Retire or restructure this family if:

- activity is restored only by materially worsening net/gross loss;
- the event becomes effectively a post-exit reentry;
- a result depends on changing civil-session times after seeing performance;
- a positive pocket requires repeated range-duration or confirmation recutting;
- the same exact configuration reverses sign across modeled surfaces without a documented structural explanation;
- the incremental benefit is too small to justify a session/DST state machine.

## Required result diagnostics

For each configuration:
- session proposal count;
- distinct days;
- accepted entries;
- R032 collisions;
- position-blocked events;
- duplicates;
- long/short split;
- wins;
- gross profit;
- gross loss;
- net;
- average net/trade;
- max balance DD;
- max equity DD;
- hold-time diagnostics;
- session contribution;
- parent + candidate combined metrics.

## Durability sequence

1. research/provenance — frozen here;
2. preregistration — frozen here;
3. producing code/config hash — next;
4. bounded Stage-A replay — only after code durability;
5. result writeback;
6. decision;
7. CURRENT_STATE update last.

No R037 result exists until a completed output is durably persisted and reconciled.
