# DELTA R037 — DH05 Post-Signal Episode Persistence / Invalidation — Checkpoint 09K

**Status:** COMPLETE NEGATIVE QA / SIMPLE LIFETIME EXTENSION REJECTED  
**Unit:** R037_DH05_POST_SIGNAL_EPISODE_PERSISTENCE_AND_INVALIDATION_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_SIGNAL_MULTIPLICITY_ADMISSION_CHECKPOINT_09J  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Bounded question

Checkpoint 09J found only a weak boundary-recycle multiplicity clue. This unit tested whether the historical generator instead preserves the same failed-break thesis longer after the first signal.

Two post-signal lifetime families were tested without changing any frozen numeric threshold:
1. renew the existing `max_failure_age` whenever a new causal signal fires;
2. after the first signal, ignore failure-age expiry until price causally retakes the original breakout boundary.

Each was paired with either reversal false→true rearm or a new completed reversal-bar edge. The same one-position admission replay and exit-tick latch diagnostic were retained.

## Producer

Path:
`research/delta/experiments/delta_r037_dh05_post_signal_persistence_invalidation_parity.py`

Commit:
`4e16b70f28fcaa1e0389010b7d39c9a6d87f5b2e`

Blob:
`60debec9c4c4e8f468a8a768a5949514c802da30`

File SHA-256:
`6dd2ced331abf671fe688eb8aa847c4af350691b1ee3d17ca3be3169a21463d8`

Official output SHA-256:
`d41fbc1c6ba548017e7ef1a6f4b246350d6e0c9952e53fe36ad6544f870c2031`

Runtime: **26.13 s**; max RSS **700,332 KB**; hard external timeout **120 s**.

All 09J/09F control gates reproduced before result acceptance. No signal buffer overflow occurred.

## Result

The lifetime-extension hypotheses fail decisively.

| Profile | Aggregate trade-count abs error |
|---|---:|
| 09J boundary-recycle control | **324** |
| 09J one-shot control | 336 |
| Signal-refresh + reversal-toggle + latch | 7,107 |
| Signal-refresh + reversal-toggle | 7,279 |
| Signal-refresh + new-bar-edge + latch | 7,955 |
| Signal-refresh + new-bar-edge | 8,241 |
| Persist-to-original-rebreak + reversal-toggle + latch | 58,651 |
| Persist-to-original-rebreak + reversal-toggle | 59,831 |
| Persist-to-original-rebreak + new-bar-edge + latch | 64,963 |
| Persist-to-original-rebreak + new-bar-edge | 66,847 |

### S06 illustrates the failure

Historical S06:
- signals 672
- trades 615
- wins 307
- net -$101.08

Signal-refresh / reversal-toggle:
- signals **9,247**
- trades **7,632**
- wins **3,348**
- net **-$1,671.79**

Persist-until-original-rebreak / reversal-toggle:
- signals **56,538**
- trades **48,946**
- wins **22,077**
- net **-$10,446.85**

The observation latch suppresses some entries under these extreme populations, but never remotely restores parity.

## Interpretation

The historical DH05 episode does **not** simply stay alive after a signal by:
- refreshing its normal failure clock after each new signal; or
- suspending that clock until the original breakout boundary is retaken.

Therefore post-signal lifetime remains tightly constrained. The sparse-vector deficits from 09J cannot be repaired by a broad lifetime extension.

The best tested architecture remains the ordinary short-lived serial episode with the 09J boundary-recycle signal rule as a **weak diagnostic clue only**.

## Decision

**Checkpoint 09K = QA PASS / STRONG NEGATIVE RESULT.**

Reject:
- signal-refreshed failure clock;
- persist-until-original-rebreak lifetime;
- both completed-bar and reversal-toggle variants.

No new semantic is frozen.

## Next bounded unit

`R037_DH05_POST_SIGNAL_INTRABAR_REARM_EDGE_PARITY_RECONSTRUCTION`

Test short-lifetime, causal edge rearm only:
- retain the frozen failure-age clock from FAILURE_CANDIDATE;
- after a signal, rearm only after a tick-level excursion back inside an already-frozen state threshold and a subsequent outward recross;
- compare existing original-boundary recycle against reclaim-threshold recycle;
- keep generator and executable admission separate;
- no new numeric threshold, no hindsight, no signal-every-tick behavior.

No SORB. No August. No MQL5.
