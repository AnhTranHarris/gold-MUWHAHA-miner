# DELTA R037 — VCE + Queue-Imbalance Confirmation Stage-A Screen — Checkpoint 17CE–17CH

**Status:** COMPLETE / NO PREREGISTERED SURVIVOR  
**Family:** R037-VQCF-v1  
**Parent:** R037_BREAKER_BLOCK_RETEST_STAGE_A_SCREEN_CHECKPOINT_17CC_17CD  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Research question

Can causal top-of-book quoted-volume imbalance confirm the direction of the previously near-neutral M5 BB/KC volatility-release source strongly enough to improve frozen 30-second executable persistence while retaining usable supply?

The test was already preregistered and producer-committed before the chat-delivery timeout. Recovery resumed at the first missing phase: official compute.

## Crash/timeout recovery

Preregistration commit:
`26d6e97a7ea5c2a6fadc7b903a6dde193b85cf9d`

Producer:
`research/delta/experiments/delta_r037_vce_qim_confirmation_17ce_17ch.py`

Producer commit:
`97d0aa6b6784e5ddc1464ba6f2d1dddaed8d9fea`

Producer blob:
`204a6587d0c941d18db098f8dab011b845bb5258`

Producer SHA-256:
`844dc08593e641294ac46d7d0839ad99b123488a90574409add867926c47d453`

The local producer and bounded-runner bytes were verified against their committed SHA-256 fingerprints before official compute. The official bounded replay completed in **7.241 seconds**.

## Control verification

The run was required to reproduce the frozen VCE-C04 control before any candidate result could be trusted.

Control reproduced exactly:

- **27 trades**
- **20 official wins**
- **11 distinct days**
- **+$0.71 direct net**

Therefore the reconstruction/control gate passed.

## Candidate results

| Profile | Trades | Days | Wins | Retention | Direct net | Gate |
|---|---:|---:|---:|---:|---:|---|
| 17CF QI ≥ 0.25 aligned | 8 | 6 | 7 | 29.63% | **+$1.19** | FAIL sample + retention |
| 17CG QI ≥ 0.50 aligned | 2 | 2 | 2 | 7.41% | **+$0.30** | FAIL |
| 17CH QI ≥ 0.75 aligned | 1 | 1 | 1 | 3.70% | **+$0.16** | FAIL |

The preregistered advancement gate required:
- at least 10 trades;
- at least 5 distinct days;
- at least 35% retention versus the 27-trade control;
- direct net strictly above +$0.71.

No profile satisfied all gates.

## Interpretation

The **QI ≥ 0.25** lane is a useful synthesis clue: it concentrated the control from 20/27 wins to **7/8 wins** and raised direct net from **+$0.71 to +$1.19**. However, it retained only **29.63%** of source events and only eight trades.

That is not enough evidence to promote a DELTA candidate and is explicitly protected by the preregistered no-micro-sample rule. The threshold must not be weakened or interpolated after result visibility.

## Decision

**RETIRE R037-VQCF-v1 AS A PROMOTABLE PATH.**

Preserve only the qualitative clue:
> causal queue imbalance may contain useful confirmation information when attached to a larger event, but the frozen thresholds are too selective to satisfy Miner supply requirements.

Do not:
- add a sign-only or smaller QI threshold after seeing this result;
- tune VCE parameters;
- rescue by session/side/weekday;
- change timeframe;
- tune exits;
- access August;
- begin MQL5.

Result SHA-256:
`1775b2c2787563311f2d8c050e0ea1615f698f05f09b09e5d62ac8160e335855`

## Next

`R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST`

Research bias: seek a higher-supply event-defined continuation source, while preserving the general lesson that microstructure confirmation is more useful as a filter than as a standalone entry source.
