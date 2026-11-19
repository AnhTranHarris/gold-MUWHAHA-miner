# January AR1 R6 integrated account-risk research release

**No trade filter, altered order, historical trade removal, shadow booked-P&L or EA deployment.**

This small release depends on *unchanged* January R1 source manifest and R5 strict-entry predictors, which are pinned in the main report. The original 21 `R9_REAL_2026-01-*_ticks.csv.gz` Coinexx original source files remain outside this archive. No raw ticks are duplicated.

Run in the established research environment (Python3, numpy, pandas, sklearn):

```
python test_integrated_runtime_contract.py
python integrated_january_ar1_policy_stress.py
python proxy_missing_and_gap_stress.py
python stress_qc_and_atlas_acceptance.py
```

For the research workspace used to create this release, the scripts refer to `/mnt/data` and read earlier R1/R5 artifacts in place. Reproduce using the same pinned source files and current scripts; they do **not** download raw ticks or invent missing observations. `stress_qc_and_atlas_acceptance.py` checks source, protected families, profit collision, full cohort and Atlas integrity. `JAN_R6_INTEGRATED_ACCEPTANCE_SCORECARD.json` is the machine-readable test status; the human report lists limits and failed tests.
