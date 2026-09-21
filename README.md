# gold-MUWHAHA-miner

Clean-room MT5 research project for the **Gold MUWHAHA Miner** XAUUSD Expert Advisor.

## Current R10 branch

Branch: `carson/mt5-r10-session-regime-certification`

Authoritative R10 EA:

- `Experts/GoldMuwahahaMiner_R10_AuctionState.mq5`

Current architecture notes:

- `docs/R10_AUCTION_STATE_REBUILD.md`

Historical R1-R9 EAs and their certification notes remain in the branch for lineage and comparison.

## R10 architecture

The current R10 compile/test candidate replaces the obsolete server-time profile strategy with the later causal research stack that is reconstructible from project evidence:

- R9 minute-boundary event population and S1 eligibility gate
- transparent **CONTINUE / FADE / ABSTAIN** action router
- balanced-strengthened and defensive auction-state profiles
- wide `$5.00` emergency room
- near-immediate `$0.01` ignition / `$0.01` high-water harvest
- 10-second **same-direction catastrophe memory** after an unharvested losing stop
- XAUUSD-only execution guard
- broker tick-size, volume-step, stop-level, filling-mode and trade-retcode handling

The old five server-time R10 execution profiles are no longer the active design.

## Important limitation

The later five-scale 1m/3m/5m/10m/20m auction portfolio and opposition-heat governor are **not claimed as implemented** here because their exact event-generator source is not present in the repository. Their research results remain part of the project history, but R10 will not fabricate missing rules from summary metrics.

## Next gate

1. Compile the authoritative R10 EA in MetaEditor with zero errors.
2. Run XAUUSD **Every tick based on real ticks** from January 1 through July 31, 2026.
3. Test `$100` and `$200` starting balances separately.
4. Record monthly net profit, gross loss and maximum dollar drawdown, plus overall Jan-July metrics and account survivability.
5. Keep **August 2026 sealed** until the Jan-July system is frozen.

No Python result or generated-tick result overrides the MT5 real-tick test.
