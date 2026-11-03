# R15 — H1V2 60-second observed-quote waiting experiment

**Classification:** Research-only, future-privileged hindsight; **not approved for MT5 live, paper, demo or user-account execution**. This project preserves historical H1V2, R9v2 and R11–R14 source verbatim. It intentionally adds code and creates no changes to the EA.

## Source-exact chain

- H1V2 teacher: `edce573d9c53b743dc5de1b0d741c81370af52c1`
- Repaired runtime R9 v2: `ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0`
- R13 source: `8d2e5524edd6f52f43503e30060285d909855925`
- R14 source parent: `743bc5768fd39e34a7d2ea8d1528318c50692f8e`
- Canonical original unsummarized forensic audit: https://docs.google.com/document/d/1n8Zd37SH3k2mNYpCERHsGSeR5GL-vDNLDv780Bv5-Do/edit
- Source progress ledger: https://docs.google.com/document/d/1iVv1tAmJlBWhNfXMcw2N50VEVIFrawMObGOzyfUGWmI/edit
- MT5_EXPAND canonical research folder: https://drive.google.com/drive/folders/1vpHz_U-eVFyiC4Tf6YLgFlCK3HN3vP7L

## Source runner

`PYTHONPATH=src python src/r15_asof_watch60.py` on Python 3.13 with numpy/pandas/numba, using exact raw quote gzip and unchanged source R13 and R11S1 helper at the pinned local dependency paths described in source. The script aborts on source SHA mismatch. Exact initial real-tick tester / synthetic Strategy Tester / Dukascopy source SHA pins are embedded in `R13_EXPECTED`. **Do not** infer live Coinexx executions or Dukascopy trading fills from tester/vendor quotations. This revision tests only 2026-02-02 06:00–07:00 UTC, not all January/February/June/July.

`python -m pytest -q tests/test_r15_asof_watch60.py`

`python verify_r15_source_exact.py`

`python build_complete_r15_report.py`

Independent original source quote ordinal, both price sides, strict15/full30 labels, original and expanded horizons, calendar quota, strict one-position interval scheduling, latency-scenario outcome parity and original R13 base/widened control counts are verified. Failed initial execution F01 and repair are preserved in logs. The full no-truncation 282KB report contains 84 source-hour, 336 source-quarter, 189 stress-hour and 756 stress-quarter original CSV rows, and **the entire original 85KB source forensic audit as Appendix A**. All 37,038 original selected quote ordinal rows, 189 full scenario NPZs and the three full candidate membership and future-outcome NPZs remain in source exact ZIP (no truncation).

Original research historical acceptance remains >=85% R9 SYNTH monthly trade count, >=80% strict first15/safe30 correctness on each active day/week/month, positive full economic account net and bounded drawdown. R15 neither demonstrates causal prediction nor full portfolio outcomes and cannot be promoted. The longer 60s initial window has two disjoint semantics: **as-of pre-entry observation** versus **future favorable/60s adverse surveillance**. It never reclassifies later favorable as original 15-second success.

## Restart

Read all complete original material and the full progress document, verify SHA of whole R15 archive and each member manifest, rerun tests, inspect this version's failure log and complete receipt, check isolated GitHub branch ancestry against R14 source anchor. If a new extension fails, return to this exact pinned source and create a new additive branch/experiment; do not alter original results. Follow-on multi-hour HTF context/causal training and full source month transfer are OPEN, not implied complete.
