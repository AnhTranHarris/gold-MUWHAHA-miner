# Delta-A-alpha Append-Only State Journal Protocol

## Purpose

Protect long research chains from UI delivery timeouts, retried tool calls, and out-of-order state-pointer writes.

## Authority order

1. **Immutable scientific artifacts/reports/helpers**
2. **Append-only state journal**
3. `CURRENT_STATE.json` and `CURRENT_INFLIGHT.json` convenience pointers
4. Chat transcript

A mutable pointer is never allowed to invalidate an immutable completed unit.

## Journal rule

Every scientifically meaningful completed unit must create a new file under:

`research/delta_a_alpha/state_journal/`

Journal files are never edited or deleted.

Filename format:

`NNNN_<UNIT_ID>.json`

The highest valid sequence number is the authoritative restart cursor.

Each journal entry must contain:
- sequence;
- unit ID;
- status;
- predecessor sequence/unit;
- branch head/commit when known;
- completed output paths;
- scientific decision;
- next unit;
- immutable constraints.

## Timeout recovery

After any timeout or retry:

1. list `state_journal/`;
2. read the highest sequence entry;
3. verify its completed output paths;
4. ignore any mutable cursor that points to an older unit;
5. resume only the journal entry's `next_unit`;
6. create a new journal file when that unit completes.

## Stale replay defense

A delayed/replayed historical tool call may overwrite a mutable state file, but it cannot replace a journal entry because journal files are create-once.

If a mutable cursor disagrees with the highest journal entry, the journal wins and the pointer should be repaired.

## Research constraints

- main `delta`: read-only;
- XAUUSD only;
- fixed 0.01 lot;
- Martingale prohibited;
- loss-dependent sizing prohibited;
- August 2026 sealed;
- MQL5 unauthorized unless explicitly approved.
