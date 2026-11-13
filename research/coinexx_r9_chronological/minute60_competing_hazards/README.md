# R9 M60 event-time competing hazards / quote-flow proxies

**Experimental status: FAILED owner ROC-AUC gate (<0.75), shadow only. Do not merge into the EA.**

This source-exact continuation uses all nine original 2026 monthly Coinexx XAUUSD tick gzip files (72,129,347 quotes) at the original **303,934 frozen R9 entry timestamps**, and produces **607,868** hypothetical BUY/SELL side-specific first-passage paths. Production `GoldMuwahahaMiner_R9_HybridGate.mq5` is unchanged.

## Included research

- `src/event_engine.py`: exact timestamp/ordinal 100ms to 60s trend-within-trend features, source quote revision balance (not actual volume), completed-second quote-activity flow (not money flow), spread/volatility-aware stop/target, actual future BUY/SELL Bid/Ask first-passage events.
- `src/extract.py`: original-source SHA verification and monthly derived feature/label receipts; never modifies broker ticks.
- `src/train.py`: time-dependent competing-risk hazard at [250ms, 1s, 3s, 5s, 15s] with four nested feature families, five chronological expanding train→test checks May–September, prior-training frozen utility thresholds and full-source original R9 opportunity denominator.
- `src/verify_models.py`: 20 serialized model hashes and 40 AUC value readback tests.
- `tests/`: 15 local unit tests for causal boundaries, future-label isolation, risk-set timing, missing history, volume-proxy code and model utility.
- `RESULTS.md`: detailed formula, AUC, pricing, missing-data and trade-coverage audit.
- `manifest.json`: source, 9 monthly derived, and 20 model digests.

## How to reproduce

Requires Python with numpy, pandas, numba, lightgbm, scikit-learn and joblib. Original nine Coinexx monthly tick gzip and the preceding frozen `/mnt/data/r9_m60_expanded/full_derived` archives are required. Source code uses pinned local research paths and can be copied into the matching directory.

```bash
OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=2 OMP_NUM_THREADS=3 python -m unittest discover -s tests -v
OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=2 OMP_NUM_THREADS=3 python src/extract.py
OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=2 OMP_NUM_THREADS=3 python src/train.py --folds 4
# repeat --folds 5, 6, 7, 8 separately; each writes one receipt
OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=2 OMP_NUM_THREADS=3 python src/verify_models.py
```

**Model AUC is not win rate, actual dealer fills or account-USD PnL.** AUC <0.75 fails. >0.80 target does not itself grant deployment permission. All five original validation months had already been exposed in prior R9 research; this is retrospective development evidence only. See `RESULTS.md` for exact results and risk limitations.
