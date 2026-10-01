# BETA074 — Structural Residual-Duration Extension

**Status:** PREREGISTERED / NOT TESTED  
**Parent:** BETA071 structural event bus  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

BETA071–073 show that short structural holds remain negative, while the least-negative families generally improve as duration increases. BETA074 tests the simple hypothesis that confirmed M1/M5 structural transitions need longer than the prior 30–300 second windows to express their directional value.

No entry filter or learned model is added. The frozen BETA071 event identity is partitioned only by its already-existing mechanism and level timeframe. Fixed executable holds of 300, 600, 900 and 1800 seconds are compared.

CAL selection requires at least 50 one-position trades, positive after-cost net, PF > 1, positive average, and a neighboring duration or neighboring structural timeframe result with the same economic sign. The chosen policy is frozen before DIAGNOSTIC is opened.

A surviving candidate would be an Entry→Hold research candidate, not a completed exit/risk system. Human QA must show the structural level, confirmation time, entry quote, chosen residual-duration horizon, exit quote, PnL, and ownership blocks.