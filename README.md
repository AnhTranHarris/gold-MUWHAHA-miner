# gold-MUWHAHA-miner

Clean-room MT5 research project for the **Gold MUWHAHA Miner** XAUUSD Expert Advisor.

## Active R10 reconstruction lineage

Canonical post-R9 integration branch:

`carson/r10-r9-breakthrough-research-14-integration`

Research index:

- `docs/R9_BREAKTHROUGH_RESEARCH/README.md`
- `docs/R10_MASTER_REBUILD.md`

Authoritative current compile/test EA:

- `Experts/GoldMuwahahaMiner_R10_AuctionState.mq5`

Historical R1-R9 EAs and certification notes remain preserved for lineage.

## What the current EA actually implements

- R9 causal event population and completed-S1 eligibility
- transparent **CONTINUE / FADE / ABSTAIN** action routing
- balanced-strengthened and defensive S1 profiles
- wide $5.00 emergency room
- near-immediate $0.01 favorable ignition
- $0.01 high-water harvest trail
- 120-second maximum lifecycle
- 10-second same-direction catastrophe memory after an unharvested losing stop
- XAUUSD-only guard
- broker tick-size, volume-step, stop-level, filling-mode and retcode handling

## What has been reconstructed as post-R9 research but is not yet integrated into the EA

- P4 low-volatility rotation
- P6 expansion continuation
- P5 H1/H4 structural trend
- P8 sweep/reclaim
- P9 acceptance
- P11/P12 3-minute propagation
- P13 1m/3m/5m/10m/20m boundary ladder
- four-sleeve portfolio-knee logic
- worst-month-PF state-stability filter
- opposition-aware portfolio heat
- KEEP-vs-FLIP post-catastrophe routing

Each mechanism has its own cumulative research branch named:

`carson/r10-r9-breakthrough-research-XX-...`

The documentation records whether a mechanism is **implemented**, **faithfully reconstructed**, or **research-only / pending MT5 certification**.

## Scientific rules

- R9 SYNTH is a teacher/reference ceiling, not deployment truth.
- REAL ticks and broker-native MT5 testing determine execution validity.
- Invalidated look-ahead and retrospective-order experiments remain rejected.
- No Martingale or grid is introduced.
- Fixed 0.01 remains the research exposure until the strategy itself is certified.
- August 2026 remains the sealed holdout.

## Next engineering gate

1. Rebuild the multiscale boundary generators as independent MQL5 modules.
2. Reproduce their Jan-Jul research ledgers before integration.
3. Add four-slot portfolio state and opposition heat.
4. Add worst-month-PF capital priority.
5. Propagate catastrophe memory across scales.
6. Compile with zero errors/warnings.
7. Run XAUUSD **Every tick based on real ticks**, Jan 1-Jul 31, 2026.
8. Report monthly net profit, gross loss and max dollar drawdown.
9. Test $100 and $200 starting balances including marked-equity and broker-margin survivability.
10. Only after freeze: open August once.

No Python result or generated-tick result overrides MT5 real-tick certification.
