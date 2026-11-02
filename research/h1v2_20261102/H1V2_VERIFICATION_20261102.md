# H1V2 four-month source-exact verification — 2026-11-02

## Source lineage

- Parent repaired branch: `carson/r9-v2-source-audit-repairs-independent-20261102`; SHA `997dfdbd06157faa426c143874ad84277971570e`.
- New branch: `carson/h1v2-fourmonth-hindsight-teacher-20261102`.
- Read complete source audit `R9_V2_ENTRY_ASYMMETRY_SOURCE_AUDIT_20261102.md` and repaired source, not research summaries.
- All four raw Dukascopy monthly gzip archives fetched from PRIMARY Drive folder `1lSCfO_awUKkbR4I6xDTy9orjIl0SrgIV`, independently SHA-256 checked against archival 60-second source pins. No synthetic OHLC generated.
- The original R9 `ActivePath` was not altered. Python R9 quote-ordinal replay: **1,916 sampled BUY/SELL lifecycles** across four months reconciled exactly on exit quote ordinal and realized net, 0 mismatches. Parity checks used original archived source files, not new approximated exits.
- The repaired original 99-dimensional ordered-quote geometry matched a separate independent high-performance raw-tick kernel on 8 real quote-state snapshots per month (32/32), including 250/500/1000ms, 5/15/30/45/60/300-second intervals.
- Unit tests: **10 passed**; dynamic-program scheduling compared with exhaustive brute force for 40 toy cases; future at equal millisecond excluded via tick-ordinal prefix; future last-tick-of-slot selection expressly prohibited.

## H1V2 strict hindsight labels and count target

Independent BUY / SELL at the first actually observed quote in each 250ms slot after 300-second warmup and <=$1.50 source spread. Original R9 stop/trail/30s exit, inclusive $0.02 simulated flat fee. A correct label needs **first executable +$0.10 net** before -$0.10 adverse change of the opening liquidation quote, favorable event within 30s, and final original-R9 exit net >0 inside 30s. Gap-forced later closes do not qualify. Future labels are teacher-only. All 513,262 selected intervals are nonoverlapping in quote ordinal and priced with independent original BUY or SELL quote sides.

| Dukascopy month | Raw quotes | 250ms candidate quotes | One side strictly good (overlapping candidates) | Hindsight optimal nonoverlapping wins | R9 SYNTH reference | 80% SYNTH monthly floor |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Jan | 9,135,062 | 4,025,968 | 1,072,358 | 137,402 | 27,980 | 22,384 |
| Feb | 7,538,339 | 3,112,593 | 894,468 | 125,472 | 33,523 | 26,819 |
| Jun | 8,201,406 | 4,190,620 | 1,183,511 | 149,273 | 31,801 | 25,441 |
| Jul | 7,415,841 | 4,072,211 | 883,570 | 101,115 | 24,382 | 19,506 |
| **Total** | **32,290,648** | **15,401,392** | **4,033,907** | **513,262** | **117,686** | **94,150** |

**No prospective entry accuracy is established by this result.** The dynamic program uses the future outcome of *both* candidate directions. Every oracle-selected winner is correct by construction, so quoting oracle accuracy as a 100% predicted win rate is prohibited. Model cost/slippage assumptions are optimistic. The modeled sum of oracle net outcomes is NOT a trading profit, portfolio backtest, live ledger, account survival or execution claim. Source feed is Dukascopy (not Coinexx, whose matching raw monthly ticks are not presently mounted); the R9 SYNTH count is an external volume comparator, not an equal-broker outcome.

## Geometry discriminability stress test

- **60,000 uniformly selected candidate quote timestamps** across the four months have raw-ordered 99-dimensional geometry + spread. Hindsight label classes are `[NO_GOOD, BUY_GOOD, SELL_GOOD]`; features never contain future outcomes.
- 3-class LightGBM trained only January/February. June-only frozen admission cutoff calibration; July held untouched. Compare 100-feature ordered subminute model with 12-feature five-minute-only control using identical 70-round fixed hyperparameters.
- The all-subminute model June top-5% strict directional precision **19.73%** versus slow control **16.53%**. July top-5% **13.73%** versus slow **13.07%**; top-1% July **11.33%** versus slow **17.33%**. Geometry adds context but does not reliably select direction with 80% correctness.
- For both models, no June calibration threshold met the 95% Wilson interval lower bound of ≥80% strict directionally correct admissions with at least 150 selected calibration rows; frozen July selections **zero**.
- This is a separate sampled learner probe, **not** a trained/approved foresight trading strategy. It does not measure full month on-policy fills or turnover.

## Portable recovery

1. Exact source modules and tests under `src/` and `tests/` and original repair lineage ZIPs.
2. Four complete report receipts, full exhaustive label-array SHA-256 hashes; rebuild the large label arrays in ~15s/month from pinned original raw ticks and these source scripts.
3. Four compact `selected_exact_trace.npz` archives containing all 513,262 hypothetical oracle entry/exit tick indices, UTC timestamps, bid/ask quotes, first favorable elapsed times, side and modeled net. These are **actual stored datasets**, not summary claims.
4. Four 15,000-row raw-as-of geometry atlases, two fitted fixed LightGBM comparison models and July untouched diagnostic.
5. Full raw source archives are NOT copied into the recovery ZIP to avoid 240MB redundant storage; source links and exact hashes resolve them.

**Promotion status: NONE.** H1V2 is an offline target-bound teacher. The next legitimate work is deeper session/regime-dependent causal signal discovery and a strictly chronological, source-exact on-policy 250ms replay of a frozen entry policy; do not replace these negative predictive results with oracle selection statistics.
