# DELTA R037 — Conditional Failure-Clock Challenger Replay — Checkpoint 09T

**Status:** COMPLETE NEGATIVE QA / 09S PROVENANCE ROUTER FALSIFIED CAUSALLY  
**Unit:** R037_DH05_CONDITIONAL_FAILURE_CLOCK_CHALLENGER_REPLAY_NON_PROMOTING  
**Parent:** R037_DH05_SIGNAL_TRADE_GAP_PROVENANCE_ACCEPTANCE_CLOCK_CHECKPOINT_09S  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Purpose

Checkpoint 09S found a striking historical fingerprint: routing preserved Checkpoint-09 semantics by acceptance/reversal timeframe reduced aggregate historical count error from the best live 09L value of 304 to 61. Because that router was assembled from historical fingerprints rather than current causal event replay, this unit tested it as a non-promoting challenger on canonical Stage-A ticks.

No numeric vector threshold was changed.

## Exact rebuild provenance

Producer:
`research/delta/experiments/delta_r037_dh05_conditional_failure_clock_challenger_replay.py`

- final producer commit: `cf74119286100230bca2a5f8dc9c6909e85b23bf`
- producer blob: `0749a0f326ff0a81006f7234f5065963e26e8dab`
- producer SHA-256: `2b041a90fe5fa8e9ea13e4489a36e309e48dfae06e21a1050037cbd6dd8101a7`

Minimal runtime helper:
`research/delta/experiments/delta_r037_dh05_runtime_primitives.py`

- helper commit: `fdebfe5f04d10ac6b35a8cf96c7e258b7cc75985`
- helper blob: `328b16a80cf5bff58734a556561625adf89100ae`
- helper SHA-256: `5a53170d1a3f460a299a53aeaf067d4af5ac49db2726f576569d6c643b6f0848`

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**.

Official replay:
- exit code: **0**
- elapsed: **15.18 s**
- peak RSS: **698,640 KB**
- runtime result SHA-256: `ff906dfd560902f564e5b6bcc586c37979d85e69db73aa9773773b224630e9bd`

The official exact-byte replay reproduced the earlier pre-durability diagnostic result bit-for-bit.

## Frozen causal base

The replay preserved:
- 09C symmetric two-bar confirmed M5 swing boundary;
- 09E repeated same-boundary attempt ledger with per-attempt `max_probe_age`;
- 09F acceptance-bar completion strictly after qualification;
- 09D signed completed acceptance-bar body displacement / event M5 ATR;
- one-position-at-a-time R9/Coinexx execution;
- position-observation latch as a reported execution control.

The CONTROL_CURRENT_NEUTRAL branch exactly reproduced the frozen POST_QUAL funnel before challengers were scored.

## Main result

### Frozen current neutral control

Generator signals:
- A03 192
- S05 9
- S06 651
- S09 11
- S10 227
- S16 7

Aggregate signal-count error versus historical trades: **338**.  
Position-observation-latch trade error: **336**.

S06:
- 651 generator signals
- 649 trades
- 274 wins
- -$150.35 net

Historical S06:
- 672 signals
- 615 trades
- 307 wins
- -$101.08 net

### 09S acceptance-clock router

Causal signals:
**16 / 3 / 651 / 1 / 227 / 7**

Aggregate signal error: **530**.  
Latch trade error: **528**.

### 09S clock-topology router

Causal signals:
**16 / 3 / 651 / 6 / 227 / 7**

Aggregate signal error: **525**.  
Latch trade error: **523**.

The historical 09S fingerprint error of 61 therefore does **not** reconstruct under the current causal clean-room state machine.

## Secondary diagnostic

Universal current-clock + stage-normalized reversal generated:

**256 / 14 / 689 / 40 / 280 / 15**

Aggregate count error improves only slightly to **323**, versus control 338/336.

But S06 deteriorates:
- 689 signals vs 672 historical
- 689 trades vs 615
- 294 wins vs 307
- -$154.81 vs -$101.08

Therefore this is only a weak semantic clue and fails the carry-forward rule.

## Interpretation

09S exposed a real structural fingerprint, but not a reconstructible conditional failure-clock rule. Its low historical error was dependent on older preserved chronology that the clean-room causal generator does not reproduce.

The repeated 09M–09R execution-scheduler failures and this 09T clock-router failure jointly shift the remaining parity question upstream toward **generator ownership and episode release** rather than downstream execution persistence.

The next useful class is constrained between two already-rejected extremes:
- fully serial generator ownership under-produces sparse vectors;
- immediate fully decoupled failure episodes massively over-produce.

The next bounded test therefore targets **new-boundary-only generator release while a downstream failure episode remains alive**, avoiding immediate same-boundary full decoupling.

## Decision

**Checkpoint 09T = QA PASS / NEGATIVE CHALLENGER / NO SEMANTIC UNFREEZE.**

Reject:
- acceptance-timeframe conditional failure clock;
- acceptance/reversal-timeframe clock-topology router;
- universal wait-reentry clock;
- universal stage-normalized carry-forward.

Preserve only the weak observation that stage normalization slightly raises sparse-vector density; it is not frozen because S06 worsens materially.

## Next bounded unit

`R037_DH05_GENERATOR_OWNERSHIP_NEW_BOUNDARY_RELEASE_PARITY_RECONSTRUCTION`

Question: can the generator become eligible for a **new causally revealed M5 boundary identity** while the previous failed-break episode continues downstream, without permitting immediate repeated same-boundary full decoupling?

No numeric retuning, no August, no SORB, no MQL5.
