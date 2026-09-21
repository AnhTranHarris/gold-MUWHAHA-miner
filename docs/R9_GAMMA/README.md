# R9 GAMMA Codeline

## Purpose

R9 GAMMA is the new cumulative post-R9 research line.

It is intentionally separate from the historical R10 branches. The immutable parent is:

- Branch: `carson/mt5-r9-hybrid-gate-certification`
- EA: `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`

R9 GAMMA follows the same promotion discipline as the original R-series:

1. Start from the last validated GAMMA checkpoint.
2. Add exactly one validated breakthrough or tightly related breakthrough family.
3. Document the breakthrough in a dedicated Markdown file.
4. Preserve the prior successful GAMMA branch unchanged.
5. Reject or roll back any change that fails compile, causal backtest, real-tick, survivability, or regression criteria.
6. Never fold an unverified reconstruction into the next checkpoint as if it were proven.

## Naming

- `carson/r9-gamma-00-baseline` — exact R9 baseline, no intended strategy change.
- `carson/r9-gamma-01-<breakthrough>`
- `carson/r9-gamma-02-<breakthrough>`
- etc.

Each numbered branch must be created from the immediately preceding successful GAMMA checkpoint.

## Documentation

Every promoted GAMMA breakthrough gets a file under:

`docs/R9_GAMMA/`

Each breakthrough note must contain:

- hypothesis
- source/provenance
- causal implementation
- equations or thresholds
- data window
- test methodology
- monthly results
- gross profit / gross loss
- profit factor
- trade count
- drawdown
- small-account survivability
- known failure modes
- rejected alternatives
- exact code changes
- promotion decision
- parent and child branch names

## Scientific controls

Historical R9 SYNTH is a teacher/reference ceiling, not execution truth.

REAL-tick and broker-native evidence take precedence over generated-tick performance.

Any result contaminated by look-ahead, retrospective order scheduling, optimistic intrabar ordering, hidden overlap, or double-counted exposure is rejected.

August 2026 remains sealed until the designated final holdout gate.

## Baseline checkpoint

Checkpoint 00 intentionally changes no trading logic. It exists solely to establish a clean parent for the cumulative GAMMA series.
