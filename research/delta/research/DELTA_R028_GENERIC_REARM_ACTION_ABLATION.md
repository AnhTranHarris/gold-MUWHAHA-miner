# DELTA R028 — Generic Same-Minute Rearm Action Ablation

**Status:** COMPLETE — NO MODELED-SURFACE SURVIVOR  
**Parent:** R025 M30_KEEP_OWNED  
**Evidence parent:** R027 generic-rearm harvest  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Frozen actions
- OPPOSITE_ONLY_CONTROL
- NO_REARM
- FRESH_TWO_SIDED using original frozen minute brackets
- SAME_SIDE_ONLY using original frozen minute brackets

Owned exits remain fully suppressed. Maximum ordinary rearm count remains three where rearm is allowed. No thresholds changed.

## Stage-A modeled results

P50:
- control net -$2,682.46
- NO_REARM -$2,408.07 (+$274.39) but only 74.79% trade / 78.77% winner retention: FAIL_ACTIVITY
- FRESH_TWO_SIDED -$3,594.49: FAIL_NET
- SAME_SIDE_ONLY -$3,396.71: FAIL_NET

P75:
- control net -$2,863.34
- NO_REARM -$2,571.31 (+$292.03) but only 74.42% trade / 78.77% winner retention: FAIL_ACTIVITY
- FRESH_TWO_SIDED -$3,803.09: FAIL_NET
- SAME_SIDE_ONLY -$3,599.80: FAIL_NET

P90:
- control net -$558.14
- NO_REARM -$490.89 (+$67.25) but only 71.33% trade / 74.39% winner retention: FAIL_ACTIVITY
- FRESH_TWO_SIDED -$745.44: FAIL_NET
- SAME_SIDE_ONLY -$706.94: FAIL_NET

Native diagnostic:
- NO_REARM equals control because control had no generic rearm.
- both alternate rearm direction policies added 10 trades and worsened net by about $2.09.

## Decision
Generic same-minute rearm local repair is stopped.

Suppression consistently improves loss metrics but violates activity preservation. Restoring activity through the same original frozen minute bracket — whether two-sided or same-side — worsens net.

The next research target is an independent opportunity replacement mechanism, not another local generic-rearm threshold/action tweak.

## Drive
Doc: https://docs.google.com/document/d/15ekw9SauWSqkmf6E6smxhAsmn-qFgxVT_VGxWuibCPk/edit
Workbook tabs: `53 R028 Prereg`, `54 R028 Results`

## Execution source
`r028_generic_rearm_action_ablation.py`
SHA-256: `c8dbe472c58c430f96e10277cb502a3b3e84f96b2321e103343eea7006d911cc`
