# R02 — High-Velocity Native-Tick Mechanism Discovery (16 Oct 2026)

**Status: RESEARCH_IN_PROGRESS / NO CANDIDATE PROMOTED.**

This continues, without rebasing or modifying, the project's v1.3/QC lineage and the R01 arbiter branch at parent `fb372a0288d717b01042faa6be84c4e40c7a41f0`. The pinned R9 code remains READ-ONLY. Preserve the original investigator's constructive research mission and mandatory full-account investor scoring.

## Original executable research/evidence — permanent MT5_EXPAND archive

- [Full R02 original Python source, 64 original-tick trade ledgers, source manifests and param sweeps](https://drive.google.com/file/d/1N46YgcqWl2OpN0Vnqcn6GOQ4VmxSZx_R/view)
- [R02 research folder](https://drive.google.com/drive/folders/1lpLVj-Q0Ge49GTMFZkKkTh32jjhYhrq1)
- Archive exact 902,309 bytes, SHA256 `05ac4819e993c1ea07a11faf94af8848459706c9e0baefbc9f9bf6cdd0e386ba`; independently downloaded after upload, rehashed and CRC validated.
- This is a reproducible **original code/evidence archive**, not a new market-data source. The four immutable bid/ask tick tapes remain in PRIMARY Drive; all source hashes are in archive's `SHA256_MEMBER_MANIFEST.json`. Source provenance is Coinexx Jan/Feb UTC-corrected minus 120 minutes and native UTC Dukascopy Jan/Feb.
- Run `restore_and_validate.py` in this folder against the downloaded archive to check byte integrity and execute the synthetic-quote causal test fixture. Reproducing all original-tick experiments additionally requires the separately approved original market-data files in `/mnt/data`, with exact source SHA256, plus NumPy, pandas, Numba, and optional LightGBM.

## What was implemented, not hypothetical

Original R9 source was re-read at pinned commit `8729a6345655a7b4ea31facc81982004ee2b8921`. Research scripts independently implement completed-second quality, minute-reset bracket selection, opposite-side rearm, strict next-quote fills, actual recorded original-tick bid/ask, tick-level trailing stops, latency, account margin and mark-to-market DD. Specialized candidate modules in research test Fibonacci 60s structural zones, ATR regimes, rapid Wilder RSI, rolling quote-event-weighted anchored price (QWAP, NOT traded VWAP), quote pulse and causal session context.

- Four immutable broker-month tapes freshly hashed: 31,475,493 original quote events.
- Exact derived second histories are reproducible; empty seconds never fabricated.
- 1,080 seconds-scale geometry/indicator variants.
- 1,344 stop/target/trailing lifecycle trials (one-second screening).
- 288 cautious passive trade-through entry trials (screening, queue fills not certified).
- 1,400 minute-bracket / rearm architecture trials.
- 280 original recorded-tick candidate variants on January Coinexx, plus 64 original-tick twin-broker Jan/Feb $100/$200 scenario ledgers.
- Supervised LightGBM Jan2–12 direction research evaluated Jan13–30 and February without refit, with 24 causal features.
- A **separate** $10,000 hypothetical-capital capacity experiment found 375/1,400 bracket settings exceeding 710 completed trades per calendar day; maximum 19,758 completed trades over Jan2–12 inclusive (~1,796/day). This is a trade-generation-capacity diagnostic only; **ALL these high-throughput capacity arms were after-cost negative** and the $100/$200 cases are NOT investable or certified. Do not promote the highest-volume arm merely because it meets velocity.

## Validity and repair ledger

Fee reporting bug discovered in earliest R02 screening: entry-side commission was charged to balance but inadvertently absent from some exported *per-trade net* fields. Affected initial R02 reports are **SUPERSEDED_NOT_ACCEPTED**. Fixed simulator source and regenerated seconds-lifecycle, passive, minute-bracket and capacity receipts before archiving. Native recorded-tick 280-screen and 64 validation ledgers use both-side fees and reconcile net to balance for fully closed test scenarios. The included `test_native_contract.py` passes a fixture establishing no same-tick fills and two-sided commission reconciliation. This does not prove matching MT5 live trade execution or approved real broker rules.

No tested high-velocity implementation passes the complete survival/positive-net/investor-target set. R9 SYNTH outcomes remain a historically synthetic performance comparator; there is no guarantee that any permitted configuration attains the aspiration. Tiny positive results with one or two trades are not successes.

## Next constructive engineering action — DO NOT RESTART AUDITS

1. Preserve the original-authorized risk-source rules, R9 historical code and existing shared-account signal bus; wire **five causal specialists** as distinct conditional engines (trend impulse, fib liquidity-sweep/reclaim, ATR compression-expansion, RSI kinetic turning/rearm and QWAP acceptance/reversion). Use session/ATR/quote activity to select specialists, not one universal indicator AND gate.
2. Optimize **full entry→fill→trail→exit→rearm lifecycle and broker-specific cost headroom**, not slow M1 close-to-close entries. Use actual tick quotes, independent broker fills/fee profiles, and protect a common account.
3. Select candidates on a Pareto frontier of account survival, after-cost net, gross loss, drawdown, accuracy, PF and 710–2,127/day activity. Low-activity stop-outs and tiny one-trade positives are not candidate winners. Freeze experiment IDs and preserve ALL sweeps, day/week/hour/session results in Drive. No train-on-holdout or repeated result cherry-picking.
4. Cross-month January→February→March and forward, same causal calendar-blind router, 12 broker/balance/latency scenarios and immutable ledgers. No MQL5 port or trading release without owner authorization.

All new research remains on this isolated branch; prior validated engine and R9 reference untouched.
