# BETA078 Human QA Checklist

Engineering QA: **80/80 assertions PASS**  
Candidate: **M5 FIRST_RETEST / level age 7–9 M5 bars / 1800-second hold**  
August: **SEALED**  
MQL5: **NOT AUTHORIZED**

## Manual review workflow

1. Open `BETA_078_HUMAN_QA_CASES.csv` and choose cases from each type: ADMITTED, REJECT_MATURITY, and REJECT_OWNERSHIP.
2. For an ADMITTED case, verify the level is a confirmed M5 pivot, the breakout precedes the retest, the retest event is RIGHT-edge observable, and entry occurs on the first later quote.
3. Confirm maturity admission is inclusive only for ages 7, 8, or 9 completed M5 bars.
4. Confirm a second eligible setup is blocked while the prior 1800-second position is still open.
5. Recalculate BUY P&L as `exit_bid - entry_ask - 0.02`; SELL as `entry_bid - exit_ask - 0.02`.
6. Verify the recorded exit is the first source quote at or after 1800 seconds from actual entry.
7. Review both largest winners and largest losers from every month; do not assess only favorable examples.
8. Reconcile monthly totals against `BETA_078_RESULTS.json` and the full selected ledger.

## Research interpretation boundary

This is a **human-QA research candidate**, not independently validated alpha. The maturity window was discovered on Jan–Jul, which are historically inspected. Human QA evaluates causality, implementation, accounting, state transitions, explainability, and reproducibility. It does not convert these Jan–Jul economics into out-of-sample evidence. August remains sealed for the blind gate after QA.
