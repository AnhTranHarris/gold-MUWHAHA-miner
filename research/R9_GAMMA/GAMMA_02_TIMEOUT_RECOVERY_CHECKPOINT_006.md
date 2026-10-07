# GAMMA-02 — Timeout Recovery Checkpoint 006

**Status:** DURABLE / RESUMED AFTER UI DELIVERY TIMEOUT  
**Date:** 2026-10-07  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Exact January R9 SYNTH benchmark recovered

Source: `ReportTester-871471_jan2026_jul2026_R9_ticklog_synth(4).xlsx`

January 2026:
- net **+$41,520.82**
- trades **27,980**
- PF **23.7154**
- strict win rate **87.09%**
- expectancy **+$1.48395/trade**
- average hold **16.46 s**
- median hold **18 s**
- closed-trade balance DD ~$3.40

This is now the exact January hard comparator.

## Funded-cap utilization 027

Primary funded architecture:
- start cap 64
- +64 slots / $2,500 already-realized cumulative net
- hard base ceiling 256
- **+$154,538.37 / 24,646 trades / PF 4.0911 / +$6.2703 expectancy**
- realized balance DD ~$4,179.75

Unlock chronology:
- 64 from Jan 2 start
- 128 at 2026-01-12 15:00:25 UTC
- 192 at 2026-01-13 15:04:46 UTC
- 256 at 2026-01-14 11:53:41 UTC

The funded cap is not decorative. At every level median/p90/p99 utilization reached 100%, with skip rates ~91% at cap64, ~75% at cap128, ~50% at cap192, and ~65% at cap256.

## Full-tick funded-cap equity DD 028

Ordered every-tick Bid/Ask equity marking:
- funded128: +$83,897.56 / equity DD ~$10,712.77
- funded192: +$117,400.75 / equity DD ~$15,701.00
- funded256: +$154,538.37 / equity DD ~$17,547.11

Entry times, exit times and accepted P/L reconstructed exactly.

## Major new architecture — session surge capacity

The funded base cap remains 64 -> 256, but extra inventory is available only inside high-value NY phases.

Surge-only findings:
- NY17 +256 temporary slots: +$171,284.20 / 22,987 / PF 5.004
- NY16+17 +256: **+$186,768.13 / 23,498 / PF 5.353 / +$7.948 expectancy**
- NY16+17+18 +256: +$193,077.18 / 25,822 / PF 4.790

This is not global leverage expansion. The extra capacity is phase-routed.

## Quality routing

Hour 14 is negative and is removed from the quality base.

With hour14 removed and NY16/17 +256 surge:
- **+$187,384.63 / 22,502 / PF 6.152 / +$8.327 expectancy / 71.0% wins**
- realized balance DD ~$2,668.86

High-quality subset without hours14/18:
- +$184,064.51 / 18,649 / PF 8.569 / +$9.870 expectancy / 76.27% wins

Source subset diagnostic:
- excluding 9/14/18: +$175,082.14 / 14,950 / PF 10.14 / +$11.71 expectancy / 78.46% wins
- extreme quality subset excluding 7/8/9/12/14/18: +$151,193.57 / 8,755 / PF 13.17 / +$17.27 expectancy / 83.23% wins

## Weak-source displacement repair

Rather than delete all weak hours:
- 09 UTC minimum favorable M1 displacement: $1.00
- 12 UTC minimum favorable M1 displacement: $0.50

This raises the surge-quality portfolio to:
- +$188,891.46 / 22,104 / PF 6.226 / +$8.546 expectancy

## NY18 subphase gate

Best January net subphase set in the filtered base:
- retain 18:10-18:39 UTC
- +$189,264.59 / 21,324 / PF 6.416 / +$8.876 expectancy / 73.49% wins

## Massive breakthrough — NY16/17 heartbeat reopened under surge capacity

Previously-rejected NY16/17 heartbeat becomes strongly profitable after session-surge capacity removes the slot bottleneck.

Best screen:
- NY16 heartbeat ~1000 ms
- NY17 heartbeat ~1000 ms
- fixed 0.01 tickets
- one-event-per-source-per-market-tick scientific counting remains in force
- source14 removed
- 09/12 depth filters retained
- NY18 restricted to stronger middle subphases

January:
- **+$250,007.74**
- **24,083 trades**
- **PF 7.8372**
- **+$10.3811 expectancy/trade**
- **75.31% wins**
- realized balance DD ~$2,846.54
- max open 512 research heat frontier

Source contributions:
- 16 UTC: +$71,729.84 / 4,624 trades / PF ~13.50
- 17 UTC: +$102,464.87 / 2,175 / PF ~508.7
- 18 UTC: +$2,894.86 / 2,627
- London/overlap remain positive contributors

This is approximately 6.0x January R9 SYNTH net while retaining ~86% of its trade count.

## Quality version of the heartbeat-surge breakthrough

Removing only source18:
- +$247,112.88 / 21,456 / PF 9.956 / +$11.517 expectancy / 78.30% wins

Quality frontier excluding 8/9/12/18:
- **+$209,521.00**
- **11,726 trades**
- **PF 14.1419**
- **+$17.868 expectancy**
- **82.83% wins**

The new research problem is now explicit:
- net and expectancy already massively exceed January R9 SYNTH;
- trade density is close on the max-net frontier;
- remaining hard gap is PF/win-rate/speed while preserving the large net capture.

## Exact durable Library artifacts

Persistent root:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/`

New authoritative files:
- gamma02_funded_cap_utilization_027.py/json
- gamma02_funded_cap_equity_dd_028.py/json
- gamma02_jan_r9_synth_benchmark_029.json
- gamma02_session_surge_capacity_033.py/json
- gamma02_session_surge_quality_034.py/json
- gamma02_session_surge_subset_035.py/json
- gamma02_weak_source_displacement_036.py/json
- gamma02_ny18_subphase_gate_037.py/json
- gamma02_ny_surge_heartbeat_038.py/json
- gamma02_ny_surge_heartbeat_quality_039.py/json

## Next atomic unit

`GAMMA_02_SURGE_HEARTBEAT_EQUITY_DD_040`

Required before further promotion:
1. full ordered-tick equity-DD for max-net and quality finalists;
2. exact utilization/saturation of temporary 16/17 surge slots;
3. then attack PF/win rate with causal source routing, not by lowering trade count blindly.

No Jan-Jul promotion yet. R9 SYNTH remains the hard target.
