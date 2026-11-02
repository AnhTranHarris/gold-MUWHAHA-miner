# R9 v2 — chronological 30-second hindsight-teacher / foresight-student experiment

Date: 2026-11-01 (America/Chicago). Status: **RESEARCH FAILURE, NO MODEL PROMOTION**.

This experiment used the **complete eight original source-month archives**: Coinexx and Dukascopy, 2026-01, -02, -06, -07. All 64,515,445 ticks were used to reconstruct causally observable data at all 2,481,012 previously executed, nonoverlapping v2 baseline entry times. No trade entry file was sampled, truncated or extrapolated. R9 SYNTH monthly counts serve as immutable throughput references. R9 synthetic trade results are not runtime features.

## Freeze and provenance

Original R9 executable entry/exit baseline source: `8729a6345655a7b4ea31facc81982004ee2b8921`. Frozen v2 research source head: `35056fa38c11a7b2e9b9d6bab984af3368e905be`. High-volume research replay source branch: `carson/r9-v2-high-volume-event-stream-repair-20261101`. Verified eight full-month baseline descendant branch: `carson/r9-v2-eight-fullmonth-untrained-baseline-verified-20261101`. The existing EA and all these source branches remain unchanged. The eight original full ledgers and native raw ticks are already archived in the owner's primary Drive.

## Explicit non-hindsight feature contract

- The original entry's side, spread and evidence came from the original v2 decision tick.
- All quote-side event, bid/ask pressure, volatility, ATR-like surfaces, 5-minute rolling state, and 15m/1h/4h context inputs were computed from the raw tick source **at or before the prior completed 1-second quote bucket**.
- A separate high-resolution expansion uses completed 250ms slots strictly earlier than the entry's 250ms slot; it never reads the current incomplete slot or later quotes. This expansion completed on every source-month but is **NOT** fully trained/evaluated on all eight because the last Coinexx July multi-month fit exceeded this worker's memory/time budget. Partial models were not promoted.
- The prior-trade win rate, prior-trade net, and last exit gap are shifted to **previous completed positions only**.
- All future `net`, `mfe`, `mae`, `exit_ms`, `win`, `quality` and SYNTH historical marks are prohibited model input fields. Offline features and training labels are separately stored.
- This experiment uses the R9 trade lifecycle and realized outcome *up to* its stop/trailing/30-second timeout. Classification `quality` means **realized executable-side net > $0.10 and MFE >= $0.12 before exit** (with the simulator's $0.02 fixed fee). Values between -$0.10 and +$0.10 are tracked as neutral, not approved. This is a **proxy** for 30-second path quality; it does not certify that an unclosed position remains favorable at the exact 30-second timestamp, because most R9 positions exit much sooner. A true fixed-30s first-passage label needs the separate exact-path follow-through audit.

## Hindsight teacher vs foresight student

- The direct hindsight oracle selects future-profitable entries and can reach **100%** of this proxy-quality label at the R9 85%-trade-count quota in every source-month, solely because there are enough future-favorable candidates. This is retrospective **upper-bound arithmetic**, not predictive evidence.
- Weak SYNTH teacher labels were joined by original Coinexx-server-native minute and side, after UTC-offset reconciliation. A separate teacher model was fitted **on past dates only**, and its *predicted* output could contribute **at most 10%** of scoring. The true teacher flag is not used during test-time inference.
- A LightGBM Bayesian-like empirical posterior, payoff regressor, and weak teacher student were trained chronologically on disjoint dates with an independent older-day Platt calibration set. This is **not** a proof of a mathematically exact Bayesian posterior. A Neyman–Pearson-type acceptance threshold was set by the 90th percentile of calibration negative-class scores, but repeated quote events are dependent, so it is not a guaranteed 10% future false-trade bound.
- Four time folds per source: January earlier-day fit/calibration then a partial January check; February entire month using previous January; June entire month using Jan/Feb; July entire month using Jan/Feb/Jun. No future-month outcomes fit an earlier-month test model. Every test position was already nonoverlapping in the frozen high-volume source stream.

## Binding acceptance criteria

1. Per-source per-calendar-month selected completed trades >= 85% of identical-month R9 SYNTH completed positions (Jan 23,783 / Feb 28,495 / June 27,031 / July 20,725). Partial January test scores use an explicitly labeled prorated *diagnostic* floor, never reported as monthly acceptance.
2. >= 80% *quality* among selected trades on every **active trading day**, every active ISO week, and every full source-month. Missing days without trades are not reported as passing; volume is evaluated separately.
3. Positive commission-inclusive selected expectancy, defensible tail exposure, and broker-specific viability. No selection policy passes on these experiments.
4. The original baseline remains immutable, and all data used here were full-month original data. The selected-trade subset is a subsequence of original historical positions; **skipped entries have not been replayed through newly freed tick time**. This is a teacher/student *admission-filter diagnostic*, not a new complete EA backtest. A true integrated entry-runner replay is mandatory before any acceptance.

## Outcome

See `results/ALL_EIGHT_30S_SURVIVAL_AUDIT.json`, all eight `fold_*_summary.json`, and all eight `volume_*_summary.json` for exact counts, windows and negative experiments. The stringent expected-value + NP policy selected **zero** future-trades in the eight uniform resource-bounded fitted folds. The separate volume-constrained, still NP-calibrated rank policy selected trades, but its quality remained only about **17%–31%**, many months failed the 85% floor, and every fold lost money. No daily, weekly or monthly 80% quality target was achieved. Source-month upper-bound calculations show this is an **information problem**, not a mathematical absence of favorable historical outcomes.

## New data/mechanism audit

The first one-second feature student has almost no out-of-time discrimination (AUC approximately 0.49–0.59 across folds). The full 250ms/500ms quote-response extraction has therefore been built and preserved, together with the first partial experimental fits. The last-stage multi-month feature-combination needs memory-bounded or incremental learner implementation. Do not reinterpret a partial micro fitted model as cross-broker/whole-period success.

## Required next code boundary

1. Incremental, memory-bounded, reproducible fit for all eight 250ms + 1s + 5m + 15m/1h/4h contexts, *without* reducing evaluation coverage; add exact first-passage ordering and 30s executable-side continuation labels even for trades that exited early.
2. Separate continuation, reversal, pullback and spread-toxicity specialists with a calibrated regime-conditional payoff distribution. Treat adverse-path arrival and neutral no-follow-through as explicit competing causes, not simply a single binary success label.
3. Calibrate selection with upstream chronological disjoint data and monitor precision/volume/expected-net **jointly**. If constraints conflict, record FAILED rather than weakening safety or generating fabricated trades.
4. Only after the entry policy freezes, replay the policy **from all original ticks** to expose reentry opportunity changes. Do not claim the ledger-subset diagnostic is the full EA's executed P&L.

**Governance:** Original source and exact raw archives, not synopsis/summary text, remain the only authority for continuing work.
