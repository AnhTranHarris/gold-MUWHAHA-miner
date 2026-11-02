# R9 v2 full-source-month hindsight-teacher / causal-student training

**Status: RESEARCH FAILURE. Zero of eight sources meets the combined 80% daily/weekly/monthly survival + 85% R9 SYNTH monthly volume + positive-net contract. No policy promoted.**

## Complete scope and source provenance

All January, February, June and July 2026 real tick archives from Coinexx and Dukascopy were read without truncation or sampled windows. Exact native timestamp and executable-side price matches were obtained for all 2,481,012 observed entries. The original v2 baseline engine was never overwritten.

Each surviving research candidate had a label = (profit > $0 after $0.02 simulated round-trip fee AND recorded exit within 30,000 wall-clock ms). Positions closed after 30 seconds are censored/not successful, because timeout is evaluated only when a subsequent quote arrives; a weekend-spanning close is not evidence of first-30-second survival. This is a coarse closed-trade proxy, **not** a fully event-ordered first-passage adverse-versus-favorable label.

89 runtime-only feature columns were reconstructed from each trade entry’s matched quote and exclusively earlier raw ticks (250ms, 500ms, 1s, 5s, 15s, 45s, 5m, 15m, 1h, 4h bid/ask displacement, quote revision intensity, spread compression, realized volatility). The SYNTH teacher’s same-minute/side historical positive marker enters only as +5% sample weight for real-tick-positive training examples; no teacher or future label appears in the runtime feature matrix.

## Complete ledger baseline

| Source | Month | Baseline trades | Verified within-30s profitable exits | Source success rate | 85% SYNTH floor |
|---|---|---:|---:|---:|---:|
| coinexx | 01 | 414,938 | 172,487 | 41.57% | 23,783 |
| coinexx | 02 | 477,916 | 196,925 | 41.20% | 28,495 |
| coinexx | 06 | 387,283 | 166,912 | 43.10% | 27,031 |
| coinexx | 07 | 312,856 | 133,413 | 42.64% | 20,725 |
| dukascopy | 01 | 238,644 | 57,497 | 24.09% | 23,783 |
| dukascopy | 02 | 236,293 | 53,183 | 22.51% | 28,495 |
| dukascopy | 06 | 235,139 | 61,553 | 26.18% | 27,031 |
| dukascopy | 07 | 177,943 | 37,549 | 21.10% | 20,725 |

## Chronological walk-forward student and Neyman–Pearson optimization

For each source separately, train on earlier months and current month through an early calendar cutoff; calibrate on later dates within the current month; evaluate on still-later dates. The entire source-month is used for feature generation; only held-out suffix dates constitute the reported chronological check. Older source-months can be in training but never later calendar months. The +5% SYNTH teacher weight applies only during fitting.

The NP calibration was searched over nine false-class rejection quantiles, 0.50 through 0.999, using calibration dates alone. No candidate calibration policy simultaneously achieved >=80% net-positive within 30 sec and positive expectancy. Therefore runtime policy approval = **FAIL CLOSED / NO TRADING**. The following tiny nonzero selections were forced negative diagnostic choices only and must not be deployed.

| Source | Month | Chronological check selected | Good30 rate | Net diagnostic | Days passing 80% |
|---|---|---:|---:|---:|---:|
| coinexx | 01 | 527 | 46.68% | $-90.73 | 0/10 |
| coinexx | 02 | 265 | 47.17% | $-43.15 | 0/8 |
| coinexx | 06 | 200 | 44.50% | $-46.02 | 0/11 |
| coinexx | 07 | 144 | 37.50% | $-31.43 | 0/12 |
| dukascopy | 01 | 625 | 28.80% | $-366.92 | 0/10 |
| dukascopy | 02 | 22 | 27.27% | $-14.69 | 1/8 |
| dukascopy | 06 | 275 | 31.64% | $-133.79 | 0/11 |
| dukascopy | 07 | 522 | 28.54% | $-274.17 | 0/12 |

## Chronological check: generous volume-constrained score ranking

As a deliberately optimistic *ranking diagnostic* only, the full-month 85%-of-SYNTH quota was prorated to each later chronological check window and the best scores selected ex post. Even with this retrospective threshold, no source-month approaches 80% survival; this is not a replay of changed entries.

| Source | Month | Check AUC | Target check entries | Survival of best-scored entries | Net outcome |
|---|---|---:|---:|---:|---:|
| coinexx | 01 | 0.548 | 14,437 | 44.95% | $-2,782.83 |
| coinexx | 02 | 0.522 | 6,950 | 45.94% | $-1,376.46 |
| coinexx | 06 | 0.521 | 10,610 | 45.77% | $-2,175.07 |
| coinexx | 07 | 0.528 | 8,405 | 45.53% | $-1,726.13 |
| dukascopy | 01 | 0.565 | 14,564 | 30.30% | $-8,582.63 |
| dukascopy | 02 | 0.561 | 7,678 | 27.32% | $-5,589.23 |
| dukascopy | 06 | 0.565 | 10,312 | 31.51% | $-5,322.13 |
| dukascopy | 07 | 0.601 | 8,548 | 27.94% | $-4,800.53 |

## Full-month optimistic *in-sample* volume constrained model

The final source-specific students were fitted using **all four real-tick months**. These are training artifacts only, **not** backtests or OOS. For a generous *upper bound on these fitted students*, the top exactly 85%-of-SYNTH count was picked retroactively from each full month. This uses future score distribution for the threshold and does not simulate newly available entries when earlier ones are rejected.

| Source | Month | Quota selected | In-sample survivor rate | Modeled net | Days at 80% | Weeks at 80% |
|---|---|---:|---:|---:|---:|---:|
| coinexx | 01 | 23,783 | 50.73% | $-3,828.49 | 0/26 | 0/5 |
| coinexx | 02 | 28,495 | 48.72% | $-4,824.33 | 1/24 | 0/5 |
| coinexx | 06 | 27,031 | 49.58% | $-4,762.00 | 1/27 | 0/6 |
| coinexx | 07 | 20,725 | 48.14% | $-3,883.56 | 1/28 | 0/5 |
| dukascopy | 01 | 23,783 | 33.50% | $-12,443.64 | 1/26 | 0/5 |
| dukascopy | 02 | 28,495 | 29.61% | $-20,458.52 | 0/24 | 0/5 |
| dukascopy | 06 | 27,031 | 33.02% | $-13,685.72 | 0/26 | 0/5 |
| dukascopy | 07 | 20,725 | 28.95% | $-11,729.61 | 0/27 | 0/5 |

## Perfect hindsight teacher supply ceiling (NOT EXECUTABLE)

An unrealizable oracle that selects only trades whose future realized net was already known can find enough winners to meet the monthly volume floor in every source-month and at least one on every baseline-active day/week. This proves that the *recorded candidate supply* is not empty; it does **not** prove that a causal student can distinguish those trades. We must not convert this oracle into runtime entries, add its future labels as features, or present its ideal P&L as achievable.

## Exact failure mechanism

1. Win-prediction information from top-of-book quotes is weak: held-out AUC across source-months ranges about 0.52–0.60, far from the accuracy needed for 80% high-volume first-30s survivability.
2. Dukascopy spread and quote-side execution lead to adverse net outcomes much more often; a universal filter is not sufficiently broker-calibrated.
3. Each baseline trade occupies a position and suppresses other signals; selecting a subset of a fixed baseline ledger changes subsequent available opportunities. A fresh streaming filtered re-simulation is mandatory before calling any optimized model a real EA baseline.
4. The original high-volume lane does not use the trained BNP governor. The fitted student is an additive research artifact only, and cannot be described as an updated live/MT5 EA.
5. The current research still lacks exact *ordered* first favourable vs adverse barrier timestamps in the massive baseline ledgers. The strict within-30s close classification is necessary but not sufficient for path-survivability certification.

## Next architecture-scientific action (not automatic deployment)

Build a true quote-event/action counterfactual **BUY, SELL, WAIT, DELAY** router for each source, with fill-aware first-passage labels and no reliance on fixed baseline position availability. The 250ms to 4h causal feature bank and Hawkes signals remain, but trade timing/side must become the predicted action, not a mere veto after the old high-volume runner chooses direction. Then run real-tick chronological stream and grade EVERY source-day/week/month, +85% SYNTH volume and positive P&L. Otherwise fail closed.

## Preservation law

All feature data and model weights are stored in source-month recovery checkpoints; independent raw ticks and R9 SYNTH references remain pinned. The full scripts and output JSONs are preserved. **Do not replace originals with a summary, do not reclassify this training experiment as deployable profit, and do not delete unsuccessful experiments.**
