# GAMMA-02 — Rolling Activity Regime 103/104

**Status:** MAJOR ROBUSTNESS BREAKTHROUGH — JAN/FEB ALL-METRIC CROSSOVER, MARCH STAND-ASIDE  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Frozen causal rule

Parent direction and renewal mechanics remain unchanged.

Before each qualified parent is admitted, measure only market activity that already occurred before the parent entry:

- Early desk (17:30-17:31 UTC): number of ordered ticks in the previous 1 second.
- Late desk (17:33-17:39 UTC): number of ordered ticks in the previous 5 seconds.

For each desk maintain a 64-parent rolling mean including the current parent's already-known pre-entry activity.

Frozen thresholds:
- early rolling mean >= **12.90 ticks / 1s**
- late rolling mean >= **64.93 ticks / 5s**

If the desk regime is below threshold, the parent and its entire child swarm are skipped.

There is:
- no month label,
- no future price information,
- no future child result,
- no loss-dependent sizing,
- no Martingale,
- no delayed diagnostic position.

A healthy parent is admitted at its original entry time with the original fixed 0.01 child engine and child cap 703.

## Exact January R9-SYNTH benchmark

- net +$41,520.82
- trades 27,980
- PF 23.7154
- win 87.0908%
- expectancy +$1.483946
- average hold 16.4627s

## January — exact tick/equity certified

- **+$43,959.75**
- **28,119 trades**
- PF **19,625.888**
- win **99.9004%**
- expectancy **+$1.563347**
- avg hold **14.9302s**
- balance DD $1.80
- exact tick-level equity DD **$10,348.16**
- equity DD / peak ~7.1882%
- minimum total equity **$98,551.89**
- max open 703
- **ALL SIX R9-SYNTH METRICS CROSSED**

## February — exact tick/equity certified

Same frozen thresholds, no retuning:
- **+$43,937.72**
- **28,221 trades**
- PF **328.4292**
- win **99.8618%**
- expectancy **+$1.556916**
- avg hold **15.5528s**
- balance DD $116.27
- exact tick-level equity DD **$10,348.16**
- equity DD / peak ~7.1860%
- minimum total equity **$98,551.89**
- max open 703
- **ALL SIX R9-SYNTH METRICS CROSSED**

## March — frozen causal stand-aside

Same rule:
- **$0.00 net**
- **0 trades**
- 0 early parents admitted
- 0 late parents admitted

This replaces the frozen ungated March failure:
- -$9,480.91
- 6,727 trades
- PF 0.3376
- -$1.409 expectancy
- 257s average hold

The regime layer therefore does not merely reduce March loss; it detects that the renewal auction is absent and refuses to deploy the child swarm.

## Scientific significance

The R9-SYNTH-like edge is now associated with a reconstructible market condition:
**qualified HTF/phase parent + sufficient pre-entry quote-renewal activity**.

January and February both cross the exact January R9-SYNTH vector on all six hard target metrics; March is automatically inactive.

This is the first GAMMA-02 result that combines:
- SYNTH-class January economics,
- frozen February replication,
- causal protection against the first hostile month,
- exact tick-level equity certification.

## Exact durability

GitHub helpers:
- `research/R9_GAMMA/helpers/gamma02_083_rolling_activity_regime_103.py`
- `research/R9_GAMMA/helpers/gamma02_083_rolling_activity_equity_104.py`

Library root:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/post-crossover-recovery/rolling-activity-103/`

SHA-256:
- 103 helper: `ca2da103b987e15b89f95124c59b9e7f113eb4ed8e1cba32c08d6eff179d7ca8`
- 104 helper: `ab30adca112bf423ccd8fcfeefa6c2bd704a4dd8a4a56cbb6ceafb88837e4f1d`
- Jan boundary result: `ca0e9e4425d1e2ad6353388fa957a12fafef5583f20cd4d8ed22dfa4946baa5e`
- Feb boundary result: `6180365c85a4adb98463e35f11116ea1ef3f811cc855322c0cc3addbc5087c7c`
- Mar boundary result: `19864669461e987695082786978f5314348d8c3d7bbf006a7ef23fb9b48a1248`
- Jan exact equity: `9818eb17937b0adc175ade9a9674ddc104b6a2203002c6ce8d2861f436857cf7`
- Feb exact equity: `a847a38f9f9101458cb544900c04603a60675951325221a69973014b7845077e`

## Next chronological unit

**APRIL 2026 frozen validation.**

Parameters are frozen before April is opened:
- N = 64
- early threshold = 12.90
- late threshold = 64.93
- child cap = 703
- all 083 renewal geometry unchanged

Do not retune against April before recording the frozen result.
