# 11 — Near-Immediate Favorable-Excursion Harvest

**Status:** validated across five independently trained temporal engines; implemented in the current single-stream R10 EA.

## First cross-scale lifecycle

The boundary engines converged on:
- wide emergency room ≈ $5.00;
- favorable ignition ≈ +$0.03;
- high-water retracement ≈ $0.02;
- max lifecycle ≈ 90–120 s.

On untouched May-Jul this improved every scale by roughly 24–49% versus its older lifecycle while reducing gross loss about 6–8%.

## Stronger later discovery

Holding entry events and action decisions fixed, changing only lifecycle to:

- **+$0.01 favorable ignition**
- **$0.01 high-water trail**

improved May-Jul at all five scales.

Representative 1m:
- old +$13,605 / -$13,917 gross loss
- new +$15,309 / -$11,960 gross loss
- +12.5% net
- ~14% less gross loss
- catastrophic stops ~1,372 -> ~1,110.

The same direction reproduced at 3m/5m/10m/20m.

## Existing MQL5 implementation

`GoldMuwahahaMiner_R10_AuctionState.mq5` currently freezes:
- emergency stop = $5.00 price distance;
- activation = $0.01;
- trail = $0.01;
- maximum hold = 120 s.

Broker minimum stop distance still overrides an impossible requested trail.

Research interpretation: REAL Gold frequently gives useful MFE but does not sustain SYNTH-like serial persistence. Harvest early after proof of favorability.
