# DELTA Clean-Room Lock

**Status:** MANDATORY  
**Scope:** branch `delta`, `CURRENT_STATE.json`, `research/delta/**`, and DELTA-only CI.

DELTA is a standalone research and development lineage.

## Allowed inputs

Active DELTA research may use only:
- the R9 engineering/evidence baseline explicitly registered under `research/delta/reference/`;
- DELTA-created source, manifests, checkpoints, reports, models, fixtures and QA artifacts;
- the registered ordered market-data corpus;
- reconstructible public research used to generate independently testable causal hypotheses.

## Prohibited cross-lineage use

Prior internal research lineages are outside scope.

Active DELTA work must not read, import, cite, compare, port, merge, reconstruct, summarize, use, or derive candidate logic from prior-lineage:
- code;
- documents or handoffs;
- controller/current-state files;
- metrics or performance claims;
- hypotheses or strategy mechanisms;
- models, caches, labels or feature sets;
- candidate EAs;
- governance or approval rules.

Git ancestry or inherited repository files do not make those materials valid DELTA inputs.

## Enforcement

The DELTA governance gate scans the active DELTA surface and fails closed on prohibited legacy-lineage references.

A violation invalidates the affected unit. Restore the last clean DELTA checkpoint and rerun only the contaminated unit.

## Holdout

August 2026 remains sealed until the DELTA rules permit opening it and the owner explicitly authorizes access.

## Owner-authorized one-time R9 baseline inspection exception

On 2026-10-01 the owner explicitly authorized a one-time read-only inspection of the legacy R9 baseline solely to summarize the preserved R9 MT5 EA's functional mechanics for DELTA.

Inspection was restricted to:
- `historical R9 baseline source` — blob `7eecb5f1947017a01ce85b2520725de54749e523`;
- `carson/r9-tick-logger/Experts/GoldMuwahahaMiner_R9_TickLogger.mq5` — blob `5c7655cd3357f9126e8bffd97c34374dfb29f83e` — only to cross-check that instrumentation preserved R9 trading logic;
- historical source/evidence notes only to verify the same R9 mechanics.

The resulting DELTA-owned durable references are:
- `research/delta/reference/R9_MT5_EA_FUNCTIONAL_SUMMARY.md`;
- `research/delta/reference/R9_MT5_EA_FUNCTIONAL_FAST_REFERENCE.json`.

No later legacy candidate logic, specialist design, optimization result, or governance was imported.

**Exception status: CLOSED_AFTER_R9_SUMMARY.** Active DELTA work must use the durable DELTA references above and must not reopen any prior internal lineage unless the owner gives new explicit authorization.
