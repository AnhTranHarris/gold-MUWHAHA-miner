# MICRO180 RB3 — Owner-directed positive-cycle-only Coinexx tick-path research protocol

Date: 2026-11-17 (America/Chicago)
Authority: Direct user instruction, XAUUSD HTF project chat. Complements, does not modify or supersede, `RB3_OWNER_APPROVAL_ACTIVE_ENTRY_BASELINE_20261117.md`.
Research status: GUIDELINES ONLY; no hold/stop/trailing implementation or profitability claim authorized by this file.

## 1. Immutable research cohort: original R9 SYNTH **net-profitable COMPLETE cycles only**

- Eligibility is computed **only from original R9 SYNTH leg `net_usd` values summed for a complete original minute-cycle**: `sum(original_synth_net_usd) > 0` under exact decimal arithmetic.
- Correct source index: `R9_ORIGINAL_SYNTHETIC_WINNING_CYCLE_TARGETS_253477_20261117.zip` (primary Drive ID `1QzjjGO7RREgw1RywbGOZeQCX02XnOMnc`). Confirmed target: **178,511 complete winning cycles, 253,477 total component legs, +$366,719.55 original SYNTH cycle net**. This necessarily includes **21,827 negative component legs and 45 zero-profit legs** inside winning cycles; retaining them is mandatory. Other 13,976 nonpositive complete cycles are excluded as *research candidates*.
- The `MICRO180_REBUILD_R9_SYNTH_WINNING_TARGET_ATLAS` and RB3 entry atlas enumerate **236,079 individually positive legs** (+$379,057.59); this is a DIFFERENT, overlapping corpus and cannot select complete positive cycles alone. Use that existing atlas as joinable labels/taxonomy and chronological index, not as the final hold cohort.
- The `R9_SYNTH_POSITIVE_TRADES_COINEXX_MERGED_20261117.csv.gz` (primary Drive ID `1wrkrSQzk-GioEadtuFAoNi1oEYZzomla`, SHA256 `6246e26e1ce1c7ad556c9672b633b32c08047e0d9f57e3009299141f2641fd04`) contains only individually positive legs. Join to the corrected complete-cycle index and original full R9 merged trade marks to retrieve companion negative/zero legs; **never erase them or impute them as zero**.
- Original full nine-month merged file `r9_synthetic_teacher_to_original_REAL_TickLogger_9m_trade_marks.csv.gz`, primary Drive ID `1CC30szLw0_R9UpaRScPJZamgasqGjEsm`, SHA256 `9c9ebf5889c309a10e4370e355b99d75ae54cf5ccfdaa5ebab9042206f3f8cc5`; contains 272,352 original R9 SYNTH legs in 192,487 cycles and **+$360,693.05** net for the entire original SYNTH strategy. That full result is a context/reference ledger only, not eligible for hold-policy sample selection.
- The older `R9_COINEXX_POSITIVE_CYCLE_HOLD_DISCOVERY_README_20261117.md` used `sum(mapped quote_net)>0` and 110,957 mapped-positive cycles: **it does not satisfy the new owner criterion**. Its numbers must not be used as baseline counts, account balances or training labels for this research.
- The earlier 236,072-path winning-*leg* intratrade audit and 23-atomic+4-parent preservation report are preliminary context only; recompute or reindex any claims to the **253,477 complete-cycle leg** cohort when actually analyzing paths.

## 2. Fixed chronological backtest experiment — what must NOT change

- Use the **existing original Coinexx REAL TickLogger tick stream**, original preserved source identifiers and verified hashes, with a causal, chronological **Python tick-sequence traversal**. Do not download, resynthesize, resample, refit, rebuild, duplicate, or remerge giant tick libraries.
- For each eligible R9 original positive complete cycle, **pin every original R9 entry and exit timestamp, side, first/second leg order, and original SYNTH `net_usd`**. No premature exit, stop fill, entry shift, retroactive stop logic, direction changes, or deleted paired leg in this fixed-endpoint observational baseline.
- Use existing `equote_ms`/`xquote_ms` anchors and original bid/ask matched quote-side prices to resolve actual source quotes. Record lag, spread, missing coverage and cross-day cases. If an anchor is not verifiable, mark `COVERAGE_UNKNOWN` and retain the target with null path statistics; do not manufacture ticks, silently drop it, or move it to a profitable time.
- Quote-mark floating P&L at **liquidatable side**: BUY open ask / close-and-mark bid; SELL open bid / close-and-mark ask; preserve verified contract/tick value, 0.01-lot conventions and original fees without double charging. Quote marks are **not actual fills**, and no execution/slippage assumption may be silently presented as broker-realized performance.
- Preserve precise ordered milliseconds, event sequence and original broker/UTC time conversion; distinguish trade holding vs the flat interval between first and second legs. Compute spreads and adjacent tick jumps as observed, without cherry-picking or deleting outliers.

## 3. Three separate chronological balance/equity contexts (never conflate)

**A — Full original R9 SYNTH account balance (reference ONLY):** If complete original account statement/starting balance is available, place its historical balance/equity on the clock, including all original strategy outcomes as reference. Nonpositive cycles are NOT studied as policy candidates. If original account starting balance, deposits, withdrawals, or timing are missing, DO NOT invent them; report cumulative realized `net_usd` rather than claiming actual account balance.

**B — Original R9 SYNTH selected-positive-cycle fixed-endpoint ledger:** Reproduce the **same selected 178,511 original net-positive cycles and all 253,477 component legs** in original chronological order, accumulating original SYNTH leg net only when exited. Label this clearly a retrospectively **winner-selected hypothetical balance**, never the original all-trade account curve.

**C — Coinexx original REAL quote-side fixed-endpoint ledger + tick floating equity:** Apply the *exact same* eligible fixed entry/exit/leg schedule on original Coinexx bid/ask quotes. Book mapped fixed-exit net in exit-time order and also compute tick-by-tick floating equity, peaks, troughs, and maximum open-position adverse excursion. Missing quote paths stay unknown and are reported separately, not filled or counted as zero. Use the same verified opening-balance convention as B to enable aligned dollar deltas. Values are observational quote marks, not executable P&L.

Do not present a comparison of B/C to A as a fair, all-trade, deployable strategy comparison: B/C condition retrospectively on successful SYNTH cycles, while A represents the full original system.

## 4. Forensic objectives, not proposed live stop rules

For each selected complete cycle and every included leg, by original source family, 23 exclusive atomic family labels, role (A1/B1/B2/C2/D1/N1/N2), trading session, broker minute phase, and month:
1. Exact live-quote path entry→exit, fixed SYNTH vs Coinexx quote-fixed exit, time in drawdown, MAE, MFE, peak-to-trough open-floating drawdown, peak-to-fixed-exit giveback, start/end and durations of excursions, time-to-favorable and time-to-adverse.
2. Separate price reversal from widening bid/ask spread and discrete adjacent-tick jumps; record both unfiltered and quality-stratified results, never discard observations to improve conclusions.
3. Paired first-leg, flat-gap, and second-leg exposure as a single selected cycle; compare marks, clock phases, path sequence and leg roles without assuming future family outcome is knowable at entry.
4. Read prior historical stop-preservation threshold and activation/interference grids as **counterfactual stop-touch diagnostics only**. A minimum observed non-triggering gap is not an optimum, not an account drawdown limit, and not a live stop recommendation. No early stop/trailing simulation is permitted to rewrite the fixed-endpoint baseline.
5. Verify exact count and accounting invariants above, source hashes, timestamp monotonicity, fee/sign convention, missing/cross-day statuses, and ledger reconciliation before any downstream policy design.

## 5. Source custody and authorization

- Approved active entry architecture: **MICRO180 RB3 frozen January–July 2026, 347 experts**, human owner approved November 17, 2026; original weights and source remain unchanged. Its Aug–Sep entry-volume replay was entry-*intentions*, not executed fills or positive trading P&L.
- Historical R9 SYNTH original trades, their profits and their endpoints cannot be relabeled or altered in this observational research.
- No new hold policy, initial stop, drawdown gate, trailing stop, or live MT5 EA modification is authorized **by this guidelines-only record**. Later policy design must occur as an independent successor with human review.
- Do not expand the research population to R9 SYNTH nonpositive complete cycles unless the human owner explicitly changes the cohort. A full-strategy balance may be displayed as a reference but must not trigger candidate-level analysis outside the cohort.
- Do not create redundant archives or regenerate original ticks. Retain the source files and earlier findings; append isolated compact research receipts only when necessary.

## Source locations
- Corrected original complete-cycle index: https://drive.google.com/file/d/1QzjjGO7RREgw1RywbGOZeQCX02XnOMnc/view
- Corrected original source accounting: https://drive.google.com/file/d/1XR4H3v_igYvLBCt3VPFImGhQ8fxbc3Jx/view
- Original full 9M R9 matched source: https://drive.google.com/file/d/1CC30szLw0_R9UpaRScPJZamgasqGjEsm/view
- Updated individually positive-leg Coinexx working merge: https://drive.google.com/file/d/1wrkrSQzk-GioEadtuFAoNi1oEYZzomla/view
- Earlier winner-leg tick-path audit (different population): https://drive.google.com/file/d/1SaJfm8bdVC01yyoCcdd1iw5HCFK6Mpnw/view
- RB3 owner-approved entry baseline: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/micro180-rb3-owner-approved-entry-baseline-20261117/research/micro180/governance/RB3_OWNER_APPROVAL_ACTIVE_ENTRY_BASELINE_20261117.md
