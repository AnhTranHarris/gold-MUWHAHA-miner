# DELTA 005K-001 — Protection-Benefit Paired Counterfactual Forensic Differential

**Status:** PREREGISTERED
**Mode:** historical forensic discovery only
**Candidate promotion:** prohibited in this unit
**Focus:** ENTRY + INITIAL-HOLD
**Mature Holding-Trade + Exit + High-Profit:** deferred / out of scope
**Stage-A:** [2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)
**Surface:** DUKAS_COINEXX_LIKE_P75
**August:** SEALED

## Why this unit exists

DELTA_005H established that looser early trail activation materially improves first-seconds survival.
DELTA_005J showed that the current accepted-consolidation state reduces collateral damage when used for conditional loose protection, but the best net improvement remains only 0.67%.

The next question is not another threshold search.

It is:

**Which causal states, on the same original entry and same future tick path, specifically benefit from looser initial protection relative to baseline R9 protection?**

## Paired treatment design

Use the original R9-style Stage-A entry stream.

For every original entry, independently replay the same subsequent quote path under:

### Control
- hard stop $0.30
- trail activation +$0.10
- trail distance $0.03
- max hold 30 seconds

### Treatment
- hard stop $0.30
- trail activation +$0.30
- trail distance $0.03
- max hold 30 seconds

Entry price, side, entry timestamp, boundary, quote path and commissions are identical between the pair.

This is a forensic paired replay. Treatment outcomes do not alter the parent entry stream or generate additional entries/rearms.

## Causal feature snapshots

For each original entry, record only right-edge market/path state available at:

- entry / 0 ms
- 250 ms
- 500 ms
- 1000 ms
- 2000 ms
- 3000 ms

Features include where supported:
- side-adjusted boundary acceptance;
- current and historical boundary-loss state;
- 250ms / 1000ms aligned tick flow;
- completed-S1 efficiency and change from entry;
- completed-S1 range and turns;
- side-adjusted S1 displacement;
- causal MFE and MAE through snapshot;
- path efficiency;
- aligned tick fraction;
- tick count/intensity;
- session;
- modeled spread.

No treatment outcome may enter a feature.

## Paired retrospective labels

For each entry, derive:

- `TREATMENT_SURVIVES_5_CONTROL_DOES_NOT`
- `TREATMENT_SURVIVES_10_CONTROL_DOES_NOT`
- `TREATMENT_SURVIVES_15_CONTROL_DOES_NOT`
- `CONTROL_SURVIVES_5_TREATMENT_DOES_NOT`
- `CONTROL_SURVIVES_10_TREATMENT_DOES_NOT`
- treatment minus control final P/L;
- treatment minus control hold duration;
- control final winner;
- treatment final winner;
- winner-to-loser conversion;
- loser-to-winner conversion.

These are labels only.

## Anti-leak rule

A feature measured at horizon H may use only ticks/state with timestamp <= entry + H.

Future control/treatment outcomes are labels and may never be candidate inputs.

If a future candidate uses a horizon that baseline protection can exit before, that candidate must separately preregister the required observation grace. This forensic unit does not silently assume such grace.

## 2D matrix harvesting

At minimum generate support-aware paired-benefit matrices for:

1. S1 range × boundary acceptance;
2. S1 efficiency change × boundary acceptance;
3. flow250 × flow1000;
4. MFE × MAE;
5. path efficiency × MAE;
6. aligned tick fraction × boundary acceptance;
7. S1 turns × flow250;
8. session × S1 range state.

For every matrix report:
- support;
- probability treatment uniquely survives 5s/10s;
- mean P/L delta;
- loser→winner conversion rate;
- winner→loser conversion rate;
- net conversion balance;
- stability across neighboring bins/horizons.

## Fixed treatment rationale

The +$0.30 treatment is frozen before compute because DELTA_005H showed a broad, monotonic persistence gain around this region.

005K does not optimize treatment intensity.

## Decision

005K cannot promote a rule.

It must identify broad causal state regions where looser protection has a favorable paired treatment effect. Any deterministic state-conditioned protection candidate derived from the census must be separately preregistered as a new version/unit.

Holding-Trade + Exit + High-Profit remains deferred.

August remains sealed.
