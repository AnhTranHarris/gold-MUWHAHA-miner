# DELTA-A R9 GRID MILESTONE 01 — Pre-August Adaptive High-Frequency Grid

**Status:** Major research milestone / August sealed / not MT5 production-authorized.

## Executive finding

The grid research has matured from a conventional physical basket grid into a causal, volatility-normalized, multi-specialist event engine with a calendar-blind cold-start state, mature specialist state, selective recovery routing, and a live portfolio-pressure wrapper. The current milestone is intended as a **potential future MT5 EA build candidate**, not as a live-deployment approval.

## Anti-overfit state machine

The system does not switch because the calendar says “February.” It begins in **BOOTSTRAP** and becomes mature-eligible only after:

- at least **25 active signal days**, and
- at least **25,000 completed strategy outcomes**.

The transition is delayed until the next market inactivity gap of at least **24 hours**, so the strategy does not change personality mid-session. In the historical Jan-Jul replay the criteria were satisfied after the January 29 session, and the first safe transition occurred at the first eligible event following the weekend gap.

A deterministic parity audit reconstructed **186,901** pre-pressure events and matched the previously completed tick-replay event specification exactly.

Event-spec SHA-256:

`55f04e2b8c39e3b7693a6850cb540b7cc00705623f6dccd12b1736b379fd249a`

## Portfolio-pressure wrapper

The current safety wrapper is causal and calendar-blind:

- hard cap: **250 concurrent positions**;
- reject a new same-direction entry once live net directional imbalance is already **225 positions** in that direction.

It removed only **332 trades (0.18%)** from the raw unified population while reducing peak floating-equity drawdown and concentration.

## Jan-Jul Dukascopy tick-level result

| Metric | R9 Grid Milestone 01 |
|---|---:|
| Trades | **186,569** |
| Winning entries | **113,958** |
| Win rate | **61.08%** |
| Net profit | **+$194,674.33** |
| Gross loss | **-$770,911.86** |
| Profit factor | **1.2525** |
| Expected payoff | **+$1.0434/trade** |
| True max floating-equity DD | **$27,904.26** |
| Minimum equity on $100k diagnostic account | **$92,519.38** |
| Max simultaneous positions | **250** |
| Max absolute directional imbalance | **231** |

All seven January-July months remain profitable in the accepted trade ledger. August was not accessed.

## R9 SYNTH human-facing alignment

- trade count: **85.1%**
- winning-entry count: **59.6%**
- net profit: **63.0%**
- expected payoff: **74.0%**
- win-rate level: **70.1%** relative to R9 SYNTH

The primary remaining gap is still **loss efficiency**: gross loss and profit factor remain far from the synthetic R9 reference even though volume, net profit, and expectancy are materially closer.

## Runtime / MT5 translation intent

The architecture is suitable for a future MT5 translation because the live decision path is deterministic and bounded:

1. per-tick virtual-grid state updates;
2. fixed feature/routing state;
3. one-event-per-tick-per-scale emission;
4. bounded specialist lifecycles;
5. fixed-size portfolio-pressure accounting;
6. no Martingale;
7. no future labels;
8. no month-coded routing.

The compiled research pressure gate processed roughly **17 million event decisions/second** in a local Numba benchmark. That is only a research-environment benchmark, not an MT5 latency guarantee. A production EA should use fixed arrays/ring buffers, avoid scanning full position history on each tick, and throttle diagnostic logging.

## Live-deployment cautions

The research account uses a $100,000 diagnostic balance and can carry up to 250 simultaneous 0.01-lot positions. That exposure is **not appropriate for a $100-$500 account without a separate physical-exposure/margin scaling layer**. A future MT5 build must preserve the virtual specialist/event engine while translating it into account-size-appropriate physical exposure.

The P75 execution surface is a research comparator only. Live MT5 must use actual Coinexx Bid/Ask, commission, slippage, stop constraints, margin, and broker execution behavior.

## Remaining gates before funded deployment

1. August holdout remains sealed until explicit owner authorization.
2. Build a production-grade MT5 translation only after separate owner authorization.
3. Validate on Coinexx **Every tick based on real ticks** and then live demo forward data.
4. Add account-size/margin scaling and, if needed, a prop-firm deployment wrapper without changing alpha.
5. Only after demo evidence should funded deployment be considered.

## Rollback

This milestone supersedes R2 as the current Delta-A grid research rollback target, while the prior R2 hard checkpoint remains preserved as historical provenance. Main `delta` is not modified.
