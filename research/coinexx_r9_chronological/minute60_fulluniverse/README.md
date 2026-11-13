# R9 M60 full-universe AUC ceiling audit — source and evidence

Preservation-only branch. The existing `minute60_firstpassage` and production EA remain untouched. This is a full-universe extension of the failed 8,189-sample model.

**Result: 0/20 15-second model-month ROC-AUC checks pass the 0.75 hard cutoff. Best 0.6100.** Secondary 5-second horizon reaches 0.7043, but its selected subsets still fail after-cost quote-price expectancy.

See [FULL_UNIVERSE_RESULTS.md](FULL_UNIVERSE_RESULTS.md) for mathematical details, source provenance, five-fold results, and missing-data diagnostics.

The 120-point historical representation is constructed exclusively from actual Coinexx source-ordinal past Bid/Ask quotes; cost-aware hypothetical first-passage labels use only future actual quotes and are never model inputs. Original 103 HFT features and first-passage engine are imported from the preserved sibling `minute60_firstpassage/src`. No new raw data are needed. Optional model caches and complete receipts are in the associated MT5_EXPAND and primary Drive archives.

To rerun full feature extraction with downloaded monthly original source and candidate cache:

```bash
export PYTHONPATH=research/coinexx_r9_chronological/minute60_fulluniverse/src:research/coinexx_r9_chronological/minute60_firstpassage/src
python research/coinexx_r9_chronological/minute60_fulluniverse/src/full_extract.py \
  --raw-dir /path/to/coinexx/raw --cache-dir /path/to/original/r9_candidate_cache --out-dir /path/to/new/full_derived
python research/coinexx_r9_chronological/minute60_fulluniverse/src/train_full.py \
  --input-dir /path/to/new/full_derived --out-dir /path/to/new/full_results
python -m unittest discover -s research/coinexx_r9_chronological/minute60_fulluniverse/tests -v
```

Local diagnostics `horizon_economics.py`, `immediate_stop_hazard.py`, `audit_quote_fields.py`, `save_shadow_models.py`, and `verify_full.py` default to their study workspace and are not live EA modules. Five frozen SHADOW-ONLY trained models with exact-score replay verification are packaged separately. **No out-of-sample result has been certified as profitable or safe to deploy.**
