# R9 Micro180 V6 – development audit, integration, and bounded causal economic verdict

**2026-11-14 · RESEARCH ONLY · FAIL profit/throughput gates · NO MT5 PROMOTION.**

## Exact lineage and work already done
This is a delta on the existing V5 source commit `8f44f35dd8de596cf0ad8bdfa3d0fb51f88a147b`; **do not repeat or rebuild**:
- frozen Jan–Sep 2026 original R9 baseline: **303,934 completed trades; −$120,212.46** modeled net; original all-nine-month Coinexx gzip quotes 72,129,347 rows, SHA-matched to existing receipt;
- original four-lane OR dual 5s/15s baskets × 15s/30s breakouts: **419,389; −$162,656.05** modeled net;
- prior selective Micro180 original-source 180s completed-quote context: **61,258; −$24,158.30** modeled net, only ~20% of original R9 volume, zero positive months;
- prior V3 asymmetry with independently signed BUY/SELL completed Bid/Ask paths, V4 deferred fill, old aggressive/relaxed structural thresholds and sign-reversal probes, V5 first 200k Jan/Sep and 250 ms path tests: all fail after-cost positivity;
- *historic formula errors*: inverted SELL label in old 250ms teacher, action chosen before eligibility in old Bayesian router, and collapsing distinct source-ordered paths into identical representations. V6 guards independent BUY/SELL evaluation and uses preserved completed-quote millisecond source order.
- The original Coinexx first 1M quote audit found **`last` and `volume` all zero**. Derive quote intensity and coherent Bid/Ask revisions, **not genuine traded volume, VWAP, order-flow delta, market depth or liquidity imbalance**.

## V6 implemented without modifying frozen control
- New `v6_past_only_utility.py`: uses existing `RollingThreeMinute` ring, **past only** 180s of completed 1s Bid/Ask closes; 5s detection, 15s structural validation, 15/30s executable Bid (BUY) / Ask (SELL) breakout and source-ordered 250ms path remain in existing V5. Non-overlapping historic anchor stride 8s, finite horizon 6s and strict quote-gap refusal. Independent BUY and SELL first passages: `N_buy=K*(Bid_liq−Ask_entry)−C`, `N_sell=K*(Bid_entry−Ask_cover)−C`; preferred $0.10 harvest, $1.75 maximum, -$2 modeled adverse barrier. Report mean and *heuristic* one-standard-error penalty; **not** calibrated probabilities/learned conditional expectancy. No current unfinished bar or future quotes consumed. Economic gate **shadow/audit-only by default** (failing gate must not activate silently). V6 explicit experiment runner opts in to prior veto.
- A separate three-second past-only hold-increment estimate uses the same executable-side liquidation quotes, without charging already-incurred commission again.
- Found and repaired an existing V5 **Python research protected-runner high-watermark bug** only in the V6 subclass: its cash trailing stop previously did not ratchet as net MFE increased, unlike the MQL5 V5 fork. V6 cash trailing uses maximum observed net less prior runner cash-trail allowance, only tightens legal stops, and requests harvest when profit cannot be protected; equal-ms and gaps cannot be assumed executable. BUY and SELL stop-ratchet regressions added.
- New `run_v6_bounded_replay.py` replays existing gzip read-only; `--economic-control-ungoverned` is explicit for isolated diagnostics. **Account governor ON by default**; existing daily gross/peak and permanent-capital controls are not relaxed.
- Separate research-only V6 MQL5 fork `Experts/GoldMuwahahaMiner_R9_Micro180_V6_Research.mq5`, plus `GoldMuwahahaR9V6PastOnlyCash.mqh`: existing millisecond `CopyTicks` catch-up, native completed M1 `iADXWilder` (+DI/−DI), EMA20, M1/M5 ATR, quote count/intensity, spread, 250ms price coherence plus V6 native `OrderCalcProfit` BUY/SELL cash history, at most once per source second. MT5 default `InpEnableDemoOrders=false`, V6 cash gate default OFF, V6 hold utility default OFF, old 155-feature high AUC absent. **NOT MetaEditor compiled, not native/Python parity-verified.** Native V6 gate's technical defaults are not equal to the permissive Python fast pilot profile.
- Original `GoldMuwahahaMiner_R9_HybridGate.mq5`, original V5 MQL5 fork, older Python source, and original Coinexx/Dukascopy archives **unchanged**. No source download rebuild or bulky new caches. CI regression suite **41 tests** passed at preceding checked revisions.

## Same-original-source January and September bounded first 200,000 quote evidence
**Unexposed source was NOT used:** these are heavily research-inspected *in-sample partial-month pilots*; all source quotes are original, same exact first 200,000 per month; ungoverned economic arms explicitly marked for apples-to-apples research. Illustrative nonbroker-certified K=$1 account-currency/$1 XAUUSD move at 0.01 lot; C=$0.20 added per round trip beyond observed entry Ask/exiting Bid or SELL Bid/Ask; source-native gap stop may lose >$2.

| Original source slice | Old V5 cash harvest | V6 relaxed past-cash gate | V6 near-zero past-cash gate | V6 cash gate + **corrected** protected hold |
|---|---|---|---|---|
| Jan first 200k | **912 / −$350.04** | **249 / −$93.29** | **1 / −$0.76** | **247 / −$92.19** |
| Sep first 200k | **1,116 / −$453.51** | **307 / −$128.92** | **2 / −$0.71** | **305 / −$132.39** |

Cells are completed trade count / modeled NET account cash. Late-slice open positions excluded; entry counts can exceed completed counts by one. January V6 relaxed retains **27.3%** of V5 completed trades, September **27.5%**. All four new arms still negative net. V6 runner change versus earlier partial results: Jan −$92.35→−$92.19, Sep −$132.43→−$132.39. Do not misinterpret reduced TOTAL losses from far fewer trades as a profitable improvement.

The 155-feature old AUC model was **not** used. V6 ungoverned historical prior is not proof of positive conditional expected cash, and the tested thresholds do not provide the original R9's 303,934 trades/9mo.

**$500 capital governor reality check (first Jan 200k, same source):**
- V5 36 / **−$15.12** modeled net.
- V6 relaxed 38 / **−$15.88**.
- V6 near-zero 1 / **−$0.76**.
- V6 corrected protected hold 38 / **−$14.58**.

The existing stricter daily gross-loss and peak-account controls halt throughput long before 25% permanent capital-loss floor if the strategy continues losing. The owner requirement is jointly high trade volume, **positive NET after actual commissions/slippage**, $2 intended per position and 25% capital-loss circuit breaker *with stricter original governor intact*. Positive+high throughput was not demonstrated; do not disable risk to create order volume.

## Engineering defects and unresolved source-parity risks
1. Old native R9 trailing +0.10 **PRICE** move is not +$0.10 **NET**. Preserve executable-side cash accounting and broker cost reserve.
2. Local 180s historical BUY/SELL outcomes are *unconditional near-past first-passages*; they are **not conditioned on current entry signal regime**, so treating them as profitable posterior or high AUC is mathematically unjustified. This is the principal next quant modeling target, with paired **on-policy** stop/harvest/horizon labels.
3. Price-only quote stream has no transaction volume, DOM, actual broker fill paths; 250ms and 1s bars cannot be fabricated across missing timestamps. Equal-ms records must retain arrival/source order.
4. MQL5 `OnTick` can coalesce incoming events. `CopyTicks` recovers context but a market order can only fill at the *latest available* executable quote; Python source tick-order replay needs a terminal order-latency/slippage bridge.
5. MT5 broker `OrderCalcProfit` real symbol sizing, commission, margin, min stops, freeze level, tick size, and native indicator buffer parity not yet verified. The additional assumed C=$0.20 and K=$1 are not broker fills. Open position can gap past $2 loss.
6. V6 source prior may reduce per-trade aggregate negative cash while vastly lowering frequency; positive expectancy at scale has **not** emerged. Prior January/September in-sample score chasing has low statistical credibility.
7. Separate native MQL5 code has **not** been MetaEditor compiled; GitHub Actions Python regression success is NOT MQL5 compilation or performance certification.
8. Neither old original R9 nor V5 nor V6 satisfies proof of positive OOS economics, simultaneous original-like throughput, and live governor safety.

## Next bounded scientific gate — no gratuitous search or expensive rebuild
First run a **source-exact matched-entry first-passage audit** of V5 fast and frozen original R9 candidates: BUY vs SELL, source time in ms, session, quote activity/gaps, spread shock, completed M1 ATR/Wilder trend, prior 180s structure, MFE/MAE at **future executable quotes** conditional on **entry at actual signal timestamp**, first target +$0.10/+$.50/+$1.75, loss -$2 and timeout +1/3/5/10/15/30s, including realistic order-latency/slippage stress. Restrict research to compact candidate records from existing gzip streams, no raw ticks duplication or broad parameter grid. Only then derive regime/side-conditioned exit utility/threshold bands using an early training portion, freeze them and use *later untouched dates* as true OOS. Preserve a count/volume ceiling **AND** net-profit gate jointly.

**RELEASE STATUS: REJECTED FOR PRODUCTION. No guarantee of profitability, per-trade maximum realized $2, or account maximum loss under gaps. The economics cannot be made positive by relabeling loss, deleting losing trades post hoc, inventing volume or loosening the governor.**
