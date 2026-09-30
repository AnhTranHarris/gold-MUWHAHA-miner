# BETA064 CHECKPOINT 02E — Session-Aware Derivative Children, Coverage Utility & New-Chat Research Handoff

**Date:** 2026-09-30  
**Branch:** `beta`  
**Frozen control:** BETA064 Major Checkpoint 02 — immutable  
**Research parent:** Checkpoint-02C / C02D opportunity-expansion children  
**Scope:** ENTRY→HOLD only  
**HOLD→EXIT:** intentionally deferred  
**August:** SEALED and not read  
**Alpha/GAMMA:** DEAD / PROHIBITED DEPENDENCIES / ZERO IMPORTS  
**Status:** DERIVATIVE RESEARCH COMPLETE — ARCHITECTURAL DIRECTION ACCEPTED — NOT A NEW MAJOR CHECKPOINT

## Executive conclusion

Second- and third-order derivatives of Entry specialists **do help**, but the Jan–Jul Dukascopy evidence rejects using them as independent Entry clocks.

The useful architecture is:

`valid parent specialist thesis`
→ `session authority`
→ `parent-aware D1/D2/D3 microstructure state`
→ `derivative admission/timing adapter`
→ `coverage-utility router`
→ `one-position ownership`
→ `ENTRY→HOLD thesis packet`

The derivative child never creates a trade without a valid parent thesis in the current research design.

This is important because broad standalone derivative clocks produced only ~17–26% Entry→Hold survivability, while derivative features materially improved failure discrimination **after** the parent specialist had already narrowed the state space to a high-quality Entry→Hold population.

## Why derivatives were researched

The owner proposed exploring second- and third-order derivatives of Entry specialists, with each derivative child made session-aware like its parent.

The hypothesis was that:
- D1 velocity can tell whether a parent thesis is actually moving;
- D2 acceleration can identify strengthening/weakening of that motion;
- D3 jerk can detect changes in acceleration early enough to distinguish exhaustion, rejection, or renewed expansion;
- the useful derivative order may depend on session and parent mechanism.

This hypothesis is supported as a **mechanical research direction**, not as a community performance claim.

## Community / public-mechanics cross-reference

Only reconstructible mechanics were borrowed. Performance claims were not accepted as evidence.

### MQL5 / MetaQuotes

1. PriceSpeed — price speed in points per minute; peak speed intended for breakout/pulse analysis:
https://www.mql5.com/en/code/26025

2. Institutional Kinematic Price Physics — explicit discrete first derivative / velocity and second derivative / acceleration implementation:
https://www.mql5.com/en/code/72936

3. VAMA — an older open-source MetaTrader implementation explicitly combining first-, second-, and third-order finite differences:
https://www.mql5.com/en/code/21044

4. VA — open-source velocity/acceleration oscillator:
https://www.mql5.com/en/code/20326

5. Price speed indicator blog — millisecond/tick-level price-speed motivation for microstructure analysis:
https://www.mql5.com/en/blogs/post/770046

6. Session Sync MT5 — separate local-session/DST handling for Sydney, Tokyo, London and New York:
https://www.mql5.com/en/market/product/191687

7. Broker server time / DST warning — explains why broker-hour filters can drift away from real London/New York sessions:
https://www.mql5.com/en/blogs/post/776634

### TradingView open/reconstructible mechanics

8. Gold Session Map & Sweep Signals — finished Asian range, London/overlap sweep, close-back-inside reclaim, ADR/session filters:
https://www.tradingview.com/script/bo1WdFiL-Gold-Session-Map-Sweep-Signals/

9. TradingView session/sweep scripts repeatedly classify wick-through + close-back-inside separately from accepted close/run, and use session VWAP/range context:
https://www.tradingview.com/scripts/search/sessions/page-12/

10. Session tools emphasize that Asia, London and New York have different volatility/range behavior, session VWAP/value anchors, and session-high/low liquidity:
https://www.tradingview.com/scripts/search/session/page-7/?script_type=indicators

### Community anecdotes

ForexFactory/Reddit discussions were used only as hypothesis generation. Repeated themes included:
- rejection speed matters;
- quick sweep/reclaim behaves differently from slow grind through a level;
- session hand-off changes the meaning of the same pattern;
- London/NY overlap tends to be more active than quieter sessions.

These anecdotes were never treated as proof and were independently checked against Dukascopy ticks.

## Causal derivative construction

### Completed 5-second parent-candidate derivative state

All derivative state is computed only from completed bars.

For midpoint (P_t):

- D1 / velocity:
  - 1-step velocity: `v1 = P_t - P_{t-1}`
  - 3-step velocity: `v3 = (P_t - P_{t-3}) / 3`
  - 12-step velocity: `v12 = (P_t - P_{t-12}) / 12`

- D2 / acceleration:
  - `a1 = v1_t - v1_{t-1}`
  - `a3 = (v3_t - v3_{t-3}) / 3`

- D3 / jerk:
  - `j1 = a1_t - a1_{t-1}`
  - `j3 = (a3_t - a3_{t-3}) / 3`

Each derivative is normalized by a trailing completed-state scale based on the median absolute midpoint change.

### Completed 1-second selected-trade derivative state

For already selected high-quality C02C trades, a finer 1-second causal state was built:
- D1: v1, v3, v5, v15
- D2: a1, a3, a5
- D3: j1, j3, j5
- spread first difference / 5-second change
- tick-count z-score / change

Each 1-second bucket is shifted to become observable only after the bucket completes.

No future ticks or forming-bar lookahead are used.

## Raw derivative-child specialist experiment

Eight session-aware derivative children were generated from parent concepts:

- E5D2 Session-VWAP Reclaim Acceleration
- E5D3 Session-VWAP Reclaim Jerk
- E6D2 Session-Value Curvature
- E6D3 Session-Value Jerk Turn
- E7D2 Sweep Snap Acceleration
- E7D3 Sweep Snap Jerk
- E9D2 Break Acceleration Acceptance
- E9D3 Break Jerk Persistence

Jan–Jul raw results:

| Derivative child | Candidates | Survival | FP success | Diagnostic value |
|---|---:|---:|---:|---:|
| E5D2 | 19,425 | 21.40% | 11.95% | -$15,373.81 |
| E5D3 | 14,881 | 23.60% | 13.04% | -$12,024.79 |
| E6D2 | 677,702 | 18.85% | 12.75% | -$509,661.77 |
| E6D3 | 212,854 | 24.10% | 15.62% | -$159,004.73 |
| E7D2 | 8,099 | 22.84% | 12.74% | -$6,681.00 |
| E7D3 | 5,631 | 25.84% | 14.19% | -$4,645.73 |
| E9D2 | 4,792 | 17.13% | 14.19% | -$3,772.68 |
| E9D3 | 4,017 | 18.70% | 15.29% | -$3,214.60 |

Third-order children improve raw survival over D2:
- E5: +10.3% relative
- E6: +27.9%
- E7: +13.1%
- E9: +9.1%

But absolute survival remains far below 85%.

**Decision: raw derivative specialists are rejected as independent Entry clocks.**

## Broad candidate LOMO discrimination

A LightGBM survivability model was trained leave-one-month-out with and without derivative features on the huge raw derivative-candidate population.

Held-out AUC improvement from adding derivatives was small:

| Held-out month | Base AUC | + derivatives | Delta |
|---|---:|---:|---:|
| Jan | 0.72484 | 0.72569 | +0.00085 |
| Feb | 0.72123 | 0.72242 | +0.00119 |
| Mar | 0.72586 | 0.72697 | +0.00110 |
| Apr | 0.73135 | 0.73143 | +0.00008 |
| May | 0.73602 | 0.73693 | +0.00090 |
| Jun | 0.73030 | 0.73079 | +0.00049 |
| Jul | 0.73597 | 0.73559 | -0.00038 |

No meaningful standalone >=85% derivative tail survived cross-month testing.

This confirms that derivatives do not rescue a weak parent-state universe.

## Positive result — derivative meta-admission on C02C

The same derivative idea becomes useful when applied **after** a valid parent specialist has already selected a high-quality C02C Entry→Hold candidate.

Leave-one-month-out survivability AUC:

| Month | Existing C02C state | + causal micro derivatives | Delta |
|---|---:|---:|---:|
| Jan | 0.68416 | 0.69123 | +0.00707 |
| Feb | 0.64284 | 0.65324 | +0.01040 |
| Mar | 0.65356 | 0.68596 | +0.03240 |
| Apr | 0.62268 | 0.67938 | +0.05669 |
| May | 0.65740 | 0.66644 | +0.00905 |
| Jun | 0.63547 | 0.69242 | +0.05695 |
| Jul | 0.63394 | 0.65187 | +0.01793 |

Derivatives add material failure-discrimination power inside the already-valid parent context.

### Cross-fitted low-tail rejection / survivability reserve

A threshold was chosen on the other six months to retain at least ~92% of training trades while keeping the training portfolio at >=87.5% survival.

Applied to each held-out month:

- C02C before: 5,519 trades / 88.20% weighted survivability
- derivative meta-admission after: 5,094 trades / 89.20% weighted survivability
- retained: ~92.3%
- rejected: 425 trades

Held-out monthly survivability after derivative admission:

- Jan: 655 trades / 91.15%
- Feb: 910 / **87.14%**
- Mar: 1,402 / 88.23%
- Apr: 629 / 89.51%
- May: 568 / 90.67%
- Jun: 612 / 90.20%
- Jul: 318 / 90.25%

This fixes the C02C February robustness failure **without a February-specific rule**.

Important interpretation:
this is a **survivability reserve**, not an opportunity-expansion result by itself. The objective is to use that reserve later to admit genuinely new under-covered opportunities, not simply to shrink the trade count.

## Derivative-order ablation

Mean leave-one-month-out AUC across the selected C02C population:

- BASE: 0.64715
- D1 velocity: **0.67081**
- D2 acceleration: 0.66336
- D3 jerk: 0.66405

D1 is strongest globally.

Therefore the user hypothesis is partly confirmed:
second/third derivatives add information, but a universal D3-first architecture is not justified.

## Session-aware derivative order

Mean AUC by session:

| Session | Base | D1 | D2 | D3 | Best observed |
|---|---:|---:|---:|---:|---|
| Asia | 0.6601 | **0.6847** | 0.6772 | 0.6453 | D1 |
| Australia | 0.6454 | 0.6343 | **0.6574** | 0.6272 | D2 |
| Europe | 0.5062 | 0.5054 | 0.5042 | **0.5138** | D3, weak |
| Middle East | 0.5805 | 0.6389 | **0.6434** | 0.6239 | D2 |
| New York | 0.6195 | **0.6419** | 0.6353 | 0.6372 | D1 |
| UK | 0.6398 | 0.6676 | 0.6648 | **0.6723** | D3 |

A nested session-order selection using the other six months shows stable positive value mainly in:
- Middle East: D2
- New York: D1
- UK: D3

Australia D2 is plausible but not yet robust enough for a frozen rule.
Asia/Europe order selection was unstable.

**Decision: derivative order should be session-aware, but only stable session/order pairs may eventually become authoritative.**

## Parent-specialist-aware derivative order

Mean LOMO AUC:

| Parent | Base | D1 | D2 | D3 | Interpretation |
|---|---:|---:|---:|---:|---|
| E10 Compression Release | 0.5445 | 0.6501 | 0.6536 | **0.6594** | D3 strong |
| E11 Kinetic Ignition | 0.6099 | **0.6482** | 0.6427 | 0.6413 | D1 strong, but E11 already saturated |
| E12 Failed Expansion | 0.4567 | 0.4350 | 0.5290 | **0.5338** | D3 strong |
| E5 VWAP Reclaim | **0.6687** | 0.6317 | 0.6064 | 0.6357 | derivatives hurt |
| E6 Value Reversion | 0.5521 | **0.6134** | 0.5776 | 0.5925 | D1 strongest; D3 secondary |
| E7 Sweep/Reclaim | **0.6677** | 0.6184 | 0.6132 | 0.6125 | derivatives hurt |
| E9 Level Break | 0.4979 | **0.5248** | 0.5046 | 0.5090 | D1 modest help |

### Child-specialist recommendation

Do **not** create four free-floating E17–E20 derivative strategies.

Instead create internal derivative children:

- **E6.D1** — primary value-reversion velocity adapter
- **E6.D2-MIDEAST** — Middle East acceleration adapter
- **E6.D3-UK** — UK jerk-turn adapter
- **E6.D1-NY** — New York velocity adapter
- **E9.D1** — accepted-break velocity/persistence adapter
- **E10.D3** — compression-release jerk persistence adapter
- **E12.D3** — failed-expansion jerk/curvature reversal adapter

Do not currently add derivative children to:
- E5 VWAP Reclaim
- E7 Sweep/Reclaim

Do not expand E11 even though D1 improves discrimination, because E11 is already condition-cell saturated relative to the SYNTH denominator.

## Coverage-utility architecture

The next research router should score **incremental opportunity value**, not raw probability alone.

Research utility:

`coverage_utility = survival_probability × deficit_weight × novelty_weight × execution_feasibility`

Where:

- `survival_probability` protects the >=85% Entry→Hold objective;
- `deficit_weight` increases priority for under-covered session×specialist cells;
- `novelty_weight` penalizes temporal/state duplication with already-saturated desks such as E11;
- `execution_feasibility` penalizes high spread/ATR burden, stale quotes, bad ownership geometry, and infeasible broker state.

The derivative meta-score should be used to create a **survivability reserve**. The router may then spend that reserve only on independently validated under-covered opportunity cells.

Do not simply lower a global threshold.

## Next bounded research unit

Recommended:

**BETA064_CHECKPOINT_02F_DERIVATIVE_COVERAGE_UTILITY_EXPANSION**

1. Keep Major Checkpoint 02 immutable.
2. Keep C02C as research parent.
3. Apply cross-fitted derivative meta-admission to create quality reserve.
4. Focus opportunity expansion on E6, E9, E10, E12 in under-covered session cells.
5. Use only stable parent/session derivative pairs.
6. For each candidate added below an old parent threshold, require:
   - derivative meta-score support;
   - session-specific deficit weight;
   - novelty vs current selected positions;
   - no ownership conflict;
   - monthly portfolio survivability >=85%;
   - LOMO survivability >=85% before any checkpoint proposal.
7. Continue E13 Absorption-Divergence as shadow evidence only.
8. Leave E14–E16 shadow-only.
9. HOLD→EXIT remains deferred.
10. August remains sealed.
11. No MQL5 changes.

## Reproduction bundle

Google Drive BETA_RESEARCH contains:

`BETA064_CKPT02E_DERIVATIVE_ENTRY_HOLD_REPRO_BUNDLE.zip`

Drive file ID:
`1ASmoWdV6x3kRhryY-2elIWGdt9rPTHJq`

SHA-256:
`4cccedcf3aab353f1719afa29e08c1f9e743e252c7ee9bd1e2788fb86b24cd7c`

The archive includes:
- raw derivative candidate generator;
- LOMO modeling scripts;
- selected micro-derivative builder;
- derivative-order/session/specialist ablation scripts;
- compact CSV results;
- C02C selected-trade ledger;
- selected micro-feature/scored PKLs;
- README and checksum manifest.

Large monthly raw derivative-candidate PKLs are intentionally omitted from the archive because they are deterministically regenerated from the Jan–Jul raw Dukascopy tick files by the included generator.

## New-chat recovery invariant

A new chat must not infer state from memory alone.

Read, in order:

1. live `beta/CURRENT_STATE.json`
2. `research/BETA_064_MAJOR_CHECKPOINT_02_SESSION_AWARE_ENTRY_HOLD_FREEZE.md`
3. `research/mt5/BETA_064_MAJOR_CHECKPOINT_02_ENTRY_HOLD_MT5_PRODUCTION_CONTRACT.md`
4. `research/artifacts/BETA_064_MAJOR_CHECKPOINT_02_MODEL_MANIFEST.json`
5. C02B coverage diagnostic
6. C02C refinement record
7. C02D shadow-specialist record
8. this C02E derivative record
9. authoritative Google Drive new-chat handoff
10. BETA Research Journal

Hard reminder:
- Major Checkpoint 02 is the only frozen control.
- C02C/C02D/C02E are research children.
- Alpha/GAMMA are dead and prohibited.
- HOLD→EXIT is deferred.
- August is sealed.
- no official MQL5 without owner approval.
