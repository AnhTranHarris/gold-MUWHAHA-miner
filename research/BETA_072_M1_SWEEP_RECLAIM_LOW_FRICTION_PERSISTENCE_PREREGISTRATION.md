# BETA072 — M1 Sweep/Reclaim Low-Friction Persistence

**Status:** PREREGISTERED / DIAGNOSTIC STILL CLOSED  
**Parent:** BETA063 safe causal base; BETA071 supplies only the newly reconstructed structural event definition  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Why this unit exists

BETA071's standalone structural screen was negative at 30/60/120 seconds, but CAL diagnostics revealed a coherent longer-horizon basin specifically for **M1 sweep/reclaim reversal** when the known-at-entry spread is low enough.

The strongest CAL neighborhood was around:
- spread cap approximately $0.65;
- no or small minimum sweep overshoot;
- 5–15 minute persistence, strongest near 10 minutes.

This follow-up is explicitly CAL-designed. It therefore does not claim pristine out-of-sample discovery. Its value is whether a frozen rule survives the within-unit Jan11–Jan18 diagnostic without being changed.

## Mechanism

Use only M1 left2/right2 confirmed pivots. A pivot is active only after the two right bars have closed.

- High sweep: M1 trades above the active confirmed pivot high and the same completed M1 bar closes back below it -> primary side SHORT.
- Low sweep: M1 trades below the active confirmed pivot low and closes back above it -> primary side LONG.

The event is visible at the M1 right edge. Execution occurs on the first source tick strictly later.

## Bounded CAL grid

Execution spread cap: $0.60 / $0.65 / $0.70.  
Minimum sweep overshoot: 0.00 / 0.05 / 0.10 M1 ATR14.  
Hold: 300 / 600 / 900 seconds.

One-position chronological scheduler. Actual Bid/Ask, $0.02 round-trip fee.

## Freeze gate

At least 20 CAL one-position trades, positive net, PF > 1, positive average trade, and a positive adjacent spread/overshoot/horizon setting. Select the highest-net robust candidate, serialize it, and only then open DIAGNOSTIC.

The 20-trade floor reflects the natural capacity of a 10-minute one-position structural strategy over the two-day CAL wall (~10+ trades/day), rather than the 50-trade floor used for dense 30-second clocks.

## Diagnostic success required for human-facing QA candidate

The frozen policy must produce:
- at least 40 DIAGNOSTIC trades;
- positive after-cost net;
- PF > 1;
- positive average trade;
- no parameter changes after DIAGNOSTIC is opened.

If it passes, build a human-facing trace packet before any Jan–Jul expansion: setup ID, pivot confirmation, sweep/reclaim bar, side, overshoot/ATR, spread/cost decision, entry/exit quotes, holding age, P&L, and explicit skip/ownership reasons.

This remains research-only until reproducibility, BETA015 funded-risk, Coinexx real-tick parity, and owner MQL5 gates are satisfied.
