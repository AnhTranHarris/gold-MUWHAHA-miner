# DELTA R033 — A01 Incremental Density Toxicity and Interaction Harvest

**Status:** HARVEST COMPLETE / NO BEHAVIOR TEST  
**Parent:** R032-C03  
**Surface:** P90  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Broad result
- A01-only signals: 682
- executed A01-only entries: 129
- wins: 56
- win rate: 43.41%
- net: -$30.03
- mean: -$0.23279

Broad A01 density is toxic and must not be imported wholesale.

## Descriptive interaction hypotheses
The strongest mechanism-first cell is **NESTED_S5_S15**:
- S5 NetATR in (0.43606557, 1.39348837]
- S15 NetATR in (1.03122498, 1.78181818]
- 10 events / 8 wins / +$1.33 / seven distinct days.

Other positive same-sample cells:
- S5_EFF_DISP: 11 events, +$1.26
- S1_TIME: 9 events, +$0.94
- MICRO_M1: 12 events, +$0.93
- H1_S5: 8 events, +$1.71

These are **HYPOTHESIS_ONLY** because they were selected after a pairwise scan. No behavior rule was tested or promoted.

## Next
R034 must preregister a small fixed causal-pocket set and validate it out of sample, preferably on the later-January interval after 2026-01-18T12:00:00Z with prior January used only for causal indicator/state warmup.

## Provenance
- event CSV SHA-256: `66db344df25342f4a296f6b1a943701febd7d4c65ccb1fcd6b830cfff11aeb42`
- summary JSON SHA-256: `af4068474a788d94d432722b487836009d22cf570f2e6b2bb8e169f3ff6ca60d`
- workbook tab: `62 R033 A01 Harvest`

Drive doc:
https://docs.google.com/document/d/15J3lOVQJ0OYVJmtyn4l9PMl1IB5YBPeWUOleGn_ovGw/edit
