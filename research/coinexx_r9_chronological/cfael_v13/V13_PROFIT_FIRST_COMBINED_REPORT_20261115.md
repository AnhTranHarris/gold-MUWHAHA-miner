# R9 V13 — Causal Fibonacci–Anchor Execution Lattice: profit-first Python study

**Research date:** 2026-11-15. **Source:** Original Coinexx XAUUSD January–September 2026, nine original monthly CSV.gz files, SHA-256 verified against frozen V12 receipts. **Objective:** Positive modeled net expectancy, sustainable trade throughput, and a majority of profitable completed trades. **Result:** Neither condition was reached by the evaluated candidates; no candidate is authorized for MT5 implementation.

## Executive result

The existing frozen R9 V9 micro180 entry cohorts yielded **338,064 completed trades and 128,203 positive modeled cash outcomes (37.92%)** across 72,129,347 original source quotes, under research exposure k=$1 cash per $1/oz XAUUSD move plus an extra assumed $0.20 per round trip **on top of the observed executable Bid/Ask spread**.

A compact, predeclared family of causal Fibonacci, price-duration-weighted midquote anchor, EMA9/20 and SMA12/20 prototypes was evaluated without rebuilding quotes or placing broker orders. The source-order replay used observed BUY Ask / SELL Bid entry prices, SELL Ask / BUY Bid exit marks, original millisecond ordinals, 250ms rebound confirmation, first-available stop execution and no martingale or simultaneous grid accumulation. Unlike a passive-limit fill assumption, the candidate only enters when the original quote stream actually supplies an executable-side pullback followed by an observed rebound. The main full-period versions are *post-signal counterfactual strategies*, not independently rearmed V9 variants.

| Candidate | Construction | Completed alternative entries | Positive outcomes | Modeled net total | Mean net/trade | Positive months |
|---|---|---:|---:|---:|---:|---:|
| E | Observed 180-second range, Fib 23.6%, EMA20/SMA20 soft direction, 30c stop and 10c cash harvest | 57,430 | 38.97% | -$22,353.14 | -$0.3892 | 0/9 |
| F | Same, Fib 38.2% | 43,383 | 38.77% | -$16,918.51 | -$0.3900 | 0/9 |
| G | Signal-anchored Fib 23.6% step, bounded 22–80c, observed pullback/reclaim | 38,214 | 40.41% | -$14,388.51 | -$0.3765 | 0/9 |
| H | Equal-distance fixed 25c step control | 58,021 | 40.09% | -$22,009.60 | -$0.3793 | 0/9 |
| P | 180-second Fib38.2% structural entry, 100c stop, $3 target, up to 10min hold | 32,353 | 25.80% | -$12,272.99 | -$0.3793 | 0/9 |

**Interpretation:** Variant G had the least-negative per-trade result under these assumptions, but it was not profitable, and its ~0.28-cent difference versus the equal-step control is too small to establish a Fibonacci advantage, especially because the two cohorts do not contain identical entry instances. Extended holding and a larger payoff did not rescue variant P. Stop and cost conditions are illustrative, not broker-certified.

### Winner-location map: why profit mapping did not identify a deployable setting

Across the source-exact nine-month entry feature cohort:

- **65,935 / 128,203 (51.43%) historical winners** occurred with directional price at **80–100% of the prior observed 180-second range**. But 176,963 total candidate entries occurred there, and mean net remained **-$0.4022**, so the concentration of winners follows the concentration of all V9 signals—not conditional alpha.
- **46,403 / 128,203 (36.19%) historical winners** occurred at least **150c beyond their past-only 180-second quote-duration equilibrium in their trade direction**. Their mean net was **-$0.3992**. This does not imply a sell/fade or buy/chase edge.
- At confirmed M1 Fibonacci 50% rails within +/-25c, source-verified original entries remained near **-$0.40** each; the same lack of positive separation appeared in many EMA20-versus-SMA20 alignment bins.

A single capped-complexity histogram gradient boosting map used **Jan–Apr for training, May–Jun for calibration, Jul–Sep for later evaluation**. Features were source-causal entry-time geometry (and the already-existing V9 quote quant measurements), **never exit conditions or future price paths**. Its later-month win AUC was **0.5362**, and the top 1% ranked from the calibration threshold averaged **-$0.4040** across 1,009 later entries. In-sample top-ranked bins were much better than these later bins: **a clear fit-instability warning**, not a positive candidate. The later period is chronologically separate for this experiment but not an independent untouched OOS sample of the wider project.

### Economics and signal-clock finding

The V9 baseline averaged **-$0.4003/trade**. An extra $0.20 assumption plus an approximately $0.20 mean round-trip Bid/Ask spread imposes about **$0.40 of modeled friction before directional price edge**. A positive route needs measurable forward price displacement beyond this hurdle, not merely a prettier Fibonacci grid or a higher backtest win fraction. With the original mean winning-trade magnitude (~$0.235) and mean loss magnitude (~$0.789), break-even under unchanged payoffs would require approximately **77% winners**; to achieve both more than 50% winners *and* positive net results, the exit payoff and loss distribution must change substantially.

Fibonacci 38.2/50/61.8% confirmed M1/M5 pivots with EMA9/20 and M5 SMA12/20 were also investigated in three development months. Those strict confluences resulted in **fewer than 45 completed positions per month**, too sparse for a high-volume system and not net-positive. Micro180 source-observed extremes and 23.6% Fibonacci rails restored thousands of opportunities; they still did not generate a positive edge. Therefore do **not** prescribe a 'best MT5 indicator setting' from these data. No MT5 EA or live trading source was modified.

## What is actually recommended next — positive-expectancy research target

The **profitability objective remains active**, but these versions fail the promotion gate. Stop fitting more parameters to the same V9 breakout signals: the evidence indicates those short-clock signals have little stable forward-return discrimination once costs are included. Instead, put one independent **M15/H1 structural pullback specialist** into a *new* source-exact Python shadow, keeping micro180 as a **timing/confirmation component**, not the primary source of trade direction. Its entry should occur after a genuine confirmed swing pullback (cost-adjusted entry discount), have a structurally defined stop without averaging down, and require a prospective target at least 2–3× the expected total cost and modeled loss hurdle. Do not equate an old research claim with reproducible proof; certify that specialist independently from the original Jan–Sep quote files and then on genuinely later/untouched dates. Actual broker slippage, commission and latency observations from the DEMO-only V12 telemetry remain a separate release gate.

The next design should be accepted only if **positive net expectancy after spread+stress costs, positive months, acceptable tail drawdown and sustained frequency** appear on *closed-loop on-policy* alternate strategy simulations with future signals regenerated, not on filtered historical V9 entries. The objective of majority profitable trades should be measured alongside realized net, not used as an excuse to overfit or hide losing months.

## Method, safety and limitations

- Original nine source SHA-256s matched pinned V12 receipts. All 72,129,347 quotes were read via existing files, **not reexported, reaggregated into another tick warehouse, or duplicated into Drive/GitHub**.
- Snapshots were at original V9 entry ordinals. EMA/SMA used only fully closed observed M1/M5 bars, M1/M5 swing pivots required 2 bars to the right before first eligibility, and session quote-duration weighting excluded stale quote intervals and real volume. The session boundary was UTC, not a verified Coinexx broker session.
- Trade interventions were simulated *after* those signals, using only subsequent original Bid/Ask quotes, with a conservative pullback+reclaim and at most one active position. Equal-ms events retained source row order.
- **Limit:** the opportunity set consists only of V9's own on-policy entry signals. Changing actual entries and exits would alter future V9 rearming, minute caps and signal availability. These cohort simulations are **not an independently closed-loop strategy backtest**, and even a positive result would require that follow-up before MT5 work. Result table is correctly labeled experimental counterfactual, not live or deployable performance.
- No passive limit-order fills were assumed; new entries are market-side quote-observed, without verified execution rejection/slippage. Cost sensitivity to actual broker terms remains unresolved.
- The multiple trials and the entire 2026 Jan–Sep period were used in development. **No clean out-of-sample positive validation has occurred**.
- Unit contracts verify exact source order, entry/exit Bid/Ask, same-ms confirmations, quote-time anchor causality and source hash pins.

## External research grounding (mechanisms, not promises of profit)

1. **Federal Reserve Bank of New York, Carol Osler** (2000, 2001, 2002): measured FX intraday support/resistance, stop and take-profit clustering and price-cascade behavior. Those mechanisms motivate distinct rejection versus continuation states; they do not prove this XAUUSD lattice profitable: https://www.newyorkfed.org/research/epr/00v06n2/0007osle.html and https://www.newyorkfed.org/research/staff_reports/sr125.html
2. **BIS 2025 FX market structure and BIS 2020 FX execution-algorithm study**: OTC venue fragmentation and internalisation mean Coinexx update counts are not market-wide trade volume; dealer execution and adverse selection matter: https://www.bis.org/publications/qr-202512/fx-trade-execution-landscape-through-prism-2025-bis-triennial-survey and https://www.bis.org/publ/mktc13.pdf
3. **Lalor & Swishchuk (2024), Market Simulation under Adverse Selection:** simulated passive fill assumptions can substantially exaggerate results, supporting the conservative quote-side-only intervention: https://arxiv.org/abs/2409.12721
4. **Practitioner evidence**: independent community testing of mean reversion and grid variants emphasizes fees and broad stable parameter plateaus; these anecdotes are not institutional proof nor independent validation: https://www.reddit.com/r/algotrading/comments/1iq21bf/optimizing_parameters_with_mean_reversion_strategy/


## Second-stage INDEPENDENT signal-generation pilot — added after nine-month cohort analysis

This separate six-variant pilot uses **new causal M15/M5/M1 entry signals rather than the original V9 signal list**, with one position at a time and source-ordered first-observed Bid/Ask exits. A completed M1 bar becomes available upon the first quote of the next minute, and the prototype waits until the **next quote after that observation** to model a market-side fill (no instant closing-quote capture). M15 EMA20 and M5 SMA20 directional alignment, prior completed M5 high/low Fibonacci rails, optional M1 EMA9 and quote-duration session anchor were used. An opposite-direction M15 countertrend-rejection control was also included. Fixed 1.00$/oz stop, $2.00 modeled cash target, 10-minute max hold, $0.20 extra fee, maximum one position; no martingale or passive maker-fill assumptions. The quote-gap event is labelled uncertain instead of a profitable target. Only January, May and September were tested, predeclared as representative **development** months; the pilot was not expanded to the other six months after no candidate passed the positive-profit gate.

| Independent closed-loop prototype | Trades (Jan+May+Sep) | Profitable trades | Modeled net | Net per trade |
|---|---:|---:|---:|---:|
| M15_Fib382_reclaim | 883 | 27.63% | $-385.67 | $-0.4368 |
| M15_Fib618_reclaim | 552 | 27.90% | $-182.22 | $-0.3301 |
| M15_EqualMid_reclaim | 700 | 27.29% | $-289.71 | $-0.4139 |
| M15_Fib382_EMA9_confirm | 527 | 25.62% | $-261.28 | $-0.4958 |
| M15_Fib382_anchor_discount | 128 | 22.66% | $-83.98 | $-0.6561 |
| M15_Fib382_countertrend_rejection | 710 | 25.63% | $-341.87 | $-0.4815 |

All six independent variants lost modeled money in each of the three development months, and entries were only 128–883 in aggregate per tested variant. This does **not** disprove all possible profitable lattice strategies. It does show that this particular M15 directional/swing-reclaim blueprint, with these frozen fixed parameters, does not deliver positive expectancy or high trade volume. Calling one of the losers the 'correct Fibonacci or EMA setting' would be unsupported.

**Accuracy and limitations:** direct entry observations are next quote after closed-bar first-availability, but broker response delay, slippage, actual volume/liquidity, terminal OnTick coalescing and order rejection remain unmeasured. Python original source hashes are checked per month; no native MT5 parity, broker fills or untouched OOS. The nine-month cohort results and independent 3-month pilot are separate evidence tiers, and must not be summed as independent trading systems.

### Cost-aware next research decision (rather than endless retrospective tuning)

The **profit objective remains active**. A statistically useful way forward requires a change in *signal information*, not another search across Fibonacci percentages: (1) add an independent M15/H1 structural pullback/sweep and **future-only** quote-pressure/reclaim condition, with the quote-side spread and stress costs visible at the decision; (2) compute a time-frozen likelihood of reaching a cost-adjusted target before structural invalidation; (3) make no trade when conditional expected payoff does not clear the spread+commission+stress hurdle; (4) freeze at most one or two designs and test them as complete, continuously rearmed strategies on **untouched later data**, paired with authorized DEMO-only broker fill telemetry. This does not assert profitability before evidence.