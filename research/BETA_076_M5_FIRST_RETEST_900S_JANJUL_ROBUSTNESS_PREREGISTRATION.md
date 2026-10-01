# BETA076 — Frozen M5 First-Retest 900s Jan–Jul Robustness

**Status:** PREREGISTERED / NOT TESTED  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

BETA074's January CAL discovery showed M5 FIRST_RETEST positive at every tested longer duration: 300s +$4.62, 600s +$8.60, 900s +$33.83, 1800s +$38.71. Counts were below the 50-trade CAL gate, so no promotion occurred. The 900-second version is frozen here because it retains more events than 1800 seconds while remaining well inside the positive duration neighborhood.

BETA076 performs no policy search. It reconstructs the same causal M5-level break -> first accepted M1 retest state machine continuously across Jan–Jul, executes one global chronological one-position ledger, and holds each admitted trade exactly 900 seconds.

Jan–Jul have been inspected elsewhere in this project and are **not pristine OOS**. This is therefore a robustness and human-QA readiness gate only. August remains sealed for a later blind test.

Human-QA readiness requires: aggregate net > 0, PF > 1, positive average; at least 200 Jan–Jul trades; at least 4 of 7 calendar months positive; deterministic quote-side accounting and chronology QA. No parameter is changed after the monthly scorecard is observed.