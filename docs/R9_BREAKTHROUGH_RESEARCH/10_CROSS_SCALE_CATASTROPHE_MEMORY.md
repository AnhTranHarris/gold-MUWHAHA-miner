# 10 — Cross-Scale Catastrophe Memory

**Status:** mechanism implemented in the current R10 EA for the single R9-event stream; multiscale portfolio form remains to be integrated.

## Rule

A full unharvested catastrophic stop is a **market-state event**.

After a catastrophic failure in direction X:
- temporarily distrust new direction-X auctions;
- continue allowing opposite-direction opportunities;
- expire the distrust after a short fixed horizon.

This is not a generic cooldown.

## Five-scale research result

Fresh five-scale baseline:
- +$309,222 net
- -$82,959 gross loss
- 614,739 trades.

Memory sweep:
- none: +$309.2K / -$83.0K
- 2 s: ~+$317.0K / -$75.2K
- 5 s: ~+$312.3K / -$74.4K
- **10 s: ~+$310.0K / -$73.8K**
- 15 s: ~+$307.9K / -$73.4K
- 30 s: ~+$303.4K / -$72.6K

Ten seconds is the benchmark-preserving knee.

## Existing MQL5 implementation

`Experts/GoldMuwahahaMiner_R10_AuctionState.mq5` already contains:
- `R10_CATASTROPHE_MEMORY_SEC = 10`
- same-direction block only;
- opposite side remains eligible;
- activation only after a losing SL that had not armed harvest.

The multiscale form must share the failed-thesis state across 1m/3m/5m/10m/20m engines.
