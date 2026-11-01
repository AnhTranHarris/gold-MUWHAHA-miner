### Model assumptions and deployment safeguards

**Research scope:** replace R9 entry selection only. Keep R9 exits unchanged to permit controlled attribution.
**Data clocks:** observed quote tick, 250ms, 500ms, 1s, 5s, 15s, 30s and 45s; bars are completed and non-interpolated.
**Causality:** future tick/millisecond values never enter the current decision; completed clock rings reset after 15 seconds without ticks.
**Teacher:** R9 synthetic entries are a weak, potentially biased supervisory signal. This build does not fit or use them yet.
**Bayesian:** five-bin 11-feature log likelihood ratio, Dirichlet shrinkage, tempered correlated evidence; score is not calibrated probability.
**NP:** negative-class held-out order statistic, alpha=0.15, delta=0.05 design controls; no live statistical guarantee under dependent clustered ticks.
**Hawkes:** two directional quote event intensities with exponential decays and stable fixed priors; coefficients not estimated yet.
**VWAP substitute:** quote-update-weighted mean only. True volume VWAP unavailable for spot gold CFD quote data.
**MT5:** actual order path requires explicit disabled-by-default flags and a separate validated frozen policy. MQL5 compilation and cross-language parity pending.
**Known risk:** inherited R9 SL/trailing/timeout and no-tick gap behavior remain unchanged and must not be treated as deployment-safe.

See research/r9_subminute_bnp_hawkes_v1/entry_model.py and Experts/GM_BNP_HawkesEntry.mqh.