# BETA064 missing multidesk helper recovery — R12 source-forensic findings

**Date:** 2026-10-01  
**Status:** ACTIVE RECOVERY / RECOVERY_UNCERTIFIED  
**Lineage:** BETA only  
**Alpha/GAMMA:** prohibited and not inspected  
**August:** sealed  
**MQL5:** prohibited during recovery

## What this unit adds

This unit resumes the authoritative Google Drive crash/retry recovery log at R11 and records source forensics that prevent several false reconstruction paths.

### 1. Existing recovery continuity confirmed

Authoritative Google Doc:
**BETA064 beta064_multidesk_loop.py Recovery Log — Crash/Retry Continuity**
Drive ID: `1VJaUMULaTonJxTRCiWKsof_bHSsjg1ouSfLVCKDepi8`.

A second duplicate recovery document is explicitly superseded. Do not create or follow a parallel recovery lineage.

### 2. Missing helper still not found as a loose source file

BETA_RESEARCH Drive metadata/direct-name searches again found no loose:
- `beta064_multidesk_loop.py`;
- `beta064_allmonths_predictions.pkl`;
- `beta064_session_meta_all.pkl`;
- historical cache-builder source.

The V2 freeze archive still contains `beta064_multidesk_v2.py` but not its imported helper.

This supports the prior conclusion that the original helper was a transient `/mnt/data` research source.

### 3. Git commit timeline does not contain the helper

The BETA commit sequence around the R1B/R1B2 build was audited:
- R1B1 H4 harness;
- multiscale timing ablations;
- R1B2 specialist registry;
- R1B2 survivability record;
- Checkpoint-01 freeze;
- causal alignment erratum;
- later session-gapfill work.

Those commits add durable reports/registries/harnesses but do not add `beta064_multidesk_loop.py`.

### 4. Google Docs revision history exists and is useful

The BETA Research Journal retains 22 revisions spanning the construction period.
Initial historical revision mining did not reveal the helper in older BETA008/009-era revisions.
A broad revision sweep hit Google read-rate limits and was stopped rather than repeatedly retrying.

Sep-30-era revisions remain a useful low-frequency forensic source and should be queried selectively.

### 5. Predecessor persistence/debounce evidence

BETA009 predecessor code directly preserves state-machine persistence examples:
- threshold state can persist across distinct tick events;
- an example persistence gate requires both tick-count and elapsed-time conditions;
- sweep/pullback states have bounded expiries;
- rearm logic resets state on specific ownership transitions.

These older thresholds are **not** imported into BETA064. They only demonstrate that persistent-state / expiry / debounce emitters existed in the BETA engineering lineage and are consistent with R11's rejection of one universal FALSE→TRUE edge rule.

### 6. BETA026/BETA039 quote-pressure lineage clue

The Master Protocol / BETA Research Journal preserves this exact historical fact:

> BETA026 `quote_pressure1` was already signed relative to the original proposed BUY/SELL side.

BETA039 later corrected a double-signing error and explicitly prohibited multiplying this already-signed value by side again.

This does **not** prove that BETA064 one-second cache `quote_pressure` is identical to BETA026 `quote_pressure1`, but it narrows the predecessor lineage and must be tested before inventing a new formula.

### 7. C02E does not recover historical qp/qv

The C02E micro-derivative reproduction code builds completed one-second:
- velocity;
- acceleration;
- jerk;
- spread changes;
- tick intensity

directly from raw Bid/Ask.

It does not use or reconstruct BETA064 historical `quote_pressure` / `qv_imb`.
Therefore C02E cannot by itself identify those two lost cache formulas.

### 8. Corrected causal model is the wrong target for historical C02C probability inversion

The V2 bundle contains `beta064_causal_router_janfit.joblib`, created after the causal timestamp erratum.
The historical session-router pipeline consumes `beta064_allmonths_predictions.pkl`.

A trial using reconstructed historical-left-edge state and the corrected causal model produced very large probability mismatches versus preserved C02C `p_surv/p_win`.
That mismatch is expected from the different probability lineage and must **not** be interpreted as evidence against a candidate qp/qv formula.

Rule:
**Do not solve historical qp/qv by forcing the post-erratum causal model to reproduce historical C02C probabilities.**

### 9. Final selected-trade cadence cannot identify candidate debounce

The C02C selected ledger was audited by specialist.
Its timestamp gaps are censored by:
- base-first ownership;
- specialist horizons;
- one-position scheduling;
- session-child idle-slot rules.

Examples:
- E6 minimum selected gap = 180s, equal its horizon;
- E11 minimum selected gap = 45s, equal its horizon;
- E10 minimum selected gap = 120s, equal its horizon.

This is evidence of ownership censoring, not proof of candidate cooldown.

Durable CSV:
`research/recovery/BETA_064_MULTIDESK_LOOP_R12_SELECTED_CADENCE_DIAGNOSTIC.csv`

Therefore exact emission/debounce must be inferred from a pre-ownership candidate/prediction surface or from source/history, not from final selected-trade gaps.

## Current recovery state

Still HIGH confidence:
- raw Jan-Jul Dukascopy source;
- exact right-edge causal 5s feature engine;
- exact active V2 E1/E2/E4 rules;
- Entry feature order/model parameters;
- exact frozen learned artifacts;
- session router logic;
- Hold model;
- selected ledgers and observed downstream metrics.

Still unresolved:
- historical E3/E5-E12 exact candidate emission/debounce;
- historical raw-score identity where not directly preserved;
- exact BETA064 one-second `quote_pressure`;
- exact BETA064 one-second `qv_imb`;
- provenance/body of `beta064_allmonths_predictions.pkl`;
- a causal right-edge replacement checkpoint.

## Next exact action

1. Search only BETA predecessor source/history for `quote_pressure1`, quote-volume imbalance, and candidate-state persistence.
2. Selectively mine Sep-30 Google-Doc revisions after connector cooldown.
3. Locate any pre-ownership prediction/candidate ledger; do not substitute selected-trade cadence.
4. Use selected-timestamp mechanism-mask recall as constraints, prioritizing E6/E11.
5. Once historical formulas are sufficiently constrained, reproduce historical helper for **forensics only**.
6. Then build a corrected RIGHT-edge causal parent generator and train/validate a **new replacement checkpoint**.
7. Official MT5 Entry parity remains blocked until that replacement source closes.

