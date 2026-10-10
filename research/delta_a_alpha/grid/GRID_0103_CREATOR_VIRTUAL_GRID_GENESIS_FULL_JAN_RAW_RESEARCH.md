# GRID-0103 — independent creator-grid GENESIS research, BEFORE Vertical Grid trading

**Status:** JANUARY 2026 FULL RAW-TICK SHADOW OPPORTUNITY RESEARCH DONE; NO TRADE ENGINE, NO ACCEPTED EDGE.
**Owner interpretation:** MegaJoctan/OmegaFX H1 rolling-extrema contra-grid is the master opportunity-generating *concept*, not direct trades. Preserve historical Martingale's **level-by-level sequencing and next-anchor memory**, but absolutely no loss-dependent volume, scaling, unbounded inventory or no-stop funded averaging. No retired R9/old Jan-Feb model components are imported.

## Exact external original and source lessons
- Creator video: https://youtu.be/4WQEoQxsJMc
- Creator actual GitHub: https://github.com/MegaJoctan/omegafx-youtube-shared-files/tree/main/Python%20Grid%20Bot
- Source grid_bot.py blob `1d5efa140b363941e7360bd0ae85ac7e04d0ecaa`: 48 H1 bars; buy on gap below rolling high, sell on gap above rolling low; later gap anchor = last side's open position. LIVE script `count_positions` and `last_position` call missing required `which_mt5` arg. In-sample US500 1m OHLC backtest and later 2x Martingale are NOT XAUUSD real-tick accuracy evidence.
- Independent dynamic spacing precedent https://www.tradingview.com/script/KtEbldM6-Dynamic-Grid-BOT-Engine/ ; Japanese MQL5 martingale tail-risk article https://www.mql5.com/ja/articles/8390 ; inventory risk model https://www.mql5.com/en/articles/23571 . These are reconstructible mechanism ideas, NOT evidence of edge.

## Scope of new standalone clean source research
Source used read-only: `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`, **SHA256 d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5**, 9,135,062 original ordered Bid/Ask ticks. Prior contaminated Jan/Feb derivative models untouched and NOT USED. R9 SYNTH January protected original completed entry count=**27,980** across 21 trading days; this is *volume reference only*, NOT direction truth.

Primary source-independent Python shadow scanner uses:
1. Source-**inspired** completed-H1 48-bar rolling extrema boundary CROSSING events. It is NOT source's open-position semantics.
2. **VIRTUAL INDEPENDENT ladder**, tracking price gap crossing, consecutive same-direction virtual depth, current timestamp, Bid/Ask, contrarian hypothesis side and alternative continuation hypothesis. A virtual rung is NOT a funded order. No more than one event per observed tick, even if it jumps multiple levels.
3. Optional cooldown/cadence: suppress repeat event reporting without physical position exposure. Optional adaptive spacing from prior **completed** one-minute ranges; current forming bar not exposed.
4. Record actual native spread-to-grid cost pressure, as-of UTC session timestamps. Subsequent future quote-side marks are strictly *evaluation only*.
5. ZERO MT5 requests, lot sizing, positions, trades, PnL, exit optimizer or automatic L1-L7 quality admission.
7 deterministic unit tests passed locally for gap steps, virtual depth, one-per-tick, cooldown, completed-H1 non-lookahead, completed-minute volatility, and no broker execution calls.

## Full January SOURCE-only measured event counts
| Hypothesis | Raw shadow crossing events |
|---|---:|
| 48 completed-H1 boundary crossings / $1.00 | 1,302 |
| $1.00 virtual continuous | 138,620 |
| $0.50 virtual continuous | 378,387 |
| $0.75 virtual /1s cooldown | 152,724 |
| completed-M1 volatility-adaptive no cooldown | 176,855 |
| $0.75 virtual /5s | 92,709 |
| **$0.75 virtual /15s** | **54,210** |
| $0.75 virtual /30s | 35,200 |
| $1.00 virtual /15s | 43,430 |
| $0.50 virtual /30s | 42,182 |
| completed-M1 adaptive /15s | 64,907 |

**Provisional 21/21 daily shadow-event counts above 75% of R9 daily completed count** for all six throttled variants, *only* when assuming report-time UTC+2 in January. Broker clock not independently certified; and these are NOT funded or quality-qualified opportunities and do NOT satisfy owner final 75% opportunity-QUALITY rule. Monthly 175% maximum is for completed funded trades, not raw events.

## Critical direction and latency falsification
$0.75/15s source-native spread median **$0.696**, >$0.75 full grid gap on **37.316%** of events. Quote-side markout positive at 30s: **28.999% proposed reversal**, **29.025% opposite continuation**; at 120s: **38.923% versus 38.144%**, no proven directional edge. No commission or slippage, no actual fills; NOT PnL and NOT position win rate.
Local 250ms nominal observation lag: **12.389%** of events moved >=half-gap in next observed quote; at 1000ms **24.829%**. NOT measured execution latency or broker fill.
52k+ event supply does NOT imply those signals are safely executable or directionally correct. Avoid resurrecting creator physical averaging or claims of 95% directional accuracy.

## Four market-desk opportunity tagging (NOT L1 activation)
$0.75/15s stage-zero tape: London-only 9,666, London/NY overlap 12,681, NY-only 11,283; Sydney-only 2,397, Sydney/Tokyo overlap 13,718, Tokyo-only 4,465. Zone-aware local clock *diagnostics*, not verified broker session schedules or approved stage-zero session parameters.

## Scientific verdict
**RETAIN ONLY AS UNFUNDED CANDIDATE:** virtual multi-rung crossing/event clock, clock-aware geometry, 15s/5s/30s cadence hypotheses, both possible action directions as uncommitted candidate fields, native spread and quote-age warnings, depth and session tags.
**REJECT:** source-style unrestricted position accumulation, Martingale multiplier, no-stop funded grid, assuming all raw level crossings are profitable, R9 BUY/SELL labels as truth, optimized Jan-only spacing promoted without blind period tests.
**DO NOT MODIFY** existing live/research V1 engine or R9/Dukascopy inputs under GRID-0103. Next step should test a separately held-out period and then pass shadow candidates through the completed, causally qualified **full** L1–L7 funnel; final direction remains to be determined by downstream quality, not grid source alone.

## Reproducible artifact provenance
Source, six testable research scripts, seven passing unit tests, full JSON metrics, compressed event tapes and full narrative report were generated in the current conversation as `GRID_0103_SOURCE_TESTS_FULL_JANUARY_RESEARCH.zip`, **ZIP SHA256 `12ec7c6c34d74eba0e45ffc7f87cee59beda566fe138228a47a807f113c0db6d`** (original raw GZ intentionally excluded). A user-facing download link is in the corresponding ChatGPT response. GitHub checkpoint intentionally registers exact source/results semantics rather than pretending uncommitted candidate engine exists.

Original whitepaper and owner correction remain higher authority: `research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt`; `research/delta_a_alpha/governance/OWNER_20261010_MASTER_GRID_EVENT_STRATEGY_LINEAGE_CORRECTION.md`.
