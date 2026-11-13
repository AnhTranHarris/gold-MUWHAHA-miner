# R9 M60 Joint Cross-Family Training — Source-Exact Research Handoff

**Date:** 2026-11-13 | **Status:** RESEARCH ONLY, owner acceptance gates NOT PASSED.

This is a continuation of the existing XAUUSD / Gold MUWHAHAHA Miner R9 M60 project, **not an EA rewrite**. The underlying MT5 source is unchanged and QRB/QAF telemetry remains enabled **on the isolated existing research branch**. No trained model is installed in an Expert Advisor.

## Frozen inputs and provenance

- Original Coinexx XAUUSD Jan–Sep 2026: 72,129,347 Bid/Ask quote events, original source SHA-256 rechecked for all nine months.
- Original source-ordered R9 decisions: 303,934 entries and 607,868 BUY/SELL counterfactuals; 120 censored, resulting in 607,748 labeled action observations.
- Upstream immutable features: 155-feature direct classifier baseline, 27 quote-only Hawkes-inspired excitation / latent directional pressure / spread-resilience proxy features, plus original R9 entry timestamps, risk barriers and labels.
- Added predeclared 55 cross-family interaction features (total 237), including QRB/QAF, nested trends, CUSUM, signed quote intensity, analytically derived first-passage features, latent pressure and resilience.
- All features and interaction transforms derive exclusively from quote observations at or before a frozen R9 decision ordinal. Missing 60s histories are retained missing in upstream columns and explicitly flagged in interaction columns.
- No executed volume, true liquidity quantities, trade aggressor direction or order book depth was reconstructed.

**Immutable upstream evidence:**
- Baseline 155 training: `R9_M60_JanSep_FullTraining_155Features_20261113.zip` on MT5_EXPAND, file ID `14DAEMRvfEW1cXvi2AWr9ix1w5Mh_-LXi`.
- Prior 27-proxy feature extractor/model evidence: `R9_M60_HawkesLatentResilience_20261113_Source_Models_Audit.zip`, MT5_EXPAND ID `1s1HzAs-BljB0yNC_3I4uSaAGMoAJCpXL`.
- Source-derived quote-proxy cache: `R9_M60_Coinexx_QuoteOnly_27Proxy_Derived_JanSep_20261113.zip`, primary Drive ID `17lYmG_JWczXTAqM-Tw-23f1pmw5ex5ym`.

## How this joint-training experiment works

1. Five expanding chronological development folds: Jan–Apr → May, Jan–May → June, etc. The R9 opportunity universe, frozen 5s target, barrier geometry, and quote-side outcomes are identical for all models.
2. Replay original saved 155 direct and 182 append-only models for exact comparisons.
3. Evaluate an **expanded capacity-only 182-feature** LightGBM, then the **same architecture with 55 cross-mechanism products/consensus states** (237 total); compare differences. Train a side-specific R9 original-direction model separately and two 50/50 fixed blends.
4. Fixed learning configuration: 160 trees, 23 leaves, learning rate .04, min 220 rows/leaf, L1=3, L2=24, max bins 63, seed 20261113. No per-month tuning or new label selection was used.
5. Fit a FINAL 237-feature pooled joint model and original-R9-side specialist on **all nine months**. Mark those **IN-SAMPLE ONLY — NO held-out AUC**.
6. Evaluate pooled AUC, R9 original-direction AUC, precision-recall, full opportunity counts and descriptive day-cluster paired resampling. **No execution-aware or account-level profitability is inferred.**

## Reproduction

Python 3.11+ with `numpy`, `scikit-learn`, `lightgbm`, `numba`, `joblib`. Source expects the frozen upstream research cache trees at `/mnt/data/r9_m60_proxy_20261113/` and original monthly broker gzip at `/mnt/data/` (pinned source paths for this snapshot). Restore those from the referenced archives, or adapt only the path configuration and rerun the source-hash checks.

```
python -m unittest discover -s tests -v
python src/fit_isolated.py --month 05 --family capacity_182
python src/fit_isolated.py --month 05 --family synergy_joint
python src/fit_isolated.py --month 05 --family original_side_specialist
# Repeat for evaluation months 06, 07, 08, 09 (independent processes).
python src/assemble.py
python src/fit_full_isolated.py --family joint
python src/fit_full_isolated.py --family r9_specialist
python src/verify_joint.py
python src/bootstrap_joint.py
python src/report.py
```

Independent training processes are important: the multi-fit variant intermittently exceeded this constrained execution runtime. No training-time subsampling was introduced in the isolated workflow.

## Decision

The best five-month mean pooled AUC was 0.739491 (expanded 182 control), versus 0.738513 (frozen 155); the joint 237 model scored 0.739282. Original R9 chosen-direction means were 0.723976 (182 control), 0.723175 (frozen baseline), and 0.723715 (joint). No original-direction fold reached 0.75. **None reached the 0.80 objective.** A day-block resampling interval for the original-direction joint improvement overlaps zero.

All May–September evaluation months were previously exposed to researchers. These results are development experiments, **not independent prospective OOS certification**. Do not merge these models into trading code, or infer profitable high-volume trading from AUC or full opportunity scoring. Preserve the next unseen period for true evaluation.
