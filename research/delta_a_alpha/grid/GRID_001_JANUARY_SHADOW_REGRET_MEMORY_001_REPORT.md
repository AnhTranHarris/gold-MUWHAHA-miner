# GRID-001 January Shadow-Regret Memory 001

**Status:** COMPLETE / NEGATIVE

A05 events were grouped only by crossing direction and coarse adaptive-gap band. MR and continuation shadow outcomes were allowed to influence future events only after the full 5-minute shadow horizon had matured.

Three fixed memory horizons were tested: 30 minutes, 2 hours, and 8 hours.

All remained negative:
- M30: **-$7,008.60 / PF 0.824**, validation PF **0.939**
- M120: **-$7,430.68 / PF 0.822**, validation PF **0.926**
- M480: **-$7,497.64 / PF 0.824**, validation PF **0.935**

A05 always-continuation remained better at PF **0.845**, validation PF **0.977**.

## Interpretation

Recent realized directional winners are not sufficient state by themselves. The market does not appear to stay in one simple MR-vs-CONT mode long enough for this coarse family memory to become an edge.

The counterfactual shadow twin remains valuable as a diagnostic tool, but not yet as a direct selector.

## Decision

Do not tune more memory windows or deadbands.

The strongest surviving clue remains the adaptive A10/A15 geometry, where continuation is already near break-even and direction-oracle quality is very high.

Next attack the actual red flag directly: **gross loss**.

The next mutation will test an early thesis-failure state on A10/A15 continuation: a new continuation trade begins unconfirmed, must demonstrate favorable progress, and can be cut before consuming the full hard-stop budget if the adverse path proves the thesis wrong first.
