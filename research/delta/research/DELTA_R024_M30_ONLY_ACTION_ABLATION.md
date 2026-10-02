# DELTA R024 — M30-Only Ownership Action Ablation

**Status:** PREREGISTERED / STAGE-A REPLAY NOT YET STARTED  
**Parent:** GOV-018 P01/P02 ownership formulas  
**Scope:** ENTRY + INITIAL-HOLD / HIGH-CAPACITY DIRECTION OWNERSHIP  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Why R024 exists

GOV-018 P02 added `M30NetATR > 0.35` to the exact R010/P01 H1+micro250 ownership condition and improved P01 net in every February–July month.

Aggregate February–July P02 versus P01:
- additional net improvement +$1,146.53
- additional gross-loss reduction +$2,143.86
- +2.73 percentage points incremental net-loss closure
- +3.19 percentage points incremental gross-loss closure
- trade-retention change -3.36pp
- winner-retention change -3.33pp

R024 freezes the M30 threshold and isolates the causal action.

## Frozen parent P01

`H1NetATR > 0.35 OR micro250 <= -0.55`

If true:
- FLIP intended R9 side
- assign ownership
- suppress generic same-minute rearm after exit

Otherwise:
- ordinary R9 side
- ordinary R9 rearm

## Frozen M30-only event

`M30NetATR > 0.35 AND NOT(H1NetATR > 0.35 OR micro250 <= -0.55)`

## Preregistered variants

1. `P01_CONTROL`
   - KEEP original R9 side
   - no special ownership
   - ordinary R9 rearm

2. `M30_KEEP_OWNED`
   - KEEP original side
   - assign ownership
   - suppress generic same-minute rearm

3. `M30_FLIP_NORMAL`
   - FLIP intended side
   - do not retain ownership
   - ordinary R9 rearm

4. `P02_FLIP_OWNED`
   - FLIP intended side
   - assign ownership
   - suppress generic same-minute rearm
   - this is the existing P02 architecture

5. `M30_SKIP`
   - skip current M1 opportunity

Everything outside the M30-only branch remains exact P01.

## Stage-A contract

Window:

`[2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)`

Primary surfaces:
- P50
- P75
- P90

Native:
- diagnostic only

Modeled-surface advancement:
- trade retention >=80% R9
- winner retention >=80% R9
- candidate improves P01 net on P50/P75/P90
- <=5% gross-loss or drawdown deterioration versus P01

No threshold/action invention is permitted after seeing Stage-A results.

Any survivor requires exact month-by-month validation before promotion.

## Causal interpretation

The ablation separates:
- direction effect: KEEP vs FLIP
- ownership effect: ordinary rearm vs owned/no-rearm
- avoidance effect: SKIP
- direction × ownership interaction

## Execution source

`r024_m30_only_action_ablation.py`

SHA-256:

`5a5e0ddab9703a088ad3fd1cd3ba2447f69ec972e1671c2b528625dc1ae23588`

## Drive

Google Doc:

https://docs.google.com/document/d/1bc0h303EyDstcI2ToC9uAoFOk8ywBFecTi7pISv9GqQ/edit

Workbook tabs:
- `43 R024 Prereg`
- `44 R024 Results`

## Current gate

- Stage-A replay: NOT STARTED
- promoted candidate: NONE
- metric locks: NONE
- August: SEALED
- MQL5: NOT AUTHORIZED

## Stage-A completion

R024 is complete across P50/P75/P90 plus native diagnostic.

### Modeled-surface survivor

`M30_KEEP_OWNED` is the only non-control action that passed every modeled-surface gate.

- P50: +$95.55 net vs P01; trade retention 83.77%; winner retention 88.54%.
- P75: +$103.30 net vs P01; trade retention 83.48%; winner retention 88.93%.
- P90: +$23.47 net vs P01; trade retention 80.87%; winner retention 84.85%.

`M30_FLIP_NORMAL` failed net on every modeled surface.

`P02_FLIP_OWNED` passed P50/P75 but failed P90.

`M30_SKIP` improved net materially but failed the preregistered activity floor on all modeled surfaces.

### Native diagnostic

Native is diagnostic only.

- P01_CONTROL: 91 trades, 20 wins, net -$39.08.
- M30_KEEP_OWNED: 91 trades, 20 wins, net -$39.08.
- M30_FLIP_NORMAL: 99 trades, 15 wins, net -$53.229.
- P02_FLIP_OWNED: 91 trades, 15 wins, net -$47.172.
- M30_SKIP: 77 trades, 15 wins, net -$37.484.

Native therefore does not contradict the modeled-surface conclusion.

### Decision

`M30_KEEP_OWNED` becomes the sole R024 validation survivor.

It is **not promoted**, creates **no metric lock**, and may not be retuned.

Next required research unit:

`EXACT_MONTH_BY_MONTH_JAN_JUL_P75_VALIDATION_OF_M30_KEEP_OWNED`

with the same frozen condition:

`M30NetATR > 0.35 AND NOT(H1NetATR > 0.35 OR micro250 <= -0.55)`

and the same KEEP-owned / suppress-rearm action.

### Result hashes

- P90: `71579b3326573c76e0d70734251171c8feaedf0ed701c0641997fa5b7c7f1724`
- Native: `dc382a59dbb62dfcf5f7b55465bafb76adcc91ab4d649064128b101853dc45f0`

