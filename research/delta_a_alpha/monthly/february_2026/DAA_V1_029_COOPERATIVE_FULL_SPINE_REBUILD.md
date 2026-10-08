# Delta-A-Alpha — V1 Unit 029: Cooperative Vertical Grid Execution Rebuild

**Owner task:** Restore a full, cooperating HTF/scalping frenzy XAUUSD vertical grid bot instead of cherry-picked independent sleeves.

**Status:** **IMPLEMENTED AND EXECUTED AS A NEW FULL-LAYER COOPERATIVE RESEARCH SCAFFOLD; NOT HISTORICAL V1 131E/134K SOURCE PARITY, NOT PROFIT QUALIFIED, NOT MT5 PORT**.

**Deployment:** February 1, 2026 00:00 UTC. January 18–31 (14-day requested range) supplies **pre-deployment historical EMA and completed-M5 features only**, no January funded trades, no February future labels. First February quote: February 1, 23:06:26.655 UTC. August sealed; September reserved. Do not claim that February is a pristine untouched holdout because its historical outcomes were previously inspected.

## What was repaired in execution logic

**Before:** Rebuild 028 chose a single `sr` source and skipped independent L3/L4/L5/L6/L7 proposals based on `if sr==0` priority branches. This is a source-suppression defect: making one candidate could prevent other valid strategies from even reaching the portfolio governor.

**After:** 
1. L0 executes all prior funded positions and records completed results from actual ordered Bid/Ask ticks, checking first-touch target, protective stop, age and simulated stopout.
2. L1 updates each session's grid anchor / gap and first-passage ownership; separate Asia/London/overlap/NY/late partition. A bounded adaptive gap uses *already completed* M5 range.
3. L2 computes completed-bar EMA8/21 state on H4/H1/M15/M5 and previous completed M5 range. H4 defines environment; H1 parent; M15 phase; M5 transfer. Distinct contextual roles are required and not assumed to be captured by sign-only MTF; fuller phase/location reconstruction is a parity gap.
4. L3 reconstructs source-019 hour and 10-minute subphase cadence/TP/SL/hold and **preserved January 131D entry-ownership signatures**; emits its own proposals independently. An optional *separately attributed* L3B high-volume HTF continuation is available only as an **OFF by default, REJECTED research switch**.
5. L4 emits independently from session-local Asia grid crossings and topology, even when L3/L5 generates on the same tick.
6. L5 Watchdog proposes funded scouts/renewals, requires *actual funded closed wins* for four-fast-win unlock and relock, keeps campaign depth, cell ownership and end timestamp, and never uses shadow outcomes. Legacy 049→051→075→084→119→131E **multi-parent stream is not yet exactly reproduced**; current result is materially lower velocity.
7. L6 trend-within-trend generates native structural reclaim and independently attributed M1 stair continuation signals using only H4/H1/M15/M5 completed structure, session grid and present tick displacement. This is an engineering candidate, not validated Feb134C/PF10 routing parity.
8. L7 physically generates bounded recovery proposals only after *actual funded* session/native loss followed by already observed HTF reversal + price reclaim, fixed 0.01 lot, no averaging/Martingale.
9. L8 sees all proposals in an independent bounded 1,500ms queue. It applies **one new supplemental ticket per market tick**, shared physical position cap, combined L3 + L3B capacity, per-engine inventory, actual quote spread, full floating equity, modeled free margin/stopout and funded prior-outcome-only rolling priority. Each layer's proposals, fills, denials, dropped queue items and P/L are separately counted. The global arbiter chooses funded tickets, **not the order of the source-code `if` branches**.

## February full historical run (reconstructed executable model)

**File** `coop029_cap128_a1_h0_d28_metrics.json`. Input Feb 7,538,339 ticks, 14-day Jan history, 0.01 lot=1 XAU ounce assumed, research transaction charge $0.02/trade plus actual Bid/Ask spread, cap128, capital $100k, leverage100 hypothetical, original L3B research OFF, causal M5 grid-width adaptation ON.

| Metric | Rebuilt 029 | R9 SYNTH reference (canonical MT5 tester report) |
|---|---:|---:|
| Net | **+$8,573.59** | +$66,213.65 |
| Funded trades | **3,667** | 33,523 |
| Gross loss | **-$4,000.97** | -$2,327.59 |
| PF | **3.1429** | 29.447 |
| Win | **47.01%** | 88.387% |
| Floating equity DD | **$3,058.38** | Not comparable across execution environments |
| Positive trading days | **7/20** | Not a direct same-model comparison |
| Positive weeks | **4/4** | Not a direct same-model comparison |
| Maximum open | **107/128** | Not a direct same-model comparison |
| Time first quote / HTF ready | **2026-02-01 23:06:26.655 UTC, identical** | — |
| First funded trade | **2026-02-02 09:00:00.113 UTC** | — |

**Independent layer attribution**: L3 +$10,424.08 / 1,560 trades; L4 -$440.39 / 320; L5 -$38.64 / 36; L6 -$1,378.18 / 1,749; L7 +$6.72 / 2. See exact JSON/CSV.

**Reject L3B aggressive expansion as profit candidate:** three-day sample produced **3,160 additional residual hourly tickets**, source8 net **-$3,715.39**; no favorable conclusion. This experiment demonstrates that high trade count without price-edge eligibility is unsafe.

**Important:** This rebuild remains **far below the required R9 SYNTH target**. It is an orchestration correction and QA baseline, **not** a performance milestone. All mandatory interfaces have code, but detailed original 134K source equivalence / physical lifecycle parity is unproven. The historical February $189K–$200K frontiers were selected after February outcomes and must not be passed off as as-of Feb 1 deployment settings.

## Remaining fidelity blockers before profit optimization or production

1. **P0 L5:** Recover the exact completed parent-builder and Watchdog chain 019→024→049→051→075→084→119→131A→131E under real executable quotes, with independent *actual funded parent and child* genealogy, campaign depth and global budget. Existing 029 L5 (36 tickets) is not faithful to the 131E profitable owner engine (tens of thousands). No phantom child credits.
2. **P0 L3:** Reconstruct original profitable high-volume coverage/residual owner streams using first-passage and funded evidence, not February hindsight-selected PF4 cells. The currently enabled 131D core has only 1,560 trades February. Do not turn on unqualified residual cadence merely to increase velocity.
3. **P0 L6:** Recover full February native PF10/WIN80 candidate-generation from disclosed rules (not frozen hindsight-winning cells), so trend-within-trend acts as a substantial positive-profit contributing layer rather than generic micro-stair losers.
4. **P1 L4/L7:** Build original Asia PF8 *causal entry qualification* and independent reversal-recovery ownership without February outcome-selection leak.
5. **P1 L8:** Coinexx symbol-specific contract size, fees, trading hours, fill/slippage, actual MT5 margin/stopout are still modeled, not validated; capital ladder $100k→$1k→$500→$300→$100 not certified.
6. **P1 live readiness:** Static historical bootstrap reached HTF state on the first tradable quote but **first funded order did not occur within five minutes**. The global order-ready state meets a simulated software readiness check; arbitrary deployment live MT5 readiness remains unverified.
7. **P1 MTF sophistication:** H4/H1/M15/M5 currently use completed EMA state; true multi-state structural location/phase/transfer reconstructible from original whitepaper is not fully implemented.

## Reproduction

```bash
python -m py_compile v1_029_cooperative_vertical_grid.py
python v1_029_cooperative_vertical_grid.py --cap 128 --capital 100000 --leverage 100 --adaptive 1 --hourly-expansion 0
python test_v1_029_cooperation.py
```

Raw inputs expected at the paths in the source code. Jan SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`; Feb SHA256 `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`. Unit029 archive does not repackage raw ticks.

## Owner-approved constraints

Whitepaper: `research/delta_a_alpha/whitepapers/DAA_VERTICAL_GRID_SYSTEM_V1_WHITEPAPER.md`. No month/date selector, no incomplete bar, fixed 0.01 lot, no Martingale, no buying larger after losses; cold-start tradable without online training if a qualifying opportunity is present; preserve all nine layer responsibilities and day/week/month scorecards; sealed August, reserved September. Research isolated; production and protected owner May cursor remain untouched.

## Unit 029 paired geometry ablation (same unified multi-source execution)

One additional unchanged-full-engine February run with **adaptive grid spacing OFF** (static per-session gaps) provides a causal paired architecture check:

| Cap128, February | Static geometry | Adaptive completed-M5 geometry |
|---|---:|---:|
| Net | +$7,755.61 | **+$8,573.59** |
| Trades | **4,332** | 3,667 |
| Gross loss | -$5,205.55 | **-$4,000.97** |
| PF | 2.49 | **3.14** |
| Win rate | 42.50% | **47.01%** |
| Floating equity DD | $3,116.75 | **$3,058.38** |
| Positive days | 7/20 | 7/20 |

**Interpretation:** preliminary January-preseeded adaptive gap helps multiple portfolio economics but sacrifices funded velocity; it does not satisfy targets. No February-specific parameter tuning is permitted to convert this into a claimed held-out result. Complete all 131E/134K original source parity first.

**Performance certification remains FAILED**, despite cooperative source integration QA PASS.