# GRID0307–GRID0311 — January original-tick $100 independent random-start survivability and profit-funded-growth experiments

**Status: UNPROMOTED RESEARCH ONLY.** Original scientific cursor J0183 remains unchanged; official V1 `FourSessionV1` has NOT integrated the experiments; owner QC PENDING; August SEALED, trading OFF. This document is an evidence locator; original source in attached archive and original governing documents are controlling.

## Original controlling authorities

- Full owner frozen V1 whitepaper: `delta-A-alpha/research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt` SHA `1b92b3c89159681a7181508de158af685cf5780c`
- Full owner-ratified conversation: https://docs.google.com/document/d/1J9d_P4ooCnNmcxPwG1F178aE4ktpkLrFclcyQPaQJ8k/edit
- Full unabridged roadmap: https://docs.google.com/document/d/1PcaksxuiayFXVW3QtKfzitARvQj6NyL4IIbGhG8K9z4/edit
- Full owner anti-summary and original-source QC law: https://docs.google.com/document/d/1eG5F76uvm9M-1JXs4LvAaTzPEurU5l4Pgj2sUUelc1o/edit
- January source-specific original law: https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit
- Owner tick/UTC/reference correction: `delta-A-alpha/research/delta_a_alpha/governance/OWNER_20261013_VERBATIM_DUKASCOPY_TICK_CANDLES_R9_REFERENCE_LOCK.md`

## Data and reference mechanics — no resets of established audits

- Exactly `9,135,062` ordered original January 2026 Dukascopy XAUUSD original Bid/Ask quotes; Google Drive file ID `1ghF2blUzJwwufFrD-P-1aS3bklGuOSHz`; original gzip SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5` independently hashed this run.
- Exact source dependency archive from GRID0300–0306 SHA256 `60295a03f9f4e2d954229f92d3f0ad7ca5992a625c9879e689ac7c5dd32b7717` embedded in this package; it includes the earlier original exact helper archives and prior source ledgers. Newly authored source scripts GRID0307–0311 are preserved separately with their actual results JSON and all logs.
- Research contract `0.01 lot=1 oz`, fee `$0.20` modeled round-trip, 250ms quote latency, `500:1` margin leverage **hypothetical, NOT verified Coinexx account specifications**. One physical fill per original tick, no lot escalation following losses; all capacity unlocks depend only on already CLOSED realized profit.
- Original signal/exit candidate universe was selected previously from January research; **it is not yet the fully endogenous `FourSessionV1` source** and is **not out-of-sample**. The original tick/quote execution root is used to perform the simulation; archived future exit prices are never used to decide current admission.
- R9 SYNTH January whole-calendar aspirational net `+$41,520.82` and `27,980` closed trades; 21 daily and 5 ISO-week targets. R9 OVERFIT six-dimension 75% teacher **NOT TESTED** in this work.

## Newly introduced owner's random start gate

Deterministic reproducible **seed 20261014**, uniform sample of **10 different dates among January's 21 UTC trading dates**:

`2026-01-05, 2026-01-06, 2026-01-13, 2026-01-14, 2026-01-16, 2026-01-20, 2026-01-21, 2026-01-26, 2026-01-27, 2026-01-30`.

Each trial resets **all account cash, original-source admission, already-paid parent/child state and loss-pause history** to a fresh `$100` account, processes only event candidates available at/after the selected date, and marks the original ticks chronologically until **January's final quote**. The first 24h mark is computed as an independent secondary test. A January 30 start has a shorter remaining research horizon; we do NOT silently change this into a fixed 30-day episode.

**Interpret the owner target as two independent gates:** (a) survival on all ten randomly sampled historical starts, and (b) reaching `$10,000` from `$100` (100× ending capital) on all ten historical starts. Full owner acceptance still also requires daily/weekly/monthly R9 SYNTH, max hourly DD, full portfolio heat, small margin capacity, OVERFIT scoring, and month-blind later-month regressions.

### GRID0307–0308 — fixed inventory & independent margin proof

| Configuration | Ten episode minimum-margin 100% ratio checks passed | Episode ending equity across starts | $10k by end-of-Jan | Total closed trades across all episodes |
|---|---:|---:|---:|---:|
| Fixed 2 simultaneous open tickets | 10/10 | $649.59 to $1,107.17 | 0/10 | 1,441 |
| Fixed 4 simultaneous open tickets | 10/10 | $765.89 to $1,700.04 | 0/10 | 2,651 |

Both had positive minimum tick equity across all ten resets under the hypothetical `500:1` research contract (minimum `$63.93` and `$47.65` respectively). The independent quote-side mark/Margin reconstruction from original 0.01-lot executable Bid/Ask matched the funded simulator's minimum and last equity to less than `1e-6` dollars for every episode.

**Not** certification: the inherited replay does not force-close actual broker positions upon a margin breach. A positive model equity or margin ratio is merely a *necessary* check, not a *sufficient* proof of actual broker survivability. Broker-dependent stopout and commission/slippage specs were not recovered. Fail closed on interpretation.

### GRID0309 — distinct profit-funded capacity mechanism

Causal capacity tiers are governed **only by realized CLOSED cash**, not open profit or future PnL. All individual fills remain fixed `0.01` lot. Additional simultaneous physical positions are possible only after earlier closes generated sufficient booked balance; permits dynamic contraction on booked losses without martingale or loss-chasing size increases.

| Earned-capacity policy | Ten margin 100% tests | Highest ending equity | Episodes >=$10k | Total closed trades |
|---|---:|---:|---:|---:|
| Conservative (2→4→8→16→32 positions with slower gates) | 10/10 | $1,306.92 | 0/10 | 1,650 |
| Balanced | 10/10 | $2,459.06 | 0/10 | 2,513 |
| Fast | **8/10** | **$10,048.76** | **1/10** | 5,492 |

**Critical counterexample:** the fast policy's impressive Jan 5 ending result does not imply 10/10 survival. The January 14 run breached the necessary margin-level floor and January 16 produced a minimum marked equity of **−$436.02**. An equity-negative path cannot be portrayed as survivable simply because its fixed historical trades subsequently closed at profit; with actual stopout it would have changed the path.

### GRID0310 — independent tighter admission-margin frontier

No entry is allowed unless new modeled margin after entry fits a fixed fraction of the **current observed post-fill marked equity**. This is a new *complementary L7 risk guard* to realized-profit-earned capacity and source-family inventory limits. It does not pretend to forcibly liquidate existing positions.

| Maximum new margin / post-fill equity | Ten 100% modeled margin checks | Ten 200% modeled margin checks | Highest ending equity | $10k by Jan end | First 24h $10k |
|---|---:|---:|---:|---:|---:|
| 20% | **10/10** | 9/10 | $8,512.78 | 0/10 | 0/10 |
| 25% | 8/10 | 8/10 | $9,944.74 | 0/10 | 0/10 |
| 30% | 8/10 | 8/10 | **$10,048.76** | 1/10 | 0/10 |
| 35% | 8/10 | 8/10 | **$10,048.76** | 1/10 | 0/10 |

The Jan 5 result at 30–35% is **one source-identity start**, not two independent successes: `1,548` closed trades, min marked equity `$77.158`, minimum assumed 500:1 margin level ~`215.2%`, `$10,048.763` ending mark. That high-velocity modeled growth occurred over the **remainder of January**, not in a single trading day: its first-24h equity was only `$141.169`.

**The joint owner $100 gate has NOT been met:** No tested policy both passes 10/10 necessary margin and reaches $10k for all ten seeded starts. This is a strict failure of the full owner target, even though 10/10 modeled necessary margin checks or a single 100× modeled trajectory can occur separately.

### GRID0311 independent QC

**62/62 checks passed:** source gzip SHA; exact predecessor archive SHA; randomized distinct seed reproducibility; all 120 saved original-tick episode counts; full JSON margin/cash/trade-count recomputation; 24h no 100× profits; complete fail-closed target boundary; no double-counting same January 5 result. Independent rolling quote marks for GRID0308–0310 additionally agree exactly with portfolio min/last equity by `1e-6` USD. No owner QC claim, no deployment.

## New research from public community mechanisms (reconstructible, not performance evidence)

- Chinese MQL5 `CEnhancedRiskManager`: balance-vs-equity drawdown modes, after-mark dynamic risk and entry admission, portfolio kill-switch. https://www.mql5.com/zh/articles/18918
- Japanese MetaQuotes materials: minimum margin-level sentinel, per-position hard exit vs basket-wide equity kill switch, spread/slippage gate and lot/margin budget. https://www.mql5.com/ja/market/product/187004 and https://www.mql5.com/ja/articles/19655
- Korean MQL5 strategy stress methodology: change margin/leverage parameters under simulated stopout, verify close behavior, not just cash at exit. https://www.mql5.com/ko/articles/22391
- English Reddit quant community: one portfolio heat budget across correlated strategies, point-in-time tests and genuine out-of-sample evaluation. https://www.reddit.com/r/algotrading/comments/1rtwnfm/approaches_to_risk_management_and_order_size/ and https://www.reddit.com/r/algotrading/comments/1x2owmo/i_backtested_100_retail_trading_strategies_700/

These are design inspirations, **NOT** evidence of XAUUSD profit, do not import any proprietary opaque algorithm, and none overrides frozen owner V1 law. MQL5 code may be tested only after Python source acceptance and explicit owner build authorization.

## Concrete source-integrated next engineering unit

1. Rebuild small-account physically *liquidatable* L7: live portfolio Bid/Ask mark, broker-calibrated dynamic margin, server stopout and forced liquidation at next actual executable quote; cost/spread/slippage sensitivity; fair-loss debit of losing positions and relock all dependent Watchdog genealogies.
2. Test the same 10 deterministic starts under several **broker-realistic** margin/leverage/stopout assumptions, plus disjoint fresh random draws held out from optimization; do not select the highest-profit trajectory after observing dates.
3. Restore source-native initial scouts and session/HTF micro-opportunity density including Jan W01 without replacing or hardcoding date-specific selectors; initial $100 cannot safely buy 256 simultaneous 1-oz gold exposures. Keep fixed .01 lot, no martingale.
4. Test new complementary causal improvement on full 9,135,062 ticks; measure 24h, each UTC hour DD, all January R9 daily/weekly/monthly economics and trade velocity, six separate R9 OVERFIT offline dimensions, then February–July month-blind replay.
5. Append success and falsifications with complete original source/settings/results hash in GitHub and Jan Drive. Keep existing GRID0272–0306 successful/negative archival evidence immutable. Owner QC and official J0183 remain unchanged.

**Do not claim $100→$10k in 10/10 or certified 100% survivability, and do not promote engine.**


---
## Source-exact durable attachments (verified connector URLs)
- Original runnable archive with source/JSON/ancestor code/QC: https://drive.google.com/file/d/18SFVWIQrXE6eff5qdldpPPUumN_b1Y8v/view
- Original archive SHA256: `f68af9c5bdda952a1ebb2fec2a5ea60b8c4975859cabaade86dccd8cdb67d9ef`
- Exact five new Python sources (committed individually): https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/delta-A-alpha/research/delta_a_alpha/monthly_progressive_roadmap_20261013/2026-01_JANUARY/experiments/GRID0307_0311_SOURCE_CODE
- Same original research report in January Google Drive: https://drive.google.com/file/d/17y7GYgBJPugyjSn4riZbCO-2tRLdSwfU/view
- Explicitly NOT promoted, NOT broker-certified, NOT owner-QC-accepted; J0183 and active engine untouched.
