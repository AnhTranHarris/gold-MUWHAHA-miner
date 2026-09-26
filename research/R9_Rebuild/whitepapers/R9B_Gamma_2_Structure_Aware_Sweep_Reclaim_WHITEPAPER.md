# R9B_Gamma_2_Structure_Aware_Sweep_Reclaim — Public Technical White Paper

## Status

- **Canonical ID:** `R9B_Gamma_2_Structure_Aware_Sweep_Reclaim`
- **Promotion:** FORMAL SPECIALIST BREAKTHROUGH
- **Role:** High-density sweep/reclaim opportunity owner with market-structure-dependent lifecycle
- **Standalone profitability:** Positive Jan–Jul in exact Dukascopy replay
- **R9 SYNTH density:** 98.35% of SYNTH trade count
- **R9 SYNTH successful-trade count:** 91.63% of SYNTH winner count
- **August:** sealed

## Executive Summary

R9B_Gamma_2_Structure_Aware_Sweep_Reclaim solves a problem that Gamma_1 did not: **trade density**.

Instead of improving results by rejecting more opportunities, Gamma_2 reconstructs a high-frequency microstructure state machine from the older R8 research family and recertifies it on the current exact Dukascopy stack. The entry engine distinguishes liquidity sweep/reclaim behavior from ordinary continuation and then makes the **exit geometry depend on completed multiscale market structure**.

Jan–Jul exact results:

- **215,725 trades**
- **175,143 winners**
- **81.19% win rate**
- **+$29,583.12 net**
- **+$75,039.31 gross profit**
- **-$45,456.19 gross loss**
- **PF 1.6508**
- **Max DD $217.29**

R9 SYNTH executed 219,342 trades with 191,136 winners. Gamma_2 therefore reproduces **98.35% of SYNTH trade density** and **91.63% of SYNTH winning-trade count** while remaining causal and exact-tick reproducible.

It does **not** reproduce SYNTH economics yet. Net profit is only 9.57% of SYNTH net, and July is fragile under wider spread stress. The next bridge problem is therefore no longer opportunity count. It is **monetization per successful trade and regime-aware hold/exit ownership**.

## Problem Definition

Gamma_1 materially reduced toxic R9 financing but retained only ~44.6% of R9 trades. That was scientifically useful but investor-inadequate because R9 SYNTH's defining behavior included both high accuracy and very high event participation.

The project history contained two relevant clues:

1. the older R8 microstructure system explicitly classified `CONT_UP/DN` and `SWEEP_UP/DN` states and produced very high trading density;
2. later R9/R10 research showed hold/exit quality depends on market structure, event persistence and favorable-excursion renewal rather than one universal trail.

Gamma_2 reconstructs those ideas under the current causal exact-tick rules.

## Reconstructible Entry State Machine

Core state:

- liquidity lookback: **20s**
- velocity lookback: **5s**
- state persistence: **2s**
- state expiry: **20s**
- break buffer: **$0.10**
- reclaim distance: **$0.15**
- minimum directional displacement: **$0.15**
- minimum directional efficiency: **0.30**
- cooldown: **1s**
- maximum entries/minute: **5**
- session-adaptive completed-M5 ATR regime gate
- modeled baseline half-spread: **$0.10**

Action ownership:

```text
upper liquidity level swept
        ↓
price reclaims beneath the swept zone
        ↓
SWEEP_UP state
        ↓
SHORT

lower liquidity level swept
        ↓
price reclaims above the swept zone
        ↓
SWEEP_DN state
        ↓
LONG
```

The first break is not treated as a continuation entry. The market must demonstrate the sweep/reclaim transition.

## Structure-Aware Lifecycle

Completed 1m / 3m / 5m / 10m / 20m states describe environment and persistence potential.

They **do not vote entry direction**.

If fewer than three scales align:

- stop: **$3.00**
- trail activation: **$0.18**
- trail: **$0.05**
- max hold: **60s**

If at least three scales align:

- stop: **$1.00**
- trail activation: **$0.10**
- trail: **$0.04**
- max hold: **60s**

This reproduces the historical project insight that the same event should not receive the same exit geometry under every structural condition.

## Jan–Jul Validation

| Month | Trades | Winners | Net | Gross Loss | Max DD |
|---|---:|---:|---:|---:|---:|
| Jan | 30,943 | 25,368 | +$5,131.05 | -$6,091.21 | $40.80 |
| Feb | 31,072 | 25,556 | +$9,545.09 | -$6,886.70 | $29.05 |
| Mar | 39,690 | 32,778 | +$8,076.73 | -$8,347.92 | $28.72 |
| Apr | 29,320 | 23,554 | +$2,683.36 | -$6,403.31 | $48.33 |
| May | 27,964 | 22,795 | +$2,109.48 | -$5,781.26 | $47.53 |
| Jun | 30,023 | 24,342 | +$1,969.92 | -$6,261.39 | $37.48 |
| Jul | 26,713 | 20,750 | +$67.48 | -$5,684.41 | $217.29 |
| **Total** | **215,725** | **175,143** | **+$29,583.12** | **-$45,456.19** | **$217.29** |

## Density Benchmark

R9 SYNTH:
- 219,342 trades
- 191,136 winners
- 87.14% win rate
- +$309,122.85 net

Gamma_2:
- 215,725 trades = **98.35% of SYNTH density**
- 175,143 winners = **91.63% of SYNTH winner count**
- 81.19% win rate
- +$29,583.12 net = **9.57% of SYNTH net**

Relative to the R9 REAL benchmark, Gamma_2 improves net by about **$79,868** and closes about **22.22% of the REAL→SYNTH net bridge**.

## Robustness

Aligned-trail neighborhood at baseline cost:

- $0.03 trail: 215,741 trades, +$29,376.96, PF 1.648, every month positive
- $0.04 trail: 215,725 trades, +$29,583.12, PF 1.651, every month positive
- $0.05 trail: 215,702 trades, +$29,712.23, PF 1.652, every month positive

A stricter structure threshold of four aligned scales also remains stable:

- 210,596 trades
- +$29,510.92
- PF 1.626
- 172,845 winners
- every month positive

Wider-spread stress degrades July first. At $0.11 half-spread the system remains strongly profitable overall but July turns negative. This is a known boundary and a direct target for future event/regime-aware lifecycle research.

## System Interaction With Gamma_1

Two chronological integration forms were tested.

Single-slot Gamma_1 + Gamma_2:
- 301,220 trades
- 211,878 winners
- +$12,933.63
- PF 1.173
- Max DD $1,897.53

Two-sleeve opposition-aware integration:
- 309,936 trades
- 215,796 winners
- +$11,332.63
- PF 1.146
- Max DD $2,700.17

Both are materially inferior to Gamma_2 alone.

Therefore **Gamma_1 is not automatically stacked onto Gamma_2**. Gamma_1 remains a valid formally discovered toxicity specialist, but under the current active architecture Gamma_2 is the superior high-density owner.

## Why This Is a Breakthrough

Gamma_2 changes the project bottleneck.

Before Gamma_2:
- accuracy could be improved only by heavy filtering;
- trade count collapsed far below SYNTH;
- the investor concern was missing opportunity density.

After Gamma_2:
- trade count is essentially SYNTH-scale;
- successful-trade count is close to SYNTH;
- every Jan–Jul month is positive at baseline cost;
- structure-dependent lifecycle logic is causal and reconstructible.

The remaining gap is now primarily **profit per successful trade**, especially during slow/low-volatility July-like states.

## Refinement Starting Point

Preserve:
- sweep/reclaim entry ownership;
- high trade density;
- completed multiscale structure as lifecycle context;
- baseline causal timing;
- max five entries/minute;
- August seal.

Next research should focus on:

1. **HARVEST / MEDIUM / RUNNER** state-dependent exits.
2. MFE renewal count and renewal spacing.
3. Giveback relative to current MFE.
4. Directional-change overshoot size/age.
5. Tick-arrival/activity acceleration.
6. Event-time bar physical duration.
7. structure-specific trail expansion/contraction.
8. explicit event/news-volatility state where reconstructible from market data rather than retrospective calendars.
9. orthogonal FADE/rotation ownership for events Gamma_2 does not take.

The objective is to move successful-trade monetization toward R9 SYNTH without materially reducing the ~216K trade count.

## Revision History

| Revision | Change |
|---|---|
| 1.0 | Initial formal promotion after Jan–Jul exact replay, trail/structure stress, and Gamma_1 integration test |

---
This document records historical research evidence and reproducible mechanism behavior; it is not a promise of future trading performance.
