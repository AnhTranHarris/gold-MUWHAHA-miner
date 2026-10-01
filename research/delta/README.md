# DELTA Research

DELTA is the standalone clean-room research lineage for Gold MUWHAHA Miner.

## Clean-room scope

Only the following are authoritative inputs for DELTA:
- the preserved R9 engineering/evidence baseline explicitly registered under `research/delta/reference/`;
- DELTA-created code, manifests, checkpoints, reports and QA artifacts;
- the registered ordered market-data corpus;
- reconstructible public research used only to generate testable causal hypotheses.

Prior internal research lineages are outside DELTA scope. Do not read, import, cite, compare, port, merge, reconstruct, or use their code, documents, metrics, hypotheses, candidate logic, or results.

## New-chat bootstrap order

1. Read `CURRENT_STATE.json`.
2. Read `research/delta/governance/DELTA_CLEAN_ROOM_LOCK.md`.
3. Read `research/delta/governance/DELTA_GOV_001_CAUSAL_DURABLE_MT5_RESEARCH_CONTRACT.md`.
4. Read `research/delta/governance/DELTA_GOV_002_TICK_ROOTED_NESTED_TIMEFRAME_CONTRACT.md`.
5. Read `research/delta/governance/DELTA_GOV_003_RESEARCH_SPEED_STAGE_GATE_CONTRACT.md`.
6. Read `research/delta/reference/R9_EVIDENCE_REGISTRY.json`.
7. Read `research/delta/reference/R9_REFERENCE_CORPUS_INDEX.json`.
8. Read `research/delta/handoffs/DELTA_NEW_CHAT_BOOTSTRAP_2026-10-01.md`.
9. Verify GitHub branch is `delta` and Drive target is `DELTA_RESEARCH`.
10. Resume exactly from `CURRENT_STATE.next_action`.

The first DELTA unit is an evidence/source/parity preflight. No new trading result may become a parent before it passes the DELTA manifest gate.

## Foundational timeframe rule

All DELTA Python backtests and any eventual MT5 implementation obey `DELTA_GOV_002_TICK_ROOTED_NESTED_TIMEFRAME_CONTRACT.md`. The ordered tick stream is authoritative. Every supported candle is rebuilt directly from ticks; nested timeframes provide synchronized multi-horizon state without replacing tick chronology.

## Research-speed funnel

All DELTA candidates obey `DELTA_GOV_003_RESEARCH_SPEED_STAGE_GATE_CONTRACT.md`: first screen on the owner's first 2.5 weeks of January, then promote only qualifying candidates into bounded month-by-month January-through-July research. Monthly boundaries are compute/checkpoint boundaries, not human-review gates: persist the month, emit a micro-status, and continue automatically. Python may test and retest repeatedly for refinement and optimization; behavior changes create new candidate versions and completed results remain preserved.
