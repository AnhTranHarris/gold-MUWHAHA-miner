# GAMMA-02 — Hour-Slice Tail Entry Contamination Correction

**Status:** FORENSIC CORRECTION — Stage-2/Stage-3 hour attribution requires rerun  
**Detected after:** `0803edf6485c25eabe0af49d42de47477f98c22f`

## Defect

The January hour helper deliberately sliced:

- the target UTC hour, plus
- the first minute of the following hour,

so positions opened near xx:59:xx had enough future ticks to complete 30-second lifecycle exits.

The standalone stair simulator had only a session filter, not an explicit target-hour entry filter. It therefore also admitted **new trades in that following tail minute**.

The extra tail minute is valid for exits but invalid for attribution to the preceding hour.

## Exact reproduction

A corrected simulator with an explicit `hour == target_hour` admission check reproduces full-month chronological results exactly when run on the small hour+tail slice.

Examples using the same January configs, with activity filtering disabled to isolate the defect:

- London 11 slice contaminated: about +$1,438.65 / 1,693 trades.
- London 11 corrected: about **-$424.54 / 1,661**.
- Overlap 13:30-14 contaminated: about +$3,719.41 / 2,376.
- Corrected 13:30-14: about **-$233.92 / 2,261**.
- Overlap 14-15 contaminated: about +$5,959.67 / 7,732.
- Corrected 14-15: about **-$1,586.30 / 7,550**.
- NY 17-18 contaminated: about +$2,796.09 / 8,005.
- Corrected 17-18: about **+$163.99 / 7,887**.

Corrected slice outputs match the equivalent full-month hour-filtered simulator exactly in net, trades, and event count.

## Scientific consequence

Do NOT use Stage-2/3 hour-attribution profit numbers as evidence until rerun with explicit entry-window guards.

The discrepancy itself is informative: the first minute of several following phases may carry exceptional directional behavior. The next rerun will therefore test both:

1. clean full-hour windows;
2. explicit first-minute / opening-burst windows as their own separately labeled specialists.

This is a correction to attribution, not permission to hide or delete the prior artifacts. Prior Stage-2/3 files remain preserved as forensic evidence.

## Unaffected work

The frozen STMR parent, runner-shadow foundation, sleeve-specific root research, and earlier exact parent parity work are not based on these hour+tail attribution slices and remain intact.

## Rule added

Every future time-window helper must distinguish:

- **entry window**
- **exit-tail window**

Tail ticks may manage existing positions but may never create new entries unless that next window is explicitly being tested.

No integrated portfolio result is valid until each specialist passes one-specialist parity under this corrected rule.
