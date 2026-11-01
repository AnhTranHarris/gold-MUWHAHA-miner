# BNP-Hawkes v1 frozen policy contract

The MQL5 include reads a comma-delimited file through FILE_COMMON. No policy is shipped.

Required rows: version,r9_bnp_hawkes_entry_v1_20261101; prior,<number>; threshold,<number>; real_validated,1; then 55 rows w0000 through w1004. Feature index is 00–10 and 5-level bin index is 00–04.

Approval rule: prior + 0.25 * sum(weight[feature][bin]) > threshold.

A frozen negative-class Neyman–Pearson calibration threshold and a separate real-tick validation sign-off are mandatory. Synthetic-teacher-only fitted models must not be permitted to authorize trades. Posterior score is NOT a calibrated trade-win probability.

The EA defaults to InpBNPShadowOnly=true and InpBNPAllowOrders=false. No policy is attached. All production evaluation requires exact feature parity and compilation in MetaEditor before enabling orders.
