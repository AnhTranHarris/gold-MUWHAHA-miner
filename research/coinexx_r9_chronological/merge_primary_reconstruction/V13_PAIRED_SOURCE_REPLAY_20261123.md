# V13 — Source-exact paired R9 lead-up / merged-primary reconstruction (2026-11-23)

**NOT approved for MT5 execution.** This is an iterative nine-month **heavy in-sample** research checkpoint. Original R9 v1.90 code and all historical merged trade records remain unchanged.

## Read the complete executable source — never work from this handoff alone

**COMPLETE SOURCE KIT (31 entries; 30 payload hashes verified):** [MT5_EXPAND: R9 V13 merged-primary paired source ZIP](https://drive.google.com/file/d/1D7JKZQ1qko4CqxM5X6DO9HfYoXAJS7vl/view). ZIP SHA-256 `9fcb9fe69797f4d10108eb410acec5ba2704c39998fa400736152f314ec97bda`, 57,476 bytes, no raw tick copies. Includes original frozen C++ R9 parent, source-diff-generating Python build scripts, instrumented paired replay, merged-source readback, self-directed profit-exit/reclaim and two-lifecycle C++ variants, the complete source-level documentation, nine-month comparison scorecards, scientific QA and source receipts.

Original R9 MQL5: [GoldMuwahahaMiner_R9_HybridGate.mq5](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/mt5-r9-hybrid-gate-certification/Experts/GoldMuwahahaMiner_R9_HybridGate.mq5), unchanged blob SHA `7eecb5f1947017a01ce85b2520725de54749e523`.

**Primary immutable historical trade ledger:** latest frozen January R9+Coinexx ZIP and Feb–Sep 244,372-row R9+Coinexx ZIP (272,352 original mapped bid/ask entry+exit ordinals, +$360,693.05 historical benchmark). These frozen quote locations are the reference and training evidence—not future live order instructions. Coinexx original nine monthly TickLogger gzip files are chronological quote-by-quote simulator inputs.

## Source-observed entry mismatch

Original R9 minute bracket satisfied at 44.47% of NEW merged mapped entries; S1 only 5.48%; full bracket/S1/M5-ATR/spread gate 3.73% of mapped entries. Same-direction **full gate occurred within the prior 30 seconds on 36.82%** of mapped entries. This supports a post-original-pulse opportunity-state hypothesis but is retrospective. S1 efficiency 0.70 typically absent at the mapped entry; median observed 0.319. R9's 98.43% position occupancy in the no-trailing/no-max-hold ablation is a mechanical consequence of no profit exit, not a general broker statistic.

Nine instrumented original R9 no-exit source ledgers are byte-for-byte identical to preserved baseline. Source-prefix: 3,885 mapped observer records and 114 closed original R9 positions match full-month source when January is truncated at 1.2M original quotes.

## Mechanisms tested, honest economics

At hindsight-**seeded** frozen merged entry ordinals, causal subsequent quote-first-passage TP150c / SL90c / 60s exits produce +$153,275.70 total, only ~42.5% of the known merged reference; **not autonomous entry performance**. At those mapped positions, second legs average ~+$1.068 under this exit, first legs ~+$0.353. Such statistics cannot directly be inferred for self-generated R9 entries.

**Actual autonomous R9 on-policy simulation** with added TP120c/SL60c/45s: 268,720 nine-month trades, -$62,775.40 fee-inclusive; R9 after event-qualified $0.25 pullback / $0.10 rebound: 180,445 trades, -$38,584.42. Both 0/9 frozen monthly profit targets and exhaust $100 simulated cash. Dedicated first-scout/rearm lifecycle and relaxed completed-S1 reversal rearm also fail January/February/July. No model promoted. The pullback mode passed a 2,813-trade source-prefix identity test.

## Next evidence-driven mechanism to **develop** (NOT completed)

Treat the initial R9 gate as **an observed setup precursor**, not necessarily an immediate order. Build two separate source-tick hazard/action-value specialists: first entry after 5–15s pullback/overshoot confirmation, and **actual executed** first-leg-to-opposite recovery with 1s/5s/15s confirmed candles, spread, quote-arrival duration proxy and actual first-leg excursion. Include explicit WAIT/HOLD/HARVEST action value and first-passage tail risk, no original future exit supplied to live inference. Source-bounded candidate generation and **full self-directed on-policy nine-month** account tests are required. No native MQL5 compilation or MT5 Strategy Tester validation has occurred.

**Rollback:** original HybridGate v1.90 branch unchanged; this checkpoint is research documentation only. Read executable ZIP, forensic receipts and frozen primary source files before any continuation.
