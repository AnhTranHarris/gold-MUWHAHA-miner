# DELTA R018 — GOV-018 Cycle-1 Monthly Formula Replay Results

**Status:** CYCLE-1 COMPLETE / P02 ADVANCES TO COMPONENT ABLATION / NO PROMOTION  
**Parent:** exact rounded R010  
**Scope:** ENTRY + INITIAL-HOLD / DIRECTION OWNERSHIP  
**Replay:** February–July 2026 P75 DST-aware  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Leader

P02:
`H1NetATR > 0.35 OR M30NetATR > 0.35 OR micro250 impulse <= -0.55`

Action remains:
- flip intended R9 side;
- suppress generic same-minute rearm after an owned trade.

P02 beat P01 exact rounded R010 on net in every February–July month.

## Aggregate Feb–Jul

R9:
- trades 201,044
- winners 88,500
- net -$41,963.14
- gross loss -$67,262.94

P01 exact rounded R010:
- trades 175,038
- winners 77,788
- net -$36,707.08
- gross loss -$58,364.15
- net-loss improvement 12.53%
- gross-loss improvement 13.23%
- trade retention 87.06%
- winner retention 87.90%

P02:
- trades 168,285
- winners 74,844
- net -$35,560.55
- gross loss -$56,220.29
- net-loss improvement 15.26%
- gross-loss improvement 16.42%
- trade retention 83.71%
- winner retention 84.57%

Incremental P02 vs P01:
- net +$1,146.53
- gross-loss reduction +$2,143.86
- +2.73pp net-loss closure
- +3.19pp gross-loss closure
- -3.36pp trade retention
- -3.33pp winner retention

## Decision

P02 advances to causal component ablation, not promotion.

The incremental gain is consistent but below the GOV-007 +10pp escalation threshold.

Cycle-2 must separate:
1. M30-only direction flip value;
2. M30-only ownership/rearm suppression value;
3. M30-only skip/avoidance value;
4. M30/H4 regime-dependent ownership.

No threshold retuning is authorized inside the ablation.

## Drive

https://docs.google.com/document/d/1Qw9HdcpvGOFZPYkzIYc4OuA_13thQne8NwQ27bxbC6s/edit

Heavy synthesis workbook:

https://docs.google.com/spreadsheets/d/1CF15bSAjCDfIyvX3FaaTfjJqRulBZsIhfDUWuIaTSIE/edit
