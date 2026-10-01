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

**Owner hold:** Do not load R9 REAL, R9 SYNTH, R9 OVERFIT, R9 ticklog, or Coinexx report files yet. Continue defining goals until the owner explicitly authorizes evidence loading.

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

## Recorded next action: DELTA_001

Run **DELTA_001_R9_SOURCE_EVIDENCE_PARITY_PREFLIGHT**.

It must:
- verify both R9 MQL5 source identities and behavior-critical input defaults;
- verify REAL/SYNTH report availability and roles;
- verify REAL/SYNTH tick index, daily manifest, validation and paired-corpus availability;
- verify Dukascopy Jan-Jul canonical hashes;
- register OVERFIT/ORACLE quarantine;
- verify DELTA Drive + GitHub write/readback;
- freeze the initial data walls and research metric schema;
- produce a complete rebuild-ready DELTA manifest.

DELTA_001 performs no strategy optimization.

## After DELTA_001

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
