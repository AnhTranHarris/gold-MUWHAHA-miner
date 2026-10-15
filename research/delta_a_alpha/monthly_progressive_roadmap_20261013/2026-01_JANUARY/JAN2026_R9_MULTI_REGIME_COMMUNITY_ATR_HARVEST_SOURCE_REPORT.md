> **SUPERSEDING OWNER INVESTOR-PERFORMANCE CORRECTION (2026-10-14): THIS IS NOT A SUCCESS OR ACCEPTED BREAKTHROUGH.** Any prior "breakthrough", "profit success", "large improvement" or "superior gross-loss control" wording below refers exclusively to relative **internal in-sample research**, not the owner's actual R9 SYNTH $100 target. R9 January net +$41,520.82/27,980 funded closes; the strongest prior Dukascopy experiment +$243.779/194 closes is **0.587% of R9 net and 0.693% of its trades**. Owner now requires >=60% of actual corresponding R9 hourly and daily performance before any human-facing success claim; <50% is failed internal research. See [binding correction and 1,536 further full-original-tick trials](OWNER_20261014_R9_60PCT_SUCCESS_GATE_RETRACTION_AND_1536_FULLTICK_TRIAL_ARCHIVE.md). Preserve all historical detail below without treating this document as approved or deployed. Git commit history retains original bytes.

# January 2026 — R9 H1 net-first reverse-engineering: ATR-conditioned runner, community reconstruction, one-slot grid

**Date:** 2026-10-14 | **Research:** delta-A-alpha / January only / original Dukascopy ordered Bid/Ask | **Disposition:** SOURCE-COMPLETE POSITIVE IN-SAMPLE RESEARCH CHILD, **NOT OWNER-ACCEPTED**, not wired into frozen V1 execution. Official J0183 unchanged, trading disabled, August SEALED.

## 1. Authoritative sources and contract
- R9 ten-page cross-scale research specification GitHub source (Git blob **4cc4433a6cc8320f92c20e68d074a1b206db8743**) https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/monthly_progressive_roadmap_20261013/2026-01_JANUARY/R9_JAN2026_INSTITUTIONAL_QUANT_REVERSE_ENGINEERING_SOURCE_OF_TRUTH_10P.md
- Complete governing **January-only original-source QC law** https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit. Owner full frozen V1 original original SHA **1b92b3c89159681a7181508de158af685cf5780c**; preserving L0–L7; direct owner instruction prevails.
- Existing V1 vertical-grid kernel **v1_vertical_grid.py** Git blob **85e7d55944a3a1fd4e12d244c466210f6a0c4a22**; existing four-desk integrated architecture **v1_four_session_architecture.py** Git blob **64b75c39c41ff8ccd0d0e8b02e45bdf5b9ca54e2**. These are NOT modified by the new child.
- Original January Dukascopy gzip checksum **d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5**, 9,135,062 ordered original Bid/Ask millisecond rows. Not included inside research ZIP, remains original source. No February+ used in this research cycle.
- Original R9 Coinexx MT5 **Every tick** reference: **27,980** Jan positions, **+$41,520.82** native tester net, gross wins +$43,348.69 / gross losing -$1,827.87 / PF23.7154 and 480 trade-active hours all realized-positive; these are generated-tick **teacher performance**, not real Bid/Ask causal profits. Native tester M1/M5/H1 deal histories match, so do NOT count as 3 independent datasets. Original R9 OVERFIT future labels never supplied to executable.

## 2. Community mechanism source reconstruction (external proposal, NOT earnings proof)
- **MetaQuotes research-grounded finite-cycle grid** — restartable BGT range rotation, TGT trend directional grid, MGT mean-reversion, ATR spacing, CUSUM regime switches. https://www.mql5.com/en/articles/21833 . Reconstruct into *virtual* armed rungs and one physically funded slot, never import martingale or multi-loss inventory.
- **MetaQuotes regime switching EA** — distinct trend, ranging and breakout strategy ownership rather than one rigid indicator stack. https://www.mql5.com/en/articles/17781 . Note published example's initial XAUUSD backtest was suboptimal, so concept not external performance certification.
- **Chinese FMZ 黄金动态网格测试策略** — regression-slope/range occupancy/state invalidation and fee-covered grid spacing; originally PAXG/USDC perpetual, not Coinexx spot gold. https://www.fmz.com/strategy/530403 . Single-inventory range reset only.
- **Chinese FMZ cost-budget grid** — grid decides when price permits action, capital governor decides actual exposure; dynamic rung spacing max of min spacing, ATR allowance, and cost floor, with target fixed at fill. https://www.fmz.com/digest-topic/11014 . Discard original sizing/Kelly accumulation to preserve fixed 0.01.
- **TradingView open BB/Keltner squeeze** — compression then breakout/release, momentum exit. https://www.tradingview.com/script/yU4Zq0jT-BB-Keltner-Squeeze-Strategy/ . Use reconstructed completed-S15 release and previous completed M5 volatility.
- **Korean FMZ ATR-RSI trailing** — trend filter plus ATR stop/trail architecture, but RSI midpoint-only rule is not assumed profitable. https://www.fmz.com/lang/ko/strategy/457811 . Research innovation: give ATR influence on profitable position's *exit* instead of hard entry gate.

## 3. Highest-quality January discovery — net first
Frozen ORIGINAL 627 completed-S15 squeeze release source events, single 0.01 lot physically, $100 **and separately** $200 cash, no Martingale, margin 1:500 research assumption with 1 oz cash-PnL assumed/0.01 lot, first observed Bid/Ask executable >=250ms after signal, bounded quote wait <=15s, spread <=$0.55, entry quote drift <=$1.50, fee $0.20 round trip, stop distance $7, 5 entries/min max, position singleton. Real price paths; no same-candle final OHLC.

**Unchanged January parent** for all ATR regimes: static take-profit $20 gross, trail arms after $5 favorable cash-equivalent, $2.50 trailing distance, hold <=1500 seconds.

**New regime-aware research child**: when **prior completed M5 ATR(14) >= $7.77**, retain same entry and $7 stop, switch to *patient runner*: gross target $40, trailing arms after $7 favorable, $3.50 trailing gap, max hold 2700 seconds. Otherwise leave parent exit unchanged. ATR is calculated on prior FULLY completed M5 candle, not current bar nor future teacher outcomes.

| Original chronological January replay | Starting account | Realized net | Distinct closes | PF | Full-tick marked peak DD | Positive / negative trading days |
|---|---:|---:|---:|---:|---:|---:|
| Control unchanged S15 quote-queue | $100 | +$110.096 | 250 | 1.17157 | $51.765 | 14 / 7 |
| New completed-M5 ATR runner | **$100** | **+$171.868** | **244** | **1.267018** | **$45.569** | **15 / 6** |
| Same new rule on independent balance | **$200** | **+$171.868** | **244** | **1.267018** | **$45.569** | **15 / 6** |
| In-sample larger runner target/trail neighbor | $100 | +$177.005 | 242 | 1.2714 | $48.939 | 15 / 6 |

New child gross winning **+$815.524**, gross losing **−$643.656**, net +$171.868; win rate **148/244 = 60.656%**. Opening $100 → cash $271.868; opening $200 → cash $371.868. Research assumptions do NOT establish Coinexx margin/contract/slippage parity.

**Incremental net over unchanged control** = **+$61.772 (+56.11%)** from same source signals, 6 fewer closes (−2.4%). Better drawdown by $6.196 (-11.97%). Robust local neighborhood: target 30 and 40 with trail arm 7, gap 3.5, 2700s hold yielded exactly +$171.868. Variant target 48/arm8/gap4.0 reached +$177.005 but has higher DD, isolated post-hoc best not preferred.

## 4. Causal matched-signal mechanism attribution
An independent source-ID/signal-time join found **244 matched funded source events** across unchanged and updated runs. All 96 improved **high-completed-M5-ATR** events generated **+$41.028** of incremental close PnL. The 148 non-high ATR matched events had **exactly $0.000** PnL change. **Six baseline-only source events** (displaced by longer position occupancy) had **−$20.744** combined net. Thus **+$41.028 + $20.744 = +$61.772** exactly; no double-counting hypothetical shadow trades. The improved run produced no newly funded source IDs. This isolates real exit-policy gain versus changed one-slot capacity, not spurious extra fills.

**Exit anatomy:** 202 / 244 closes at risk/trail-stop condition, 41 max-hold exits, **1 fixed target exit**. Profit improvement is predominantly *regime-conditioned trailing and holding*, not fixed target hits. Average hold ~725 seconds, **not** R9 SYNTH's 18-second median; this is a profit specialist, not yet the required velocity/fast-harvest specialist.

**In-sample concentration:** first 15 calendar days +$2.230 /57 closes; Jan 16–31 +$169.638 /187 closes. 15 net-positive and 6 net-negative close-active days. Of 744 January UTC hours: 158 with closes, 92 positive, 66 negative, 586 zero closes, and 74 /158 hours above strict 75% after-cost win accuracy. January report is not a validated investor-hour positivity or R9 throughput solution. These are meaningful limitations while deciding future research priorities.

## 5. Independent original quote and cash QC
A fully independent auditing script re-read all **9,135,062 source quote rows**, checked every execution leg on exact recorded UTC millisecond and original opposite-side price, independently checked each trade's `P&L=side*(exit-entry)-$0.20`, all signal-to-first-filled quote delays in **[250ms,15s]**, absence of overlapping positions, real quote marked adverse path while held, rolling peak floating-equity max drawdown; recomputed $171.868 net, $815.524 gross wins, -$643.656 losses and DD $45.569 from source. No mismatches on each $100 and $200 separately funded account.

**Important:** source archive includes original generator, observed time-index signals, all exact codes, all 24 original $100/$200 regime tests, 36 neighbor tests, and 42 alternate-flow/additive tests plus their retained selected ledgers, 31-day, 744-hour and ISO-week cash scorecards. Zero/negative cases retained; new sources were not auto-promoted based on extra raw signals.

## 6. Proposed V1 compatible architecture and prioritized next mechanism
- L0 original raw Bid/Ask tick clock → L1 Sydney/Tokyo/London/NY DST-aware calendars and session activity priors → L2 completed H1/M5 direction, M5 ATR/cost movement budget and H4/M15 slow location → L3 specialist virtual grid source factories (range rotation, continuation, pullback/reclaim, compression release) → L4 stateful watchdog and fresh-rung rearm → L5 H1-trend-within-M5-pullback ownership → L6 bounded stop/abandon/safe re-evaluate without inventory averaging → L7 one physical 0.01-funded position, true mark-to-market and collision accounting.
- Research child `jan_atr_regime_harvest_finite_grid_v1.py` contains executable exact tick simulator module and serves as **candidate L3-to-L6 adapter**. It is intentionally **NOT wired into original `v1_four_session_architecture.py`**, because source-ancestry parity and official owner QA/promotion remain outstanding. Original V1 architecture is unchanged.
- Next high-priority **R9-like fast-pay factory** must generate many genuine high-frequency after-cost opportunities, particularly in London-US quote bursts and range rotation, without displacing profitable runners. Proposed fresh price-cycle re-entry requires last completed profitable source close + as-of event change + a fresh spread-covered rung, not adding to a losing position. Analyze combined *incremental cash minus occupancy cost* rather than raw candidate count.
- Optimize remaining January only against 27,980 reference trades, +$41,520.82 synthetic R9 ideal as **comparison objective, not executable outcome**. Do not silently extrapolate 244 profit-specialist trades into 27,980 physical daily velocity. After investor's first net gate, user retains other hour/day/week/PF/accuracy gates and physical drawdown safeguards.

## 7. Exact run protocol
Extract experiment ZIP into one folder, point `DATA` and `PARENT` constants at original mounted January gzip and provided `jan_parent_causal_squeeze_signals.npz`; install numpy,pandas,numba. Run:

```bash
python jan_atr_regime_harvest_finite_grid_v1.py
python jan_atr_runner_neighborhood_v1.py
python jan_community_flow_regime_composition_v1.py
python jan_atr_harvest_independent_tick_qc_v1.py
python jan_runner_source_matched_ablation_v1.py
```

Re-run a timestamp-sorted Bid/Ask source and verify content hashes against manifest before execution. The source pack has reproducible **source code and output logs**, but does not contain original full 66MB original January tick gzip (separate protected source). No original protected EA, original V1 engine, or scientific cursor modified. **January owner QC PENDING**; no MT5 build/live authorization.
