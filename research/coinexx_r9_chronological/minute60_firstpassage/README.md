# R9 60-second Coinexx XAUUSD multiscale first-passage research

**Status:** RESEARCH-ONLY / FAIL. **No EA modifications.**

## Scope and exact source

- The frozen baseline is the existing source-exact chronological R9 Python replay, not MetaTrader synthetic `Every Tick` reconstruction.
- Original monthly Coinexx XAUUSD tick data: January–September 2026, **72,129,347 rows**. The existing `r9_shadow_path_signatures/outputs/source_receipt.json` contains the original nine broker gzip SHA-256 hashes and the original 303,934 R9 trade events. Original data are read-only.
- The input candidate universe is **the R9 entries as executed by the frozen source engine**, not all possible BUY/SELL/WAIT decisions. Therefore the study cannot establish all-market directional predictability; it only evaluates whether a 60s model can rank those existing R9 entry opportunities. Do not treat any prediction as on-policy profit.
- Prespecified experimental labels use actual *later* quote sequence: target first = side-aligned favorable executable price change **+$0.50** from source R9 actual entry (BUY at Ask -> exit Bid, SELL at Bid -> exit Ask); stop first = **−$0.30**; otherwise no barrier at horizon. Separate horizons 5, **15 primary**, 30 seconds. If no sufficient future or a >10s quote gap intervenes, censor. Further **$0.20 price-equivalent cost** is applied when calculating *illustrative* shadow returns; this is NOT verified dealer fill/slippage or account USD and must not be treated as certified profitability.
- Extractor processes all raw source ticks to label **all 303,934 original candidates**, but for convolution training builds a **deterministically distributed index sample of 1,024 candidate entries per month before checking labels** (then rejects incomplete 60s history). The nine resulting files contain 8,189 as-of observations in total (9 months, 120 points x 5 channels). This is a **bounded pilot**, not a full-universe model certification.

## As-of feature construction

The 60s trailing window has 120 uniform 500ms grid points, each sampled as the **last actual source-ordered quote at or before that point** and never later than the exact entry ordinal, including within identical millisecond timestamps. Quotes >2,500ms old invalidate the full sequence; no future bars or extrapolated OHLC values are used.

Five channels: (1) R9-side-aligned normalized observed midquote revisions; (2) normalized observed spread; (3) log1p of observed source quote-event counts in each bin; (4) R9-side-aligned normalized cumulative mid-displacement; (5) absolute normalized midquote returns. Normalization derives solely from the same trailing observed window.

`src/hft.py`: **103 fixed formulas** over 1, 3, 5, 10, 15, 30 and 60-second windows: signed midquote change, total path variation, directional efficiency, realized quadratic variation, adjacent bipower variation, jump-proxy residual, semivariation, directional imbalance, reversal frequency, quote-arrival intensity, spread widening occupancy, maximum observed movement and volatility-normalized displacement, plus latest-interval terms. The jump-proxy should not be interpreted as an identified fundamental price jump absent noise-robust inference.

`src/rocket_fallback.py`: **custom, independently coded MiniROCKET-style transformation, NOT official aeon MiniRocket**. The official package was unavailable in the container because Python `pip` could not resolve its package-index host. Fallback uses all 84 length-9 combinations of three +2 and six −1 weights, four dilations, five channels, and three **January–April training-only** learned convolution quantiles; 5,040 positive-proportion pooled features. All parameters are frozen before subsequent monthly evaluations. This is a faithful family of fixed-kernel PPV temporal classifiers but **not a numerical reproduction of the canonical MiniRocket** algorithm. The released public reference is https://github.com/aeon-toolkit/aeon , BSD 3-Clause.

## Validation protocol

Train first four calendar months, evaluate May. Repeat with expanding training months (May→June, June→July, July→August, August→September) and **compare all families on identical heldout month rows within each pass**. There is no post-September untouched test in this project. Past extensive Jan–Sep R9 research also means these months are exposed at project level; do NOT claim prospective out-of-sample certification.

- Baseline: original R9 14 causal entry features, LightGBM classifier.
- HFT: same 14 entry features +103 advanced 60-second HFT features, same LightGBM.
- Convolution: 5,040 fixed-kernel PPV features, standardized RidgeClassifier.
- Fusion: original 14 + 103 HFT + 96 PPV features selected by **training-only** ANOVA F-statistic, LightGBM.
- For each holdout, score 15-second target-first vs stop-first or no-barrier; exclude all censored outcomes. Compute AUC, average precision, train-vs-holdout AUC, acceptance using **training-score** cutoffs, and illustrative price-net expectancy. The latter is not an actual alternate EA execution or trade fill history.
- OWNER HARD RULE: **AUC < 0.75 FAIL; 0.75–0.80 research-only; >0.80 target met but no deployment without positive entire-system after-cost executable expectancy, trade-frequency and drawdown checks.**

## Observed results (20 evaluated model-folds)

| Month checked | Baseline AUC | HFT AUC | Kernel-PPV AUC | Fusion AUC |
|---|---:|---:|---:|---:|
| May | 0.5394 | 0.5397 | 0.4879 | 0.5490 |
| June | 0.5733 | 0.5746 | 0.5302 | 0.5808 |
| July | 0.5676 | **0.6056** | 0.5180 | 0.5910 |
| August | 0.5345 | 0.5457 | 0.4947 | 0.5395 |
| September | 0.6003 | 0.5968 | 0.5508 | 0.5870 |

**All models fail**. Best evaluation is HFT July at 0.6056; the convolution model's May training AUC was 0.9983 and May evaluation AUC was 0.4879, demonstrating severe overfitting. Increasing complexity did not fix the causal ranking deficit. Selected subsets at the 80th percentile of *training* scores were all negative in the modeled quote-price return proxy across the reported folds, with small coverage. No source or MT5 change is warranted.

All full results including fold counts, in-sample AUC, AP and selection bands: `evidence/results.json`. Source hashes and derived sample hashes: `evidence/manifest.json`. Nine-mount derived compressed samples are stored separately from MT5_EXPAND in the data Drive, if available.

## Run from a fresh environment

Requires `python>=3.11`, `numpy`, `pandas`, `numba`, `scikit-learn`, `lightgbm` (check your actual installed versions and Py3.13 compatibility). From `minute60_firstpassage` directory:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python src/extract.py --raw-dir /path/to/broker_ticks --cache-dir /path/to/preserved_r9_candidate_cache --out /path/to/derived --months 01 02 03 04 05 06 07 08 09 --n 1024
PYTHONPATH=src python src/train.py --input-dir /path/to/derived --output-dir /path/to/new_results --through 09
```

The candidate cache contains nine `candidate_closes_2026_MM.csv.gz` files and `source_receipt.json`; **never substitute the synthetic MT5 trade ledger**. The original raw input schema and entire chronological engine must remain pinned.

**Follow-up scientific hypothesis, NOT tested here:** independently classify BUY/SELL/WAIT first-passage outcomes at a broader opportunity universe and separate stop-location sensitivity. Treat all current negative results as preserved. Do not tune existing May–September as if they remain pristine test months. The source-exact R9 parity tests and code remain unchanged.
