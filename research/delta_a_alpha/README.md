# Delta-A-alpha

Delta-A-alpha is an isolated side-research lineage forked from the live `delta` head at `ac91fc43389a34f8ba380b58143f8e185589b106`.

## Isolation contract

- Main `delta` is read-only from this branch.
- Existing `delta-A*` branches are historical evidence only; they are not ancestors or promotion authorities.
- Nothing discovered here changes main DELTA unless the owner explicitly authorizes a later handoff.
- August remains sealed.
- MQL5 remains unauthorized until explicit owner approval.

## Research purpose

The side lineage exists to explore higher-throughput specialist ideas without slowing or contaminating the main DELTA integration work. The first family is `GRID-001`, a clean-room reconstruction of the supplied grid-trading tutorial.

## Documentation architecture

GitHub is the machine-reproducibility layer. Store code, helper modules, exact configs, manifests, hashes, schemas, compact result JSON, recovery pointers, and immutable checkpoint reports here.

Google Drive is the human-readable layer. Store the research index, white papers, checkpoint narratives, decisions, and handoffs there.

Do not put huge raw ticks in GitHub. Do commit their hashes, partitions, schemas, producer versions, and regeneration rules.

## Vertical-build rule

A useful helper is promoted immediately, not left trapped in chat. If logic is reused, non-trivial, required to reproduce a result, expensive to reconstruct, or scientifically useful even when a test fails, it becomes a durable artifact before the next dependent experiment.

Start every new session from `CURRENT_STATE.json`; do not reconstruct the project from conversation memory.
