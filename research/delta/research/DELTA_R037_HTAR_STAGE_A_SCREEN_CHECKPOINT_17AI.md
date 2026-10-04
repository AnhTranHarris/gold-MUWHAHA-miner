# DELTA R037 — Higher-Timeframe Anchored Reversal Stage-A Screen — Checkpoint 17AI

**Status:** COMPLETE — STAGE-A STRONG SURVIVOR FOUND  
**Unit:** R037_HIGHER_TIMEFRAME_ANCHORED_REVERSAL_STAGE_A_SCREEN  
**Parent:** R037_SCFR_STAGE_A_SCREEN_CHECKPOINT_17AH  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Bounded question

Does replacing the noisy S5-local liquidity pool with a causally confirmed H1/H4 structural swing anchor materially improve the same sweep → CISD → FVG → retrace sequence without threshold fitting?

## Integrity

Preregistration commit: `65ac522bd99ed1477b83746c5afc2d26299515df`

Producer: `research/delta/experiments/delta_r037_htar_stage_a_17ai.py`  
Producer commit: `2e2f04dbc3b58f68853197f731b5955b6d5de2c8`  
Producer blob: `280c3b1d852dc4fdb55c322391cf3091575c67fa`  
Producer SHA-256: `3dc5331e0f4704002d2a482e01fc8acefc2996e280b62b9c6e22aa8029a9098c`

The execution sandbox initially received corrupted transferred bytes. The Git-blob guard rejected them before compute. The file was repaired from authoritative line-level content until local Git blob exactly matched `280c3b1d...`; only then was official compute allowed.

Official result SHA-256: `15406d51f62a7140f2dd36193bd7dbcc7fbf7a98030ba1e6924d96af1b5f59fb`.

## Stage-A results

### C01 — H1 anchor

Funnel:
- 55 confirmed anchor highs / 65 lows
- 60 sweeps
- 57 CISD shifts
- 25 FVGs
- **8 causal retrace executions**

Economics:
- **8 trades across 5 distinct days**
- **4 official wins**
- gross profit **+$1.15**
- gross loss **-$0.21**
- direct net **+$0.94**
- 7 STOP exits / 1 MAX_HOLD exit

All preregistered gates pass, including the strong nonnegative-net gate.

### C02 — H4 anchor

- 18 sweeps → 18 CISD → 7 FVG → 3 retraces
- 3 trades across 3 days
- 0 wins
- **-$1.19**

H4 fails both supply and economics.

## Interpretation

This is the first fresh source in the current harvest chain to clear the preregistered Stage-A gate.

The evidence is **not** “higher timeframe is better.” It is narrower:
**causally confirmed H1 swing liquidity + S5 displacement/FVG/retrace** produced a small but positive Stage-A sample, whereas the H4 formulation starved and lost.

The sample is only eight trades. It is a valid breakthrough candidate for independent validation, not a promotion.

## Decision

Freeze **C01_H1_ANCHOR** unchanged and advance it to the independent later-January holdout.

Do not:
- retune H1 swing width;
- alter CISD/FVG/retrace windows;
- rescue H4;
- add session/side filters;
- tune exits;
- inspect August;
- begin MQL5.

## Next bounded unit

`R037_HTAR_LEADER_INDEPENDENT_LATER_JAN_VALIDATION`

Use the same independent holdout protocol as other Stage-A survivors: context/warm-up begins 2026-01-14 00:00 UTC; economics begin 2026-01-18 12:00 UTC and run through January end.
