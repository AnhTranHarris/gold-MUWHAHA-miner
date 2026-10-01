# BETA078 Human QA Checklist

Engineering QA: **102/102 assertions PASS**  
Candidate: **M5 FIRST_RETEST / level age 7–9 M5 bars / 1800-second hold**  
August: **SEALED**  
MQL5: **NOT AUTHORIZED**

## Manual review workflow

1. Open `BETA_078_HUMAN_QA_CASES.csv`; review cases from **ADMITTED**, **REJECT_MATURITY**, and **REJECT_OWNERSHIP**.
2. For an ADMITTED case, verify the displayed M5 level was confirmed before the break, the break precedes the retest, the retest is visible only at the completed M1 right edge, and the entry is the first later quote.
3. Confirm maturity admission is inclusive only for level ages **7, 8, or 9 completed M5 bars**.
4. For REJECT_OWNERSHIP, verify the referenced blocking trade was still open at the rejected entry timestamp.
5. Recalculate BUY P&L as `exit_bid - entry_ask - 0.02`; SELL as `entry_bid - exit_ask - 0.02`. The QA suite also verifies the equivalent calculation in integer quote mills.
6. Verify exit is the first source quote at or after **1800 seconds from actual entry**, not from signal time.
7. Review largest winners and largest losers from every month, plus the explicit exact-flat case.
8. Reconcile monthly totals with `BETA_078_RESULTS.json` and the complete selected ledger.

## Accounting normalization

One July trade is exactly flat in integer quote units. Earlier floating arithmetic represented it as approximately ±1e-13 and could change the win count without changing economics. QA V2 normalizes `|PnL| <= 1e-9` to flat. This is an accounting classification correction, not a strategy change.

## Research interpretation boundary

This is a **human-QA research candidate**, not independently validated alpha. The maturity window was discovered on Jan–Jul, which are historically inspected. Human QA evaluates causality, implementation, accounting, state transitions, explainability, and reproducibility. It does not convert Jan–Jul economics into out-of-sample evidence. **August remains sealed** for the blind gate after QA.