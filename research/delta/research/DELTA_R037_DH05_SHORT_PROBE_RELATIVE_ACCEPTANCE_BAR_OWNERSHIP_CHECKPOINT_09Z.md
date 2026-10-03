# DELTA R037 — Short-Probe Relative Acceptance-Bar Ownership Causal Challenger — Checkpoint 09Z

**Status:** COMPLETE MATERIAL CAUSAL CHALLENGER / NON-PROMOTING / INDEPENDENT VALIDATION REQUIRED  
**Unit:** R037_DH05_SHORT_PROBE_RELATIVE_ACCEPTANCE_BAR_OWNERSHIP_CHALLENGER_REPLAY_NON_PROMOTING  
**Parent:** R037_DH05_GENERATOR_RELEASE_TOPOLOGY_PROVENANCE_CHECKPOINT_09Y  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Recovery / timeout context

This unit resumed from the live durable cursor rather than rerunning earlier science. Checkpoint 09Y was already durable and the 09Z producer had already been preregistered at commit `74964e401c654448ac2dc39f83ea70a9dcef4ee3`.

The official replay used exact local Git-blob matches for:
- the 09Z producer;
- `delta_r037_dh05_runtime_primitives.py`;
- `delta_r037_dh05_conditional_failure_clock_challenger_replay.py`.

The canonical January gzip matched the locked SHA before execution. The process ran with a fresh Numba cache, Python faulthandler enabled, atomic result output, and a hard external 120-second timeout.

## Predeclared structural rule

From durable 09Y provenance:

`max_probe_age_s < acceptance_tf_seconds`

routes ownership as follows:

- **short probe relative to acceptance bar:** release the upstream generator at FAILURE_CANDIDATE while the downstream failed-break episode continues independently;
- **otherwise:** retain SERIAL_POST_QUAL ownership.

Selected short-probe vectors:
- S05
- S09
- S16

Serial-control vectors:
- A03
- S06
- S10

No numeric threshold was fitted or changed. The rule compares two already-frozen durations.

## Runtime provenance

Producer:
`research/delta/experiments/delta_r037_dh05_short_probe_relative_acceptance_bar_ownership_challenger.py`

- producer commit: `74964e401c654448ac2dc39f83ea70a9dcef4ee3`
- producer blob: `026f8685427ca3264582370182a8baeed424b95e`
- producer SHA-256: `7b46073de19242ce7e7f865bc7ed6730305693dd1e5474f835691e3f5f5a241f`
- canonical January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Stage-A ticks: **4,205,709**
- raw runtime result SHA-256: `236148af18566855bd276a4df2b61d4d404088d0ca987cd6f868c1de344d3a43`
- elapsed: **15.79 s**
- peak RSS: **697,964 KB**
- process exit: **0**
- hard timeout: **120 s**
- episode overflow: **0**
- signal overflow: **0**
- max concurrent failed-break episodes: **2**

## Control reproduction

The committed SERIAL_POST_QUAL control reproduced exactly before the routed challenger was scored.

Control:
- total funnel absolute error: **978**
- aggregate executable trade-count absolute error: **336**

Control stage errors:
- probe 642
- qualified 55
- accepted 24
- failure 63
- reentry 34
- reclaim 34
- reversal 63
- signal 63

## Causal challenger result

Routed candidate:
- total funnel absolute error: **782**
- executable trade-count absolute error: **335**

This is:
- **196 fewer funnel errors**
- **20.04% lower total funnel error**
- **1 fewer executable-count error**

Candidate stage errors:
- probe **449**
- qualified **49**
- accepted **31**
- failure **56**
- reentry **37**
- reclaim **36**
- reversal **62**
- signal **62**

The causal replay therefore reproduces the 09Y provenance prediction of total error **782** exactly.

## Six-vector result

Stage order:
`probe / qualified / accepted / failure / reentry / reclaim / reversal / signal`.

- **A03** serial: 6686/998/212/786/441/268/192/192; **192 trades / 77 wins / -$45.39**
- **S05** short-probe decoupled: 7818/315/34/281/56/20/9/9; **9 / 5 / -$1.25**
- **S06** serial: 3561/1599/248/1351/1210/695/651/651; **649 / 274 / -$150.35**
- **S09** short-probe decoupled: 7856/219/44/175/65/41/11/11; **11 / 7 / -$1.13**
- **S10** serial: 6440/1300/205/1095/637/309/227/227; **227 / 103 / -$46.55**
- **S16** short-probe decoupled: 7778/134/53/81/33/19/8/8; **8 / 3 / -$2.09**

## S06 veto

Historical S06:
- 672 signals
- 615 trades
- 307 wins
- -$101.08

09Z S06:
- 651 signals
- 649 trades
- 274 wins
- -$150.35

These are identical to the serial control because S06 is not selected by the short-probe rule. Therefore the mandatory S06 deterioration veto is **false**.

This does **not** mean S06 parity is solved; it means 09Z does not worsen the existing serial-control S06 discrepancy.

## Scientific decision

Checkpoint 09Z passes the predeclared Stage-A challenger gate:
1. materially lower funnel error;
2. no executable trade-count deterioration;
3. no S06 deterioration relative to control;
4. no overflow or capacity artifact;
5. no numeric retuning.

However, the rule was harvested from the same six-vector Stage-A evidence in 09Y. Therefore this result is **not eligible for semantic promotion yet**.

**Decision:** carry forward only as a non-promoting challenger.

Do not:
- freeze the router as final DH05 semantics;
- integrate SORB;
- open August;
- optimize exits/economics;
- begin MQL5.

## Next bounded unit

`R037_DH05_SHORT_PROBE_OWNERSHIP_ANTI_OVERFIT_VALIDATION`

Purpose:
independently challenge the relative-duration ownership rule against evidence not used to derive the 09Y relation, while preserving the same frozen vectors and causal chronology. Only after that validation may promotion eligibility be reconsidered.
