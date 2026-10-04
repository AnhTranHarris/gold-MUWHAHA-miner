# DELTA R037 — Stochastic Transition-Confirmation Stage-A Screen — Checkpoint 17D

**Status:** COMPLETE / NO SCREEN SURVIVOR / FAMILY RETIRED  
**Family:** R037-STX-v1  
**Parent:** R037_RSI2_STAGE_A_SCREEN_CHECKPOINT_17C  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Frozen source hypothesis

This family tested an actual oscillator **transition**, rather than the prior RSI2 extreme-state entry. Slow stochastic 14/3/3 was computed only from completed Bid bars.

- C01 M1: %D exits 20/80.
- C02 M1: %K/%D crossover while %D remains in the extreme zone.
- C03/C04: the same two transition grammars on M5.

No stochastic parameter, threshold, timeframe, session, long/short split or exit was retuned after the result.

## Crash/timeout evidence

The preregistration and producer were committed at `df0cc09f4ad5c3c79b2f53db9f3b734c5ce541dd` and passed recovery CI run **37175742195** before compute.

The official frozen producer wrote a complete atomic result before the foreground wrapper/transport stalled. The result file is valid JSON and has SHA-256:

`67c6e52866cdd025a7f19541d2faa0f3b7416fa0f31e30517101290c2b4a5f21`

A non-scientific execution/determinism diagnostic using the **same committed producer, same canonical January data, and already-built cache** then exited normally in approximately **18.02 seconds** and reproduced the **identical result SHA-256 byte for byte**. Therefore the scientific output is accepted; the foreground timeout occurred after atomic result production and is not evidence of a failed or altered candidate replay. No third scientific replay was performed.

Producer blob:
`611c651e1c478716bf721fcac40f1c1183b6a3c1`

Producer SHA-256:
`6876a73c7a30e19bd04b63cba62f21f8de4d5a9a0412b38f0fc02d2be797043f`

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

## Results

Parent: **14,034 trades / 6,349 official wins / -$2,944.94 net**.

- **C01 M1 %D exit:** 941 proposals / 898 accepted; +876 trades / +391 wins / **-$183.35 net delta**; direct STX **-$188.59**; equity-DD +6.26%.
- **C02 M1 K/D extreme crossover:** 1,316 proposals / 1,245 accepted; +1,224 / +513 / **-$291.46**; direct **-$288.33**; equity-DD +9.86%.
- **C03 M5 %D exit:** 177 proposals / 169 accepted; +167 / +79 / **-$26.78**; direct **-$28.63**; equity-DD +0.91%.
- **C04 M5 K/D extreme crossover:** 243 proposals / 230 accepted; +225 / +92 / **-$58.50**; direct **-$57.86**; equity-DD +1.99%.

No configuration met the frozen -$2 net gate.

## Interpretation

Waiting for a stochastic reversal transition does improve selectivity versus the M1 extreme-state families, but it does not reverse the economics. The best M5 %D exit remains decisively negative.

Combined with Checkpoint 17C, this is sufficient evidence to stop spending candidate slots on generic oscillator-state or oscillator-transition families under the current 30-second initial-hold contract.

## Decision

**Checkpoint 17D = NO SCREEN SURVIVOR. RETIRE R037-STX-v1 from the active promotion path.**

Next: `R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`.

The next source family should be **price-action/structure transition confirmed** rather than another oscillator variant.
