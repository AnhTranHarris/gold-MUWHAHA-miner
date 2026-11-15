# V11 all-original-Coinexx Jan–Sep 2026 — causal HTF + micro180 forward-path receipt

**2026-11-15 | Shadow only | No order changes | No profitability optimization**

## Source and execution scope

- **Nine original monthly Coinexx XAUUSD compressed CSVs**: all **72,129,347** original quotes replayed in original source order and independently SHA-256 checked against the frozen original source manifest. No new quote archives, bars, or tick caches.
- Original frozen V9 strategy monthly resets preserved: **338,065 entries, 338,064 completed trades**, reconciled month-by-month with the prior full Jan–Sep 2026 R9 V10 audit. **Do not imply this run independently rechecked all 338k trade ordinal/price tuples**; that check remains at the earlier source-verified Jan 200k V9/V10/V11 test and CI.
- Parallel observation carried V11 causal structure through **five chronological groups: Jan–Feb, Mar–Apr, May–Jun, Jul–Aug, Sep**. Independent group starts March/May/July/September each received **15 days of previous original-month, SHA-verified tick chronology** as causal H1/H4 warm-up before test entry. **Not one uninterrupted nine-month structure-state carry**: the 45-day H4 zone lifespan can extend earlier than the 15-day group initialization. Never call this exhaustive nine-month H4 persistence parity.
- Source / broker side only: all 72,129,347 ticks have **last=0, volume=0, volume_real=0**. In particular, `flags` contains frequently set bit 128 with no documented provider interpretation in this project; do not mistake Bid/Ask update count for true trade-volume / tape / institutional liquidity.

## Measured results

| 2026 month | Quotes | Frozen V9 entries | Original V10 UNRESOLVED, warmed | Entry-side valid V11 anchor | Later 180s structural invalidations |
|---|---:|---:|---:|---:|---:|
| Jan | 7,699,274 | 35,500 | 17,244 | 4.69% | 411 |
| Feb | 7,102,818 | 42,742 | 21,398 | 0.93% | 97 |
| Mar | 8,859,103 | 51,841 | 24,940 | 1.04% | 181 |
| Apr | 7,831,685 | 37,341 | 18,219 | 2.66% | 243 |
| May | 8,011,360 | 32,514 | 15,507 | 3.07% | 212 |
| Jun | 9,347,508 | 37,190 | 18,022 | 3.60% | 295 |
| Jul | 8,075,197 | 33,758 | 16,426 | 6.84% | 406 |
| Aug | 7,468,061 | 32,896 | 15,828 | 5.27% | 357 |
| Sep | 7,734,341 | 34,283 | 15,884 | 7.54% | 639 |
| **Total** | **72,129,347** | **338,065** | **163,468 / 48.35%** | **12,559 / 3.71%** | **2,841** |

- Prior V10 nine independent-month result was **162,309 / 48.01%** unresolved. The current **163,468 / 48.35%** reflects *different causal HTF warm-up/carry* and is **NOT a measured improvement/worsening**.
- H1 and H4 zones existed at **99.68% and 99.53%** of V9 entry events. A stricter five recently completed contiguous bar test passed only **80.01% H1, 80.73% H4**. Zone *existence* is not nearby structural protection.
- Only **12,559/338,065 entries (3.71%)** had a nearby, correctly sided, frozen structural invalidation reference. V11 confirmed **2,841** later breaches in the forward observation window, **zero before the actual V9 simulated exit**. V11 structural invalidation is **not an effective micro180 execution-clock exit** under present V9 holding behavior and must remain read-only.
- Original V9 average simulated hold **6.692 seconds**. Simulated stop exits **195,127 (57.72%)**, cash-0.10 harvest exits **127,247 (37.64%)**. No broker deal/price/rejection data were present to certify actual fill economics.
- Original fallback diagnostic reasons: **43,508** CHANGE_ALARM_NO_CONFIRMED_THESIS, **42,785** MIXED_STRUCTURE_INSUFFICIENT, **38,958** ENTRY_SIDE_OPPOSES_CONFIRMED_TREND, **20,040** NESTED_STRUCTURE_SIDE_MISMATCH; remaining 18,177 distributed across 11 additional subtypes. All **163,468** original fallback events accounted for, without fake classification accuracy claims.
- The specialist labels have **not** demonstrated substantial differentiation of V9 simulated stop frequencies: large groups are commonly near **57–59%** stop exits. Merely assigning new names is not evidence of predictive advantage.

## Counterfactual subsequent price paths — be precise about clocks

The independent research-only 180-second trajectory observes original quotes **after** simulated entry and frequently **after** V9 has already exited. Quote-side liquidation prices relative to entry execution prices produced:
- At ~15 seconds: **329,620/338,065** quote-close marks, mean **-$0.2021/oz**, positive **37.89%**.
- At ~60 seconds: **306,931/338,065** quote-close marks, mean **-$0.1988/oz**, positive **44.02%**.
- Only **272,272 (80.54%)** trajectory tickets had complete near-180s observation; **65,595 (19.40%)** censored by quote-gap >2.5s and **198** by month-file end.
- The exact **180.0s endpoint is NOT sampled** by this research monitor because it expires tickets before the 180-second bucket. Its last prior-to-180-second observed quote averaged **-$0.1991/oz** among completed cases; not a 180s fill.
- The audit computes one-second high/low first-barrier passage **excluding the entry calendar second**, which avoids pre-entry contamination but **misses true subsecond first-passage order and fast events**. Any same-second two-sided hits are flagged ambiguous, not invented. For ±$0.30/oz, observed favorable-first/only in **88,566** trajectories, adverse-first/only in **241,006**, **4,680** same-second ambiguous, **3,813** neither. These numbers are *exploratory bucketed event flags including censored tracks*, **not validated exact-tick probabilities or trading PnL**.

## Required additional data — without buying more giant quote archives

1. **P0 broker/execution event ledger** for the current ~6.7s positions: MT5 signal/source-ordinal timestamp, decision vs request vs fill ms, requested/filled Bid/Ask, actual spread, slippage, reject/requote/retcode, broker order/deal/position IDs, deal price and commission/fee/stop reason, actual stop-filling latency. Use `OnTradeTransaction`, `DEAL_TIME_MSC`, `DEAL_PRICE`, `DEAL_COMMISSION`, `DEAL_FEE`; collect **demo/observation only**, not live or unapproved automatic orders. Without this, the 57.7% simulated stop mix cannot be attributed to actual market vs fill mechanics.
2. **P0 source-exact original ordinal-millisecond event-path analysis** (available already): 250ms / 1s / 3s / 5s / 15s / 60s post-entry *including the remainder of the entry second*, true Bid/Ask first-hit ordering and spread shocks, actual-exit-conditioned path features. These are small derived event ledgers, **not regenerated tick archives**. Source order matters for the 49,069 identical-ms adjacent quote records.
3. **P1 existing source quote-pressure signals**: Bid-only vs Ask-only event sequencing, quote update duration/intensity, spread widening, signed midprice path, multi-horizon displacement/efficiency/turning, quote-gap flags; all **quote proxies** (not traded imbalance). Pair with the 43.5k change-alarm and 39k opposed-trend fallback cases and test *incremental* discrimination using frozen, date-separated validation.
4. **P1 small official broker/session metadata**: MT5 XAUUSD contract spec, fill policy, stop/freeze levels, order reject causes, server-time ↔ UTC offset/DST, rollover and holiday calendar, FOMC/CPI/NFP events. The original feed has **88,555 gaps >2.5s** and **197 gaps >60s**; causality/censor flags are material.
5. **P2 only if source/license exists:** real DOM sizes via `MarketBookGet` if Coinexx XAUUSD provides a reliable book; optional small matched **CME GC futures trade+depth** windows aligned for spot/futures basis, expiry and timestamp. CME execution data are **not** Coinexx spot execution data; a depth-based price-impact or OFI claim requires actual book levels and events, not two quote prices. Do not fetch/purchase a mass GC futures archive on speculation.

## Scope and release law

- Source-exact source hashes and per-month frozen V9 trade COUNT parity passed; original V9/V10/V11 EA trading code unchanged. No native MT5 compile, native↔Python structural parity, live deal PnL, or untouched OOS has been completed.
- Jan–Sep 2026 has repeatedly served as development data; do not call this nine-month sample independent out-of-sample evidence. Freeze future experiments and reserve untouched later months / genuine demo forward study.
- **Keep PR #49 DRAFT**. V11 structural advice may annotate but never block/extend/close trades or change broker stop until independent later evidence and explicit owner approval.

## References

- MetaQuotes MqlTick data/flags: https://www.mql5.com/en/docs/constants/structures/mqltick
- MetaQuotes historical deals, millisecond times, actual commission: https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties
- Cont, Kukanov, Stoikov (2014), order book events and price impact: https://academic.oup.com/jfec/article-abstract/12/1/47/816163
- Frozen code: `structure_refinement_v11.py`, `structure_overlay_v11.py` (unchanged on this study)
- Local reproducibility: downloadable 29-member zipped evidence contains all nine compact monthly JSONs, full cross-tab aggregate, field audit, SHA manifest, full detailed report and exact auxiliary audit scripts, **no market data**. The full detailed report is also delivered directly with this research conversation.
