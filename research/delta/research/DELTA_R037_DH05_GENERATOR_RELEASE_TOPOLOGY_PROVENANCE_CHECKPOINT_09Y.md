# DELTA R037 — Generator Release Topology Provenance Harvest — Checkpoint 09Y

**Status:** COMPLETE MATERIAL PROVENANCE CLUE / NON-PROMOTING  
**Unit:** R037_DH05_GENERATOR_RELEASE_TOPOLOGY_PROVENANCE_HARVEST  
**Parent:** R037_DH05_ACCEPTANCE_TF_METADATA_PROVENANCE_CHECKPOINT_09X  
**Raw ticks:** NOT ACCESSED  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose

The corrected 09X ledger invalidated the stale 09S claim that acceptance/reversal timeframe identity cleanly separates the six DH05 vectors. This unit harvested already-durable generator-release fingerprints from 09H, 09I and 09V to ask whether any **non-vector-specific, reconstructible structural relation** explains release behavior.

No new market replay and no numeric retuning occurred.

## Producer

`research/delta/experiments/delta_r037_dh05_generator_release_topology_provenance_harvest.py`

- commit: `60e57dd7327218541d14fb061caa1703db765bf3`
- blob: `c2f876270d2c2a27754412fdd4f38e856b3fc037`
- SHA-256: `1afaa788acbca5c69dc1cc4dbbae3c479f246400737c5d7bd8ea2f05f4de4fa1`
- runtime result SHA-256: `476b1f66c091b092a3372d068117b5ceb5b80f4cfb5c3a60aea59dd3892b72f5`
- runtime: **0.80 s**
- peak RSS: **134,572 KB**
- exit: **0**

## Timeframe topology fails

Per-vector best release profile among already-tested causal profiles:

- A03: NEXT_REVERSAL_BAR_RELEASE
- S05: FAILURE_CANDIDATE_RELEASE
- S06: SERIAL_POST_QUAL
- S09: RECLAIM/NEXT_REVERSAL tie
- S10: NEXT_REVERSAL_BAR_RELEASE
- S16: FAILURE_CANDIDATE_RELEASE

Two direct conflicts disprove timeframe identity as a sufficient router:

- A03 and S05 are both acceptance/reversal **15/5**, but prefer different profiles.
- S10 and S16 are both **5/5**, but prefer different profiles.

Therefore routing by vector identity or by simple acceptance/reversal timeframe category would be retrospective overfit.

## Material structural clue

A natural causal relation from already-frozen timing fields is:

`max_probe_age_s < acceptance_tf_seconds`

This selects:
- S05: 6.468982 < 15
- S09: 10.844137 < 15
- S16: 3.711492 < 5

It does **not** select:
- A03: 20 >= 15
- S06: 23.47226 >= 5
- S10: 19.210606 >= 5

This matters semantically: when a probe's allowed lifetime is shorter than one acceptance-bar duration, the attempt can reach FAILURE_CANDIDATE before a newly completed acceptance bar can exist. That creates a reconstructible reason why generator ownership may differ.

## Harvested challenger

Rule:

- if `max_probe_age_s < acceptance_tf_seconds`: release generator at FAILURE_CANDIDATE while downstream failure episode continues;
- otherwise: retain SERIAL_POST_QUAL ownership.

Using the durable per-vector fingerprints only, the blended prediction is:

- serial control total funnel error: **978**
- candidate blended funnel error: **782**
- predicted improvement: **196**, or about **20.0%**

Selected vectors: **S05 / S09 / S16**.

The rule leaves S06 and S10 on serial control and does not depend on a fitted numerical cutoff; it compares two pre-existing frozen durations.

## Decision

**Checkpoint 09Y = MATERIAL HARVEST / NON-PROMOTING.**

This is strong enough for one exact causal raw-tick challenger replay, but not for semantic promotion because the relationship was discovered from the same six-vector Stage-A evidence.

## Next bounded unit

`R037_DH05_SHORT_PROBE_RELATIVE_ACCEPTANCE_BAR_OWNERSHIP_CHALLENGER_REPLAY_NON_PROMOTING`

Requirements:
- committed producer before compute;
- canonical Stage-A only;
- exact serial POST_QUAL control;
- no numeric retuning;
- hard timeout + atomic output;
- all six funnel/trade counts + S06 economics;
- if material, retain only as challenger pending independent anti-overfit/provenance validation.

No August. No SORB. No MQL5.
