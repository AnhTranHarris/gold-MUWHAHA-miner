# Delta-A-alpha Timeout-Safe Continuity Protocol

## Purpose

Prevent a ChatGPT message-delivery timeout, tool timeout, browser refresh, or new-chat rollover from destroying or forcing reconstruction of valid research.

## Atomic research rule

Work is divided into small durable units. A unit is not allowed to depend on another new unit until its reusable helpers, config, result summary, and cursor are persisted.

For every meaningful unit:

1. mark the intended unit in `CURRENT_INFLIGHT.json`;
2. run only that bounded unit;
3. persist any reusable helper immediately;
4. persist the compact result/manifest immediately;
5. update `HELPER_REGISTRY.json` if a new reusable artifact exists;
6. update `CURRENT_STATE.json` / `CURRENT_INFLIGHT.json`;
7. only then start the next unit.

Do not defer persistence until the end of a long chat response.

## Recovery order after any timeout

1. Read branch head for `delta-A-alpha`.
2. Read root `CURRENT_STATE.json`.
3. Read `research/delta_a_alpha/CURRENT_INFLIGHT.json`.
4. Inspect the expected result/helper path before rerunning anything.
5. If the artifact exists, verify it and continue.
6. If only part of the unit is missing, rerun only the smallest missing part.
7. Never reconstruct a durable helper from chat prose when committed bytes exist.

## Chat is not storage

Conversation text may explain decisions, but it is not the authoritative location for:
- executable helpers;
- source hashes;
- configs;
- benchmark ledgers;
- result manifests;
- checkpoint state;
- recovery cursors.

GitHub is the machine truth. Google Drive is the human-readable mirror.

## Long-output avoidance

To reduce message-delivery timeouts:
- do not dump raw tick tables, giant JSON, or large source files into chat;
- write them to durable storage and summarize them in chat;
- keep tool batches small;
- prefer one verified write, then the next;
- checkpoint before expensive scans or multi-month jobs;
- use per-month/per-stage outputs so a failure never requires restarting Jan-Jul from zero.

## Current recovered boundary

The October 6, 2026 timeout occurred after the GRID-001 source reconstruction and after the R9 report extractor/benchmark were persisted. Those artifacts must be verified, not rebuilt.

Current scientific next unit remains:
`DAA_GRID_001_CAUSAL_FORENSIC_BASELINE`.

Main `delta` remains read-only. August remains sealed. MQL5 remains unauthorized.
