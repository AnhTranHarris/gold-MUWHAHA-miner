# R9 “EVERY TICK” — JANUARY 2026
## Institutional Quantitative Reverse-Engineering Source of Truth (10 pages)

**Version:** 1.0 / 2026-10-14  | **Scope:** January 2026 only | **Lineage:** delta-A-alpha | **Status:** Evidence-locked analytical baseline, unpromoted.

**Research posture:** Senior systematic-trading / market microstructure / MQL5 execution-engineering analysis. No employer affiliation or financial performance guarantee is claimed.

**Authority order:** Current owner direction > original complete January QC / V1 whitepaper > exact original evidence and executable source > official state journal > this analytical paper. This paper is the research interpretation source of truth, *not* a replacement for governing law or source bytes.

## PAGE 01 — Mandate, hypothesis and decision-use
*01 / Research constitution and executive abstract*

This memorandum is the January 2026 R9 SYNTH reverse-engineering research baseline for the Gold MUWHAHA Miner vertical-grid program. Its role is to make the existing cross-timeframe evidence technically legible and experimentally actionable. It is not an approved trading algorithm, an independent broker-fill certification, or a replacement for the owner-frozen V1 whitepaper and January QC law.

### Investment-research question

How did a fixed-0.01-lot R9 EA repeatedly harvest positive realized cash across every trade-active hour in Coinexx MetaTrader 5 generated “Every tick” tests, despite losses at individual tick, minute and five-minute horizons? Which features can be recovered causally using real January Dukascopy Bid/Ask quotes and translated into the governed L0–L7 grid?

| January source-native outcome | Observed result |
|---|---|
| Initial tester deposit / assumed lot | $100 / 0.01 lot; 1:500 leverage |
| Completed trade cycles | 27,980; 24,368 net winners; 87.0908% win rate |
| Realized net; gross winners; gross losers | +$41,520.82; +$43,348.69; −$1,827.87 |
| Profit factor / ending closed balance | 23.7154 / $41,620.82 |
| Active trading days / trade-active hours | 21/21 profitable days; 480/480 profitable hours |
| Hours above 75% after-cost win accuracy | 436/480 (90.83%); 264 zero-trade hours |

### Principal institutional findings

- The M1, M5 and H1 tester reports describe the same 27,980 trade cycles; they provide alternate observation scales, not three independent alpha confirmations.
- 97.45% of trade cycles finish inside the originating M1 candle, and the recorded synthetic outcomes depend radically on intraminute entry phase.
- Increasing completed-M5 ATR strongly coincides with higher realized profit per close, much more than with trade count; London/US overlap has the highest observed hourly throughput.
- The central research object is a state-dependent entry → hold → exit → re-arm process, tested as a one-slot account with full spread and equity accounting.

**Source-of-truth boundary —** Binding owner instruction, complete primary artifacts, executable code, hashes, original daily ledgers and official CURRENT_STATE remain superior authority. This report is the versioned analytical interpretation that must be challenged against them. [P1–P8]


---

## PAGE 02 — Data lineage, identities and timebase
*02 / Provenance, invariants and evidentiary hierarchy*

### Four observation layers—never merge their truth status

| Layer | What is actually observable | Evidence limit |
|---|---|---|
| Coinexx R9 HybridGate M1 / M5 / H1 | Native strategy-tester Orders/Deals, seconds, sides, prices, fee, balances | “Every tick” generated from M1 history; not independent real-tick fills |
| Coinexx R9 M1 TickLogger XLSX | Second-resolution Orders/Deals and logger-enabled settings | Identical deals; not a raw millisecond quote tape |
| R9 OVERFIT teacher | Retrospective trade-quality/movement labels | Hindsight targets only; never as-of features |
| Dukascopy January UTC Bid/Ask | 9,135,062 original observed quotes; executable-side path | Different feed and spread, no Coinexx identity |

The independent report-to-report comparison matches 27,980/27,980 January deal cycles across M1/M5/H1. The logger and HybridGate M1 reports also match deal IDs, entry/exit times, direction, prices, net cash and closing balances. This is strong reproducibility of tester-reported outcomes; it is not replication by independent price generation.

### Clock identification and as-of eligibility

The working Coinexx report-time minus UTC offset is approximately +02:00, inferred by minimizing cross-feed entry-price residuals (median about $0.485 at the selected offset versus $8.705 at the nearest alternate hour). Because this is a price-based estimate and not documented broker-server configuration, session assignments are conditional on the offset. A Python trade event at time t may access only fully completed M1/M5/H1 candles before t, plus actually observed quotes through t; current candle final OHLC and future R9 exit prices are unavailable.

### Reproducibility fingerprints

- Coinexx M1 native XLSX SHA-256: f9315c35bde962135785a0fb8fd268251086e9bebe27f5789757c69cfb38819d.
- Coinexx M5: 3237dfe2ebec41c0cf0699dfa65dcff1020f94869ed099b5e109b7377459face; H1: 76f478220a910a1fbc1a0fff3c0d9141617d109a25c6a9075a6806883f07adfd.
- M1 TickLogger report: 2590b6d2b254d97a1b5a516be263bd64f4e81d92277b7114dbddefe1b96d55c2.
- Original Jan Dukascopy gzip: d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5.

**Unresolved input semantics —** Compressed “TickLogger” .gz was identified as MetaQuotes SingleTestCache binary; it has not been decoded into genuine millisecond Coinexx Bid/Ask tick events. Avoid treating Orders/Deals as quote-tape microstructure. [P1–P4, M1]


---

## PAGE 03 — Intraminute execution geometry
*03 / Tick-to-M1 lifecycle; the principal research anomaly*

### R9 SYNTH entry-second attribution

| M1 entry second | Trade cycles | After-fee winners | Reported January net |
|---|---|---|---|
| 00–09 | 11,203 | 71.48% | +$5,239.42 |
| 10–39 | 16,113 | 99.63% | +$36,194.39 |
| 40–59 | 664 | 46.23% | +$87.01 |
| All January | 27,980 | 87.09% | +$41,520.82 |

The middle-phase cohort provides 87.17% of total reported net from 57.59% of closes. Across all 21 active January dates, it contributed more total cash than the first-ten-second cohort. Yet this is conditional historical attribution: the later entries were created by the tested system itself, not a randomized allocation of entry time.

### Likely confounders that must be experimentally separated

- Generated-tick path fingerprint: M1-price interpolation and minute spread behavior can create repeatable intrabar stop/target sequences. MetaQuotes documents synthetic tick generation from cached M1 prices. [M1]
- State selection: an entry around second 20 may be possible only after earlier microstructure, the current position closing, a liquidity break/reclaim, and spread gating; “wait until second 20” is not equivalent.
- Holding-time selection: median monthly hold is 18 seconds; mean holds differ by phase (about 12.17s early, 19.46s middle, 16.12s late).
- Slot availability: 19,775 entry minutes contain 27,980 entries, with 8,205 minutes hosting exactly two; forbidding early trades changes which later signals can be funded.

### Proposed mechanical reverse-engineering study

Replay each synthetic historical entry as a teacher label against elapsed-M1-second, elapsed quote-displacement from minute open, live-so-far high/low, prior completed M1 candle, quote-turn count, directional efficiency, RSI slope, spread and completed M5 ATR/H1 regime. Stratify by exit reason and same-minute rearm status. After describing the teacher, deploy each candidate event detector on every original January Dukascopy tick from a fresh $100 or $200 account; never transplant the profitable teacher trades themselves.

**Experimental design priority —** Compare event-conditioned and clock-conditioned policies using identical quote path, one physical slot, and proper trade occupancy. A phase-label classifier’s AUC alone is not investment return. [P3, P5]


---

## PAGE 04 — Loss absorption across timescales
*04 / Distinguish cash aggregation from actual equity risk*

### The same ledger rebucketed by EXIT timestamp

| January measure | M1 | M5 | H1 |
|---|---|---|---|
| All time buckets | 44,640 | 8,928 | 744 |
| Buckets with >=1 close | 20,023 | 5,338 | 480 |
| Closes / active bucket | 1.40 | 5.24 | 58.29 |
| Maximum closes / bucket | 3 | 11 | 104 |
| Net-negative active buckets | 1,418 | 190 | 0 |
| Buckets with ≥1 losing close | 3,574 | 2,737 | 473 |
| Worst gross losing cash / bucket | −$1.42 | −$2.58 | −$9.18 |
| Worst within-bucket closed DD | $1.42 | $2.16 | $3.40 |

The same January gross losing closes sum to −$1,827.87 whether inspected as minutes, five-minute segments or hours. These columns are nested decompositions of one ledger, not additive risk exposures. 7.08% of close-active minutes, 3.56% of close-active M5 windows, and 0% of close-active H1 windows end net negative.

### Mathematical mechanism: diversification through time, not free risk cancellation

For hour h, booked P&L is R(h) = Σ closed-trade net P&L allocated by exit timestamp. A positive R(h) does not mean each included trade was profitable, each intra-hour 5-minute interval won, or floating equity avoided losses. High turnover can transform a set of locally negative trades into a positive cash hour if realized winning gains dominate. This is a statement of historical arithmetic; it cannot establish that a future stream is stable.

### Critical drawdown definition and missing risk information

A maximum $3.40 decline in the closed-balance path was observed. It is not maximum floating equity drawdown, which requires valuing every live position at the proper opposing executable quote during its hold, including cross-boundary exposure. The report does not establish full January intra-trade margin headroom, stopout probability or worst spike risk.

**Investor gate —** Replicate trade P&L, worst funded drawdown and hourly accuracy separately. Report every 744 January hour, including 264 zero-close hours; do not score zero as positive. [P4, P8]


---

## PAGE 05 — Session microstructure and participation
*05 / Clock structure, activity proxy and opportunity ownership*

### Five disjoint UTC comparison windows

| UTC session proxy | Closes | Closes / active hour | Net | Gross losing | PF |
|---|---|---|---|---|---|
| Asia 00–08 | 9,380 | 56.2 | +$12,341 | −$622 | 20.83 |
| London 08–13 | 4,981 | 47.4 | +$6,055 | −$378 | 17.04 |
| Overlap 13–17 | 6,908 | 82.2 | +$11,772 | −$402 | 30.26 |
| US 17–22 | 5,493 | 53.3 | +$8,908 | −$359 | 25.82 |
| Rollover 22–24 | 1,218 | 58.0 | +$2,445 | −$67 | 37.63 |

A necessary qualification: these are fixed UTC hour labels under the inferred +02:00 tester offset, not certified exchange sessions or DST-perfect calendars. Historical synthetic earnings across the London/US overlap were coupled to the highest measured quote-update activity (~28,137 Dukascopy quote changes per trade-active hour) and highest trade throughput (~82 closes/hour).

### Liquidity is not the same as quote frequency

Across 480 R9 close-active UTC hours, the cross-feed Pearson association between Dukascopy quote updates and Coinexx SYNTH close count is r≈0.611; between quote updates and reported net is r≈0.716. Quote frequency is a real observed information-arrival proxy. It is not executed volume, aggregate market depth, or guaranteed Coinexx liquidity. A large number of bid/ask changes can still coexist with unfavourable spread, latency or microsecond adverse selection.

### Required specialist differentiation

- Asia: investigate local range rotation, periodic two-way order pressure, lower movement budgets and cost-sensitivity; do not assume Asia must be disabled.
- London pre-US: isolate low-PF hours and possible false-break continuation before allowing more physical capital turnover.
- Overlap: measure throughput scaling and price-travel per event while enforcing spread capacity and slippage stress.
- US later / rollover: model run-down, spread shocks and finite samples; high small-cell PF is not a general policy.

**Portfolio design —** Session should be a prior or regime-feature in a common causal owner/router, not a hard-coded January calendar override. Current-completed hour net, trade count, equity exposure and opportunity rejection must be reconciled. [P4, P6]


---

## PAGE 06 — Volatility is a payout amplifier
*06 / M5 ATR and the hourly conditional-expectancy surface*

### Completed Dukascopy M5 ATR(14) versus Coinexx R9 generated-tick outcomes

| ATR regime (USD) | Hours | Closes | Net / hour | Net / trade | >75% accuracy h |
|---|---|---|---|---|---|
| Q1 ≤~3.95 | 120 | 3,668 | +$20.94 | +$0.685 | 88 / 120 |
| Q2 ~3.95–5.25 | 119 | 6,065 | +$41.25 | +$0.809 | 109 / 119 |
| Q3 ~5.25–7.77 | 120 | 8,976 | +$83.87 | +$1.121 | 118 / 120 |
| Q4 ≥~7.77 | 120 | 9,211 | +$199.72 | +$2.602 | 120 / 120 |

The upper ATR quartile averaged 3.8 times the net profit per trade of the lowest, while close velocity increased only from about 30.6 to 76.8 closes/active hour. Thus the larger cash results cannot be explained by trade volume alone. High-ATR regimes coincided with richer realized payout per trading cycle in this synthetic R9 record.

### Statistical identification and a mandatory denominator

Hourly descriptive correlations: mean completed-M5 ATR versus reported net per close r≈0.893, versus close count r≈0.194, and versus hourly net r≈0.713. The 0.893 figure is in-sample association with outcomes and partly uses a within-hour aggregate ATR summary; it is not a pre-entry forecast. First-entry-as-of ATR versus hourly net per close is lower (~0.792).

Coverage control: the quartile table covers 479 of 480 active hours, totaling 27,920 closes and +$41,453.39. One hour with 60 closes and +$67.43 net lacks classified ATR features. The quartile sums MUST NOT silently be stated as complete January totals. Gross-loss strata need their own source-level reconciliation before promotion.

### Causal translation

Treat M5 ATR as a movement-budget feature, not a universal filter. For each potential fill, quantify the completed M5 ATR regime, executable current spread, conditional move distribution, expected duration, trailing capture and cost floor. Allow faster profit release in expansion, but preserve rotation specialists when ATR is low; strict high-ATR-only trading destroys broad-hour coverage.

**MT5 parity check —** Python Wilder ATR computed on Dukascopy Bid M5 bars must be reconciled with native Coinexx MT5 iATR buffer, price precision and broker clock before assigning exact indicator thresholds. [P6, M2]


---

## PAGE 07 — H1 / M5 disagreement and regimes
*07 / Conditional direction; no naive alignment veto*

### Direction state from fully completed Dukascopy H1 and M5 bars

| Completed direction relation | Attributed R9 trades | R9 historical net | PF |
|---|---|---|---|
| Same signed H1/M5 move | 14,232 | +$22,330.60 | 25.81 |
| Opposite signed H1/M5 move | 13,616 | +$19,053.89 | 21.69 |
| Flat / missing completed features | 129 categorized + 3 unjoined | Not used in pair comparison | N/A |

Almost half the matched January R9 positions generated gains in opposed H1/M5 direction states. A deterministic “buy only if M5 and H1 align” veto would remove material historical teacher participation and might remove independent reversal, retest and short-term mean-reversion opportunities. That does not imply a countertrend signal is profitable on the Dukascopy execution feed.

### Interpret regime as ownership, not one big confirmation stack

- Directional continuation: fully completed H1/M5 signed trend, as-of tick displacement, 1–5-second momentum recovery and favorable executable spread.
- Pullback / retest: H1 structural bias persists while local M5 movement opposes it; validate reclaim/failed continuation before physical execution.
- Range rotation: lower path efficiency, recurrent local turns, cost-aware virtual rungs, bounded profit target; never multiply loss positions.
- Compression release: detect completed volatility squeeze, then as-of micro break/retest; one-slot quote-admission queue previously improved January realized cash in a separately selected in-sample screen.
- Transition / uncertainty: avoid forcing a specialized rule onto every tick; the governor may hold no position when cost-adjusted opportunity is unfavourable.

### What a theory-of-MT5 specialist should test

Vary chart timeframe while freezing indicator timeframe arguments and all EA parameters; the existing same-deal results indicate chart timeframe independence, not proof that M1, M5 and H1 regime variables are redundant. If any indicator uses PERIOD_CURRENT or an accidental chart-timeframe dependency, explicitly map buffer calls and shift semantics. Develop a deterministic fixture proving the same as-of feature values after each completed bar on M1-chart and H1-chart test harnesses.

**Avoid category errors —** The teacher trades were executed under generated ticks. The regime indicators in this study came from a separate real-quote feed. Claims about causation, microstructure orders or physical liquidity require independent chronological tests. [P7, M1–M3]


---

## PAGE 08 — From hindsight teacher to causal mechanism
*08 / Experiment portfolio and statistical falsification design*

### Research objective and decomposition

Optimization target: maximize actual after-cost booked cash subject to funded daily/hourly participation, survivability, equity drawdown, and separately measured accuracy. The R9 teacher should yield explanations of good and bad trade paths, not a copied trade list. Each candidate must pass through causal generation, bid/ask fill, stateful position occupancy, independently audited close, and investor accounting.

| Candidate mechanism | Teacher discovery question | Student falsification |
|---|---|---|
| Clock-conditioned event geometry | Why is entry second 10–39 exceptionally favorable? | Use elapsed-second plus as-of displacement/turns; compare blinded event-only vs time-only. |
| ATR-conditioned harvest duration | Why does net/close grow with M5 ATR? | Vary feasible TP/trailing/hold from entry-state ATR; track realized gross loss and floating heat. |
| Session-regime ownership | Why do overlap and opposed H1/M5 remain productive? | Fixed session priors with pooled shrinkage; compare universal vs specialized router. |
| Fee-aware virtual grid re-arm | Which microstructure paths admit multiple same-M1 trades? | One physical position, fresh confirmed rung per rearm, priced bid/ask, cooldown. |
| Activity-clock momentum | Does quote burst beat arbitrary S1 RSI? | Independent quote-count bars vs fixed-time bars, as-of spread and latency. |

### Strict experimental controls

- Primary period: January 2026 only; no February, later months or August leakage. Fixed source-hash and UTC alignment; frozen train/diagnostic partitions within January before comparing variants.
- All exhaustive or repeated parameter scans must be logged with trial IDs; selected best January curve is in-sample. Prefer stable plateaus and matched-context incremental uplift over isolated sharp peaks.
- Use R8 original microstructure as the microcapital comparison control, and separately the currently measured S15 squeeze+queue specialist; none constitutes an automatically approved integrated incumbent.
- Report daily and ISO-week by investor-defined accounting, including bad/zero days and all 744 hours. Preserve separate teacher entry/hold/exit/profit/DD/gross-loss measures with explicit scoring denominators.

**Reverse-engineering success definition —** A “mechanism” exists when a reconstructible causal rule—not a hindsight label—produces independently reconciled incremental cash, adequate throughput and no unacceptable drawdown degradation inside the same $100/$200 account. [G1–G4]


---

## PAGE 09 — Production Python and MT5 architecture
*09 / L0–L7 ownership, control states and QA contract*

### Preserve the frozen vertical-grid spine

| Layer | State, invariant or action |
|---|---|
| L0 Tick execution | UTC ordered raw Dukascopy Bid/Ask; first observed executable quote; tick timestamps; no last-look fills. |
| L1 Session geometry | Fixed explicit timezone/DST mapping; one session taxonomy; regime-specific virtual rungs. |
| L2 Completed structure | H4/H1/M15/M5 as-of only; completed ATR and directional location; indicator parity fixtures. |
| L3 Opportunity factories | High-velocity continuation, sweep/reclaim, compression breakout, independent Asia rotation. |
| L4 Watchdog / renewal | Event-based state revalidation; no indefinite stale signals or unpriced rearm. |
| L5 Trend-within-trend | Use locally opposing M5 moves inside H1 trend as a candidate specialist, not blanket veto. |
| L6 Bounded failure handling | Evidence-driven abandonment, stop and recovery without Martingale/averaging-down. |
| L7 Physical portfolio governor | Single 0.01-lot initially; $100/$200 real initial cash, spread, fee, headroom, peak equity heat. |

### Every entry must create an audit-ready causal trace

Trace fields: source version/hash; parent virtual event; as-of state timestamp; session clock; S1/M1 displacement and efficiencies; completed M5 ATR/H1 direction; tick entry and opposite-side exit quotes; requested versus actual executable timing; spread, commission, P&L, bar phase, stop/trail path, margin headroom; single-slot blocking decision; holding time; source-regime ancestry.

### Technical controls at the MT5 translation boundary

- Native Strategy Tester “Every tick” generates intermediate quote paths from M1 history; its per-minute Bid/Ask/spread assumptions differ from original real Dukascopy quotes. [M1]
- MetaQuotes documents potential NewTick event coalescing when an OnTick handler is already queued or executing; lossless source collection cannot be assumed from OnTick alone. [M3]
- Compare Python indicator values with native MQL5 iATR/RSI buffers using *completed* candles and explicit timeframe handles; do not assume period numbers prove formula parity. [M2]

**Non-negotiable deployment lock —** Research does not authorize MQL5 build, live trading, lot escalation, account deposits, the official J0183 cursor, or August unsealing. Promotion requires owner QC of complete executable source and ledgers. [G1–G4]


---

## PAGE 10 — Engineering charter, acceptance and source register
*10 / Durable research truth, falsifiable milestones and references*

### January reverse-engineering production order

- 01 | Reproduce teacher: pin M1/M5/H1 and logger original SHA, prove 27,980 deal equivalence; reconstruct per-trade reported P&L, timing and source clock.
- 02 | Enumerate regimes: join as-of completed H1, M5, M1 and actual quote-path snapshots; annotate generated-tick-phase, session, MFE/MAE labels in offline teacher tables only.
- 03 | Propose mechanisms: exit-geometry and ATR movement budgets, event-clock directional momentum, session-owned range/continuation specialists, fresh virtual grid rearm.
- 04 | Run physical January: each candidate replays ordered original Dukascopy Bid/Ask, $100 and $200 cash, fixed 0.01 lot, explicit contract/leverage/fee/slippage assumptions and actual marked exposure.
- 05 | Validate incremental integration: run unchanged control and stateful composite; reconcile every hour/day/week, gross winners/losers, full floating DD, opportunity count versus physical fills and R9 teacher dimension scores.
- 06 | Deliver durable QC: source, exact hashes, command, full ledgers and test logs to protected January Drive and GitHub; owner decides acceptance, then explicit authorization precedes MT5 implementation.

### Acceptance matrix: each metric has a separate gate

| Gate | Required audit / success interpretation |
|---|---|
| Profit and velocity | Net and funded distinct closes by every active hour, UTC date and ISO week vs matching R9 SYNTH benchmarks. |
| Risk and survival | Gross loss, full tick floating equity drawdown, margin headroom, stopout and per-slot occupancy. |
| Accuracy and trade quality | Per-hour >75% win-rate requirement with sample size; six separately locked R9 OVERFIT teacher dimensions. |
| Architecture and reproducibility | Full L0–L7 preserved; original code and hashes, replay command, additive source lineage; owner QC. |

### Authority and primary source register

[G1] Owner January QC / source law: docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw. [G2] Frozen V1 original whitepaper in delta-A-alpha. [G3] Full progressive January–July roadmap and anti-summary law. [G4] CURRENT_STATE.json J0183. [P1] Coinexx original folder ID 1S0erLKfFpqQUVHHIHDql72PgsH6vQrMF; [P2–P4] M1/M5/H1 native reports and M1 logger; [P5] original paired deal-correlation QA ZIP; [P6] January hourly cross-scale 21-file source QA archive; [P7] original Jan Dukascopy ticks; [P8] owner new January $100 trade-ledger package. [M1] MetaQuotes generated-tick tester documentation; [M2] MQL5 iATR docs; [M3] MQL5 OnTick event queue docs.

**Governance conclusion —** This document is the source-locked ANALYTICAL BASELINE for future reverse engineering—not an overwrite of original owner law or original code. Each new science checkpoint must cite this paper by SHA and record evidence that revises or falsifies its claims.

## Canonical link register (research dependency graph)

- [G1: January source and acceptance law](https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit)
- [G2: Full frozen V1 whitepaper](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt)
- [G3: Full progressive roadmap](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/governance/OWNER_20261013_FULL_PROGRESSIVE_JAN_JUL_ROADMAP_VERBATIM.md); [anti-summary / preservation law](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/governance/OWNER_20261013_VERBATIM_ANTI_SUMMARY_MONTHLY_PROGRESS_QC_LAW.md)
- [G4: Live delta-A-alpha CURRENT_STATE](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/CURRENT_STATE.json) — cursor J0183 as verified on 2026-10-14.
- [P1: Original Coinexx tester source folder](https://drive.google.com/drive/folders/1S0erLKfFpqQUVHHIHDql72PgsH6vQrMF)
- [P2: M1 HybridGate](https://drive.google.com/file/d/1jASxs5gn3e1rzwGxlE-178aN07_5ksHE/view); [P3: M5](https://drive.google.com/file/d/1Fq5eku142DxoRpvBtqddR2xgbhOz4h_T/view); [P4: H1](https://drive.google.com/file/d/1nTbW7Y-bvYQO2IDHjQmLcEiFSHO5AET5/view); [M1 TickLogger report](https://drive.google.com/file/d/1d6V3fHltXl7l2V8Wlu1BD-ubb78Qypnn/view).
- [P5: M1 HybridGate / TickLogger exact deal-matching archive](https://drive.google.com/file/d/1f6TVclfwCjrkNv3n_BqB2e205KMWL8AH/view).
- [P6: January M1/M5/H1 cross-scale source scripts, raw partitions and 744-hour scorecard](https://drive.google.com/file/d/1TemWNkYXeFl7RTx-4btGRseoRH2jO0tF/view).
- [P7: Dukascopy original January tick source metadata and related reproducibility](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/monthly_progressive_roadmap_20261013/2026-01_JANUARY/R9_COINEXX_EVERY_TICK_M1_M5_H1_SESSION_ATR_HOURLY_RISK_QA_20261014_UNPROMOTED.md).
- [P8: Original Coinexx January Deals extract with daily, hourly and weekly ledgers](https://drive.google.com/file/d/1fEaAqOkA2jg3aGiTxDduQh7hCHhQl3Yl/view).
- [M1: MetaQuotes generated/real tick algorithm](https://www.metatrader5.com/en/terminal/help/algotrading/tick_generation); [M2: iATR MQL5 API](https://www.mql5.com/en/docs/indicators/iatr); [M3: OnTick MQL5 queue](https://www.mql5.com/en/docs/event_handlers/ontick).

## Precise source discrepancies / review caveats

1. The original narrative report previously rounded Q1 ATR strata to 3,666 and Q4 to 9,210. The **source CSV and machine-readable regime JSON** instead record Q1 3,668 and Q4 9,211, summing to 27,920 closes across 479 hours. This paper uses those machine-readable figures. The missing hour holds 60 closes and +$67.43; do not reassign it into a quartile.
2. Clock conversion Coinexx tester ≈ UTC+02:00 was inferred through cross-feed matching, not directly certified. If offset changes, rerun all session stratifications.
3. All gross-win and gross-loss values are native generated-tick strategy-tester cash statistics; they do not imply real Dukascopy fills.
4. January closed-balance decline is **not** a replacement for full intratrade floating-equity drawdown.
5. The M1 TickLogger XLSX is a tester *Deals/Orders* report with logging enabled. The compressed file named TickLogger inspected as a binary SingleTestCache, **not verified tick-by-tick CSV**.
6. The full owner-ratified governing conversation URL was not fully available during the prior analysis; source/governance assertions are limited to law documents and GitHub originals actually verified.
7. The same 27,980 deals across three chart timeframe runs count **once**, not three times in multi-sample statistical confidence.

## Operational replay examples (source, not execution promise)

```bash
# From the read-only 21-file [P6] evidence package after extracting it alongside its dependencies
python r9_jan_2026_three_report_m1_m5_h1_deal_parity.py
python r9_jan_2026_tick_m1_m5_h1_hourly_correlation.py
python r9_jan_hourly_regime_attribution.py
# Verify paths, Python environment, original source hashes and expected outputs in the ZIP manifests before running.
```