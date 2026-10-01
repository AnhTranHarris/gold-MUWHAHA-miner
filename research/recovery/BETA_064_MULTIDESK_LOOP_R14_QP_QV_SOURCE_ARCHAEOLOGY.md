# BETA064 missing multidesk helper recovery — R14 qp/qv source archaeology

**Date:** 2026-10-01  
**Status:** ACTIVE RECOVERY / RECOVERY_UNCERTIFIED  
**Lineage:** BETA only  
**Alpha/GAMMA:** prohibited and not inspected  
**August:** SEALED  
**MQL5:** prohibited during recovery

## Purpose

Resume R13 Next Action #1 without repeating R0-R12. This bounded unit constrains the lost one-second quote-pressure / quote-volume feature lineage and records exactly which semantics are recovered versus still unknown.

## Evidence inspected

- Authoritative R13 crash/retry recovery log and max-chat handoff.
- Live `beta/CURRENT_STATE.json` and R13 state/handoff files.
- `research/BETA_039_SIGN_CORRECTED_ADAPTIVE_FRICTION_AND_FIVE_FAMILY_JANJUL_RESULTS.md`.
- BETA Research Journal BETA057-063 internal record.
- Authoritative corrected V2 freeze bundle from Drive: `BETA064_MAJOR_CHECKPOINT_02_ENTRY_HOLD_MODEL_FREEZE_BUNDLE_V2.zip`.
- V2 bundle SHA-256 independently rechecked: `ccfc0d18d733e97b18bbd183c6cc56b6bcac0f1c2c6c525bda596d0406eb98d3` — matches the frozen manifest/current state.
- V2 source files `beta064_causal_core.py`, `beta064_frozen_monthly_ps088_hold08.py`, `beta064_multidesk_v2.py` and LightGBM text exports.
- BETA-only Drive/Library searches for BETA026/BETA039/BETA057-063 loose source, `quote_pressure1`, `quote_pressure`, `qv_imb`, and named predecessor scripts.

No Alpha or Gamma artifact was inspected. No August data was opened.

## R14 recovered facts

### 1. BETA026 predecessor `quote_pressure1` — EXACT FOR BETA026

BETA039's source audit explicitly records the BETA026 source expression:

```text
quote_pressure1 = original_side * (up_quote_count - down_quote_count) / max(1, up_quote_count + down_quote_count)
```

The feature was already signed relative to the original proposed BUY/SELL side. BETA036-038 later multiplied by `side` again, which converted the intended trade-relative pressure into raw quote-direction imbalance. BETA039 removed that second sign without retuning thresholds.

**Classification:** `EXACT_FOR_BETA026_PREDECESSOR`.

**Constraint for recovery:** never multiply a recovered already-side-signed pressure by side a second time.

**Important limitation:** this does **not** prove that BETA064 one-second `quote_pressure` is byte/formula-identical to BETA026 `quote_pressure1`.

### 2. BETA064 one-second → five-second `qp` aggregation — EXACT

The authoritative corrected V2 `beta064_causal_core.py` defines:

```text
qp_5s = sum(quote_pressure_1s * tick_count_1s) / max(1, sum(tick_count_1s))
```

over the resampled five-second bucket. The corrected causal engine then moves the five-second bar index to the RIGHT edge (`+5s`), making `[t,t+5s)` state observable at `t+5s`.

**Classification:** `EXACT` for downstream BETA064 five-second aggregation/timing.

### 3. BETA064 one-second → five-second `qv` aggregation — EXACT

The same authoritative source defines:

```text
qv_5s = sum(qv_imb_1s * tick_count_1s) / max(1, sum(tick_count_1s))
```

**Classification:** `EXACT` for downstream BETA064 five-second aggregation.

### 4. BETA064 one-second `quote_pressure` arithmetic — STILL UNRESOLVED

The surviving evidence establishes lineage constraints but not formula identity.

Known:
- a predecessor BETA026 pressure was quote-count based and already side-signed;
- BETA057-063 journal records continued use of source-signed quote pressure in that later independent BETA research;
- BETA064 downstream source consumes one-second `d.quote_pressure` and tick-count weights it into 5s `qp`;
- frozen Entry/Hold trees materially use `qp`.

Not proven:
- that BETA064 `d.quote_pressure` equals the BETA026 formula;
- whether BETA064 pressure is side-relative before candidates exist, raw-directional, or derived from a different one-second cache convention.

**Classification:** `UNKNOWN_FORMULA / PREDECESSOR_LINEAGE_CONSTRAINED`.

### 5. BETA064 one-second `qv_imb` arithmetic — STILL UNRESOLVED

No surviving BETA-only source or indexed fixture in this unit exposed the exact one-second `qv_imb` arithmetic.

Known:
- raw Dukascopy source has `ask_volume` and `bid_volume`;
- BETA064 cache has one-second `qv_imb`;
- corrected V2 converts it to five-second `qv` by tick-count weighted mean;
- frozen Entry/Hold trees materially use `qv`.

Not proven:
- bid-vs-ask volume difference convention;
- normalization denominator;
- side signing;
- clipping, zero handling, or weighting inside the one-second cache.

**Classification:** `UNKNOWN`.

## Why this matters

`qp` and `qv` are not disposable columns. The frozen LightGBM Entry models include both features and their tree exports show material split usage. Replacing either one with a guessed formula risks probability drift and invalidates any Checkpoint-03 parity claim.

Therefore the recovery scaffold remains `RECOVERY_UNCERTIFIED` and must not fill either unknown with a plausible-looking formula.

## Search result

No loose BETA026/BETA057/BETA058/BETA059 source script or complete BETA039/BETA063 reproducibility ZIP was recovered from currently indexed Drive/Library title/content search in this bounded unit. The Research Journal preserves script names and methodology but not the missing one-second `qv_imb` implementation.

## R14 disposition

- Historical Checkpoint-03 observed metrics remain preserved for forensics only.
- MT5 Entry-parity certification remains **BLOCKED**.
- No helper is promoted as recovered source.
- No MQL5 is written.
- August remains sealed.

## Exact next action

1. Search/materialize any surviving BETA-only one-second cache fixture, manifest, archive member, or predecessor source that exposes `qv_imb` and the BETA064 cache builder.
2. If exact one-second `qv_imb` still cannot be recovered, keep it explicitly UNKNOWN and move to desk-specific E6/E11 emission reconstruction using historical LEFT-edge state for forensics only; do not use one universal `edge()` rule.
3. Resolve E3/E8 and residual E5/E9 candidate gates after E6/E11 persistence/debounce is constrained.
4. Locate or construct a pre-ownership candidate/prediction surface with evidence classifications.
5. Historical LEFT-edge reproduction, if completed, remains forensic-only.
6. Build/retrain/revalidate a newly named corrected RIGHT-edge parent system before any MT5 Entry-parity claim.
