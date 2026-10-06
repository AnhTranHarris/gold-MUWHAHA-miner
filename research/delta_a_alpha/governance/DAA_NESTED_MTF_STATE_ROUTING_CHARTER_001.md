# Delta-A-alpha — Nested Multi-Timeframe State Routing Charter 001

**Status:** FROZEN BEFORE RESEARCH  
**Research category:** nested multi-timeframe state routing  
**System:** R9 Delta-A-alpha Grid System

## New architectural assumptions

### Trend within trend

Every timeframe/horizon may carry its own trend state.

A lower-timeframe trend is not automatically invalid because a higher timeframe points the other way.

Examples:
- fast downtrend inside medium uptrend may be a pullback;
- fast uptrend inside medium downtrend may be a counter-trend rally;
- aligned fast/medium/slow direction may represent impulse;
- opposite fast direction plus weakening parent may represent transition/reversal;
- low-efficiency states may represent range/noise rather than trend.

The system must model **relationships between states**, not use simple timeframe voting.

### Multi-state market awareness

The grid engine must be capable of representing at least:
- TREND / IMPULSE
- PULLBACK / COUNTER-TREND
- RANGE / ROTATION
- TRANSITION / REVERSAL
- VOLATILITY EXPANSION / SHOCK
- EXHAUSTION
- HOSTILE / ABSTAIN

State labels are research hypotheses, not hard-coded truths.

## Sandwich construction rule

Research proceeds vertically.

Each accepted structural discovery becomes a layer in the evolving grid architecture.

A new mechanism should:
1. preserve previously validated useful primitives;
2. improve at least one important metric materially;
3. avoid destroying velocity/survivability;
4. be integrated before the next breakthrough is layered on top.

Do not restart the grid from scratch after every discovery.

Do not optimize every category simultaneously.

## Current accepted primitives

- virtual grid/event lattice;
- adaptive A05/A10/A15 spacing;
- proof-before-entry as a core risk/admission primitive;
- single-owner fixed 0.01 execution;
- volatility-expansion continuation route as a January candidate;
- append-only scientific state journal.

Rejected:
- physical averaging grid;
- Martingale / loss-dependent sizing;
- universal mean reversion;
- universal continuation;
- blind recovery flip;
- dual first-proof mean-reversion ownership;
- shallow recovery-admission tree;
- simple ATR/gap/pace standalone filters.

## First hard category

**Nested multi-timeframe state routing.**

Goal:
determine whether relation between fast/medium/slow trend states can materially reduce wrong-direction gross loss while preserving a useful event stream.

This category is expected to control:
- direction authority;
- veto/abstain;
- pullback versus true reversal;
- continuation ownership;
- future recovery authorization.

It does not yet include session/news/macroeconomic routing.

## R9 REAL January benchmark

Canonical January 2026 R9 REAL:
- trades: 31,915
- win rate: 43.700454%
- net: -$6,651.62
- gross profit: +$3,785.28
- gross loss: -$10,436.90
- PF: 0.362682
- expected payoff: -$0.208417
- balance max drawdown: $6,659.15
- trade velocity: 1,519.76/day
- survival >=20s: 5.586715%

## Soft preferred breakthrough target

For this category, preferred first success is approximately **20% or more improvement in at least one R9 REAL January red-flag metric**, without catastrophic degradation elsewhere.

Primary target:
- gross-loss reduction >= $2,087.38
- equivalent January gross loss <= -$8,349.52

Secondary equivalents:
- PF >= 0.435218
- net loss >= -$5,321.30

The 20% figure is a soft preferred threshold, not a ceiling. Larger structural gains are preferred.

## Research style

Creative/original mutations are explicitly allowed.

Every speculative mechanism must be labeled as hypothesis until tested.

Public GitHub/community implementations may supply reconstructible components, but all adopted logic must be independently replayed on causal Dukascopy ticks.

Avoid the long path:
- no micro-threshold polishing;
- no giant feature sweep;
- no dozens of indicators;
- no optimizing one month until a marginal gain looks good.

Prefer large mechanisms that can change the meaning of an event.

## First research question

Can a compact multi-horizon state tensor distinguish:
- impulse continuation;
- pullback continuation;
- range/no-trade;
- transition/reversal

well enough to materially reduce the current grid's wrong-direction losses?

August sealed. Main `delta` read-only. MQL5 unauthorized.
