# DELTA R037 — Source-Default Breaker-Block Retest Stage-A Screen — Checkpoint 17CC-17CD

**Status:** COMPLETE / NO STAGE-A SURVIVOR / FAMILY RETIRED  
**Unit:** R037_BREAKER_BLOCK_RETEST_STAGE_A_SCREEN_CHECKPOINT_17CC_17CD  
**Parent:** R037_QUASIMODO_SOURCE_DEFAULT_STAGE_A_SCREEN_CHECKPOINT_17CA_17CB  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Bounded question

Does the preregistered source-default MetaQuotes breaker-block grammar provide enough causal XAUUSD supply and positive frozen 30-second persistence on fixed M5 or M15 lanes?

The preregistration froze:
- 7-bar consolidation;
- 50-point adjacent high/low tolerance;
- 3 bars after breakout;
- 1.0x consolidation-range impulse;
- swing validation enabled;
- 50-point move-away;
- invalidated order block flips breaker direction;
- retest zone touch plus close back beyond the near boundary;
- post-invalidation HH/LL swing validation;
- deterministic 300-bar block lifetime as the preregistered bridge for the source article's GUI-dependent visible-bar lifetime.

No timeframe, consolidation, impulse, move-away, lifetime, swing, session, side, or exit rescue tuning was permitted after result visibility.

## Producer / crash containment

Preregistration commit:
`cfcb44d1065a30f23aebee1b8193d749346a99d4`

Producer:
`research/delta/experiments/delta_r037_breaker_block_retest_17cc_17cd.py`

Producer commit:
`38f6d90538f24d6fc728e5ce7f9e9ef00b3b7002`

Producer blob:
`6f0c706b9921df0cd0624cc327ee150d59b3f16d`

Producer SHA-256:
`b6e29e1a7d2bbd542e74d5dbe1834c88ffc9ca030dac35e01652fc33c6d648d8`

The local producer was verified against the committed Git blob before official compute. An earlier uncommitted local draft differed byte-for-byte and was therefore not executed.

Official compute used the DELTA bounded process runner with a 120-second wall-clock guard and atomic result replacement. Runtime was approximately **5.64 seconds**.

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks:
**4,205,709**

## Official Stage-A result

| Lane | Signals | Trades | Days | Wins | Direct net | Gate |
|---|---:|---:|---:|---:|---:|---|
| 17CC M5 | 0 | 0 | 0 | 0 | $0.00 | FAIL SUPPLY |
| 17CD M15 | 0 | 0 | 0 | 0 | $0.00 | FAIL SUPPLY |

Result SHA-256:
`e7afd6b6210a02f87a6b52587d70ada3b6ab808dbc962665512d02cf8941a4bc`

Both lanes fail before economics become meaningful.

## Zero-signal QA

The zero result was investigated specifically to rule out a silent reconstruction defect.

For the source-default 7-bar consolidation to exist, six consecutive adjacent bar pairs must satisfy both:
`abs(high[i]-high[i+1]) <= 50 points` and
`abs(low[i]-low[i+1]) <= 50 points`.

On Stage-A:

- **M5:** 188 of 3,035 adjacent pairs satisfy the source-default tolerance (**6.19%**); longest consecutive qualifying run = **3**, versus **6 required**.
- **M15:** 20 of 1,011 adjacent pairs satisfy it (**1.98%**); longest consecutive qualifying run = **1**, versus **6 required**.
- M5 median adjacent high/low movement is approximately **$1.34 / $1.44**; 25th percentile approximately **$0.60 / $0.64**.
- M15 median adjacent high/low movement is approximately **$2.29 / $2.55**; 25th percentile approximately **$1.01 / $1.11**.

Therefore the source-default 50-point consolidation tolerance is structurally too tight for this XAUUSD Stage-A surface. The producer correctly records zero consolidations, so no breakout, impulse, invalidation, retest, or signal can exist downstream.

This is a **source-default supply incompatibility**, not a Python timeout or downstream trade-logic failure.

## Decision

**RETIRE R037-BBR-v1 source-default breaker-block family.**

Do not rescue by:
- widening the 50-point source-default consolidation threshold;
- reducing the 7-bar requirement;
- changing M5/M15 after seeing the result;
- weakening swing validation;
- tuning lifetime, move-away, session, side, stop, trail, or hold;
- accessing August;
- beginning MQL5.

The higher-level invalidated-zone/retest concept remains a qualitative research clue only. The exact source-default family is not a Miner candidate.

## Next unit

`R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST`

Selection bias for the next family:
1. adequate native event supply on XAUUSD;
2. causal reconstructibility;
3. near-neutral or positive evidence before refinement;
4. independent/holdout evidence whenever already available;
5. prefer high-information structures over rare multi-leg patterns.
