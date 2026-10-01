# DELTA GOV-001 — Causal, Durable, MT5-Rebuild-Ready Research Contract

**Effective:** 2026-10-01  
**Branch:** `delta`  
**Status:** MANDATORY  
**Predecessor:** None. DELTA is a standalone clean-room research lineage.

## 1. DELTA clean-room reset

DELTA begins only from the authoritative R9 MT5 source/evidence corpus registered inside the DELTA namespace.

Prior internal research lineages are outside scope. Active DELTA work must not read, import, cite, compare, port, merge, reconstruct, or use their code, documents, metrics, hypotheses, candidate logic, performance results, handoffs, controller state, or governance.

Permitted research inputs are limited to:
- the R9 engineering/evidence baseline explicitly registered under `research/delta/reference/`;
- DELTA-created artifacts;
- the registered ordered market-data corpus;
- reconstructible public research used to generate independently testable causal hypotheses.

Any violation of this clean-room boundary invalidates the affected unit and blocks promotion.

## 2. Canonical R9 authority

The engineering baseline is:
- `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`
- `Experts/GoldMuwahahaMiner_R9_TickLogger.mq5`

The research evidence hierarchy is:
1. **R9 REAL** — broker-native execution-failure benchmark and execution/path/lifecycle evidence.
2. **R9 SYNTH** — teacher/north-star reference only; never execution truth.
3. **R9 OVERFIT/ORACLE** — quarantined hypothesis/capacity source only; never execution input.
4. **Ordered Dukascopy Jan-Jul 2026** — independent causal market replay source.
5. **August 2026** — SEALED blind holdout until explicit owner authorization after frozen candidate + human QA.

Exact source identities live in `research/delta/reference/`.

## 3. Co-primary human gate: edge + activity

DELTA treats **ENTRY+HOLD quality and trade-count/opportunity retention as co-primary**.

Every research unit must preregister:
- reference population;
- reference trade/opportunity count;
- minimum acceptable count/retention for that unit;
- entry quality metric;
- hold/persistence metric;
- economic metric;
- drawdown/gross-loss metric.

A result cannot be called an improvement if it reaches the economic target mainly by starving the trade population below the preregistered floor. If the owner has not supplied a numeric floor, promotion remains `OWNER_REVIEW_REQUIRED` regardless of profit.

Always report raw trade count and retention percentage next to profit/PF/expectancy.

## 4. No-lookahead and timing contract

All features/signals must be known at decision time.

- Tick features use only ticks through the declared source ordinal.
- A bucket/bar is visible only at its **RIGHT edge** unless the feature is explicitly an in-progress tick-state feature whose exact as-of construction is preserved.
- Pivots requiring right bars activate only after those bars have closed.
- Same-millisecond tie breaking must use deterministic source ordinal.
- Future MFE/MAE, SYNTH outcome, teacher score, oracle direction, future extrema, exit result, or later state may be labels/diagnostics only.
- Every cache records timestamp convention, known-at time, missing-bucket handling and exact feature order.

A causality violation invalidates the affected unit and all descendants.

## 4A. Tick-rooted nested timeframe contract

`research/delta/governance/DELTA_GOV_002_TICK_ROOTED_NESTED_TIMEFRAME_CONTRACT.md` is mandatory for all DELTA market-state construction.

The ordered tick stream is the authoritative chronology. Every supported candle is reconstructed directly from ticks using its own exact boundary rule. The nested timeframe sequence is an analytical hierarchy, not permission to approximate a higher timeframe from an incompatible lower-timeframe partition.

The required hierarchy is:
`TICKS -> 250ms -> 1s -> 5s -> 15s -> 30s -> 45s -> M1 -> standard MT5 periods through D1`.

Python research and any eventual MT5 EA must share the same timestamp normalization, source ordering, boundary rules, BID/ASK aggregation, empty-interval semantics, and completed-bar visibility. Candle-parity failure blocks promotion.

## 5. R9 teacher quarantine

R9 SYNTH and OVERFIT/ORACLE may accelerate research by:
- ranking failure modes;
- defining labels;
- identifying path/lifecycle regimes;
- estimating theoretical capacity;
- generating reconstructible hypotheses.

They may **not** be:
- live features;
- execution gates;
- same-sample memorized selectors;
- future-informed routing;
- a substitute for causal REAL/Dukascopy validation.

Every derived teacher feature must identify its causal/label side explicitly.

## 6. Data-wall discipline

Jan-Jul have been heavily inspected historically. DELTA must not relabel them pristine OOS.

Permitted uses:
- discovery;
- nested chronological CV;
- walk-forward robustness;
- leave-one-month-out analysis;
- mechanism falsification;
- execution/path forensics.

August remains sealed. It may be opened only after:
1. candidate logic is frozen;
2. rebuild manifest is complete;
3. human-facing QA passes;
4. owner explicitly authorizes spending the holdout.

Once August is opened for a candidate, record the exact candidate/commit before access and never reuse August as fresh OOS for a revised descendant.

## 7. Preregister before compute

Every bounded unit starts with a committed manifest before testing. The manifest must state:
- hypothesis and falsification condition;
- parent and rollback target;
- source/data walls;
- exact features/logic;
- parameter neighborhood;
- cost/fill assumptions;
- trade-count reference/floor;
- primary metrics;
- human-QA relevance;
- expected artifacts.

Do not tune the hypothesis after observing its protected evaluation result. A materially changed hypothesis gets a new unit ID.

## 8. Atomic artifact transaction

A unit is not `VERIFIED_DURABLE` until all of these complete in order:

1. preregistration committed;
2. producing source/helpers committed;
3. bounded compute completes;
4. outputs written atomically;
5. QA runs;
6. large/binary evidence uploaded to DELTA_RESEARCH Drive;
7. Drive files read back;
8. hashes/IDs written to manifest;
9. compact outputs + QA committed;
10. GitHub files read back;
11. manifest sets `python_rebuild_ready=true`;
12. `CURRENT_STATE.json` advances last.

If UI/tool/runtime failure occurs before step 12, resume the **same unit at the first missing durability step**. Never jump to a new scientific unit because the chat timed out.

## 9. Mandatory reconstructibility

If an artifact influences a result, it must be durably stored or deterministically regenerable.

Preserve as applicable:
- runner and every helper;
- feature/cache builders;
- candidate generator;
- pre-ownership proposal ledger or exact generator;
- prediction/probability surface;
- ownership/scheduler logic;
- state-machine persistence/debounce/expiry/rearm;
- labeler;
- replay/execution engine;
- model training and export;
- configs/seeds/dependencies;
- results including null/failed screens;
- QA;
- hashes;
- exact reconstruction command.

Selected trades alone are insufficient.

## 10. Runtime/UI resilience

Heavy research is split into bounded jobs. Each job has:
- deterministic job ID;
- code commit;
- source hash;
- bounded scope;
- heartbeat/progress record when external/local runner is used;
- attempt manifest;
- atomic result;
- timeout;
- retry policy;
- DONE manifest.

Status vocabulary:
`PLANNED -> RUNNING -> LOCAL_COMPLETE -> DRIVE_PERSISTED -> GITHUB_COMMITTED -> VERIFIED_DURABLE`
or `FAILED_RECOVERABLE / REJECTED`.

Completed durable work is never rerun merely because a Chat/UI message failed.

## 11. Research-speed hierarchy

Use the cheapest sufficient evidence first:
- L0 compact R9 corpus index.
- L1 daily/event indexes and paired monthly research assets.
- L2 exact daily/monthly tick partitions required by the hypothesis.
- L3 full MT5 reports/raw ticklogger reconstruction only when L0-L2 cannot answer the audit question.

Do not repeatedly load or rebuild heavy canonical corpora that are already validated.

## 11A. Staged research-speed contract

`research/delta/governance/DELTA_GOV_003_RESEARCH_SPEED_STAGE_GATE_CONTRACT.md` is mandatory.

New candidates are screened first on the owner's first 2.5 weeks of January. Only candidates that satisfy the separately frozen owner acceptance requirements advance into January-through-July research.

January-through-July replay is split into independent monthly jobs with durable checkpoints to control runtime/memory pressure and support resume-from-first-incomplete-month recovery. Behavior-changing refinements create new candidate versions; completed monthly results are immutable evidence.

## 12. Community-source rule

A complex strategy/indicator from public community research may enter DELTA only if its logic is sufficiently disclosed to reconstruct a faithful causal test. Opaque/non-reconstructible systems are not candidates.

Multilingual sources may generate hypotheses, but original ordered market replay determines economic evidence.

## 13. MT5 translation gate

No owner-facing MT5 candidate review until:
- `python_rebuild_ready=true`;
- `mt5_translation_ready=true`;
- authoritative Python parent is frozen;
- feature equations/order/timing are frozen;
- state machine is executable;
- model inference/export is preserved;
- BUY/SELL quote-side execution is specified;
- ownership/concurrency is specified;
- session/DST behavior is specified;
- risk/lot behavior is specified;
- parity fixtures exist;
- trade-count behavior is reconciled;
- human QA has passed.

Owner approval is required **before** candidate MQL5 coding and again after Coinexx Strategy Tester verification.

## 14. Human-facing QA gate

Before a sealed holdout or MT5 translation review, provide a compact packet containing:
- accepted winners;
- accepted losers;
- rejected setups;
- ownership-blocked setups;
- boundary/tie cases;
- exact entry/exit quotes;
- state-machine explanation;
- expected versus reconstructed PnL;
- trade-count/month reconciliation.

Human QA records PASS / PASS_WITH_CORRECTIONS / FAIL. Corrections that alter trading behavior create a new scientific unit.

## 15. Supersession and rollback

Never silently overwrite producing logic. A replacement:
- uses a new unit/version;
- identifies superseded artifact;
- records rollback target;
- preserves old commit/path.

Git history is evidence; `CURRENT_STATE.json` is the active cursor.

## 16. DELTA first action

DELTA_001 is an **evidence/source/parity preflight**, not strategy optimization:
- verify R9 HybridGate and TickLogger identities;
- verify REAL/SYNTH report and tick-index availability;
- verify OVERFIT quarantine references;
- verify Dukascopy Jan-Jul hashes/index;
- register Drive IDs;
- establish exact DELTA research walls;
- produce the first rebuild-ready manifest.

Only after DELTA_001 is VERIFIED_DURABLE may DELTA begin new Entry+Hold research.
