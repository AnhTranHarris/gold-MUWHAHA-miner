# MICRO180 RB3 — owner-directed R9 SYNTH profitable-cycle / Coinexx REAL tick-path trade-management research governor

**Decision date:** 2026-11-17 America/Chicago.
**Authority:** Explicit human-owner instruction in XAUUSD HTF project chat. This note establishes **research boundaries**, not approved or optimized hold, exit, stop, live-trading, or deployment settings.

## Fixed research question
For each complete **original R9 SYNTH net-profitable minute-cycle**, preserve the original R9 trade chronology and determine **how the actual Coinexx REAL TickLogger bid/ask path behaved between each original R9 SYNTH entry and exit**. Use those facts to study holding, drawdown, and prospective trailing-stop hypotheses only in subsequent authorized work.

The **cycle**, not the winning trade leg, is the inclusion unit:
`sum(original_R9_leg_net_usd for all legs in the complete original minute-cycle) > 0`.
No Coinexx repricing or future-price information selects cycles.

### Invariant population and accounting
- **178,511** original R9 SYNTH complete net-profitable cycles across Jan–Sep 2026.
- **253,477** component legs: **231,605 individually positive**, **21,827 individually negative** and **45 zero-profit** (all retained).
- Original R9 SYNTH selected complete-cycle net: **+$366,719.55**. This is synthetic tester accounting, **not** Coinexx quote or executable profit.
- Parent R9 original complete strategy: **272,352 total legs, 192,487 cycles, +$360,693.05** original SYNTH net. Net-nonprofitable cycles contribute **−$6,026.50**; their **tick paths are out of scope**. Their already-recorded total may be used solely to reconcile the preexisting full-account R9 SYNTH balance trajectory.
- **1,310** selected winning-cycle component legs lack `quote_net`; retain with explicit context-quality/missing flags. Never assume zero floating risk, fabricate Coinexx ticks, or alter original eligibility.
- Distinct but related corpus: `R9_SYNTH_POSITIVE_TRADES_COINEXX_MERGED_20261117.csv.gz` has **236,079 individually positive legs**, including **4,474** original positive legs from cycles with nonpositive net. **Do not use this positive-leg corpus as the final cycle selector.** Join useful quote/provenance fields by exact original source identities when applicable, but the fixed **253,477-leg corrected index** is authoritative for inclusion and for adverse/zero companion legs.

## Source-exact custody
1. **Authority: corrected complete-cycle target ZIP:** `R9_ORIGINAL_SYNTHETIC_WINNING_CYCLE_TARGETS_253477_20261117.zip`, Google Drive https://drive.google.com/file/d/1QzjjGO7RREgw1RywbGOZeQCX02XnOMnc/view. Internal member `original_R9_profit_cycle_targets_253477.csv.gz` SHA-256 **`0c7e0895436a984c926f07897e27ef769604f10c3d3450a353c6870a42bb7169`**. Reopened and checked to contain 253,477 rows, 178,511 unique cycles, 21,827 negative companion legs, 45 zero legs, and +$366,719.55 original net.
2. **Original R9 all-trade fixed reference:** `r9_synthetic_teacher_to_original_REAL_TickLogger_9m_trade_marks.csv.gz`, https://drive.google.com/file/d/1CC30szLw0_R9UpaRScPJZamgasqGjEsm/view; original source SHA-256 `9c9ebf5889c309a10e4370e355b99d75ae54cf5ccfdaa5ebab9042206f3f8cc5`. Never edit.
3. **Updated original-winning-leg merged quote lookup:** https://drive.google.com/file/d/1wrkrSQzk-GioEadtuFAoNi1oEYZzomla/view, SHA-256 `6246e26e1ce1c7ad556c9672b633b32c08047e0d9f57e3009299141f2641fd04`. It is an observational positive-*leg* subset, not a complete-cycle source.
4. **Existing MICRO180 target atlas:** https://drive.google.com/drive/folders/1LesUxQUTdVdXAfPdNGSng1CuoI3O2dus. Its 236,079 positive-leg targets and 23 atomic family annotation are permitted as context/cross-index, **not** replacement of the original positive-complete-cycle index.
5. **Existing intratrade source/scripts and result:** https://drive.google.com/drive/folders/1JsmB3vaxp28E2c5a2Au84BAtFU3Uw4bi; reusable `r9_coinexx_intratrade_path_audit_20261117.py`, late-part traversal script, audit aggregation. Prior 236,072 full paths apply to *winning individual legs* only, not to all 253,477 cycle legs.
6. **Existing family stop-preservation report:** https://drive.google.com/file/d/1RgI6KdcIHum-3zIMr4JMb8GiYUXNklkH/view; historical non-triggering envelopes, **not** a recommended risk policy.
7. **Current approved entry system:** frozen Jan–July `MICRO180_RB3_2026-01_THROUGH_2026-07_MERGED.json`, SHA-256 `b6f7a82b6ebdfbcf4a37ec2aa64daadbaece2f55dbd1cd348add6d0cb448c1a1`. Prior human-owner approval remains unchanged.

## Immutable chronology and interpretation
- For every eligible cycle and each constituent leg, original R9 `entry_time_broker`, `exit_time_broker`, side, first/second leg sequence, original net and original cycle family are **fixed reference coordinates**.
- Replay **only** the original historical Coinexx REAL tick observations at and between those marks. Use existing verified source logs; preserve original bid/ask, millisecond ordering, spread, quote gaps, and existing entry/exit mapping lag fields. Do not synthesize replacement observations or trim shocks out of canonical results.
- BUY mark: original mapped entry ASK to current BID; SELL mark: original mapped entry BID to current ASK, with verified 0.01-lot economics and separately explicit fees. Track floating P&L, maximum favorable/adverse excursion, post-peak floating drawdown, peak-to-fixed-exit giveback, spread/jump diagnostics, time from entry/through original fixed exit, and any intervening flat phase of a two-leg cycle.
- Missing/out-of-window quote anchors, cross-UTC-day legs, source gaps and abnormal jumps require labeled quality states. Keep them in denominator/source accounting; never silently delete or claim exact path certainty.
- Distinguish **R9 SYNTH fixed-exit result**, **Coinexx historical quote-side fixed-endpoint mark**, and any **hypothetical marked path**. None is a simulated live stop fill. Distinguish retrospective ex-post R9 family labels from signals known at decision time.

## Synthetic balance versus observational Coinexx chronology
Keep parallel, timestamp-aligned ledgers with consistent 0.01-lot contract, fees, currency and fixed endpoints:
A. The **existing original full-account R9 SYNTH balance/delta timeline** for historical context, using the immutable full historical ledger. It includes its recorded nonpositive-cycle net only as already-booked balance context; **no research, optimizing, or replay of those cycles**.
B. The **selected profitable-complete-cycle R9 SYNTH conditional ledger**: book each of the 253,477 retained original leg `net_usd` at its original fixed exit; compare against full R9 only with conspicuous cohort conditioning. Its +$366,719.55 total is **not** the historical all-account +$360,693.05.
C. The **Coinexx REAL bid/ask quote-side shadow ledger** for **those same eligible cycle legs at the same fixed endpoints**: historical quote mark at each tick; realized at original fixed exit, floating while open. Never call it actual broker-fill balance or profit.

If the authentic original account starting balance/deposits/withdrawals are not documented, present **balance change from a common zero offset** rather than assert actual monetary account balance. Keep event ordering stable for simultaneous timestamps; record unknown mapping rather than interpolate. Coinexx shadow curves are conditional research cohorts, not an independent runnable trading strategy.

## Anti-drift and no premature policy selection
- Only **original R9 SYNTH net-profitable complete cycles** enter the tick-path research cohort. Negative legs **inside** such cycles stay; R9 net-nonprofitable cycles do **not** enter tick-path research.
- Study A/B/C/D chronological hold phases and original 23 atomic context labels by session/regime and quote quality. Family labels cannot feed a live controller as future-known winners.
- Keep shock-spread subsets as **diagnostic comparisons** without deleting flagged observations or revising the primary statistics.
- Reuse existing Python causal tick traversal and historical REAL TickLogger files. Do **not** rebuild, redownload, rematch, archive or duplicate 71.8M+ ticks, or modify the approved RB3 entry weights/code.
- Not authorized by this charter: optimizing stop/trail/hold parameters, moving fixed exits, closing trades early, creating executable orders, introducing negative-cycle tick paths, retuning entry systems or claiming realized profitability. These require a separate explicit research and certification decision.
- Before any policy experiments: require verified cycle coverage (178,511 and 253,477), exact original entry/exit chronology, quote-coverage diagnostics, synthetic/counterfactual ledger reconciliation, family-specific path studies and a reproducible read-only receipt.

**In short:** Frozen R9 SYNTH fixes *who and when*; actual Coinexx REAL ticks explain *what happened between those marks*; balance curves remain separate and explicitly labeled; owner-approved RB3 entries remain untouched.
