# Checkpoint 07 — Opposition Heat + State-Stability Priority

This cumulative checkpoint implements the two portfolio loss-control breakthroughs.

## Opposition heat
Entry permission now uses a signal-strength score and penalizes existing opposite-direction positions. Same-direction stacking is not penalized merely for existing.

## State stability
Every temporal scale has an explicit 0..1 stability weight that multiplies its entry score before opposition heat is applied.

The research found that ranking states by worst monthly PF could remove roughly 60% of forward gross loss while retaining most forward net. The exact original per-state rank table was not preserved in GitHub, so **the default stability weights are neutral 1.0 values**. This preserves the mechanism without inventing historical coefficients. Populate/freeze those weights only from the reconstructed Jan-Apr development ledger.

This branch is therefore code-complete for the mechanism, but its state-stability table remains pending ledger reconstruction.
