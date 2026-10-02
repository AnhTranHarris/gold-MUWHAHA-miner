# R9 MT5 EA Functional Summary — DELTA Baseline Reference

**Created:** 2026-10-01  
**Purpose:** One-time owner-authorized read-only inspection of the R9 legacy Gamma baseline solely to summarize the R9 MT5 EA as a DELTA engineering baseline.  
**Legacy access status after this document:** CLOSED. Reopening requires new explicit owner authorization.

## 1. Source identity and inspection scope

Owner-authorized legacy inspection was restricted to the R9 baseline itself.

Primary code inspected:
- `carson/r9-gamma-00-baseline/Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`
- blob SHA: `7eecb5f1947017a01ce85b2520725de54749e523`
- version: 1.90

Instrumentation clone cross-check:
- `carson/r9-tick-logger/Experts/GoldMuwahahaMiner_R9_TickLogger.mq5`
- blob SHA: `5c7655cd3357f9126e8bffd97c34374dfb29f83e`
- version: 1.92
- source explicitly states trading logic is identical to R9, with per-tick instrumentation added.

Cross-reference surfaces:
- R9 REAL and SYNTH Strategy Tester reports;
- Project source history documenting the logger creation and unchanged R9 settings;
- Drive historical R9 reconstruction notes used only to verify the same R9 mechanics.

No later legacy candidate/specialist logic is imported into DELTA by this inspection.

## 2. One-sentence architecture

R9 is a single-symbol, single-position, high-activity XAUUSD state machine:

`NEW M1 MINUTE -> VIRTUAL MIDPOINT BRACKET -> SPREAD + COMPLETED-M5-ATR SESSION GATE -> COMPLETED-S1 DIRECTION/QUALITY GATE -> MARKET ENTRY -> HARD SL / TRAIL / 30s MAX HOLD -> OPPOSITE-SIDE SAME-MINUTE REARM -> NEW MINUTE RESET`

## 3. Default behavior-critical inputs

### Execution geometry
- lot size: `0.01`
- total virtual bracket width: `30 Hunter pips = $0.30` when `HunterPipPrice=0.01`
- half-width from minute midpoint: `$0.15`
- initial stop distance: `30 Hunter pips = $0.30`, subject to broker minimum stop distance
- trailing enabled
- trail distance: `3 Hunter pips = $0.03`
- trail activation: `10 Hunter pips = $0.10`
- max hold: `30 seconds`
- same-minute opposite-side rearms: max `3`
- magic: `5559`

### Completed-S1 quality gate
- velocity/displacement lookback parameter: `10 seconds`
- minimum directional displacement: `15 Hunter pips = $0.15`
- minimum directional efficiency: `0.70`
- range lookback: `10 seconds`
- minimum range: `50 Hunter pips = $0.50`
- maximum direction turns: `9`

### Regime gate
- enabled
- ATR timeframe: `M5`
- ATR period: `14`
- ATR reads completed bar `shift=1`
- maximum spread: `25 symbol points`
- fail closed if valid ATR unavailable

### Session-adaptive ATR minimum
- London: `2.00`
- London/New York overlap: `1.75`
- New York: `1.75`
- off-session: `2.50`
- quote UTC offset input: `0` by default

### Execution infrastructure
- Hunter pip price: `0.01`
- respect broker stop-level rules: true
- max deviation: `20 points`
- synchronous `CTrade` execution
- filling mode derived from symbol

## 4. Exact minute-cycle logic

On every tick, R9 first derives the tick's minute start.

On the first observed tick of a new minute:
1. reset same-minute rearm count to zero;
2. arm both directions;
3. compute current quote midpoint: `(Ask + Bid) / 2`;
4. freeze that minute's virtual thresholds:
   - buy threshold = midpoint + $0.15;
   - sell threshold = midpoint - $0.15.

These thresholds remain the minute's original boundaries. They are not continuously recentered during that minute.

R9 does **not** place two persistent broker-side pending stop orders. The bracket is internal state. A market order is sent only when a live tick crosses an armed virtual boundary and all entry gates pass.

## 5. Tick-rooted completed-second microstructure

R9 builds its own in-memory completed one-second Bid OHLC bars from incoming ticks.

Important timing behavior:
- the currently forming second is not pushed into the completed-S1 ring until a later tick arrives in a different second;
- therefore entry-quality calculations are based on completed second buckets;
- the S1 ring capacity is 128 completed seconds.

The quality calculation uses completed S1 closes and highs/lows to derive:
- signed displacement;
- total path travel;
- directional efficiency = `abs(displacement) / total travel`;
- recent high-low range;
- direction-turn count.

A BUY candidate must satisfy:
- displacement in BUY direction >= $0.15;
- efficiency >= 0.70;
- recent range >= $0.50;
- turns <= 9.

A SELL candidate requires the symmetrical negative displacement plus the same efficiency/range/turn conditions.

This gate therefore favors a fast, directional, relatively efficient short-horizon move rather than a noisy threshold touch.

## 6. Strategic regime gate

Before S1 qualification, the prospective entry must pass the strategic regime gate.

### Spread
Current:
`(Ask - Bid) / SYMBOL_POINT <= 25`

If above the cap, entry is blocked.

### ATR
R9 obtains M5 ATR(14) from the **previous completed M5 bar**, not the currently forming bar.

If ATR is missing/invalid and fail-closed mode is enabled, entry is blocked.

### Session-adaptive minimum
The completed M5 ATR must be at least the minimum assigned to the current session.

R9's built-in session classifier has only four states:
- OFF;
- LONDON;
- LONDON/NEW-YORK OVERLAP;
- NEW YORK.

London local window:
- 08:00 through 16:30 local London time.

New York local window:
- 08:00 through 17:00 local New York time.

The code contains explicit UK and US DST calculations.

The session does not independently prohibit trading. It changes the ATR minimum. OFF-session trading is still possible if its stricter ATR requirement and all other gates pass.

## 7. Entry decision and execution

When no R9 position is open and an armed boundary is crossed:

### BUY path
- live Ask must be >= frozen minute buy threshold;
- regime gate must pass;
- S1 quality must pass for positive direction;
- R9 sends a market BUY.

### SELL path
- live Bid must be <= frozen minute sell threshold;
- regime gate must pass;
- S1 quality must pass for negative direction;
- R9 sends a market SELL.

Position volume is normalized to broker min/max/step.

### Initial SL
For BUY:
- nominal SL = current Bid - $0.30.

For SELL:
- nominal SL = current Ask + $0.30.

The actual stop distance is the larger of:
- configured $0.30;
- broker stop-level distance plus one tick when broker-stop protection is enabled.

Prices are normalized to the symbol's trade tick size.

There is no fixed take-profit order.

## 8. Position lifecycle

R9 manages one matching symbol/magic position at a time.

### Maximum hold
If elapsed position time reaches 30 seconds, R9 sends a market position close.

### Trailing
Trailing does nothing until favorable excursion reaches $0.10.

After activation:
- BUY candidate stop = current Bid - $0.03;
- SELL candidate stop = current Ask + $0.03.

Broker stop-level constraints are respected.

The stop is only moved in the favorable/tightening direction; it is never loosened.

A broker-side initial/trailing stop can therefore close a position before the 30-second maximum hold.

## 9. Same-minute opposite-side rearm

After R9 detects that its previous position has disappeared:

If the exit occurred while the current tick is still in the same minute cycle:
1. if fewer than three rearms have already occurred, increment rearm count;
2. arm **only the side opposite the position that just closed**;
3. retain the original minute's frozen buy/sell bracket thresholds.

Examples:
- previous SELL closed -> BUY side becomes eligible;
- previous BUY closed -> SELL side becomes eligible.

If the max rearm count is reached, nothing further is armed for that minute.

If the position is discovered closed after the minute has changed, the old cycle is not rearmed; the next minute cycle establishes fresh boundaries.

This makes the engine capable of rapid alternating participation during intraminute reversals/continuations.

## 10. OnTick processing order

Operationally the main `Reconcile()` state machine is:

1. update/create completed-S1 bucket state;
2. detect/reset new-minute virtual bracket;
3. inspect whether the EA currently has a symbol/magic position;
4. if position exists:
   - remember its side;
   - manage max-hold/trailing;
   - return without evaluating a fresh entry;
5. if a position existed on the prior tick but is now gone:
   - process same-minute opposite-side rearm;
   - return;
6. otherwise evaluate a fresh bracket crossing and entry gates.

That return structure is material to parity: close detection/rearm and fresh entry do not all occur as one unconstrained operation on the same OnTick call.

## 11. Broker/execution behavior

R9 uses MT5 `CTrade` and:
- magic number 5559;
- synchronous mode;
- symbol-specific filling mode;
- max deviation 20 points;
- broker volume min/max/step normalization;
- symbol tick-size price normalization;
- broker stop-level awareness;
- trade retcode acceptance for DONE, PLACED, DONE_PARTIAL, and NO_CHANGES.

This means exact broker symbol properties are part of actual execution behavior.

## 12. TickLogger v1.92 instrumentation

The logger clone retains the R9 trading state machine and writes per-tick research state into MT5 `FILE_COMMON`.

It records, among other fields:
- millisecond timestamp;
- Bid/Ask/Last;
- tick volume / real volume / flags;
- spread;
- minute cycle and second;
- frozen buy/sell thresholds;
- pending/rearm state;
- S1 displacement / efficiency / range / turns;
- completed ATR;
- session;
- gate-open state;
- position state and side;
- entry price;
- running MFE/MAE;
- current stop;
- trail-armed state;
- event marker.

The logger's intended purpose is instrumentation; the source and Project history state it does not intentionally change the underlying R9 entry/exit decisions.

## 13. What R9 does NOT contain

The inspected R9 source contains no:
- multi-specialist architecture;
- Australia/Asia/Russia/India/Middle-East/Europe specialist router;
- external economic/news calendar;
- Fed/news-event specialist;
- daily profit target;
- daily loss governor;
- weekly loss governor;
- account-equity governor;
- prop-firm maintenance controller;
- dynamic lot sizing;
- MUWHAHA lot ladder;
- balance-based scaling;
- martingale;
- grid recovery;
- fixed take-profit;
- machine-learning model;
- external Python inference;
- multi-symbol/intermarket logic.

Those are therefore future DELTA layers, not hidden R9 functionality.

## 14. Why R9 is highly path-dependent

R9 combines several tick-order-sensitive mechanisms:
- live Ask/Bid boundary crossing;
- live spread rejection;
- custom completed-second bars;
- direction/efficiency/turn calculations;
- completed-M5 ATR gating;
- broker-side SL/trailing interaction;
- 30-second lifecycle timing;
- exact exit-detection tick;
- same-minute opposite rearm state.

Consequently, two feeds can share very similar M1 bars yet produce materially different R9 trades because intraminute quote chronology, spread, threshold timing, and lifecycle events differ.

This code-level property is consistent with the observed R9 evidence:
- REAL contains more total trades than SYNTH;
- REAL has much shorter average holds and much worse conversion/economics;
- the problem is not simply lack of opportunity count.

## 15. DELTA reconstruction contract

For DELTA, the R9 baseline can be represented as six separable functional layers:

1. **Opportunity geometry** — minute midpoint ± $0.15 virtual bracket.
2. **Regime eligibility** — spread + session-adaptive completed-M5 ATR.
3. **Microstructure entry quality** — completed-S1 displacement/efficiency/range/turns.
4. **Execution** — Bid/Ask-triggered market orders, broker normalization and costs.
5. **Hold/harvest** — hard SL, +$0.10 activation, $0.03 trail, 30-second max hold.
6. **Rearm state machine** — opposite-side same-minute re-entry up to three times.

These six layers are the canonical R9 functional decomposition for future causal Python parity and DELTA candidate research.

## 16. Cross-reference conclusion

The inspected Gamma baseline source, R9 TickLogger source, Project history, Strategy Tester inputs, and historical Drive R9 reconstruction agree on the behavior-critical mechanics above.

Where a cross-feed Python reconstruction cannot reproduce broker-specific Point/Digits, stop-level, filling, commission, or OnTick chronology exactly, it must be labeled an R9-style reconstruction rather than byte/execution parity.

## 17. Legacy Gamma closure

The owner-authorized Gamma inspection exception is now complete.

**Status:** `CLOSED_AFTER_R9_SUMMARY`

DELTA must use this durable summary and the registered R9 source identities going forward. Do not read Gamma or other prior internal lineage material again unless the owner explicitly authorizes another exception.
