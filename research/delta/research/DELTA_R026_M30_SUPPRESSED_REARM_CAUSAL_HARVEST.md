# DELTA R026 — M30 KEEP-Owned Suppressed Rearm Causal Harvest

**Status:** PREREGISTERED HARVEST / NO RELEASE-POLICY TESTING  
**Parent:** R025 validated M30_KEEP_OWNED component  
**Surface:** P75  
**Months:** January–July 2026  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose

Measure the first generic same-minute R9 rearm that would have occurred after an **M30-only KEEP-owned** exit.

The shadow rearm is not executed in the actual path. Its hypothetical result is scored separately under the frozen R9 stop/trail/30-second lifecycle.

R026 does not harvest P01-owned exit descendants.

## Causal fields

- prior M30-owned trade PnL and hold time
- exit-to-shadow-rearm wait
- second inside minute
- parent H1NetATR / M30NetATR / micro250 impulse
- shadow-rearm micro250 / micro1000 impulse
- shadow 3-second displacement
- shadow H1NetATR / M30NetATR
- spread / session
- hypothetical shadow PnL / hold / winner flag

## Preregistered descriptive bins

Wait:
- <=250 ms
- 251–1000
- 1001–3000
- 3001–10000
- >10000

Prior hold:
- <=1s
- >1–5s
- >5–15s
- >15s

Prior PnL:
- <=0
- >0

Parent M30NetATR:
- >0.35–0.70
- >0.70–1.30
- >1.30

Rearm M30NetATR:
- <=-0.35
- >-0.35–0
- >0–0.35
- >0.35

Rearm micro250:
- <=-0.55
- >-0.55–0
- >=0–0.55
- >=0.55

Session uses the existing causal session code.

## Research rule

R026 is harvest-only. Any recoverable rearm subset is `HYPOTHESIS_ONLY`.

A release rule may not be tested until a new preregistered replay unit freezes its logic and thresholds.

## Execution source

`r026_m30_suppressed_rearm_harvest.py`

SHA-256:

`46213ba98ee1a8b79ee6b8d0be9336b83b4d0c5ac5cde3fb9adbef0a7fe7ae49`

## Drive

Doc:
https://docs.google.com/document/d/1zGkP6JM0C6h07s8hAuP4_du1b0_Mtzp5qFzSPXHhg1Y/edit

Workbook tabs:
- `47 R026 Prereg`
- `48 R026 Monthly Summary`
- `49 R026 Slice Matrix`
