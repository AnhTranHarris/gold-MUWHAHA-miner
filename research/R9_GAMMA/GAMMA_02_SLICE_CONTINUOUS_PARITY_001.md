# GAMMA-02 — Slice / Continuous Parity 001

**Status:** COMPLETE — HARNESS DEFECT IDENTIFIED AND CONTAINED  
**Predecessor checkpoint:** GAMMA_02_M1_DENSITY_STAGE3_RECOVERY_CHECKPOINT_003.md  
**August:** SEALED

## Root cause

The Stage-2/3 hour-sliced discovery harness retained the target UTC hour plus the first minute of the next hour so positions opened near the boundary could exit naturally.

That tail minute was intended to be **EXIT ONLY**.

However, the generic stair/activity/displacement simulator continued to allow new entries during that next-hour tail minute whenever the session code still matched.

Those tail-minute entries then encountered a discontinuous stream: after the one-minute tail, the sliced dataset jumped to the next day's target hour. Positions could therefore be marked/closed against a price roughly 23 hours later even though their configured lifecycle was only seconds.

This manufactured large hour-slice profits.

## Corrected parity evidence

Explicit target-hour gating was added while retaining the exit tail.

| Specialist | Original sliced result | Corrected continuous-equivalent result |
|---|---:|---:|
| London 11 | +$1,478.55 | **-$384.64 / 1,518 trades / PF ~0.458** |
| Overlap 13 | +$3,794.54 | **-$212.57 / 2,039 / PF ~0.839** |
| Overlap 14 | +$6,018.24 | **~-$1.50K / ~7.0K / PF ~0.76** |
| New York 17 | +$3,062.02 | **~+$370 to +$434 / ~7.0K / PF ~1.06-1.07** |

These large Stage-2/3 sliced profits are INVALIDATED as system evidence.

## Genuine survivor — New York 18 displacement specialist

The NY18 displacement-gated specialist survives exact explicit-hour / continuous chronology parity:

- UTC hour: 18
- session: New York
- permission: ALIGN4 (H4=H1=M15=M5 != 0)
- favorable-extreme step: $0.05
- permitted M1 favorable displacement band: $3.50 to $5.20
- TP: $12.00
- SL: $4.00
- max hold: 30 seconds
- max positions in standalone diagnostic: 16

Corrected January:
- **+$2,159.08 net**
- **1,081 trades**
- **PF 2.10457**
- **+$1.99730 expectancy/trade**
- 272 TP / 379 SL / 430 age exits
- max open 16
- balance DD ~$502.06

This result is byte/economically identical under the explicit-hour sliced replay and continuous full-January replay.

## Scientific disposition

1. Preserve the invalidated Stage-2/3 artifacts for forensic provenance; do not delete them.
2. Do not use their London/Overlap numbers in cumulative performance claims.
3. NY18 displacement specialist is retained as the first corrected high-density M1 specialist.
4. All future phase slices MUST:
   - precompute causal features from full chronology where needed;
   - permit entries only inside the target phase;
   - allow tail ticks for EXIT PROCESSING ONLY;
   - prove slice/continuous parity before parameter search results are promoted.
5. Re-scan London / overlap / NY hours with the corrected explicit-phase harness.
6. No MQL5 build yet.

Exact corrected parity artifact is durable in Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/gamma02_slice_continuous_parity_001.json`

SHA-256:
`1f75ab07b66bca586bdc96284ea12ae313e154bc41dd436b52faf2f6ac601d88`

## Next unit

`GAMMA_02_CORRECTED_PHASE_DENSITY_SCAN_001`

Hard north-star remains R9 SYNTH, not incremental optimization.
