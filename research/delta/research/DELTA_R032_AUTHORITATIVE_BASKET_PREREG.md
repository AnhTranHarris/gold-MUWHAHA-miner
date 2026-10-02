# DELTA R032 — Authoritative DH05 Additive Basket Preregistration

**Status:** PREREGISTERED / NOT EXECUTED  
**Parent:** R025 ownership + GLOBAL NO_REARM + independent specialist events  
**Script SHA-256:** `2058181259c37a623bc3d49a135772c12122b2138a5120f056d58ce7a9cffee3`

## QC correction
R030 and R031 were invalidated because the helper used there generated only 100 DH05-S06 signals.
The authoritative generator in `r013_selective_handoff.py` produces 672 DH05-S06 signals and exactly reproduces the frozen standalone ledger: 615 trades, 307 wins, net -$101.08, max balance DD $101.51.
R032 uses only that parity-confirmed signal stream.

## Frozen configurations
- C00: DH03-S06 + authoritative DH05-S06
- C01: C00 + DH02-S11
- C02: C00 + DH02-S08
- C03: C00 + DH02-S11 + DH02-S08
- C04: C00 + DH02-A01

## Modeled surfaces and gates
P50, P75, P90 are all required.
Every surface must have trade retention >=80%, winner retention >=80%, net better than ordinary opposite-rearm control, and gross-loss/DD deterioration less than 5%.
No new R032 configuration may be invented after results.
No post-exit same-minute reentry grammar is permitted.

Workbook tabs: `60 R032 Prereg`, `61 R032 Results`.
