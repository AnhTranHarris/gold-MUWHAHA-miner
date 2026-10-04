# DELTA R037 — Asian Session Range Breakout Stage-A — Checkpoint 17AL

**Status:** COMPLETE — STAGE-A STRONG SURVIVOR FOUND  
**Family:** R037-ASRB-v1  
**Parent:** R037_HTAR_H1_FEB_JUL_ROBUSTNESS_CHECKPOINT_17AK  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Hypothesis

Replace structural-swing liquidity with a fixed daily session range. Freeze the 00:00–06:00 UTC Asian range, then during 07:00–10:00 UTC require a completed S5 breakout plus either:

- C01_PERSIST — one more completed S5 close outside the range; or
- C02_RETEST — a causal touch/retest of the broken boundary followed by a directional close back outside within six S5 bars.

Both use the frozen P75 30-second execution lifecycle. No parameter fitting.

## Integrity

Preregistration commit: `21d85a854b0c6b6123ef05f980ea97d978fe88da`  
Producer commit: `529a62390d66bd22f373bc8a18270f7da4b991fa`  
Producer blob: `9f4d909f929e59a597585b9611440e88c215a781`  
Official result SHA-256: `3c143c5212566771fb0d2fd16cf08061cb128648348342d0bcc1b5ad702abcff`

The executable copy was Git-blob verified exactly before compute.

## Stage-A result

### C01_PERSIST
- 5 trades / 5 days
- 1 official win
- **-$2.37**
- economics gate FAIL

### C02_RETEST
- **4 trades / 4 days**
- **4 official wins**
- gross profit **+$0.97**
- gross loss **-$0.04**
- direct net **+$0.93**
- all Stage-A gates PASS

## Interpretation

A simple persistent breakout is not enough. The public/reconstructible sequence that survives this first screen is narrower: **break a fixed Asian-session range, then causally retest/reject the broken boundary before entry**.

This is a small sample and is not a promoted edge. It is a valid independent candidate for holdout validation.

## Decision

Freeze **C02_RETEST** unchanged and advance to an independent later-January holdout.

Do not retune the session window, retest horizon, range width, side/day filters, stops, trail, hold time, or inspect August.

Next: `R037_ASRB_LEADER_INDEPENDENT_LATER_JAN_VALIDATION`.
