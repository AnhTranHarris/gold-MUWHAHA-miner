# DELTA R016 — Exact Confidence-Tier Jan–Jul Validation

**Status:** LEADING REFINEMENT ARCHITECTURE / NOT PROMOTED  
**Parent:** R014 exact rounded R010  
**Scope:** ENTRY + INITIAL-HOLD  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Selected tier

Base:
`I250 <= -0.55 OR H1NetATR > 0.35`

Moderate base condition:
- flip side;
- assign reversal ownership;
- suppress generic same-minute rearm after owned exit.

Extreme T06:
`H1NetATR > 0.70 AND I250 <= -0.90`

Extreme action:
- skip the entry;
- suppress the remainder of the current M1 opportunity.

## Exact Jan–Jul aggregate

| Object | Trades | Winners | GL | Net | Net improvement vs R9 | GL improvement | Trade retention | Winner retention |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R9 | 234,417 | 103,097 | -$78,244.86 | -$49,001.79 | — | — | 100% | 100% |
| R010 | 203,864 | 90,751 | -$67,676.50 | -$42,668.19 | 12.93% | 13.51% | 86.97% | 88.02% |
| R015-T06 | 198,029 | 87,978 | -$65,816.57 | -$41,531.29 | **15.25%** | **15.88%** | **84.48%** | **85.34%** |
| R015-T10 | 199,970 | 88,954 | -$66,390.37 | -$41,847.22 | 14.60% | 15.15% | 85.31% | 86.28% |
| R015-T18 | 201,223 | 89,539 | -$66,796.68 | -$42,114.53 | 14.06% | 14.63% | 85.84% | 86.85% |

T06 improves net in every month.

Monthly T06 net-loss improvement:
- Jan 17.50%
- Feb 14.21%
- Mar 14.74%
- Apr 11.81%
- May 18.70%
- Jun 16.56%
- Jul 12.89%

## Decision

T06 becomes the leading refinement architecture.

It is not promoted or locked:
- below the 30% scoped high-value target;
- far below the 80% promotion target;
- native sensitivity remains unresolved/failing from R010.

Next research: separate micro-only, H1-only, and dual-trigger ownership classes and determine whether their actions should differ.

## Provenance
- exact tier aggregate: `b86187a3039fc01c3b9cf46bb15b00b233269ca0be068192c16edf1116343e8e`
- R015 Stage-A: `7aab1fc59a85943d3032457e511b71f8b2eeafbfbabc18997c923fefbaba36a7`
- month script: `610e2f434c76cc77af811b6142dd681624aa684f4492337b028fd4156f1c365c`
- January script: `05376ce00c1e03daffb50ec86efff8dc96ae0175ffb031fc524bb5f9789f2bd9`

Drive:
https://docs.google.com/document/d/1VwR1ZhUjuJMM3HhmmCDJvIHTWdhxJ0YaCyPzfXN4a_M/edit
