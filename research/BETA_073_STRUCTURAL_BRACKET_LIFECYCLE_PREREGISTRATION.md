# BETA073 — Structural Bracket Lifecycle

**Status:** PREREGISTERED / NOT TESTED  
**Parent:** BETA071 structural entries  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

BETA071 and BETA072 indicate that aggregate fixed-horizon direction remains negative, while BETA072 can identify a very sparse positive 120-second tail. BETA073 tests whether the structural event bus has exploitable asymmetric excursion geometry without changing the entry clocks.

The entry bus is frozen to BETA071. No learned score is required to enter. Each standalone mechanism is replayed with stop-loss dollars {1.0, 1.5, 2.0, 3.0}, take-profit dollars {1.0, 2.0, 3.0, 5.0}, and max-life {120, 300}s. All are 0.01-lot / nominal one-ounce research cash distances and include the existing $0.02 round-trip fee. Entries and exits use actual executable Bid/Ask quotes.

CAL chooses only if a mechanism/bracket has >=50 one-position trades, net >0, PF>1, positive average, and an adjacent stop/target/life configuration with the same economic sign. Freeze before DIAGNOSTIC.

This is a HOLD/EXIT attribution test. It does not retroactively improve BETA071 entry accuracy and cannot be reported as entry alpha if it succeeds. Human QA, if earned, must show the full lifecycle: structural setup, entry quote, stop/target/max-life, exit reason, exit quote, PnL, and ownership blocking.