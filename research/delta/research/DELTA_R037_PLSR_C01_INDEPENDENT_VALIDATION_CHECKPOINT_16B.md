# DELTA R037 — PLSR C01 Independent Later-January Validation — Checkpoint 16B

**Status:** COMPLETE — INDEPENDENT VALIDATION PASS / STRONG PASS / NON-PROMOTING  
**Candidate:** R037-PLSR-C01_PDH_PDL_S5_RECLAIM  
**Parent:** R037_PLSR_STAGE_A_SCREEN_CHECKPOINT_16A  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Timeout recovery

The visible ChatGPT message-delivery timeout did not invalidate the scientific state. The 16B preregistration and producer were already committed. No 16B result/report/manifest existed, so recovery correctly resumed at official compute rather than rerunning 16A.

Official producer:
`research/delta/experiments/delta_r037_plsr_c01_independent_validation.py`

Producer commit:
`ccef1cd460d585857b19b30532fd91e7d2ccc7de`

Producer blob:
`382b641e1b8598b4296da52401ec9ce795d1931a`

The GitHub recovery artifact from failed timeout-guard run 37167773135 preserved the committed producer/helper snapshot. The local recovery snapshot producer blob was verified exactly before compute.

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

The bounded official replay exited 0 in **25.795 seconds**.

## Holdout result

Later-January holdout:
- warmup: 2026-01-14 00:00 UTC to 2026-01-18 12:00 UTC, no economic entries
- validation: 2026-01-18 12:00 UTC through final January tick
- loaded ticks: **6,076,533**
- holdout ticks: **4,929,353**

Frozen C01 generated:
- **9 proposals**
- **8 source eligible**
- **8 distinct days**
- **7 accepted entries**
- 3 long / 6 short proposals
- PDH 6 / PDL 3 proposals
- only one source rejection: RELOST_RECLAIM

### Combined economics versus surrogate parent

| Metric | Parent | C01 combined | Delta |
|---|---:|---:|---:|
| Trades | 13,630 | **13,637** | **+7** |
| Official wins | 5,912 | **5,918** | **+6** |
| Gross profit | $1,877.63 | **$1,886.70** | **+$9.07** |
| Gross loss | -$4,734.64 | **-$4,735.36** | **-$0.72** |
| Net | -$2,857.01 | **-$2,848.66** | **+$8.35** |
| Max balance DD | $2,861.05 | **$2,852.70** | **improved 0.292%** |
| Max equity DD | $2,862.00 | **$2,853.65** | **improved 0.292%** |

Direct PLSR contribution:
- 7 entries
- 6 official wins
- **+$8.35**
- **+$1.19 per PLSR entry**

Diagnostic level contribution only:
- PDH: 5 entries / 4 wins / **+$0.58**
- PDL: 2 entries / 2 wins / **+$7.77**

Both sides were positive in independent validation. This strengthens the original frozen combined PDH+PDL rule and provides no evidence for a post-hoc split.

## Gate decision

Every preregistered gate passed:
- proposals >= 6
- distinct days >= 4
- accepted entries >= 5
- combined trade count not lower
- winner/quality gate pass
- incremental net nonnegative
- net deterioration limit pass
- drawdown deterioration limit pass

**16B independent validation = PASS / STRONG PASS.**

This remains non-promoting because the surrogate parent is not a final promoted DELTA system and month-by-month robustness is still required.

Official result SHA-256:
`c4ac99a81b1806f559c9d7ed8a3ba34b5fe11fac469c72ec39b33de35a8c1b5a`

Compact result:
`research/delta/reference/DELTA_R037_PLSR_C01_INDEPENDENT_VALIDATION_CHECKPOINT_16B.json`

## Next bounded unit

`R037_PLSR_C01_MONTH_BY_MONTH_SURROGATE_VALIDATION`

Freeze C01 unchanged. Run month-isolated validation sequentially under the same causal rule and surrogate-parent ownership semantics. No threshold retuning, no PDH/PDL cherry-pick, no August, no MQL5.
