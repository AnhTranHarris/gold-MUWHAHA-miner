# Delta-A-alpha Append-Only State Journal Protocol

## Purpose

Protect long research chains from UI delivery timeouts, retried tool calls, out-of-order state-pointer writes, and duplicate sequence allocation.

## Authority order

1. **Immutable scientific artifacts/reports/helpers**
2. **Append-only state journal / reconciliation chain**
3. `CURRENT_STATE.json` and `CURRENT_INFLIGHT.json` convenience pointers
4. Chat transcript

A mutable pointer is never allowed to invalidate an immutable completed unit.

## Journal rule

Every scientifically meaningful completed unit creates a new file under:

`research/delta_a_alpha/state_journal/`

Journal files are never edited, renamed, or deleted.

Normal filename format:

`NNNN_<UNIT_ID>.json`

Each journal entry should contain:
- sequence;
- unit ID;
- status;
- predecessor path/unit;
- completed output paths;
- scientific decision;
- next unit;
- immutable constraints.

## Authoritative cursor

Under normal conditions, the highest unique valid sequence is the authoritative restart cursor.

### Duplicate-sequence collision

Retries or concurrent tool continuations can allocate the same sequence to two valid immutable entries.

If that happens:

1. **do not** rename, delete, or rewrite either historical entry;
2. verify both units and their Git commit ancestry;
3. create a new later `RECONCILIATION` journal entry;
4. list every colliding entry as a predecessor;
5. distinguish scientific frontier vs remediation/infrastructure roles;
6. state the single authoritative next unit.

After reconciliation, the reconciliation entry is authoritative over the colliding sequence.

Example implemented:
`0016_DAA_STATE_JOURNAL_COLLISION_RECONCILIATION_001.json`

## Timeout recovery

After any timeout or retry:

1. list `state_journal/`;
2. inspect the highest sequence;
3. if that sequence is duplicated, find the later reconciliation entry that resolves it;
4. verify completed output paths;
5. ignore mutable cursors pointing to older units;
6. resume only the authoritative journal entry's `next_unit`;
7. persist the next meaningful unit before dependent work begins.

## Stale replay defense

A delayed historical tool call can overwrite a mutable state file, but it cannot replace immutable scientific outputs.

If `CURRENT_STATE.json` or `CURRENT_INFLIGHT.json` disagrees with the journal/reconciliation chain, the journal wins and the pointer should be repaired.

## Sequence allocation discipline

Before creating a new journal entry:
- list the journal directory;
- identify the highest **resolved** sequence;
- allocate the next integer;
- if the create call reports a conflict, relist rather than guessing another state.

## Research constraints

- main `delta`: read-only;
- XAUUSD only;
- fixed 0.01 lot;
- Martingale prohibited;
- loss-dependent sizing prohibited;
- August 2026 sealed;
- MQL5 unauthorized unless explicitly approved.
