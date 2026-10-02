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

## Completion result

Across January–July, R026 harvested **7,593** first generic same-minute rearms that would have triggered after M30 KEEP-owned exits.

Frozen R9-lifecycle hypothetical result:

- total PnL: **-$1,581.49**
- average: **-$0.20828/trade**
- win rate: **43.79%**
- positive events: 3,325
- negative/zero events: 4,268
- negative months: **7 / 7**

Monthly hypothetical PnL:

- Jan -$239.01
- Feb -$208.74
- Mar -$282.75
- Apr -$188.94
- May -$259.05
- Jun -$203.30
- Jul -$199.70

## Preregistered slices

No preregistered one-dimensional recovery bin was robustly positive.

Wait time, prior hold, prior PnL, parent M30 state, rearm M30 state, rearm micro250 state, and session all remained net negative.

Most importantly:

**7,587 / 7,593 events had rearm-direction M30NetATR <= -0.35.**

The generic opposite-side same-minute rearm is therefore almost always trying to trade against the still-dominant M30 state after an M30 KEEP-owned exit.

## Decision

Keep full same-minute rearm suppression for the validated M30 KEEP-owned branch.

R026 authorizes **no release subset** and no threshold/timing retune.

The next leverage question is whether generic same-minute rearms elsewhere in the P01/R9 surface are also toxic when their entry direction is opposed by M30.

That broader class must be harvested before any generalized rearm governor is tested.

Slice-analysis SHA-256:

`0688f955d561a9266b58c998a1bdb4c6a3d69b0b94c9ccc7158ddd4f44e7db2a`

