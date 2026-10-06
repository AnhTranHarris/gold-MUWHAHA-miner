# GRID-001 January Early Thesis Failure 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_EARLY_THESIS_FAILURE_001`  
**Status:** FROZEN BEFORE COMPUTE

## Question

Can adaptive-grid continuation reduce gross loss by demanding early favorable evidence before granting the trade its full hard-stop budget?

## Frozen lattices

- A10
- A15

These are the two higher-quality adaptive lattices from Adaptive Spacing Screen 001.

## Direction

Continuation only.

No MR selector, no shadow-memory selector, no session/news context.

## State machine

At entry:

`UNCONFIRMED`

Unconfirmed trade has:
- final TP = +1.00 event gap;
- provisional adverse failure = -0.50 event gap.

Proof of life:
- if favorable excursion reaches +0.25 event gap before provisional failure, state becomes `CONFIRMED`.

After confirmation:
- TP remains +1.00 gap;
- hard adverse bound becomes -1.00 gap.

If -0.50 gap is reached before +0.25 favorable proof:
- exit immediately;
- reason = EARLY_THESIS_FAILURE.

Horizon remains 5 minutes. Timeout exits at last executable quote.

Fixed 0.01 economics and $0.02 round-trip commission.

## Why this is structural

This is not merely a tighter permanent stop.

Risk is conditional on causal evidence:
- weak/wrong continuation receives only half the loss budget;
- a trade that demonstrates favorable path behavior earns permission to use the original full stop.

No loss-dependent sizing and no averaging are involved.

## Required comparison

Against the original A10/A15 continuation baselines report:
- net;
- gross profit;
- gross loss;
- PF;
- expected payoff;
- win rate;
- early-failure count/share;
- confirmation count/share;
- discovery vs validation.

## Advancement rule

The mechanism advances only if:
- gross-loss magnitude falls materially;
- net/PF improve in both discovery and validation, or at minimum do not reverse sign across them;
- improvement is large enough to justify a small robustness-neighborhood test.

No threshold sweep is authorized in this unit.
