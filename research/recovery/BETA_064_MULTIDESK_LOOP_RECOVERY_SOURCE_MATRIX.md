# BETA064 — beta064_multidesk_loop.py Recovery Source-Confidence Matrix

**Date:** 2026-10-01  
**Branch:** beta  
**Status:** ACTIVE SOURCE RECOVERY — NOT YET PARITY CERTIFIED  
**Scope:** BETA ONLY. Alpha/GAMMA prohibited. August sealed. No MQL5 change.

## Purpose

Recover or independently reconstruct the historical transient helper `beta064_multidesk_loop.py` required by the preserved BETA064 V2 parent proposal generator.

This document separates direct evidence from inference. Nothing marked MEDIUM/LOW may be represented as exact Checkpoint-03 source until parity tests promote it.

## Recovery evidence hierarchy

- **EXACT/HIGH** — body/interface/value is directly preserved in a BETA artifact or frozen learned model.
- **CORROBORATED/MEDIUM** — contemporaneous BETA code implements the same mechanism and/or later BETA reconstruction agrees, but exact historical helper body is absent.
- **HYPOTHESIS/LOW** — later broad reconstruction or role-level architecture only.
- **UNRESOLVED** — no sufficient BETA evidence yet.

## Shared helper API

| Item | Confidence | Evidence |
|---|---|---|
| `FIT_END = 2026-01-09 UTC` | HIGH | preserved `beta064_session_entries.py`; frozen Jan FIT recipe |
| `CAL_END = 2026-01-11 UTC` | HIGH | preserved `beta064_session_entries.py`; R1B2 record |
| `eff(s,n)` = abs displacement / sum absolute step displacement | HIGH | later BETA064 reconstruction + causal core dependency; standard formula explicitly preserved |
| required callable names | HIGH | preserved `beta064_multidesk_v2.py`: `build_features`, `candidates`, `make_labels`, `add_model_features`, `fit_models`, `eff` |
| candidate output schema | HIGH | preserved V2 `add_extra` calls `pd.DataFrame(rows, columns=c.columns)`; downstream fields prove `time,i,side,specialist,raw_score,horizon,checkpoint` lineage |
| Entry model feature order | HIGH | frozen joblib + model manifest; 38 exact columns |
| Entry model parameters | HIGH | frozen joblib + model manifest |
| `fit_models` return shape | HIGH | preserved V2 caller: `c,fit,cal,diag,ms,mw` |
| offline label geometry | HIGH | preserved `beta064_session_entries.py`, Checkpoint 02/03 contracts |
| BUY/SELL executable sides | HIGH | preserved label code + checkpoint contracts |
| $0.02 lifecycle research fee | HIGH | preserved label code + checkpoint records |
| corrected 5s right-edge observability | HIGH | preserved `beta064_causal_core.py` + causal alignment erratum |

## Multi-scale feature engine

The corrected Checkpoint-02/03 5s state is HIGH confidence because `beta064_causal_core.py` is preserved.

Exact preserved state:
- completed `[t,t+5s)` bucket becomes observable at `t+5s`;
- midpoint OHLC, last Bid/Ask/spread, tick count;
- weighted `qp` and `qv` from the one-second ledger;
- body/range;
- r15/r30/r60/r300/r900/r1800/r3600/r14400;
- efficiency at the same lags;
- vol60/vol300/vol900;
- atr60/atr300;
- prior5/prior15/prior60 structural highs/lows using `shift(1)`;
- tick_z;
- quote-activity-weighted daily value, vwap_dist/vwap_z;
- range_ratio;
- historical generic UTC ORB state.

### One-second cache fields

Required one-second schema is HIGH:
`open_mid, high_mid, low_mid, mid, bid, ask, spread, tick_count, quote_pressure, qv_imb`.

Exact formulas for `quote_pressure` and `qv_imb` are currently **UNRESOLVED**.

BETA evidence constrains them:
- R1B2 record calls `quote_pressure` a signed quote-change pressure;
- `qv_imb` is a quote-volume imbalance proxy;
- source contains Dukascopy Ask/Bid quote volumes;
- BETA063 warns that cached quote pressure was already side-signed in a different predecessor pipeline and must not be signed twice;
- later BETA064 broad reconstruction used a midpoint-change pressure proxy and `(bid_volume-ask_volume)/(bid_volume+ask_volume)`, but that later reconstruction is not proof of the historical cache builder.

## Parent specialist clocks

### E1 Macro Structural Trend
**Confidence: HIGH for V2 active rule.**
The old helper's sparse E1 is irrelevant to Checkpoint-02/03 because V2 explicitly removes it and replaces it.

Exact V2 active rule:
- side = sign(r3600 + 0.35*r14400)
- fresh directional 5m extreme using prior5 high/low
- r900 aligned
- eff3600 > .14
- eff900 > .14
- raw score = 62 + 18*eff3600 + 12*eff900
- horizon 900s / checkpoint 60s.

### E2 Structural Pullback / Reacceleration
**Confidence: HIGH for V2 active rule.**
V2 replacement exact:
- side = sign(r3600)
- r3600 aligned >0
- r300 counter-move <0
- r60 >0 aligned
- r15 >0 aligned
- eff3600 > .12
- raw score = 60 + 15*eff3600 + 10*eff60
- 300s / 30s.

### E4 VWAP / Value Trend Pullback
**Confidence: HIGH for V2 active rule.**
V2 replacement exact:
- side = sign(r3600)
- abs(vwap_dist) < .75*atr60
- r3600 aligned >0
- r60 aligned >0
- eff3600 > .12
- raw score = 58 + 15*eff3600 + 8*eff60
- 300s / 30s.

### E3 Opening Range Break
**Confidence: MEDIUM mechanism / LOW exact mask and raw score.**
Evidence:
- R1B2 role: London/NY opening-range break and acceptance.
- historical helper feature engine contains generic UTC ORB windows at 08:00 and 13:30.
- preserved session prototype later uses ORB accepted-break logic and score family `65 + 8*eff60 + 4*tick_z`.
- later broad reconstruction uses UK/NY local ORB acceptance with body/efficiency/friction gates.
Exact parent mask/raw score must be parity-derived.

### E5 VWAP / Value Reclaim
**Confidence: MEDIUM mechanism / LOW exact parent thresholds.**
Evidence:
- R1B2 role: value break/reclaim transition.
- historical core carries daily quote-activity VWAP.
- preserved session prototype uses cross-through session VWAP with r15 confirmation and score `60 + 8*eff60`.
- later broad reconstruction uses session-VWAP cross + eff/friction.
Exact original parent likely uses the generic/daily value surface; parity required.

### E6 Statistical Value Reversion
**Confidence: MEDIUM mechanism / LOW exact parent thresholds/raw score.**
Evidence:
- R1B2 role: statistical value reversion in rotational state.
- core exposes `vwap_z`, efficiency, ATR and range state.
- later broad reconstruction uses normalized value displacement, low eff300, short-horizon velocity/acceleration and friction.
- later C02C confirms E6 parent proposals already existed and were abundant; derivative E6 clocks are non-authoritative.
Exact original mask/raw score unresolved.

### E7 Liquidity Sweep / Reclaim
**Confidence: MEDIUM.**
Evidence:
- R1B2 role and timeframe contract.
- preserved session prototype uses wick/excursion beyond ORB/previous-session boundary then midpoint/body reclaim, score family `67 + 8*eff15 + 3*tick_z`.
- later broad reconstruction uses analogous boundary/reclaim logic with efficiency/friction gates.
Exact parent structural boundary and score require parity.

### E8 Key-Level Bounce / Rejection
**Confidence: LOW-to-MEDIUM.**
Evidence:
- R1B2 role: HTF/key-level rejection without requiring classical sweep.
- corrected core has prior15/prior60 highs/lows.
- later broad reconstruction uses proximity/rejection of prior180 (=15m in 5s bars), body sign, eff60 and friction.
Exact parent mask/raw score unresolved.

### E9 Key-Level Break / Acceptance
**Confidence: MEDIUM.**
Evidence:
- R1B2 role: accepted structural/key-level break.
- corrected core has prior structure.
- later session/broad logic uses open-inside/close-outside/body acceptance with efficiency/friction.
Exact parent boundary and raw score unresolved.

### E10 Compression → Expansion
**Confidence: MEDIUM.**
Evidence:
- R1B2 role: compression→directional expansion.
- corrected core exposes range_ratio, tick_z, body/range.
- preserved session prototype: pre-open range <.75*atr300; 5s range >1.8*rolling median; tick_z>.25; score `64+7*tick_z`.
- later broad reconstruction: prior compression ratio <=.30 + structural release + tick_z/eff/friction.
Exact parent mask/raw score unresolved.

### E11 Kinetic Ignition
**Confidence: LOW-to-MEDIUM.**
Evidence:
- R1B2 role explicitly names velocity, acceleration, efficiency and quote-pressure ignition.
- later broad reconstruction uses v3 normalized velocity, a3 normalized acceleration, tick_z, eff15, friction.
- E11 dominates selected real capacity, therefore exact parity is critical.
Exact original formula/raw score unresolved; one-second quote-pressure semantics may matter.

### E12 Failed Expansion / Contradiction
**Confidence: MEDIUM.**
Evidence:
- R1B2 role: failed breakout/contradiction and recross.
- preserved session prototype uses prior outside-ORB state then recross inside; score `66+6*tick_z`.
- later broad reconstruction uses prior structural-range breach then recross with body/tick_z/eff/friction.
Exact parent boundary/raw score unresolved.

## Exact model reconstruction evidence

Frozen base joblib confirms exact Entry feature names/order:
`spread,r15,r30,r60,r300,r900,r3600,r14400,eff15,eff60,eff300,eff900,eff3600,vol60,vol300,atr60,atr300,tick_z,qp,qv,vwap_z,range_ratio,body,range,side,raw_score`
plus specialist dummies:
`sp_E10, sp_E11, sp_E12, sp_E1, sp_E2, sp_E3, sp_E4, sp_E5, sp_E6, sp_E7, sp_E8, sp_E9`.

Exact LightGBM parameters:
- n_estimators 180
- num_leaves 23
- learning_rate .045
- subsample .8
- colsample_bytree .8
- reg_lambda 2
- min_child_samples 80
- n_jobs 4
- verbosity -1.

## Required certification sequence

1. Rebuild exact shared helper API and HIGH-confidence functions.
2. Rebuild one-second cache candidates from original Jan raw ticks; solve `quote_pressure` / `qv_imb` semantics by probability parity against frozen models and preserved selected ledgers.
3. Reconstruct E3/E5–E12 candidate masks from BETA evidence.
4. Candidate parity target per specialist:
   - selected Checkpoint-03 timestamp/side recall = 100%;
   - no unexplained extra candidates that alter frozen model/ownership sequence;
   - raw_score parity where a frozen reference can be inferred.
5. Model parity:
   - frozen `p_surv`, `p_win`, `entry_score` on preserved selected candidates.
6. Session probability parity.
7. Exact 5,469 selected-sequence identity and selected-panel SHA-256:
   `2fe7b28280d670b915c0968e8daac5fbcf23193faf2c36b0b6f45c0e6d480cc5`.
8. Only after the above passes may the reconstructed helper be promoted from `research/recovery` to authoritative runtime source and the Checkpoint-03 provenance blocker be removed.

## Fail-closed rule

Until parity passes, any reconstructed helper must carry **RECOVERY / UNCERTIFIED** in its header and must not be used to authorize MT5 Checkpoint-03 parity.
