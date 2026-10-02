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
6. Read `research/delta/governance/DELTA_GOV_004_BENCHMARK_ROLES_AND_HUMAN_GOAL_METRICS_CONTRACT.md`.
7. Read `research/delta/governance/DELTA_GOV_005_PROVISIONAL_CANDIDATE_IMPROVEMENT_GATE.md`.
8. Read `research/delta/governance/DELTA_GOV_006_SYNTH_METRIC_LOCK_AND_CUMULATIVE_RATCHET_CONTRACT.md`.
9. Read `research/delta/governance/DELTA_GOV_007_CREATIVE_REFINEMENT_ESCALATION_AND_DUKASCOPY_PLAYGROUND.md`.
10. Read `research/delta/governance/DELTA_GOV_008_MULTI_SPECIALIST_COMPOSITE_AND_SESSION_AWARE_ASSUMPTION.md`.
11. Read `research/delta/governance/DELTA_GOV_009_NEWS_EVENT_OPPORTUNITY_AND_IMPACT_HANDLING_ASSUMPTION.md`.
12. Read `research/delta/governance/DELTA_GOV_010_HIGH_OPPORTUNITY_DENSITY_AND_CANDIDATE_TRADE_CONTRIBUTION_ASSUMPTION.md`.
13. Read `research/delta/governance/DELTA_GOV_011_PROP_STYLE_MAINTENANCE_CAPITAL_STAGING_AND_SMALL_ACCOUNT_SURVIVAL.md`.
14. Read `research/delta/reference/R9_EVIDENCE_REGISTRY.json`.
15. Read `research/delta/reference/R9_REFERENCE_CORPUS_INDEX.json`.
16. Read `research/delta/handoffs/DELTA_NEW_CHAT_BOOTSTRAP_2026-10-01.md`.
17. Verify GitHub branch is `delta` and Drive target is `DELTA_RESEARCH`.
18. Resume exactly from `CURRENT_STATE.next_action`.

The first DELTA unit is an evidence/source/parity preflight. No new trading result may become a parent before it passes the DELTA manifest gate.

## Foundational timeframe rule

All DELTA Python backtests and any eventual MT5 implementation obey `DELTA_GOV_002_TICK_ROOTED_NESTED_TIMEFRAME_CONTRACT.md`. The ordered tick stream is authoritative. Every supported candle is rebuilt directly from ticks; nested timeframes provide synchronized multi-horizon state without replacing tick chronology.

## Research-speed funnel

All DELTA candidates obey `DELTA_GOV_003_RESEARCH_SPEED_STAGE_GATE_CONTRACT.md`: first screen on the owner's first 2.5 weeks of January, then promote only qualifying candidates into bounded month-by-month January-through-July research. Monthly boundaries are compute/checkpoint boundaries, not human-review gates: persist the month, emit a micro-status, and continue automatically. Python may test and retest repeatedly for refinement and optimization; behavior changes create new candidate versions and completed results remain preserved.

## Benchmark roles

`DELTA_GOV_004_BENCHMARK_ROLES_AND_HUMAN_GOAL_METRICS_CONTRACT.md` defines the scorecard semantics before any R9 file loading: R9 REAL is the starting baseline; R9 SYNTH is the performance-growth reference; R9 OVERFIT is the trade-capacity/high-profit-per-trade reference; Dukascopy is the independent cross-broker environment used against Coinexx MT5 evidence. The owner-primary metrics are winning trade count, net profit, gross loss, and maximum drawdown.

R9 evidence loading is currently blocked by owner instruction until goal definition is complete and explicit authorization is given.

## Candidate acceptance gate

Read `research/delta/governance/DELTA_GOV_005_PROVISIONAL_CANDIDATE_IMPROVEMENT_GATE.md` before candidate screening. It contains the owner-defined provisional acceptance thresholds and remains human-revisable.

## Cumulative performance locks

`DELTA_GOV_006_SYNTH_METRIC_LOCK_AND_CUMULATIVE_RATCHET_CONTRACT.md` creates a monotonic research ratchet. When a primary metric reaches at least 87% of its directional progress from R9 REAL toward R9 SYNTH, that metric and candidate version become a protected anchor. Descendants must preserve every accumulated lock and hard-fail if a locked metric deteriorates by 5% or more from its lock value. Research priority then shifts toward the remaining unlocked metrics.

## Creative refinement escalation

`DELTA_GOV_007_CREATIVE_REFINEMENT_ESCALATION_AND_DUKASCOPY_PLAYGROUND.md` authorizes broad candidate redesign and repeated bounded Python experimentation. If a refinement remains below goal and gains less than 10 percentage points of SYNTH-gap closure versus its parent, DELTA must materially broaden the search rather than remain trapped in minor parameter tuning. Once authorized for data use, Dukascopy tick replay is the primary experimental playground. All causality, versioning, and metric-lock rules remain mandatory.

## Multi-specialist composite assumption

`DELTA_GOV_008_MULTI_SPECIALIST_COMPOSITE_AND_SESSION_AWARE_ASSUMPTION.md` defines DELTA as a session-aware multi-specialist system. Specialists are judged against their declared scoped populations; the assembled composite is the canonical object for whole-system primary metrics and cumulative system locks. Required session-awareness covers Australia, Asia, Russia, India, Middle East, Europe, UK, and New York. Exact clock/DST/overlap definitions remain pending a dedicated session-timing contract.

## News/event opportunity assumption

`DELTA_GOV_009_NEWS_EVENT_OPPORTUNITY_AND_IMPACT_HANDLING_ASSUMPTION.md` treats medium/high-impact monetary-policy, macro-financial, and gold-specific news as a first-class opportunity regime rather than an automatic blackout. DELTA may build dedicated pre-event, release-reaction, post-event, liquidity-protection, continuation, reversal, or stand-down specialists. Exact news providers, impact taxonomy, timestamps, and event windows remain pending a dedicated event-data contract.

## High opportunity-density assumption

`DELTA_GOV_010_HIGH_OPPORTUNITY_DENSITY_AND_CANDIDATE_TRADE_CONTRIBUTION_ASSUMPTION.md` treats high daily opportunity/trade activity as part of the intended system edge. Trading specialists should add unique qualified opportunity capacity within their declared scopes; duplicate proposals do not count as new opportunities. Promotion-grade results must expose daily opportunity/trade distributions so improved headline metrics cannot hide success-by-starvation. Exact hard daily activity floors remain pending owner/data review.

## Maintenance and capital staging

`DELTA_GOV_011_PROP_STYLE_MAINTENANCE_CAPITAL_STAGING_AND_SMALL_ACCOUNT_SURVIVAL.md` separates prop-style risk maintenance from edge discovery. Testing uses fixed 0.01 lots until all primary categories are locked and the owner authorizes a later lot ladder. Starting capital stages are $100,000 at zero locks, $1,000 at one lock, $500 at two or three locks, and $100 when all four primary categories are locked. At or above $1,000 the provisional standard envelope uses a 0.5% planned-loss ceiling, 2.5% daily warning / 4% daily hard stop, and 5% weekly warning / 8% weekly hard stop. Below $1,000, small-account survivability rules are empirically calibrated rather than invented.

## R9 SYNTH fast reference

After owner authorization on 2026-10-01, DELTA loaded the Jan-Jul R9 SYNTH tester evidence and created `research/delta/reference/R9_SYNTH_PERFORMANCE_FAST_REFERENCE.json`. Use this compact file for primary SYNTH targets, monthly performance, day/week distributions, integrity checks, and observed day/week behavior before reopening the 95 MB tester workbook or massive ticklogger corpus.
