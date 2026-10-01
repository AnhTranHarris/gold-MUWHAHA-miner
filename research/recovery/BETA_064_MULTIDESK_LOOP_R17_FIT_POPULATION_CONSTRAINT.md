# BETA064 missing multidesk helper recovery — R17 FIT population constraint

**Status:** ACTIVE RECOVERY / RECOVERY_UNCERTIFIED  
**Scope:** BETA only; August SEALED; no Alpha/Gamma; no MQL5.

## Frozen invariant

The exact frozen Entry LightGBM tree export records root `internal_count=30579`. Therefore the historical January FIT parent candidate population used to train the frozen Entry model is exactly:

**30,579 rows**

This is a hard population fingerprint.

## R17 broad-persistence stress reconstruction

Using original January Dukascopy ticks, historical LEFT-edge five-second state for forensics, exact V2 E1/E2/E4 replacements, the current source-grounded broad masks, and direct persistent mask-row emission for E6/E9/E11 as introduced only for R15/R16 forensic upper bounds:

**R16 broad-persistent Jan FIT = 99,215 candidates**

Difference from frozen reference:

**+68,636 rows**

Largest broad-persistent populations:
- E6_VALUE_REVERSION: 62,076
- E11_KINETIC_IGNITION: 14,301
- E9_LEVEL_BREAK: 5,296

The remaining desks together account for only ~17.5K in this reconstruction.

## Interpretation

R15/R16 remain valid falsification results:

- E6 cannot be broad-mask FALSE→TRUE edge only.
- E11 cannot be broad-mask FALSE→TRUE edge only.
- E9 cannot be broad-mask FALSE→TRUE edge only.

But R17 proves the converse is also false:

> the lost helper did **not** emit every active broad-mask row as a proposal.

Therefore E6/E9/E11 require a missing **within-state sub-clock / secondary event gate / persistence-debounce rule** that can fire after run start but suppresses most active rows.

The R15/R16 `edge_only=False` scaffold behavior is hence an explicit **BROAD-MASK FORENSIC UPPER BOUND**, not a candidate-recovery claim.

## Cross-check against prior R9C clue

The earlier R9C universal-edge reconstruction produced 30,613 January FIT hypotheses, only +34 versus the frozen 30,579, but R11 proved the universal edge timing wrong outside January. The near-count was therefore accidental population cancellation, not source identity.

A fresh simplified all-edge counter on the current direct January reconstruction gives ~31.6K, again showing that aggregate counts can look deceptively close while specialist timing is wrong.

**Rule:** candidate count alone is necessary but never sufficient. Timestamp/side/specialist/raw_score parity remains mandatory.

## Recovery consequence

Do not promote the current RECOVERY_UNCERTIFIED `candidates_h1()` output as the historical helper.

For E6/E9/E11:
- broad mechanism mask = behaviorally constrained;
- edge-only emission = rejected;
- every-active-row emission = rejected as exact source;
- exact in-state sub-clock = UNKNOWN.

## Next action

1. Mine predecessor BETA state-machine source and Sep-30 document revisions specifically for persistence age, expiry, cooldown, re-trigger, derivative-cross, or sub-state logic that can generate events inside a persistent broad mask.
2. Use the 30,579 FIT fingerprint jointly with selected-timestamp run ages—not either one alone—to constrain candidate clocks.
3. Seek a per-specialist FIT population fingerprint from any historical output/log/model training print.
4. Keep raw_score and one-second qv_imb unresolved unless direct evidence appears.
5. Do not attempt Checkpoint-03 MT5 parity. Historical LEFT-edge reconstruction remains forensic; a newly named RIGHT-edge checkpoint must ultimately be trained/validated.
