# Delta-A-alpha Bootstrap Handoff

## Authority order

1. Current owner instruction.
2. This branch's root `CURRENT_STATE.json`.
3. Delta-A-alpha governance/artifact policy and active experiment spec.
4. Frozen parent snapshot from main `delta`.
5. Historical Delta-A and older research only as evidence.

## Parent snapshot

Fork point: `ac91fc43389a34f8ba380b58143f8e185589b106` from branch `delta`.
Parent checkpoint: `R037_SPECIALIST_DOCUMENTATION_FINALIZATION_CHECKPOINT_18B`.

## Current side state

No active candidate.
GRID-001 is source-reconstructed but untested.
August is sealed.
MQL5 is not authorized.
Main delta is not writable from this lineage.

## Restart sequence

Read:
1. `CURRENT_STATE.json`
2. `research/delta_a_alpha/README.md`
3. `research/delta_a_alpha/ARTIFACT_LIFECYCLE.md`
4. `research/delta_a_alpha/HELPER_REGISTRY.json`
5. `research/delta_a_alpha/SOURCE_REGISTRY.md`
6. `research/delta_a_alpha/CURRENT_INFLIGHT.json`
7. active experiment spec and last checkpoint manifest

Then resume only `first_incomplete_unit`.
