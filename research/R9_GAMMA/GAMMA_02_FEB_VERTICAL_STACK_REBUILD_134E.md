# GAMMA-02 — February Vertical Stack Rebuild 134E

**Status:** DURABLE MAJOR FEBRUARY REBUILD / CORRECTED ARCHITECTURE  
**January fallback:** `carson/r9-gamma-02-jan-grid-milestone` untouched  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Why this checkpoint exists

The earlier February adaptive work compressed the January architecture into component/expert streams and inverted the intended hierarchy. This unit restores the owner's required vertical design: tick/session/MTF grid is the spine; hourly/session volume mechanics, regime routing, Watchdog renewal, trend-within-trend state experts, recovery logic, and heat control sit above it.

## Restored vertical architecture

1. Ordered tick execution and session-local grid geometry.
2. Completed H4/H1/M15/M5 structural permission.
3. Session-specific geometry (Asia distinct from London/overlap/NY/late).
4. High-volume London/overlap/NY hourly harvesting under causal fast/slow governance.
5. Watchdog-119 renewal regime layer, refined for February to **max renewal layer 30 / cap 384**.
6. February-native PF10 completed-HTF + 10-minute-subphase + realized-displacement specialist as the trend-within-trend layer.
7. Earlier-session coverage + cold-start + Asia02 + late-session sleeves.
8. Supplemental one-ticket-per-market-tick de-duplication and one chronological global heat cap.
9. Wrong-direction recovery remains shadow-only pending 134F because the generic March 109 reversal geometry was negative in February.

No calendar month/date/week is used as an execution feature. February is the discovery/evaluation partition only.

## February benchmark

R9 SYNTH February: **+$66,213.65 / 33,523 trades / GL -$2,031.42 / PF 33.59 / 88.30% wins / +$1.975 expectancy**.

## Selected corrected February frontier — global cap 640

- net: **+$117,022.07**
- trades: **25,073**
- gross loss: **$-13,205.42**
- PF: **9.8617**
- win rate: **87.31%**
- expectancy: **+$4.6673/trade**
- balance DD: **~$2,173.33**
- full-tick equity DD: **~$0.00**
- max open: **640**
- positive days: **14/20**
- days beating same-date R9 SYNTH: **11/20**
- positive weeks: **4/4**
- weeks beating same-week R9 SYNTH: **4/4**

This is approximately **1.77x** February R9 SYNTH net.

Weekly net:

- W06: **$63,887.07** vs SYNTH $34,837.88
- W07: **$20,328.08** vs $13,876.89
- W08: **$11,486.00** vs $8,320.42
- W09: **$21,320.92** vs $9,178.46

All four weeks beat R9 SYNTH.

## Watchdog refinement inside the vertical stack

The aggressive February layer35/cap703 Watchdog produced about +$14.68K but GL about -$10.84K. Layer30/cap384 produces about **+$12.67K with GL only ~-$1.82K and PF ~7.96**. Most Watchdog profit is retained while the realized-loss pathology is sharply reduced.

## What still needs work

- Gross loss and DD remain much worse than R9 SYNTH despite much higher net.
- Feb 3, Feb 6, and Feb 18 receive no trades; Feb 12/16/24 are slightly negative. These are state-coverage diagnostics, never calendar rules.
- Existing Asia02 sleeve is only modestly positive and relatively loss-heavy; Asia needs a stronger distinct geometry.
- Generic failed-ignition reverse recovery is negative in February and must not be funded blindly. 134F must discover **state-conditioned wrong-direction recovery** using only evidence known at the recovery timestamp.

## Next atomic unit

`GAMMA_02_FEB_ASIA_AND_STATE_CONDITIONED_RECOVERY_134F`

Keep this exact vertical stack frozen as the fallback while testing: (1) stronger Asia geometry and (2) state-conditioned recovery from failed/wrong-direction entries.