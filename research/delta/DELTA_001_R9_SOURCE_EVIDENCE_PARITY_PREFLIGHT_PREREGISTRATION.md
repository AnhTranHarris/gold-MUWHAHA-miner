# DELTA 001 — R9 Source / Evidence / Parity Preflight

**Status:** PREREGISTERED / NOT YET RUN  
**Parent:** DELTA_BOOTSTRAP_000  
**Strategy optimization:** PROHIBITED  
**August 2026:** SEALED

## Purpose

Before DELTA performs any new trading research, establish a fail-closed evidence and reconstruction baseline around the authoritative R9 MT5 implementation and the existing validated R9 research corpus.

## Required verification

DELTA_001 must independently verify:

- the exact R9 HybridGate and TickLogger source identities;
- behavior-critical R9 default inputs and session/execution defaults;
- R9 REAL report/tick-index/daily-manifest/event-index/validation availability;
- R9 SYNTH report/tick-index/daily-manifest/event-index/validation availability;
- paired REAL/SYNTH corpus availability and role;
- OVERFIT/ORACLE quarantine identity and prohibition from execution inference;
- canonical Dukascopy Jan-Jul source filenames and hashes;
- DELTA_RESEARCH Drive and GitHub read/write/readback;
- the initial DELTA data-wall contract;
- the metric schema every later Entry+Hold study must report.

## Activity contract frozen here

Every later DELTA candidate must report, at minimum:

- upstream opportunity count;
- selected/admitted trade count;
- trade-count retention versus its preregistered reference;
- winning trade count;
- entry-quality metric;
- hold/persistence metric;
- net, PF and average trade;
- gross profit and gross loss;
- maximum drawdown;
- monthly counts/economics.

A later study may not claim improvement by suppressing the trade population below its preregistered activity floor.

## Evidence roles

R9 REAL is execution/path evidence.  
R9 SYNTH is teacher/north-star evidence only.  
R9 OVERFIT/ORACLE is quarantined capacity/hypothesis evidence only.  
Jan-Jul Dukascopy is historically inspected causal research/robustness data.  
August is a sealed blind holdout.

## Pass condition

DELTA_001 becomes VERIFIED_DURABLE only when its producing source, compact results, QA, hashes, Drive references and GitHub readback all satisfy DELTA GOV-001. No strategy research begins before that closure.
