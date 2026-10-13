# GRID0257 — R9-overfit-guided earned H4 slots, exact-tick 7-month positive research portfolio

**Governing owner formulation:** "r9 syth as perfomance goals, r9 overfit shows optimal trades, each month's market conditions are mostly unique, the grid trading strategy trading edge is a high trading volume trading bot, the grid trading strategy is a near multi-HTF, the grid trading strategy is a near multi-scalping trading bot, the grid trading strategy is a near sniper trading bot."

**Status:** historical, repeatedly inspected **research-only** incremental improvement; NOT positive in all 31 benchmark weeks; NOT Coinexx funded cash or R9 net/trade volume equivalence; no trading authorization. Scientific J0183 remains disabled. August remains sealed. Same `delta-A-alpha` branch; no extra branches, scheduled tasks, or Vertical L1-L7 changes.

## Causal mechanism, NOT lookahead or a martingale

Preserve the entire previously accepted GRID0256 (1,156 positions). Recover original H4 sniper 4-source-slot offers that were originally denied by the baseline 2-slot H4 sniper. An extra fixed **one-ounce** position may be admitted only if (a) original as-of completed-H4 + second consecutive completed M1 source is genuine, (b) both original H4 base positions are already open, (c) the previous **five ACTUALLY SETTLED base H4 sniper tickets** have a **positive sum of net after-friction quote PnL**, (d) at most four H4 positions and 16 global positions remain, and (e) a genuine next observed quote is timely. Extra tickets cannot earn further funding credit, and no positions/lots are added because of a loss. History of July, target week, month number and retrospective OVERFIT scores never enter the rule.

Source permissions: [v1_grid_earned_h4_extension_0257.py](../implementation/v1_grid_earned_h4_extension_0257.py); [11 unit tests](../implementation/test_v1_grid_earned_h4_extension_0257.py); the cumulative G0 router exposes this as an **optional research-only permission**, never automatically issues orders. This preserves original S1/M1/M5, H4 breaker, H4 retest, H4 two-minute sniper and J179F T1/T2 semantics. The original J179F T1 generator still requires recovery before a truly autonomous source-engine backtest.

## Full 57,527,562 original Jan-Jul Bid/Ask quotes, one chronological research book

| Metric | GRID0256 reference | GRID0257 earned H4 permission |
|---|---:|---:|
| Closed, independently funded *quote-model* positions | 1,156 | **1,163** |
| Net, USD per one-ounce quote model after $0.52 per ticket | +$6,539.081 | **+$6,786.350** |
| Delta | — | **+$247.269 (+3.78%)** |
| Original additional source invitations admitted | — | **7 out of 16**, IDs 14,15,40,56,63,74,124 |
| Positive Jan-Jul months | 7/7 | **7/7** |
| Positive represented ISO weeks | 23/31 | **23/31** |
| Gross loss, same quote model | −$9,367.447 | **−$9,654.011**, worsened |
| Full-tick marked DD, same quote model | $1,205.295 | **$1,205.295**, unchanged |
| Max concurrent actual model positions / cap | 16/16 | **16/16** |
| Exact observed opposing Bid/Ask quote mismatch / source capacity breach | 0 / 0 | **0 / 0** |

**Monthly exact-quote PnL**: January +$1,940.184/66 closes; February **+$12.292**/53; March +$1,865.484/67; April +$801.697/202; May +$978.760/233; June +$1,134.389/270; July **+$53.544**/272. Both February and July have little execution-cost cushion. No weekly-profit category or broker-loss/DD category is locked. The **1,163** completed research closes remain only ~0.53% of R9 SYNTH's 219,342 historical completed tester deals; source USD/oz and R9 account-cash dollars are not comparable.

## Exact provenance, evidence and replication

Re-use original immutable [GRID0256 preserved 12-slot J179F research](./GRID_0256_ORIGINAL_J179F_MULTI_HTF_SOURCE_CAP12_SHARED_BOOK_SUCCESS.md), its 1,156 original source-ticket close ledger, the original GRID0255 H4 2- and 4-slot exact-ticket outputs, the pre-existing GRID0252 `load_month` and `book_chunk` helpers. **No input tick archive or previously working mechanism was overwritten.**

The research ZIP created in this conversation, `GRID0257_EARNED_MULTI_HTF_CAUSAL_SHARED_BOOK_20261012.zip`, contains:
- `grid0257_earned_h4_child_research.py`: five separately prespecified source eligibility arms and its internal unpromoted journal.
- `grid0257_earned_h4_parity_replay.py` / `GRID0257_EARNED_H4_SOURCE_PARITY.json`: fresh invocation of the actual `v1_grid_earned_h4_extension_0257.py` module against ordered *truly closed* base tickets selects exactly **7 of 16** original extra source invitations.
- `grid0257_earned_h4_original_tick_reconciliation.py` and `GRID0257_EARNED_H4_SHARED_EXACT_TICK_PORTFOLIO.json`: full 57,527,562 original ticks in one 16-position marked-to-market account-quote book; all **1,163** settlements precisely match the original source quote Bid/Ask and modeled $0.52 friction.
- `v1_grid_earned_h4_extension_0257.py`, corresponding exact tested source and regression tests; staged source/router suite **118/118 locally passing tests**. The tested new source Git blob SHA is `3b4ad98983cd77dcb5559f29d5e1cbee0dd667d7`.
- Several ML walk-forward and as-of gating **internal** ablation records. Those unpromoted hypotheses do not establish an independently profitable high-frequency sleeve.

**Scientific reading:** R9 SYNTH sets the performance and trade-cycle targets; R9 OVERFIT only supplies hindsight-optimal research labels; offline trade simulations use only original ordered Bid/Ask quotes and as-of structural/previously settled state. Previous positive HTF specialists are preserved. The new improvement is **small and retrospective**, not an all-month/week solution. Continue researching genuine near-multiscalping source/cycle selection until 31/31 weeks, much higher truly profitable trade throughput and broker-realistic funding are demonstrated before any Vertical Grid promotion.
