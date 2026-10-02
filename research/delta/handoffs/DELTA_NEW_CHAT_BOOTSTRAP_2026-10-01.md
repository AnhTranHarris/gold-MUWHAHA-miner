# DELTA New-Chat Bootstrap — Fresh R9-Based Research Lineage

**Created:** 2026-10-01  
**GitHub:** `AnhTranHarris/gold-MUWHAHA-miner` branch `delta`  
**Drive:** DELTA_RESEARCH  
**Status:** READY FOR NEW CHAT  
**Research scope:** DELTA-ONLY CLEAN ROOM  
**August 2026:** SEALED

## Clean-room owner directive

DELTA is a standalone research and development lineage.

Prior internal research lineages are outside scope. Do not read, import, cite, compare, port, merge, reconstruct, or use their code, documents, metrics, hypotheses, candidate logic, results, handoffs, controller state, or governance.

DELTA may use only:
- the preserved R9 engineering/evidence baseline registered inside DELTA;
- DELTA-created research artifacts;
- the registered ordered market-data corpus;
- reconstructible public research used to generate independently testable causal hypotheses.

## Active engineering baseline

DELTA starts from the preserved R9 MT5 implementation:
- `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5` — source blob `7eecb5f1947017a01ce85b2520725de54749e523`
- `Experts/GoldMuwahahaMiner_R9_TickLogger.mq5` — source blob `5c7655cd3357f9126e8bffd97c34374dfb29f83e`

R9 itself is a reference baseline/evidence generator, not a claim that its REAL execution is profitable.

## Fast research corpus

Use `research/delta/reference/R9_EVIDENCE_REGISTRY.json` and `R9_REFERENCE_CORPUS_INDEX.json` before touching heavy files.

Canonical roles:
- **REAL:** execution/path/lifecycle benchmark.
- **SYNTH:** teacher/north-star only.
- **OVERFIT/ORACLE:** quarantined hypothesis/capacity source only.
- **Dukascopy Jan-Jul:** causal replay/robustness research; historically inspected.
- **August:** sealed blind holdout.

The Drive registry points to the validated REAL and SYNTH tick indexes, daily manifests, event indexes, paired monthly corpus, MT5 reports and overfit reference.

## Hard DELTA research rules

1. DELTA clean-room scope is mandatory.
2. Every scientific unit is preregistered and gets a manifest before compute.
3. Every material helper/candidate generator/cache/model/replay/QA artifact is preserved or exactly regenerable.
4. Candidate/prediction surfaces are preserved before ownership/routing whenever they affect results.
5. RIGHT-edge/as-of timing is mandatory. No future outcome may enter inference.
6. Entry+Hold quality **and trade-count retention are co-primary**. No starving-the-system success.
7. Jan-Jul are nonblind historical research, never relabeled pristine OOS.
8. August stays sealed until a frozen candidate passes rebuild readiness + human QA and the owner explicitly authorizes opening it.
9. UI/tool/runtime failure resumes the same unit from the first incomplete durability step; never restart science from memory.
10. Null/failed results remain durable evidence.
11. No candidate MQL5 coding before owner approval and `mt5_translation_ready=true`.
12. Every MT5-worthy candidate must include Python→MQL5 parity fixtures, state machine, feature timing/order, execution, ownership, session/DST and risk contracts.
13. All market-state candles obey `DELTA_GOV_002_TICK_ROOTED_NESTED_TIMEFRAME_CONTRACT.md`: ticks are authoritative, every timeframe is reconstructed directly from ticks, and completed bars become visible only at their right edge.

## Nested timeframe base reference

DELTA uses one tick-rooted market chronology across Python research and any eventual MT5 implementation:

`TICKS -> 250ms -> 1s -> 5s -> 15s -> 30s -> 45s -> M1 -> standard MT5 periods through D1`.

Every candle is rebuilt directly from the ordered tick stream for accuracy. The sequence expresses progressively slower analytical context; it does not permit timestamp approximation or chained aggregation where boundaries do not align exactly.

## Research-speed stage gate

DELTA uses a two-stage development funnel:

1. Screen every new candidate on the owner's first 2.5 weeks of January. The exact ending tick boundary and acceptance thresholds are frozen before compute once the owner supplies the next requirements.
2. Only qualifying candidates advance to bounded month-by-month January-through-July replay.

Each month is a separate durable job so a long replay cannot crash the entire campaign. Monthly completion is not a human approval gate: persist the checkpoint, emit a micro-status, and continue automatically into the next month unless a failure blocks safe continuation or the owner explicitly asks to stop. Python is the iterative research laboratory and may test/retest repeatedly for refinement and optimization. Any behavior-changing change creates a new candidate/version and never rewrites prior results. A stable promotion candidate is ultimately replayed as one frozen version across all seven monthly jobs.

## Benchmark and goal roles

Before loading any R9 evidence files, DELTA freezes these roles:
- **R9 REAL:** starting-point baseline EA and REAL ticklog; every modification must show its change versus this baseline.
- **R9 SYNTH:** performance-growth reference used to judge how much improvement has been recovered beyond REAL.
- **R9 OVERFIT:** capacity/upper-envelope reference for maximum trade participation and possible high profit per trade; never execution truth.
- **Dukascopy:** independent cross-broker tick environment used to test behavior against the Coinexx MT5 evidence stream.

The owner-primary human metrics are:
- winning trade count;
- net profit;
- gross loss;
- maximum drawdown.

Total trade count and per-trade efficiency remain companion metrics for diagnosing whether favorable headline results came from real improvement or from reduced activity.

**Evidence status:** Owner authorized R9 evidence loading on 2026-10-01. REAL and SYNTH compact references are loaded. Use compact DELTA references before touching heavy evidence; August remains sealed.

## Provisional candidate acceptance gate

Before testing a candidate, the owner defines its research scope and target area.

The current provisional human gate is:
- at least one owner-targeted primary metric must improve by **80% or more** versus R9 REAL;
- **85% or more** improvement is the soft preferred target;
- if any supported primary metric deteriorates by **17% or more but less than 25%**, flag it for investigation and improvement;
- if any supported primary metric deteriorates by **25% or more**, the candidate hard-fails the cross-metric floor regardless of gains elsewhere.

The four protected primary metrics are winning trade count, net profit, gross loss, and maximum drawdown. Direction is normalized so higher winning trades/net profit are better, while lower gross-loss magnitude/drawdown are better.

These thresholds are deliberately human-revisable after actual data review. See `DELTA_GOV_005_PROVISIONAL_CANDIDATE_IMPROVEMENT_GATE.md`.

## Cumulative SYNTH metric locks

When any primary metric reaches at least **87% of the directional performance journey from R9 REAL to R9 SYNTH**, that metric and the exact candidate/version become a protected anchor.

Future research is built on that anchor and targets the remaining unlocked primary metrics. Every descendant must preserve all inherited locked metrics. A locked metric that deteriorates by **5% or more** from its lock value causes `HARD_FAIL_LOCKED_METRIC_PRESERVATION`, even if another metric improves strongly.

Locks accumulate across descendants. If an already locked metric improves further, its anchor may ratchet to the better value; it may not silently move backward. See `DELTA_GOV_006_SYNTH_METRIC_LOCK_AND_CUMULATIVE_RATCHET_CONTRACT.md`.

## Creative refinement and optimization authority

Carson is authorized to modify, adjust, recombine, restructure, repair, simplify, expand, or replace candidate mechanisms as needed to reach the active DELTA goals.

If a refinement remains below goal and improves the targeted metric by less than **10 percentage points of additional SYNTH-gap closure versus its parent**, mark `CREATIVE_ESCALATION_REQUIRED`. The next research branch should materially broaden the intervention rather than remain limited to minor parameter changes.

Once evidence/data loading is authorized, Dukascopy tick-level Python replay is the primary experimental playground. Multiple bounded runs, parameter/configuration searches, architectural comparisons, repeated retests, and best-configuration selection are allowed and expected. “Best” means best under all active primary metrics, activity requirements, warnings, hard floors, and inherited metric locks—not merely highest profit.

Creative authority never overrides causal timing, version traceability, preserved failures, sealed-data rules, or the 5% preservation floor on locked metrics. See `DELTA_GOV_007_CREATIVE_REFINEMENT_ESCALATION_AND_DUKASCOPY_PLAYGROUND.md`.

## Multi-specialist composite architecture assumption

DELTA assumes the eventual system is a team of complementary specialists rather than one universal strategy.

Required session-aware research coverage includes Australia, Asia, Russia, India, Middle East, Europe, UK, and New York. Exact clock boundaries, DST treatment, overlap rules, and transition buffers are not yet frozen and must be defined separately before production/MT5 translation.

A specialist is judged within its declared session/regime/target scope. It may contribute primarily to one or a subset of the primary metrics. The complete composite system—specialists plus causal router/ownership logic—is the object ultimately judged against the full system-wide primary goals.

System-level metric locks attach to the exact accepted composite configuration, not automatically to one specialist. Future specialist changes must preserve inherited composite locks. This makes creative candidate combination a core research mechanism rather than an exception.

See `DELTA_GOV_008_MULTI_SPECIALIST_COMPOSITE_AND_SESSION_AWARE_ASSUMPTION.md`.

## News/event opportunity assumption

DELTA treats medium/high-impact monetary-policy, macro-financial, market, and gold-specific news as a potential opportunity regime, not an automatic no-trade zone.

Required research domains include US/Federal Reserve and macro news, European macro-financial news, Asian macro-financial news, and gold-specific developments. DELTA may build separate pre-event, release-reaction, post-event, continuation, reversal, spread/liquidity-protection, or evidence-based stand-down specialists.

All news features must be causal and as-of: no release value, revision, headline, interpretation, or classification may be used before it became public. Event timestamps, provider hierarchy, impact taxonomy, and exact windows remain pending a dedicated event-data contract.

See `DELTA_GOV_009_NEWS_EVENT_OPPORTUNITY_AND_IMPACT_HANDLING_ASSUMPTION.md`.

## Prop-style maintenance and staged-capital assumption

DELTA maintains a separate capital/risk-management layer around the trading logic. Fixed lot size is 0.01 until all four primary categories are locked and the owner explicitly defines a future lot-sizing ladder.

Test starting capital follows the durable primary-lock count: zero locks = $100,000; one lock = $1,000; two locks = $500; three locks remain $500 because no separate owner amount has been defined; all four locks = $100. The all-lock $100 stage focuses on survival and rapid growth toward $1,000, after which standard maintenance rules reapply.

At or above $1,000, the provisional community-derived internal envelope is: 0.5% planned loss per position, 2.5% daily warning, 4% daily hard stop, 5% weekly warning, and 8% weekly hard stop, all evaluated on intraday equity including floating P/L and costs. No martingale/grid recovery is allowed.

Below $1,000, standard large-account percentage rules may be relaxed or modified because the minimum 0.01 lot can dominate percentage-risk math. Exact small-account thresholds are intentionally pending empirical survivability tests and owner review. Raw strategy metrics and maintenance-governed metrics must both be reported so risk throttling cannot masquerade as edge.

See `DELTA_GOV_011_PROP_STYLE_MAINTENANCE_CAPITAL_STAGING_AND_SMALL_ACCOUNT_SURVIVAL.md`.

## R9 SYNTH evidence loaded — fast reference available

Owner authorized R9 evidence loading on 2026-10-01. R9 SYNTH was loaded first.

Canonical compact lookup:
`research/delta/reference/R9_SYNTH_PERFORMANCE_FAST_REFERENCE.json`

Use that file before reopening the 95 MB tester workbook or the massive SYNTH ticklogger corpus. It contains exact Jan-Jul primary reference metrics, monthly performance, daily/weekly distributions, source hashes/Drive IDs, integrity reconciliation, and observed day/week behavior.

Headline SYNTH reference:
- winning trades: 191,136;
- total trades: 219,342;
- net profit: $309,122.85;
- gross loss: -$16,238.66;
- balance max drawdown: $3.41;
- equity max drawdown: $4.34;
- 149/149 trading days profitable;
- 31/31 ISO weeks profitable.

The ledger reconciles exactly to the MT5 report for closed-trade net profit and balance drawdown. No visible day/week profit cap, loss kill-switch, or balance-based lot scaling is present in the tester inputs/realized SYNTH ledger; treat that as observed behavior, not a claim about hidden source-code rules.

## R9 REAL evidence loaded — fast reference available

Canonical compact lookup:
`research/delta/reference/R9_REAL_PERFORMANCE_FAST_REFERENCE.json`

Authoritative Jan-Jul REAL baseline:
- winning trades: 102,385;
- total trades: 236,647;
- net profit: -$50,285.28;
- gross loss: -$80,465.51;
- balance maximum drawdown: $50,285.30;
- equity maximum drawdown: $50,285.50;
- 149/149 trading days negative;
- 31/31 ISO weeks negative.

REAL actually executes 17,305 more trades than SYNTH (+7.8895%), so opportunity volume is not the primary deficiency. The central gap is conversion/quality/persistence/harvest: REAL has 88,751 fewer winning trades, a $359,408.13 net-profit gap, $64,226.85 excess gross loss, and much shorter average holds (5s vs 16s).

Use the REAL and SYNTH compact references as the baseline/goal pair before reopening the large raw evidence.

## R9 MT5 functional summary — Gamma inspection closed

The owner authorized a one-time read-only inspection of the R9 Gamma baseline solely to summarize R9 itself. That exception is complete and closed.

Canonical DELTA-owned references:
- `research/delta/reference/R9_MT5_EA_FUNCTIONAL_SUMMARY.md`
- `research/delta/reference/R9_MT5_EA_FUNCTIONAL_FAST_REFERENCE.json`

R9's canonical functional chain is:
`new M1 minute -> frozen midpoint ±$0.15 virtual bracket -> spread + completed-M5 ATR session gate -> completed-S1 displacement/efficiency/range/turn gate -> market entry -> hard SL / +$0.10 activation / $0.03 trail / 30s max hold -> opposite-side same-minute rearm up to 3 -> next-minute reset`.

The inspected R9 source contains no multi-specialist router, news calendar, daily/weekly governor, dynamic lot sizing, martingale/grid, fixed take-profit, ML inference, or intermarket logic. Those are DELTA additions, not hidden R9 behavior.

Do not reopen Gamma or another prior internal lineage unless the owner explicitly authorizes another exception.

## DELTA_002 Dukascopy tick lab — VERIFIED_DURABLE

Canonical runtime:
- `research/delta/lab/dukas_tick_lab.py`
- `research/delta/lab/run_candidate_month.py`
- `research/delta/lab/candidate_template.py`
- `research/delta/qa/DELTA_002_DUKASCOPY_TICK_LAB_QA.py`
- `research/delta/checkpoints/DELTA_002_LAB_QA.json`
- `research/delta/DELTA_002_DUKASCOPY_TICK_LAB_REPORT.md`

Verified Jan-Jul surface:
- 57,527,562 exact ordered Dukascopy ticks;
- 920,443,680-byte core memmap cache at 16 bytes/tick;
- 28,697,391 independently matched 250ms bars;
- 10,696,540 independently matched 1s bars;
- all seven monthly source hashes/rows/order/Ask-Bid/right-edge/execution-side checks PASS;
- month-isolated candidate jobs with atomic completion checkpoints;
- August not accessed.

The raw Bid/Ask tick stream is execution truth. Derived candle caches are causal state only. The current broker layer preserves native spread and executable quote sides, with configurable commission/slippage/latency/contract size, but it does **not** yet claim Coinexx MT5 parity.

Next phase: a separately preregistered Coinexx/R9 parity calibration covering symbol properties, costs, stop/freeze/fill/deviation behavior, margin/stop-out, and R9 OnTick/order-lifecycle ordering. August remains sealed.

## DELTA_003 Coinexx R9 parity — VERIFIED_DURABLE

Canonical files:
- `research/delta/lab/coinexx_r9_adapter.py`
- `research/delta/lab/r9_parity_runner.py`
- `research/delta/reference/DELTA_003_COINEXX_EXECUTION_CONFIG.json`
- `research/delta/qa/DELTA_003_COINEXX_R9_PARITY_QA.py`
- `research/delta/checkpoints/DELTA_003_PARITY_QA.json`
- `research/delta/DELTA_003_COINEXX_R9_PARITY_REPORT.md`

Full January Coinexx parity: 21 files / 7,699,274 logger rows / zero event mismatches / exact MT5 January accounting (31,915 trades, 13,947 wins, $3,785.28 gross profit, -$10,436.90 gross loss, -$6,651.62 net). July 1 provides a zero-mismatch post-DST cross-check.

Frozen 0.01-lot execution economics: two-decimal XAUUSD, $0.01 point/tick, $1 P/L per $1 price move, -$0.01 commission on entry and exit deals, BUY entry Ask/exit Bid, SELL entry Bid/exit Ask, and protective stops at the first executable quote after crossing. R9's observed-position latch is required before same-minute rearm.

Native Dukascopy is deliberately kept separate: January median native spread is about $0.70 versus Coinexx $0.19, so only about 0.0476% of Dukascopy January ticks satisfy R9's $0.25 spread gate. This is a feed-surface difference, not a parity defect.

Next unit: preregister and build a distinctly labeled Coinexx-like modeled execution/quote-cost surface over the independent Dukascopy path. Do not overwrite DUKAS_NATIVE. August remains sealed.

## DELTA_004 Coinexx-like Dukascopy surface — VERIFIED_DURABLE

Canonical files:
- `research/delta/lab/coinexx_like_surface.py`
- `research/delta/reference/DELTA_004_COINEXX_SPREAD_PROFILES.json`
- `research/delta/qa/DELTA_004_COINEXX_LIKE_DUKASCOPY_QA.py`
- `research/delta/checkpoints/DELTA_004_SURFACE_QA.json`
- `research/delta/DELTA_004_COINEXX_LIKE_DUKASCOPY_REPORT.md`

Surface labels are mandatory:
- `DUKAS_NATIVE` — untouched Dukascopy Bid/Ask;
- `DUKAS_COINEXX_LIKE_P50` — median-friction sensitivity;
- `DUKAS_COINEXX_LIKE_P75` — default research surface;
- `DUKAS_COINEXX_LIKE_P90` — stress-friction sensitivity;
- `COINEXX_PARITY` — preserved R9 REAL logger/report parity surface.

Default P75 Jan-Jul R9 control: 234,417 trades; 104,294 wins; $29,243.07 gross profit; -$78,244.86 gross loss; -$49,001.79 net. Versus R9 REAL, aggregate errors are -0.94% trades, +1.86% wins, -3.11% gross profit, -2.76% gross-loss magnitude, and -2.55% net-loss magnitude. All preregistered monthly/aggregate tolerances pass.

P50/P75/P90 spreads are derived from R9 REAL Coinexx evidence only. No SYNTH outcome was used to calibrate the modeled environment. February-July use 90 minutes of prior-month raw Dukascopy state warm-up; scoring begins at the target month boundary.

The lab is now ready for the first owner-governed January candidate campaign. Before candidate compute, freeze the exact end boundary of the first-2.5-week January filter. August remains sealed.

## Research objective

Rebuild a high-activity causal Entry+Hold architecture around the R9 evidence base while preserving real chronology, causal execution, and trade velocity.

Research should use REAL/SYNTH/OVERFIT evidence to answer *where R9's apparent edge came from and why REAL lost it*, then reconstruct only causal mechanisms on ordered REAL/Dukascopy chronology.

Trade velocity is not a cosmetic secondary metric. Any candidate must report:
- opportunity count;
- selected trade count;
- retention versus declared reference;
- winning-trade count;
- entry quality;
- hold persistence/survival;
- net/PF/expectancy;
- gross loss and drawdown.

## Current next action

Preregister DELTA_005 as the first owner-governed January candidate campaign. Freeze the exact first-2.5-week January end boundary before compute. Use DUKAS_COINEXX_LIKE_P75 as the default research surface, P50/P90 as execution-friction sensitivities, and DUKAS_NATIVE as the independent robustness control. August remains sealed.

## Subsequent research

The first scientific campaign should decompose R9 into:
- ENTRY/ACTION timing and directional selection;
- HOLD/PERSISTENCE survival;
- EXIT/HARVEST;
- execution friction/path-density transfer REAL↔SYNTH;
- opportunity/trade-count retention.

Use paired REAL/SYNTH evidence to localize the transfer failure, then test reconstructible mechanisms causally on original ordered quotes. Do not simply stack indicators.

## Recovery instruction for the next chat

If the UI times out:
1. inspect `CURRENT_STATE.json`;
2. inspect the active DELTA unit manifest;
3. verify GitHub/Drive artifacts that already exist;
4. resume the same unit at its first missing durability step;
5. do not repeat verified work;
6. do not advance the cursor until readback/hashes pass.

This document is the bootstrap pointer, not a substitute for the repository state.
