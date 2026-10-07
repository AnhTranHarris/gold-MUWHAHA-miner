# GAMMA-02 — April Persistent NY17 Short Specialist 116

**Status:** APRIL DISCOVERY / MAY+JUNE FORWARD VALIDATED / JULY FAILURE BOUNDARY  
**Parent architecture:** 103/104 and 109 remain frozen  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Rule

Qualified parent must be:
- UTC hour 17;
- minute 40-59;
- H4 = H1 = M15 = M5 = short;
- parent direction = short.

Child renewal:
- q = $1.25
- rearm = 0
- fixed 0.01
- child cap 703

This is a narrower persistent subset extracted from April discovery. The broader April phase basket was rejected because May became strongly negative; this short-only subset survives forward.

## Chronological results

| Month | Net | Trades | PF | Win | Expectancy | Avg hold |
|---|---:|---:|---:|---:|---:|---:|
| Apr discovery | **+$9,716.65** | 12,484 | 2.667 | 92.41% | +$0.778 | 175s |
| May frozen | **+$10,092.80** | 18,305 | 1.896 | 85.26% | +$0.551 | 281s |
| Jun frozen | **+$4,671.62** | 16,076 | 1.330 | 85.64% | +$0.291 | 324s |
| Jul frozen | **-$300.98** | 3,771 | 0.921 | 72.47% | -$0.080 | 522s |

April-Jun cumulative: **+$24,481.07**.

## Scientific interpretation

The same exact continuation state survives two forward months after April discovery, so it is not merely an April curve-fit.

July is the first clear failure boundary:
- hold time expands to ~522 seconds;
- PF falls below 1;
- expectancy turns slightly negative.

Do not retune the April-Jun rule using July. July becomes the discovery month for another specialist/regime guard.

## Exact helper

`research/R9_GAMMA/helpers/gamma02_april_persistent_ny17_short_116.py`

## Next unit

`GAMMA_02_JULY_SPECIALIST_DISCOVERY_117`

Frozen architecture entering July:
1. high-activity 103/104;
2. March reverse 109;
3. April-Jun persistent short 116.

No August access.
