# BETA078 — M5 Level-Maturity Retest × Hold Neighborhood

**Status:** PREREGISTERED / NOT TESTED AS A FORMAL UNIT**  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

The BETA076 postmortem found a transparent structural state worth formalizing: M5 first-retest entries whose broken confirmed level was neither fresh nor very stale. In the diagnostic audit, level ages 7–9 M5 bars had 427 one-position 900-second trades, small positive net, PF just above 1, and 4/7 positive months; the neighboring 7–10 window was also slightly positive.

That observation is **discovery leakage from Jan–Jul**. BETA078 therefore does not call Jan–Jul validation or OOS. It asks whether the immediate structural neighborhood is coherent enough to justify human-facing QA before August is ever opened.

Frozen neighborhood:
- level-age windows: 7–9, 7–10, 8–9 completed M5 bars;
- fixed executable holds: 600, 900, 1200, 1800 seconds;
- exact BETA076 M5 first-retest entry logic;
- no session, side, spread, ML, or extra confirmation filter.

A human-QA research candidate requires >=200 one-position trades, aggregate net >0, PF>1, positive average, >=4/7 positive months, and at least one adjacent maturity/hold cell with positive net/PF>1 and >=150 trades. The selected cell is for QA inspection only. It is not a promoted EA and it does not unlock August automatically.

Public break/retest implementations commonly retain explicit bars-since-break/retest lifecycle state rather than treating every old level identically; that supplies mechanism provenance only. The economic test remains our original quote replay.