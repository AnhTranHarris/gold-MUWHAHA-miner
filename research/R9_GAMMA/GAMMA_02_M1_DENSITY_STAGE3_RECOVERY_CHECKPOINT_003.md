# GAMMA-02 — January M1 Density Stage-3 Recovery Checkpoint 003

**Status:** RECOVERED / DURABLE / INTEGRATION SEMANTICS UNDER INVESTIGATION  
**Predecessor:** GAMMA_02_M1_DENSITY_RECOVERY_CHECKPOINT_002.md  
**Branch:** carson/r9-gamma-02-velocity-geometry-research  
**August:** SEALED

## Recovered Stage-3 standalone discoveries

All numbers below are January discovery on ordered Dukascopy Bid/Ask ticks and were produced by hour-sliced replay. They are NOT yet approved as composable portfolio economics.

### Activity-conditioned hour specialists

- London 11 UTC: ~+$1,551.85 / 1,261 trades / PF ~3.645 / +$1.231 expectancy.
- Overlap 13 UTC: ~+$3,848.47 / 1,475 trades / PF ~4.707 / +$2.609 expectancy.
- Overlap 14 UTC: ~+$5,667.10 / 6,058 trades / PF ~1.971 / +$0.935 expectancy.
- New York 17 UTC: activity filtering improves the Stage-2 frontier; an exact recovered configuration around 3-second activity >=12 produced about +$3.06K / 7.06K trades / PF ~1.50.
- New York 18 UTC: displacement-gated specialist around favorable M1 extension roughly $3.5-$5.2 produced ~+$2,159 / 1,081 trades / PF ~2.105 / +$1.997 expectancy.

## Critical integration finding

A continuous full-January integrated replay using the intended five specialists did NOT preserve those standalone economics.

Recovered integrated cap-16 result:
- net: +$507.41
- trades: 18,829
- PF: ~1.0319
- expectancy: +$0.02695/trade
- drawdown: ~ $4,166
- max open: 16

Attribution:
- London11: -$384.64 / 1,518
- Overlap13: -$212.57 / 2,039
- Overlap14: -$1,510.12 / 7,010
- NY17: +$369.73 / 6,999
- NY18: +$2,245.01 / 1,263

This is NOT an acceptable integrated candidate.

### Why this is scientifically important

The discrepancy persists even with a single specialist enabled. Example:
- London11 hour-sliced activity config: approximately +$1,478.55 / 1,550 / PF ~3.08.
- The nominally same London11 rule inside continuous full-January replay: -$384.64 / 1,518 / PF <1.

Therefore the problem is not merely portfolio overlap or global concurrency. There is a replay-state/feature-semantics difference between hour-sliced discovery and continuous chronology.

Potential causes to diagnose explicitly:
1. rolling tick-activity state at the hour boundary;
2. minute anchor/reset initialization;
3. favorable-extreme state initialization;
4. next-hour exit-only tick treatment;
5. event counters / one-shot state resetting;
6. any feature that is implicitly reset because non-hour ticks are absent from the sliced stream.

Until that discrepancy is resolved, the large Stage-2/3 standalone profits are retained as **hypothesis evidence only**, not as system performance.

## Exact durable artifacts

Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/`

Recovered files include:
- gamma02_hourly_refinements_stage3.json
- gamma02_tick_activity_stage3.json
- gamma02_ny_hour18_rank_stage3.json
- gamma02_ny_hour18_displacement_stage3.json
- gamma02_integrated_specialists.py

## Next atomic unit

`GAMMA_02_SLICE_CONTINUOUS_PARITY_001`

Required order:
1. reproduce one hour-sliced specialist exactly;
2. replay the same UTC-hour ticks while retaining full chronological preprocessing;
3. log the first event where eligibility, anchor, activity, direction, or exit differs;
4. repair the research harness if slice reset is introducing artificial information;
5. rerun only the affected Stage-2/3 variants under continuous chronology;
6. persist corrected positive and negative results before another density mutation.

No MQL5 build. No promotion. R9 SYNTH remains the hard target.
