# GRID-001 January Path-Shape Discovery 001

**Status:** COMPLETE / NEGATIVE

A bounded ExtraTrees-style ensemble was used only as a discovery microscope on the retained elastic alpha-0.50 event clock.

Causal features included post-crossing path shape over 3s and 10s, virtual lattice depth, elastic-gap state, and completed-M1 parent context. The model trained only on the first two-thirds of January ticks and was evaluated on the final third.

## Result

3-second probe:
- validation balanced accuracy: **0.338**
- predicted-policy PF: **0.724**
- expected payoff: **-$0.204/accepted event**
- always-continuation PF at the same delayed entry: **0.711**

10-second probe:
- validation balanced accuracy: **0.336**
- predicted-policy PF: **0.715**
- expected payoff: **-$0.212/accepted event**
- always-continuation PF: **0.722**

The feature importance was diffuse; no small feature group dominated.

## Decision

REJECT this nonlinear path-shape family as a direction solution.

Do not tune the ensemble, add model depth, or promote ML. The result is useful because it shows that merely adding complexity to the same price-path information does not manufacture the missing edge.

The retained alpha-0.50 elastic event clock remains valid infrastructure. Directional research must change the **trade contract/regime semantics**, not hide the problem in a larger classifier.
