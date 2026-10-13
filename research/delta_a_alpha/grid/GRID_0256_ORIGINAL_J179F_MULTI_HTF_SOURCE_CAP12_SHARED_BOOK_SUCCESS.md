# GRID0256 — Original J179F multi-HTF campaign throughput upgrade, preserved positive Jan–Jul book

**Governing owner formulation**: "r9 syth as perfomance goals, r9 overfit shows optimal trades, each month's market conditions are mostly unique, the grid trading strategy trading edge is a high trading volume trading bot, the grid trading strategy is a near multi-HTF, the grid trading strategy is a near multi-scalping trading bot, the grid trading strategy is a near sniper trading bot".

**Status**: researched successor to GRID0255; NOT qualified for 31/31 positive weeks, broker-funded execution, live MT5 or Vertical L1–L7. Do not activate, revive retired Gamma, open sealed August, or create branches/automations. Exact active branch remains `delta-A-alpha`; scientific cursor J0183 unchanged.

## Mechanism recovered and changed

Retain **all** original GRID0255 January–July fixed 1oz source-quote positions from five sleeves, except replace the 8-source-slot `GRID0185J_STRICT_BASE+IG+TRANS_M5_ENERGY_FAST30_SLOW90_CLOSES` harvester with the **original GRID0185G_STRICT_BASE+IG+TRANS_ALL90_CAP12**, a *preserved source-approved variant*, not a newly invented grid-gap rule. J179F is available in the original tick-derived 2026-04..07 source only; January-March unchanged. Replace; do not add duplicate J179F portfolios. Close/entry timestamps/side/price and ticket PnL are from the original preserved strict J179F source, and full shared portfolio is re-marked and reconciled to native source Bid/Ask on every tick.

Original J179F source conditions (from `GRID0185/_j185_horizon_base.py` and `grid0185g_strict.py`): T1 originally registered only after actual original source event; T2 original source quote arrives 2–10s later; H4=M15 completed alignment; strict H1=H4/M5=-H4 admission, ignition H1=M5=H4 at tight H1 location, transition H1=M5=-H4 with direction flipped and only if **actually closed** previous four full-hour portfolio PnL <=-$10 and at least one closed trade; market spread <=$1, completed M5 true-range ratio <=6, original GROSS40 NY17 risk/pilot governor, one original source quote per T2 millisecond, and Friday-close exclusion. Larger campaign authorization is **12 original source reservations (including pending) instead of 8**. All are constant one-ounce fixed exposures (broker 0.01-lot equivalence only if contract 100oz). No increasing risk/lot size after losses.

New source-permission port in `v1_grid0185_multiscale_permission_0256.py` enforces existing J179F T1 verification, observed T2, completed 4-scale state and source-global capacity, including prior actually settled hour loss. **It does not regenerate the original T1 source**, which remains absent from the active `FourSessionV1` code and must be recovered before runtime engine certification. Thus the historical ROI is confirmed by original archived J179F exact source + the full original Dukascopy tick book; it is **not** yet the autonomous runtime implementation's result.

## Verified one shared original-quote portfolio (source-quote USD/oz, NOT Coinexx account cash)

| Identical Jan–Jul source quote book | GRID0255 | GRID0256 |
|---|---:|---:|
| Net USD/oz (after modeled $0.52 round-trip) | +6,152.697 | **+6,539.081** |
| Genuinely closed one-ounce positions | 1,053 | **1,156** |
| Monthly positive periods | 7/7 | **7/7** |
| ISO weekly positive periods | 23/31 | 23/31 |
| Gross loss USD/oz | -8,727.613 | -9,367.447 |
| Worst original-tick floating equity DD USD/oz | 940.945 | 1,205.295 |
| Shared global max observed positions (cap16) | 12 | **16** |
| Quote-side entry / close mismatches | 0 | **0** |
| Global 16-slot denials | 0 | **0** |

Increment over original accepted: **+$386.384 (+6.28%) net and +103 (+9.78%) completed research trades**, without losing a positive month. This improves the user's two primary research categories under an already-preserved source definition. Increased gross loss and drawdown are **not** treated as success. This result is historical inspected, NOT blind out-of-sample, and not a viable $100–$300 starting-account claim.

**Month-by-month new complete-book account-quote proxy**: January +$1,508.141 (64 positions); February +$69.619 (52); March +$1,954.404 (65); April +$903.554 (201); May +$978.760 (233); June +$1,071.059 (269); July +$53.544 (272). Weekly eligibility remains 23/31; this was not a full weekly pass. July is especially vulnerable to additional realized brokerage costs.

### Exact QA protocol

`grid0256_preserved_j179f_capacity_variant.py` replays existing original strict archived J179F source positions in the same open ledger as all prior GRID0255 sleeves (not separate arithmetic). Original 57,527,562 Jan-Jul Dukascopy tick quote streams are read in UTC order, old positions settled before new ones at an identical timestamp, no synthetic quote is inserted; all 1,156 entry/exit PnL amounts match exact observed opposing Bid/Ask quote to within 1/1000 raw unit using $0.52 per roundtrip. Ten-times-millions of quote-side floating equity marks are processed across the one 16-position limit; max marked drawdown $1,205.295 source USD/oz, no timestamp mismatch or slot denial. Local source-permission unit tests: **11 passing**. No Android/browser or MT5 live orders, no new project branch.

Research rationale: confirmed structural persistence at multi-HTF source should be combined with independently bounded multiple near-scalping/harvest source decisions, but **volume alone is not a market edge**. Original R9 SYNTH full target still 219,342 completed trades / +$309,122.85 tester cash; January–July all-week quote profit and high R9 velocity are unachieved. Preserve current GRID0255 if available risk budget limits 16 concurrent source positions; do not automatically switch to GRID0256 in production.

## Source evidence and exact regeneration

`GRID0185_PROFIT_FIRST_HOURLY_STRICT_BIDASK_FULL_FLOATING_RISK_CODE_AND_EVIDENCE.zip`: original strict G/J source code and original `GRID0185G_STRICT_BASE+IG+TRANS_ALL90_CAP12_CLOSES.csv.gz`; immutable.
`GRID0255_CAUSAL_H4_TWO_SLOT_PROFIT_AND_VOLUME_RESEARCH_20261012.zip`: original quote-verified GRID0255 five-cohort source book, immutable.
`GRID0256_J179F_CAP12_SHARED_ORIGINAL_TICK_CLOSES.csv`: canonical 1,156 combined historical closed source ticket positions.
`GRID0256_J179F_CAP12_SHARED_ORIGINAL_TICK_PORTFOLIO.json`: monthly and weekly score, gross loss, full-tick marked DD, invariant checks.
`grid0256_preserved_j179f_capacity_variant.py`: replay script using preexisting full original 7-month source quote files and preserved `book_chunk`; no rebuilt raw 57m-tick ledgers.
`v1_grid0185_multiscale_permission_0256.py`: recovered causal T2-role permission source for eventual integration when original T1 source is available. The source *cannot* independently reproduce trades until original T1 event generator and Coinexx broker-cash calibration are provided.

## Next nonpromoted research priority

Retain original GRID0255/0256 positive monthly sleeves, while independently restoring upstream original J179F source T1 invite generation, connecting the original completed H4/H1/M15/M5 at 1–2s survivability and 15/20/30s profitable microcycle admission, and creating an actual funded shared portfolio with strict unit/cost/clock/margin checks. Attempt an additional genuinely positive weekly near-multi-scalping sleeve, not a calendar-week switch or retrospective OVERFIT whitelist. Save unsuccessful experiments to internal journal and do not promote them. The 31/31 positive-week and R9 SYNTH net/volume requirement remain open.
