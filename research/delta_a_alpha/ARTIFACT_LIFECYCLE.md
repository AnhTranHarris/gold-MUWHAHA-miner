# Delta-A-alpha Artifact Lifecycle

## Goal

Prevent repeated byte-for-byte rebuilds while preserving research integrity and keeping disposable scratch from polluting the durable record.

## Levels

### L0 — Scratch
Ephemeral calculations or one-off inspection that no later unit depends on. It may disappear.

### L1 — Reusable helper
Promote immediately when any condition is true:
- used by a second experiment;
- contains non-trivial parsing, feature, execution, accounting, or state-machine logic;
- costs meaningful time to reconstruct;
- is required to reproduce a result;
- repairs a previously discovered failure mode.

L1 requires a stable path, short purpose note, input/output contract, and source commit.

### L2 — Candidate artifact
A config, event corpus definition, result JSON, or diagnostic used to evaluate a hypothesis. Requires parent checkpoint, dataset partition, execution surface, producer path/commit, config hash, and result hash where applicable.

### L3 — Scientific checkpoint
Any positive OR negative result that changes the next decision. Requires a compact report, manifest, exact durable cursor update, and Drive narrative/readback.

### L4 — Promoted specialist
Requires reconstructible logic, code/config, causal assumptions, test matrix, monthly/OOS evidence, failure modes, provenance, white paper, and an MT5 mapping note. Promotion does not authorize MQL5.

## Rebuild prohibition

If a required artifact exists with known committed bytes or a verified hash, load or reproduce from that source. Do not reconstruct it from chat prose. If the artifact is missing but only a hash/report survives, perform one clean-room reconstruction, prove parity, and persist it before continuing.

## Derived-data rule

Large derived tick/bar/event files may live in Drive/Library rather than GitHub. Their registry entry must record:
- canonical raw-data hash;
- partition/window;
- schema;
- producer commit/blob;
- parameters;
- output hash;
- regeneration command or function.

## Cleanup rule

Only L0 scratch may be deleted freely. L1+ artifacts are retained or explicitly superseded with a pointer to the replacement. Never silently overwrite a checkpoint.
