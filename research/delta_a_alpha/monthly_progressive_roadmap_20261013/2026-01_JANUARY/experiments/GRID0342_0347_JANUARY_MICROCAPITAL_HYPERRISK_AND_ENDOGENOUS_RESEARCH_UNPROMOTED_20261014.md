# January 2026 | GRID0342–0347 — Microcapital risk + original-tick endogenous strategy science

**Disposition:** RESEARCH ONLY / UNPROMOTED / NO ACCEPTED PROFIT EDGE. 2026-10-14. None of these results certifies Coinexx execution, future survival, R9 parity, or a $100→$5,000 endpoint. This is a cross-experiment index; original scripts, source archives, and exact results take precedence over this report.

## Original governing authority
- Owner anti-drift: https://docs.google.com/document/d/1eG5F76uvm9M-1JXs4LvAaTzPEurU5l4Pgj2sUUelc1o/edit
- Owner original January source law: https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit
- Full unabridged roadmap: https://docs.google.com/document/d/1PcaksxuiayFXVW3QtKfzitARvQj6NyL4IIbGhG8K9z4/edit
- Full ratified owner governing conversation: https://docs.google.com/document/d/1J9d_P4ooCnNmcxPwG1F178aE4ktpkLrFclcyQPaQJ8k/edit
- Original R8 MQL5 source: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/mt5-r8-s1-wave-confirm-certification/Experts/GoldMuwahahaMiner_R8_Microstructure.mq5
- Frozen V1 whitepaper Git blob `1b92b3c89159681a7181508de158af685cf5780c`.
- Official `delta-A-alpha` cursor remains J0183; active V1 blob SHA `64b75c39c41ff8ccd0d0e8b02e45bdf5b9ca54e2`; production trading OFF; August SEALED. No production code or official journal changed.

## Reframed research question
Can an *independently fundable*, after-cost, source-generated XAUUSD small-capital strategy with only virtual (unfunded) grids, one initial physical 0.01 lot, hard account loss/margin controls, and profit-earned physical capacity gradually scale from $100 to $5,000, then hand off to the original V1 L0–L7 governor **without hindsight-selected winners, martingale, or hidden margin exposure**?

Two acceptance predicates must pass independently: (1) genuine positive after-spread expectancy per physical trade across ten reproducible original-tick reset windows; (2) broker-calibrated absence of ruin, with legitimate fast cycles and growth, plus ongoing daily/worst-hour equity control. Failing either fails the whole strategy.

## Source and execution definitions
- Raw immutable January Dukascopy UTC `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`, SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`, **9,135,062** strictly ordered or equal-timestamp events.
- Hypothetical research account: initial $100, fixed 0.01 lot **assumed** equivalent to one troy ounce, 500:1 leverage, $0.20 round-trip fee, first observed opposing Bid/Ask quote at or after 250ms entry delay, 20% equity admission-margin cap, 50% stopout in endogenous branches, 1 physical position. Contract, broker stop levels, actual fills and execution quality **not certified**.
- The seed and cohort are frozen in each exact original experiment. The new GRID0346 cohort is sampled from actual quote-bearing January weekdays with complete seven-day horizons: 2026-01-06, 09, 13, 14, 15, 16, 20, 21, 22, 23. These windows overlap and are not independent out-of-sample markets.

## Native market microstructure economics
Original January bid/ask spread median $0.70, 10th percentile $0.54, 90th percentile $1.36. Fraction of 9,135,062 quote events below or equal to spread $0.25: 0.0476%; $0.50: 5.78%; $0.75: 62.18%; $1.00: 84.42%; $1.25: 88.84%. A 0.01-lot/one-oz position must offset actual entry and exit side spread and modeled $0.20 fee before any real net positive scalp; **these costs were represented at quote-level**.

## Original microcapital hyper-risk and virtual-grid hypothesis records GRID0342–0345
The enclosed source-exact predecessor artifacts contain two independent branches, not one promoted algorithm:

**Capital-only overlay on the inherited historically selected candidate tape:**
| Policy | Positive seven-day ending accounts | No modeled stopout | Total trades / ten | Final cash range | Worst UTC-hour drawdown | $5,000 reached |
|---|---:|---:|---:|---:|---:|---:|
| Preserved 2-slot control | 10/10 | 10/10 | 711 | $243.14–$396.04 | $82.36 | 0/10 |
| R8 strict one physical position | 10/10 | 10/10 | 242 | $142.89–$196.83 | $23.00 | 0/10 |
| Stress escrow $8 / 90% cash floor | 7/10 | 10/10 | 194 | $95.80–$227.85 | $42.18 | 0/10 |

Strict singleton reduces physical simultaneous risk and hourly drawdown but *severely limits capacity*. Escrow, when actually binding, sacrifices some positive episodes. None proves that the original source-selected tape is an autonomously reproducible edge; use only as risk-overlay study.

**Fully endogenous, unselected independent original quote signal tests:**
- Whole-month virtual liquidity sweep and continuation (four variants): **38–47 booked trades** each, **$41.29–$43.59** January ending cash from $100; all lose.
- Separate completed-second momentum breakout, pullback, multi-state router, reversal (six seven-day portfolio variants): **0/10 profitable** per portfolio; in the original result cohorts the broadest losses ended around $42–$83 across strategies. Nonruin was caused by skipped funding/drawdown admissions, NOT proven profitable trading.
- Explicit $90 account-equity circuit shortened adverse exposure, but booked seven-day balances were about $89–$90, again not an edge. The stop is quoted at the first observed *worse* execution price when gapped, never a guaranteed exact-price liquidation.
- Original predecessor files provide the genuine code and complete ledgers. Prior independent-read-only QC checks: 103 on one branch and 444 on the other. These are accounting integrity checks, not owner certification.

## NEW GRID0346 — orthogonal 15/30/60-minute and completed 60-second pullback-resumption
New source: `grid0346_endogenous_multiscale_pullback.py`. It uses price slopes from *completed earlier second* at 15, 30 and 60 minute offsets (2 of 3 agreement), rolling 60 completed-second virtual high/low structure, and 5-second resumption momentum. The initial signal is the first quote of a second; fills occur at the first actual quote >=250ms later. No historical R8 or R9 deals and no inherited January candidate source labels are used. Exactly one 0.01-lot physically funded position is permitted. Four independent parameter hypotheses, all based on observable prior-second quotes, with cash risk budgets and loss pauses, were tested on the corrected ten January quote-bearing trading-day cohort.

| New configuration | Trades, 10 x 7d | Positive ending $100 accounts | Modeled nonruin / no stopout | Ending cash across accounts | Worst hourly DD | $5,000 within seven days |
|---|---:|---:|---:|---:|---:|---:|
| STRUCT_A | 468 | 0/10 | 10/10 | $43.47–$48.38 | $24.99 | 0/10 |
| STRUCT_B | 549 | 0/10 | 10/10 | $45.14–$49.60 | $14.19 | 0/10 |
| STRUCT_C | 551 | 0/10 | 10/10 | $44.64–$49.30 | $29.55 | 0/10 |
| STRUCT_D | 597 | 0/10 | 10/10 | $44.09–$49.50 | $17.31 | 0/10 |

All four **REJECTED as profitable microcapital sources**. They are under the $100 original balance in all 40 reset windows; 10/10 modeled nonruin at the expense of stop-entry permission when available cash shrinks. These hypotheses were developed in-sample. Their numerical difference is not evidence of robust optimal parameters.

GRID0347 is a separate read-only original quote/direction/execution ledger checker. **207 assertions PASS** on 40 episodes and four original-quote settlement ledgers; no two funded positions overlap inside a single reset episode; exact PnL identity reconstructs from `(Bid_exit−Ask_entry)−$0.20` for buys or `(Bid_entry−Ask_exit)−$0.20` for sells. Independent source quote identity was checked against raw gzip first rows and full SHA-256. This is not an independently written strategy execution engine, brokerage verification, or month-blind validation. The first draft GRID0346 date selector included calendar nontrading days and is quarantined; only the **corrected actual trading-date** run and its updated ledgers are within this archive. Using isolated per-variant execution processes recovered and completed all 4 cases after a combined runner encountered a runtime stall.

## Reconstructible community mechanism candidates (not proof of edge)
1. [MQL5 2026 whole-basket position/margin risk](https://www.mql5.com/en/articles/24331): separate aggregate physical heat from per-order legality; forbid multiple seemingly safe orders that combine into one unsafe correlated inventory. This aligns with demonstrated singleton risk gains.
2. [MQL5 2026 margin vs stop risk](https://www.mql5.com/en/articles/23897): calculate both initial physical margin and loss-to-stop; when minimum 0.01 lot makes stop loss exceed cash risk budget, **SKIP**; don't secretly upscale lot size or relax capital risk.
3. [FMZ Chinese full-code regime-grid](https://www.fmz.com/strategy/530403): a SCANNING→ACTIVE→RESET virtual range regime with slope/structure/box confirmation, cost-aware step spacing and full state invalidation is reconstructible, but product is PAXG/USDC perpetual, **not XAUUSD spot CFD**; its execution geometry cannot be copied without a broker/price-side redesign. It has not been shown profitable in our model.
4. [TradingView Japanese-timeframe gold entry example](https://www.tradingview.com/script/MfLB5Fml-KenKem-Gold-Scalper-Lite/): completed previous bar, minimum stop beyond spread, first partial profit and breakeven rules are reconstructible concepts; not an independent verified edge.
5. [Chinese MQL5 grid/martingale hazard analysis](https://www.mql5.com/zh/articles/8390): trend runaways and gaps can defeat apparent grid certainty, supporting hard loss and inventory boundaries. Reject doubling-after-loss schemes.
6. [Reddit spread and execution cost discussions](https://www.reddit.com/r/algotrading/comments/1sm6agl/tips_to_beat_the_cost_of_spread/): anecdotal trader experiences, not validation; retain only as cost-robustness motivations.

## Future subsystem architecture hypothesis — not a solved algorithm
**MICROCAP-L0:** original Bid/Ask, absolute UTC, actual Coinexx contract/tick value, `SYMBOL_TRADE_STOPS_LEVEL`, `SYMBOL_VOLUME_MIN`, free margin + stopout, live spread, pessimistic quote gap fill. **L1:** virtual/unfunded micro-grid levels from completed seconds/M1; avoid actual passive-fill simulation unless historical best-bid/ask and queue model can justify. **L2:** range-versus-trend mode inferred from completed-bars only, no artificial January label. **L3:** independently demonstrated quote-side **positive conditional expectancy**; otherwise idle or demo only. **L4:** one physical 0.01 lot, no averaging-down and no martingale; stops/hold/emergency unwind on executable opposing quotes. **L5:** loss escrow/cooldown and daily/hourly physical equity protection, with persistent lock state; stopout on gaps may still be fatal. **L6:** earn up to two physical slots only after genuinely banked surplus, independent uncorrelated sources and sufficient stress-test headroom; do not grant leverage when losing. **L7:** stage graduation $100→$500→$1k→$5k requires realized equity, verified broker margin, representative OOS safety and explicit owner approval; hand off to the preserved high-capital V1 L0–L7 only then. This is a conceptual roadmap, *not the result of a successful backtest*.

There is **no scientifically demonstrated risk- and fundability-certified strategy that grows all ten $100 accounts to $5,000 within seven days**. That is a 50x seven-day ambition, not a robust guaranteed outcome. Do not convert a safety-pass with losses into positive strategy acceptance. Any future novel entries must first pass **independent, out-of-sample original tick P&L** under realistic broker settings, then portfolio risk + transition gates.

## Preservation and no-promotion
- This report does not change `CURRENT_STATE.json`, scientific J0183, original accepted monthly sources, active V1 code, or MT5; trading OFF.
- Archive contains original two independently produced GRID0342–0345 source/QC archives, source code and exact results/ledgers of new GRID0346–0347, original-trading-date cohort manifest, quote cost analysis and cryptographic file manifests.
- Raw January ~69MB gzip is *not re-packed*; it is referenced by immutable SHA256.


---
## Exact verified research archive and originals
- [Complete original source, predecessor archives, four cohorts/40 funded ledgers and 207-check QC](https://drive.google.com/file/d/10ivjZ-aVCh1k2Xryv7RvMj0Sv9sYqh1g/view)
- Raw archive sha256: `bc322da90945173b681108e1d27423bf6261e279f9d4f45badaca01da512bbb7`.
- [Drive full same research report](https://drive.google.com/file/d/1DLhrwuDlLcq76MuUT0ytX3BvNmr8-WJD/view).
- [New exact Python GRID0346/0347 source](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/delta-A-alpha/research/delta_a_alpha/monthly_progressive_roadmap_20261013/2026-01_JANUARY/experiments/GRID0342_0347_SOURCE_CODE).
- Active V1 and official cursor unmodified. This is only an in-sample research archive, NOT an accepted strategy.
