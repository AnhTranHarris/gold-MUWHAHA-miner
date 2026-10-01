# BETA067 — Causal State-Enriched Hurdle / Actionability Study

**Date:** 2026-10-01  
**Parent:** BETA063  
**Inputs:** exact BETA065 proposal surface + exact BETA066 delayed-action labels  
**Status:** PREREGISTERED / NOT YET TESTED  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Rationale

BETA066 rejected the three-clock + 28-feature architecture after both gradient boosting and Extra Trees failed on CAL, even though fixed delayed actions increased CAL hindsight capacity to +$0.326/proposal. The next test therefore changes the **information representation and decision factorization**, not the economic threshold.

## New causal state

Keep the original 28 RIGHT-edge features and append only as-of/prior-history variables: cyclical UTC minute/second phase, weekday, same-specialist trailing spread rank/median ratio, event ages, recent proposal densities, quote-pressure divergence, multi-scale acceleration, range-normalized movement, spread/range ratio, same-specialist state-index delta, and distance to minute boundary. No future state and no hard session confirmation gate.

## Hurdle architecture

Stage 1 predicts `P(any action is positive after cost)`.  
Stage 2 predicts `P(action_j > 0)` separately for the eight BETA066 now/wait actions.  
For each action, FIT-only positive/nonpositive payoff means convert probability to an expected-value proxy:
`q_j = p_j * mean_positive_j + (1-p_j) * mean_nonpositive_j`.

Trade only if both the global actionability hurdle and selected action q clear preregistered thresholds.

## Model families

- HGB_HURDLE
- EXTRA_HURDLE

No AutoML and no diagnostic-driven parameter search.

## CAL grid

Global actionability thresholds: 0.55 / 0.60 / 0.65 / 0.70.  
Action q thresholds: $0.00 / $0.05 / $0.10.  
Minimum 100 completed one-position CAL trades plus positive net, PF >1 and positive average.

If nothing passes, this feature-enriched hurdle branch is rejected. Do not lower the thresholds. Diagnostic is read only after a CAL winner is frozen.

## Durability

BETA GOV-001 applies before any durable/frozen status.
