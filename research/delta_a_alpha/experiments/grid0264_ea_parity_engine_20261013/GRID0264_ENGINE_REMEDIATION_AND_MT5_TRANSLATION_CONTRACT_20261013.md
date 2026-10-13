# GRID0264 — Python Engine Remediation / MT5-Translation Contract
**Date:** 2026-10-13. **Branch:** `delta-A-alpha` (no new branch). **Class:** source-preserving engineering repair; research-only, no trading activation, no GRID0258/official J0183 promotion. **August 2026 sealed**.

## Executive engineering verdict

**This package repairs and regression-tests the discrete execution defects and provides a working causal GRID0257-source → observed-quote shadow funding research pipeline plus a separately verified-position MT5 event contract.** It does **not** falsely certify that the current active `FourSessionV1` is now a faithful MQL5 EA specification. No Coinexx real symbol/account transaction history has been provided; the newest repository source router's extra GRID0258 renewal features and the active V1's entire L0–L7 implementation must be plugged in and verified independently before translating that engine into an EA.

The fixed modules are executable Python. They are NOT pseudocode. They are isolated from current active trading code pending complete equivalence tests. No synthetic shadow fills are promoted to a live broker-paid anchor.

## Preserved owner mandate

* Original Jan–Jul Dukascopy XAUUSD **ordered original Bid/Ask ticks** are the causal backtesting environment; the first-observed quote per second can screen engineering performance but is not full tick-execution equivalence.
* R9 SYNTH (219,342 trades; +$309,122.85 original MT5 account dollars) is the objective; its 60% gate is **131,606 real completed deals and +$185,473.71 original tester-account dollars, both simultaneously**. R9 OVERFIT may inform *research hypotheses* about optimal direction, lifecycle, exit, speed and profit, but never live future labels.
* The bot is a coordinated high-daily-velocity, high-accuracy-hourly, multi-day-geometry, multi-HTF, multi-scalping, sniper, multiregime grid system, not just an HTF sniper strategy.
* Jan–Jul monthly conditions are different and must not become month-identity input features; August is sealed. Avoid nonreconstructible indicators, Martingale, loss-based size escalation, unauthorized branches/live EA activation.

## Concrete defects and fixes

| Failure or conflict | Repair | Evidence |
|---|---|---|
| G0 source separated from funded Python execution | `v1_grid_cumulative_source_adapter_0264.py` connects real cumulative **archived GRID0257** router to explicit completed M1/H4 observer; rejects unsigned/unknown/stale events | Jan 300K first-second source replay; unit tests; 7x 205K integrated monthly samples |
| Python quote simulator could execute on nontradeable quotes or same-ms exit/reentry | Reuse GRID0262 hardened quote engine with required explicit research quote permission, delayed entry, stop/expiry and same-ms protections | Inherited 231 tests; updated 63 tests; all-month sample cash reconciliation |
| Research marked equity omitted expected fees on *open* positions | `CostReservedObservedFundingEngine0264` subtracts projected roundtrip fees from marked equity/free capital; actual settlement fee remains charged once on close | Fee reserve regression |
| Protective target/trail lacked continuous research bridge | `Grid0264ResearchRuntime` now attaches predeclared source-specific target/trail/time-stop policies through inherited observed lifecycle module | source→shadow tests; no broker stop ACK claimed |
| Old GRID0263 transaction record assumed close uses the same entry order ID | `VerifiedMT5PositionLedger0264` reconciles by `DEAL_POSITION_ID`; separate `DEAL_ORDER` for entry/exit; permits broker-generated server SL/TP/SO history exits | separate-entry/exit-order tests, server stop tests |
| OrderCheck or OrderSend acceptance could be misinterpreted as filled deal | Only explicitly verified external `DEAL_ENTRY_IN/OUT` `HistoryDeal` records change accounting; duplicate events idempotent, conflicting IDs error | no-confirmation/no-fill tests |
| Out-of-order MT5 transaction callbacks and partial fills | Stage pending events until order evidence exists; full broker-history sorted replay with exact broker cash-delta reconciliation for late receipts | 3 new history reconciliation regressions |
| Parent paid anchors could accept position of the wrong strategy | `PaidSourcePositionBridge0264` verifies exact `proposal_id`, immutable source key, direction, chronology, .01-lot fill, observed VWAP, full close and verified account cash | wrong-owner test, source-time test, partial fills, server close tests |
| Broker SL/TP/trailing modification assumed without server acknowledgement | `BrokerAcknowledgedStops0264` requires observed position readback, actual broker quote, stop/freeze/tick-size properties and positive modify ACK before changing protected stop | 11 explicit stop ACK, deny, off-grid, bid/ask and wrong-position tests |
| Date/data horizon slippage in loop | `grid0264_integrated_replay.py` only permits calendar months 1–7, requires original-data explicit permission and never includes August | 7 monthly raw and 7 monthly 1s replay audit |

**No unverified 'broker_tradable=True' is inferred from the original Dukascopy timestamp or from the quote.** The offline scenario is named `hypothetical_research_tradable` and never produces broker-acknowledged fills. For actual EA, a broker-paid source must come exclusively from externally observed MT5 history and verified balance reconciliation.

## Repeated verification (not performance certification)

- Full archived inherited source+funding tests: **231 run, 1 skipped** (skipped prior missing separate asset).
- New GRID0264 targeted and integration tests: **63/63 pass**.
- Original **unresampled** Dukascopy `*.csv.gz` tick-row smoke: **25,000 in each of Jan, Feb, Mar, Apr, May, Jun, Jul = 175,000 raw rows**; original ordering and input validation; no long H1 warmup assumed from this prefix.
- Jan–Jul *first ORIGINAL observed quote per second* inherited datasets: **205,000 quotes/month = 1,435,000 observations**; 37,943 G0 emitted source candidates; 1,589 **hypothetical** shadow completed positions. **These are not 1,589 MT5 trades**. All 7 scenario ledgers reconcile; zero forged broker paid-anchor acknowledgements. This is a bounded *prefix* test, not a complete-month strategy backtest.
- January and July complete 205,000-quote integration outputs and settlement SHA256 each repeated **exactly** with current repaired code.
- Exact research model assumptions used for replay demonstration: $300 simulated starting cash, 0.01 lot, a *hypothetical* XAUUSD 100oz/lot, hypothetical 500:1 leverage, assumed $0.52 charge per 0.01-lot roundtrip (configured $52/1.0 lot), 16 shared slots, 250ms latency, 2.2 USD/oz protective stop, 3.6 USD/oz profit target, 2.0 USD/oz trail arm and .9 USD/oz trail distance, 30s horizon. **None are claimed as verified Coinexx values.** Model outcomes cannot be compared as if they were R9 account-dollar realizations.

## NOT YET RESOLVED—actual missing evidence / newest-source integration

1. **Newest original current branch source and full V1:** The code integrated in repeated local tests is the recovered *actual* GRID0257 router, with GRID0246–0257 cumulative source; it is **not** the latest GitHub `v1_grid_strategy_source_router.py` SHA `14e4c449b64c745c745e62c99d71be9fb0694257` with added GRID0258 micro renewal. And current `v1_four_session_architecture.py` SHA `ab2a623f2ee8c1aec37fee4894abd5e0f9d3302c` still uses `CooperativeGridGenesis`, not this new adapter. Replace/verify in a separate no-trading integration revision, not by silently changing the accepted V1. Must feed actual completed H4/H1/M15/M5 state and L0–L7 decisions instead of frozen smoke `research_geometry`.
2. **Broker external facts:** Verified Coinexx XAUUSD symbol point/tick sizing, contract, volume min/step/max, filling policies, stops/freeze limits, margin calculation, commission and swap history, actual broker-clock mapping, user account hedging mode and actual ordered deals are still not provided. The included read-only collector from GRID0262 can acquire many of those facts when run by the owner with MT5 connected; nothing invented here certifies them.
3. **Broker transaction authority:** The offline `VerifiedMT5PositionLedger0264` is a tested Python specification accepting externally authenticated `HistoryDeal` inputs, **not** the actual MQL5 `OnTradeTransaction` implementation, and no actual Coinexx transactions were provided. A positive `OrderSend` result is not a completed order, and trailing stops cannot be broker certified from Dukascopy quote observations.
4. **Full-period economics and source parent renewal:** GRID0258 parent ledger and August remain unchanged. The GRID0258 optional quote-only renewal must not be automatically interpreted as paid MT5 cash; neither the J179F T1 source gap nor complete L0–L7/7-month broker-funded economic gate is solved by this engineering package. Do not promote source events or paper settlements as 60%-of-R9 trading breakthroughs.

## Source-to-MQL5 conversion contract

Every approved EA would need explicit modules translating these units *without altering contract semantics*:

- `OnTick` → immutable original quote / as-of completed HTFs / protected source invitations; never convert source events directly to fills.
- `OrderCheck` → checks decision only; `OrderSend` → request acceptance only.
- `OnTradeTransaction` + `HistoryDealGet*` for `DEAL_TICKET`, `DEAL_ORDER`, `DEAL_POSITION_ID`, `DEAL_ENTRY`, `DEAL_TIME_MSC`, `DEAL_PROFIT`, `DEAL_COMMISSION`, `DEAL_SWAP`, `DEAL_FEE` → duplicate-resilient trade evidence, not synthetic quote fills.
- Stop-modification requests must get a positive broker ACK and readback of the *position's* actual installed SL, accounting for BUY Bid / SELL Ask and observed symbol stop/freeze rules.
- All refunds, charges, commissions, margin, account cash and server trading day must come from broker-verified values; if absent, fail closed and keep marked research totals labeled hypothetical.

## Reproduction

Extract this ZIP; run from the extraction root:

```bash
PYTHONPATH="$PWD:$PWD/recovered" python -m unittest discover -s recovered -p 'test_*.py' -q
PYTHONPATH="$PWD:$PWD/recovered" python -m unittest discover -s . -p '*_0264.py' -q
PYTHONPATH="$PWD:$PWD/recovered" python grid0264_integrated_replay.py --month 1 --one-second --limit 205000
PYTHONPATH="$PWD:$PWD/recovered" python grid0264_integrated_replay.py --month 1 --limit 25000
```

The replay scripts expect the same original Jan–Jul `.csv.gz` and inherited `j0261_Mxx_original_first_1s_QBV.npz` external paths from the owner handoff; the ZIP deliberately does not replicate the enormous raw source data or August. All exact latest tested replay results are in `results/`. The alternative hypothetical all-tradable permission is explicitly model-only. Never treat it as genuine Coinexx session permission.

**Engineering sign-off:** New targeted components repaired and tested; isolated end-to-end research replay functional. **Active full V1/real MT5 EA translation still not certified.** No current strategy economics promoted, no trading activated, no new branch.
