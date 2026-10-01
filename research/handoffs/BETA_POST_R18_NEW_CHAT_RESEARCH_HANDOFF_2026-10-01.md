# BETA Research New-Chat Handoff — Post-R18 Safe Restart from BETA063

**Date:** 2026-10-01  
**Branch:** `beta`  
**Purpose:** authoritative restart packet for the next research chat after the BETA064 missing-helper repair/rebuild  
**Scientific status:** recovery closed safely; research may resume from BETA063 under corrected causal/right-edge rules  
**August 2026:** SEALED  
**Alpha/GAMMA:** prohibited  
**MQL5:** not authorized until a future causal candidate passes the research/owner gates  
**Durability policy:** BETA GOV-001 is mandatory

---

## 1. Bootstrap order for the new chat

Before proposing, coding, or testing any new strategy, read these in this order:

1. **Live state first**
   - `beta/CURRENT_STATE.json`
   - This is the authoritative live cursor and overrides stale chat summaries.

2. **Permanent rebuild-artifact governance**
   - `research/governance/BETA_GOV_001_MT5_REBUILD_ARTIFACT_RETENTION_POLICY.md`
   - `research/artifacts/BETA_RESEARCH_UNIT_REBUILD_MANIFEST_TEMPLATE.json`
   - `research/qa/BETA_GOV_001_REBUILD_MANIFEST_GATE.py`

3. **BETA064 recovery closure**
   - `research/recovery/BETA_064_MULTIDESK_LOOP_R18_STATE_MACHINE_TOPOLOGY_FINAL.md`
   - `research/recovery/BETA_064_MULTIDESK_LOOP_R18_STATE.json`
   - Google recovery log:
     `https://docs.google.com/document/d/1VJaUMULaTonJxTRCiWKsof_bHSsjg1ouSfLVCKDepi8/edit`

4. **Safe empirical parent**
   - `research/BETA_063_FIVE_SOFT_EXPERT_ENTRY_HOLD_SHARED_CONTINUATION_VALUE_SPEC.md`

5. **Post-BETA063 redesign hypothesis**
   - `research/BETA_063A_ENTRY_HOLD_UNIFIED_CONTINUATION_ADVANTAGE_BLUEPRINT.md`
   - DESIGN/HYPOTHESIS ONLY; do not mislabel it as a backtested result.

6. **BETA064 architecture concepts, hypothesis only**
   - `research/BETA_064_HIERARCHICAL_ENTRY_HOLD_MOE_ARCHITECTURE_AND_HANDOFF.md`
   - Use architecture concepts only. Historical BETA064 Checkpoints 01/02/03 are not causal parents.

7. **Long-form research journal**
   - `https://docs.google.com/document/d/1_zuLcHwsPnul8XtfLLlrK9-Mogk120qk0xWdlVWAzPQ/edit`

Do not restart BETA040–063 research as if it never happened. Do not reopen BETA064 helper archaeology unless a genuinely new primary artifact appears.

---

## 2. Authoritative current scientific state

### Safe active causal base: BETA063

BETA063 is the last causally audited empirical Entry/Hold research base that survives the BETA064 repair.

It implements five soft expert families:

- TREND / accepted continuation
- SWEEP / reclaim
- COMPRESSION / expansion
- ROTATION / range
- PREENTRY_LEADUP

with shared continuation-value logic and observed-quote execution semantics.

Frozen Jan–Jul BETA063 result versus the corrected BETA039 rolling-P89 incumbent:

| Metric | BETA039 P89 incumbent | BETA063 five-expert |
|---|---:|---:|
| Net | -$118,080.34 | -$116,008.01 |
| Trades | 166,394 | 162,899 |
| Winning closes | 39,708 | 38,774 |
| Profit factor | 0.2506 | 0.2353 |

Incremental BETA063 improvement versus the correct incumbent:
- **+$2,072.33**
- **1.755% smaller negative net loss**

BETA063 remained after-cost negative, April and June regressed, profit factor was lower than the incumbent, and there were no profitable calendar months. Therefore BETA063 is a **research base**, not a profitable strategy and not an MT5 candidate.

BETA063 bounded QA: **62/62 PASS** for its declared source/order/execution checks.

Important limitation:
BETA005 full materialized 17-layer feature/cache parity remains incomplete. Do not call the full feature stack universally MT5-certified merely because BETA063 bounded QA passed.

---

## 3. What BETA064 was trying to solve

BETA063 exposed the main scientific problem:

> The system still lacked a strong independent after-friction directional/continuation edge. Much of the apparent improvement was inherited from the BETA039 P89 cost gate rather than a new profitable Entry mechanism.

BETA064 was designed to be structurally different by removing E060 as the mandatory master opportunity clock and moving toward:

- independent causal Entry clocks;
- hierarchical macro/meso/micro state;
- state-conditioned specialist ownership;
- direct LONG / SHORT / WAIT comparison;
- expert regret / conditional utility routing;
- multiple causal continuation ages rather than one +5s refresh;
- more independent Entry mechanisms instead of several similar Ridge heads;
- separation of Entry, Hold and later Hold→Exit.

That direction remains scientifically relevant **as a hypothesis**, but the historical BETA064 checkpoint results do not.

---

## 4. Why historical BETA064 cannot be resumed as the parent

The BETA064 recovery campaign R0–R18 established:

1. The historical five-second feature path used left-edge timestamps for bars covering `[t,t+5s)`, allowing intra-bar future information to appear at `t`.
2. Historical Checkpoints 01/02/03 therefore have suspended causal certification.
3. The transient upstream helper `beta064_multidesk_loop.py` was not durably preserved.
4. Final selected ledgers were insufficient to reconstruct the exact pre-ownership candidate stream.
5. Universal broad-mask FALSE→TRUE edge emission was falsified.
6. Emitting every active broad-mask row was also falsified.
7. The later September-30 all-12 child formulas were tested and rejected as the historical parent source.
8. R18 strongly constrained the missing topology to a specialist-specific in-state finite-state event clock, but exact historical thresholds/raw scores remain unknown.
9. A corrected RIGHT-edge R14 rebuild was actually executed and failed the required research quality:
   - January CAL survivability about **11.57%**
   - best minimum-20-trade CAL threshold about **57.14%**
   - historical 0.88/0.30 gates selected **zero** Jan–Jul trades under the corrected rebuild
10. Therefore the correct action was safe rollback to BETA063, not continued reconstruction of an invalid checkpoint.

Historical BETA064 Checkpoints 01/02/03 are **FORENSIC ONLY**.

Do not:
- inherit their reported economics;
- use their left-edge timestamps;
- claim their missing candidate helper has been recovered;
- use `beta064_multidesk_loop_RECOVERY_UNCERTIFIED.py` as a training or MT5 parent;
- resume archaeology without a new primary artifact.

---

## 5. R18 lesson that *does* carry forward

R18 found strong independent BETA evidence for this event-generator topology:

```text
broad causal market state
    -> specialist-specific transient/secondary state
    -> persistence / retest / renewal transition
    -> bounded elapsed-time and/or tick-count requirement
    -> debounce / expiry
    -> proposal
    -> reset / rearm
```

This is an architecture lesson, not a recovered formula.

Earlier BETA source preserves examples of:
- persistence across multiple observed ticks;
- tick-count + elapsed-time confirmation;
- bounded setup expiry;
- break→retest→rebreak finite-state logic;
- post-exit cooldown;
- ownership-triggered rearm;
- no retroactive fill at the origin event.

The next causal architecture may use these **state-machine principles**, but must independently specify and validate its own thresholds on corrected observable timing.

---

## 6. Exact research problem to resume

The next chat should resume this problem:

> **Build a new, corrected RIGHT-edge causal Entry architecture from the BETA063 research base that can discover real after-spread expected value on original Dukascopy quotes, without inheriting BETA064 left-edge contamination or guessed helper logic.**

The specific deficiencies to attack are:

1. **Independent opportunity clock**
   - E060 must not remain the mandatory master eligibility clock.
   - New Entry events must arise from causal observable state.

2. **Actual directional/continuation edge**
   - Beat the correct BETA039/BETA063 same-feed controls through new signal information, not mainly inherited friction avoidance.

3. **Specialist heterogeneity**
   - Avoid five mathematically similar models over mostly overlapping features.
   - Specialists should own genuinely different market mechanisms.

4. **State-conditioned event timing**
   - Use explicit reconstructible finite-state sub-clocks where appropriate.
   - No universal edge-only or every-active-row shortcuts.

5. **Unified economic action value**
   - BETA063A proposes comparing LONG / SHORT / WAIT and later HOLD advantage on one executable after-cost scale.
   - This is a design hypothesis to test, not an accepted result.

6. **Causal continuation**
   - Multiple observable ages may be evaluated, but no future quote/bar may enter inference.
   - Offline future path is labels only.

7. **Opportunity vs quality**
   - Do not reach survivability or quality by collapsing trade count to near zero.
   - Measure retained opportunity, winners, gross loss, drawdown, cost sensitivity and month stability.

---

## 7. Recommended first bounded unit in the new chat

Do **not** begin with a giant Jan–Jul optimization.

Start with a newly named post-R18 research unit under BETA GOV-001.

### Step A — create the rebuild manifest first

Before running the experiment:

- create the unit's `BETA_RESEARCH_UNIT_REBUILD_MANIFEST`;
- declare the parent as BETA063;
- declare corrected RIGHT-edge timing;
- list every helper/cache-builder/candidate-generator/model/result artifact that must be preserved;
- set `python_rebuild_ready=false` until all artifacts are durably stored and verified.

### Step B — rebuild the corrected causal state surface

Use original Dukascopy chronology.

Initial research window may retain the existing BETA063 stage-1 walls:

- FIT: Jan 1–Jan 9
- CAL: Jan 9–Jan 11
- later Jan 11–Jan 18 12:00 UTC: historically consulted diagnostic, **not pristine OOS**

All completed bars must be usable only at their RIGHT-edge completion timestamp.

Preserve:
- raw source identity;
- time/tie-break chronology;
- feature schema;
- cache builder;
- LEFT/RIGHT edge semantics;
- quote-pressure/volume feature equations actually used.

### Step C — test independent causal Entry clocks

Candidate clocks may include the BETA064 architectural hypotheses:

- completed 250ms state update;
- material BOCPD/change event;
- confirmed structural-level interaction;
- reconstructed V8 M1 original-boundary interaction;
- specialist-specific finite-state persistence/retest/rearm clocks.

These are hypotheses. They must be independently coded, documented and evaluated.

### Step D — test action value, not stacked confirmation

A sensible first model family is the BETA063A proposal:

- LONG_NOW
- SHORT_NOW
- WAIT_SHORT
- SKIP

with executable after-cost utility and uncertainty.

Avoid a giant confirmation stack. Use market state to route/weight specialists, not to require every indicator to agree.

### Step E — preserve every upstream surface

For every test that materially affects a conclusion, durably preserve or deterministically reconstruct:

- pre-ownership candidate ledger;
- source ordinal/time;
- side;
- specialist;
- state-machine state;
- raw score;
- feature version;
- model probability/utility;
- horizon/checkpoint;
- selected/owned ledger;
- labels;
- exact producing code/config;
- negative/null results.

This is mandatory under BETA GOV-001.

### Step F — research gate

The owner research policy remains:

- strictly **>10%** comparable improvement for formal candidate review;
- **>20% preferred** as the stronger breakthrough target;
- do not promote a loss reduction as profitable alpha;
- require gross-loss, drawdown, winner/trade-retention and month stability safeguards;
- freeze a passing candidate before broader Jan–Jul replay;
- August stays SEALED.

---

## 8. BETA GOV-001 — mandatory anti-loss-of-artifact rule

The BETA064 incident must never recur.

A future unit cannot become `VERIFIED_DURABLE`, frozen, or a research parent unless:

- `python_rebuild_ready=true`;
- `missing_required_artifacts=[]`;
- source/helpers/config are committed;
- required large/binary artifacts are in Drive;
- hashes and provenance are recorded;
- pre-ownership proposal and prediction surfaces are preserved or exactly regenerable;
- state-machine semantics are executable source, not prose only;
- reconstruction entry point and timing semantics are documented;
- GitHub/Drive readback is verified.

Before any owner-authorized MT5 build review:
- `mt5_translation_ready=true`;
- exact Python parent and helpers exist;
- feature/timing/state-machine/model/execution/ownership/session/risk contracts exist;
- parity fixtures exist.

The CI enforcement is already active on `beta`.

---

## 9. Hard prohibitions for the next chat

- Do not use Alpha or Gamma.
- Do not open August.
- Do not treat historical BETA064 Checkpoints 01/02/03 as causal.
- Do not use historical LEFT-edge timing for a production candidate.
- Do not promote the R18 forensic scaffold.
- Do not guess missing historical BETA064 formulas.
- Do not resume the old helper recovery absent new primary evidence.
- Do not write official MQL5 without explicit owner authorization.
- Do not advance CURRENT_STATE beyond a research unit whose rebuild manifest has not passed BETA GOV-001.
- Do not describe Jan–Jul as pristine OOS; those months have been inspected historically.

---

## 10. New-chat bootstrap prompt

The owner can start the next chat with:

> Carson, resume Gold MUWHAHA Miner independent BETA research from the Post-R18 Safe Restart handoff. Read this handoff first, then live `beta/CURRENT_STATE.json`, BETA GOV-001, the R18 recovery closure, BETA063, BETA063A and the BETA064 architecture handoff in the exact bootstrap order. Do not reopen historical BETA064 helper archaeology. Historical BETA064 Checkpoints 01/02/03 are forensic only. Safe empirical parent is BETA063. Start a newly named corrected RIGHT-edge causal Entry research unit, create its rebuild manifest before testing, preserve every helper/candidate/prediction/model artifact needed for later MT5 translation, keep August sealed, and do not write MQL5 without my explicit approval.

---

## 11. One-sentence restart cursor

**Resume from BETA063, not historical BETA064: build and test a newly named, fully reconstructible RIGHT-edge causal Entry architecture that seeks independent after-friction edge while preserving BETA GOV-001 durability for eventual MT5 translation.**
