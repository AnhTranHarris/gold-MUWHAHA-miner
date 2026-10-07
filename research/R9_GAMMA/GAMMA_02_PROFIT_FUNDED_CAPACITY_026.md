# GAMMA-02 — Profit-Funded Capacity 026

**Status:** MAJOR JANUARY EXPOSURE-EFFICIENCY BREAKTHROUGH  
**Parent opportunity engine:** GAMMA_02_HOUR_SPECIFIC_HEARTBEAT_022  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Hypothesis

Do not grant the high-cap research frontier from the first tick.

Every ticket remains fixed 0.01. Begin with a smaller global position cap and unlock additional concurrent slots only after already-realized net profit has paid for them.

No Martingale, no loss-dependent sizing, no lot-size escalation, no borrowing against unrealized P/L.

If realized profit later falls, the allowed cap may contract; existing positions are not forcibly closed and new entries wait until open exposure is below the currently funded cap.

## Strongest cap-256 funding point

Funding rule:
- starting cap: **64**
- realized-profit unit: **$2,500**
- slots unlocked per unit: **+64**
- hard ceiling: **256**

January:
- **+$154,538.37 net**
- **24,646 trades**
- PF **4.09110**
- expectancy **+$6.27032/trade**
- realized balance DD **~$4,179.75**
- observed max open: 256

Static cap-256 comparator on the same heartbeat opportunity family:
- **+$157,787.96**
- **27,008 trades**
- PF ~3.958
- expectancy ~+$5.842
- realized balance DD ~$4,290.43

The funded-cap mechanism therefore captures about **97.94% of the static cap-256 net** while starting with only 64 permitted positions.

It also improves per-trade expectancy and slightly reduces realized balance DD in this January screen.

## Other useful points

Cumulative funding examples:
- start 64, +32 slots / $5,000, max 192: +$117,400.75 / 17,647 trades / PF 4.152
- start 64, +64 / $10,000, max 256: +$127,983.22 / 18,929 / PF 3.883
- start 32, +64 / $2,500, max 256: +$139,194.53 / 21,115 / PF 4.018
- start 64, +64 / $5,000, max 320: +$159,056.70 / 24,620 / PF 4.011

Daily-reset funding is more conservative but gives back substantial net; it is retained as a risk-control family rather than the January profit frontier.

## Scientific interpretation

This result separates **opportunity quality** from **capacity financing**.

The high-cap static results proved the opportunities existed. Profit-funded capacity shows that much of that economics can be accessed causally without granting maximum inventory at the beginning of the test.

This is an exposure architecture, not a new directional signal. It must therefore be validated separately from entry-edge claims.

High maximum caps remain research heat frontiers, not low-capital or live recommendations.

## Rejected/secondary entry experiments in the same recovery cycle

- heartbeat-specific London lifecycle: supporting efficiency only; +~$96 net versus the hour-specific heartbeat parent.
- CUSUM/intrinsic-time pulse: rejected for London and NY17; small positive velocity add-on for NY18 only.
- directional-change partial-recovery entry: rejected for London and NY17; full-reclaim desk-specific rebreak remains superior.

## Exact artifacts

Persistent Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/`

- `gamma02_profit_funded_capacity_026.py`
  SHA-256 `b567b1c5cd3d1545c8c1757bd7545ca5fcbdeb70e25f0f648caa35741b2ae0bc`
- `gamma02_profit_funded_capacity_026.json`
  SHA-256 `3da426e798a3ae6211e95cc29ef765fac9b98fdc2236e402e65e0013e58ed401`
- `gamma02_profit_funded_capacity_026b.json`
  SHA-256 `5501afe8e0e7163b6d31dcb332182874c5e148efca6b4e68721031e46b805dc1`

## Next required work

1. record unlock chronology and funded-cap utilization;
2. combine the funded-cap rule with the cleaner quality heartbeat frontier and compare against the velocity frontier;
3. full ordered-tick equity-DD replay for cap/funding finalists;
4. extract exact January-only R9 SYNTH benchmark;
5. freeze January architecture before chronological Jan-Jul validation.

R9 SYNTH remains the hard target.
