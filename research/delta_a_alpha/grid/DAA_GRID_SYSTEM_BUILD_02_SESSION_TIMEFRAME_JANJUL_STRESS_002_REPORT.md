# BUILD-02 Session/Timeframe Jan-Jul Stress 002

**Unit:** `DAA_GRID_SYSTEM_BUILD_02_SESSION_TIMEFRAME_JANJUL_STRESS_002`  
**Candidate:** `STMR_XMONTH_ADMISSIBILITY_001`  
**Parent accepted floor:** `STMR_SLEEVE_PHASE_001`  
**Status:** **STRONG CROSS-MONTH RESEARCH CANDIDATE — NOT PROMOTED**

## Provenance

The authoritative January result remains `STMR_SLEEVE_PHASE_001`: **+$877.78 / 1,518 trades / PF 1.602933**.

The exact portable January helper that produced that result was never durably committed. The Jan-Jul stress harness is therefore a clean-room reconstruction from committed session/timeframe semantics, source hashes, reports, ordered-tick Bid/Ask accounting and completed-bar-only state. Its January baseline is **+$779.00 / 1,724 trades / PF 1.46044**. It is useful for relative cross-month research but cannot silently replace the authoritative January floor.

## Frozen 12-sleeve stress

| Month | Net |
|---|---:|
| Jan | +$779.00 |
| Feb | -$254.58 |
| Mar | -$198.17 |
| Apr | -$231.64 |
| May | -$78.78 |
| Jun | +$31.61 |
| Jul | -$185.67 |
| **Jan-Jul** | **-$138.23** |

Aggregate: PF **0.9837**, 8,403 trades, expected payoff **-$0.01645**, gross loss **-$8,480.19**.

The January sleeve population therefore does not generalize as one executable cross-month set.

## Jan-Apr-frozen sleeve admissibility

Development rule: a semantic sleeve may own executable risk only if its frozen **Jan-Apr aggregate net is positive**. Otherwise it remains visible to the state system but becomes `OBSERVE_ONLY`.

Executable:
- `ASIA_LOWER_TAKEOVER`
- `LONDON_M5_TAKEOVER`
- `OVERLAP_LOWER_TAKEOVER`
- `LATE_ALIGNED_MOMENTUM`
- `LATE_MACRO_SPLIT_TRANSFER`
- `LATE_LOWER_TAKEOVER`

Observe-only:
- `ASIA_M15_DIVERGE_M5_RECLAIM`
- `LONDON_M5_RECLAIM`
- `OVERLAP_ALIGNED_COUNTERCROSS`
- `NY_LOWER_TRANSFER`
- `NY_LOWER_COUNTERCROSS`
- `LATE_M5_REJECTION`

Leave-one-development-month-out diagnostics supported the split. Directional FLIP tests of all six observe-only sleeves remained negative in Jan-Apr aggregate.

## Frozen May-Jul re-test

May-Jul had already been broadly inspected in earlier timeout-era sweeps, so this is **not pristine OOS**. The final sleeve-selection rule itself was nevertheless frozen from Jan-Apr only.

| Month | 12-sleeve baseline | Candidate |
|---|---:|---:|
| May | -$78.78 | **+$47.41** |
| Jun | +$31.61 | **+$184.81** |
| Jul | -$185.67 | **-$70.57** |
| **May-Jul** | **-$232.84** | **+$161.65** |

Candidate May-Jul PF: **1.2123** on 770 trades.

## Full Jan-Jul candidate

| Metric | Baseline | Candidate |
|---|---:|---:|
| Net | -$138.23 | **+$780.42** |
| Gross profit | $8,341.96 | $5,078.00 |
| Gross loss | -$8,480.19 | **-$4,297.58** |
| PF | 0.9837 | **1.1816** |
| Trades | 8,403 | 3,963 |
| Expected payoff | -$0.01645 | **+$0.19693** |
| Worst month equity DD | $282.50 | **$111.37** |
| Positive months | 2/7 | **5/7** |

Net improves **+$918.65**, gross loss falls **49.3%**, and trade retention is **47.2%**.

## Rejected session/timeframe refinements

Rejected after bounded testing:
- blanket DST session remapping;
- removing the accepted Asia/London subphase gates;
- global M5-fast / M15-fast / all-fast timeframe ownership;
- per-sleeve timeframe-speed mapping;
- directional FLIP of toxic sleeves;
- overlap-only 15:00–16:00 UTC restriction.

The message timeout interrupted a broader **Jan-Jul in-sample** sleeve/timeframe role-map. Recovery resumed only the missing months. It finished at **+$519.02 / PF 1.0591 / 7,879 trades**, inferior to the simpler admissibility candidate, so it is rejected.

## Scientific decision

Retain fixed UTC sessions, both accepted targeted subphase gates, completed-bar H4/H1/M15/M5 EMA8/21 role speed, and the six development-positive executable sleeves. Carry the six toxic sleeves as `OBSERVE_ONLY` so later orthogonal system layers may re-earn them with new causal information.

**Do not promote this candidate over the authoritative January floor until exact historical replay parity is recovered or the owner explicitly authorizes the clean-room Jan-Jul lineage as the new authority.**

April and July remain unresolved hostile months. They must not be optimized away using future outcomes.

Full runtime/result bundle:
`/xauusd-trading-bot/delta-A-alpha/recovery/2026-10-06/STMR_JANJUL_TIMEOUT_RECOVERY_20261006_v2.zip`  
SHA-256: `17dc185badc66b09140f02d11aaeacf44e94525da91b94569b66a9902a72ba31`.
