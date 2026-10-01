# BETA064 multidesk_loop recovery — R13 max-chat handoff

**Date:** 2026-10-01  
**Status:** ACTIVE RECOVERY / RECOVERY_UNCERTIFIED  
**Lineage:** BETA ONLY  
**Alpha/GAMMA/Gamma2/Gamma Dynamic:** PROHIBITED — not inspected, imported, inferred from, or used  
**August 2026:** SEALED  
**MQL5:** NO EA CREATION OR MODIFICATION DURING RECOVERY

## Mission

Recover or reconstruct the missing historical helper `beta064_multidesk_loop.py` from BETA-only durable evidence, preserve the historical observed checkpoint for forensics, and then build a corrected RIGHT-edge causal replacement Entry system before any official MT5 Entry-parity claim.

This is a continuity artifact for retry/new-chat recovery. Do not restart prior recovery work unless new evidence contradicts it.

## Authoritative continuity sources

1. Google Doc: **BETA064 beta064_multidesk_loop.py Recovery Log — Crash/Retry Continuity**  
   Drive ID: `1VJaUMULaTonJxTRCiWKsof_bHSsjg1ouSfLVCKDepi8`
2. GitHub live state: `beta/CURRENT_STATE.json`
3. Recovery scaffold: `research/recovery/beta064_multidesk_loop_RECOVERY_UNCERTIFIED.py`
4. R12 findings: `research/recovery/BETA_064_MULTIDESK_LOOP_R12_SOURCE_FORENSIC_FINDINGS.md`
5. This R13 handoff.

A smaller duplicate recovery Doc is superseded and must not become authority.

## What is NOT lost

The project is not a blank-slate rebuild.

Surviving BETA evidence includes:
- original Jan-Jul Dukascopy XAUUSD ordered Bid/Ask ticks;
- corrected RIGHT-edge causal 5-second state engine;
- historical LEFT-edge builder used in the contaminated Checkpoint-01 lineage, preserved for forensics only;
- exact V2 E1/E2/E4 replacement rules;
- frozen Entry/session/Hold learned-model artifacts and their hashes;
- six-session authority logic;
- session probability blend;
- base-first ownership and one-position scheduling;
- C02C/C02D selected ledgers;
- Major Checkpoint 02/03 observed monthly metrics;
- Hold continuation model and threshold;
- Checkpoint-03 router overlay;
- strong Jan/Feb/Mar selected-timestamp mechanism-mask evidence for E5-E12;
- session child and derivative research records.

## Critical causal correction

Historical Major Checkpoint 03 observed result remains preserved:

- 5,469 one-position Entry+Initial-Hold trades;
- 88.3891% weighted survivability;
- 60.8155% favorable-first-passage;
- +$5,981.669 diagnostic path value;
- every observed month >=85%;
- historical C02D LOMO panel 7/7 >=85%.

However **Checkpoint 03 is NOT presently certified as a causal MT5 Entry implementation target.**

Why:
- the 2,097 Checkpoint-01 base positions were generated through a historical LEFT-edge 5-second timestamp path later identified by the causal erratum;
- Checkpoint-02 session gap-fill explicitly reserved those same base positions first;
- no surviving durable proof has been found that `beta064_allmonths_predictions.pkl` was regenerated from the corrected RIGHT-edge parent state after the erratum;
- therefore the later session additions are high-risk/presumed inherited from the same historical candidate/probability lineage until contrary BETA evidence is found.

The historical panel remains valuable forensic evidence, but it may not be relabeled MT5-causal by simply recreating the old helper.

## Exact historical call chain recovered

From preserved BETA V2/frozen source:

`load beta064_MM_1s.pkl (+ prior tail / next head)`
→ `feat_from_d(d)`
→ `v2.add_extra(v1.candidates(b), b)`
→ month/end trim
→ `v1.make_labels(d,b,c)`
→ `v1.add_model_features(b,c)`
→ frozen Jan-fit LightGBM scoring.

The missing helper therefore owned at least:
- `candidates(b)`;
- `make_labels(...)`;
- `add_model_features(...)`;
- `fit_models(...)`;
- `eff(...)`.

E1/E2/E4 were later replaced by exact V2 rules.

## Historical feature-state recovery

Recovered historical LEFT-edge 5s builder includes:
- open/high/low/mid;
- last Bid/Ask/spread;
- tick sum;
- tick-count-weighted qp/qv;
- body/range;
- r15/r30/r60/r300/r900/r1800/r3600/r14400;
- corresponding directional efficiencies;
- vol60/300/900;
- atr60/300;
- prior5/15/60 highs/lows using shift(1);
- tick_z;
- quote-activity-weighted daily value;
- vwap_dist / vwap_z;
- range_ratio;
- generic UTC ORB state.

Corrected `beta064_causal_core.py` moves completed 5s buckets to their completion time (+5 seconds) and is the only acceptable future runtime basis.

## Specialist mechanism recovery status

Exact active V2 replacements:
- E1 Macro Structural Trend — EXACT
- E2 Structural Pullback/Reacceleration — EXACT
- E4 VWAP/Value Trend Pullback — EXACT

Strong BETA-supported parent mechanism shapes, but candidate-emission parity still uncertified:
- E3 ORB
- E5 VWAP Reclaim
- E6 Value Reversion
- E7 Sweep/Reclaim
- E8 Level Bounce
- E9 Level Break
- E10 Compression Release
- E11 Kinetic Ignition
- E12 Failed Expansion

Jan/Feb/Mar selected-timestamp mask recall is especially strong:
- E5 approximately 92.6–98.4% in Feb/Mar;
- E6 approximately 99.2–99.6%;
- E7 100%;
- E10 100%;
- E11 100%;
- E12 100%;
- E9 approximately 94.4–95.8%;
- sparse E3/E8 selected points also matched.

These validate mechanism families, **not exact proposal emission**.

## Universal edge-emission hypothesis rejected

R11 proved the lost helper did not simply emit every specialist on a generic FALSE→TRUE mask transition.

Examples:
- E6 selected trades in Feb/Mar occur almost entirely inside persistent active states despite ~99% base-mask recall.
- E11 edge-transition recall was only about 41% Feb / 34% Mar despite 100% base-mask recall.
- E9 and E10 also show substantial persistent-state selection.

Therefore `research/recovery/beta064_multidesk_loop_RECOVERY_UNCERTIFIED.py` is a forensic scaffold only. Its generic edge emission must not be promoted.

## Current unresolved upstream items

1. Exact E3/E5-E12 proposal emission, persistence, debounce and desk-specific gating.
2. Exact historical `raw_score` identity where not preserved literally.
3. Exact BETA064 one-second `quote_pressure` semantics.
4. Exact BETA064 one-second `qv_imb` semantics.
5. Provenance/body of `beta064_allmonths_predictions.pkl`.
6. Any pre-ownership candidate/prediction surface that can expose proposal cadence without one-position censoring.
7. Corrected RIGHT-edge retraining/revalidation and a new replacement checkpoint.

## R13 source archaeology completed

### Google Drive direct search
Searched BETA-only indexed Drive for:
- `beta064_multidesk_loop.py`;
- `beta064_allmonths_predictions.pkl`;
- `beta064_session_meta_all.pkl`;
- recovery/build logs;
- `quote_pressure`, `qv_imb`, raw_score, debounce/cooldown;
- predecessor BETA026/BETA039 and BETA057/058/059 source filenames.

No loose helper or prediction table was found.

No loose BETA057/058/059 Python source was found under its exact filename in indexed Drive.

### Existing recovery docs
Authoritative crash/retry log exists and was resumed. A smaller live-continuity Doc exists; an older duplicate is explicitly superseded.

### Google Docs revision history
BETA Research Journal retains revisions through Sep-30/Oct-1. Selective Sep-30 revision reads were resumed. No embedded copy of the missing helper was found before the revision endpoint returned HTTP 429 rate limiting. Do not hammer the provider; resume selectively after cooldown if needed.

### Predecessor quote-pressure clue
Current BETA journal explicitly records that predecessor `quote_pressure1` was already source/side-signed, and later BETA039/BETA058 logic corrected a double-signing error. This is a lineage constraint only:
- do not multiply a recovered already-side-signed pressure by side again;
- do not assume BETA064 `quote_pressure` equals BETA026/039 `quote_pressure1` until parity proves it.

No exact durable `qv_imb` formula was recovered in this pass.

### Persistence/debounce clue
BETA009-era records preserve persistent states, bounded expiries, elapsed-time/tick-count confirmation and ownership resets. These establish that desk-specific state persistence/debounce is plausible in the BETA engineering lineage. Their thresholds must NOT be imported into BETA064 without direct evidence.

### Project/file-surface sweep
A Project/Library search did not recover standalone BETA057/058/059 source files or a hidden `beta064_multidesk_loop.py`. It surfaced historical project notes and reports only. Do not treat unrelated historical R9/Gamma artifacts as source for BETA064.

## Safe interpretation

This is **not** a GAMMA-scale total strategy loss.

The failure is concentrated in an upstream transient helper and prediction-lineage provenance. The market corpus, major downstream model artifacts, routing architecture, selected ledgers, Hold model, and observed research results survive.

But it **is** a serious MT5 certification blocker. We must not build an official Checkpoint-03 Entry EA until a corrected causal replacement checkpoint exists.

## Exact next actions for the next chat

Resume here, in this order:

1. **BETA-only source archaeology for qp/qv**
   - selectively inspect surviving BETA026/BETA039/BETA057-063 archives/fixtures if materializable;
   - solve the exact one-second pressure/volume-imbalance arithmetic from source or frozen feature fixtures;
   - classify every recovered field EXACT / DERIVED_EXACT / SUPPORTED_RECONSTRUCTION / UNKNOWN.

2. **Desk-specific E6/E11 emission reconstruction**
   - use historical LEFT-edge state for forensics only;
   - reconstruct active-state run lengths around preserved selected timestamps;
   - test desk-specific persistence/debounce hypotheses, not universal edge();
   - do not infer candidate cooldown from final selected-trade spacing because horizons/ownership censor those gaps.

3. **E3/E8 and residual E5/E9 gates**
   - resolve boundary semantics and any extra gating from BETA-only history/candidate fingerprints.

4. **Find or reconstruct a pre-ownership candidate/prediction surface**
   - search Drive revisions/archives for all-month predictions or candidate ledgers;
   - if unavailable, construct a forensic candidate corpus with evidence classifications and compare timestamp/side/specialist/raw_score fingerprints.

5. **Historical forensic reproduction**
   - when sufficiently constrained, produce a historical LEFT-edge helper reproduction for source archaeology only;
   - never use it as future runtime/MT5 logic.

6. **Corrected causal replacement**
   - rebuild the parent generator on completed RIGHT-edge state;
   - retrain/recalibrate only under a newly named BETA checkpoint;
   - re-run Jan-Jul causal Entry+Initial-Hold validation;
   - preserve August seal unless owner explicitly authorizes unsealing;
   - only after successful causal replacement and parity specification may an MT5 EA build be proposed.

## MQL5/MT5 boundary

No actual MQL5 is authorized by this recovery handoff.

Later MT5 implementation may begin only after:
- missing/derived parent-clock semantics are parity-certified;
- one-second qp/qv semantics are parity-certified;
- corrected RIGHT-edge Entry models and router are frozen;
- exact model translation/inference parity is proven;
- candidate/ownership sequence parity is proven;
- Hold continuation parity is proven;
- Hold→Exit remains separately researched/frozen rather than invented.

## Retry instruction

If a new chat or retry starts:

1. Read the authoritative Crash/Retry Google Doc first.
2. Read `beta/CURRENT_STATE.json`.
3. Read this R13 handoff.
4. Read R12 findings and the recovery scaffold.
5. Resume **R13 Next Action #1**.
6. Do not repeat R0-R12 searches unless contradictory evidence appears.
7. Do not touch Alpha or Gamma.
8. Do not open August.
9. Do not write an EA during helper recovery.
