# BUILD-02 Session/Timeframe Jan-Jul Stress 002

**Unit:** `DAA_GRID_SYSTEM_BUILD_02_SESSION_TIMEFRAME_JANJUL_STRESS_002`  
**Candidate:** `STMR_XMONTH_ADMISSIBILITY_001`  
**Status:** **STRONG CROSS-MONTH RESEARCH CANDIDATE — NOT PROMOTED**

The owner required the January-only session/timeframe layer to be stress-tested month-by-month on January-July ordered Dukascopy ticks before any new whole-system dimension is added. August remained sealed.

## Provenance

The authoritative January floor remains `STMR_SLEEVE_PHASE_001`: **+$877.78 / 1,518 trades / PF 1.602933**.

The original portable January replay helper was never durably committed; only its hash and result survived. The Jan-Jul extension is therefore a clean-room replay from committed semantics and canonical source hashes. Its January control is **+$779.00 / 1,724 trades / PF 1.46044**. This is close enough for relative stress diagnosis but not byte-identical parity, so this unit does not overwrite the accepted January floor.

## Frozen baseline stress

| Month | Frozen clean-room layer |
|---|---:|
| Jan | +$779.00 |
| Feb | -$254.58 |
| Mar | -$198.17 |
| Apr | -$231.64 |
| May | -$78.78 |
| Jun | +$31.61 |
| Jul | -$185.67 |
| **Jan-Jul** | **-$138.23** |

Baseline aggregate: GP $8,341.96; GL -$8,480.19; PF 0.9837; 8,403 trades; expected payoff -$0.01645; worst month-local equity DD $282.50.

The January sleeve population therefore does **not** generalize as-is.

## Preregistered cross-month admissibility refinement

Selection used **Jan-Apr only**. May-Jul were not used by the final sleeve-selection rule. However, broad May-Jul baseline/timeframe sweeps had already been inspected before the final candidate was frozen, so May-Jul is a **frozen-rule forward re-test, not pristine untouched OOS**.

Rule: **fund a semantic sleeve only when its frozen Jan-Apr aggregate net is positive; otherwise keep the state visible but OBSERVE_ONLY.**

Funded:
- ASIA_LOWER_TAKEOVER
- LONDON_M5_TAKEOVER
- OVERLAP_LOWER_TAKEOVER
- LATE_ALIGNED_MOMENTUM
- LATE_MACRO_SPLIT_TRANSFER
- LATE_LOWER_TAKEOVER

Observe-only:
- ASIA_M15_DIVERGE_M5_RECLAIM
- LONDON_M5_RECLAIM
- OVERLAP_ALIGNED_COUNTERCROSS
- NY_LOWER_TRANSFER
- NY_LOWER_COUNTERCROSS
- LATE_M5_REJECTION

Five toxic sleeves remained negative in all four leave-one-development-month-out tests; LONDON_M5_RECLAIM was negative in the full Jan-Apr block and 3/4 LOO tests. Directional FLIP was also tested and all six FLIP families remained negative over Jan-Apr.

## Frozen May-Jul forward re-test

| Month | Frozen | Candidate | Improvement |
|---|---:|---:|---:|
| May | -$78.78 | **+$47.41** | +$126.19 |
| Jun | +$31.61 | **+$184.81** | +$153.20 |
| Jul | -$185.67 | **-$70.57** | +$115.10 |
| **May-Jul** | **-$232.84** | **+$161.65** | **+$394.49** |

Forward candidate: GP $922.98; GL -$761.33; PF 1.2123; 770 trades; expected payoff +$0.20994; worst month-local equity DD $100.38.

## Full clean-room Jan-Jul candidate

| Metric | Frozen reconstruction | Candidate |
|---|---:|---:|
| Net | -$138.23 | **+$780.42** |
| Gross profit | $8,341.96 | $5,078.00 |
| Gross loss | -$8,480.19 | **-$4,297.58** |
| PF | 0.9837 | **1.1816** |
| Trades | 8,403 | 3,963 |
| Win rate | 27.89% | **32.05%** |
| Expected payoff | -$0.01645 | **+$0.19693** |
| Worst month-local equity DD | $282.50 | **$111.37** |
| Forced final liquidations | 0 | **0** |

Net improves **+$918.65** and gross loss falls **49.3%**, while trade retention is **47.2%**. Five of seven reconstructed months are positive; April and July remain negative.

## Rejected fine-tuning

- **Blanket DST remapping:** inconsistent and not promoted.
- **Removing Asia/London subphase gates:** increases activity but weakens development economics.
- **Global M5/M15/all-fast ownership:** faster settings repair isolated months but fail forward; original completed-bar EMA8/21 remains.
- **Directional FLIP of toxic sleeves:** negative Jan-Apr; rejected.
- **Higher-throughput five-toxic-sleeve filter:** retains more trades but is inferior on net, PF and drawdown versus the strict six-sleeve core.

## Decision

Retain fixed UTC sessions, both accepted subphase gates, completed-bar H4/H1/M15/M5 EMA8/21 ownership, and sleeve-local genealogy. Carry `STMR_XMONTH_ADMISSIBILITY_001` as the strongest Jan-Jul session/timeframe **research candidate**, with six sleeves executable and six observe-only.

Do **not** promote it over the authoritative January floor yet because exact historical replay parity is unavailable. April and July remain unresolved hostile months for later orthogonal system dimensions. Observe-only sleeves are not deleted; future volatility/structure layers may re-earn them with new causal information.


## Timeout recovery reconciliation

A message-delivery timeout interrupted a broader **Jan-Jul in-sample** per-sleeve timeframe-role diagnostic after months 1-3 had completed. Recovery resumed only months 4-7.

Final role-map diagnostic:
- net **+$519.02**;
- gross profit **$9,298.99**;
- gross loss **-$8,779.97**;
- PF **1.0591**;
- 7,879 trades;
- expected payoff **+$0.06587/trade**.

This is inferior to the simpler `STMR_XMONTH_ADMISSIBILITY_001` result (**+$780.42**, PF **1.1816**, much lower gross loss), so the interrupted role-map is **rejected**.

Exact timeout-era helpers/results are preserved in the Library recovery bundle:
`/xauusd-trading-bot/delta-A-alpha/recovery/2026-10-06/STMR_JANJUL_TIMEOUT_RECOVERY_20261006_v2.zip`

Bundle SHA-256:
`17dc185badc66b09140f02d11aaeacf44e94525da91b94569b66a9902a72ba31`

See append-only journal 0027 for provenance reconciliation.
