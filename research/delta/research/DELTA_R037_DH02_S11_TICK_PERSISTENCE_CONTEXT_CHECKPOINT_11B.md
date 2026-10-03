# DELTA R037 — DH02-S11 Tick Persistence / Context Semantics Fingerprint — Checkpoint 11B

**Status:** COMPLETE STRONG NEGATIVE LOCALIZATION / EXACT HISTORICAL PARITY NOT ACHIEVED  
**Unit:** R037_DH02_S11_TICK_PERSISTENCE_AND_CONTEXT_SEMANTICS_PARITY_FINGERPRINT  
**Parent:** R037_DH02_S11_CLEANROOM_PARITY_CHECKPOINT_11A  
**Vector:** DH02-S11 / fingerprint `50d1bb2e656e`  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Source-grounded question

Checkpoint 11A localized the residual to the categorical meaning of `tick persistence` and/or the exact scope of the DH01 `conflict-only veto`.

The surviving DH-02 white paper says:
- after BROKEN, price must remain on the breakout side for the required causal observation condition;
- failure is causal acceptance of the pre-break side;
- one boundary plus one original break direction is one event.

The historical parameter ledger names `tick persistence`, but the exact confirming-tick count is not preserved. The DH01 source defines CONFLICT_CHOP but does not preserve whether the veto is checked only at decisions or continuously during the pre-entry lifecycle.

Therefore this checkpoint tested only categorical, reconstructible interpretations. No numeric S11 threshold was changed.

## Preregistered matrix

Committed evidence:
`research/delta/reference/DELTA_R037_DH02_S11_TICK_PERSISTENCE_CONTEXT_EVIDENCE_11B.json`

Evidence commit:
`21acf1cee5eae10e329c0118a878dc1c8ddfe322`

Producer:
`research/delta/experiments/delta_r037_dh02_s11_tick_persistence_context_fingerprint.py`

Producer commit:
`2823c95c012b1236fe6ad87c2d4526cf55aefbc2`

Producer blob:
`788959802b8ec98ac5629462fddda4a0082384cf`

Six profiles:
1. next-tick persistence + decision-time conflict context (11A control)
2. two-tick persistence + decision-time context
3. three-tick persistence + decision-time context
4. next-tick persistence + continuous lifecycle conflict veto
5. two-tick persistence + continuous lifecycle conflict veto
6. three-tick persistence + continuous lifecycle conflict veto

The producer contains a fail-closed control gate requiring the 11A counters and signal SHA to reproduce exactly before the result is accepted.

## Crash / timeout containment

The official replay used the committed GitHub Actions recovery snapshot rather than an uncommitted scratch copy. The local producer and evidence Git blobs were verified against their GitHub blobs before execution.

The replay ran through:
`research/delta/qa/delta_bounded_python_runner.py`

with:
- hard 120-second subprocess timeout;
- Python faulthandler;
- unbuffered child output;
- isolated Numba cache;
- producer-owned atomic result write.

Official execution completed in approximately **9.42 seconds**.

## Result

Historical target:
- **75 trades**
- **41 raw-positive wins**
- GP **+$9.39**
- GL **-$17.60**
- net **-$8.21**

| Profile | Trades | Raw+ wins | GP | GL | Net |
|---|---:|---:|---:|---:|---:|
| **Next-tick / decision context (control)** | **106** | **42** | +7.80 | -35.10 | -27.30 |
| Two-tick / decision context | 108 | 43 | +8.02 | -35.63 | -27.61 |
| Three-tick / decision context | 106 | 42 | +7.67 | -35.06 | -27.39 |
| Next-tick / lifecycle context | 106 | 42 | +7.80 | -35.10 | -27.30 |
| Two-tick / lifecycle context | 108 | 43 | +8.02 | -35.63 | -27.61 |
| Three-tick / lifecycle context | 106 | 42 | +7.67 | -35.06 | -27.39 |

The 11A control reproduced exactly:
- 106 signals/trades
- 42 raw-positive wins
- 278 breaks
- 276 accepted
- 236 retests
- 130 failed
- 42 expired
- 86,547 context veto observations
- signal SHA `803fc20c55ed1d7f30356f2610392c12e6b43544f7f512bdd347cead69901dab`

## Strong negative localization

### Tick persistence count is not the missing population filter

Increasing persistence from one to two or three causal confirming ticks did not move the reconstruction toward 75 trades:
- one tick: 106
- two ticks: 108
- three ticks: 106

The accepted/retest counts changed, proving the semantic variants were active, but the executable population did not contract toward the historical fixture.

### Simple continuous CONFLICT_CHOP invalidation is not the missing filter

For every persistence count, the continuous-lifecycle context profile produced the **same signal fingerprint and economics** as the corresponding decision-only profile.

The continuous interpretation changed only two expired events into two context-vetoed events; it did not change executable signals.

Therefore a simple “keep checking the same conflict predicate continuously” interpretation cannot explain the missing 31 trades.

## Interpretation

Checkpoint 11B closes two attractive but unsupported repair branches:
1. hidden 2/3-tick persistence count;
2. simple continuous application of the reconstructed conflict predicate.

The residual is still strongly asymmetric:
- reconstructed wins: 42 versus historical 41;
- reconstructed trades: 106 versus historical 75;
- reconstructed gross loss: -35.10 versus historical -17.60.

That pattern still implies a missing **event-admission / ownership / context-state** semantic that suppresses a predominantly losing subset without materially reducing winners.

The next source-grounded clue is the DH-02 state grammar itself: **ARMED requires a causally known boundary and parent context that permits breakout research**. The current clean-room implementation largely evaluates conflict at break/rebreak decisions; it has not yet reconstructed context-conditioned boundary eligibility / arming identity.

## Decision

**Checkpoint 11B = QA PASS / STRONG NEGATIVE LOCALIZATION / HISTORICAL PARITY FAIL.**

Carry forward:
- next-tick persistence remains the leading source-faithful reconstruction;
- simple continuous conflict invalidation is rejected as the missing filter;
- all frozen numeric S11 thresholds remain unchanged.

Do not:
- retune S11 thresholds;
- select two/three ticks from fit;
- start S08;
- integrate SORB;
- access August;
- begin MQL5.

Compact result:
`research/delta/reference/DELTA_R037_DH02_S11_TICK_PERSISTENCE_CONTEXT_CHECKPOINT_11B.json`

Committed result blob:
`801bf4ee7a561f47dcfe41d0e56a155ed65e792d`

Committed result SHA-256:
`24f09be8822a3830c764bd76ba1017071c91b6be5209a006ef74bb238a465b2b`

## Next bounded unit

`R037_DH02_S11_EVENT_OWNERSHIP_AND_CONTEXT_STATE_PARITY_RECONSTRUCTION`

Primary question: does historical `parent_context = conflict-only veto` govern **boundary arming/eligibility and event identity**, rather than merely filtering break/rebreak decisions?

Test only source-grounded categorical state placements. No threshold search.
