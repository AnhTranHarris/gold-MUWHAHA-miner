# DELTA R037 Timeout-Safe Continuation Handoff — Checkpoint 09D

**Status:** CURRENT READ-FIRST HANDOFF  
**Project:** Gold MUWHAHA Miner — XAUUSD  
**Branch:** `delta`  
**Last verified durable unit:** `R037_DH05_ACCEPTANCE_FAILURE_REENTRY_CHECKPOINT_09D`  
**First incomplete unit:** `R037_DH05_PROBE_QUALIFICATION_CLOCK_AND_EVENT_LIFECYCLE_PARITY_RECONSTRUCTION`  
**Operational parent:** `R032-C03_PLUS_DH02_S11_S08`  
**Promoted candidate:** NONE  
**Primary metric locks:** NONE  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**MT5 translation ready:** FALSE  

## Authority and startup

Use this order:
1. current owner instruction;
2. live `delta/CURRENT_STATE.json`;
3. DELTA governance through GOV-018;
4. this handoff;
5. current R037 checkpoint artifacts and working workbook;
6. older handoffs only as historical evidence.

A message-delivery timeout is not proof that research failed. After a timeout, read live `CURRENT_STATE.json`, inspect the last durable unit, read its full rebuild manifest, verify CI, and resume only `first_incomplete_unit`.

## Current R037 state

R037-SORB-v1 is preregistered and source QA passed, but official integrated replay is NOT started. Integration remains blocked until exact R032-C03 parent specialist parity is reconstructed.

The non-specialist backbone is exact:
- R9 -> P01 -> M30_KEEP_OWNED -> GLOBAL NO_REARM.

Remaining full-parent specialist parity:
- DH03-S06
- DH05-S06
- DH02-S11
- DH02-S08

DH05-S06 is the active clean-room parity target.

## DH05 authoritative fixture

Frozen historical fixture:
- 672 signals
- 615 standalone trades
- 307 official wins
- net -$101.08
- fixture SHA-256 `2deb601035d3e460f6de76ab8045b890ba7c5065b00a8815fceaf482916e2eae`

The historical producing file `r013_selective_handoff.py` is not recoverable from live GitHub/Drive. Do not guess it and do not restart the project. The accepted recovery path is clean-room reconstruction from durable vectors, reports, manifests, workbook fingerprints, and canonical ticks, with parity required before active use.

## Checkpoint 09C

Frozen parity hypothesis:
- symmetric two-bar confirmed M5 swing;
- repeated causal same-boundary pre-failure probe-attempt ledger.

Producer:
`research/delta/experiments/delta_r037_dh05_boundary_probe_parity.py`

Producer commit:
`9d8b3d0b53deedb69e81ffd132feb82888176c71`

Result SHA-256:
`c7afe32a538c1168523a664f67ed1f32f394f8ea7f537e92dbc6c590f2e64cf5`

## Checkpoint 09D — latest durable science

Frozen additional hypothesis:
- BREAK_ACCEPTED only while event remains a qualified probe;
- acceptance displacement is signed completed acceptance-bar body displacement / event M5 ATR;
- acceptance close remains beyond the original boundary;
- failure clock starts at FAILURE_CANDIDATE;
- no numeric vector retuning.

Producer:
`research/delta/experiments/delta_r037_dh05_acceptance_failure_reentry_parity.py`

Producer commit:
`1fc60c12c4c6aba74fb74c1d13e9241f63bb9977`

Producer blob:
`21ee0fa6d32f292f49549c7639aa0313174d23c3`

Compact checkpoint:
`research/delta/reference/DELTA_R037_DH05_ACCEPTANCE_FAILURE_REENTRY_CHECKPOINT_09D.json`

Report:
`research/delta/research/DELTA_R037_DH05_ACCEPTANCE_FAILURE_REENTRY_CHECKPOINT_09D.md`

Result SHA-256:
`9b1ebf24e3f01dd52f9c9e0e19c4d966883f657570b3dd36892e9602e2615fb9`

09D reduced first-five-stage absolute error from 3,012 to 1,749, accepted-stage error from 1,070 to 70, and reentry-stage error from 521 to 159. Full parity remains false.

## Exact next unit

`R037_DH05_PROBE_QUALIFICATION_CLOCK_AND_EVENT_LIFECYCLE_PARITY_RECONSTRUCTION`

Only repair residual probe-qualification timing and event-lifecycle/reset semantics. Do not retune vector thresholds. Do not optimize economics. Do not integrate SORB. Do not access August. Do not begin MQL5.

## Durability repair

The rebuild artifact gate failed because `CURRENT_STATE.active_rebuild_manifest_path` still referenced checkpoint 09B while `last_verified_durable_unit` was 09D.

Repair:
- full 09D rebuild manifest added at  
  `research/delta/artifacts/DELTA_R037_DH05_ACCEPTANCE_FAILURE_REENTRY_CHECKPOINT_09D_MANIFEST.json`
- manifest commit `015dac2288c1b81b95713db1997e4baa82cbeca9`
- CURRENT_STATE pointer repair commit `31f02b22460e4590ae508d862730cb8c785a8544`
- GitHub Actions run `37093844911`: SUCCESS.

Do not roll back that repair.

## Crash-safe write order

For each new bounded unit:
1. freeze the unit/parity target;
2. commit producing source before official compute;
3. run bounded compute;
4. persist result and hashes;
5. write/read back workbook or Drive evidence;
6. update a complete rebuild manifest;
7. advance `CURRENT_STATE.json` last;
8. require the DELTA rebuild artifact gate to pass;
9. only then send the chat summary.

If the summary times out after step 8, the next chat resumes from durable state and does not repeat the completed work.

## Drive handoff pack

Current folder ID:
`13PZqzTG-vFz-jgK6okiL6YEOL0a2grKE`

READ FIRST doc ID:
`14pzhNREDtHXBtKxy-QqWbsH5qwc_CaP9iACjIjx5XqU`

Restart contract doc ID:
`1LlZrGb_ZEXOHRrtmDE-IL2wHiYuW6vRGcN4_UF_ryXc`

MT5 readiness doc ID:
`18W0lPE8TrEXBSn-6hjNkrRkQiU9hwFw6wcR2KOD9tWc`

Artifact map doc ID:
`1SjmuMf0gAfDk6F1YhYmclV1iYZUMyfodgWXBrPmeHdA`

New-chat starter doc ID:
`15bKGqPsBebEXBdpgqhI1f6ItjoeJ4jc_3ZBzkN7woAU`

Continuity QA doc ID:
`18W8y8hHqcK84rkSW66tRWIcT1R5YBxJhitsziRRNLEI`

Working workbook ID:
`1C2EOJ2WDZgVMcGG8s1WPY46-Q4U8QQXUhZytqPJVsY0`

Relevant R037 tabs:
69 through 74.

## Current gate

Research chain durable through 09D.  
Next unit unambiguous.  
Integrated SORB replay blocked on full parent parity.  
August SEALED.  
MQL5 NOT AUTHORIZED.  
