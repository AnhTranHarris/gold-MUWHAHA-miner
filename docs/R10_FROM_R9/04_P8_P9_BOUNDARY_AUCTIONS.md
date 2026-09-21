# Checkpoint 04 — P8 Sweep/Reclaim + P9 Acceptance

This checkpoint adds executable non-R9 boundary events while retaining R9 as the original activity chassis.

A boundary is calculated from completed one-second data before penetration.

- P8: price penetrates a known boundary and reclaims back through it.
- P9: price penetrates and establishes acceptance outside it.
- Neither event forces a direction. The existing causal CONTINUE/FADE/ABSTAIN layer still decides the trade action.

The exact original learned Python event coefficients were not preserved in GitHub. Penetration/reclaim/acceptance distances are therefore explicit tester inputs with conservative reconstructed defaults.

The one-position account model remains in force at this checkpoint. Multiscale propagation and portfolio concurrency are later checkpoints.
