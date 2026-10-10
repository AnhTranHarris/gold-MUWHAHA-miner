# Delta-A-alpha clean V1 | Four-session whole-vertical research cycle 003

2026-10-10 | **NO PROMOTED TRADING EDGE: initial owner criteria FAILED**

## Scope, source discipline and engineering result

One clean V1 core; original R9 SYNTH/REAL and Dukascopy JAN/FEB .csv.gz protected and read-only. No contaminated prior JAN/FEB mechanism, files or earlier economics were imported. The pre-existing clean Cycle 001 UTC tick and completed-bar kernel was the sole source base. The new research material below is original to this cycle.

A fresh integrated research prototype implements one tick-rooted, shared capital path from L0 to L7 with four declarative session profiles; quality routing cannot be bypassed by L1 or L2. Distinct broker-server clock calibration (3 paired real UTC observations required) converts any trusted broker wall clock to UTC and then each actual local market timezone; it rejects stale/mismatched samples, rather than guessing server DST from MetaTrader Strategy Tester. MT5 Python tick time_msc is already UTC and is not double shifted. Session hours are **unverified configurable hypotheses**, not Coinexx certified trading hours.

## Candidate mechanisms — FOUR desk-conditioned approaches per layer (all RESEARCH HYPOTHESES)

| Layer | Sydney | Tokyo | London | New York |
|---|---|---|---|---|
| L1 opportunity | open/close rotational & spread-aware | Tokyo local opening range and Sydney overlap | Asia-range transition to London volatility | London-NY overlap / US impulse / later NY phase |
| L2 opportunity + volume | H4 envelope + H1 location; M15 compression M5 rejection | H4 context H1 range M15 phase M5 transfer | H4 direction H1 structure M15 pullback M5 transfer | H4 environment H1 alignment M15 phase M5 transfer |
| L3 grid opportunity refinement | low-density rotation after M5 excursion | opening-range break/retest only after completion | Asia sweep/continuation into directional microgrid | pullback/retest after high-liquidity impulse |
| L4 Watchdog/regime quality | spread-qualified rotational state | activity+spread regime | trend activity confirmed not just clock | fast tape plus spread and event control |
| L5 trend quality | failed-edge reclaim quality | H1/M15 compatible reversal-or-continuation | HTF continuation/pullback capture | trend-in-trend momentum quality |
| L6 failure recovery management | early exit and state-aware reassessment | failed ignition exit, no generic hedge | structure invalidation and no-loss scaling | stop warning + bounded directional re-evaluation |
| L7 single global capital governor profile | low one-position heat | one-position heat | overlap-aware heat cap | volatility-limited shared heat |

**Not four separate robots**: these are four configurations of one mutually constrained vertical owner; in overlaps two desks can propose, but the single L7 account arbitrates and enforces one physical order per tick, no multiplying shadow profits. L4 earns renewal only from realized cashflows; L5 uses structurally distinct H4/H1/M15/M5 roles; L6 can issue a bounded corrective *proposal* only after observed failure and fresh full-chain confirmation. All sessions remain rejectable by L7.

## Fresh original Jan/Feb real-tick session research

16,673,401 raw quote records total; hourly timezone-shift correct via IANA; all five-minute labels evaluated from the next completed interval but NEVER used for generating predictions. Quote update intensity is **not centralized traded volume**.

| Desk | Month | Base next 5m mean XAUUSD range ($) | Activity-gate range lift | Activity selection | Activity+spread range lift | Prior baseline mean spread ($) |
|---|---:|---:|---:|---:|---:|---:|
| SYDNEY | 2026-01 | 6.9600 | +13.36% | 47.47% | -9.72% | 0.8021 |
| SYDNEY | 2026-02 | 10.0067 | +18.14% | 46.23% | -0.33% | 1.1446 |
| TOKYO | 2026-01 | 6.6896 | +14.49% | 47.30% | +1.47% | 0.7518 |
| TOKYO | 2026-02 | 9.6338 | +11.99% | 45.86% | -3.86% | 1.0478 |
| LONDON | 2026-01 | 7.8396 | +15.22% | 47.65% | -4.68% | 0.7257 |
| LONDON | 2026-02 | 9.9219 | +12.49% | 45.25% | -5.69% | 0.8863 |
| NEW_YORK | 2026-01 | 9.0590 | +15.56% | 44.17% | -3.34% | 0.7632 |
| NEW_YORK | 2026-02 | 10.0216 | +10.68% | 45.52% | -3.11% | 0.8541 |

Five tested, reconstructible as-of conditions per desk: ALL, ACTIVITY, ACTIVITY_SPREAD, EXPANSION and COMPRESSION. Activity increased *future price range* across all four desk buckets both months, but the strict activity+spread combination often **reduced** subsequent opportunity range. This is not evidence of positive net returns, and it does not establish a unique optimum.

## Fully routed, L7 broker-hypothetical economic testing (partial history only)

Fixed 0.01 lot, hypothetical 100 oz/lot and 1:500 leverage (NOT Coinexx verified), $300 start, $0.20 roundtrip commission, real Dukascopy Bid/Ask executions delayed by 250 or 1000 ms; $0.01 slippage not invented. Fill may occur ONLY on a later quote at or after intended broker-arrival timestamp, with first real Bid/Ask and guard. The future quotes were not used in source generation.

| Source slice | Last observed quote UTC | Tick count | Lag | L3 proposals | Full-chain qualified | Funded closes | Net realized USD | Gross loss USD | PF | Max quote-equity DD USD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-01-05 (01) | 2026-01-06T02:33:08.587000Z | 450,000 | 1000ms | 744 | 631 | 74 | -103.57 | -140.10 | 0.26077243171093784 | 109.70 |
| 2026-01-05 (01) | 2026-01-06T02:33:08.587000Z | 450,000 | 250ms | 744 | 632 | 81 | -102.97 | -144.41 | 0.2869449003192333 | 112.78 |
| 2026-01-12 (01) | not recorded in early independent slice | 450,000 | 250ms | 1,221 | 1,043 | 84 | -106.59 | -132.76 | 0.19713769207590948 | 107.67 |
| 2026-02-05 (02) | 2026-02-05T15:04:46.399000Z | 450,000 | 1000ms | 1,409 | 797 | 6 | -5.58 | -10.15 | 0.4496895634177843 | 14.58 |
| 2026-02-05 (02) | 2026-02-05T15:04:46.399000Z | 450,000 | 250ms | 1,409 | 810 | 4 | +1.50 | -6.64 | 1.2258550549948883 | 6.55 |
| 2026-02-12 (02) | not recorded in early independent slice | 450,000 | 250ms | 1,140 | 915 | 8 | -3.63 | -11.95 | 0.6961071578065746 | 11.09 |

**Rejected for economic promotion**. January slices lost >$100 out of $300 and activated capital protection. February slices produced too few fills; one +$1.50 4-trade sample is not statistically meaningful or eligible for promotion. The 75%-of-R9 SYNTH **daily** qualified opportunity floor was NOT demonstrated; none of these partial-day slices may be treated as a full trading-day or full-month certification. The 175% monthly volume ceiling was not meaningful on partial slices either. No true Coinexx order confirmations or verified contract/margin data were supplied; no MT5 tester or live performance is claimed.

## What has been implemented vs missing certification

- **Implemented/tests passed:** L0 ordered real quote chronology; L1 UTC master and distinct civil-session clocks, tested US/UK/Sydney DST, offset +2→+3 self-calibration with stale/ambiguous rejection; L2 completed H4/H1/M15/M5 role separation; L3 four desk microgrid candidates; L4 realized-result Watchdog relock/renewal eligibility; L5 independent structural quality veto; L6 early warning/limited correction proposal; L7 one quote-aware illustrative funded ledger, margin guard, max-open, fixed 0.01 lots, trailing stop, margin/rejection reasons and no duplicate funded order on one tick; latency fills at future executable quote. 18/18 deterministic tests passed locally.
- **Still incomplete:** calibrated real Coinexx broker trade schedule, actual leverage/margin/contract specifications, measured execution latency and rejection profiles, reliable region-event calendar feed, physically accurate MT5 deal/commission and spread parity, full monthly validated objective performance, genuine 75% R9 daily opportunity coverage, statistical robustness across remaining months and walk-forward demonstration. The session "best" profiles have not been established.
- **Architecture classification:** full L0–L7 *research-path prototype* now implemented; not a proven "high-volume HTF/scalping monster" and not ready for MT5 deployment. No safe performance shortcut is available; do not claim to have met owner acceptance criteria.

## Reconstructible reference ideas (NOT proof of profitability)

- MT5 trade/quote session and server clock: https://www.mql5.com/en/book/automation/symbols/symbols_sessions
- MT5 Python ticks are UTC: https://www.mql5.com/en/docs/python_metatrader5/mt5copyticksfrom_py
- MT5 tester TimeGMT limitation: https://www.metatrader5.com/en/terminal/help/algotrading/testing_features
- TradingView IANA sessions and DST: https://www.tradingview.com/support/solutions/43000729030-trading-sessions/
- Chinese MetaQuotes per-session spread/time analysis: https://www.mql5.com/zh/articles/18821
- Chinese MetaQuotes gold London opening range idea: https://www.mql5.com/zh/code/75586
- Japanese TradingView ORB and session idea: https://jp.tradingview.com/scripts/orb/
- Japanese TradingView open session markers: https://jp.tradingview.com/script/BSlvprMr-Session-Open-Tines-Tokyo-London-NY-most-recent-ones-only/
- TradingView completed opening-range breakout / retrace hypothesis: https://www.tradingview.com/script/GImmIKBy-Open-Range-Breakout/
- TradingView session-average range measurement: https://www.tradingview.com/script/bnJ1taBu-Average-Session-Range/
- MQL5 event coalescing and fill uncertainty: https://www.mql5.com/en/docs/event_handlers/ontick
- MT5 OrderCalcMargin broker-specific margin: https://www.mql5.com/en/docs/trading/OrderCalcMargin

## Protected sources and revision guard

Raw Dukascopy XAUUSD January–August datasets and original R9 Gamma HybridGate SYNTH/REAL reports remain byte-unchanged. Original whitepaper, October10 owner addenda, and clean Cycle001 kernel remain source authority. No old contaminated JAN/FEB research mechanism is imported. Repo source paths are new \`research/delta_a_alpha/implementation/v1_session_broker_clock.py\` and \`v1_four_session_architecture.py\` alongside existing clean \`v1_vertical_grid.py\`. Do not reactivate deleted engines.
