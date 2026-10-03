# DELTA R037 — DH05-S06 Parity Reconstruction — Reversal/Rebreak Fingerprint Checkpoint 02

**Status:** COMPLETE BOUNDED QA UNIT / PARITY STILL NOT ACHIEVED  
**Parent:** R032-C03_PLUS_DH02_S11_S08  
**Prior checkpoint:** DELTA_R037_DH05_S06_PARITY_CHECKPOINT_01  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Window:** Stage-A only  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Question tested

Can the frozen historical DH05 family fingerprint be recovered by repairing only the reversal/rebreak implementation semantics, without changing any frozen vector parameter?

The six M5-swing vectors remain the fingerprint:

| Vector | Historical executed trades |
|---|---:|
| DH05-A03 | 306 |
| DH05-S05 | 51 |
| DH05-S06 | 615 |
| DH05-S09 | 119 |
| DH05-S10 | 206 |
| DH05-S16 | 24 |

## Causal semantic variants tested

The bounded replay held all numeric vectors fixed and varied only implementation semantics that were ambiguous because the original transient generator is missing:

- reversal pivot = none / immediately preceding completed reversal-bar extreme / reclaim-bar extreme / first-reentry-bar extreme;
- reversal may or may not be confirmed on the same completed bar that confirms reclaim;
- failed-break clock starts from probe, causal re-entry, or reclaim;
- current M5-swing boundary may re-arm only after price causally returns to the pre-break side;
- M5 ATR remained the primary normalization hypothesis for the main fingerprint run;
- a bounded S5/S15/M1/M5 ATR comparison was run only as a diagnostic, not as parameter selection.

## New key finding — separate failure clock is directionally correct

The prior implementation measured the entire failed-break lifetime from the original probe timestamp.

Reconstructing `max_probe_age_s` and `max_failure_age_s` as separate clocks improves the family fingerprint materially.

Under M5 ATR, no-pivot constraint, same-bar reversal allowed, and the failure clock beginning at causal re-entry/failure state, representative executed-trade counts became:

- A03: **215** vs 306
- S05: **3** vs 51
- S06: **829** vs 615
- S09: **26** vs 119
- S10: **199** vs 206
- S16: **8** vs 24

S10 moving to **199 vs 206** is strong evidence that the old one-clock implementation was wrong.

However the whole family still fails parity, so this semantic repair is necessary-looking but not sufficient.

## Probe-expiry reinterpretation tested

A second causal state-machine interpretation treated `max_probe_age_s` as the end of the probe/acceptance-observation phase rather than automatic event death:

`PROBE -> qualified but not accepted by max_probe_age -> FAILURE_CANDIDATE -> wait for re-entry/reclaim under max_failure_age`

This improved A03 and S10 further relative to the old implementation, but S05/S09/S16 remained far too sparse and S06 remained too dense.

Therefore this rule alone also cannot explain the authoritative generator.

## ATR diagnostic

With the repaired failure-state clock and the same reversal semantics:

**M5 ATR**
- A03 215
- S05 3
- S06 829
- S09 26
- S10 199
- S16 8

**M1 ATR**
- A03 627
- S05 **51**
- S06 1488
- S09 225
- S10 423
- S16 81

M1 ATR reproduces the S05 trade count exactly but grossly over-produces the other vectors, especially S06. S15/S5 ATR references over-produce the family even more strongly.

Conclusion: a simple universal replacement of M5 ATR with another single ATR clock is rejected. The historical generator either used different stage-normalization semantics, different event-stage transitions, or both.

No ATR clock is being retuned or selected from these results.

## What is now ruled out

The following are insufficient to recover the authoritative family:
- changing only pivot definition;
- changing only same-bar vs next-bar reversal confirmation;
- changing only failed-break clock origin;
- changing only probe-expiry semantics;
- substituting one universal S5/S15/M1 ATR clock for M5.

## Exact next bounded unit

`R037_DH05_PARITY_STAGE_FUNNEL_DIAGNOSTIC_M5_SWING_SIX_VECTOR`

Instrument the six frozen M5-swing vectors and count, for each:

1. boundary probe starts;
2. probes reaching required excursion;
3. original-break acceptances;
4. failure candidates;
5. causal re-entries;
6. reclaim confirmations;
7. reversal confirmations;
8. executable signals;
9. sequential lifecycle trades.

Run the funnel under the current best causal state-machine interpretation, then compare where the historical target densities imply the missing semantics must sit.

The next unit must diagnose the stage responsible for the mismatch before any further semantic changes are tested.

## Gate

- DH05-S06 exact parity: **FAIL / NOT YET**
- other R032 specialist reconstruction: **BLOCKED**
- official R037 SORB integrated replay: **NOT STARTED / BLOCKED**
- SORB retuning: **PROHIBITED**
- August: **SEALED**
- MQL5: **NOT AUTHORIZED**
