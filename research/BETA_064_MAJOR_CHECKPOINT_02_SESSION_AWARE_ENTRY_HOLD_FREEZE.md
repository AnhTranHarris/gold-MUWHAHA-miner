# BETA064 MAJOR CHECKPOINT 02 — SESSION-AWARE ENTRY→HOLD FREEZE

**Branch:** `beta`  
**Authority:** NEW MAJOR CHECKPOINT — supersedes Major Checkpoint 01 for future Entry→Hold research and eventual MT5 parity work.  
**Scope:** ENTRY + HOLD only. HOLD + EXIT remains intentionally incomplete.  
**August:** SEALED.  
**Official EA promotion:** NO.  
**Official MQL5 implementation:** NOT YET AUTHORIZED / NOT YET COMPLETE.

## Frozen result

Major Checkpoint 02 is the frozen session-aware Entry→Hold architecture produced by adding the six-session contextual gap-fill layer on top of the immutable Major Checkpoint 01 control.

Frozen Jan–Jul observed panel:

| Month | Trades | Entry→Hold survivability | First-passage success | Diagnostic path-resolution value |
|---|---:|---:|---:|---:|
| Jan | 726 | 87.60% | 62.40% | +$894.48 |
| Feb | 910 | 87.36% | 58.24% | +$1,081.53 |
| Mar | 1,463 | 87.29% | 58.92% | +$1,640.56 |
| Apr | 589 | 90.15% | 61.46% | +$711.29 |
| May | 509 | 91.94% | 63.85% | +$576.06 |
| Jun | 585 | 88.21% | 61.88% | +$623.69 |
| Jul | 288 | 90.63% | 60.76% | +$254.46 |
| **Total** | **5,070** | **88.44% weighted** | **60.53% weighted** | **+$5,782.07** |

Checkpoint-01 control was 2,097 trades at 90.56% survivability. Checkpoint 02 therefore increases Entry→Hold coverage by **2.42×** while keeping every month above the owner's 85% survivability gate.

Leave-one-month-out held-out survivability also remained above 85% in all seven months; February was the weakest at approximately 86.36%.

## Frozen architecture

`causal tick chronology`

→ `multi-scale state engine`

→ `six-session authority surface`

→ `eligible E1–E12 Entry specialists`

→ `Major Checkpoint 01 router first ownership`

→ `session gap-fill router only when the frozen control is idle`

→ `one-position chronological ownership`

→ `fill + immutable origin/thesis packet`

→ `H1–H8 Hold specialist floor`

→ `shared continuation-value arbiter`

HOLD→EXIT is **not** part of this checkpoint.

## Session authorities

Session local-time definitions are frozen:

- Australia: Australia/Sydney, 08:00–17:00
- Asia: Asia/Tokyo, 09:00–18:00
- Middle East: Asia/Dubai, 08:00–17:00
- Europe: Europe/Berlin, 08:00–17:00
- UK: Europe/London, 08:00–17:00
- New York: America/New_York, 08:00–17:00

Use timezone-aware conversion. Do not hard-code UTC hours across DST-changing sessions.

Frozen session survival authorities:

- Australia 0.920
- Asia 0.900
- Middle East 0.915
- Europe 0.910
- UK 0.925
- New York 0.925

Session gap-fill precheck:

- broad session survivability score >= 0.89
- broad session economic score >= 0.08

Major Checkpoint 01 gates remain immutable inside the new checkpoint:

- `P_survive >= 0.88`
- `entry_score >= 0.30`

## Session-gap specialists

Only these specialists may create session gap-fill positions in this checkpoint:

- E5 VWAP Reclaim
- E6 Value Reversion
- E7 Sweep/Reclaim
- E9 Level Break
- E10 Compression Release
- E11 Kinetic Ignition
- E12 Failed Expansion

E1/E2/E3/E4/E8 remain available to the frozen base architecture but are not permitted to create session gap-fill entries until separately validated.

## Entry specialist registry

The twelve Entry specialists remain:

1. E1 Macro Structural Trend
2. E2 Structural Pullback / Reacceleration
3. E3 Opening Range Break
4. E4 VWAP / Value Trend Pullback
5. E5 VWAP / Value Reclaim
6. E6 Statistical Value Reversion
7. E7 Liquidity Sweep / Reclaim
8. E8 Key-Level Bounce / Rejection
9. E9 Key-Level Break / Acceptance
10. E10 Compression → Expansion
11. E11 Kinetic Ignition
12. E12 Failed Expansion / Contradiction

The authoritative specialist horizons/checkpoints are defined in:
`research/experiments/BETA_064_R1B2_SPECIALIST_REGISTRY.py`

## Hold specialist registry

The eight post-fill Hold roles remain:

- H1 Ignition Confirmation
- H2 Extension / Runner Persistence
- H3 Healthy Pullback
- H4 Reacceleration
- H5 Transient Scalp / Fragile Continuation
- H6 Stall / Chop
- H7 Failed Acceptance / Thesis Failure
- H8 Exhaustion / Climax

These roles inform continuation worthiness only. They are **not** a production exit policy.

## Frozen execution contract

- preserve stable original tick chronology including same-millisecond ordering where available;
- BUY observes and enters Ask;
- SELL observes and enters Bid;
- BUY mark-to-exit uses Bid;
- SELL mark-to-exit uses Ask;
- no retroactive fill;
- no future bar or future tick in runtime features;
- completed bars only unless a forming-bar feature is explicitly identified;
- confirmed pivots only after right-side confirmation completes;
- one account / one open 0.01-lot research position;
- Checkpoint-01 ownership has priority; a session addition must fit entirely outside reserved base-position intervals;
- on MT5, NewTick coalescing must be reconciled with CopyTicksRange or equivalent tick-history reconciliation;
- actual order/fill/exit ownership must be confirmed before rearm;
- $0.02 lifecycle fee is a research accounting assumption, not a final Coinexx production-cost specification;
- actual broker contract size, tick value, commission, stop/freeze levels, execution/slippage and symbol settings require parity certification.

## Frozen research artifacts

Major Checkpoint 02 is built from the following durable records:

- `research/BETA_064_R1B2_ENTRY_HOLD_85_SURVIVABILITY_RESEARCH_RECORD.md`
- `research/BETA_064_MAJOR_CHECKPOINT_01_ENTRY_HOLD_SURVIVABILITY_FREEZE.md`
- `research/BETA_064_CHECKPOINT_02_DUAL_TICK_SYNTH_VS_DUKAS_ENTRY_HOLD_DIAGNOSTIC.md`
- `research/BETA_064_CHECKPOINT_02A_SESSION_GAPFILL_SPECIALIST.md`
- `research/experiments/BETA_064_R1B2_SPECIALIST_REGISTRY.py`
- `research/experiments/BETA_064_C02_SESSION_GAPFILL_ROUTER.py`
- `research/results/BETA_064_C02A_SESSION_GAPFILL_MONTHLY.csv`

Key commits:

- R1B source/architecture audit: `a213944a354981762763c33bdf8cbc84fe7caabe`
- Entry→Hold 85% research record: `6734cb20906a9c27227fdffdc5039ab70cf9a2f1`
- Major Checkpoint 01 freeze: `6dd2f91a91d58abef30858385da4a47dcd97fb99`
- dual tick diagnostic: `c66fac3a69ef6a9aeb8e49d1b1ea376af05f25f9`
- session gap-fill implementation: `67f7116350b3287548c0af4ce9afa307fa4a929a`
- session gap-fill research record: `e6944ed001c9618d12e15bfe96e1574b3e0d88d6`
- session monthly results: `ff67b5314264d1756c2aaac39d892de14d3e171a`

## MT5 production rule

Future MT5 encoding must treat this checkpoint as a specification, not an invitation to reinterpret it.

No coder may:
- substitute Alpha/GAMMA rules;
- resurrect E060 as the master eligibility clock;
- merge Entry and Hold into one signal;
- allow the session router to replace frozen base trades;
- loosen the 0.88 base survivability authority;
- turn session thresholds into position sizing;
- invent a Hold→Exit policy;
- use current forming bars where the Python checkpoint used completed information;
- retrain or replace the learned models without creating a new checkpoint.

The corresponding MT5 production contract is:
`research/mt5/BETA_064_MAJOR_CHECKPOINT_02_ENTRY_HOLD_MT5_PRODUCTION_CONTRACT.md`

The model/reproducibility manifest is:
`research/artifacts/BETA_064_MAJOR_CHECKPOINT_02_MODEL_MANIFEST.json`

## Incomplete by design

This checkpoint deliberately does **not** define a complete live EA.

The missing production layer is HOLD→EXIT.

Until HOLD→EXIT is researched, frozen, implemented and parity-certified, any MQL5 build created from this checkpoint must be labeled **ENTRY+HOLD PARITY / RESEARCH BUILD ONLY**, not a finished trading EA.

August remains sealed.
