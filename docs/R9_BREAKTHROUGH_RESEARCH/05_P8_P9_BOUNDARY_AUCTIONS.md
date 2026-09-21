# 05 — P8 Sweep/Reclaim / P9 Acceptance

**Status:** validated research specialists; exact original Python event generator not preserved, so this is a faithful causal reconstruction specification.

## Boundary definition

A boundary must be known **before** the event. Use confirmed rolling/pivot/Donchian structure only; never retroactively draw a level from future bars.

## P8 — Sweep/Reclaim

Event sequence:
1. price penetrates a known boundary;
2. penetration is bounded / volatility-normalized;
3. price returns back through the boundary within a finite confirmation window;
4. completed-state features determine CONTINUE, FADE or ABSTAIN.

Representative result:
- ≈ +$30.6K
- ≈ 102K trades
- rolling May/Jun/Jul positive.

## P9 — Acceptance

Event sequence:
1. price penetrates a known boundary;
2. instead of reclaiming, price establishes itself outside;
3. displacement/body/range/efficiency state is evaluated;
4. action-value layer chooses CONTINUE, FADE or ABSTAIN.

Representative result:
- ≈ +$36.8K
- ≈ 135K trades
- rolling May/Jun/Jul positive.

## Key rule

A sweep is an **event**, not automatic reversal confirmation. Acceptance is also an event, not automatic continuation.

Community reconstruction references:
- https://www.tradingview.com/script/FG507Q8S-HTF-Liquidity-Sweep-Reclaim/
- https://www.tradingview.com/script/83NNMfO1-Liquidity-Sweep-Pivot-Reclaim-v2-memo/
- https://www.tradingview.com/script/z3UjniQ6-Liquidity-Entry-Zones/

These sources corroborate confirmed levels, sweep depth, reclaim windows and post-event confirmation.
