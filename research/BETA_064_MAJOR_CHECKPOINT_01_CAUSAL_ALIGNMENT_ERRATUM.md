# BETA064 Major Checkpoint 01 — Causal Alignment Erratum

**Date:** 2026-09-30  
**Branch:** `beta`  
**Status:** HISTORICAL CHECKPOINT PRESERVED / CAUSAL CERTIFICATION SUSPENDED  
**EA promotion:** NO  
**MQL5 authorization:** NO  
**August:** SEALED

## What was found

During the Checkpoint-2 SYNTH-vs-Dukascopy dual tick replay, the BETA064 Entry→Hold research harness was audited at the bar/tick interface.

The five-second feature bars were constructed from each interval `[t, t+5s)`, but the resulting bar retained Pandas' default left-edge timestamp `t`.

The Entry simulation then treated that left-edge timestamp as the decision/entry timestamp.

Therefore a candidate stamped at `t` could contain information from ticks occurring after `t` and before `t+5s`.

This is an intra-bar look-ahead / timestamp alignment defect.

## Correct causal convention

A completed five-second bar covering:

`[t, t+5s)`

is first usable at:

`t+5s`

All Entry candidate timestamps must therefore be shifted to the bar-completion time before:

- applying specialist conditions,
- producing Entry proposals,
- starting the first-passage replay,
- measuring Entry→Hold survivability.

The diagnostic harness now applies this convention.

## Effect on Major Checkpoint 01

The historical Checkpoint-01 artifacts and commits remain frozen and are not deleted or rewritten.

However, the previously reported:

- 2,097 Jan-Jul one-position trades;
- 90.56% weighted Entry→Hold survivability;
- every-month >85% survivability;

must **not** be used as causal certification.

When the exact same architecture/model family and historical `p_survive >= 0.88`, `entry_score >= 0.30` gates are replayed with corrected five-second decision timestamps, the probability scale collapses and those gates select zero trades.

A January FIT/CAL repair using the same specialist universe and model family also failed to find a meaningful sample of >=20 one-position CAL trades with >=85% survivability.

Interpretation:

the previous Checkpoint-01 survivability result depended materially on the timestamp defect rather than merely requiring threshold rescaling.

## Project rule going forward

Major Checkpoint 01 remains a durable historical artifact showing the architecture we intended.

Its **causal performance claims are suspended**.

Checkpoint-2 diagnostics and all subsequent BETA research must use:

- right-edge / completion-time bar timestamps;
- exact raw-tick first-passage ordering;
- BUY at observed Ask, SELL at observed Bid;
- exit/markout on opposite executable quote;
- no future bar information;
- August sealed.

No Hold+Exit optimization begins until a new causal Entry→Hold checkpoint is established.

