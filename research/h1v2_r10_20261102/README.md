# H1V2 R10 — source-exact order-path hazard research, 2026-11-02

Status: **FOUR FULL MONTHS COMPLETE; EXTREME BUY/SELL SKEW FAILED.** Not a deployable policy. Do not merge with R9 EA.

- Jan/Feb/Jun/Jul Dukascopy: 32,290,648 raw quotes; 15,401,392 first-observed 250ms causal decisions. Original H1V2 teacher 30s BUY/SELL strict labels and original R9 stop/trail/fee exits unchanged.
- 48 newly engineered quote-ordinal grammar features per event (4/16/48 raw quote history). All four full-month feature arrays were built and source-SHA-pinned. 6 R10 unit +10 original H1V2 unit tests pass.
- 20 full-population side-specific motif grids, 30 confidence/economic gates per grid = 600 full-month cohort experiments. **All fail** the joint 80% strict-success and minimum 80% R9 SYNTH volume target, even though grids fit/evaluate the same month's future labels.
- Bounded direct three-class LightGBM research fit (40,000 chronological samples/month; 160k total training, 101 asof features, 30 trees/31 leaves). Whole 15.4m four-month universe scored and every threshold replayed using original quote-ordinal entry/exit records. No improvement over R9 first volume-qualified precision in any month. Also left July out of fitting (120k source samples); July test remained negative.
- The larger attempted multiclass fits (180k/month 180trees and 72trees) hit compute ceiling and were terminated without a stored model. Their fits **do not count as training**. Freeze the bounded 30-tree model weights and tests.
- Original source exact audit and direct R9 research parent retained. Raw gzip ticks in PRIMARY Drive https://drive.google.com/drive/folders/1lSCfO_awUKkbR4I6xDTy9orjIl0SrgIV . Full original H1V2 dependencies at https://drive.google.com/file/d/14Zqs-PyZ70qr0NTvpJRxpT0XcVc8msUu/view . H1V2 R9 complete source under previous research recovery archive, included inside R10 complete kit.

Recovery: read `H1V2_R10_SOURCE_EXACT_VERIFICATION_20261102.md` and `results/H1V2_R10_FOURMONTH_EXPERIMENT_MATRIX_20261102.json`. Source sha manifests preserve original ticks, H1V2 30s labels, R8 ASOF and R10 grammar float16 matrices. The R10 grammar arrays (~1.4GB) and all original full label arrays (~1GB) are **not duplicated** in this compact recovery. Recreate separately per month from the verified raw sources and original teacher. Original H1V2 R9 fast simulator and MT5 files never modified.
