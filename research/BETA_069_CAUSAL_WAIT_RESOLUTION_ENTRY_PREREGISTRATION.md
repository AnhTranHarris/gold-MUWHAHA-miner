# BETA069 — Causal WAIT→Resolution→Entry

**Status:** PREREGISTERED / NOT TESTED  
**Parent:** BETA065 proposal clocks  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

BETA067/068 showed friction is predictable but direction is not. BETA069 therefore stops predicting 30-second direction at the original proposal instant.

For every existing BETA065 proposal, test WAIT horizons of **1, 3, and 5 seconds**. At the wait horizon, observe the first real source quote at/after the horizon. Direction is then resolved from the observed midpoint displacement since the original proposal. To prevent same-quote hindsight, execution occurs on the **next source ordinal**.

Two causal interpretations are tested:
- **CONTINUATION:** enter in the direction of the observed displacement.
- **REVERSAL:** enter against the observed displacement.

Entry is admitted by one economic state variable: `abs(observed displacement) / delayed entry spread`, with a small preregistered threshold grid. No extra technical confirmations are added.

The resulting position is held for a fixed 30 seconds after delayed entry. All P&L uses actual source Bid/Ask plus the established $0.02 round-trip research fee.

CAL selects the wait/mode/specialist/strength combination. A survivor needs ≥50 one-position trades, positive net, PF>1, positive average, and a neighboring strength threshold with the same sign. The policy is frozen before DIAGNOSTIC is opened.

This unit is specifically designed to answer whether *waiting for causal phase resolution* creates an edge that snapshot direction models could not discover.
