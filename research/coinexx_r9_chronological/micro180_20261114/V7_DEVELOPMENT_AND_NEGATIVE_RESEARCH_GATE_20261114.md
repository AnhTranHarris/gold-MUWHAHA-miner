# R9 Micro180 V7 — source-aware conditional-entry integration, research verdict

**2026-11-14 | NEW VERSION: V7 | NOT PROFITABLE | NO R9 EA PROMOTION | PYTHON 47/47 LOCAL PASS, NATIVE COMPILE NOT VERIFIED.**

## Governor and historical lineage preserved — no repeated rebuilding
V7 is strictly additive on V6 branch `carson/r9-micro180-v6-past-only-cash-utility-20261114`, **source commit `6162e4ae7011a85119353fb5e7ee2018839eb53f`**. Original R9 v1.94 EA and rollback untouched. Previously completed/rejected variants were inspected and **not repeated**:

| Frozen test | Trades | NET modeled account cash | Status |
|---|---:|---:|---|
| Original 60s R9, 2026 Jan–Sep | 303,934 | -$120,212.46 | reference only |
| 4-lane 5s/15s OR-entry, same 9 months | 419,389 | -$162,656.05 | worse |
| Selective Micro180, same nine months | 61,258 | -$24,158.30 | fails profit AND throughput |
| V5 250ms BUY/SELL quote-path and protected-hold Jan/Sep first 200k | reported in V5 ledger | negative in both | rejected |
| V6 unconditional 180s first-passage gate Jan/Sep first 200k | reported in V6 ledger | negative and sub-volume | rejected |

**Known formula and engineering traps preserved:** old 250ms teacher inverted SELL sign; old Bayesian selection chose direction before checking eligibility; old 102-feature path collided distinct chronology; original R9 cash trailing activation was PRICE not NET; earlier V5 Python runner lacked high-watermark ratchet; V6 past 180s cash outcomes were *UNCONDITIONAL on actual entry setup*. V6 had already fixed the runner issue; V7 addresses **only the unconditional prior**. No rebuild of a huge tick library, no Dukas files, no old 155-feature AUC.

## V7 implementation
- New `v7_conditioned_cash.py`: existing original source-ordered millisecond quotes → bounded rolling **180s**, existing 250ms/1s/5s/15s/30s candles, original V5 independent executed-side BUY/Sell quote paths. Does not fabricate missing seconds or consume forming bar high/low.
- V7 evaluates both **BUY Ask-entry/Bid-liquidation** and **SELL Bid-entry/Ask-liquidation** at each actual eligible current quote, as distinct action labels. For historical 180s anchors, it independently computes *already completed* 5s and 15s executable-side directional efficiencies, spread change relative to previous 15 completed seconds, and quote updates relative to earlier observed seconds. Anchors must agree on 5s and 15s signed direction and carry their entire completed future *6-second* first-passage path in **the past relative to the current decision**.
- Similarity: `w_i=exp[-.5*((ΔER5/.55)^2+(ΔER15/.55)^2+(ΔspreadRatio/.5)^2+(ΔquoteRate/1.5)^2)]`, with 7s anchor stride, source gap refusal and weights below .01 discarded. **These engineering weights are not trained nor validated.**
- Historical first passage: break at first executable-side **NET cash >=+$0.10** or **<=-$2**, otherwise mark the completed six-second endpoint. Each path charges the original quote-side spread **and** incremental $0.20 round-trip. Separate side-weighted expected cash and heuristic standard-error penalty are outputs; effective sample count `(Σw)^2/Σw²`; not a calibrated lower CI or Bayesian posterior.
- Existing V6 $0.10 first cash harvest, $1.75 preferred cap, $2 first-available cash emergency, at most 30s default hold, optional risk-protected continuation, daily/peak/25%-capital governors and max four source-minute entries **unaltered**.
- V7 entry gate and V7 conditioned-hold changes **OFF by default**. This is an observation overlay to protect throughput; opt-in admission gates are research-only experiments, *not* model updates or deployable strategies.
- Native `Experts/GoldMuwahahaMiner_R9_Micro180_V7_Research.mq5` fork and `GoldMuwahahaR9V7ConditionedCash.mqh`: source-history `CopyTicks` catch-up + original Bid/Ask source ms; existing `iADXWilder` M1 +DI/-DI, EMA20 M1, `iATR` M1/M5, quote-activity count (not traded volume), 180s conditioned executable-cash shadow via native `OrderCalcProfit`. **All demo orders OFF, cash gate OFF, old high-AUC disabled**. New native V7 feature formulas intended analogous but not parity-certified. Python bounded fast profile differs from native conservative default technical filters. No MetaEditor compiler was available: **cannot claim the native fork builds or matches Python yet**.

## Original-Coinexx January and September controlled diagnostic (200k each; IN-SAMPLE)
Same original 200,000 quote rows in each month, same fixed V5 'fast' structural settings and same $0.20 round-trip extra fee, K=$1 / $1 XAU price at 0.01 lot, identical read-only original source. **Governor explicitly OFF only for isolated economics** (not a deployable performance report). Open positions at slice boundary excluded. Four arms share a single source iteration per month; **no new tick cache**.

| Arm | Jan trades | Jan NET | Sep trades | Sep NET |
|---|---:|---:|---:|---:|
| V5 frozen quote-path first $0.10 harvest | 912 | **-$350.04** | 1,116 | **-$453.51** |
| V7 setup-conditioned SHADOW; no gate | 912 | **-$350.04** | 1,116 | **-$453.51** |
| V7 relaxed matched setup cash gate | 217 | **-$82.77** | 317 | **-$138.77** |
| V7 strict nonnegative matched setup gate | 5 | **-$0.54** | 5 | **-$1.15** |

The *shadow* preserves exact entry/exit model scores, proving it is observation-only on these slices. Both active V7 gates remain negative and sacrifice throughput; they **FAIL joint positive-NET + >=original R9 volume criteria**. A smaller negative TOTAL is NOT positive, and a stricter gate yielding almost no trades is not a trading breakthrough. The current threshold experiments are already exposed in-sample and must not be rebranded OOS.

## Trade-volume / profit / risk contract
- **Objective must pass simultaneously:** at least 303,934 comparable filled positions on identical Jan–Sep source chronology **AND positive after-cost total NET**; owner prefers stable performance across months, independent later frozen out-of-sample validation. With 419,389 original dual OR fills, high volume is feasible as a count but those entries lose worse.
- Intended per trade limit $2 NET **cannot guarantee realized loss during quote gaps / broker slippage**. New cash gate cannot weaken original stop/quotetime safety. Daily governor and stricter existing 10% peak drawdown remain, plus persistent 25% starting-equity emergency; multi-terminal account-risk coordination remains unverified.
- Trade proxy `volume` and `last` in first 1M source rows were zero in previous QA; use quote intensity only as explicitly labeled **market-quote activity**, not transacted volume, VWAP, order flow or order book depth.
- User's high trade *COUNT* objective is NOT the same thing as BUY/SELL transaction volume. R9 restricted to 0.01 lot unless owner explicitly changes sizing; no invented high-volume filled orders.

## Required next gate (source-exact, no broad parameter grid)
1. **Native MT5 compile and exact Python↔MQL5 signal/indicator parity**, including equal-ms updates, broker `OrderCalcProfit`, M1/M5 indicator warmup, session ATR and actual spread. CI Python tests do NOT satisfy this.
2. Audit V7 setup-conditioned predictions at each **actual candidate ordinal** with paired actual first-passage outcomes and protective stops to see whether 180s history has any predictive information; current estimator uses a heuristic similarity kernel and sparse samples, not stable positive-hazard evidence.
3. If warranted, source-only chronologically frozen walk-forward **entry** calibration and matched-entry **exit** counterfactual on original historical data. Do not optimize on Jan/Sep slices and pretend OOS. Evaluate +0.10 harvest vs legal protected continuation toward +1.75, no lookahead or cash-target guarantee.
4. Separately assess account constraints at $100/$500, true stop/freeze distances, actual Coinexx broker fees/slippage, and full nine-month original trade count. If all candidate modes remain negative, **REJECT**. Do not loosen risk rules or change sign of cash to force a positive label.

**Status: V7 code integrated as separate research overlay with MT5 price indicators/proxies; no demonstrated positive net, no live/demo trading authorization, no full nine-month V7 run, no MT5 compile/parity certification.**


## Follow-up V7 optional conditional hold: active code, still negative (2026-11-14)

The first V7 Python build contained an unused `enable_conditioned_holding` option. **This dead/inert flag has now been repaired** without touching V6: `conditioned_incremental_hold` matches past completed 5s/15s executable-side configurations, evaluates a 3s future-liquidation-price increment **strictly within already completed historical quotes**, and charges **no second commission**. It can request cash harvest at >=$0.10 observed net when continuation is not supported. It cannot execute unless *both* the existing experimental runner and legal protected V5 stop logic are enabled. It retains the inherited $1.75 maximum, 30s timeout, $2 first-available cash emergency and account governors. The estimator is cached **once per observed second**, rather than recomputing on every source tick; 49 local and 49 GitHub Actions regression contracts passed.

New bounded **first 50,000** original quote checks (separate from the above first-200,000 results), fixed original fast profile and ungoverned economics for comparison:

| Slice | V5 unchanged first harvest | V7 conditional protected hold (no V7 entry gate) |
|---|---:|---:|
| January first 50k | 216 trades / **-$72.21** | 215 / **-$70.49** |
| September first 50k | 232 / **-$96.54** | 232 / **-$97.16** |

January reduces gross model loss slightly; September worsens, so this **does not demonstrate stable positive expectancy or full-system profitability**. The native V7 MQL5 fork presently includes V7 **entry-conditioned cash SHADOW**, not a separately compiled/parity-proven V7 hold model; its original V6/V5 cash exits remain the native comparator. **Do not claim end-to-end Python/MT5 V7 exit parity.**

The 200k Jan/Sep conditional entry gating, 50k hold experiments and their negative results are all research-exposed in-sample. No full nine-month V7 replay or real fill/commission certification has occurred.
