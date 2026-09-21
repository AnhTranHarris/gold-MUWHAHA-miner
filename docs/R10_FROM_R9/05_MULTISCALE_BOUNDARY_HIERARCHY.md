# Checkpoint 05 — P11/P12/P13 Multiscale Boundary Hierarchy

The P8/P9 auction mechanism is now executable at multiple causal scales.

- 1m uses the completed 60-second microstructure boundary.
- 3m uses the prior three completed M1 bars and labels acceptance P11 / sweep P12.
- 5m/10m/20m extend the same auction family as P13-scale states.
- A penetration is only an event. The existing causal action router still decides CONTINUE / FADE / ABSTAIN.

At this checkpoint the system remains one-position-at-a-time. The order in which simultaneous scale events are evaluated is deterministic and intentionally temporary; the later portfolio checkpoint allows independent scale sleeves to coexist.

The original Python scale-specific learned coefficients were not preserved in the repository. Shared penetration/reclaim/acceptance distances are therefore reconstructed tester parameters and must be re-certified.
