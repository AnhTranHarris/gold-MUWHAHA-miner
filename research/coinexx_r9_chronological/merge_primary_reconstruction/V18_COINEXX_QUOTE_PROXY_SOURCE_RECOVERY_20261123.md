# R9 HybridGate V18 — source-exact Coinexx-only advanced quote-process proxies (2026-11-23)

**STATUS: ENTRY-ONLY RESEARCH — NOT APPROVED FOR MT5 TRADING. V17B REMAINS THE LEADING CONTROL.**

## Mandatory reading order: ORIGINAL SOURCES FIRST, not this summary

**[Complete V18 corrected executable C++17/Python + MQL5 research-source kit in MT5_EXPAND](https://drive.google.com/file/d/12R7l0JbKPJhbQwSufRJSH5iE0vF1jifJ/view)**. ZIP SHA-256 **`d6ae5f159fc2703c69e1ccbe5e6033e281bdb04a5cadf1fc3606f2a3c5b8d2d0`**; 6,532,858 bytes; **56 members, all 55 source/receipt/ledger payload hashes and ZIP CRC verified**. Compiled exact archived C++ and re-ran first 1.2M Jan source quotes: **252,673 source-second observations, gzip output SHA-256 `569701cd138233d7b24669014f7f8b6f51c7bfacb8b270c7b57f69a0c4dbc355`**, exact earlier output reproduction.

Read in the ZIP: `V18/SOURCE_EXACT_CONTINUATION_V18.md`, `V18/quote_proxy_v18.hpp`, `V18/v18_proxy_second_candidates.cpp`, `V18/sample_v18_fast.cpp`, `V18/fit_proxy_ablation.py`, `V18/replay_v18_source_only.py`, `V18/grade_v18_frozen.py`, `V18/proxy_side_override.py`, model coefficients, 18 source-only frozen 9-month signal ledgers, numerical nine-month scorecards, full original V17/V16/V14 C++ dependency chain, original source fingerprint pins, and **research-only uncompiled** MQL5 proxy observer `V18/R9_QuoteProcessProxy_V18_Research.mqh` / QA script `V18/R9_QuoteProxyAudit_V18_Research.mq5`. Do NOT treat this README as sufficient documentation.

- Canonical R9 v1.90 MQL5 `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`, Git blob **`7eecb5f1947017a01ce85b2520725de54749e523`** is unchanged.
- **Immutable new merged-primary Jan + Feb–Sep R9+Coinexx source ZIPs:** 272,352 historical entry timestamps and directions. Original Coinexx nine monthly TickLogger gzip files: **72,129,347 quotes**. Source 9/9 raw SHA256 and 2/2 original merge ZIP SHA256 reverified during V18. Historical merged records ONLY offline labels/grades.
- Source-only C++ decoder uses tick Bid/Ask/time_msc/MQL5 Bid/Ask change flags; 14 new derived indicators, including quote-arrival intensity (Hawkes-like), one-sided quote flag asymmetry, price-change pressure, spread recovery, activity/price-displacement (absorption-*like*) and quote impact. **There is no actual traded volume, DOM, executable OFI or true CVD in this data.** Quote-pressure indicators are proxies, not reconstructed unavailable order-book observations.

## Corrected research results

A source-only V18 circular-buffer newest-second bug was found and corrected **before final packaging**; all 9 months of extraction, sampling, model fitting, independent signal replay, and offline grading were repeated. Old provisional V18 numbers are superseded by **corrected** results below.

| Controller | 9m proposed entries | same side ±2 sec | ±5 sec | ±15 sec | ±30 sec |
|---|---:|---:|---:|---:|---:|
| Equal-capacity baseline with existing V17 features | 280,403 | 52,391 | 101,593 | 146,923 | 179,941 |
| Corrected V18 plus all 14 Coinexx-only indicators | 281,835 | 52,696 | 101,881 | 147,353 | 180,516 |
| **Frozen original V17B GOVERNING control** | **287,770** | **53,384** | **102,681** | **148,895** | **182,699** |

New V18 proxies improve ±5s alignment **+288** vs matched-capacity equal-threshold internal baseline, but underperform original V17B by **800**. All nine months satisfy >=90% monthly signal-count floor; none of this is an executed/filled trade or a P&L claim.

Research diagnostic, with observed-minute groups withheld from fitting *within* the same nine-month in-sample months: first-entry event AUC existing/augmented **0.846666/0.848553**, rearm **0.824550/0.825045**, first-side **0.785482/0.787593**, rearm-side **0.803949/0.807220**. The incremental explanatory signal is small and does not transfer to a better full-controller alignment score.

Second targeted test held the **exact V17B 287,770 entry timestamps fixed**, allowing model-based proxy BUY/SELL overrides. On the original nine-month frozen merged matching ledger, the best threshold caused **zero overrides**; same side ±5s match stayed 102,681. Thus **proxy side override REJECTED**, also no native MQL5 integration of proxy signals.

## Governing next mechanism, NOT yet implemented

Instead of stacking more generic indicators, reverse engineer **market-event queue states** that create separate first/rearm opportunities using earlier R9-qualified bracket/S1 impulse memory, causal sweep/reclaim state, quote-impact/renewal proxies, eligibility/position-clock and the option to WAIT. Fit full **sequence-aware entry-hazard decisions** only with observed Coinexx ticks; grade one-to-one same-direction ±2/5/15/30s alignment, volume floor in each month, and future compatibility with the one-position R9 minute-cycle execution structure. Frozen merged timestamps are training/benchmark labels, never runtime inputs.

**Rollback:** this branch is isolated, inherited directly from V17B. Original approved HybridGate MQL5 untouched. **No native MQL5 compilation**, no real-tick MT5 Strategy Tester certification, no hold/exit or funded-account results in V18. Full executable source is pinned in MT5_EXPAND ZIP, not just in this README.