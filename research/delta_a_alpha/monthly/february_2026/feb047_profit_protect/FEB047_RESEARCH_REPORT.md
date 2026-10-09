# FEB047 — Timeout recovery, causal winning-cohort reductions, strict rate checks

**Status:** Completed February **in-sample frozen-accepted-source-ledger** diagnostics. Not a complete owner-V1 economic backtest, not a full native L6 repair engine, not blind, and **not an MT5 or Coinexx certification**. The full original 14,232-character eight-stage L0–L7 owner whitepaper remains unchanged.

## Recovered predecessor (FEB046)
The 2026-10-09 timed-out session had already generated `/mnt/data/FEB046_COMBINED_PORTFOLIO_RECOVERY_RESEARCH.zip` and GitHub journal `0064`. The verified archive includes 70 completed FEB046 evaluations, including actual-funded-close loss recovery, pre-close M5/H1 correction entries, funded-source relocks, structural exits, and L7 equity-entry guards. No FEB046 variant passed the actual full-quote equity-DD <$10k constraint. In particular source-to-source hedge entries after loss were late and negative; entry-event-only DD was optimistic.

## New FEB047 portfolio-repair hypothesis
The main floating-equity DD cohorts are often profitable S22/S25 campaigns. Our causal counterfactual therefore (i) samples actual observed Bid/Ask quotes every five seconds (no artificial fill); (ii) assesses a rolling 60–180 second sampled-price high/low and already-funded directional inventory and equity pressure; (iii) upon an observed unfavorable price retreat, schedules reduce-only exits of existing **profitable** fixed 0.01-lot S22/S25 positions, only when their current executable quote exceeds a minimum earned P/L; (iv) restricts supplementary closes to one per quote and audits original accepted entries plus reduction closes against 10 total orders/UTC second; (v) recomputes all-quote equity/DD independently after modified exits. This is a test of combined L3 cohort management plus L7 capacity; it does not substitute for the original L6 specialist.

## Independently reconciled selected research frontiers
| Scenario | Net | Gross loss | PF | Trades | Exact quote equity DD | Combined max orders/sec | Early reductions |
|---|---:|---:|---:|---:|---:|---:|---:|
| FEB045 profit baseline | +206,528.58 | -7,616.38 | 28.12 | 25,443 | 19,308.09 | 10 original admissions/s | 0 |
| FEB045 prevention baseline | +200,982.52 | -8,721.15 | 24.05 | 25,313 | 16,458.45 | 10 original admissions/s | 0 |
| FEB047 profit cushion | **+206,303.05** | **-7,615.39** | **28.09** | **25,443** | **17,183.83** | **10** | 361 |
| FEB047 balanced-quality | **+201,230.31** | **-7,615.39** | **27.42** | **25,443** | **16,215.59** | **10** | 1,586 |
| FEB047 lower DD | **+200,329.84** | **-8,721.15** | **23.97** | **25,313** | **15,741.94** | **10** | 224 |

Independent quote-side audit: `FEB047_INDEPENDENT_QA.json`; both raw month compressed tick hashes reverified. Monthly profit and trade velocity remain above owner floors; **$10k exact DD not achieved**. Profits are model-specific; e.g., for +$200,329 on 25,313 trades, +$0.10 incremental roundtrip friction would take net below $200,000.

## How the incomplete screen was resumed
The first FEB047 aggressive profitable-exit sweep (24) was rerun after fixing a numerical intermediate DD error caused by int32 multiplication in a vectorized checker. The corrected baseline reconciles **$19,308.087** full-quote DD. A 96-case gentler screen was interrupted after 49 records, resumed from its JSON, and completed. We completed additional 192 original reversal scenarios, 216 focused configurations, 144 combined-rate-queued variants, 24 independent lower-DD baseline transfers, plus 40 explicit combined-order-rate tests; **736 total recorded evaluations including repeats and tests**.

**Critical rejected-model evidence:** Some initial reduction schedules attempted up to 48 same-quote closes. A revised queue limited its own closes, but post-hoc audit found up to **14 combined entries-plus-exits in a UTC second** in one aggressive case. Those failing cases are **rejected**, not breakthrough candidates. Of the 40 leading queued scenarios explicitly re-audited, 25 passed combined <=10/s and 15 failed. The three selected cases above passed this stronger test, including independent executable-side P/L and one new reduction per observed quote. The stronger test still does *not* solve actual broker orders or original future child genealogy.

## Why no ultra-breakthrough claim
The best exact DD remains **$15,741.94**, not <$10,000, on an already February-fitted model. Peak open stays **1,536 positions** (0.01 lot per position). Position liquidation may occur on different broker quotes or be rejected; more importantly, the fixed FEB045 source proposal tape cannot regenerate future Watchdog/structure activity after realized exits change. The needed economic engine is the owner-authorized full V1 L0–L7 funded genealogy + quote-level L7 portfolio governor (gate 033). A monthly-fitted source screen is **not** evidence of deployable or adaptive profitability.

## Research alternatives and future testing
- Select between a **profit-preserving** and **DD-preserving** regime only using entry-time causal structural context across earlier months; do not hard-code February or dates.
- Model *earned campaign profit harvesting before deterioration*, not a forced loss-closing stop, as a participating L3/L7 risk repair.
- Reconstruct full original L4 Watchdog funded child reward/relock, native L5 continuation/pullback, and separately permissioned L6 recovery; do not treat generic flip or late hedge as native L6.
- Replay JAN039 unchanged and FEB045/FEB047 research recipes through the same endogenous funded engine, then compare monthly and cumulative results; reserve August and September for their existing holdout rules.
- Stress-test +$0.10/0.20 costs, broker latency and execution rate, realistic margin and 0.01-lot small capital capacity. No changing lot size after losses, no DCA or Martingale.

## Public mechanism inspirations (concepts, not validation)
- English MQL5 finite risk grid: https://www.mql5.com/en/articles/21833
- Chinese MQL5 equity-guard concept: https://www.mql5.com/zh/articles/18918
- Japanese MQL5 floating DD monitoring: https://www.mql5.com/ja/articles/2704
- Chinese grid staged exits: https://www.mql5.com/zh/articles/10671
- Japanese portfolio-risk awareness: https://www.mql5.com/ja/articles/16604

## Reproduction
Python3 with numpy,numba, source packages. All scripts in ZIP; raw canonical Jan/Feb `.csv.gz` and FEB045 source proposals are intentionally referenced by manifest, **not duplicated**. `python independent_check_047.py` performs all-quote independent QA on the preserved final candidate ledgers; `python audit_queued_candidates_047.py` validates the combined order-stream constraint. Run from identical verified data files; do not replace original upstream source candidates with synthetic trades. `FEB047_FINAL_QA.json` stores performance and blockers.