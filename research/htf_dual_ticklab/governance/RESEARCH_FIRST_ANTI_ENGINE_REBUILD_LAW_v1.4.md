# XAUUSD HTF EA — RESEARCH-FIRST / ANTI-REBUILD / ANTI-AUDIT-LOOP LAW v1.4

**Policy ID:** XAU-HTF-RESEARCH-FIRST/1.4
**Effective:** 2026-10-18
**Status:** BINDING ADDITIVE research-workflow governance. NOT a trading-performance certification.
**Scope:** All future XAUUSD HTF chat handoffs, research branches, researcher agents, Python experiments, tests, recovery scripts, and MT5 EA development.
**Authority:** Latest explicit user instruction > current source authorization and investor mandate > the complete cumulative v1.0 anti-drift, v1.1 whole-system, v1.2 anti-amnesia, v1.3 emergency handoff and this v1.4 research-first law. This document does not alter source permissions, accepted evidence, trading code, UTC calculations, or investor constraints.

## Governing prohibition — BACKTEST ENGINE IS NOT THE RESEARCH TASK

The **Coinexx real-bid/ask tick replay and Dukascopy independent tick replay already exist as a shared, versioned Python research infrastructure** under `research/htf_dual_ticklab`. The historically validated UTC-corrected runtime is:
- https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/carson/htf-dual-broker-utc-alignment-v0.3/research/htf_dual_ticklab
- Pinned release commit: `ca4b58aec597174b6f6d18ab2f36cba6836e4f4c`.
- Synchronization and acceptance documents: https://drive.google.com/drive/folders/15etN9KMQxZKbApGu0gtml1R2a6SUET6N
- Previous rollback: `8754155bfa9bfe2ce62d3f97e8259da32dfd829f` on `carson/htf-dual-broker-replay-recovery-v0.2`.
- The established infrastructure is a **research replay baseline**, not live-fill simulation certification, alpha certification, or a complete portfolio engine. Its performance limitations remain disclosed.

**Do not reimplement or regenerate either broker's tick-replay engine merely because a new chat, agent, branch or research experiment started. Do not spend a research session re-auditing both replay engines when there is no concrete defect.** Reuse approved code by pinned Git commit, checked-out package, or a minimal import/adapter. No divergent ad-hoc reconstruction of the UTC reader, quote schema, chronology, source-hash registry, bar builder, fills, ledger, or reporting stack. Where newer research branches contain verified extensions, inspect and preserve their actual complete lineage before choosing the current technical baseline; **do not reset to v0.3 and erase subsequent work**.

## LAW 1 — Separate infrastructure acceptance from alpha research

Research objective: develop and test causal multi-timeframe/multi-session/multi-regime entry, lifecycle, exit, risk, signal-routing and portfolio-level mechanisms, subject to explicit active research scope. Environmental QA is a prerequisite service, not a research deliverable. An infrastructure PASS must be **reused as evidence**, not treated as an invitation to repeat its entire audit. A prior no-trade replay certifies ingestion/continuity only, never profitable strategy logic.

## LAW 2 — Fast-path new-chat bootstrap, not a rebuild

Before a new scored experiment, perform only the **bounded continuity check**:
1. Read the latest primary Drive handoff, exact cumulative governance, current approved source supersession and CURRENT research receipt/complete result files (research may have progressed since the October 16 QC release).
2. Verify the **live exact GitHub HEAD and ancestry of the research branch actually containing the last work**, and the pinned infrastructure code dependency. Do not default to `main`, R9, an old governance-only branch, or v0.3 as the newest research HEAD.
3. Verify that the registered source names/clock profile are unchanged. During execution, check SHA-256 on **inputs actually used**, or reuse an independently verified immutable receipt tied to those exact bytes and code. Do not rehash/re-download/replay every historical month just to open a chat.
4. Run a **tiny deterministic import/reader/smoke test only when needed to establish the local environment**, and reuse the recorded passing CI/test receipt if the code and data fingerprint are unchanged. Do not rerun months of source data or full regression suites as routine new-chat onboarding.
5. Announce LAST_RESEARCH_EXPERIMENT, LAST_COMPLETE_ARTIFACT, NEXT_RESEARCH_ACTION, exact verified code/data references, and carry out the assigned scientific task.

Default target for this routine preflight is **under 10 minutes**. This is an **operational timebox, not a safety bypass or investor criterion**. If genuinely blocked, issue a narrowly scoped defect ticket; do not spontaneously expand into an open-ended rebuild.

## LAW 3 — Exhaustive backtester re-audit prohibited without a trigger

A deep engine investigation is authorized **only** by:
(A) a reproducible wrong fill/order/clock/tick/ledger behavior, direct evidence of look-ahead or contamination, actual data hash mismatch, corrupted checkpoint, or broken unit/regression test;
(B) a deliberately proposed change to the broker data adapter, time normalization, account/margin/risk/execution semantics or another critical core interface;
(C) a user-requested infrastructure audit/rebuild or explicit scoped research requirement.
An unprofitable signal, an invalidated candidate, unexpectedly poor accuracy, a lower-than-R9 result, an agent's curiosity, a chat restart, or the age of a passing test **is NOT an audit trigger**. Negative strategy results must be recorded as strategy evidence; do not assume an engine error merely because results are disappointing.

## LAW 4 — Bounded defect triage and smallest repair

Each trigger requires a written ENGINE_DEFECT_TICKET: symptom, full failing original artifact, smallest reproducible scenario, expected/actual result, exact file SHA/commit, which output may be compromised, severity, and user/scientific decision. FIRST isolate via a small frozen fixture; do NOT rerun January–September as a fishing expedition. Pin a last-known-good baseline. Repair only the affected module on a lineage-preserving isolated branch; add targeted regression test; then rerun affected paths and paired regression before deciding whether a wider replay is necessary. Keep original input files, invalid results, and full research trace unchanged. If unresolved, **block only impacted scored conclusions**, while independent unaffected research proceeds with clear caveats. A safety-critical defect affecting the whole engine blocks scored trading claims, not all scientific thought or documentation.

## LAW 5 — Research-first time accounting and anti-audit spiral

On every research session, predeclare the exact research question, planned experiment/EA subsystem, outcome criteria, deliverables, and actual artifacts that already exist. Record hours/effort under RESEARCH, ROUTINE_PREFLIGHT, ENGINE_DEFECT_REPAIR, and ARCHIVAL. If any untriggered engine QA starts expanding, STOP and return to the research objective. Do not improve accuracy claims by suppressing negative outcomes or treating this guard as an excuse to skip a necessary safety fix. Do not repeat completed tests merely to produce a new assistant-authored report.

## LAW 6 — Frozen API and compatibility over reconstruction

Prefer reusable imports and thin compatibility adapters. Preserve original schema: Coinexx raw timestamp plus verified UTC correction (January–February -120m, March DST transition, thereafter -180m in the calibrated 2026 profile); Dukascopy UTC unchanged; separate broker streams; exactly approved source registry; causal completed bars; and existing declared execution assumptions. Any revised interface must have a version, migration adapter, consumer-impact inventory, smoke test, and a committed changelog. No silent source or clock redefinition. Historical recovery/smoke fixtures are not evidence of live MT5 order handling.

## LAW 7 — Preserve subsequent research lineage

Existing research may now include later R00 and other task-specific branches and complete archived experiment outputs. Those are research artifacts requiring exact live verification, NOT grounds to discard them by restarting from an older infrastructure branch. Find the actual latest approved active experiment from ORIGINAL Drive receipts, pinned code, raw result arrays and artifact fingerprints. Do not infer the active branch solely from the most recent branch name or a compressed chat summary. Never retrain, refit, rerun, rebuild or re-optimize a previously complete experiment unless new evidence establishes a targeted reason. Keep superseded reports and invalidations; append decisions.

## LAW 8 — Preserve scientific and whole-system standards

Maintain complete evidence, negative periods, source hashes, multi-broker reproduction on matched corrected UTC coverage, $100/$200 constraints, realistic quoted spread/latency assumptions, leak-free features, declared unverified assumptions, and eventual paired whole-EA account comparisons. A component's standalone profit or failure is diagnostic only. The guard prohibits **redundant infrastructure auditing**, not mandatory causal validation of a novel trading hypothesis, new feature, changed critical code, or implementation of a complete shared-capital executor.

## LAW 9 — Exit conditions / measurable work

A researcher may report ROUTINE_PREFLIGHT_COMPLETE only with exact dependency commit, artifact receipt, data source/clock identity and any scoped limitations. The NEXT output must be a research plan, execution results, design/white paper, reproducible strategy code, or a specifically authorized system-build increment—not yet another backtest-environment audit memorandum. Engine repair requires a trigger and scoped ticket. Successful experiments and failed experiments must remain independently reproducible and available to later EA integrations.

## LAW 10 — Enforcement at each handoff

At every new-chat handoff, put this instruction first:
**"Use the existing Coinexx and Dukascopy Python tick backtest environments; do not rebuild or comprehensively re-audit them. Reuse verified releases and actual newer lineage. Start with the last unfinished research experiment. Perform a scoped engine repair only when a concrete evidenced trigger exists."**

Report `ENGINE_DEPENDENCY`, `REPLAY_HEALTH_STATUS`, `TRIGGERED_DEFECT_TICKET` (or NONE), `LATEST_ACTIVE_RESEARCH_BRANCH`, `LAST_COMPLETE_RESEARCH_ARTIFACT`, and `NEXT_RESEARCH_ACTION`. If no exact current research branch/experiment can be verified, recover it from original artifacts; do NOT default to infrastructure research.

## Exact evidence references and account routing

PRIMARY research workspace: https://drive.google.com/drive/folders/1IAoHUE9Gfb6YYrleZdLtiJ0jydc__gfZ
PRIMARY canonical handoff: https://drive.google.com/drive/folders/1v1bhQx_6LvM9-Xv5oJtYP8fImFR_Bzkp
PRIMARY Coinexx approved Jan–Sep: https://drive.google.com/drive/folders/1XzHug6HYQdSKIbKuGhBTOUHawAXynIb4
PRIMARY Dukascopy approved Jan–Jul: https://drive.google.com/drive/folders/1lSCfO_awUKkbR4I6xDTy9orjIl0SrgIV
MT5_EXPAND maintenance root: https://drive.google.com/drive/folders/1iN-wfoCni64OX12r2FeGFVUzKOYSPcjv
MT5_EXPAND archive canonical index: https://drive.google.com/drive/folders/1p4XSv86nlp9RjMjsGhR_1ZC80BCXbvVK
Historical v1.3 handoff prompt (needs this additive v1.4): https://docs.google.com/document/d/1u1ClV5rT4M31aS2LxfgN1CBFFZkSH70_kYjmOwC1fmE/edit

**Non-retroactive claim:** This law does not certify subsequent R00 outputs or later branch code, and does not assert that either replay engine is flawless. It explicitly preserves proven provenance and promotes focused scientific research over repeated reconstruction.
