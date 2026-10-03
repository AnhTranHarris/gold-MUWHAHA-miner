# DELTA Full New-Chat Handoff — 2026-10-02

**Project:** Gold MUWHAHA Miner — XAUUSD  
**Repository:** `AnhTranHarris/gold-MUWHAHA-miner`  
**Branch:** `delta`  
**Purpose:** disaster-recovery bootstrap for a new chat after repeated delivery timeouts / context exhaustion  
**Research lineage:** DELTA-only clean room  
**August 2026:** SEALED  
**MQL5 candidate coding:** NOT AUTHORIZED  
**Approved DELTA EA:** NONE  
**Current research focus:** ENTRY + INITIAL-HOLD  
**Deferred research focus:** HOLDING-TRADE + EXIT + HIGH-PROFIT

---

## 0. Critical recovery instruction

A new chat must **not** trust the old top-level cursor that said `DELTA_005I compute next`.

That cursor became stale during repeated delivery-timeout failures.

The actual durable research chain progressed through:

`DELTA_005A -> 005B -> 005C -> 005D -> 005E -> 005F -> 005G -> 005H -> 005I -> 005J -> 005K -> 005L -> 005M`

The current last complete scientific unit is:

`DELTA_005M_001_TRAIL_STEP_FREQUENCY`

The strongest Entry + Initial-Hold finding remains:

`DELTA_005H_001_INITIAL_TRAILING_SHIELD`

005M is a secondary refinement around 005H, not a replacement breakthrough.

**Do not resume 005I compute.**

Before any new experiment, the new chat must read:
1. `CURRENT_STATE.json`
2. this handoff
3. `research/delta/handoffs/DELTA_ARTIFACT_AUDIT_2026-10-02.json`
4. the DELTA_005 master Google research ledger
5. 005H checkpoint/report
6. 005M checkpoint/report + recovered 005M analysis Sheet

Only then preregister the next small Entry + Initial-Hold micro-unit.

---

## 1. Canonical recovery resources

### GitHub

Repository:
`AnhTranHarris/gold-MUWHAHA-miner`

Branch:
`delta`

Primary status file:
`CURRENT_STATE.json`

Full machine audit:
`research/delta/handoffs/DELTA_ARTIFACT_AUDIT_2026-10-02.json`

This full handoff:
`research/delta/handoffs/DELTA_FULL_HANDOFF_2026-10-02.md`

Original bootstrap:
`research/delta/handoffs/DELTA_NEW_CHAT_BOOTSTRAP_2026-10-01.md`

### Google Drive

DELTA_RESEARCH folder:
https://drive.google.com/drive/folders/1x5dLfZB8wqxbqq8hJSsxtBSnlKF7CYel

Original DELTA bootstrap Doc:
https://docs.google.com/document/d/1lqUO9ab9QFFMf2ilOi8gl3JsvwkcZPRJmtyn8vi__5g/edit?usp=drivesdk

DELTA_005 Entry + Initial-Hold master research ledger:
https://docs.google.com/document/d/1T9MPuuMsxB5gv7Zz8nvzFmaQy00_7Q-7X_4F2qrcR6k/edit?usp=drivesdk

Per-test analysis Sheet template:
https://docs.google.com/spreadsheets/d/1Zy_TfGfc6E0tJmEsoFmSONqM9W4wKuAqTPcITC5OXb0/edit?usp=drivesdk

---

## 2. Clean-room and governance rules that remain mandatory

DELTA is a standalone research lineage.

Do not read/import/use prior internal research lineages unless the owner explicitly authorizes a narrow exception.

The one-time prior-lineage exception used only to summarize R9 is CLOSED.

Canonical governance:

- `DELTA_CLEAN_ROOM_LOCK.md`
- `DELTA_GOV_001_CAUSAL_DURABLE_MT5_RESEARCH_CONTRACT.md`
- `DELTA_GOV_002_TICK_ROOTED_NESTED_TIMEFRAME_CONTRACT.md`
- `DELTA_GOV_003_RESEARCH_SPEED_STAGE_GATE_CONTRACT.md`
- `DELTA_GOV_004_BENCHMARK_ROLES_AND_HUMAN_GOAL_METRICS_CONTRACT.md`
- `DELTA_GOV_005_PROVISIONAL_CANDIDATE_IMPROVEMENT_GATE.md`
- `DELTA_GOV_006_SYNTH_METRIC_LOCK_AND_CUMULATIVE_RATCHET_CONTRACT.md`
- `DELTA_GOV_007_CREATIVE_REFINEMENT_ESCALATION_AND_DUKASCOPY_PLAYGROUND.md`
- `DELTA_GOV_008_MULTI_SPECIALIST_COMPOSITE_AND_SESSION_AWARE_ASSUMPTION.md`
- `DELTA_GOV_009_NEWS_EVENT_OPPORTUNITY_AND_IMPACT_HANDLING_ASSUMPTION.md`
- `DELTA_GOV_010_HIGH_OPPORTUNITY_DENSITY_AND_CANDIDATE_TRADE_CONTRIBUTION_ASSUMPTION.md`
- `DELTA_GOV_011_PROP_STYLE_MAINTENANCE_CAPITAL_STAGING_AND_SMALL_ACCOUNT_SURVIVAL.md`
- `DELTA_GOV_012_EXACT_JANUARY_STAGE_A_FILTER_WINDOW.md`
- `DELTA_GOV_013_CANDIDATE_LEVERAGE_AND_CRASH_SAFE_RESEARCH_LEDGER.md`

All 001–013 governance files were re-audited on 2026-10-02 and exist on the `delta` branch.

---

## 3. Key owner-defined research gates

### Primary metrics

The protected human-primary metrics are:
1. Winning trade count
2. Net profit
3. Gross loss
4. Maximum drawdown

Total trade count / opportunity count remain mandatory companion metrics.

### GOV-005 provisional improvement gate

At least one owner-targeted primary metric must improve by at least **80%** versus R9 REAL for the hard numerical gate.

**85%** is the soft preferred target.

If any supported primary metric deteriorates by:
- **17% to <25%**: warning / investigate
- **>=25%**: hard fail

### GOV-006 SYNTH lock

When a primary metric reaches at least **87% of the directional path from R9 REAL to R9 SYNTH**, that metric and exact candidate/composite version become a lock anchor.

A locked metric may not deteriorate by **5% or more** in descendants.

Locks accumulate and ratchet only upward.

No primary category is currently locked.

### GOV-007 creative escalation

If a candidate remains below goal and gains less than **+10 percentage points of additional SYNTH-gap closure** versus its parent, local tuning should stop unless evidence identifies a narrow high-sensitivity region.

The next intervention should be structurally broader.

### High activity

Success by starving trades is prohibited.

High daily trade/opportunity density is part of the intended edge.

---

## 4. Stage-A filter

Exact frozen Stage-A window:

`[2026-01-01T00:00:00.000Z, 2026-01-18T12:00:00.000Z)`

Epoch milliseconds:
- start inclusive: `1767225600000`
- end exclusive: `1768737600000`

Duration: exactly **17.5 calendar days / 420 hours**.

January is a cold start:
- no December 2025 warm-up
- no hidden pre-2026 state

If a position remains open at the final eligible tick, it is force-closed at the final executable side before the end boundary.

No post-window tick may affect Stage-A scoring.

---

## 5. R9 benchmark roles and compact references

### R9 REAL — starting baseline

Canonical:
`research/delta/reference/R9_REAL_PERFORMANCE_FAST_REFERENCE.json`

Jan-Jul:
- winning trades: **102,385**
- total trades: **236,647**
- net profit: **-$50,285.28**
- gross loss: **-$80,465.51**
- balance max drawdown: **$50,285.30**
- equity max drawdown: **$50,285.50**
- 149/149 trading days negative
- 31/31 ISO weeks negative

### R9 SYNTH — performance north-star / growth reference

Canonical:
`research/delta/reference/R9_SYNTH_PERFORMANCE_FAST_REFERENCE.json`

Jan-Jul:
- winning trades: **191,136**
- total trades: **219,342**
- net profit: **+$309,122.85**
- gross loss: **-$16,238.66**
- balance max drawdown: **$3.41**
- equity max drawdown: **$4.34**
- 149/149 trading days positive
- 31/31 ISO weeks positive

SYNTH is never execution truth and never enters live causal inference.

### R9 OVERFIT

Capacity / upper-envelope reference only.

Never use it as execution truth or a live selector.

### Dukascopy

Independent cross-broker replay/robustness environment.

August remains sealed.

---

## 6. R9 MT5 functional baseline

Canonical references:
- `research/delta/reference/R9_MT5_EA_FUNCTIONAL_SUMMARY.md`
- `research/delta/reference/R9_MT5_EA_FUNCTIONAL_FAST_REFERENCE.json`

R9 functional chain:

`new M1 minute -> frozen midpoint ±$0.15 virtual bracket -> spread + completed-M5 ATR session gate -> completed-S1 displacement/efficiency/range/turn gate -> market entry -> hard SL / trail / max hold -> opposite-side same-minute rearm -> next-minute reset`

Behavior-critical defaults include:
- lot: 0.01
- bracket half-width: $0.15
- hard stop: $0.30
- trail activation: +$0.10
- trail distance: $0.03
- max hold: 30 seconds
- max same-minute rearms: 3
- completed-S1 directional displacement threshold: $0.15
- directional efficiency threshold: >0.70
- S1 range minimum: $0.50
- max turns: 9
- spread maximum: 25 points / $0.25
- ATR M5 period: 14
- session-conditioned ATR floors
- completed-bar/right-edge timing

R9 contains no hidden:
- multi-specialist router
- news calendar
- daily/weekly governor
- dynamic lot ladder
- martingale/grid
- fixed TP
- ML model
- intermarket logic

Those are DELTA concepts, not R9 behavior.

---

## 7. Verified execution/research environment

### DELTA_001 — R9 source/evidence parity preflight

Status: VERIFIED_DURABLE.

Canonical outputs exist:
- manifest
- preregistration
- result
- behavior-critical defaults
- data walls/metric schema
- report
- QA

### DELTA_002 — Dukascopy tick lab

Status: VERIFIED_DURABLE.

Key runtime:
- `research/delta/lab/dukas_tick_lab.py`
- `research/delta/lab/run_candidate_month.py`
- `research/delta/lab/candidate_template.py`

Verified Jan-Jul:
- **57,527,562 ordered ticks**
- 16 bytes/tick hot cache
- 920,443,680 bytes core cache
- 28,697,391 validated 250ms bars
- 10,696,540 validated 1s bars
- seven month-isolated jobs
- exact source hash/order/Bid-Ask/right-edge QA
- atomic month checkpoints

### DELTA_003 — Coinexx/R9 execution parity

Status: VERIFIED_DURABLE.

Canonical runtime:
- `coinexx_r9_adapter.py`
- `r9_parity_runner.py`
- `DELTA_003_COINEXX_EXECUTION_CONFIG.json`

Full January:
- 21 files
- 7,699,274 R9 logger rows
- **zero event mismatches**
- exact January MT5 accounting:
  - 31,915 trades
  - 13,947 wins
  - $3,785.28 gross profit
  - -$10,436.90 gross loss
  - -$6,651.62 net

July 1 post-DST cross-check also has zero event mismatches.

Frozen 0.01-lot economics:
- $1 P/L per $1 XAUUSD move
- -$0.01 entry commission
- -$0.01 exit commission
- BUY entry Ask / exit Bid
- SELL entry Bid / exit Ask
- protective fill at first executable quote after crossing

### DELTA_004 — Coinexx-like Dukascopy surface

Status: VERIFIED_DURABLE.

Canonical:
- `research/delta/lab/coinexx_like_surface.py`
- `research/delta/reference/DELTA_004_COINEXX_SPREAD_PROFILES.json`

Surfaces:
- DUKAS_NATIVE
- DUKAS_COINEXX_LIKE_P50
- DUKAS_COINEXX_LIKE_P75
- DUKAS_COINEXX_LIKE_P90
- COINEXX_PARITY

Default research surface:
`DUKAS_COINEXX_LIKE_P75`

P75 Jan-Jul R9 control:
- trades: 234,417
- wins: 104,294
- gross profit: $29,243.07
- gross loss: -$78,244.86
- net: -$49,001.79

Errors vs R9 REAL are within preregistered tolerances.

No SYNTH outcome was used to calibrate the environment.

---

## 8. Current research phase

Active:
**ENTRY + INITIAL-HOLD**

Deferred:
**HOLDING-TRADE + EXIT + HIGH-PROFIT**

Do not prematurely optimize mature hold/harvest/exit/high-profit logic.

The current phase may use the frozen R9 downstream lifecycle only as an accounting scaffold.

---

## 9. DELTA_005 research chain A→M

### 005A — Tick-flow continuation

Mechanism:
short-window tick-count flow as an entry confirmation.

Result:
- improved loss/DD by filtering
- deleted too many trades/winners
- barely changed 1–15s survival

Disposition:
tick flow may remain a routing/context feature, not a global hard gate.

Status:
COMPLETE — NOT PROMOTED.

Source identity:
EXACT.

Sheet:
https://docs.google.com/spreadsheets/d/17Rcz6Jq4btAgdZz7lY1vjbAhbou8IyVIjUZ_-U3k9kY/edit?usp=drivesdk

### 005B — Micro-retest/reclaim continuation

Mechanism:
route 005A-rejected breaks into retest -> reclaim continuation.

Highest-activity:
- 13,856 trades
- 6,280 wins
- 299 retest entries
- retest sleeve win rate 44.48%
- net -$2,927.20

Finding:
retest continuation did not recover enough opportunity; longer timeout became another exclusion mechanism.

Disposition:
NOT PROMOTED.

Source identity:
EXACT.

Recovery note:
missing prereg/report markdowns were reconstructed 2026-10-02 from durable manifest/checkpoint/ledger.

Sheet:
https://docs.google.com/spreadsheets/d/1V-VHkj1jYPXebOtGcPVlhc81cvuqV4Q7pTl8ZzU37SM/edit?usp=drivesdk

### 005C — Failed-break reversal

Mechanism:
treat failed original breaks as opposite-side reversal opportunities.

Finding:
reversal sleeve roughly 45.5–48.3% win rate; more complementary than 005B but did not fix initial-hold persistence.

Disposition:
preserve as possible future specialist sleeve; NOT PROMOTED.

Source identity:
EXACT.

Sheet:
https://docs.google.com/spreadsheets/d/1q8MVbzpIuQQYvx3S4UAQMIUmLzR7sEF0cuMpUeG3a5Q/edit?usp=drivesdk

### 005D — First-seconds acceptance / early invalidation

Mechanism:
boundary loss + adverse flow + ER maintenance floor during first seconds.

Best net gain:
~0.31%.

5s/10s survival worsened materially.

Finding:
early-invalidating this way contradicts the Initial-Hold objective.

Disposition:
NOT PROMOTED.

**Artifact warning:** checkpoint result-source SHA does not resolve and differs from current source file. Treat 005D as research evidence only until rerun/reconstructed.

Sheet:
https://docs.google.com/spreadsheets/d/1186BfUL6fr6imDBQ_7P2wwts7bioVfdHNrwxo449rdY/edit?usp=drivesdk

### 005E — Initial-hold forensic census

Mode:
discovery unit, not candidate.

16,801 original trades / 82,774 causal snapshots.

Major discovery:

At 1s:
- baseline open-position 5s survival: 51.94%
- baseline 10s survival: 26.41%

S1 range < $0.50 + boundary held:
- support 342
- 5s survival 73.39%
- 10s survival 48.25%

S1 range $0.50–$0.75 + boundary held:
- support 3,464
- 5s survival 68.24%
- 10s survival 39.29%

Interpretation:
successful entries often follow:

`IMPULSE -> ACCEPTED BOUNDARY -> MICRO-CONSOLIDATION / COOLING`

not continuous high flow/high ER.

Source identity:
EXACT.

Sheet:
https://docs.google.com/spreadsheets/d/1Ngbap0ordQVpEnrBdrxoatLXm9uAMexiJUUD8ZbL9lQ/edit?usp=drivesdk

### 005F — Direct + delayed accepted-consolidation entry

Attempt:
translate 005E accepted-consolidation state into a delayed fresh entry.

Finding:
recovery sleeve win rate remained roughly 39–44%.

The forensic state predicts survival of an already-open position better than edge for a new delayed entry.

Disposition:
NOT PROMOTED.

Source identity:
EXACT.

Sheet:
https://docs.google.com/spreadsheets/d/1Cv_fiMOOr6Lmn1rmbjH8RP9DPZBoKNjj5zUSxoJLpLw/edit?usp=drivesdk

### 005G — Dual-state initial-hold validator

Attempt:
keep original entry only if direct flow ownership or accepted consolidation validates the hold.

Best net:
~1.51% improvement.

Collateral:
- winner retention ~87.17%
- 5s survival -7.80pp
- 10s survival -4.12pp

Finding:
hard keep/kill interpretation of accepted consolidation is too destructive.

Disposition:
NOT PROMOTED.

**Artifact warning:** checkpoint result-source SHA does not resolve and differs from current source file. Do not use as direct MT5 translation parent without rerun/reconstruction.

Sheet:
https://docs.google.com/spreadsheets/d/12VclDyjItrZ_OjsnCefxGUBE1PV1IwzaDsvgmyjMyxY/edit?usp=drivesdk

### 005H — Initial trailing shield / activation timing

**This is the strongest current Initial-Hold breakthrough.**

Control:
R9 trail activation +$0.10 / distance $0.03.

High-leverage cell:
trail activation +$0.30, no extra shield delay.

Results:
- trades: 16,578
- wins: 6,131
- gross profit: **$2,377.80**
- gross loss: -$6,050.23
- net: -$3,672.43
- average hold: **9.027s**
- 5s survival: **+11.01pp**
- 10s survival: **+10.69pp**
- 15s survival: **+8.50pp**

Interpretation:
R9's early fixed trailing is a genuine Initial-Hold bottleneck.

Looser activation gives trades room to survive and creates more favorable excursion/gross profit, but the unchanged downstream R9 lifecycle fails to harvest/protect those longer-lived paths efficiently.

This exposes a later Hold/Exit/High-Profit problem but does **not** authorize that later phase yet.

Status:
RESEARCH BREAKTHROUGH — NOT PROMOTED.

Source identity:
EXACT.

Sheet:
https://docs.google.com/spreadsheets/d/1SWEzgzBpfgYxMyc2LMKY68qEmxqND2z-iMrlPygEF-Y/edit?usp=drivesdk

### 005I — Early breathing trail distance

Kept +$0.10 activation and widened trail distance during a short early window.

Finding:
distance is lower leverage than activation timing.

High-retention cell:
5s / $0.05:
- 98.05% winner retention
- ~+0.98pp 5s survival
- ~0pp 10s survival

High-survival:
10s / $0.20:
- +9.45pp 5s
- +8.05pp 10s
- only 76.36% winner retention

Disposition:
NOT PROMOTED.

Source integrity:
checkpoint-producing source blob was older than current file, but the exact old blob remained retrievable and is now preserved at:

`research/delta/recovered_sources/DELTA_005I_001_RESULT_SOURCE_8f22b1ff.py`

Recovered report also added.

Sheet:
https://docs.google.com/spreadsheets/d/1Q0QvgdOX5Nx96YdnLeS9XaAosz7U_kBwx4hMXYdk2Ck/edit?usp=drivesdk

### 005J — State-conditioned initial protection

Used 005E accepted consolidation to selectively loosen early protection.

Canonical checkpoint best region:
- 16,753 trades
- 7,149 wins
- winner retention 97.25%
- net -$3,730.61
- net-loss improvement ~1.00%
- gross loss worsened ~2.19%
- 5s +3.40pp
- 10s +4.52pp
- 15s +1.43pp

Finding:
state conditioning is better than global loosening for activity preservation, but one static 1s accepted-state snapshot is too low leverage.

Status:
NOT PROMOTED.

**Canonical report:**
`research/delta/DELTA_005J_001_STATE_CONDITIONED_INITIAL_PROTECTION_REPORT.md`

**Superseded/conflicting noncanonical report:**
`research/delta/DELTA_005J_001_STATE_CONDITIONED_PROTECTION_REPORT.md`

The canonical report is the one matching the canonical checkpoint.

**Artifact warning:** checkpoint result-source SHA does not resolve and differs from current source. Rerun/reconstruct before using 005J as an MT5 translation parent.

Canonical Sheet:
https://docs.google.com/spreadsheets/d/1fP3FXWAiWEs_MSy9ScmMpQbGJFIc0ls1VnT1aoF98eE/edit?usp=drivesdk

### 005K — MFE-gated initial protection

Preserved 005H +$0.30 activation and added one MFE-triggered stop lock.

Finding:
creates a real Pareto frontier but no tested cell dominates 005H.

Examples:
- +$0.25 trigger / +$0.05 lock preserves 99.59% of 005H winners and improves gross loss ~1.81%, but loses ~1.08pp 5s and ~1.27pp 10s survival
- +$0.20 / +$0.05 improves gross loss ~4.32% while keeping winner count near 005H, but loses ~2.7pp / ~3.15pp survival

Status:
NOT PROMOTED.

**Artifact warning:** checkpoint result-source SHA does not resolve and differs from current source. Rerun/reconstruct before direct MT5 translation.

Sheet:
https://docs.google.com/spreadsheets/d/1GmA0TwTeWQibZqFpQOh1p7LoaIdRA3mEIbb-wK7qKB0/edit?usp=drivesdk

### 005L — Multi-stage initial protection

Tested explicitly designed stop ladders.

Finding:
no ladder dominates 005H.

Repeated stop tightening converts too many recoverable 005H winners into exits.

Status:
NOT PROMOTED.

**Artifact warning:** checkpoint result-source SHA does not resolve and differs from current source. Rerun/reconstruct before direct MT5 translation.

Sheet:
https://docs.google.com/spreadsheets/d/1EgQDfNLrChF-ZzdG_Ou8MxsYG4nIWsvT1KBwM82xWl0/edit?usp=drivesdk

### 005M — Trail ratchet step / frequency

Parent:
005H mechanics:
- activation +$0.30
- trail distance $0.03
- hard stop $0.30
- max hold 30s

20-cell grid:
- trail step: 0 / 0.03 / 0.05 / 0.10 / 0.15
- minimum update interval: 0 / 250 / 500 / 1000ms

Best net cell:
step $0.05 / interval 500ms:
- 16,564 trades
- 6,111 wins
- winner retention vs 005H: **99.67%**
- net -$3,661.62
- net-loss improvement vs 005H: **0.29%**
- gross-loss improvement: **0.07%**
- 5s survival: **+0.73pp**
- 10s survival: **+0.52pp**
- trail moves reduced **32.47%**

Highest-survival cell:
step $0.15 / interval 1000ms:
- winner retention: **99.30%**
- 5s +1.32pp
- 10s +1.05pp
- 15s +0.62pp
- trail moves reduced **41.96%**
- economics still sub-percent

Finding:
ratchet step/frequency is a **real secondary refinement** around 005H, but not a large breakthrough.

Do not fine-tune it next.

Status:
COMPLETE — NOT PROMOTED.

Source identity:
EXACT.

The required post-test Sheet was missing after timeout and was recovered from the surviving full 20-cell result:

https://docs.google.com/spreadsheets/d/1EcOfavsfFO2QxqHltv11e6fxO79XTh3k49ysD10qefo/edit?usp=drivesdk

---

## 10. Current scientific interpretation

The Entry + Initial-Hold campaign has ruled out several low-leverage interpretations:

- universal tick-flow gating
- simple retest/reclaim recovery
- binary accepted-state keep/kill
- static ER maintenance invalidation
- broad early trail-distance widening
- one static accepted-consolidation routing state
- one-time MFE lock as a complete answer
- multi-stage stop ladders as a complete answer

The strongest evidence now is:

### Primary breakthrough

**Early trailing activation timing is a real R9 Initial-Hold bottleneck.**

005H materially increased:
- average hold
- 5s survival
- 10s survival
- 15s survival
- gross profit / favorable excursion

### Secondary refinement

005M shows that slowing trail ratchet churn with a step/update-frequency rule can add roughly another 0.5–1.3pp persistence while preserving >99% of 005H winners.

Its economic effect is too small to justify more local tuning now.

### Important forensic state

005E accepted-consolidation remains useful as a descriptive market state, but attempts to use it as:
- delayed fresh entry
- binary hold validator
- simple protection router

did not generate large enough economic gains.

### No promotion yet

No 005A–005M candidate has met the project's full promotion gate.

No primary metric has reached a lock.

No candidate is authorized for MQL5 translation.

---

## 11. Artifact integrity / timeout recovery findings

Machine-readable audit:
`research/delta/handoffs/DELTA_ARTIFACT_AUDIT_2026-10-02.json`

### Repaired

- 005B missing preregistration markdown recovered from manifest/ledger.
- 005B missing final report recovered from checkpoint/ledger.
- 005I missing final report recovered from checkpoint/ledger.
- exact 005I result-producing source blob preserved under `recovered_sources/`.
- 005M missing post-test analysis Sheet rebuilt from surviving full result.
- 005M checkpoint/report updated with recovered Sheet.

### Unresolved source-identity risks

The following checkpoints record a result-producing source SHA that does not resolve as a Git blob and differs from the current branch source:

- 005D
- 005G
- 005J
- 005K
- 005L

These results remain useful research evidence.

However, **do not use any of those units as a direct Python->MQL5 translation parent** until the exact behavior is reproduced from a committed frozen source and a new checkpoint proves parity.

### 005I special case

005I also had a source mismatch, but its original checkpoint source blob was still retrievable and has been preserved explicitly.

Therefore 005I is recoverable.

### 005J report conflict

Two 005J reports exist.

Canonical:
`DELTA_005J_001_STATE_CONDITIONED_INITIAL_PROTECTION_REPORT.md`

Noncanonical/superseded:
`DELTA_005J_001_STATE_CONDITIONED_PROTECTION_REPORT.md`

Use the canonical report because it matches the canonical checkpoint.

---

## 12. Future MT5 EA safety requirements

Do not build the DELTA EA yet.

Before any candidate becomes MT5-worthy, the exact accepted candidate/composite must have:

1. exact frozen Python source SHA
2. exact preregistration + manifest
3. exact full Stage-A result/checkpoint
4. Jan-Jul frozen month-by-month replay
5. P50/P75/P90 execution-friction sensitivity
6. DUKAS_NATIVE robustness replay
7. Coinexx parity fixtures
8. Python->MQL5 tick/candle parity fixtures
9. feature timing/right-edge contract
10. session/DST contract
11. specialist router/ownership contract
12. execution/fill/stop/trailing parity contract
13. maintenance/risk contract
14. exact opportunity/trade ledger semantics
15. human QA
16. explicit owner approval
17. `mt5_translation_ready=true`

Candidate units with currently safe exact source identity:
- 005A
- 005B
- 005C
- 005E
- 005F
- 005H
- 005I via recovered source snapshot
- 005M

Units that must be rerun/reconstructed before direct translation:
- 005D
- 005G
- 005J
- 005K
- 005L

The verified environment layers 001–004 are intact and suitable for eventual translation work.

---

## 13. Multi-specialist and session assumptions still pending production contracts

The eventual DELTA system is assumed to be multi-specialist and session-aware across:
- Australia
- Asia
- Russia
- India
- Middle East
- Europe
- UK
- New York

Exact session clocks, DST boundaries, overlaps and transition buffers are still pending a dedicated session-timing contract.

Medium/high-impact news remains a potential opportunity regime, not an automatic blackout.

The news feed/provider/taxonomy/as-of timestamp contract remains pending.

These pending contracts must be frozen before final MT5 production implementation if the final composite uses them.

---

## 14. Maintenance / capital layer remains separate

Initial lot:
0.01 fixed.

Starting capital by primary-lock count:
- 0 locks: $100,000
- 1 lock: $1,000
- 2 locks: $500
- 3 locks: $500
- 4 locks: $100

Below $1,000:
small-account survivability rules remain empirical/pending.

At/above $1,000 provisional maintenance envelope:
- planned loss ceiling: 0.5%
- daily warning: 2.5%
- daily hard stop: 4%
- weekly warning: 5%
- weekly hard stop: 8%

No martingale/grid recovery.

The future lot-sizing ladder is owner-pending.

---

## 15. Timeout-safe workflow for the new chat

Because repeated delivery timeouts occurred, future work should stay in small durable units.

For each research unit:

1. preregister and commit
2. update cursor
3. stop/checkpoint
4. write/commit source
5. update cursor
6. stop/checkpoint
7. run bounded compute
8. persist checkpoint before interpretation
9. stop/checkpoint
10. create per-test Sheet
11. write leverage conclusion into master Doc
12. commit report
13. update `CURRENT_STATE`
14. only then begin the next unit

Never chain several new experiments into one long delivery.

After any timeout:
- read `CURRENT_STATE.json`
- read this handoff
- read the audit JSON
- inspect the last unit's exact checkpoint/source/report/Sheet
- resume the first incomplete durability step
- never infer missing work from memory

---

## 16. Authoritative current cursor for the next chat

### Last complete research unit

`DELTA_005M_001_TRAIL_STEP_FREQUENCY`

### Strongest current breakthrough

`DELTA_005H_001_INITIAL_TRAILING_SHIELD`

### Secondary refinement

`DELTA_005M_001_TRAIL_STEP_FREQUENCY`

### Current research focus

ENTRY + INITIAL-HOLD

### Deferred

HOLDING-TRADE + EXIT + HIGH-PROFIT

### Next scientific unit

**UNDEFINED ON PURPOSE.**

Do not invent 005N from memory.

The next chat must first review:
- 005H
- 005M
- 005E forensic result
- the artifact audit

Then perform GOV-013 quick leverage analysis and preregister one new distinct Entry + Initial-Hold micro-unit.

### Explicitly do not do

- do not resume stale 005I compute
- do not open August
- do not build MQL5 yet
- do not promote 005D/G/J/K/L directly into MT5
- do not begin Hold/Exit/High-Profit phase without owner acceptance of Entry + Initial-Hold
- do not fine-tune 005M step/frequency next unless a new leverage analysis specifically justifies it

---

## 17. New-chat bootstrap prompt

Paste or say this in the next chat:

> Carson, read the DELTA Full New-Chat Handoff dated 2026-10-02, CURRENT_STATE.json, and DELTA_ARTIFACT_AUDIT_2026-10-02.json on the delta branch. Then read the DELTA_005 master research ledger, 005H checkpoint/report, and 005M checkpoint/report plus its recovered analysis Sheet. Confirm the actual cursor is after 005M, not the stale 005I cursor. Do not run new research until you have verified the artifact integrity warnings and summarized the Entry + Initial-Hold leverage state. Keep August sealed and do not begin MQL5 or Holding-Trade + Exit + High-Profit research.

---

## 18. Final handoff condition

The DELTA project is recoverable.

The verified R9 baseline, causal tick lab, Coinexx parity layer, modeled Dukascopy research surface, governance, compact metrics, experiment sources, checkpoints, reports and analysis Sheets are substantially intact.

The main timeout damage was administrative:
- stale status cursor
- a few missing narrative artifacts
- one missing 005M analysis Sheet
- several candidate checkpoint/source identity mismatches

The recoverable narrative/Sheet gaps were repaired.

The remaining source-identity mismatches are explicitly quarantined from direct MT5 translation.

The next chat can continue safely from the post-005M leverage-review point without repeating the entire research program.
