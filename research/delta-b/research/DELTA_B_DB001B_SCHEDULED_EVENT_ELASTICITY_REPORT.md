# DELTA-B DB001B — Scheduled Event Elasticity Mechanics Report

**Status:** VERIFIED MECHANICS CHECKPOINT — NO PROFITABILITY CLAIM  
**Date:** 2026-10-06  
**Lineage:** DELTA-B only  
**Layer:** Grid Layer 1 — Intrinsic-Time Executable Lattice

## Question

Can the Grid respond to MEDIUM/HIGH scheduled USD events without either:

1. ignoring genuine release-time execution stress, or
2. suppressing HFT/scalping opportunity merely because the calendar says an event is important?

## Frozen scheduled-event input

DELTA-B now uses:

- `research/delta-b/reference/DELTA_B_USD_EVENT_TAXONOMY_V1.md`
- `research/delta-b/reference/DELTA_B_USD_EVENTS_2026_JAN_JUL_V1.csv`
- event-cache Git blob: `158e253611337f9d8da3911ad307118e3c2d8cf5`
- 132 Jan-Jul scheduled USD rows
- August excluded and SEALED

Primary release-time authorities are BLS, Census, BEA, Federal Reserve, and DOL schedules. `HIGH` / `MEDIUM` is a frozen DELTA-B research taxonomy and is not claimed to be a universal vendor label.

## Rejected first implementation — static calendar defense

The initial kernel applied fixed phase multipliers such as a full `1.8x` Q envelope and `0.20` entry-authority floor for every HIGH release.

January event-window replay showed this was too blunt.

### Static January aggregate

| Phase | Mean Q-context / Q-base | Mean entry authority | L0 events / 1,000 ticks | Shock fraction |
|---|---:|---:|---:|---:|
| NORMAL | 1.032 | 0.958 | 3.893 | 0.083 |
| PRE_HIGH | 1.241 | 0.591 | 3.790 | 0.090 |
| RELEASE_HIGH | 1.859 | 0.200 | 0.706 | 0.079 |
| DISCOVERY_HIGH | 1.495 | 0.400 | 1.556 | ~0.083 |
| STABILIZATION_HIGH | 1.185 | 0.730 | 3.479 | ~0.081 |
| PRE_MEDIUM | 1.134 | 0.776 | 4.749 | diagnostic |
| RELEASE_MEDIUM | 1.443 | 0.450 | 2.464 | diagnostic |
| DISCOVERY_MEDIUM | 1.287 | 0.592 | 2.865 | diagnostic |
| STABILIZATION_MEDIUM | 1.113 | 0.822 | 4.261 | diagnostic |

The critical failure was structural rather than numerical:

- HIGH release base-Q rose only about 29% versus PRE_HIGH;
- observed shock fraction did not rise with the fixed calendar defense;
- yet contextual Q nearly doubled;
- L0 event density collapsed from ~3.79 to ~0.71 / 1,000 ticks.

FOMC windows were the clearest example. The calendar layer was suppressing opportunity more strongly than observable quote stress justified.

## Accepted mechanics correction — conditional event elasticity

Scheduled-event severity now defines the **maximum defensive envelope**.

Observable tape stress determines how much of that envelope becomes active.

### Causal observed-stress score

```
spread_tail =
    clamp((prior_history_spread_percentile - 0.80) / 0.20, 0, 1)

shock_component =
    min(1, shock_score / 2)

path_component =
    clamp((path_noise - 2) / 4, 0, 1)

observed_stress =
      0.50 * spread_tail
    + 0.35 * shock_component
    + 0.15 * path_component
```

Phase activation begins from a bounded calendar prior and moves toward the maximum envelope only when the tape itself confirms stress.

Examples of phase base activation:

- PRE_MEDIUM 0.10
- PRE_HIGH 0.15
- RELEASE_MEDIUM 0.30
- RELEASE_HIGH 0.40
- DISCOVERY_HIGH 0.25
- STABILIZATION_HIGH 0.10

Then:

```
event_activation =
    base_activation
  + (1 - base_activation) * observed_stress
```

Q, hysteresis, confirmation and cost-buffer adjustments interpolate from neutral toward their configured cap. Entry authority interpolates from 1.0 toward the configured minimum.

During a scheduled event phase, the separate unscheduled-shock Q multiplier is **not stacked again**. During NORMAL state, the observable shock mechanism remains active as before.

## January mechanics comparison

| Phase | Static Q ratio | Dynamic Q ratio | Static authority | Dynamic authority | Static L0/1k | Dynamic L0/1k |
|---|---:|---:|---:|---:|---:|---:|
| NORMAL | 1.032 | 1.032 | 0.958 | 0.958 | 3.893 | 3.905 |
| PRE_HIGH | 1.241 | 1.092 | 0.591 | 0.819 | 3.790 | 6.444 |
| RELEASE_HIGH | 1.859 | 1.485 | 0.200 | 0.521 | 0.706 | 2.304 |
| DISCOVERY_HIGH | 1.495 | 1.231 | 0.400 | 0.695 | 1.556 | 3.229 |
| STABILIZATION_HIGH | 1.185 | 1.064 | 0.730 | 0.896 | 3.479 | 5.774 |
| PRE_MEDIUM | 1.134 | 1.038 | 0.776 | 0.924 | 4.749 | 6.838 |
| RELEASE_MEDIUM | 1.443 | 1.211 | 0.450 | 0.718 | 2.464 | 4.738 |
| DISCOVERY_MEDIUM | 1.287 | 1.117 | 0.592 | 0.812 | 2.865 | 5.286 |
| STABILIZATION_MEDIUM | 1.113 | 1.031 | 0.822 | 0.942 | 4.261 | 6.630 |

HIGH release shock fraction remained about `0.079`; the correction restored event resolution without weakening the observable shock detector.

For HIGH release state specifically:

- ROTATION ~76.95% -> ~68.35%
- TRANSIT ~15.10% -> ~23.60%
- RECLAIM ~0.04% -> ~0.14%
- L0 density ~0.706 -> ~2.304 / 1,000 ticks
- L1 density ~0.012 -> ~0.087 / 1,000 ticks

These are state/event mechanics only. No trade profitability is inferred.

## Additional QA defect caught

The first observed-stress implementation used:

```
sum(history <= current_spread) / N
```

after appending the current spread.

With a constant spread this falsely produced a 100th-percentile reading.

This was corrected to a **prior-history tie-midrank percentile**:

```
( count(history < current)
  + 0.5 * count(history == current) ) / N_prior
```

A stable repeated spread therefore sits near the 50th percentile rather than manufacturing stress.

## Exact committed-byte QA

GitHub branch-native workflow:

- `.github/workflows/delta-b-grid-qa.yml`
- workflow Git blob: `23a5c3bd677b6c1a5c9e5fc85b3a788651d0a59d`
- workflow run: `37455926127`
- checked-out commit: `e17dac49911586ae8f12bbb6693f4132027a89e8`
- result: **SUCCESS**
- Python: 3.11
- compile gate: PASS
- exact committed tests: **13/13 PASS**

Current verified code blobs at that run:

- Grid kernel: `f8c200648de0a94571bd24952cfa5249878fd96b`
- QA: `c24aef599c95a19227d85fb14a6c4affb0601a6a`

Regression tests now include:

- DST-aware London sessions
- HIGH-over-MEDIUM event priority
- non-USD event exclusion
- Q response to friction
- conditional HIGH-release defense
- flat-spread tie-midrank behavior
- HIGH scheduled shock cannot exceed configured envelope
- NORMAL unscheduled shock retains its defensive multiplier
- threshold cannot shrink mid-leg
- directional-change event emission
- transition-only reclaim semantics
- shock-state classification

## Decision

**Carry forward conditional event elasticity.**

The static scheduled-event multipliers are rejected as the active event mechanism.

The governing principle for DELTA-B Grid Layer 1 is now:

> Calendar severity sets the maximum defensive envelope; the observed tape determines how much protection is actually activated.

This is a mechanics breakthrough because it resolves a lower-layer architectural conflict between scheduled-event awareness and high-frequency opportunity retention.

It is **not** yet evidence that the Grid makes money.

## Next unit

`DB001C_MINIMAL_EXECUTABLE_SCALP_LIFECYCLE`

The next unit attaches the smallest possible trade lifecycle to Grid events, with no Volume Profile and no RSI:

- transition/event-based entries only;
- actual Bid/Ask economics;
- no martingale or adverse adds;
- fixed 0.01 lot;
- causal stop/harvest/timeout;
- chronological one-account ledger;
- gross profit/loss, net, DD, opportunity retention, loss clusters;
- later $100/$500/$1k/$10k overlays.

Grid Layer 1 must demonstrate economic value before Layer 2 Volume Profile begins.
