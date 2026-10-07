# GAMMA-02 — Router 122 Warmup Leakage QA 001

**Status:** CRITICAL QA FINDING — 103/104 CROSS-MONTH AUTHORITY SUSPENDED  
**Date:** 2026-10-07  
**August:** SEALED

## Finding

During timeout recovery, router-122 specialist streams were converted from month-local tick indices to absolute UTC timestamps.

That exposed a defect in the frozen `gamma02_083_rolling_activity_regime_103.py` / `gamma02_083_rolling_activity_equity_104.py` helper family:

- `load_month(m,10)` prepends the prior 10 calendar days for EMA/state warmup;
- the 103/104 entry-selection code does not apply `start <= entry < end` before selecting parents;
- therefore selected warmup entries can be admitted and reported as if they belong to target month `m`.

## Direct evidence

Absolute-time router cache for nominal February 103:
- raw entries: 36,355
- entries whose absolute entry timestamp is actually in February: **102**
- target-February net of those 102 raw specialist events: approximately **-$22.03**
- the previously frozen 103/104 February report claimed about **+$43,937.72 / 28,221 trades**.

The discrepancy is explained by warmup-entry leakage, not a valid February edge.

Nominal July 103 similarly contains 28 raw entries but **zero July entries** after absolute-time filtering.

## Disposition

1. Suspend 103/104 as cross-month authority.
2. Preserve all historical 103/104 artifacts for forensic provenance; do not delete them.
3. Router 122 must not use 103/104 until the helper is rebuilt with explicit target-month entry gating and revalidated.
4. Recompute the non-deployable oracle without contaminated 103/104 before making further gap-to-R9-SYNTH claims.
5. Audit all specialist helpers for target-entry gating. Current router helper already has explicit target gating in:
   - 119;
   - 114/115 rule streams.
   109 must also be checked month-by-month because its helper does not explicitly gate target entries.
6. No month label may enter the deployable router; month boundaries are dataset partitions only.

## Continuity

All seven router-122 raw stream caches and all seven absolute-time caches are durable in Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/meta-router-122/`

The absolute-time caches make this QA reproducible without rebuilding the underlying specialists.

## Next

`GAMMA_02_ROUTER_122_SPECIALIST_GATE_AUDIT_AND_FEB_REPAIR`

Do not optimize router thresholds against contaminated 103/104 data.
