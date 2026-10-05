# DELTA-A R10I — Transparent 5-Second Micro Loss-Conversion Router

Status: **PROMISING JANUARY BREAKTHROUGH — EXACT CAPITAL REPLAY REQUIRED**  
August: **SEALED / NOT ACCESSED**  
Production MQL5: **NOT AUTHORIZED**

## Objective
Reduce the broad January primary gross-loss pool and convert selected losing trajectories into wins while preserving useful velocity and the frozen $100→$1,000 survivability architecture.

## Fixed causal router
Every decision occurs at +5 seconds after the existing primary entry. Only state visible by that time is used.

1. **Ignition harvest R1** — previous completed-30s range $2.50–<$4.00 and first-5s aligned displacement >+$1.00: close the primary at +5s.
2. **Evening failed-ignition R2** — UTC 18:00–21:59 and first-5s aligned displacement -$0.50–<$0: close primary at +5s and open equal 0.01 opposite for 120s.
3. **London ignition harvest R3** — LONDON_ONLY and first-5s aligned displacement +$0.50–+$1.00: close primary at +5s.
4. **Quiet-flow failed-ignition R4** — source gap <=$2.375, first-5s aligned displacement $0–<$0.50, first-5s path efficiency 0.30–<0.50: close primary at +5s and open equal 0.01 opposite for 90s.

No lot escalation. The four rules are mutually exclusive by first-5s displacement band.

## January screen
Control: 3,841 physical episodes, +$1,242.09 net, -$16,725.52 gross loss, PF 1.0743, 49.52% wins.

Router screen: 3,841 episodes, **+$1,822.70 net**, **-$15,486.45 gross loss**, PF **1.1177**, **52.67% wins**.

Delta: **+$580.61 net**, **$1,239.07 less gross loss**, 382 modified episodes, **79.32% modified-episode win rate**, 176 baseline losses converted to wins.

Late-January holdout is stronger than discovery: +$350.26 incremental net, $838.20 less gross loss, 52.68% overall wins, **84.96% modified-episode wins**.

## R9 SYNTH January distance
Teacher/reference: 27,980 trades, +$41,520.82 net, -$1,827.87 gross loss.

The current physical lane is only ~13.7% of SYNTH January trade count and ~4.4% of SYNTH January net, while its gross-loss magnitude is still ~8.47x SYNTH. Therefore R10I is a specialist seed, not parity.

## Promotion boundary
This is a counterfactual ledger screen using a fixed $0.225 round-trip 0.01-lot research cost for modified legs. Earlier exits alter slot availability; therefore exact chronological capital/tick replay is mandatory before promotion. Preserve the rules as fixed while performing that replay.
