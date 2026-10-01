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
