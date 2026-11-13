# R9 XAUUSD M60 event-time competing-risk and quote-activity experiment (13 November 2026)

**STATUS: FAILED OWNER'S 0.75 ROC-AUC GATE; SHADOW RESEARCH ONLY.** R9 EA remains unchanged. Both original 500ms-history and exact event-time features remain preserved; no synthetic OHLC path, no external indices, no volume fabrication.

## Scope and causal source

Nine original Coinexx XAUUSD broker tick source gzip months January–September 2026: **72,129,347 records**. Each original monthly SHA-256 revalidated before extraction against prior frozen source receipt, **303,934 original frozen R9 entries**, exact entry ordinal and timestamp matched to prior full feature cache; **607,868 independent BUY/SELL simulated actions** marked at the recorded entry Bid/Ask. Both directions are hypothetical alternatives *at the original R9 decision times*, not independently generated opportunities. This is not a deployable opportunity→action routing strategy and R9 occupancy/rearm would change if trades were changed.

## Proposed mechanisms (implemented and evaluated)

**Exact-event-time trend within trend:** rolling 100, 500, 1000, 3000, 5000, 15,000, 60,000 ms from all observed source-order tick revisions. Per-window signed midpoint displacement, gross variation, directional path efficiency, realized quadratic variation, nonzero directional reversal rate and update arrivals/second. Cross-window agreement, micro-vs-macro residual and nested subtrend alignment. No replacement by 500ms OHLC; original 145 features used as a baseline context only.

**Volume-free OBV/CMF analogues:** quote-revision balance `QRB=Σ sign(ΔBid+ΔAsk)`, quote-signed fraction, widening/tightening quote pressure, update-intensity logarithm. Completed-one-second quote activity flow `QAF=Σ count × (2Close−High−Low)/(High−Low) / Σ count` using **only completed 1s intervals before decision**. These quantities are observations of quotes, not executed market orders, displayed size, dealer liquidity or actual trading volume. Archived `last`, `volume`, `volume_real` are zero throughout the original 72.1M source rows. MT5 `iOBV(..., VOLUME_TICK)` counts tick updates; `iOBV(..., VOLUME_REAL)` does not create trade volume if the feed does not supply it. MT5 has no standard built-in CMF handle in the reference indicators list; CMF can be coded from bar OHLC and appropriate volume, but here it would still be quote-count-weighted.

**Spread-and-volatility-aware competing risk:** At each source R9 decision, for each BUY (`Ask` entry, future `Bid` exit) and SELL (`Bid` entry, future `Ask` exit), freeze a research stop `L=max(30, 2×spread_cents, 1.5×sqrt(Σ Δmid_cents² over last 1s))` and target `G=max(50, ceil(1.6L))` in integer XAUUSD price cents. At raw future ticks label which boundary arrives first (or none/censored) within 15s, with interval boundaries `[250ms,1s,3s,5s,15s]`. Apply separate modeled 20 XAU-price-cent fee buffer for economic diagnostics; this is **not** USD account commission, fill parity or slippage.

A multiclass LightGBM predicts `P(favorable bin k | alive at k, entry features)`, `P(adverse | alive)` and `P(alive)`. Cause-specific cumulative incidence uses `S_k=S_{k−1}(1−h⁺_k−h⁻_k)` and `CIF⁺=Σ S_{k−1}h⁺_k`. The model **does not** receive updated future quote observations at later hazard intervals; these are static entry-time landmark forecasts.

**Experiment fairness and compute control:** Four nested feature families (14 R9 context; compact earlier M60 features; +46 event-time trend features; +31 quote-count/CMF-style features). Same fixed LightGBM specification, objective and train/evaluation periods for all, with 40,000 deterministic chronological at-risk training exposures maximum per time bin, preserving observed class proportions within each bin. Every eligible source R9 opportunity is retained for evaluation in both sides, except genuinely censored labels; missing past observations are explicit NaN. Five chronological expanding train→test folds: Jan–Apr→May, Jan–May→June, Jan–June→July, Jan–July→August, Jan–August→September. All five test months have **previously been exposed** in earlier R9 research, so do not call this pristine or certified prospective OOS.

## Five-second favorable-first AUC (both possible actions)

| Test month | R9 entry context | Earlier M60 context | Exact event trend | Event trend + quote flow |
|---|---:|---:|---:|---:|
| 05 | 0.6889 | 0.6911 | 0.7078 | 0.7076 |
| 06 | 0.7008 | 0.7029 | 0.7181 | 0.7177 |
| 07 | 0.7248 | 0.7249 | 0.7388 | 0.7383 |
| 08 | 0.7181 | 0.7212 | 0.7370 | 0.7360 |
| 09 | 0.7070 | 0.7125 | 0.7266 | 0.7258 |

**All 20 five-second model/month checks FAIL 0.75.** Trend-within-trend improved the compact M60 competing-risk baseline on each month, approximately +0.014 to +0.017 AUC, but adding OBV/CMF-like quote flow **slightly worsened** the scores. These comparisons share labels/action universe within each new fold; they are *not* directly comparable to prior R9 original-direction fixed +50/−30 first-passage results, because the labels and action choices are different.

## Fifteen-second favorable-first AUC (both actions)

| Test month | Earlier M60 context | Exact event trend | Trend + quote flow |
|---|---:|---:|---:|
| 05 | 0.6375 | 0.6488 | 0.6489 |
| 06 | 0.6348 | 0.6449 | 0.6446 |
| 07 | 0.6527 | 0.6665 | 0.6661 |
| 08 | 0.6456 | 0.6574 | 0.6572 |
| 09 | 0.6431 | 0.6510 | 0.6507 |

The strongest 15s AUC is 0.6665. All fail.

## Trade volume and after-cost truth

An **unavailable live oracle** that chooses BUY or SELL using future outcomes would find a favorable-first 5s event at 38,043/303,934 original R9 decisions (**12.52%**) or 15s event at 90,212/303,934 (**29.68%**). Oracle figures measure the prevalence ceiling of *this particular barrier event*, not a mathematical ceiling of gold predictability or of profitability with different exits. Using hindsight would be prohibited in trading.

All five monthly event-time-trend hazard fits forecast **negative expected after-cost utility for both sides at all evaluated R9 entry decisions** under the specified strict BUY/SELL/WAIT rule: **zero positive-utility entries**, so no viable high-frequency strategy. To test high-volume retention independently, also evaluate a **frozen 75th-percentile cutoff from training-derived utility**, regardless of its sign. At 15s that cutoff retains only roughly **6.24%** of evaluation opportunities on average (regime-score drift), and the 15s observed quote-price net proxy is negative each month. The five-second holdout price economics are intentionally marked **unavailable** because the stored terminal return is a 15s path, not guaranteed 5s liquidation; do not apply that 15s return as a 5s fill.

These are hypothetical static-entry shadow outcomes, not realized Coinexx dealer fills, not MT5 PnL, not actual brokerage costs and not a full on-policy account simulation. Nothing should be merged to R9.

## Mechanisms now ruled out vs still open

- **Retain as genuine incremental information:** exact event-time trend persistence/nesting and price-revision cascades; 500ms aggregation discarded some useful within-bin sequence information.
- **Reject as demonstrated incremental signal in this test:** quote-count OBV/CMF analogues. They cannot reconstruct market buy/sell volume or displayed depth from `volume=0` source records; this experiment measured no additional AUC from them.
- **Persistent limitation:** fixed R9 *decision times* offer relatively few rapid profitable-barrier events in May–September; selecting both directions alone does not rescue the 0.75 AUC or after-cost utility.
- **What is actually missing for stronger microstructure inference:** executed trade prints and aggressor side, Bid/Ask *size*, real L2 liquidity/depth, broker-specific fill and slippage latency, and a broader independent decision-time universe. These are not recoverable from iOBV, CMF or quote counts.
- **Next experiment if approved:** target first-passage risk geometry and trigger-time sampling rather than training yet another model on fixed R9 entry timestamps. Preregister exact alternative entry decision times from raw ticks before inspecting labels, keep the entire decision-time denominator, and test true forward trade occupancy and after-cost economics. Do NOT add hundreds of arbitrary indicators or tune to exposed September.

## Reproduce (research environment)

Python>=3.11, numpy, pandas, numba, lightgbm, scikit-learn, joblib. Requires `/mnt/data/r9_m60_expanded/full_derived` (frozen original M60 features) and original monthly tick gzip; uses hardcoded pinned local paths in this experiment. From working folder, use `OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=2 OMP_NUM_THREADS=3 python src/extract.py` (reads all nine original files but does not alter them), then one fold at a time `python src/train.py --folds 4`, `--folds 5`, `--folds 6`, `--folds 7`, `--folds 8`. Per-fold receipts are in `results/fold_MM.json`. Run `python -m unittest discover -s tests -v` and `python src/verify_models.py`. All 15 local tests passed, 20 saved models reloaded with exact 40 recorded AUC results, all original raw month hashes checked. GitHub Actions status must be independently checked, not inferred from local tests.

Scientific basis: MetaQuotes iOBV / iVolumes documentation; standard CMF formula from TradingView/Fidelity; quote order-flow impact research (Cont, Kukanov, Stoikov). Avoid incorrectly naming the quote proxies genuine L2 OFI, actual volume or executable trading alpha.
