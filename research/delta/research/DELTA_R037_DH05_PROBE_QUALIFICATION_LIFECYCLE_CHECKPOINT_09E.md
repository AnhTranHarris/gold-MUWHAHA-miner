# DELTA R037 — DH05 Probe Qualification Clock / Event Lifecycle Parity — Checkpoint 09E

**Status:** COMPLETE MATERIAL PARITY BREAKTHROUGH / FULL DH05 PARITY NOT YET ACHIEVED  
**Unit:** R037_DH05_PROBE_QUALIFICATION_CLOCK_AND_EVENT_LIFECYCLE_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_ACCEPTANCE_FAILURE_REENTRY_CHECKPOINT_09D  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB integrated replay:** NOT STARTED / BLOCKED

## Bounded question

Can the residual 09D probe/qualified mismatch be explained by the causal origin of `max_probe_age` and same-boundary attempt lifecycle semantics, without retuning any frozen DH05 numeric vector?

Frozen from 09C + 09D:
- symmetric two-bar confirmed M5 swing boundary;
- repeated causal same-boundary pre-failure probe-attempt ledger;
- BREAK_ACCEPTED only while the event remains a qualified probe;
- acceptance displacement = signed completed acceptance-bar body / event M5 ATR;
- completed acceptance close remains beyond the original boundary;
- max-failure clock starts at FAILURE_CANDIDATE.

No threshold was changed.

## Producer and crash-safety

Producer:
`research/delta/experiments/delta_r037_dh05_probe_qualification_lifecycle_parity.py`

Final producer commit:
`04356db0605033ab436e4d9513e9a56397778722`

Blob:
`e2ecd08b95b1538f4ce0403f9d73cb098c661c3a`

File SHA-256:
`76ddaacd56a27e1ea5a8e451bdf20280eb29047ee595291afa90126fbf35a2f9`

The first execution intentionally failed closed because its internal CONTROL_09D gate detected an acceptance-stage implementation defect before any result file was written. The defect was fixed and recommitted before official compute. The final producer writes through a temporary file, flushes/fsyncs, and uses atomic `os.replace` into the destination.

Canonical January source SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks:
**4,205,709**

Final bounded replay completed in approximately **9.6 seconds**.

## Tested semantic profiles

1. **CONTROL_09D** — original event-start clock governs stage-1 and stage-2 max-probe age.
2. **ATTEMPT_STAGE1_CLOCK** — every causal same-boundary re-attempt gets a fresh stage-1 qualification clock, but stage-2 still uses original event start.
3. **ATTEMPT_LIFECYCLE_CLOCK** — every causal same-boundary re-attempt gets a fresh clock, and the qualified stage-2 lifecycle stays anchored to that attempt.
4. **QUALIFIED_LIFECYCLE_CLOCK** — stage-1 uses the attempt clock, then stage-2 restarts max-probe age at the qualification instant.

All profiles retain the frozen max-failure clock starting at FAILURE_CANDIDATE.

## Result

The leading semantic interpretation is:

> **ATTEMPT_LIFECYCLE_CLOCK**

Meaning:

> `max_probe_age` is a property of the currently active causal same-boundary probe attempt, not the age of the original boundary event. A fresh causal re-attempt resets the probe clock; if that attempt qualifies, stage-2 remains anchored to that same attempt clock. `max_failure_age` remains unchanged and starts only at FAILURE_CANDIDATE.

### Aggregate six-vector parity

| Metric | 09D control | 09E attempt-lifecycle | Improvement |
|---|---:|---:|---:|
| Probe + qualified absolute error | 1,125 | **554** | **50.76% lower** |
| First five stages absolute error | 1,749 | **920** | **47.40% lower** |
| Downstream reclaim/reversal/signal error | 205 | **144** | **29.76% lower** |
| Total eight-stage absolute error | 1,954 | **1,064** | **45.55% lower** |

This satisfies the handoff carry-forward rule because the upstream lifecycle error falls materially **without compensating downstream deterioration**. Downstream error also falls.

## Six-vector fingerprint

Stage order: `probe / qualified / accepted / failure / reentry / reclaim / reversal / signal`.

- **A03** target 6731/1009/207/797/432/266/187/187; 09E **6731/1006/247/759/425/258/184/184**
- **S05** target 7875/318/28/290/51/15/9/9; 09E **7731/309/47/262/52/18/8/8**
- **S06** target 3470/1606/245/1358/1211/683/617/617; 09E **3579/1606/259/1347/1205/692/648/648**
- **S09** target 7748/208/40/168/61/40/9/9; 09E **7670/206/66/140/52/34/9/9**
- **S10** target 6496/1316/202/1106/623/294/206/206; 09E **6464/1306/222/1084/626/303/222/222**
- **S16** target 7870/135/43/92/37/18/8/8; 09E **7708/130/81/49/24/15/6/6**

Notable fingerprints:
- A03 probe count is now **exact** and qualifications are only 3 low.
- S06 qualifications are now **exact**.
- S09 reversal/signal are now **exact 9/9**.
- Reentry aggregate error falls from 159 to **39**.

## Residual defect

Full historical DH05 parity is still false.

The leading 09E remaining aggregate errors are:
- probe 525
- qualified 29
- accepted 157
- failure 170
- reentry 39
- reclaim 38
- reversal 53
- signal 53

Qualification timing is now nearly solved. The remaining upstream mismatch is concentrated in **event reset/boundary identity and accepted-versus-failure conversion**, especially in short-window vectors S05/S16 and the S06/S10 reversal tail.

## Decision

**Checkpoint 09E = QA PASS / MATERIAL PARITY BREAKTHROUGH / FULL PARITY FAIL.**

Carry forward as a frozen parity hypothesis:
- 09C width-2 M5 swing boundary;
- 09C repeated same-boundary pre-failure attempt ledger;
- 09D stage-gated body-displacement acceptance;
- **09E per-attempt probe lifecycle clock**.

Do not:
- retune vectors;
- optimize economics;
- repair mature exits;
- integrate SORB;
- access August;
- begin MQL5.

Compact result:
`research/delta/reference/DELTA_R037_DH05_PROBE_QUALIFICATION_LIFECYCLE_CHECKPOINT_09E.json`

Result SHA-256:
`39a64ba212124a84a7fe2df681171f330fde3661aa1ad8b204eb5c1d4b4d2eb9`

## Next bounded unit

`R037_DH05_EVENT_RESET_AND_BOUNDARY_IDENTITY_PARITY_RECONSTRUCTION`

Purpose: tighten the remaining probe-count and accepted/failure mismatch by testing only causal event-reset and boundary-identity persistence semantics under the now-frozen 09C + 09D + 09E interpretation. No numeric retuning and no downstream economic optimization.
