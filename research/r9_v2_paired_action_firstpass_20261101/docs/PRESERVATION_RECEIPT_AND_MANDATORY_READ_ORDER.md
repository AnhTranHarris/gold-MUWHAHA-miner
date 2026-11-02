# Research continuation preservation receipt — 2026-11-01

## Source truth and exact lineage
Additive child of `carson/r9-v2-hindsight-teacher-eight-source-training-20261101`.
The baseline R9 v2 branch and all prior eight-month source files remain unchanged.

New causal same-event BUY/SELL first-passage dataset: 2,481,012 entry timestamps,
4,962,024 two-sided quote-path counterfactual outcomes. Original direction
lifecycle replay matches exactly (exit millisecond and net) for all 2,481,012.
Every input source-month SHA-256 and output dataset SHA-256 is in the exact
`results/*_paired_receipt.json` and `results/*_features_receipt.json` files.
Complete research code, fitted model weights, run receipts, calibration choices,
102 runtime feature definitions and tests are also preserved in this branch.
All original binaries are stored as eight separate ZIP checkpoints, each with
an individual full SHA256 manifest; machine-readable metadata is in
`results/RECOVERY_INDEX.json`.

## Required read order — use original sources, never a summary
1. Read original full design contract
   https://docs.google.com/document/d/1vJPgj_nWadWVALQC0UWB68evqSkKuKwz7KIF_LhXqkA/edit
2. Read original full eight-source teacher training record
   https://docs.google.com/document/d/10W8PTGCXAi1wRPoIP44_1OwEozH97h0ouL2ejsXxrv8/edit
3. Read original full ordered first-pass teacher training record
   https://docs.google.com/document/d/1moZNDhkf-oBjYBzh6dEHQiGMbq-FAh52jke7TcmJmoM/edit
4. Read THIS full native research log
   https://docs.google.com/document/d/1qeI5ZTk5La3lj1Ncf_6dhDHTFDqLUi1LnilH3oV0Tr0/edit
5. Verify exact source code, model weights, checkpoint receipt hashes, and raw
   paired actions — do not interpret prose as a substitute for complete data.

## Persistence state
Native Google Doc log is in main Drive research folder.
One full binary checkpoint, Dukascopy July, verified uploaded:
https://drive.google.com/file/d/18XwKobDws6flejx48xMcoI4Udn-u8QT2/view
All eight complete source-month binaries (720 MB total) in persistent personal
Library `/XAUUSD_V2_PAIRED_ACTION/` with the complete `RECOVERY_INDEX.json`.
**The remaining seven binaries are NOT YET mirrored to Google Drive**; do not
misstate this. The previous source tick baselines are already on Google Drive.

## Scientific acceptance
All eight new chronological student fits unapproved.
No source/month meets calibration >=80% strict favorable-first and positive P&L.
Same-baseline-entry off-policy check is not a new on-policy high-volume run.
Never promote a parameter set or call an oracle feasible live.
The next scientific research build must learn BUY/SELL/WAIT/DELAY timing at ALL
eligible 250ms events, freeze thresholds chronologically, then retest actual
non-overlapping executions with 85% R9 SYNTH volume and 80% daily/weekly/monthly
strict first-30s survival on BOTH sources.
