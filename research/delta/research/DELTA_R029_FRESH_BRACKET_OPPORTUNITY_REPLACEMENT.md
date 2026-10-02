# DELTA R029 — Fresh-Bracket Opportunity Replacement Ablation

**Status:** COMPLETE — NO MODELED-SURFACE SURVIVOR  
**Parent:** R025 M30_KEEP_OWNED  
**Evidence parents:** R027, R028  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Preregistered configurations
- OPPOSITE_ONLY_CONTROL
- NO_REARM_CONTROL
- RECENTER_IMMEDIATE
- RECENTER_NEXT_S5
- RECENTER_NEXT_S15

The three replacement variants discard the stale original post-exit minute bracket and create a fresh two-sided ±$0.15 bracket centered on current price at the specified causal reset clock. All R9 quality/session/ATR gates and P01/M30 ownership logic remain frozen.

## Stage-A result

No replacement variant improved the exact OPPOSITE control on P50, P75, and P90.

P50:
- control -$2,682.46
- no-rearm -$2,408.07 but FAIL_ACTIVITY
- immediate -$3,560.03
- S5 -$3,276.29
- S15 -$3,071.77

P75:
- control -$2,863.34
- no-rearm -$2,571.31 but FAIL_ACTIVITY
- immediate -$3,800.57
- S5 -$3,499.95
- S15 -$3,288.96

P90:
- control -$558.14
- no-rearm -$490.89 but FAIL_ACTIVITY
- immediate -$762.22
- S5 -$689.57
- S15 -$653.13

Recentered variants restore substantial activity, often above R9 trade count, but losses worsen materially. A slower reset reduces damage monotonically but never becomes beneficial.

Native diagnostic produced only a trivial +$0.11 for S15 on one extra trade; modeled-surface failure dominates.

## Decision
Retire the post-exit same-minute bracket-replacement family.

R027 showed generic rearms are broadly toxic. R028 showed changing their direction rule does not fix them. R029 shows even discarding the stale bracket and recentering a fresh bracket does not fix them.

The next activity source must be an **independent first-entry/specialist opportunity**, not any post-exit same-minute re-entry grammar.

## Drive
Doc: https://docs.google.com/document/d/1Ulq-TX-cqsgJON1NbPybpPbgunyx1dRa6EhaIoQEywk/edit
Workbook tabs: `55 R029 Prereg`, `56 R029 Results`

## Execution source
`r029_fresh_bracket_replacement.py`
SHA-256: `0c145e993f443424788b2ea39addcd2e9f489db6d2653b025ce7aeb52bf71080`
