# BETA064 MAJOR CHECKPOINT 03 — HIGH-COUNT ENTRY + INITIAL-HOLD FREEZE

**Date:** 2026-09-30  
**Branch:** `beta`  
**Authority:** NEW MAJOR CHECKPOINT — supersedes Major Checkpoint 02 for future Entry→Initial-Hold research and eventual MT5 parity work.  
**Scope:** ENTRY + INITIAL-HOLD only. HOLD→EXIT remains intentionally undefined.  
**August:** SEALED.  
**Official EA:** NO.  
**Official MQL5 implementation:** NOT CREATED / NOT AUTHORIZED BY THIS CHECKPOINT.  
**Parent lineage:** Major Checkpoint 02 → C02C → C02D robustness repair → C02H repeated optimization and final margin-rescue rejection.

## 1. Why this checkpoint is promoted

The research objective was to maximize valid Entry opportunity count while preserving the owner's >=85% Entry→Initial-Hold survivability requirement, avoiding two invalid shortcuts:

1. deleting large amounts of opportunity merely to raise the headline survival percentage; and
2. admitting weak new trades whose poor standalone survival is hidden by a strong parent portfolio.

Repeated Jan–Jul experiments established the following Pareto frontier:

- Major Checkpoint 02: 5,070 trades / 88.44% weighted survival.
- C02D robust child: 5,469 / 88.39% / 7 of 7 LOMO months >=85%.
- C02C aggressive child: 5,519 / 88.20%, but threshold-reselection LOMO was 6/7 with February ~84.95%.
- C02H derivative expansions could reach roughly 5,527–5,569 observed trades while keeping each observed month >=85%, but the new additions themselves survived only ~55–61% and diagnostic value fell materially.
- A final E7/E9 specialist-adapter attempt to rescue the exact 50 trades removed by C02D failed out of sample: 43 held-out restorations survived only ~65.1%.

Therefore 5,469 trades is the strongest currently reproducible high-count / high-survival operating point satisfying the broadest set of quant requirements.

## 2. Frozen Jan–Jul result

| Month | Trades | Entry→Initial-Hold survival | Favorable first passage | Diagnostic path value |
|---|---:|---:|---:|---:|
| Jan | 761 | 88.83% | 61.63% | +$760.672 |
| Feb | 1,021 | 85.99% | 58.28% | +$1,158.883 |
| Mar | 1,484 | 87.80% | 60.31% | +$1,730.660 |
| Apr | 657 | 88.74% | 61.19% | +$718.725 |
| May | 582 | 90.55% | 64.09% | +$646.402 |
| Jun | 636 | 89.94% | 62.42% | +$693.564 |
| Jul | 328 | 89.94% | 59.45% | +$272.763 |
| **Total** | **5,469** | **88.3891% weighted** | **60.8155% weighted** | **+$5,981.669** |

Relative to Major Checkpoint 02:
- +399 trades;
- +7.87% opportunity count;
- weighted survivability changes only from 88.44% to 88.39%;
- every month remains >=85%.

Condition-matched mechanism coverage:
- Major Checkpoint 02: 3,044 / 71,810 = 4.24%.
- Checkpoint 03 / C02D: 3,127 / 71,810 = 4.35%.

## 3. Leave-one-month-out robustness

For each held-out month, the E7/E9 child authority pair was selected using only the other six months, subject to every development month remaining >=85% while maximizing retained trade count.

All seven folds independently selected the same pair:

- E7 child `ps_b75 >= 0.915`
- E9 child `ps_b75 >= 0.915`

Held-out survival therefore equals the fixed-rule monthly panel above.

**7/7 held-out months pass >=85%.**

The weakest month remains February at 85.99%, giving a narrow but positive robustness buffer.

## 4. Exact checkpoint overlay

Checkpoint 03 uses the exact C02C router and changes only the E7/E9 child authority.

Frozen base Entry authority:
- `P_survive >= 0.88`
- `entry_score = P_survive * P_first_passage`
- `entry_score >= 0.30`

Session-child precheck:
- `ps_b75 >= 0.89`
- `es_b75 >= 0.08`

Under-covered non-E6 child floors:
- E5 VWAP Reclaim: `ps_b75 >= 0.9145`
- E7 Sweep/Reclaim: **`ps_b75 >= 0.9150`**
- E9 Level Break: **`ps_b75 >= 0.9150`**
- E10 Compression Release: `ps_b75 >= 0.9145`
- E12 Failed Expansion: `ps_b75 >= 0.9145`

E11 Kinetic Ignition is not expanded. It retains frozen session authority thresholds.

E6 Value Reversion retains the C02C session-conditioned rules:
- New York: `ps_b75 >= 0.920`, `eff60 >= 0.30`, `friction <= 0.14`, `session_value_z >= -2.5`.
- UK: `ps_b75 >= 0.905`, `eff60 >= 0.40`, `eff300 <= 0.10`, `session_value_z >= -4.0`.
- other sessions: frozen Major-Checkpoint-02 session threshold.

Frozen session thresholds:
- Australia 0.920
- Asia 0.900
- Middle East 0.915
- Europe 0.910
- UK 0.925
- New York 0.925

## 5. Ownership and scheduling

1. Generate all causal parent E1–E12 proposals.
2. Select frozen-base proposals first with the 0.88 / 0.30 gates.
3. Reserve each base proposal's specialist horizon.
4. Session-child proposals may be considered only if their entire proposal horizon lies outside every reserved base interval.
5. Only E5/E6/E7/E9/E10/E11/E12 may own session-child positions.
6. Apply the Checkpoint-03 child authority above.
7. Schedule approved session children by earliest finish:
   - ascending proposal end time;
   - tie-break higher `ps_b75`;
   - then higher `es_b75`.
8. One account / one open research position.
9. Base ownership always wins.

## 6. Session probability blend

For an active session authority:

`ps_b75 = 0.25 * p_surv + 0.75 * session_p_surv`

`pw_b75 = 0.25 * p_first_passage + 0.75 * session_p_first_passage`

`es_b75 = ps_b75 * pw_b75`

If multiple sessions overlap, choose the active session whose session model maximizes:

`session_p_surv * session_p_first_passage`

If no declared session is active, fall back to base probabilities.

## 7. Six frozen local sessions

- Australia/Sydney 08:00–17:00
- Asia/Tokyo 09:00–18:00
- Asia/Dubai 08:00–17:00
- Europe/Berlin 08:00–17:00
- Europe/London 08:00–17:00
- America/New_York 08:00–17:00

Timezone conversion must be calendar/DST aware. Fixed UTC tables are forbidden.

## 8. E1–E12 Entry specialist registry

1. E1 Macro Structural Trend — horizon 900s / Initial-Hold checkpoint 60s.
2. E2 Structural Pullback / Reacceleration — 300s / 30s.
3. E3 Opening Range Break — 300s / 30s.
4. E4 VWAP / Value Trend Pullback — 300s / 30s.
5. E5 VWAP / Value Reclaim — 120s / 15s.
6. E6 Statistical Value Reversion — 180s / 20s.
7. E7 Liquidity Sweep / Reclaim — 120s / 15s.
8. E8 Key-Level Bounce / Rejection — 300s / 30s.
9. E9 Key-Level Break / Acceptance — 300s / 30s.
10. E10 Compression → Expansion — 120s / 15s.
11. E11 Kinetic Ignition — 45s / 10s.
12. E12 Failed Expansion / Contradiction — 120s / 15s.

E13–E16 remain SHADOW ONLY and have no position ownership authority.

## 9. Initial-Hold model

The exact frozen Major-Checkpoint-02 Hold model is inherited unchanged.

Purpose:
estimate post-checkpoint continuation worthiness for positions that:
- survived to the specialist checkpoint;
- have not already resolved through favorable or adverse first passage.

Frozen Hold continuation threshold:

`P_continue >= 0.6185642603486833`

H1–H8 trajectory roles:
- H1 Ignition Confirmation
- H2 Extension / Runner Persistence
- H3 Healthy Pullback
- H4 Reacceleration
- H5 Transient Scalp / Fragile Continuation
- H6 Stall / Chop
- H7 Failed Acceptance / Thesis Failure
- H8 Exhaustion / Climax

The Hold layer does **not** define a final exit.

## 10. Research label geometry

Offline Entry→Initial-Hold labels only:

`spread = max(candidate_spread, 0.05)`

`atr = max(atr60, spread)`

`favorable_barrier = max(0.35, 1.25*spread, 0.30*atr)`

`adverse_barrier = max(0.30, 1.00*spread, 0.22*atr)`

Survival:
the executable adverse barrier does not hit before the specialist Initial-Hold checkpoint.

First-passage success:
the favorable barrier hits before the adverse barrier within the specialist horizon.

Diagnostic resolution:
opposite executable quote at first favorable/adverse resolution, or last quote at horizon, minus $0.02 research lifecycle fee.

These are research labels, not a final live exit policy.

## 11. Exact selected-panel identity

The exact Checkpoint-03 selected panel is reproducible from the C02C selected ledger by removing:

`specialist in {E7_SWEEP_RECLAIM, E9_LEVEL_BREAK} AND ps_b75 < 0.915`

This removes exactly 50 trades:

5,519 → **5,469**.

Exact selected CSV SHA-256:

`2fe7b28280d670b915c0968e8daac5fbcf23193faf2c36b0b6f45c0e6d480cc5`

Monthly result SHA-256:

`03dc5e620f8e8575d569768d1ed7e2f1d73a98047c4c5907627b1502367c0b60`

## 12. Final attempted rescue — rejected

A final leave-one-month-out adapter attempted to restore the exact 50 discarded E7/E9 trades using:
- existing microstate;
- E7 regime/entropy/Kalman/CUSUM state;
- E9 completed Heikin-Ashi, squeeze and structural/Fibonacci location.

Development thresholds were required to make the restored trades themselves >=85% with positive diagnostic value.

Held-out union:
- 43 attempted restorations;
- only ~65.1% survival;
- inconsistent month transfer.

Decision:
**do not restore the 50 discarded trades.**

This is the final optimization result supporting the 5,469-trade freeze.

## 13. Learned-model artifacts

Checkpoint 03 does not retrain the learned Entry/session/Hold models. It inherits the corrected Major-Checkpoint-02 V2 bundle:

- file: `BETA064_MAJOR_CHECKPOINT_02_ENTRY_HOLD_MODEL_FREEZE_BUNDLE_V2.zip`
- Drive file ID: `1phzsMX0SKESoqJ4O53vI9nE7fffrX6T-`
- SHA-256: `ccfc0d18d733e97b18bbd183c6cc56b6bcac0f1c2c6c525bda596d0406eb98d3`

Critical model hashes:
- base Entry model: `ba68874a69ce19db0768e8ebe8feefd3a6ec34c1bb076437815452366f9057cf`
- final session-router models: `bb985b1461da3f44eff43742d1b67fb8875f6b5742333df09ccade9a5250dc78`
- Hold joblib: `0f24f18dffabf681157dfef14bc4c67898b561f26d8fe7d372fa72623b99eef1`
- Hold tree: `06214dc6b08b37e64ad26626471c46c2cf9bb21327554ce99c8ea6d69d41718e`

## 14. Non-authoritative research retained outside the checkpoint

The following remain valuable research but do not change Checkpoint-03 ownership:

- C02G same-timestamp derivative-state matrix;
- C02H specialist-specific context adapters;
- E13–E16 shadow specialists;
- C02C aggressive 5,519-trade child;
- C02H derivative count frontier.

No future implementation may silently add these to Checkpoint 03 and retain the Checkpoint-03 name.

## 15. Reproducibility / provenance blocker

The corrected V2 bundle contains `beta064_multidesk_v2.py`, but that file imports historical helper:

`/mnt/data/beta064_multidesk_loop.py`

That helper is not currently in the V1/V2 freeze bundles, live GitHub `beta`, or Drive search.

Consequences:
- exact broadened E1/E2/E4 source is preserved in `beta064_multidesk_v2.py`;
- exact learned models are preserved;
- the Checkpoint-03 routing overlay is preserved;
- several older parent specialist proposal formulas cannot be claimed line-for-line from durable source today.

This does **not** invalidate the frozen observed panel, but it is a hard MT5 coding/parity blocker.

Before an official MT5 parity build, either:
1. recover the historical helper exactly; or
2. create an independently verified candidate-parity corpus and reconstruct every missing specialist until proposal timestamp/side/raw-score/horizon/checkpoint identity is exact.

No approximate rewrite may be called Checkpoint 03.

## 16. Authority

Major Checkpoint 03 is now the authoritative BETA Entry + Initial-Hold research checkpoint.

Future Entry/Initial-Hold research must compare against it.

Hold→Exit remains deferred.

August remains SEALED.

No MQL5 EA has been created by this checkpoint.
