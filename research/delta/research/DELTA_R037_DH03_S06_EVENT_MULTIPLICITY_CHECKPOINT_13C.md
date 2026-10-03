# DELTA R037 — DH03-S06 Pullback Event Multiplicity / Reset — Checkpoint 13C

**Status:** COMPLETE MAJOR PARITY BREAKTHROUGH / FULL HISTORICAL PARITY NOT YET ACHIEVED  
**Unit:** R037_DH03_S06_PULLBACK_EVENT_MULTIPLICITY_AND_RESET_PARITY_RECONSTRUCTION  
**Parent:** R037_DH03_S06_STATE_FUNNEL_CHECKPOINT_13B  
**Vector:** DH03-S06 / `a3a086b7344c`  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Bounded question

Does an ENTRY_ELIGIBLE signal consume the entire DH03 pullback episode, or can a still-valid original pullback causally rearm for another exhaustion → S5 reclaim → later S5 reacceleration sequence?

All S06 numeric thresholds remained frozen. 13B S5 reclaim timing remained frozen.

## Crash-safe execution

Evidence, engine, and producer were committed before the replay. Local producer, engine and evidence Git blobs matched GitHub before execution. The canonical January source SHA was verified. The job ran under the 120-second bounded subprocess wrapper with isolated Numba cache, faulthandler, unbuffered output, and atomic producer output.

Official replay: **12.42 seconds**, peak RSS **698,016 KB**.  
Official raw-result SHA-256: `145692aef5f9b8991a7435da6e5338f46223bc5fa05ffe5dcabf3674f131345c`.

The 13B source-grounded control reproduced exactly at **783 trades / 363 raw-positive wins**, including the exact signal fingerprint.

## Major breakthrough

The leading source-compatible lifecycle is:

> After ENTRY_ELIGIBLE, do **not** consume the original pullback episode if parent structure, specialist invalidation, and original max-pullback age remain valid. Rearm the same episode to PULLBACK_ACTIVE and require a **fresh exhaustion** before a new S5 reclaim and later S5 reacceleration.

That single state-machine change, with **zero threshold retuning**, produces:

- **1,586 signals**
- **1,513 executed trades**
- **674 raw-positive wins**
- **661 official wins**
- gross profit **+$137.12**
- gross loss **-$476.26**
- net **-$339.14**
- max balance drawdown **$339.14**

Historical target:

- **1,563 trades**
- **690 raw-positive wins**
- gross profit **+$151.82**
- gross loss **-$490.75**
- net **-$338.93**
- max balance drawdown **$339.25**

The lifecycle repair closes **93.59% of the remaining 13B trade-count deficit**.

Most strikingly, the resulting **net differs from the historical fixture by only $0.21**, and max balance drawdown differs by only **$0.11**, despite still being 50 trades short.

## Episode evidence

The leading profile emitted 1,586 signals from **563 signal-producing pullback episodes**.  
**453 episodes** produced multiple signals.  
Maximum signals in one episode: **8**.  
Mean signals per signal-producing episode: **2.817**.

This is direct evidence that a repeated-attempt ledger inside one still-valid pullback is the missing population mechanism.

The one-position execution ledger suppresses **73 of the 1,586 signals**, leaving 1,513 executed trades. The historical target is 1,563 trades—only **50** higher.

## Rejected alternatives

A stricter rule requiring a new adverse S15 extreme before another exhaustion collapses back to 762 trades and therefore does not explain the historical population.

Keeping exhaustion permanently valid after the first signal is far too permissive: 3,267 executed trades on post-pullback pivots and 3,628 with any-causal pivots.

The any-causal-pivot + fresh-exhaustion interaction gives 1,672 trades, above target. It remains a pivot-age diagnostic only and is not promoted by fit.

## Decision

**Checkpoint 13C = MAJOR PARITY BREAKTHROUGH / FULL PARITY FAIL.**

Carry forward as a parity hypothesis:

- structural-priority M15/M30 parent;
- either S15 or S30 exhaustion weakening;
- S15 pivot reclaim level;
- LOCAL_RECLAIM observed on completed S5;
- later completed-S5 reacceleration;
- **same pullback episode survives an entry and rearms to PULLBACK_ACTIVE, requiring fresh exhaustion before another attempt**;
- original pullback-age clock remains attached to the episode;
- all numeric S06 thresholds remain frozen.

Do not retune thresholds, alter exits, integrate SORB, access August, or begin MQL5.

## Residual and next bounded unit

The leading profile has 1,586 signals but only 1,513 executed trades because the existing one-position admission ledger discards 73 signals arriving while a trade is active. Historical trade count is 1,563.

The next bounded question is therefore:

`R037_DH03_S06_EVENT_ATTEMPT_ADMISSION_AND_EXECUTION_PARITY_RECONSTRUCTION`

Goal: reconstruct the causal specialist signal-admission / position-observation semantics that determine which repeated episode attempts survive into executed trades. No signal thresholds or event thresholds may change.
