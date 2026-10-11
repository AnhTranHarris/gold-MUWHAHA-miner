# GRID0134–0139 — Six linked original-XAUUSD-grid research cycles: session geometry vs market-state experts

**Date:** 2026-10-10 (America/Chicago). **Branch:** existing `delta-A-alpha`. **Scientific parent:** J0133; original V1 owner architecture frozen. **Research only, not an MT5 trading-system promotion.** Stage L1–L7 remains locked, `trading_enabled=false`, no Martingale or loss-dependent lots, August 2026 sealed.

## Owner's scientific question

Are the disappointing hourly outcomes relative to the R9 SYNTH aspiration attributable to pooling structurally distinct Sydney/Tokyo/London/New York gold auction behaviors into one universal grid, and could complementary session-aware, market-condition-owned sub-grids restore **monthly -> daily -> weekly -> hourly** consistency at high executable opportunity velocity?

*Tested hypothesis, not assumed answer.* Keep the authoritative original creator-derived GRID0108 K2/K4 virtual geometry (`gap=max($0.75,1.5×EWMA prior spread)`, original 7-second cooldown), the GRID0109 **3,332 original weekday UTC-hour denominator / 1,389 K4-capacity weak hours**, original GRID0111 T1 quote entry, and every accepted unsigned historical finding. R9 SYNTH supplies an external target, **not** a teacher of BUY/SELL signs. The 75% R9 SYNTH same-day qualified completed-trade floor remains **unmeasured** by these quote-based candidates. No claimed R9 hourly equivalence or funded PnL.

**Input history:** Jan–Jul original Dukascopy 57,527,562 source Bid/Ask observations, original derived 279,486 quote-trigger T1 event tape, GRID0124/J0121 frozen Jan–Apr HGB7 600-second model forecast tape; all historical months previously inspected. The May–July comparison is chronological but **not pristine untouched holdout**. Native quote exits charge real source opposing Bid/Ask and a hypothetical $0.02/oz roundtrip fee once; broker slippage still modeled separately. No exchange depth feed exists in this quote source. Source quote values are not broker fill guarantees. Frozen owner scalp lifecycle is approximately 2–4 minutes; 10-minute models are research probes, not lifecycle acceptance.

## GRID0134 — Exact all-hour DST session audit

Session diagnostic windows: Europe/London 08–17 **local London clock**, America/New_York 08–17 local NY clock, Tokyo 09–18 local, Sydney 09–17 local; London–NY overlap takes precedence. These are reproducible **approximate center activity windows**, not the broker's literal XAUUSD auction opens. Standard-library `zoneinfo` handles real DST dates. The region label is descriptive, not a live hour-avoidance policy.

| UTC-hour assigned session | Original eligible hours | Original K4 weak hours | Weak share | Original observed T1 candidates | Original weak hours receiving ≥5 broad original T1 quotes | Weak hours receiving ≥5 G1 medium/long forecast-consensus quotes |
|---|---:|---:|---:|---:|---:|---:|
| Tokyo | 1,106 | 466 | 42.1% | 77,926 | 460 | 12 |
| London | 731 | 309 | 42.3% | 53,280 | 307 | 6 |
| New York | 700 | 270 | 38.6% | 48,944 | 257 | 8 |
| London–New York overlap | 615 | 260 | 42.3% | 88,911 | 260 | 26 |
| Sydney | 120 | 50 | 41.7% | 5,323 | 45 | 0 |
| Transition | 60 | 34 | 56.7% | 1,656 | 32 | 1 |
| **Total** | **3,332** | **1,389** | **41.7%** | **276,040 within reference hours** | **1,361 within reference hours** | **53** |

The poor hours are spread across **all** main regional sessions and do not admit a simple 'avoid Asia' solution. Their share changes sharply by month; e.g. original July Tokyo weak share ~53% and Sydney ~91%, while February Tokyo ~32%. At the very restrictive causal model agreement gate, raw predictions no longer serve most weak hours.

## GRID0135 — Prior causal grid-event auction geometry and competing original specialist sleeves

First recalculate 900s and 3600s **previous-grid-event-only** high/low from genuinely earlier T1 source quote observations, not future ticks, current event, broker volume, or genuine continuous tick session range. Preregistered breakout/false-break fade, 300/900s counter-pullback, frozen medium/long HGB7 forecast agreement, session shadow mix, and clock-independent state mix; fixed 120/600s source opposing quote exits with FIFO caps4/8. **64 methods × 7 months = 448 method-month evaluations**.

- Pre-session 900/3600s breakout continuation and narrow auction-boundary reversal yielded negative source Bid/Ask expectancy in **all seven** source months under the tested horizons. 3600s boundary fade G0.25 held 6,606 selected source quote outcomes at 600s cap4 with mean **−$0.478/oz**; no route certified positive. Do not hide that result by selecting only the most favorable hour.
- The predeclared London breakout / Asia fade / overlap pullback / New York quote-consensus **session shadow router** earned **−$0.780/oz**, 600-second four-slot pooled, negative every month. The clock-free complementary source-state router also negative **−$0.743/oz** at 600 seconds four-slot, negative every month; it supported **1,182** previous weak hours but was not profitable.
- Cost-gated 600/1800s HGB7 forecast agreement, 600s four-slot, entry source quote G1.0, generated **+3.346/oz**, 1,766 quote outcomes, 7/7 positive month means—**but only 40 of 1,389 original weak hours supported**. This is the prior narrow J0127-style source-model lead, not a new economical dense sleeve.

**Conclusion:** Simple session-labelled ORB or fade after original grid events is not enough. Session-specific opportunity production needs genuinely distinct causal state transitions, cost gates and structural permissions; not merely a UTC clock switch.

## GRID0136 — Is the clock more useful than current economic price state?

Freeze a HGB7 global Jan–Apr model, separately fit HGB7 source-quote 600s midpoint movement models on Jan–Apr by five DST-aware session categories (Tokyo, London, NY, overlap, other), and by four causal **source spread × past-300s displacement** groups; use exactly original J0121 entry-only features, without future labels or date/hour/month in market-state features. Sampled 0.5,1.0,1.5 source spread+fee gates, cap4/8, real later quote-side exit. **18 methods × 7 = 126 method-months**.

At the common **G1, 600s, cap4** gate:

| Month | Global Jan–Apr forecaster | Session-specialist forecaster | Clock-free source-state specialist |
|---|---:|---:|---:|
| Jan | +6.298 | +4.052 | +3.132 |
| Feb | +2.508 | +2.734 | +4.997 |
| Mar | +2.952 | +1.905 | +3.318 |
| Apr | +0.739 | +0.179 | +1.180 |
| May | +0.894 | −0.598 | −1.041 |
| Jun | −0.705 | −0.574 | +0.076 |
| Jul | +0.647 | −0.840 | −0.340 |

The historical 4 separate regional expert models **did not transfer profitably May–Jul** even though their overall source quote sample density increased. Clock-free economic-regime training modestly salvaged June but failed May/July. Clock identity alone is not demonstrated as useful execution permission.

## GRID0137–0138 — Causal expert consensus versus disagreement, with entry-known cost

J0137: six preregistered sign-owner combinations of global, local-session and source-state 600s forecasts, three original-spread gates, caps4/8: **36 ×7=252 method-months**. Two-agree G1.5 cap8 had +$0.082/oz weighted May–July quote mean (not stress-resilient), 85 original weak supported hours over all months, 6/7 month means positive.

J0138: seven preregistered ownership mechanisms using expected after-cost forecast surpluses, including a **session-conditioned agreement** rule: during London/overlap require the global and DST-session model predicted BUY/SELL signs agree; outside those windows require global and clock-free market-state model signs agree. Select the minimum agreed forecast magnitude at the current T1, require >=1.25×(observed source spread+0.02), enter own sign, cap eight 600s virtual slots. **28 ×7=196 method-months**. This shadow rule yielded +$6.444/oz weighted average across seven source months and +$0.408/oz May–July, all 7/7 month means positive **before simulated slippage**, but supports only **56/1,389 historical weak hours** and has a historical worst adverse quote near −$129.55/oz. No physical account heat/governor or broker transaction reality certified.

This is a **reconstructible conditional directional research lead**, not proof that time-of-day routing solves weak hourly behavior or any case for widening live session participation.

## GRID0139 — Independent genuine delayed Bid/Ask entry stress of frozen GRID0138 session rule

Freeze that exact rule and sign; source original `T1` quote tick, actual source entry quote at first tick **at or after +0ms, +250ms, or +1000ms**, opposite Bid/Ask actual quote liquidation after 120/240/600s, no hindsight exits, fee $0.02 once, modelled additional $0.25/trade cost. Conservative FIFO time admission recalculated at *predeclared* horizons for cap4/8. **18 ×7=126 method-months**. Original unlagged 600s/8slot source mean matches J0138 month-by-month to within source integer rounding 0.002 USD/oz; regression test passed.

| Month | Actual +1000ms 600s eight-slot mean quote net, USD/oz | Actual +1000ms 240s eight-slot mean quote net, USD/oz | 600s eight-slot delayed quote count |
|---|---:|---:|---:|
| Jan | +11.089 | +5.206 | 491 |
| Feb | +7.842 | +3.496 | 577 |
| Mar | +5.905 | +1.081 | 769 |
| Apr | +1.849 | +1.063 | 192 |
| May | +0.697 | +1.004 | 82 |
| Jun | +0.075 | +0.734 | 156 |
| Jul | +0.261 | **−0.441** | 61 |

For the **600s** original quoted outcomes with delayed entry, all seven monthly means remain above zero before the extra stress; **June becomes negative after a further $0.25/quote assumption** (June −$0.175/oz). The 240s shorter-horizon rule does not earn positive July even before extra stress. Four-slot configurations are weaker and generally fail later-month consistency. This signal does not prove short-term (<5min) profitability, wide daily/hours coverage, gross loss/stop containment, or safety with a $100–$300 research account. Real broker latencies/spreads differ from the Dukascopy source. No stop or protective funded exit has been certified.

## Quantitative scope and forward path

- **Historical reference:** all 3,332 GRID0109 original eligible hours, 1,389 originally weak hours and original GRID0108 daily unsigned K4 capacity improvement retain their original interpretation. These new source quote signed tests do not override it.
- **This research batch:** 448 +126+252+196+126 = **1,148 method-month evaluations**, plus seven-month original DST hourly diagnostic. New source-native causal/regression checks: 8/8 pass; complete Jan–Jul hourly, monthly, daily stage panels, weekly GRID0136 report and source scripts saved with SHA manifest.
- **Evidence:** Jan-Apr fitted forecasters vs May-Jul previously studied chronological sequence; no unexamined holdout, data-snooping from many variants remains a material risk. No promotional validation, funded account profit factor, equity drawdown, realized broker fills or overlap heat numbers from source quote marks.
- **Direct R9 SYNTH per-hour/day/week/month comparison:** **not established** by this batch because complete identical-time R9 SYNTH closed-order schedule, physical qualified lifecycle, spread source and global capital governor are not yet reconciled on the same timeline. Never equate J0134 GRID unsigned hour wins or J0139 sparse quote marks with R9 SYNTH actual funded closed trades. Owner 75% same-day qualified executable opportunity floor currently fails demonstration.
- **Next falsifiable research question (GRID0140):** true quote-native, **completed prior-auction** session highs/lows (rather than grid-event extrema), conditional compression-to-displacement transitions, distinct Asia rotation versus London impulsive breakout versus overlap structural reversal and separate NY risk decay; overlay original frozen J0139 sign lead, source quote-cost and global 4-slot capacity. Diagnose why 1,389 weak hours remain weak rather than deleting them. Such shadow research **does not activate owner L1/HTF architecture or modify the EA**. Preserve original historical source and stage0 genesis; do not use an oracle or import unverified community profit statements.

## Public reconstructible ideas (not external validation)

- Original creator grid: https://github.com/MegaJoctan/omegafx-youtube-shared-files/tree/main/Python%20Grid%20Bot
- MetaQuotes session-aware price/spread analysis (Chinese/English): https://www.mql5.com/zh/articles/18821 and https://www.mql5.com/en/articles/18821
- MetaQuotes DST and broker-clock calibration: https://www.mql5.com/en/articles/16171
- MQL5 Gold London breakout using completed Asia range and OCO, not copied as an approved system: https://www.mql5.com/en/code/75586
- Japanese MQL5 London breakout implementation: https://www.mql5.com/ja/articles/18867
- TradingView open-source session breakout-and-sweep semantics (concept only): https://www.tradingview.com/script/yl96pAod-Session-Breakout-Context/

**Scientific disposition:** preserve the useful source-model agreement lead and the possible clock/market-state interaction **in research only**. Reject the simple fixed-session routing and insufficient after-slippage / insufficient hourly-density candidate as deployable. Do not claim the user's full-system performance target is achieved.
