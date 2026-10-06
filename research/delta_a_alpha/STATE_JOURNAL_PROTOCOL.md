# Delta-A-alpha State Journal Protocol

## Purpose

Protect long research chains from UI delivery timeouts, retried tool calls, stale pointer writes, duplicate sequence allocation, and research-order contamination.

## Authority order

1. durable scientific artifacts / helpers / source hashes;
2. active-lineage state journal and explicit clean-reset entries;
3. `CURRENT_STATE.json` and `CURRENT_INFLIGHT.json`;
4. chat transcript.

A mutable pointer never invalidates a completed durable unit.

## Normal append-only rule

Every scientifically meaningful completed unit creates a new file under:

`research/delta_a_alpha/state_journal/`

Normal journal files are append-only and are not edited, renamed, or deleted.

Filename:

`NNNN_<UNIT_ID>.json`

Each entry records:
- sequence;
- unit;
- status;
- predecessor;
- completed outputs;
- scientific decision;
- next unit;
- immutable constraints.

## Owner-directed contamination reset exception

A cleanup may remove historical files from the **active research lineage** only when all conditions are met:

1. the owner explicitly directs deletion/quarantine because the prior research order is invalid or contaminating;
2. the complete pre-cleanup branch head is frozen to a named rollback branch before deletion;
3. the cleanup uses an expected-head/lease check so concurrent valid work cannot be overwritten;
4. a new clean-reset journal entry records what was deleted and where it remains recoverable;
5. active pointers and helper registries are repaired immediately;
6. removed work becomes forensic/rollback evidence only and cannot silently re-enter the active floor.

This exception was invoked for `DAA_GRID_SYSTEM_CLEAN_RESET_003`.
Recovery branches:
- `delta-A-alpha-pre-system-cleanup-20261006`
- `delta-A-alpha-pre-system-cleanup-20261006-v2`

The active journal may therefore contain sequence gaps after an owner-directed clean reset. Gaps are intentional; the reset entry is authoritative.

## Authoritative cursor

Under ordinary conditions, the highest valid active journal sequence is the restart cursor.

After a clean reset, the highest clean-reset-or-later sequence is authoritative even if earlier active files were purged.

## Duplicate-sequence collision

If retries create two entries with the same sequence:

1. do not rewrite either while they remain active evidence;
2. verify both units and Git ancestry;
3. create a later reconciliation entry;
4. record all colliding predecessors;
5. state one authoritative next unit.

## Timeout recovery

After any timeout:

1. inspect `CURRENT_STATE.json`;
2. inspect the journal path named there;
3. verify expected output paths;
4. if outputs already exist, do not rerun them;
5. rerun only the smallest incomplete unit;
6. persist results before dependent work.

## Stale replay defense

If convenience pointers disagree with the journal/reset chain, the journal/reset chain wins and pointers must be repaired.

## Sequence allocation discipline

Before creating a new journal entry:
- inspect the latest authoritative sequence;
- allocate the next integer;
- if a write conflicts, relist before retrying.

## Research constraints

- main `delta`: read-only;
- XAUUSD only;
- fixed 0.01 lot;
- Martingale prohibited;
- loss-dependent sizing prohibited;
- August 2026 sealed;
- MQL5 unauthorized unless explicitly approved.
