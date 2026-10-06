# DELTA R003 — Direction + Hold Causal Grammar White Papers

**Date:** 2026-10-02  
**Status:** RESEARCH_ONLY / NO TESTING  
**Active parent:** `DELTA_004_COINEXX_LIKE_DUKASCOPY_RESEARCH_SURFACE`  
**Scope:** ENTRY + INITIAL-HOLD  
**August 2026:** SEALED  
**MQL5:** NOT AUTHORIZED

## Stage folder

Google Drive folder:

`DELTA R001 Direction-Hold Candidate Harvest — Research Only`

https://drive.google.com/drive/folders/1iCg7Ptl8zRQ-5QUFGSuB7sPTqsNKzxiX

The working GOV-014 harvest workbook and pre-backtest shortlist document were moved into this stage folder. Seven candidate/component white papers were created there.

## Frozen v0 timeframe-role grammar

DELTA's full tick-rooted hierarchy remains authoritative.

For R001 v0 direction/hold research, the documented role bundles are:

- Micro observation: TICKS, S0.25, S1
- Fast execution context: S5, S15, S30, S45
- Execution structure: M1, M5
- Intermediate structure: M15, M30
- Higher structural context: H1, H4

Other DELTA timeframes remain available but are not part of the R001 v0 feature grammar unless a later research unit explicitly adds them.

## Candidate/component white papers

### DH-01 — Nested Direction State
Role: shared context infrastructure.
Drive:
https://docs.google.com/document/d/1WrDPUavWb-bbv7gmxnnlEAFjT1NA9wYbPAwl-ayREAw/edit

Frozen grammar includes:
- midpoint signal features;
- NetMove, Path, SignedEfficiency, DirectionalDisplacement;
- causal confirmed swing structure;
- trend-within-trend state taxonomy;
- completed-bar/right-edge anti-lookahead rules.

### DH-02 — Breakout Retest Rebreak Specialist
Role: standalone entry specialist.
Drive:
https://docs.google.com/document/d/18KpLADXCt-MlIQgZ4j6papHdE7SUtrl8kVTbn0x1XNc/edit

Frozen state chain:
`IDLE -> ARMED -> BROKEN -> ACCEPTED_BREAK -> RETESTING -> RETEST_HELD -> REBREAK_CONFIRMED -> ENTRY_ELIGIBLE`
with explicit FAILED / EXPIRED branches.

### DH-03 — Pullback Continuation Specialist
Role: standalone entry specialist.
Drive:
https://docs.google.com/document/d/13pa0KSxVy93yajDEGAIkeY4V8Z3egMDIPxPV0nM3ia8/edit

Frozen logic separates:
- parent trend validity;
- fast countertrend pullback;
- exhaustion candidate;
- local reclaim;
- reacceleration;
- specialist-specific early invalidation.

### DH-04 — Compression Expansion Continuation Specialist
Role: standalone entry specialist.
Drive:
https://docs.google.com/document/d/1S9VYfq3DrDqabMaHHqq6BB2ueB-CPBw9OLYnFOZlQDg/edit

Frozen features include:
- causal compression box;
- ATR/true-range-normalized compression;
- frozen box at arm time;
- expansion probe/acceptance/quality;
- initial invalidation on accepted re-entry into the box.

### DH-05 — Failed-Break Reversal Specialist
Role: standalone reversal specialist.
Drive:
https://docs.google.com/document/d/1mIcrUUeK0lGwfR6L_26O47DQxQV7xygbnFcnkvE4s6k/edit

Frozen state chain:
`IDLE -> PROBE -> FAILURE_CANDIDATE -> REENTRY -> RECLAIM_CONFIRMED -> FAILED_BREAK_CONFIRMED -> REVERSAL_REBREAK -> ENTRY_ELIGIBLE`.

An accepted original breakout is explicitly routed away from DH-05.

### DH-06 — Quote-Pressure Initial-Hold Persistence
Role: shared initial-hold component.
Drive:
https://docs.google.com/document/d/1MAkyDsu1TK7VC8Rlx4ahlIxznPFEJKy_uX4k31heIhc/edit

Frozen deterministic tick-derived features:
- FavDisplacement
- Path
- DirectionalEfficiency
- StepBalance
- BidAskImpulse
- RetreatFraction
- SpreadStress
- TickRate / TickRateRatio

Observation windows:
250 ms, 1 s, 3 s, 5 s.

The component is explicitly a quote-pressure proxy, not true centralized limit-order-book OFI.

### DH-07 — Specialist-Aware Initial-Hold State Machine
Role: shared initial-hold state machine.
Drive:
https://docs.google.com/document/d/1CyZ-WBMpBCfQfz_dnfbOAfCktDgbC7uPlW-72NGM7ww/edit

Frozen checkpoints:
fill, 250 ms, 1 s, 3 s, 5 s, 10 s, 15 s.

Frozen high-level states:
`FILLED_VULNERABLE -> MICRO_ASSESSMENT -> DEVELOPING / UNCERTAIN_HYSTERESIS -> ESTABLISHING -> INITIAL_HOLD_SURVIVED`
with EARLY_INVALIDATE and HARD_STOP_EXIT branches.

Mature hold, profit exit, and high-profit logic remain deferred.

## Working workbook index

The R001 working workbook now contains a new tab:

`11 White Papers`

It records each white paper, role, stage, grammar status, threshold status, testing status, and Drive link.

Working workbook:
https://docs.google.com/spreadsheets/d/1C2EOJ2WDZgVMcGG8s1WPY46-Q4U8QQXUhZytqPJVsY0/edit

## Threshold policy

The white papers freeze:
- feature identity;
- formula meaning;
- timeframe ownership;
- state-transition order;
- causal visibility;
- specialist thesis/invalidation semantics.

They intentionally do **not** freeze optimized numeric thresholds.

Thresholds remain parameter slots for later preregistration before Stage-A Dukascopy replay.

## Testing state

- empirical event harvesting from Dukascopy: NOT STARTED
- Stage-A preregistration: NOT STARTED
- Python/tick replay: NOT STARTED
- promoted candidate: NONE
- metric locks: NONE
- GOV-018 heavy synthesis: DORMANT
- August: SEALED
- MQL5: NOT AUTHORIZED


## Timeout recovery and canonicalization — 2026-10-02

A delivery-timeout sequence created an additional exploratory workbook and DH-Cxx package shortlist outside the R001 stage folder. Those artifacts are preserved but renamed with the prefix:

`ZZ_SUPERSEDED_TIMEOUT_EXPLORATORY__`

They are **not** active candidate definitions, not Stage-A candidates, and not substitutes for the DH-01 through DH-07 white papers.

The canonical R001 causal-grammar stage is now the Drive folder:

https://drive.google.com/drive/folders/1iCg7Ptl8zRQ-5QUFGSuB7sPTqsNKzxiX

Folder-level index:

`00 STAGE INDEX — DELTA R001 Direction-Hold Candidate Harvest — Research Only`

https://docs.google.com/document/d/1Tpx2ZZTwHZqtVQv6mVgyZ0acADFQ1OugcpDDNpkoGBA/edit

The common vocabulary document was moved into the same stage folder:

`DELTA R003 — Causal Direction + Initial-Hold Research Vocabulary`

https://docs.google.com/document/d/1ei6AcvQUO1Wzx4EUlVaCGWjdl6pCBajcjrzWEtMs3-w/edit

## Source-traceability QA

The source-anchor labels in the candidate white papers were converted to live external hyperlinks where the source was reconstructible and directly relevant.

Fresh 2026 research cross-checks support the architecture but **do not authorize importing source thresholds**:

- MQL5 Market Microstructure Part 7 demonstrates causal regime classification and smoothed regime transitions; its published NQ calibration is not transferable to XAUUSD.
  https://www.mql5.com/en/articles/22940
- MQL5 Market Microstructure Part 9 explicitly separates pullback depth from trend existence and reports that its own NQ hypothesis did not generalize cleanly across regimes. This is a direct reason to keep DH-03 threshold slots pending rather than copying Fibonacci or lookback constants.
  https://www.mql5.com/en/articles/23628
- MQL5 Swing Extremes and Pullbacks Part 3 distinguishes raw swing candidates from structurally validated levels using break, displacement, sweep, and respect concepts. DELTA preserves only the reconstructible structural idea and retains its own causal swing grammar.
  https://www.mql5.com/en/articles/21888
- MQL5 volatility-breakout research describes the false-breakout problem and volatility-relative breakout confirmation, supporting DH-04's contraction/expansion research family without validating any specific ATR multiplier.
  https://www.mql5.com/en/articles/19459
- MQL5 Bootstrap IV contrasts fixed trailing behavior with ATR-adaptive trailing. DELTA uses this only as architectural support for specialist-aware initial-hold treatment; mature trailing/exit research remains deferred.
  https://www.mql5.com/en/articles/23882
- Cont, Kukanov & Stoikov support short-horizon order-flow imbalance as a price-impact variable in full limit-order-book data. DH-06 therefore remains explicitly a **quote-pressure proxy**, not true OFI.
  https://arxiv.org/abs/1011.6402

## Canonical white-paper stage after recovery

Active documented objects:

- DH-01 — shared nested-direction context infrastructure
- DH-02 — breakout/retest/rebreak entry specialist
- DH-03 — pullback-continuation entry specialist
- DH-04 — compression/expansion continuation specialist
- DH-05 — failed-break reversal specialist
- DH-06 — quote-pressure initial-hold persistence component
- DH-07 — specialist-aware initial-hold state machine

No DH-Cxx package is active in this stage.

The next legal research step is preregistration design / parameter-slot definition for a first testing queue. Dukascopy/Python testing still requires a separate owner transition.


## R037 final specialist consolidation — 2026-10-05

The earlier pre-backtest status in this historical R003 document is superseded by the current R037 consolidation below. The original causal grammars remain preserved; this section records their present empirical/reconstruction disposition.

### Frozen specialist roster

- **DH-01 — Nested Direction State:** retain as shared causal direction/context infrastructure. It is not a standalone entry specialist. Its active reconstructed use is the parent-context concept required by DH02-S08. Exact historical DH01 aggregation/veto placement remains provenance-limited.
- **DH-02 — Breakout Retest Rebreak Specialist:** retain two frozen reconstructed streams for refinement/integration: **DH02-S11** and **DH02-S08**. S11 preserves causal persistent failure acceptance; S08 preserves causally valid DH01 parent direction at rebreak/entry eligibility. Both remain provenance-limited and non-promoting rather than fabricated exact historical reconstructions.
- **DH-03 — Pullback Continuation Specialist:** retain **DH03-S06** using the best reconstructible frozen surrogate `POST_PULLBACK_REARM_FRESH_EXHAUSTION_STRICT_POST_ORIGINAL_PULLBACK_PIVOT`. Exact historical generator parity is not claimed.
- **DH-04 — Compression Expansion Continuation Specialist:** keep as forensic/research reserve. No DH04-derived execution stream currently belongs to the frozen active specialist roster; adjacent compression/expansion screens did not produce a durable survivor.
- **DH-05 — Failed-Break Reversal Specialist:** retain **DH05-S06** using the frozen 09Z best reconstruction. Its residual repeated-attempt counter/reset mismatch is explicitly provenance-limited; do not infer or retune the missing historical helper from sample fit.
- **DH-06 — Quote-Pressure Initial-Hold Persistence:** retain only as a shared post-entry evidence component. It is not a standalone entry generator or promoted order-flow specialist.
- **DH-07 — Specialist-Aware Initial-Hold State Machine:** retain as the common early post-entry orchestration layer for admitted specialist trades. Mature hold/exit and capital escalation remain deferred.

### Current tested execution streams

The frozen R032 provenance-limited specialist set is:

1. `DH03-S06` — pullback continuation;
2. `DH05-S06` — failed-break reversal;
3. `DH02-S11` — breakout/retest/rebreak with persistent failure acceptance;
4. `DH02-S08` — breakout/retest/rebreak with DH01 parent-direction context.

All four are rebuild-ready from current DELTA artifacts. Their missing historical producer details are provenance limitations, **not unfinished current helper code**.

The integrated scheduler hypothesis remains `BACKBONE_FIRST_FLAT_ONLY_CONFIG_ORDER` under the R032 provenance-limited surrogate parent. Exact historical R032-C03 parity is not claimed, and no final DELTA EA is promoted.

### Late R037 harvest disposition

The later 17-series source-class campaign produced several temporary Stage-A or later-January clues, but no new entry family survived the required robustness path strongly enough to join the frozen specialist roster. PLSR/PDHSR, HTAR, ASRB, SIFVG, VCE, XECTSB and neighboring structural/session/liquidity families were retired or retained only as forensic reserve after holdout/monthly failure. Checkpoint 17DE–17DG also completed and retired the Asia-range directionality branch with no Stage-A survivor.

**Owner decision:** pause new specialist harvesting. The next DELTA workstream is specialist **refinement, interaction/ownership integration, and shared initial-hold integration**, not another open-ended source-class harvest.

August 2026 remains **SEALED**. MQL5 translation remains **NOT AUTHORIZED** until the owner explicitly opens that stage.
