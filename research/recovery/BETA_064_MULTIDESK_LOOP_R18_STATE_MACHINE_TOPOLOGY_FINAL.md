# BETA064 missing multidesk helper recovery — R18 State-Machine Topology Constraint and Final Closure

**Date:** 2026-10-01  
**Status:** RECOVERY CLOSED SAFELY / EXACT HISTORICAL SOURCE NOT RECOVERED  
**Lineage:** independent BETA only  
**Alpha/GAMMA:** prohibited and not inspected  
**August:** SEALED and not opened  
**MQL5:** not authorized

## Purpose

R17 proved that neither a universal broad-mask FALSE→TRUE edge nor emission on every active broad-mask row can be the lost `beta064_multidesk_loop.py` source. R18 performs the final bounded archaeology requested by R17: inspect surviving BETA state-machine implementations and September-30 BETA064 revisions for the topology of an in-state retrigger/debounce/sub-clock.

This unit does **not** invent missing thresholds. It separates what is now strongly constrained from what remains unrecoverable.

## Hard invariants carried from R14–R17

- Frozen historical January FIT Entry population: **30,579 rows**.
- Historical BETA064 Checkpoints 01/02/03 are left-edge contaminated and remain **FORENSIC ONLY**.
- Corrected RIGHT-edge R14 rebuild was executed and rejected for promotion.
- E6/E9/E11 broad mechanism masks have high selected-timestamp recall, but:
  - broad-mask edge-only emission is rejected;
  - every-active-row emission is rejected;
  - therefore an in-state secondary event clock is required.
- One-second `qv_imb` source arithmetic and exact BETA064 `quote_pressure` source identity remain unrecovered.
- Exact candidate timestamp/side/specialist/raw_score parity remains unavailable.

## September-30 BETA064 child sub-clock test

A later durable BETA064 research child exists at:

`research/experiments/BETA_064_ALL12_ENTRY_SPECIALIST_BROAD_CLOCK_PRESCREEN_01.py`

Commit: `872b7cf66b662bde97245df02edcea592fbe1061`.

Its emitter uses a clear event-clock topology:

```text
secondary mechanism mask
    -> FALSE→TRUE edge of that secondary mask
    -> per-emitter 30-second debounce
    -> proposal
```

For E6/E9/E11 the child uses richer transient sub-state conditions inside the broader desk state, including acceleration/velocity/session/friction constraints. This is exactly the *kind* of mechanism capable of firing inside a long broad E6/E9/E11 state without emitting every five-second row.

However, the contemporaneous research record explicitly says this child is **not** an exact replay/reconstruction of the missing historical parent generator.

R18 independently tested those later formulas against historical LEFT-edge Jan–Mar selected timestamps.

### Falsification result

- Later-child January FIT population: **5,511**, versus frozen historical **30,579**.
- Jan–Mar preserved selected rows tested: **3,293**.
- Exact timestamp + side + specialist matches: **969 / 3,293 = 29.426%**.
- E6 exact recall: **100 / 502 = 19.920%**.
- E9 exact recall: **54 / 508 = 10.630%**.
- E11 exact recall: **563 / 1,263 = 44.576%**.
- Timestamp offset comparison was also strongest at zero shift; nearby ±5s/±10s shifts did not rescue parity.

**Classification:** later September-30 sub-clock formulas are **REJECTED AS HISTORICAL SOURCE IDENTITY**.

They remain useful only as independent BETA architectural evidence that a transient in-state sub-mask plus debounce is a valid design pattern.

## Exact predecessor state-machine evidence

Surviving earlier BETA source independently preserves multiple stateful event-clock patterns.

### BETA009 R9-entry predecessor

`BETA_009_JAN_R9_ENTRY_PARALLEL.py` preserves a persistence gate in which:

- threshold state remains armed across distinct observed ticks;
- at least **3 ticks** must satisfy the condition;
- at least **250 ms** must elapse from the persistence start;
- the state resets when the threshold condition lapses;
- same-minute ownership can rearm the opposite side after exit, up to the preserved rearm limit.

This demonstrates a **counter + elapsed-time persistence sub-clock**, not one universal bar-edge event.

### BETA009 bounded setup-state predecessors

`BETA_009_JAN_PARALLEL_ENTRY_SCREEN.py` preserves:

- failed-ignition setup with a **2,000 ms expiry**;
- dwell-beyond-level setup requiring **>=250 ms**, cancelled if the condition lapses or exceeds **2,000 ms**;
- break → retest → rebreak state with **8,000 ms expiry**;
- a **500 ms post-exit cooldown** in the early-momentum branch;
- setup reset on entry/expiry/invalidating state.

This demonstrates **arm → persist/retest → fire → expire/reset** logic.

### BETA029 observed-confirmation FSM

`research/experiments/BETA_029_PROOF_FSM_PURE.py` preserves an incremental observed-tick finite-state machine:

```text
origin event arms bounded window
    -> observe only later real ticks
    -> transition through retreat/renewal state
    -> fire on confirmation
    -> cancel on timeout or quote gap
```

It never fills retroactively at the origin.

## R18 topology conclusion

Across independent BETA predecessor source and the later BETA064 child, the common architecture is:

```text
broad market-mechanism state
    -> specialist-specific secondary/transient state
    -> persistence/retest/renewal or transition condition
    -> bounded elapsed-time / tick-count / debounce rule
    -> proposal
    -> reset/rearm on lapse, expiry, or ownership transition
```

This topology explains all three R17 constraints simultaneously:

1. a proposal may occur **after** broad-state run age 0;
2. the desk does **not** emit every active broad-state row;
3. aggregate proposal density can remain near the frozen 30,579 FIT population.

**Classification:** `SPECIALIST_SPECIFIC_IN_STATE_FSM_TOPOLOGY = STRONGLY_SUPPORTED`.

What is **not** recovered:
- the exact historical E6/E9/E11 FSM states/thresholds;
- exact expiry/debounce values used by the lost helper;
- exact E3/E8 residual gates;
- exact raw_score formulas where not preserved;
- exact one-second qp/qv builder;
- an exact pre-ownership candidate/prediction ledger.

The exact BETA009 thresholds and the later BETA064 child thresholds must **not** be transplanted into the historical helper. Doing so would manufacture false precision.

## Code disposition

The file:

`research/recovery/beta064_multidesk_loop_RECOVERY_UNCERTIFIED.py`

is retained only as a forensic scaffold. Its broad persistent E6/E9/E11 emission is an explicit **upper-bound diagnostic**, not recovered source. It must not be used for historical checkpoint parity, training, MT5, or production.

No further formula patch is scientifically justified without new primary evidence.

## Final repair/rebuild verdict

The repair/rebuild is complete in the only defensible form:

- repository lineage is coherent;
- invalid historical causal authority is suspended;
- exact missing-source claims are blocked;
- false edge-only and false every-active-row reconstructions are both recorded as rejected;
- the missing clock topology is constrained to a specialist-specific state machine;
- the failed corrected RIGHT-edge R14 rebuild is preserved;
- the safe active causal base is **BETA063**;
- no historical BETA064 Checkpoint-03 parity claim survives;
- no MQL5 is authorized;
- August remains sealed.

Further historical archaeology should resume **only if a new primary artifact appears**, such as the original helper, a pre-ownership candidate ledger, the missing cache-builder source, or a byte-identical prediction table with source provenance.

## Research continuation point

Research can now move forward rather than continue reverse-engineering the invalid checkpoint.

The next scientific unit should start from **BETA063** and build a **new corrected RIGHT-edge causal Entry architecture**. It may reuse only:
- verified causal state infrastructure;
- exact surviving BETA064 E1/E2/E4 logic when scientifically appropriate;
- specialist taxonomy/horizon concepts as hypotheses;
- R18's state-machine topology lesson;
- original Jan–Jul Dukascopy source;
- existing scientific/risk governance.

It may **not** inherit:
- historical BETA064 Checkpoint-01/02/03 performance claims;
- left-edge timestamps;
- guessed E6/E9/E11 thresholds;
- the uncertified recovery scaffold as a parent generator;
- the old checkpoint identity.

August stays sealed until a genuinely new causal candidate earns the project's holdout gate.
