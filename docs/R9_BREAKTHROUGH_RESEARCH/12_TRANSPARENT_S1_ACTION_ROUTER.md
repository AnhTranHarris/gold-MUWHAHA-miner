# 12 — Transparent S1 CONTINUE / FADE / ABSTAIN Router

**Status:** implemented in the current R10 EA.

## Discovery

On the R9 REAL event population, a complex causal action-value model could be collapsed into a simple rule using the **last completed one-second move relative to the original R9 event direction**.

Interpretation:
- strong final-second movement already aligned with the break often represented late/chased impulse exhaustion -> FADE;
- strong final-second movement against the break often represented pullback/reacceleration -> CONTINUE;
- the ambiguous middle should be ABSTAIN.

## Balanced-strengthened profile

- CONTINUE if aligned S1 displacement <= -$0.255 **and** S1 range >= $0.285.
- FADE if aligned S1 displacement >= +$0.275 **and** completed S1 tick count >= 5.
- otherwise ABSTAIN.

## Defensive profile

- CONTINUE <= -$0.290
- FADE >= +$0.310
- same range/tick-quality rules.

The simple router captured most of the more complex model's forward profit while remaining directly auditable.

## Existing implementation

See:
- `RouterThresholds()`
- `RouteAuctionEvent()`

in `Experts/GoldMuwahahaMiner_R10_AuctionState.mq5`.

Only completed pre-entry one-second information is used.
