# BETA 009 — January entry/scalping parallel quant research (no qualifying breakthrough)

**Status:** TWO COMPLETED JANUARY EXPLORATORY DIRECT-ORIGINAL-TICK BATCHES, 32 INDIVIDUAL CAUSAL ENTRY SCENARIOS, no promoted candidate and no MT5 code authorization. Not a professional live fill certificate. No August read.


## 1. Owner-defined question and promotion discipline

Use the read-only R9 REAL strategy as a historical failed-performance starting/control idea and R9 SYNTH/OVERFIT as a hindsight oracle/capacity map. Seek earlier, more accurate and more plentiful profitable entries using one or more strategies; **hold/exit preserved** during these controlled ENTRY tests. Start with January; expand to February–July only for valid ≥10% material improvement that also survives predefined profitability, winning-count/trade-retention, gross-loss, drawdown and causality gates. No discovered positive qualifying result in the January tests below, so no Jan–Jul forward expansion or MQL5 code is authorized.

**Baseline distinction:** R9 REAL is a Coinexx seven-month historical source report (236,647 trades, 102,385 winners, -$50,285.28 net). R9 SYNTH generated model is an untradeable target (219,342 trades, 191,136 winners, +$309,122.85 net). The Python R9-style reconstructed full-January control is a **different Dukascopy feed and a simplified broker model**, not the same executed Coinexx EA, and never a valid cross-feed percentage baseline. Current `approved_beta_ea=null`.

## 2. Full-month source integrity — now independently completed

- Full original Jan source `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5` (compressed SHA match); **9,135,062 original ordered individual Bid/Ask quotes**; gzip decoded to EOF with native CRC verified, no timestamp descent, crossed quote, negative volume or nonpositive price. 26 observed UTC date buckets (market closed on some dates).

- Mean observed **Ask−Bid = $0.841/oz**; only **0.0476%** of quote events had spread ≤$0.25/oz, **5.78%** ≤$0.50, and **84.42%** ≤$1.00. These observed Dukascopy costs are NOT the original Coinexx spread distribution. R9 `InpMaxSpreadPoints=25` maps to $0.25 only if `_Point=$0.01`; broker point size has not been independently verified. Using numeric points as dollars without broker specification would be a scientific error.

- Precise 17-layer context bar cache certification remains incomplete. These pilots performed *direct original quote-event replays* using only causally observed completed S1 and M5 features; no cached candle data was used and no raw tick was fabricated. Local `BETA_009_JAN_QUOTES_LOCAL_ONLY.npy` was an ephemeral 146 MB staging mirror, not uploaded or marketed as certified cache.

## 3. Prespecified controls and approximation boundaries

Wave 1 preregistered before execution and Wave 2 distinctly preregistered after observing wave-1 failures. Both used a one-position-at-a-time chronological state machine on individual original quotes with first-tick-of-minute mid ±$0.15 bracket, causal completed observed S1 quality, causal M5 ATR14/session gate, and real quote Bid/Ask entry/exit. Both held **fixed R9-style exit geometry**: initial stop relative to contemporaneous Bid/Ask by $0.30, $0.10 activation, $0.03 trailing distance, 30-second max hold and at most 3 same-minute opposite rearms. A fixed assumed $0.20 per roundtrip, **1 oz per 0.01 lot**, idealized instantaneous fill, 0 added slippage. Historical broker minimum-stop points, real commissions, precise ticks OnTick coalescing, point size, swaps and original MT5 code/broker parity remain unverified. Therefore absolute net figures below are **scenario dollars under declared assumptions**, not broker profits.

Independent entry scenario overlays preserve Hold/Exit while changing ENTRY. Specific approximate prototypes: current-quote trigger, spread-neutral midpoint, 250ms/3 quote persistence, causal completed 1-second EMA(5/13), EMA price-cross scalp, preemptive bracket, completed S1 range breakout, observed 10-sec squeeze break, frozen-boundary sweep/reclaim, EMA-pullback/reacceleration, fresh opposite rearm, quote momentum and a deterministic one-account three-specialist router. The router is actually simulated under one state machine with exclusive positions; profits are not summed from unrelated cohorts.

### Cost/model controlled January reference

- R9-style **Dukascopy cap $1.00/oz exploratory**: **32,084** completed trades, **3,430** winning trades (win rate 10.69%), net **$-28,563.72**, gross loss **$29,537.82**, max mark-to-market DD **$28,564.61**. This is an entry-study same-feed denominator, not true R9 Coinexx result.

- Strict **hypothetical** R9 25-point=$0.25 cap on original Dukascopy: **289** trades, **52** winners, net $-149.58; too few compared with R9 original high-frequency regime to serve as an equivalent feed control.

## 4. Full January original-quote direct tick screens

### Wave 1: R9 bracket and early-momentum ablations

| Strategy scenario | Completed trades | Wins | Win % | Net (scenario $) | Gross loss (abs $) | Max equity DD (scenario $) |

|---|---:|---:|---:|---:|---:|---:|

| `R9_QUOTE_TRIGGER_CAP025` | 289 | 52 | 17.99 | -149.58 | 169.60 | 152.71 |

| `R9_QUOTE_TRIGGER_CAP075` | 28,120 | 3,034 | 10.79 | -23,873.99 | 24,695.32 | 23,873.99 |

| `R9_QUOTE_TRIGGER_CAP100` | 32,084 | 3,430 | 10.69 | -28,563.72 | 29,537.82 | 28,564.61 |

| `R9_QUOTE_TRIGGER_CAP150` | 33,501 | 3,588 | 10.71 | -31,054.26 | 32,146.99 | 31,054.26 |

| `MID_TRIGGER_CAP100` | 29,477 | 3,187 | 10.81 | -26,185.18 | 27,096.69 | 26,186.07 |

| `MID_PERSIST_250MS_3T_CAP100` | 28,496 | 3,067 | 10.76 | -25,275.42 | 26,127.49 | 25,276.30 |

| `MID_MICRO_EMA_CAP100` | 29,285 | 3,158 | 10.78 | -26,008.75 | 26,910.29 | 26,009.64 |

| `MID_PERSIST_MICRO_EMA_CAP100` | 28,334 | 3,045 | 10.75 | -25,124.22 | 25,967.98 | 25,125.11 |

| `QUOTE_MICRO_EMA_CAP100` | 31,795 | 3,394 | 10.67 | -28,296.39 | 29,256.81 | 28,297.28 |

| `EMA5_13_S1_REACCEL_CAP100` | 3,537 | 404 | 11.42 | -3,201.32 | 3,322.33 | 3,201.32 |

| `MID_TRIGGER_CAP150` | 30,791 | 3,336 | 10.83 | -28,518.27 | 29,543.28 | 28,518.27 |

| `MID_PERSIST_250MS_3T_CAP150` | 29,927 | 3,233 | 10.80 | -27,686.59 | 28,666.47 | 27,686.59 |

| `MID_MICRO_EMA_CAP150` | 30,597 | 3,308 | 10.81 | -28,333.54 | 29,347.25 | 28,333.54 |

| `MID_PERSIST_MICRO_EMA_CAP150` | 29,758 | 3,211 | 10.79 | -27,521.59 | 28,491.77 | 27,521.59 |

| `QUOTE_MICRO_EMA_CAP150` | 33,204 | 3,551 | 10.69 | -30,769.21 | 31,846.87 | 30,769.21 |

| `EMA5_13_S1_REACCEL_CAP150` | 3,941 | 462 | 11.72 | -3,791.29 | 3,942.09 | 3,791.29 |

### Wave 2: distinct scalping specialists and integrated router

| Strategy scenario | Completed trades | Wins | Win % | Net (scenario $) | Gross loss (abs $) | Max equity DD (scenario $) |

|---|---:|---:|---:|---:|---:|---:|

| `EARLY_BRACKET_CAP100` | 30,457 | 3,297 | 10.82 | -27,031.12 | 27,962.36 | 27,032.01 |

| `S1_LAST10_HIGHLOW_BREAK_CAP100` | 19,974 | 2,194 | 10.98 | -17,462.26 | 18,107.52 | 17,462.26 |

| `S1_SQUEEZE_RELEASE_CAP100` | 12,286 | 1,115 | 9.07 | -10,669.36 | 10,934.48 | 10,671.96 |

| `SWEEP_RECLAIM_CAP100` | 30,814 | 3,796 | 12.32 | -26,461.74 | 27,566.29 | 26,463.47 |

| `EMA_PULLBACK_REACCEL_CAP100` | 16,819 | 1,949 | 11.59 | -14,691.25 | 15,258.39 | 14,691.88 |

| `FRESH_OPPOSITE_REARM_CAP100` | 25,281 | 2,686 | 10.62 | -22,518.04 | 23,282.05 | 22,518.93 |

| `QUOTE_MOMENTUM_CAP100` | 20,547 | 2,514 | 12.23 | -17,994.27 | 18,739.82 | 17,994.27 |

| `JOINT_ROUTER_CAP100` | 64,825 | 7,554 | 11.65 | -55,897.49 | 57,998.19 | 55,899.08 |

| `EARLY_BRACKET_CAP150` | 31,804 | 3,447 | 10.84 | -29,427.29 | 30,464.65 | 29,427.29 |

| `S1_LAST10_HIGHLOW_BREAK_CAP150` | 21,023 | 2,344 | 11.15 | -19,174.12 | 19,921.81 | 19,174.12 |

| `S1_SQUEEZE_RELEASE_CAP150` | 12,413 | 1,120 | 9.02 | -10,862.07 | 11,127.35 | 10,862.07 |

| `SWEEP_RECLAIM_CAP150` | 33,214 | 4,116 | 12.39 | -30,240.57 | 31,560.80 | 30,241.09 |

| `EMA_PULLBACK_REACCEL_CAP150` | 18,161 | 2,132 | 11.74 | -16,678.56 | 17,345.54 | 16,681.19 |

| `FRESH_OPPOSITE_REARM_CAP150` | 26,332 | 2,795 | 10.61 | -24,439.19 | 25,272.30 | 24,439.19 |

| `QUOTE_MOMENTUM_CAP150` | 21,710 | 2,662 | 12.26 | -20,085.31 | 20,945.95 | 20,085.31 |

| `JOINT_ROUTER_CAP150` | 68,095 | 7,986 | 11.73 | -60,973.96 | 63,368.74 | 60,973.96 |

**Result:** 32 of 32 Jan experiments yielded **negative signed net** under the original Dukascopy Bid/Ask costs and frozen R9-style Hold/Exit. None qualifies the predeclared >10% entry success gate requiring positive whole-account net, acceptable loss/drawdown and substantive winning-trade gain; **no February–July extension was triggered**. Do not use a percentage of a *negative* net to describe a winning strategy.

- A useful **negative control** was the three-specialist joint router at cap $1.00: 7,554 historical-winner labels vs 3,430 for the same-feed R9-like reference (**+120.2% absolute win count**), but net deteriorated to $-55,897.49 versus $-28,563.72 and gross loss increased to $57,998.19. A large win-count improvement *without profitability* is definitively **NOT a formal breakthrough**. Its higher position frequency increased loss throughput instead of net edge.

- Wave 2 sweep/reclaim alone produced modestly more wins than its reference but was also loss-making. Neither its realized lower-likelihood win rate, nor hypothetical profit under a different broker, is proven by the community discussions. Complete individual daily `net/trades/wins/gross_loss/max_dd_diagnostic` are in the archived JSON; do not interpret each scenario as a cumulative EA merge.

## 5. Cost-translation caveat and model QA

- A **post-hoc** diagnostic narrowed observed Dukascopy Bid/Ask spreads to 25% around the same quoted midprices. This fabricates alternative quote levels (not ticks), thus is not the original Dukascopy market and cannot promote any candidate. A separately run corrected wave-2 sensitivity also remained negative in all 16 scenarios. A first multi-module experimental cost script was found to mix JIT module identities, and was **invalidated and not published**; the separated wave-2 diagnostic is the only retained comparison. Even spreading cost compression did not reproduce generated R9 SYNTH win statistics, consistent with, but not proving, both quote path and trade lifecycle geometry contributing to historical disparity.

- During QA, initial daily Max DD display was discovered to initialize each day-local equity peak at zero instead of starting day equity. **Bug was fixed and both entire batches recomputed**; original uploaded scripts/results were renamed `ZZ_SUPERSEDED_DAILY_DD_BASIS__...`, never silently overwritten. The final active scripts/JSON are the corrected ones. Aggregate net, gross loss and global maxDD stayed unchanged; day-local maximum drawdown was corrected. This is mandatory for all future reporting.

- Independently tested chronological prefix invariance: four code paths (R9 cap1, mid+persistence+EMA, independent sweep-reclaim, and joint router) replayed on Jan1–Jan2 ticks only and matched the full-January runs **exactly** for completed daily trade counts, win counts and rounded net. The test does not establish full MQL5 parity, data-wall independence or the 17-frame derived cache.

## 6. Broad external mechanism literature (source statements vs tested approximation)

- **Russian MQL5 official and research:** MetaQuotes spread Bid/Ask analyzer: https://www.mql5.com/ru/articles/9804 ; the native real-tick testing model: https://www.mql5.com/ru/docs/runtime/testing ; volatility-breakout algorithm and false-signal gate: https://www.mql5.com/ru/articles/19459 ; dynamic scalping/swing regime switch: https://www.mql5.com/ru/articles/19989 ; tick-debounced spread sign as example of causal consecutive-tick confirmation: https://www.mql5.com/ru/articles/2739 . The real-tick/transaction-cost explanations are relevant, **not claims their historical backtests are transferable to 2026 spot gold**.

- **Chinese MetaQuotes:** moving-envelope + long-term EMA/short RSI bounce scalping signal and known regime failure: https://www.mql5.com/zh/articles/18269 . Our EMA pullback is a separate, simplified transparent causal approximation: not a claim to reproduce this article’s entire strategy.

- **Japanese MetaQuotes:** ATR/ADX volatility vs direction logic: https://www.mql5.com/ja/articles/16213 ; dynamic volatility breakout/retest: https://www.mql5.com/ja/articles/19459 . ATR measures movement potential, not sign, and must be combined with genuinely causal entry confirmation.

- **Korean MetaQuotes:** ATR measures volatility but is not a stand-alone directional signal: https://www.mql5.com/ko/articles/10748 . Korean open trader design EMA+RSI pullback: https://kr.tradingview.com/script/XLx4CnI6/ . The XAUUSD output must not borrow unsupported profit claims from them.

- **TradingView OPEN descriptions/scripts:** aggressive EMA5/13 RSI7 ATR scalp: https://www.tradingview.com/script/5q4PsY3a-XAUUSD-Scalping-AGRESIV/ ; Gold Smart Scalper V3 EMA9/21 pullback: https://www.tradingview.com/script/zMAKRynu-Gold-Smart-Scalper-V3-Clean-Chart/ ; Bollinger/Keltner squeeze: https://www.tradingview.com/script/bIjrCSBf-XAUUSD-Family-Bollinger-Scalper/ ; EMA+volume/Bollinger breakout for gold: https://www.tradingview.com/script/VGpGuyG0-Breakout-Follow-Trend-Indicator/ . Real exchange volume/VWAP is not observed in Dukascopy Bid/Ask quotes, so any such source volume filter is **not faithfully reproduced**.

- **Retail community:** https://www.reddit.com/r/Forex/comments/1the56x/building_a_fully_automated_mt5_scalper_for_gold/ discusses quote spread/news filter vulnerabilities, but qualitative anecdotes are not proof of performance and may be unrepresentative.

## 7. Follow-on scientific question, strictly no promotion

January authentic Dukascopy Bid/Ask quote spreads (average $0.841/oz) dwarf R9 source $0.03 trailing distance and $0.10 activation, illustrating the pressure on seconds-long scalps and why adding many entry modules may generate extra gross loss. This is **hypothesis-compatible**, not proof entry-only repair is impossible. Next targeted research should determine the earliest **observable** price expansion that could clear real spread + commissions before 30-second max-hold, and distinguish quote-side artifacts from true midprice movement and spread-normalized markouts. Preserve current Hold/Exit as a control while testing this, then seek owner approval before any intentional HOLD alteration. If genuine positive January result appears under the fixed original quote feed, initiate Feb–Jul chronological confirmation; do not tune on August or use hindsight future paths as signals.

## 8. Reproduction, hashes, evidence, current resume pointer

- `BETA_009_JAN_SOURCE_EOF_AUDIT.py` | SHA256 `ed6a9172aaa064b9f6da9230d9705ff698c543a45f9479b262c0a8442f2b826b`

- `BETA_009_JAN_SOURCE_EOF_AUDIT.json` | SHA256 `a00f91057021caef2d62dca5f8e34600ce3839bfa800ab8a6de3f5350fe7fe2a`

- `BETA_009_JAN_R9_ENTRY_PARALLEL.py` | SHA256 `de81c44ef2c0cee739f801d98f177db286dd0492bfbcf9e0a18c03114f001fec`

- `BETA_009_JAN_R9_ENTRY_PARALLEL_SCREEN.json` | SHA256 `f83a5e6f7060326c8107d37b9741d277a4476319bfa2f22e440274326c4cbbb4`

- `BETA_009_JAN_SECONDARY_SCALP_PARALLEL.py` | SHA256 `439535ad7670cf30d661ba229bc16b16383061b388f83a677cf1738fc810b18c`

- `BETA_009_JAN_SECONDARY_SCALP_SCREEN.json` | SHA256 `9a4b3850199b1d9ba0f8a9524c8a812053ec7457b1f2c73f1fc7aa64405c0315`

- `BETA_009_JAN_ENTRY_PARALLEL_PREREG.md` | SHA256 `eaaaf397cbc41beeef2db660fef5f445dddf87b5ca04dd37154d8aef42e7990a`

- `BETA_009_JAN_SECONDARY_SCALP_PREREG.md` | SHA256 `daa32971093adf1ca40411ba9b28f411bc1dbd4add84c8eab560089f3c8124d5`

- `BETA_009_CAUSAL_PREFIX_TEST.py` | SHA256 `6cc109613596e72a50a14c4633014768dbb5ff4abb77378c451d43fbdb61a738`

Evidence Drive: https://drive.google.com/drive/folders/11imx5cE1Pvzr81V0nRJs2MEjBy5mt4nE ; GitHub beta `research/checkpoints/BETA_009_JAN_ENTRY_PARALLEL_WAVE1.json` and `_WAVE2.json` are initial versioned checkpoints and must be marked superseded by **corrected-daily-DD** manifests. The exact source SHA is `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`. Avoid double-scanning this verified January source after stream timeouts.

**Next first-incomplete scientific unit:** `BETA_005_CACHE_INTEGRITY_CERTIFICATION__2026-01__002_FEATURE_PARITY_AND_CACHE_CERTIFICATION` (original Jan gzip and chronological quote audit complete; independent multi-resolution 17-layer feature cache certification NOT complete). `approved_beta_ea=null`, `current_approved_baseline=null`, zero formal breakthroughs. August remains sealed. This is a continuing ordinary chat research record, not a handoff.

