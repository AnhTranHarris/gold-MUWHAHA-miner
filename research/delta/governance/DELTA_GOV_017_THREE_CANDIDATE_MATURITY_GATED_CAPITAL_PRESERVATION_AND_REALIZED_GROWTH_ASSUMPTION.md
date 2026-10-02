# DELTA GOV-017 — Three-Candidate Maturity-Gated Capital Preservation and Realized Growth Assumption

**Effective:** 2026-10-02  
**Branch:** `delta`  
**Status:** MANDATORY / HUMAN-REVISABLE ASSUMPTION  
**Layer:** CAPITAL POLICY / SYSTEM MATURITY ARCHITECTURE  
**Research metrics:** NOT DEFINED BY THIS CONTRACT  
**Capital-policy research:** NOT AUTHORIZED BY THIS CONTRACT

## 1. Purpose

DELTA assumes that capital preservation and realized account growth should exist from the beginning as **soft contextual concerns**, but should not dominate early edge discovery.

Once the system has matured enough that **three distinct primary candidates are sufficiently locked**, DELTA may transition into a later phase where capital preservation and realized account growth become **aggressive system-level optimization priorities**.

This is an architecture assumption only. It does not define a position-sizing formula, lot ladder, withdrawal schedule, risk percentage, compounding rule, candidate metric, or research target.

## 2. Two maturity phases

### Phase A — PRE-THREE-CANDIDATE MATURITY

Before three primary candidates are sufficiently locked:

- capital preservation is considered softly;
- realized account growth is considered softly;
- research remains centered on discovering and stabilizing edge;
- capital policy must not suppress viable candidate discovery merely to manufacture a smoother equity curve;
- fixed-lot and existing maintenance rules remain authoritative;
- no aggressive capital-allocation behavior is implied.

Capital awareness exists, but it is not yet the dominant optimization layer.

### Phase B — THREE-CANDIDATE MATURITY REACHED

After three distinct primary candidates are sufficiently locked:

- capital preservation becomes an active system-level objective;
- realized account growth becomes an active system-level objective;
- the system may later pursue both objectives much more aggressively;
- candidate interaction, capital deployment, realized-PnL retention, risk budgeting, and account-growth policy may become explicit research subjects;
- the system should seek to protect accumulated capital while efficiently converting validated edge into realized account growth.

This transition does not itself authorize any specific implementation.

## 3. Meaning of "sufficiently locked"

A primary candidate is **sufficiently locked** only when its relevant logic is materially stable and frozen enough that subsequent capital-policy research is not optimizing against a moving target.

At minimum, a sufficiently locked candidate should eventually have:

- a stable candidate identity and version;
- frozen causal logic for its scoped role;
- reproducible configuration;
- durable results;
- required governance review completed for its stage;
- known interaction boundaries with other system components;
- no unresolved behavior-changing ambiguity that would invalidate downstream capital-policy conclusions.

The exact quantitative lock criteria remain governed by existing and future DELTA contracts.

## 4. Three candidates means three primary candidates

The maturity gate requires **three distinct primary candidates**, not three parameter variants of the same candidate.

A minor threshold variation, cosmetic version bump, or duplicated specialist configuration does not count as a separate primary candidate.

The eventual three candidates may represent different system roles, specialists, regimes, or other materially distinct edge components.

## 5. Candidate locks are not automatically metric locks

The three-primary-candidate maturity gate is conceptually separate from the existing DELTA primary-metric lock mechanism.

Therefore:

- three locked candidates do not automatically mean three primary metrics are locked;
- three primary-metric locks do not automatically mean three primary candidates are locked;
- neither mechanism replaces the other;
- they may be related later only if the owner explicitly authorizes a unification.

## 6. Meaning of realized account growth

For this assumption, **realized account growth** means growth that has been converted into closed/realized trading PnL and reflected in the account balance, rather than merely existing as:

- unrealized floating profit;
- theoretical maximum favorable excursion;
- unexecuted opportunity;
- hindsight profit potential.

This contract does not define withdrawals, distributions, tax policy, external capital transfers, or owner compensation.

Those remain separate future decisions.

## 7. Aggressive does not mean reckless

After the three-candidate maturity gate, "aggressive" means the capital layer may actively optimize how validated edge is converted into preserved and realized account growth.

It does **not** mean:

- martingale;
- grid recovery;
- uncontrolled leverage;
- doubling after losses;
- ignoring survivability;
- abandoning drawdown controls;
- sacrificing a locked edge for short-term balance spikes;
- increasing lot size without a validated capital-allocation rule.

Existing prohibitions and survivability rules remain active.

## 8. Preservation and growth are joint objectives

The mature capital layer should eventually reason about both sides simultaneously:

- how much accumulated capital must be defended;
- how much validated edge can be deployed;
- how realized gains can support future growth;
- how losses affect future deployable capital;
- when growth pressure should be reduced to preserve the account;
- when accumulated survivability evidence supports greater capital deployment.

Capital preservation is therefore not equivalent to minimizing all risk, and account growth is not equivalent to maximizing leverage.

The future objective is **efficient realized growth under explicit capital-survival constraints**.

## 9. Relationship to trade survivability and exit maturity

GOV-015 and GOV-016 remain upstream.

The dependency is:

`MARKET CONTEXT -> TRADE SURVIVABILITY -> TRADE MATURITY -> PROFIT REALIZATION -> CAPITAL PRESERVATION / ACCOUNT GROWTH OPTIMIZATION`

A capital-growth policy must not force trade-level behavior that violates validated survivability or exit logic.

## 10. Relationship to existing maintenance rules

GOV-011 remains active.

This assumption does not modify:

- the current fixed 0.01 research lot;
- existing maintenance risk warnings/stops;
- no-martingale / no-grid rules;
- current starting-capital staging;
- future owner-controlled lot-ladder authorization.

Capital-policy maturation must coexist with, and later explicitly reconcile against, GOV-011.

## 11. No automatic lot escalation

Reaching three sufficiently locked primary candidates does not automatically increase position size.

It only unlocks the architectural stage in which aggressive capital-preservation and realized-growth policy may be researched and designed.

Any future sizing change must be separately specified, tested, causally validated, and owner-authorized.

## 12. Future capital-policy research may include

Subject to later owner authorization, mature capital research may investigate:

- capital allocation across specialists;
- realized-profit retention;
- compounding policy;
- dynamic but bounded risk budgets;
- candidate contribution weighting;
- drawdown-responsive deployment;
- capital floors and ratchets;
- profit-locking at the account level;
- growth acceleration after validated stability;
- de-risking during structural degradation;
- account-state-dependent specialist routing.

This list is illustrative only and does not approve any mechanism.

## 13. No metric or threshold authorization

This contract does not define:

- required account growth rate;
- drawdown target;
- compounding frequency;
- reinvestment percentage;
- withdrawal percentage;
- capital floor;
- lot-size ladder;
- leverage target;
- risk-per-trade percentage;
- minimum realized profit;
- candidate score;
- optimization grid.

Those belong to future research.

## 14. Current DELTA phase remains unchanged

Current DELTA remains:

`POST-DELTA_004 / PRE-CANDIDATE / ENTRY + INITIAL-HOLD`

No capital-policy candidate research begins from this assumption.

No active candidate is created.

No exit or high-profit research is reopened.

## 15. Future MT5 reconstruction

If mature capital-policy logic is eventually approved for MT5 implementation, the final handoff must explicitly document:

- three-candidate maturity-gate state;
- candidate identities and versions;
- capital-state variables;
- realized-balance semantics;
- equity semantics;
- preservation constraints;
- allocation/sizing rules;
- growth rules;
- precedence relative to survivability and specialist routing;
- exact update order;
- exact formulas and parameters;
- parity fixtures.

MQL5 coding remains owner-authorized only under existing governance.

## 16. August

August 2026 remains sealed.

This contract does not authorize August access.
