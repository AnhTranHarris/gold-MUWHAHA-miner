# R9 M60 — Coinexx-only indicator feasibility and research-stop rules

**Date:** 2026-11-13  
**Scope:** Existing Gold MUWHAHAHA Miner R9 60-second event-time branch; research only, no production deployment.  
**Owner decision:** Enable QRB/QAF observation in an isolated R9 branch. Do **not** install statistical trading filters below the hard 0.75 ROC-AUC acceptance gate; 0.80+ remains research target, not proof of profitability.

## What the pinned data contain—and do not contain

- Original 2026 January–September broker quote logs: 72,129,347 rows, 303,934 original R9 decision opportunities; observed Bid, Ask, timestamp/time_msc and tick flags.
- Historical `last`, `volume`, and `volume_real` are zero in the complete source audit. No real executions, aggressor-side classification, per-price resting sizes, L2/L3 depth or live latency/fill data can be recovered from these fields. No genuine microprice (depth-weighted mid), full order-flow imbalance, VPIN, true CMF, or actual-volume OBV.
- Flags overwhelmingly identify joint quote changes (~93.9% flag 134), so assume no independent trade-side insight from flag distribution until proven.
- New hazard evaluation used hypothetical BUY/SELL at the **same frozen original R9 entry timestamps**, not a full new decision-time universe or a deployed policy.
- Latest exact-event-time trend model: May–September 5-second pooled action ROC-AUC `0.707756, 0.718137, 0.738770, 0.736999, 0.726584`. The same model *with* QRB/QAF: `0.707615, 0.717726, 0.738305, 0.736012, 0.725815`. Thus QRB/QAF has not demonstrated incremental pooled AUC so far. Best R9-original-side AUC 0.726300; strong difference from pooled action AUC.
- 15-second AUC markedly lower; modeled positive-utility trade count zero in evaluated folds; 12.52% hindsight *either side* reach favorable-first 5-second barrier. The latter is **not** an ROC-AUC ceiling or tradable oracle.

## Formulas and native MetaTrader indicators: targeted matrix

| Diagnostic question | Coinexx-only mechanism | MT5 native analogue | Information status | Cost/priority |
|---|---|---|---|---|
| Has a statistically unusual price drift begun *at this instant*? | **Spread- and volatility-normalized two-sided CUSUM / sequential probability-ratio test** (SPRT), evaluated on observed quote changes; no future-bar close | `iAMA`, `iFrAMA`, `iADXWilder` provide slower completed-bar trend context | Exact tick CUSUM uses permitted data; native completed M1 bars lag 1–5-second decisions | **1: direct, cheap** |
| Is fast movement self-sustaining or only quote flicker? | **Marked quote-event intensity** (exponentially decayed upward/downward revision arrivals); optionally Hawkes self-/cross-excitation | `iVolumes(VOLUME_TICK)`, `iOBV(VOLUME_TICK)`, `iMFI(VOLUME_TICK)` are rough *bar-count*, not trade-volume analogues | Exact quote-event timestamps and Bid/Ask revisions support intensity; no actual aggressor flow | **2: direct, moderate** |
| Are the proposed stop/target reachable under current spread and volatility? | **Spread-aware analytical first-passage benchmark**, using train-only estimates of drift, realized variance and price-side distances; compare to empirical competing-hazard probabilities | `iATR`, `iStdDev`, `iBands` for completed-bar volatility; original R9 already has completed M5 ATR gate | Directly addresses stop geometry; diffusion model is misspecified in jumps/nonstationarity, so use only as a calibrated baseline | **3: direct, cheap** |
| Is the market persistently directional or oscillatory within its trend? | **Variance ratio**, sign-run persistence, permutation entropy; fractal dimension only with sufficient event count / short finite-sample caution | `iAMA`, `iFrAMA`, `iADXWilder` | Repackages price process; evaluate conditional *incremental* value beyond existing exact-event trend | **4: conditional, cheap** |
| Is apparent acceleration genuine, or microstructure bounce / discontinuity? | **Preaveraged realized variance / bipower jump contrast**, volatility of volatility; stable as-of return sampling | `iStdDev`, `iATR` | Raw ticks are enough; under 60s horizon, jump tests have sampling and microstructure bias | **5: conditional, moderate** |
| Did quote-price location and update-count pressure change? | **QRB/QAF** and spread widening/tightening; tick activity count | `iOBV(VOLUME_TICK)`, `iAD(VOLUME_TICK)`, `iMFI(VOLUME_TICK)`, `iBWMFI(VOLUME_TICK)`, `iChaikin` where supported | These reuse quote-count information; none yields actual volume or market orders | **Retained; do not clone redundant indicators blindly** |

**Do not prioritize:** real-volume variants (`VOLUME_REAL`), conventional L2 depth imbalance or size-weighted microprice, VPIN, full order-flow imbalance, synthetic 500ms OHLC-bar fills, or undisclosed ML packages, because they require unavailable information or violate causal source policy.

### Minimal quantitative definitions (candidate features only; not verified predictive alpha)

Let `m_i=(bid_i+ask_i)/2`, `s_i=ask_i-bid_i`, `a_i` be historical quote arrival time, and `d_i=sign(m_i-m_(i−1))`, with source-ordinal tie breaking for equal timestamps.

1. **Volatility-normalized sequential trend surprise:** `CUSUM+_i=max(0,CUSUM+_(i−1)+(m_i-m_(i−1))/sigma_hat-k)`, `CUSUM-_i=min(0,CUSUM-_(i−1)+(m_i-m_(i−1))/sigma_hat+k)`. Fit sigma and threshold **using past data only**; use spread as a separate state variable. Direct question: does directional change exceed recent noise before stops are reached?
2. **Signed arrival-intensity imbalance:** `I_tau(t)=Σ_{i<=t} d_i exp(-(t-a_i)/tau) / (1+Σ_{i<=t} |d_i| exp(-(t-a_i)/tau))`, computed for predeclared `tau` (e.g. 0.25, 1, 5 seconds). This is *quote revision* imbalance, not market-order OFI. Test incremental change versus existing QRB (high collinearity likely).
3. **Spread-aware drift-diffusion hitting probability baseline:** approximate `P(hit +G before -L | current price is already down by spread s)` under local Brownian drift `mu` and variance rate `sigma^2`: for `0<=s<L`, `p=(1-exp[-2 mu (L-s)/sigma^2])/(1-exp[-2 mu (L+G)/sigma^2])`; for `mu→0`, `p=(L-s)/(L+G)`. It ignores waiting time and jump risk. Estimate/calibrate only on training months and retain separately measured horizon censoring. Used to test whether label geometry, not missing indicators, is the limiting factor.
4. **Pre-registered variance ratio:** `VR(q)=Var(m_t-m_{t-q})/[q Var(m_t-m_{t-1})]` on an as-of regularized sample, with careful treatment of empty sample periods and bid/ask bounce. Estimate whether 100ms→1s direction predicts next-second continuation rather than reflection. A high sample VR alone does not establish useful economic momentum.

## How we decide whether formulas answer the question WITHOUT wasting months

1. **Do not create another gigantic 72M-tick feature cache.** Use existing frozen 303,934-opportunity and event-time derived caches on the primary Drive, validate hashes, then extract at most one predeclared compact candidate set on a bounded sample. Revisit raw ticks only for formulas not reconstructible from cached moments.
2. Direct screening: fit small chronologically trained baselines for CUSUM, intensity and analytical hitting probability separately, then in one joint ablation. Keep **both original-side AUC** and **pooled buy/sell AUC** and all 303,934 original opportunities in the accounting denominator. Evaluate May–Sep comparably, noting those months are previously research-exposed.
3. At each test, compute AUC, PR-AUC, 5s/15s calibration, regime/session slices, source count and **expected trade frequency**, plus spread/slippage sensitivity and complete-account quote-to-fill assumptions. A conditional high AUC that retains only a small subset does not pass the owner's high-volume objective.
4. **Stop rule:** if a mechanism adds less than a statistically credible incremental effect across held-out chronological months, or improves only training AUC, mark it negative and stop adding similar indicator families. Do not target 0.75 by tweaking the already-exposed evaluation months.
5. Require a **new post-September blind period** for any certification. No deployment/EA gating based on the current five retrospective months. An 0.80 AUC score alone never certifies positive expectancy.

## Native MQL5 implementation guidance

- MetaQuotes documents standard indicator handles such as `iAMA`, `iFrAMA`, `iADXWilder`, `iATR`, `iStdDev`, `iOBV`, `iMFI`, `iAD`, `iBWMFI`, `iVolumes`. Native handles are bar/timeframe calculations: use completed bars (typically CopyBuffer shift 1) to prevent future/partial-bar lookahead; M1 bars are too coarse to replace exact-event 100ms–5s features. Never fill missing subsecond history from an entire current M1 candle.
- `OnTick` can coalesce events while a previous tick handler is running. Newly enabled QRB/QAF uses only observed on-chart event callbacks; this may differ from lossless ordered source file traversal. The optional `CopyTicksRange`/`CopyTicks` functions can fetch ordered ticks but potentially block; assess offline parity and timing first, not in the critical trade path.
- The QRB/QAF feature module is default-ON **only on the isolated research branch**, for observational telemetry; no trade filtering, stops, targets, position sizing or R9 minute-bracket logic has been enabled from unapproved research results. No MetaEditor compilation, Strategy Tester, or forward parity has been verified.

## Sources

MQL5 technical indicator list: https://www.mql5.com/en/docs/indicators
MQL5 iOBV: https://www.mql5.com/en/docs/indicators/iobv
MQL5 iMFI: https://www.mql5.com/en/docs/indicators/imfi
MQL5 OnTick: https://www.mql5.com/en/docs/event_handlers/ontick
MQL5 CopyTicksRange: https://www.mql5.com/en/docs/series/copyticksrange
Cont, Kukanov & Stoikov, *The Price Impact of Order Book Events*: https://doi.org/10.1093/jjfinec/nbt003
Easley, López de Prado & O'Hara, *Flow Toxicity and Liquidity in a High-frequency World*: https://doi.org/10.1093/rfs/hhs053
