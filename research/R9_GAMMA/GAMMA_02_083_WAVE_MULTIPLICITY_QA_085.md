# GAMMA-02 — 083 Wave Multiplicity QA 085

**Status:** COMPLETE REJECTION / OWNERSHIP SEMANTICS CONFIRMED  
**Parent:** GAMMA_02_083_HEAT_PARENT_OWNERSHIP_QA_084.md  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Hypothesis

Collapse all children that enter on the same market tick into one desk-level renewal signal, then apply a fixed explicit ticket multiplicity. This would separate signal timing from exposure scaling and could, in principle, reduce synchronized heat.

## QA result

The same-tick clusters are homogeneous in:
- direction;
- executable child entry price.

But they are **not** homogeneous in:
- parent-owned exit timestamp;
- final P/L.

Early desk:
- 768 unique renewal-entry ticks
- maximum original cluster: 678
- representative-signal expectancy: +$0.9122/trade
- representative average hold: 7.34s

Late desk:
- 855 unique renewal-entry ticks
- maximum original cluster: 765
- representative-signal expectancy: +$1.6795/trade
- representative average hold: 61.39s

A bounded grid of 538 early/late fixed multiplicity combinations targeting roughly 24K-36K tickets produced:

**0 variants that crossed all six exact January R9 SYNTH metrics.**

## Scientific disposition

REJECT desk-level signal collapse + fixed wave multiplicity.

The synchronized child entries are not fully fungible because each child remains owned by a distinct structural parent with a different remaining campaign horizon. Parent ownership must be preserved.

This strengthens, rather than weakens, 083's interpretation:
- 083 is a parent-owned pyramiding/renewal architecture;
- its same-tick multiplicity is explicit scaling;
- reducing heat must preserve parent-specific causal state rather than erase it.

## Next unit

`GAMMA_02_083_PARENT_PHASE_DESYNC_086`

Use only causal metadata known at parent entry to de-synchronize future renewals while preserving parent ownership. Candidate mechanisms:
- deterministic renewal phase derived from parent entry price / displacement;
- stable cohort-specific post-harvest rearm offsets;
- no future parent exit time, future P/L, or hindsight ranking.

Goal:
retain all six January R9 SYNTH crossover metrics while materially reducing:
- same-tick child cluster fraction;
- maximum same-tick child cluster;
- full-tick equity DD;
- maximum open positions.

## Exact artifacts

- helper SHA-256: `c7270ecf5a2ac28d92b12521b7b60688b5c3da914515cbef4f3a9c76932b1625`
- result SHA-256: `94993bcebc0b16c86a2b4034c8309f2ac7a90e3ee64802769858622f4ad83204`
- Library mirror: `/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/post-crossover-recovery/`

Do not rerun <=085 after timeout.
