# DELTA-A GRID — CURRENT HANDOFF — 2026-10-05

**Purpose:** authoritative restart handoff for the isolated `delta-A` XAUUSD grid research lineage. This file exists specifically to prevent loss of research state, helper logic, or MT5 translation semantics when a ChatGPT conversation reaches message-length/time limits.

## 0. New-chat bootstrap order

A new chat must bootstrap in this order before doing research:

1. Read the project master protocol Google Doc: `1ycB5bQ3P24w7BZz54RwgJbc5CX5aRcqgr0KiI0Iidkw`.
2. Read `research/delta-a/DELTA_A_GRID_HF_STATE.json` from GitHub branch `delta-A`.
3. Read this handoff file.
4. Read `DELTA_A_R9_GRID_MILESTONE_01.md`, `DELTA_A_R9_GRID_MATURE_FILTER_MANIFEST.json`, and `DELTA_A_R9_GRID_MT5_BUILD_CANDIDATE.md`.
5. Read `DELTA_A_R9_GRID_SMALL500_FALLBACK_MILESTONE.md`.
6. Read `DELTA_A_SMALL100_PROFIT_RAMP_RESEARCH01.md` and `DELTA_A_SA100_HELPER_STATUS_2026-10-05.json`.
7. Only then resume the $100 January speed-run work unit described below.

Never reconstruct the active state from chat memory alone.

## 1. Governance / isolation

- Repository: `AnhTranHarris/gold-MUWHAHA-miner`
- Active side-research branch: `delta-A`
- Main `delta` must remain untouched unless the owner explicitly directs otherwise.
- Instrument: XAUUSD only.
- Signal clock: native ordered Dukascopy Bid/Ask ticks.
- Research execution comparator: `DUKAS_COINEXX_LIKE_P75`.
- P75 is a research surface only; a live MT5 EA must use broker-native Bid/Ask and margin/contract data.
- Martingale: forbidden.
- Lookahead: forbidden.
- Production MQL5: not authorized.
- August 2026: **SEALED**. Do not inspect or use the August tick file until the owner explicitly unseals the holdout.

## 2. Primary frozen milestone — R9 Grid Milestone 01 / Pre-August

Authoritative checkpoint: `R9_GRID_MILESTONE_01_PREAUG`.

Snapshot branch: `delta-A-r9-grid-milestone-01-preaug`.
Frozen commit: `0b9c88d51144b424d00803b43d6a8c43b35a0ac7`.

Calendar-blind state machine:

- BOOTSTRAP until at least 25 active signal days and 25,000 completed outcomes;
- after becoming mature-eligible, switch only after the next >=24-hour market inactivity gap;
- no month-name switch is permitted.

Jan-Jul accepted tick result after the portfolio-pressure wrapper:

- trades: 186,569
- winners: 113,958
- win rate: 61.08%
- net: +$194,674.33
- expected payoff: +$1.0434/trade
- PF: 1.2525
- gross loss: -$770,911.86
- true max floating-equity DD: $27,904.26
- max simultaneous positions: 250
- max absolute directional imbalance: 231
- all Jan-Jul months positive

Portfolio-pressure wrapper:

- hard gross concurrency ceiling: 250 positions;
- reject a new same-direction entry when live net imbalance is already >=225 positions.

Exact state-machine parity artifact:

- reconstructed pre-pressure events: 186,901
- event-spec SHA-256: `55f04e2b8c39e3b7693a6850cb540b7cc00705623f6dccd12b1736b379fd249a`
- event rows bitwise equal: true

R9 SYNTH alignment at the milestone:

- trade count: ~85.1%
- winning-entry count: ~59.6%
- net profit: ~63.0%
- expected payoff: ~74.0%

Loss efficiency/PF remains the largest headline gap to R9 SYNTH.

## 3. Minor fallback milestone — $500 small-capital adapter

Snapshot branch: `delta-A-r9-grid-small500-fallback-v1`.

Core design:

- starting capital: $500;
- physical lot: fixed 0.01;
- full grid/specialist engine remains virtual;
- initially only `CORE_H4_M1800` receives physical capital;
- slot compounding, not lot compounding;
- scheduled market-gap guard remains active.

Physical concurrency ladder:

- < $750: 1 slot
- $750 to < $1,500: 2 slots
- $1,500 to < $3,000: 3 slots
- $3,000 to < $6,000: 4 slots
- >= $6,000: 5 slots

Feb-Jul tick-level research result with January retained as virtual warm-up:

- physical trades: 8,520
- net: +$13,754.29
- ending research balance from $500: $14,254.29
- minimum tick-level equity: $469.82
- worst floating-equity DD: $750.30
- max physical concurrency: 5
- all Feb-Jul physically traded months positive

Interpretation: the $500 account is not a miniature 250-position portfolio. It is a virtual high-frequency specialist engine with a capital-admission controller.

## 4. Current $100 research — last complete promotable research state

The current $100 work is **experimental and not a milestone**.

Authoritative completed research note: `DELTA_A_SMALL100_PROFIT_RAMP_RESEARCH01.md`.

Working hypothesis: emulate the useful part of R9 SYNTH's $100 / fixed-0.01 behavior by compounding physical **position slots** and specialist ownership as realized capital grows, while keeping the full grid virtual.

Best completed staged ignition prototype before the timeout:

- balance < $80: London/NY overlap + prior same-side specialist agreement; max loss target about $3; 1 slot
- $80 to < $125: London/NY overlap; max loss target about $5; 1 slot
- $125 to < $175: prior 10-second same-side specialist confirmation; max loss target about $7.50; 1 slot
- $175 to < $200: all eligible CORE_H4; max loss target about $10; 1 slot
- $200 to < $250: max loss target about $10; up to 2 slots
- $250 to < $350: max loss target about $15; up to 2 slots
- $350 to < $500: max loss target about $20; up to 3 slots
- at $500: hand off to the frozen $500 adapter

Measured completed behavior:

- favorable historical February path: about $100 -> $530, 97 physical trades, ~10.7 calendar days;
- rolling active-day starts: ~78.1% reached $500 within 90 days;
- ~14.2% dipped below $60;
- ~1.9% fell below $30;
- median successful time to $500: ~13.1 days.

Conclusion: promising but **not robust enough for a $100 milestone**. The promotion objective remains >=95% rolling-start survival to $500 before considering the seed architecture durable.

## 5. Additional completed $100 diagnostics — not promoted

Several full Feb-Jul exact candidates were generated as diagnostics. They do not supersede the rolling-start survival test because they can hide start-date fragility.

`sa100_core_gapguard_candidate`:

- trades: 8,175
- net: +$12,411.27
- final balance from $100: $12,511.27
- min tick equity: $77.06
- max concurrency: 5

`sa100_rampC_candidate`:

- trades: 47,570
- net: +$26,698.96
- min tick equity: $77.06
- max concurrency: 16

`sa100_rampN_candidate`:

- trades: 84,769
- net: +$94,539.12
- min tick equity: $77.06
- max concurrency: 185

These are research diagnostics only. In particular, the high-concurrency variants are not acceptable proof that a $100 live account is safe.

## 6. Timeout/helper forensic boundary

The conversation timed out while the owner had asked to use **January as the speed-run filtering month**, then expand any viable configuration through February-July.

### 6.1 Completed negative helper — may be retained as failure evidence

Helper: `sa100_r2_port_month.py`.

Tested a `run>=2` / time-since-opposite-crossing <=10 seconds filter with a $5 stop against R2 core events for February-July. Capital runs were tested with 1, 2 and 3 slots from $100.

Result: **failed**. Every Feb-Jul monthly $100 capital run exhausted the account before reaching $500. This mechanism is retired as a candidate but preserved as negative evidence.

### 6.2 Incomplete helper analysis — MUST NOT be continued from partial state

Helper: `sa100_build_core_stop_variants.py`.

It successfully generated Feb-Jul CORE event matrices with stop variants at approximately $3, $5, $7.50, $10 and $15. Six derived CSVs were produced.

However:

- no January stop-variant matrix was generated;
- no January speed-run selector was completed;
- no configuration ranking was completed;
- no cross-month selection/validation decision was completed;
- therefore there is **no valid conclusion** from these matrices.

The next chat must not continue the unfinished selection loop. It should rerun this work unit from scratch, beginning with January, and use the Feb-Jul matrices only as optional checksum/reproduction references after January has selected candidate mechanics.

## 7. Next active work unit

`SA100_JAN_SPEEDRUN_RESTART_01`

Objective: raise $100 -> $500 survivability and profit velocity without changing the broker minimum 0.01 lot.

Required workflow:

1. Rebuild the January seed-event population from raw January Dukascopy ticks / frozen grid logic.
2. Re-run stop/lifecycle/entry/slot experiments from scratch in January; do not import conclusions from the incomplete stop-variant helper.
3. Prioritize survival first, then velocity:
   - primary survivability diagnostic: reaching $500 without dropping below $60;
   - separately track catastrophic paths below $30;
   - promotion target: >=95% rolling-start success to $500 within the research window;
   - report median and tail days-to-$500 rather than optimizing only the favorable first start.
4. Candidate mechanisms to test causally:
   - capital-floor ratchet / defensive-rescue mode;
   - best-opportunity priority queue when the only physical slot becomes free;
   - balance- and free-margin-aware slot unlock;
   - session/consensus quality gates only where they improve survival without starving velocity;
   - balance-dependent stops rather than one universal stop;
   - selective recovery handoff for rejected toxic states;
   - virtual state pre-warm compatible with future MT5.
5. Once January has a viable neighborhood, freeze the mechanic definition before testing Feb-Jul.
6. Validate Feb-Jul sequentially. Do not retune each month independently into a calendar-fitted system; month-specific diagnostics may inform causal state features only.
7. August remains sealed.

## 8. Source and execution requirements

Raw Dukascopy XAUUSD Jan-Jul tick attachments are available in the project source environment:

- `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`
- `XAUUSD_DUKAS_2026_02_ticks.csv(3).gz`
- `XAUUSD_DUKAS_2026_03_ticks.csv(3).gz`
- `XAUUSD_DUKAS_2026_04_ticks.csv(3).gz`
- `XAUUSD_DUKAS_2026_05_ticks.csv(3).gz`
- `XAUUSD_DUKAS_2026_06_ticks.csv(3).gz`
- `XAUUSD_DUKAS_2026_07_ticks.csv(2).gz`

August exists but is sealed and must not be read.

R9 SYNTH benchmark is historical/aspirational, not causal proof. The exact MT5 report contains 219,342 trades, 191,136 winners, +$309,122.85 net, PF 20.036, and +$1.409319 expected payoff/trade.

## 9. Future MT5 translation lock

Do not build the EA from prose/chat alone. Future MQL5 work must read the frozen GitHub mechanics/manifests and reproduce:

- virtual grid event timing;
- feature-state calculations;
- specialist routing;
- source-specific lifecycles;
- capital admission / slot scheduler;
- portfolio-pressure rules;
- broker-native Bid/Ask and `OrderCalcMargin` semantics;
- state pre-warm procedure;
- deterministic telemetry sufficient to compare Python and MT5 event-by-event.

Production MQL5 requires separate explicit owner authorization after research approval.

## 10. Anti-Gamma handoff rules

To avoid a prior-lineage-style reconstruction failure:

- never promote a result that exists only in chat;
- every durable result must have a GitHub file and commit;
- every major milestone gets a snapshot branch and a Google Docs white-paper snapshot;
- every helper must be marked COMPLETE, FAILED, or INCOMPLETE;
- an INCOMPLETE helper is rerun from scratch, not resumed;
- preserve source code for every helper that materially influences a candidate;
- preserve enough numeric artifacts or hashes to reproduce the decision;
- never silently replace a frozen milestone with a later experiment;
- August access requires explicit owner authorization;
- no MQL5 build from an unfrozen experimental helper state.

## 11. Rollback hierarchy

1. Primary grid rollback: `R9_GRID_MILESTONE_01_PREAUG` / branch `delta-A-r9-grid-milestone-01-preaug`.
2. Small-capital fallback: `R9_GRID_SMALL500_V1` / branch `delta-A-r9-grid-small500-fallback-v1`.
3. $100 seed research: experimental only; no rollback milestone yet.

## 12. Immediate new-chat instruction

When a new chat is opened, say: **"Bootstrap DELTA-A from the current handoff Google Drive and GitHub branch delta-A. Verify the state file and helper-status manifest. Then restart SA100_JAN_SPEEDRUN_RESTART_01 from January from scratch. Do not access August and do not build MQL5."**
