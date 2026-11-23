# R9 HybridGate — January 2026 R03 causal MTF hazard and intrasecond feasibility research

**Owner-scoped status: IN-SAMPLE RESEARCH ADVANCED; FULL OWNER STRATEGY GATE NOT PASSED.**
Research date: 2026-11-22 America/Chicago. **No production MQL5, original R9, original synthetic book, approved capital policy, July R8, S100 V2, January R5 or February policy was changed.** This is not a deployable or broker-filled strategy. R03 is continuation of R01/R02, not a new baseline, source reset, or unapproved replacement.

## W0 — Preserve sources and original accounting

- Original GitHub R9 HybridGate v1.90 MQL5 blob SHA: `7eecb5f1947017a01ce85b2520725de54749e523`.
- Original January Coinexx REAL TickLogger source gzip SHA256: `1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8`. **7,699,274** chronological original Bid/Ask records, **413** adjacent equal-millisecond records. Source is read-only. Independent actual prices use BUY Ask entry, BUY Bid exit; SELL Bid entry, SELL Ask exit. Original broker contract size, fills, slippage, queue and stop execution not certified.
- Original R9 January SYNTH booked historical reference is **27,980 trade legs**, **24,368 originally booked-profitable exits**, **19,775 first legs**, **8,205 second legs**, in 21 January trading days. Reference booked P&L is NOT a Coinexx realized-profit target ledger and never entered the live replay.
- The earlier W2 original 27,980 row historical reference is preserved in https://drive.google.com/file/d/1CHCXeBYDDQSI9PiZ06TfWy1xUlEpPQGC/view . Original full merged 272,352-row REAL quote witness file is not replaced.
- Official governing advanced source order inherited from https://docs.google.com/document/d/1yi3cT1IbutlwPcDCiapHxIg41nIrZAlKnGuTjHbu_tY/edit : source lock → narrow original Atlas → reverse-engineer real quote witness → academic/quant/MetaQuotes research → causal mechanism and MT5 proxy design → incremental C++/Python → full January comparison → revise if objectives not jointly met → owner approval only after full pass. Here, owner deliberately requests **January fitted/in-sample research** first. February and later were NOT read to fit, score or tune R03.

## W1/W2 — Distinctive original R9 fixed-point observations

- First-leg entry is a nearly universal **per-minute hazard**: all 19,775 original first legs occur in distinct minutes, **97.13%** enter by the :30 second of their minute. Original first-leg exits at seconds :42 and :43 total **5,498**; original second-leg exits at seconds :42 and :43 total **5,617**. First-leg exits from entry seconds :01–:03 commonly cluster at :05–:06 or after a maximum-hold boundary. Exactly **2,780** R9 legs have 30-second holds.
- This is an intraminute phase signature of the original SYNTH tester book, **not a known causal trading rule**. The original MT5 `Every tick` tick generator can create an M1-based intraminute path distinct from the recorded REAL sequence. Exact generator equality is not proven. Real quote overlap can be missing in individual original seconds; no price is invented.
- Coinexx source is sufficient to build every *observed* M1/M5/M15/H1 and longer timeframe OHLC from original rows. This R03 features and tests use **completed M1/M5/M15/H1 Bid candles only** for past multi-timeframe trend and ATR; current price/minute high-low/quote intensity are explicitly *as-of-now*, not completed M1 bars. No future H1/H4 candle is read.
- 1,652,250 source-observed second states were streamed from 7,699,274 raw ticks in ~9.84s, ~2 MB C++ process RSS, including first Bid/Ask per second, phase, minute geometry, completed MTF ATR14, current minute displacement, 1–300-second causal returns, 10/30/60-second path efficiency, quote arrival intensity, realized range, and **quote-update direction proxy**. No real trade sizes, market-depth queue, order-book imbalance or true volume-based OFI are available in the source; `last`, `volume`, `volume_real` are not reliable signed-order-flow inputs here.

## W3 — External quant/academic/MT5 research actually consulted

1. **MetaQuotes, MT5 Strategy Tester documentation and MQL5 book:** `Every tick` mode emulates ticks from M1 quote data; real-tick mode uses recorded history. https://www.mql5.com/files/book/mql5book.pdf . This motivates treating the 42/43-second historical exit clustering as source-specific until reproduced with real quote data.
2. **MetaQuotes, CopyBuffer and MTF closed-bar causality:** current indicator buffer shift 0 can be incomplete; shift 1 is the last fully closed bar in the common MTF pattern. https://www.mql5.com/en/docs/series/copybuffer ; https://www.mql5.com/en/articles/22363 . MQL5 port must validate `BarsCalculated`, `CopyBuffer` timing, DST and broker tick size.
3. **López de Prado, _Advances in Financial Machine Learning_**, event-based sampling, triple-barrier first passage, meta-labeling, purged validation: https://www.wiley.com/en-us/Advances%2Bin%2BFinancial%2BMachine%2BLearning-p-9781119482086 . These motivate two competing models: directional entry hazard and spread-adjusted exit competing risks, NOT fixed threshold optimization.
4. **Research on order-flow and transaction costs** emphasizes that proxy quote order flow may be misleading without size/depth and that gross signals may disappear after costs: https://papers.ssrn.com/sol3/Delivery.cfm/7053198.pdf?abstractid=7053198&mirid=1 . This does NOT validate any XAUUSD alpha or justify labeling quote movement as trade-side volume.

## W4/W5 — Two separate causal entry learners and source-exact execution

**First iteration:** LightGBM in-sample original January first/second-entry classification on 1.65m-second causal features. Under one-first-per-minute chronological selection, first-leg ±2s matches **6,153 / 19,775 (31.11%)** and ±5s **7,886 / 19,775 (39.88%)**, but 6,832 first triggers in minutes with no original first leg. Raw probabilistic label accuracy is not execution accuracy.

**Second iteration:** January-supervised **discrete-time competing-direction entry hazard**. Separate first/second-leg 3-class LightGBM models (WAIT / BUY / SELL), fitted using risk sets from the original fixed book for *training* only. The 513,016 training at-risk states include 294,875 first-leg risks with 19,128 positive label seconds and 218,141 second-leg risks with 8,028 positive label seconds. The original entry/exit manifest is **not opened by the inference scorer or C++ replay**. Features use source-observed seconds and completed history, not outcome prices. Classification has obvious in-sample bias; it is not an OOS generalization claim.

**C++17 replay:** for 7,699,274 source rows, parse original time_msc/Bid/Ask in original order including same-ms duplicates; only act on the first observed quote of a second whose score comes from that exact as-of quote (quote Bid/Ask parity verified). Enforce one first leg per minute, only one open position at a time, one same-minute second leg, optional opposite direction, exact source-ordinal stop/target/hold. Never read the original book during execution. Separate one-to-one sparse maximum-cardinality original same-side entry/exit matching is **post hoc only**. A strict ±2-second tolerance is the preexisting R01/R02 **interim metric proxy**, not a formal owner-approved interpretation of the requested "within 5% range".

**Intrasecond third iteration:** causal intent-to-quote microstructure specialist waits for an observed Ask pullback (BUY) or Bid improvement (SELL) and subsequent observable rebound before entering, with bounded fallback. Noncausal first/last-second or hindsight-picked ticks are never accepted as strategy actions. This modestly changed ±2s matching but did not improve whole-system economics.

## W6 — January full-month numerical results, separated from genuinely matched wins

| Candidate | Complete REAL positions | Positive REAL quote exits | Original joint same-side entry+exit ±2 seconds | Quote-result per 1 oz equivalent before additional costs |
|---|---:|---:|---:|---:|
| Original R9 source-faithful REAL baseline | 32,179 | 14,080 | 441 / 27,980 (1.58%) | −$6,053.12 |
| Hazard, profit target, original exploratory config | 38,173 | 25,266 | 1,525 (5.45%) | −$8,195.96 |
| Hazard, phase-clock, original exploratory config | 38,547 | 13,762 | 7,307 (26.12%) | −$7,105.21 |
| Hazard, source-ordinal pullback/rebound, original exploratory config | 37,593 | 24,860 | 1,766 (6.31%) | −$8,207.30 |
| **Fully pinned reproducible profit V02** | **37,052** | **24,577** | **1,501 (5.36%)** | **−$8,326.84** |
| **Fully pinned reproducible phase-clock V03** | **37,348** | **13,365** | **7,428 (26.55%)** | **−$6,919.98** |

Reproducible V02/V03 exact configuration: `--f=0.24 --s=0.23 --spread=80 --pt=14 --sl=180 --hold=30 --second=1 --opp=1`; `--clock=0` for V02, `--clock=1` for V03. The historical read-only source and separate inference score stream are identical. V03 is **16.84×** the source-R9 strict joint match count (7,428 vs 441), but still far below the required 26,581 original-pair 95% count. Phase-clock ±5s matched **10,014 (35.79%)**, also far below 95%.

V02: 37,052/24,577 satisfy the two numerical count requirements, **but only 1,501** historical entry/exit matches within ±2s, and only **1,112 original booked-positive trade identities** BOTH match the two clocks and close positive on REAL quotes. Of 24,577 gross positive REAL exits, only **12,337** remain positive after a hypothetical *additional* $0.20 per-one-ounce cost. V02 realized quote-book max cumulative exit-to-exit drawdown was **$8,330.83 per ounce-equivalent**, not a real broker balance DD. All **21 January dates** show negative aggregate REAL quote-side returns in V02.

V03: 7,428 historical entry/exit pairs within ±2s, of which 7,277 are booked-original winners, but only **4,184** matched generated trades are REAL quote-positive and only **4,171** are simultaneously original booked winners AND REAL positive. **9,906 / 37,348** are positive after the additional 20-cent proxy. V03 realized quote-equivalent drawdown **$6,921.60**; again all **21 days quote-negative**.

The "real positive" and "20c additional-cost-positive" are two explicitly separate measures. R9 original source booked net is not the quote-dollar aggregate above. All quote-dollar totals refer to an illustrative *one-ounce-equivalent* exposure, NOT broker contract/lot-scaled funded P&L. No spread-free rewards or execution latency repairs are invented.

## Per-original-row chronology-respecting quote teacher (offline **hindsight upper bound**, not strategy)

Using immutable original first/second leg labels **only** to define retrospective ±T-second windows, a separate C++ oracle scans real original Bid/Ask ticks, then selects an entry quote observed **strictly before** its exit quote with the best attainable trade-side markout within each independently fixed window. This is retrospective noncausal price selection, NOT feasible simultaneous portfolio execution. The teacher never enters the C++ trading replay.

| Original window | Rows with strictly ordered observed entry/exit quotes | Individual positive hindsight markouts | Additional 20-cent-price-proxy positive |
|---|---:|---:|---:|
| Exact source entry and exit seconds | 27,025 | 17,197 | see teacher output |
| ±2 s | 27,960 | 23,232 | 20,850 |
| ±5 s | 27,974 | **26,305** | **24,863** |

At ±5s, first real quote of each independently teacher-selected entry/exit **second** is profitable for just 23,710 cases (21,555 with 20-cent extra cost). Hindsight-best within-second quote selection contributed a median **$0.24/oz**; 2,540 individually positive teacher paths become nonpositive when using the first observed quote in those selected seconds. The paired teacher windows are independently optimized and may overlap / conflict; these are **not attainable portfolio fill counts**, not a trading performance report, and cannot certify a profitable executable EA. At strict ±2 seconds, even a hindsight maximum of 23,232 profitable independently fixed-window paths falls below the 24,368 original winner count; this does NOT prove no different schedule can create more positive trades elsewhere.

## S1/R02 protected control continuity and exact-match epistemics

Earlier R02 fixed-time analysis finds that full-source R9 original S1 directional gate exists in only 3,339 of 27,496 quote-observed historical entry-seconds and all market-side gates co-occur during original second in only 2,914; **716** add available original position/rearm. January historical 2,147 first-negative / later-positive original two-leg cycles are fixed *positive recovery controls*, not targets for indiscriminate suppression. R03's source-independent second legs must be graded for preservation and later portfolio unwind; generating a second leg is not automatically a matched or protected recovered cycle.

Original manifest includes only whole-second entry/exit clock stamps and original booked net, **not the original MT5 synthetic entry/exit fill price**. Thus an exact “5% price range” reconstruction metric cannot honestly be certified here. The available joint ±2s and ±5s figures are **timestamp-and-side correspondence proxies**. Metric definition needs explicit entry-price tick-size and exit-price tolerance authority from original MT5 tester fill ledger if user seeks price correspondence.

## W6 research quality and engineering non-interference

- Source SHA256 pinned; R03 research feature extraction processed 7,699,274 real source rows, 413 equal-ms neighboring ticks, without source-row deduplication or bar lookahead; 1,652,250 observed second summaries.
- Replay models can see completed M1/M5/M15/H1 + current quote only; first-source quote-of-second score equality enforced against raw source; fixed original labels enter offline fit and **offline evaluation only**.
- Strict C++17 `-O3 -Wall -Wextra -Werror` compilation passes for source feature, replay, ordered teacher and microstructure sources.
- Five regression tests pass: source/reference pins; no historical oracle read in replay; full source feed quote alignment/invariants; teacher ordered strict entry-before-exit; altered future quotes do not change prior closed source-stream trade history.
- Base features local only: no new raw tick warehouse uploaded. Repro models and source get saved in tiny versioned package; exact archive hashes and GitHub isolated branch are documented in an attached source manifest.
- Limitations: hypothetical quote execution at observed Bid/Ask, not broker fills; `time_msc` ordering preserved but not actual trade latency; no stop-level restrictions, reject handling, commission/profit currency, financing, margin, broker contract-lot normalization, or independent February OOS evidence. Early in-sample training may memorize timestamp phase; not promotion-grade.

## W7 — Decision and next *constructive* research gate

**The combined acceptance contract remains UNSATISFIED.** No live EA changes, no frozen capital-risk policy modifications, no retroactive deletion or mutation of original R9 winner trade IDs; no February source contamination; no optimization reported as forward validity. Owner approval is still required for a new MT5 EA variant.

**R04 should directly attack the missing tick-ordinal decision and exit economic edge**, not repeat a generic 25-parameter screen or an unconstrained model-fitting marathon:

1. **Extract matched positive/negative/recovered controls** for the 26,305 teacher-positive targets by the actual source quote **ordinal**, **pre-entry features**, *event-relative episode* and session; place especially strong attention on the 2,540 oracle-positive cases lost from first-quote-only entry/exit, keeping original recovered positive cycles in the same denominator. Use quote-replay exact target provenance but NEVER use teacher optimal ordinal to execute at runtime.
2. **Build competing-risk online exits:** first-passage hazards for positive **net after costs**, stop/squeeze hazard, bad microstructure state and quote-gap censoring conditioned on completed MTF regime, source-event intensity, observed spread and realized adverse move. Profitability target must be tested after spread and independent extra costs rather than choosing tiny targets to create a meaningless high raw win count.
3. **Model native MT5 feasibility:** built-in `iATR` and `iADX` on M1/M5/M15/H1 and optionally H4 using completed buffers (shift=1), and `iCustom` efficiency / realized-volatility / signed quote-update state when native data is unavailable. True order-book imbalance and true buy/sell trade volume cannot be recovered from this source; any proxies need separate tests.
4. **Whole-system test after each hypothesis:** match original same-side entry + exit clock jointly, preserve original booked-profit identities, separately measure independent source-REAL positive outcomes and whole-account cost-adjusted marked outcome, negative cycle and max floating MAE; ensure every changed order legitimately changes downstream opportunity and availability.
5. Only after **one and the same fully independently executable strategy** clears owner entry count / positive exits / same-side joint correspondence / account economics, preserve it as an in-sample candidate and freeze it before any separate month test. A month that has been used for fitting must not be represented as blind forward test.

### Sources

- Exact MQL5 EA: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/mt5-r9-hybrid-gate-certification/Experts/GoldMuwahahaMiner_R9_HybridGate.mq5
- Original R01 replay and 25-configuration receipt: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/carson/r9-jan-real-tick-reconstruction-r01-20261122/research/coinexx_r9_chronological/experiments/jan2026_r01
- Original R02 causal-state audit and specialist controls: https://docs.google.com/document/d/1wVjdMGcIfeB1OoAu7P4HIRpKLxUCt7MyI8JMH8W3mtA/edit
- January original W2 full-trade financial metric report: https://docs.google.com/document/d/1o1mXF2m_R2ARVNpGTRy0fMHDaD8tKvw-TGPoKigp-3A/edit

### Quantitative mechanisms (research specification, not proved alpha)

At each source-observed quote-second \(t\), the real-time state \(x_t\) comprises: multi-timescale completed-bar displacement and Wilder-style ATR, current-time Bid/Ask and spread, causal per-second movement and quote-update frequency, plus the deterministic second-of-minute phase. For a window \(\tau\), the causal movement-efficiency feature is \(E_{t,\tau}=|p_t-p_{t-\tau}|/(\sum_{u=t-\tau+1}^t |p_u-p_{u-1}|+\epsilon)\), where quotes at nonexistent seconds are not synthesized and sampling semantics are explicitly recorded. This differs from R9's fixed 10-completed-second minimum-efficiency gate.

The fitted per-leg competing-direction hazard is \(h_{\ell,s}(t)=P(\text{first newly qualifying }\ell\text{-leg entry of side }s\text{ at }t\mid \text{at risk}, x_{\le t})\) for \(\ell\in\{1,2\}\), \(s\in\{\mathrm{BUY},\mathrm{SELL}\}\). In an independent REAL trade simulator, BUY, SELL and WAIT are chosen by those model scores only when the live state machine allows a new position. At-risk training labels are derived from original immutable January entry seconds, but are never fed to online inference. This is a supervised phase surrogate, not a reconstructed synthetic tester path or a claimed unbiased probability.

The future R04 exit extension should use **competing observable first-passage hazards**, e.g. \(\lambda_{+}(t\mid x_t,z_t)\), \(\lambda_{-}(t\mid x_t,z_t)\), and \(\lambda_{\text{timeout}}(t\mid x_t,z_t)\), conditioned on *the position's own* observable mark-to-Bid/Ask return, maximum adverse move, spread-to-MTF volatility and quote-ordinal confirmations. The decision criterion must compare expected **after-cost** utility and protected recovery value, not fitted percent winners alone. For research labelling, the first of positive/negative/timeout **source quote ordinal** can supply competing-risk targets; for live execution only already observed outcomes can affect the next decision. This is a proposal, not a successful R03 implementation.

R03 compact source archive with frozen learned weights and complete receipts: https://drive.google.com/file/d/1Zg5ADK-Se2tyISOBn66gvA4hQW6eRq2O/view
