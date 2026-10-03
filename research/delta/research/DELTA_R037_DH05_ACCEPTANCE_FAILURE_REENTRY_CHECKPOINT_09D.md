# DELTA R037 — DH05 Acceptance / Failure / Reentry Semantic Parity — Checkpoint 09D

**Status:** COMPLETE MATERIAL PARITY BREAKTHROUGH / FULL PARENT PARITY NOT YET ACHIEVED  
**Unit:** R037_DH05_ACCEPTANCE_FAILURE_REENTRY_SEMANTICS_PARITY_RECONSTRUCTION  
**Parent:** R032-C03_PLUS_DH02_S11_S08  
**Prior durable unit:** R037_DH05_BOUNDARY_PROBE_ATTEMPT_LEDGER_CHECKPOINT_09C  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB integrated replay:** NOT STARTED / BLOCKED

## Timeout/recovery state

The repeated message-delivery failures did not require a research restart. Live `delta/CURRENT_STATE.json`, GitHub commit history, the working workbook, and the Library January corpus all survived. This unit resumed only the first incomplete parity substep.

The diagnostic source was committed before official replay:

- source: `research/delta/experiments/delta_r037_dh05_acceptance_failure_reentry_parity.py`
- source commit: `1fc60c12c4c6aba74fb74c1d13e9241f63bb9977`
- source blob: `21ee0fa6d32f292f49549c7639aa0313174d23c3`
- canonical January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Stage-A ticks: **4,205,709**

No August data was accessed. No frozen DH05 numeric vector was changed.

## Source-grounded semantic defect found

The original DH05 white paper states that BREAK_ACCEPTED requires completed-bar persistence beyond the boundary plus normalized displacement, and that FAILURE_CANDIDATE is the alternate branch when the original breakout has not been accepted or has been negated.

Checkpoint 09C was still evaluating acceptance after the event had already entered later failure/reentry states. That was inconsistent with the frozen state grammar.

This checkpoint therefore tested bounded semantic interpretations only.

The strongest reconstructible interpretation is:

1. BREAK_ACCEPTED may be evaluated **only while the event remains a qualified PROBE**.
2. `acceptance_disp_atr` measures signed directional displacement of the **completed acceptance bar body** (`close-open`) normalized by the event M5 ATR.
3. The completed acceptance-bar close must remain beyond the original boundary.
4. The primary max-failure clock continues to start at FAILURE_CANDIDATE. Starting it only at REENTRY was retained as a diagnostic, not promoted.

## Material parity improvement

Compared with the frozen Checkpoint-09C reconstruction:

| Metric | 09C-style baseline | 09D leading semantic | Improvement |
|---|---:|---:|---:|
| First five funnel-stage absolute error | 3,012 | **1,749** | **41.93% lower** |
| ACCEPTED absolute error | 1,070 | **70** | **93.46% lower** |
| REENTRY absolute error | 521 | **159** | **69.48% lower** |

This is a reconstruction breakthrough, not an economic backtest breakthrough.

## Six-vector fingerprint

Stage order:
`probe / qualified / accepted / failure / reentry / reclaim / reversal / signal`

- **A03** target 6731/1009/207/797/432/266/187/187; actual **6824/899/214/685/378/228/165/165**
- **S05** target 7875/318/28/290/51/15/9/9; actual **7709/246/38/208/44/15/6/6**
- **S06** target 3470/1606/245/1358/1211/683/617/617; actual **3607/1607/253/1354/1199/687/645/645**
- **S09** target 7748/208/40/168/61/40/9/9; actual **7659/162/50/112/44/30/7/7**
- **S10** target 6496/1316/202/1106/623/294/206/206; actual **6581/1226/212/1014/569/275/198/198**
- **S16** target 7870/135/43/92/37/18/8/8; actual **7658/111/68/43/22/14/6/6**

S06 is especially informative: after the semantic repair it reaches **1,607 qualified / 253 accepted / 1,354 failures / 1,199 reentries / 687 reclaims** against historical **1,606 / 245 / 1,358 / 1,211 / 683**. The remaining S06 signal excess, 645 versus 617, is downstream of this repaired acceptance/failure/reentry block.

## Residual defect

Full DH05 parity is still not achieved.

Remaining aggregate stage absolute errors for the leading profile:

- probe: **782**
- qualified: **343**
- accepted: **70**
- failure: **395**
- reentry: **159**
- reclaim: **75**
- reversal: **65**
- signal: **65**

The next correct question is therefore not numeric tuning and not SORB integration. The remaining upstream discrepancy is concentrated in **probe qualification timing / event lifecycle reset semantics**, with downstream reclaim/reversal only eligible after that upstream parity is tightened.

## Decision

**Checkpoint 09D = QA PASS / MATERIAL PARITY BREAKTHROUGH / FULL HISTORICAL PARITY FAIL.**

Freeze as a parity hypothesis:

- symmetric two-bar confirmed M5 swing boundary from 09C;
- repeated causal same-boundary pre-failure probe-attempt ledger from 09C;
- BREAK_ACCEPTED only while the event remains a qualified probe;
- acceptance displacement as signed completed acceptance-bar body displacement / event M5 ATR;
- completed acceptance close must remain outside the boundary;
- failure-age clock starts at FAILURE_CANDIDATE.

Do not:

- retune frozen DH05 numeric vectors;
- claim historical DH05 parity;
- integrate R037-SORB yet;
- use August;
- begin MQL5;
- optimize mature exits.

Official result SHA-256:
`9b1ebf24e3f01dd52f9c9e0e19c4d966883f657570b3dd36892e9602e2615fb9`

Compact checkpoint manifest:
`research/delta/reference/DELTA_R037_DH05_ACCEPTANCE_FAILURE_REENTRY_CHECKPOINT_09D.json`

## Next bounded unit

`R037_DH05_PROBE_QUALIFICATION_CLOCK_AND_EVENT_LIFECYCLE_PARITY_RECONSTRUCTION`

Goal: tighten the residual probe/qualified/event-reset mismatch under the frozen 09C+09D semantic hypotheses before any downstream reclaim/reversal repair or official SORB integration.
