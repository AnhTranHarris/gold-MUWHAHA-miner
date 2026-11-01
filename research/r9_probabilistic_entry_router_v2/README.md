# R9 Probabilistic Entry Router v2 — Research Build

**Build date:** 2026-11-01  
**Status:** Python research implementation complete enough for chronological training. **No MT5 compile. No live authorization. No model promotion.**

## Purpose

Replace R9's old directional impulse/bracket entry with a causal BUY / SELL / WAIT router whose objective is executable first-passage survival and expected net value under the unchanged R9 stop / trail / 30-second lifecycle.

The authoritative design contract is `docs/BUILD_DESIGN_CONTRACT.md` and the native Google Doc stored in the user's main `Micro_account` Drive folder. The build does not alter the original `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5` baseline.

## Implemented mechanisms

### 1. Millisecond event clock + quote-response state

`src/router_v2_features.py`

- quote chronology uses millisecond timestamps;
- classifies Bid Up / Bid Down / Ask Up / Ask Down / Spread Widen / Spread Narrow;
- distinguishes ask-only, bid-only and joint quote revisions;
- gap reset prevents stale microstructure state from crossing quote droughts;
- keeps current event state separate from completed historical buckets.

### 2. Marked multiscale Hawkes-style intensity bank

Exponential causal memories at:

- 250 ms
- 500 ms
- 1 s
- 5 s
- 15 s
- 45 s
- 240 s

The bank tracks bid/ask directional intensity, spread expansion/compression intensity, burst level and decayed cross-follow transitions. These are transparent engineered event-intensity states; parameters are not yet claimed to be maximum-likelihood fitted Hawkes coefficients.

### 3. Rolling 5-minute market brain

Completed 250 ms buckets feed continuously rolling windows:

`250 ms → 500 ms → 1 s → 5 s → 15 s → 30 s → 45 s → 1 m → 5 m`

The 5-minute window must be fully warm before the router is considered locally ready. Missing intervals are not synthesized.

Features include causal displacement, path efficiency, realized volatility, ATR-like true range, event-time pressure/RSI state, Bollinger position and width, entropy/choppiness, turn rate, quote activity, spread state and liquidity-weighted price-anchor displacement.

### 4. Causal Fibonacci / impulse state

`CausalImpulseTracker` freezes an impulse start only after observed displacement and efficiency qualify. The extreme advances only as new quotes arrive. Retracement is measured from the observed extreme to the current quote. No future swing high/low is used to redraw past Fibonacci geometry.

### 5. Honest liquidity / "volume" treatment

Coinexx January samples show `last=0`, `volume=0`, `volume_real=0` on the inspected raw spot-gold quotes. Therefore the build does **not** claim centralized VWAP or true order-flow volume. It uses quote-event intensity, tick rate, quote-time / quote-activity weighted price anchors, spread behavior and explicit `volume_real_valid` flags. Valid future volume can be incorporated without changing the model interface.

### 6. 15m / 1h / 4h context priors

Completed one-minute bars create separate causal geometry for 15m, 1h and 4h. Each horizon has an explicit readiness flag. A short history is never silently presented as 1h/4h context.

HTF geometry is context only; it does not directly trigger a trade.

### 7. Multi-session state

Runtime session state is derived from UTC with timezone-aware local clocks where available:

- Sydney
- Tokyo
- London
- London/New York overlap
- New York
- rollover
- off-session

Session becomes Bayesian context rather than a binary allow/deny schedule.

### 8. Probabilistic latent market-state layer

Causal state probabilities currently cover:

- compression
- ignition
- continuation
- pullback
- exhaustion
- reversal
- volatility shock
- chop
- spread toxicity
- quote drought

These initial probabilities are deterministic causal state features, not final trained hidden-state probabilities. They are inputs/context for the learned entry model.

### 9. Competing first-passage labeler

`src/router_v2_labels.py`

For BUY and SELL separately, subsequent real ticks are used **only after the decision timestamp** to label:

- time to +$0.10 net frontier;
- time to +$0.30 net frontier;
- time to +$0.50 net frontier;
- time to adverse R9 stop;
- R9 trailing-stop updates;
- timeout at 30 seconds;
- MFE / MAE;
- downside CVaR proxy;
- final executable-side net result.

Horizon targets are available at 1s / 3s / 5s / 10s / 15s / 30s.

### 10. Bayesian competing-risk model

`src/router_v2_model.py`

The transparent model uses:

- quantile-binned Bayesian likelihoods for `FAVORABLE`, `ADVERSE`, `TIMEOUT`;
- hierarchical priors by side + session + dominant market state;
- multi-horizon Bayesian first-passage probability bank;
- expected net payoff from real outcome distributions;
- downside-tail penalty;
- optional SYNTH teacher weight capped at +10%, and only on already favorable REAL labels.

The SYNTH teacher is never a runtime feature.

### 11. Regime/context-specific Neyman-Pearson governor

NP thresholds are calibrated on negative real outcomes. Context-specific thresholds are used when enough calibration negatives exist; otherwise the model falls back to a global NP threshold. Insufficient negative calibration fails closed.

The NP alpha is a research sample-level selective-risk control, **not** a guaranteed live error rate under dependent market ticks.

### 12. BUY / SELL / WAIT router

The same causal state is evaluated counterfactually for BUY and SELL. Runtime chooses the action with the higher expected utility only when:

- expected utility is positive;
- the corresponding NP threshold passes.

Otherwise the action is **WAIT**.

Candidate generation itself is direction-neutral and intentionally permissive. Direction is not hard-wired by momentum before Bayesian comparison.

## Chronological training pipeline

`src/router_v2_dataset.py` processes raw Coinexx / Dukascopy files in original order. The full file is streamed to preserve rolling local and HTF context; only declared development dates emit label candidates.

Current declared development months remain:

- January 2026
- February 2026
- June 2026
- July 2026

`src/router_v2_train.py` implements chronological walk-forward folds:

1. fit only resolved outcomes before the current calibration day;
2. calibrate NP on the later calibration day;
3. replay the still-later development-check day without refitting;
4. carry earlier historical data forward only after it is chronologically available.

This corrects the previous retrospective pooled-fit defect where June/July could influence January/February development scoring.

## Tests and build probes

`tests/test_router_v2.py` currently verifies:

- bid/ask event classification;
- cross-excitation feature creation;
- causal impulse anchoring;
- first-passage ordering;
- R9 trailing behavior;
- future-tick invariance;
- teacher exclusion from runtime features;
- true 250 ms feature availability;
- explicit 15m/1h/4h readiness;
- sparse subsecond feature preservation in the fitted model;
- NP fail-closed behavior;
- WAIT action support.

All current tests pass.

### Real-tick feature probes

25,000 January ticks per source, no future labels and no trades:

- Coinexx: 10,198 ready 500ms decision slots; candidate spread mean ≈ $0.1987.
- Dukascopy: 7,284 ready slots; 7,049 direction-neutral candidate points; candidate spread mean ≈ $0.8806.

The different spread environment is preserved rather than normalized away.

### End-to-end build smoke

A bounded 25,000-tick prefix from each January source was used only to prove the plumbing:

`real ticks → causal features → future-path labels → Bayesian fit → NP calibration → BUY/SELL/WAIT replay`.

The smoke completed successfully with 11,944 labeled action paths. It is intentionally **not** a performance experiment and no result from it is approved or optimized.

## Files

- `docs/BUILD_DESIGN_CONTRACT.md` — exact build design requested by owner.
- `src/router_v2_features.py` — event/Hawkes/multiscale/context feature engine.
- `src/router_v2_labels.py` — first-passage / R9-lifecycle labeler.
- `src/router_v2_model.py` — Bayesian competing-risk + NP + utility router.
- `src/router_v2_dataset.py` — chronological dual-source dataset builder.
- `src/router_v2_train.py` — chronological walk-forward trainer.
- `src/router_v2_probe.py` — no-label real-tick feature probe.
- `src/router_v2_end_to_end_smoke.py` — bounded plumbing validation.
- `src/r9_replay.py` — preserved source-faithful R9 chronological replay helper.
- `src/extract_synth_teacher.py` — preserved SYNTH teacher extractor.
- `tests/test_router_v2.py` — deterministic causality / integrity tests.

## Non-claims

This build does not claim:

- profitable trading performance;
- full January/February/June/July optimization;
- MT5 / MQL5 compile success;
- live-safe NP guarantees;
- true centralized XAUUSD VWAP or order-flow imbalance;
- fitted production Hawkes parameters;
- approved entry policy.

The next scientific operation is full four-month chronological dataset generation and model optimization using the frozen v2 mechanism, followed by ablation and robust dual-source acceptance tests. Only after a frozen Python policy survives that stage should native MQL5 implementation/compilation begin.
