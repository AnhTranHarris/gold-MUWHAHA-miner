# DELTA R037 — PDHSR C02 Independent Later-January Validation — Checkpoint 17AE

**Status:** COMPLETE — INDEPENDENT HOLDOUT PASS / STRONG  
**Candidate:** R037-PDHSR-C02_S5_CLOSE_RECLAIM  
**Parent:** R037_PDH_PDL_SWEEP_RECLAIM_STAGE_A_SCREEN_CHECKPOINT_17AD  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Frozen hypothesis

The 17AD winner was carried forward unchanged:

first strict prior-day high/low sweep → first completed 5-second close reclaimed back inside the swept boundary → execute reversal only if the live execution quote still remains reclaimed.

No threshold, side, session, weekday, stop, trail, or hold-time parameter was retuned.

## Independent holdout

Warm-up/context: 2026-01-14 00:00 UTC onward.  
Economic holdout: 2026-01-18 12:00 UTC through the final January tick.  
Loaded ticks: **6,076,533**.  
Holdout ticks: **4,929,353**.

## Result

- proposals: **8**
- eligible trades: **8**
- distinct days: **8**
- direction: 2 long / 6 short
- rejections: **0**
- official wins: **7 / 8**
- gross profit: **+$9.08**
- gross loss: **-$0.73**
- direct net: **+$8.35**

Level contribution was diagnostic only:
- PDH: 6 trades / 5 wins / +$0.58
- PDL: 2 trades / 2 wins / +$7.77

No post-hoc PDH/PDL split is authorized.

## Decision

All preregistered supply and economic gates passed.

**Freeze C02 unchanged and advance to month-by-month validation.**

Producer commit: `32ab7407bfbe24a96a7741fe2214be8742d33ded`  
Producer blob: `e330f2cc994f3b9112a3a6ec4176e7af3afc7cce`  
Producer SHA-256: `72e9593e593a1ac32a60c351ed2a40d8289ec0c774f50af32a3cbd7ff300b361`  
Raw result SHA-256: `393a2fc9e5bbdbe7c51fbffef28764c498ec3d4cef9d247c65d8c272d9ab4274`

## Next bounded unit

`R037_PDHSR_C02_MONTH_BY_MONTH_VALIDATION`

Freeze C02. Validate sequentially on February–July 2026 with causal prior-month/day context as needed, no August, no parameter retuning, and no PDH/PDL cherry-pick.
