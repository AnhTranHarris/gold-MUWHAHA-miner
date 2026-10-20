# R00-054 FILTER09 — Predictive neutral/opposite specialists and lifecycle arbiter

**2026-10-19: COMPLETED/VERIFIED research continuation, NOT promoted to MT5 EA or live trading.**

## Exact parent and elected foundation

- Descends from `carson/htf-r00-054-filter08-four-month-overfit70-20261019` commit `6d1e268d88c0816f91f1eac66fc368b594200524`.
- R00-054 `lgb_oracle_weighted` initial BUY/SELL generator remains the elected *unchanged* high-throughput research foundation; source-native original event time and side immutable.
- Existing Python tick backtests, per-broker source readers, Coinexx UTC correction, original January-trained parent model, event label and all prior FILTER01–08 research unchanged.
- January-only N no-opportunity/neutral probability, O opposite-direction conditional non-neutral probability, with N/O/S/R/M separately timestamped ARM → CONFIRM → EXPIRE → COOLDOWN → REARM states.
- JAN first 75% chronological original labels fit secondary models; 40s purge before remaining JAN diagnostic. FEB only used to select/freeze one numeric veto rule per broker from 55 predeclared candidates. **NO June/July model refits or threshold selection.**
- June/July historic exposure from prior R00: **NOT BLIND**, not investor-accepted system, no fills/stops/holds/exits/P&L.

## February-frozen real-quote veto decisions

Coinexx: `cooperative_2_all_Q0.50`, risk threshold `0.45952622606605953`.
Dukascopy: `cooperative_2_all_Q0.80`, risk threshold `0.5398423228298446`.
Each veto requires calibrated risk and 2 of 5 separately confirmed specialist lifecycles.

| Historical broker-month | Original correct/emitted | Filtered correct/emitted | Original accuracy | Filter accuracy | New R9 hour/day failures |
|---|---:|---:|---:|---:|---:|
| Coinexx June | 142,224 / 312,004 | 126,950 / 276,110 | 45.5840% | 45.9781% | 0 / 0 |
| Coinexx July | 143,362 / 321,069 | 119,225 / 262,939 | 44.6506% | 45.3432% | 0 / 0 |
| Dukascopy June | 132,105 / 297,035 | 116,622 / 256,313 | 44.4746% | 45.4998% | 0 / 0 |
| Dukascopy July | 130,408 / 301,280 | 110,604 / 247,768 | 43.2847% | 44.6401% | 0 / 0 |
| TOTAL | **548,099 / 1,231,388** | **473,401 / 1,043,130** | **44.5107%** | **45.3827%** | **0 / 0** |

**Performance:** +0.8721 percentage points absolute accuracy on original event population; 113,560 incorrect signals rejected and **74,698 already-correct signals lost**. Neither 70% true transfer nor 80% target reached. Historical hourly/day reference quotas maintained for all eligible windows; no new misses relative to the original.

## Fixed-policy ablation and causal tests

- 44 transfer ablation rows: no lifecycle concurrence = 46.5539% apparent precision but **529 extra R9 hourly failures**; maintaining 2-vote independent lifecycle concurrence sacrifices some precision but protects the user-prescribed throughput.
- Drop N, R or M specialist state from selected rule: combined precision falls to ~45.10%, 44.95% and 44.97%, respectively. Correlation between specialists and prospective predictive effect remain unproven.
- Tests PASS: lifecycle prefix invariance, current/future outcome mutation cannot affect matured feedback before +32s, and exactly reproducing all four frozen per-event decisions from the stored policy/states.

## Original code/models/results immutable cloud locations (BOTH ACCOUNTS)

- PRIMARY [R00_054_FILTER09_PREDICTIVE_COOPERATIVE_RESEARCH_20261019.zip](https://drive.google.com/file/d/1GsmSkpGsCCGNULHG73sE_DBU-ofs_Z2u/view)
- MT5_EXPAND [matching research archive](https://drive.google.com/file/d/1GObsMQT9la3o6-L8J_G1KQScTOvjZa7T/view)
- ZIP **8,806,519 bytes**, original SHA-256 **`66eb1f1dce60dd3d9ee921272e9509025870eabb9640ff8635b49a31e8ba11c5`**. CRC/member hashes PASS, Drive uploads succeeded; both returned exact byte length. The locally read-back archive has matching SHA-256.
- Includes `run_filter09.py`, `ablate_frozen_cooperation.py`, `test_filter09_causality.py`, `finalize_preservation.py`, Jan trained N/O LightGBM model joblibs, source-only JAN thresholds, February grids and selections, all four original event-indexed June/July decision NPZ arrays, broker-month and all-interval scores, exact member SHA manifest, full detailed receipt, and raw terminal outputs. Raw tick gzips and original R00-054 cache files are **not duplicated**; refer to the previously verified full originals.

## Continuation contract

- Do **not** rebuild backtesting infrastructure, train on/filter using a candidate's current 30s label, optimize scores retrospectively using June/July outcomes, or overwrite the original R00-054 baseline.
- Test **new causal information** instead of another micro-threshold: source-native quote freshness transitions; right-confirmed completed M15/H1 pivots/sweep/reclaim/retest with publication-time ledger; independent session/regime/quote-activity life cycles; prospective context-aware neutral and opposite hazard specialists. Score full R9 hourly/day supply; original fixed 30..32s direction label and 5sec event clock remain unchanged.
- For any *genuinely blind future month*, require investor approval of a new authorized SHA-registered broker-native source; January–September 2026 have prior exposure. No real account trades are inferred.
- This compact GitHub receipt is navigation, **not** a substitute for full original four reports, cumulative governors v1.0–1.4, or the full source/models/results in cloud ZIP.
