# GAMMA-02 — February Unchanged January-Milestone Replay 132A

**Status:** COMPLETE / BASELINE ONLY / NO FEBRUARY TUNING  
**January fallback:** `carson/r9-gamma-02-jan-grid-milestone` remains untouched  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Objective

Replay the frozen January milestone unchanged on February 2026 Dukascopy ticks and judge it against exact February R9 SYNTH daily, weekly, and monthly performance. No February-specific parameter search, rule selection, or calendar-date logic is permitted in this unit.

## QA

February Dukascopy SHA-256:

`ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`

R9 SYNTH workbook SHA-256:

`e5fcf4d6879193fac88e7a8e101db1111d59e1a7f5abfb793c970b06cfce7cc7`

The January architecture was preserved exactly. The only cross-month correction is an explicit target gate `START <= entry_timestamp < END` on supplemental heartbeat/cold-start sleeves, because February state preparation legitimately includes a January warmup window. This prevents the previously documented warmup-leakage failure mode. The target gate is QA, not a trading feature.

## Exact February R9 SYNTH benchmark

- net: **+$66,213.65**
- trades: **33,523**
- gross loss: **$-2,031.42**
- PF: **33.5948**
- win rate: **88.30%**
- expectancy: **+$1.9752/trade**
- average hold: **16.18s**
- closed-trade balance DD: **~$2.19**

## Primary unchanged transfer — aggressive January fallback `L35/C703`

- net: **+$48,224.26** = **72.83% of R9 SYNTH February**
- trades: **27,484** = **81.99% of SYNTH velocity**
- gross loss: **$-17,728.59**
- PF: **3.7201**
- win: **89.75%**
- expectancy: **+$1.7546/trade**
- balance DD: **~$9,028.52**
- full-tick equity DD: **~$19,449.55**
- max open: **703**
- positive days: **10/20**
- days beating same-date R9 SYNTH: **6/20**
- positive weeks: **4/4**
- weeks beating same-week R9 SYNTH: **0/4**

## Alternative frozen January operating points

| Frozen point | Net | Trades | Gross loss | PF | Win | Balance DD | Equity DD |
|---|---:|---:|---:|---:|---:|---:|---:|
| Full 131D | $44,097.94 | 27,819 | $-22,043.31 | 3.00 | 89.24% | $13,343 | $19,450 |
| **Balanced L35/C640** | **$46,343.38** | 26,025 | **$-17,728.59** | **3.61** | 89.18% | **$9,029** | **$17,725** |
| Aggressive L35/C703 | **$48,224.26** | **27,484** | $-17,728.59 | **3.72** | **89.75%** | $9,029 | $19,450 |

The layer-35 refinement transfers positively: both L35 variants outperform the unprotected 131D replay on net, gross loss, PF and balance DD.

## Week-by-week comparison

| Week | R9 SYNTH | L35/C703 | Capture |
|---|---:|---:|---:|
| 2026-W06 | $34,837.88 | $26,132.20 | 75.0% |
| 2026-W07 | $13,876.89 | $11,321.93 | 81.6% |
| 2026-W08 | $8,320.42 | $2,718.60 | 32.7% |
| 2026-W09 | $9,178.46 | $8,051.53 | 87.7% |

All four weeks remain profitable, but none reaches its same-week R9 SYNTH benchmark. W08 is the clearest weakness.

## Day-by-day comparison

| Date | R9 SYNTH | L35/C703 | Ratio | Verdict |
|---|---:|---:|---:|---|
| 2026-02-02 | $11,615.25 | $14,707.67 | 1.27x | BEAT |
| 2026-02-03 | $6,238.20 | $0.00 | 0.00x | NO TRADE |
| 2026-02-04 | $5,151.51 | $11,424.53 | 2.22x | BEAT |
| 2026-02-05 | $6,983.99 | $0.00 | 0.00x | NO TRADE |
| 2026-02-06 | $4,848.93 | $0.00 | 0.00x | NO TRADE |
| 2026-02-09 | $3,150.14 | $7,937.34 | 2.52x | BEAT |
| 2026-02-10 | $2,670.20 | $607.00 | 0.23x | POSITIVE |
| 2026-02-11 | $2,267.85 | $2,836.84 | 1.25x | BEAT |
| 2026-02-12 | $2,779.30 | $-59.25 | -0.02x | NEGATIVE |
| 2026-02-13 | $3,009.40 | $0.00 | 0.00x | NO TRADE |
| 2026-02-16 | $1,074.68 | $0.00 | 0.00x | NO TRADE |
| 2026-02-17 | $2,683.36 | $-24.39 | -0.01x | NEGATIVE |
| 2026-02-18 | $1,429.26 | $0.00 | 0.00x | NO TRADE |
| 2026-02-19 | $1,385.37 | $1,282.54 | 0.93x | POSITIVE |
| 2026-02-20 | $1,747.75 | $1,460.45 | 0.84x | POSITIVE |
| 2026-02-23 | $1,873.92 | $-1,418.60 | -0.76x | NEGATIVE |
| 2026-02-24 | $2,141.97 | $-70.55 | -0.03x | NEGATIVE |
| 2026-02-25 | $1,712.59 | $7,513.31 | 4.39x | BEAT |
| 2026-02-26 | $1,867.47 | $174.32 | 0.09x | POSITIVE |
| 2026-02-27 | $1,582.51 | $1,853.05 | 1.17x | BEAT |


## Interpretation

This is a **good transfer, not a January-level domination result**.

The unchanged January architecture recovers **72.83%** of February R9 SYNTH net while retaining **81.99%** of its trade count. Its win rate (89.75%) is slightly above R9 SYNTH (88.30%), and expectancy retains **88.83%** of SYNTH expectancy.

The problem is reliability distribution and loss quality. Six R9-SYNTH trading days receive no trades, four candidate trading days are negative, and gross loss is approximately **8.73x** R9 SYNTH. February therefore exposes states that the January session/router architecture does not yet own cleanly.

This baseline must be preserved unchanged before any February adaptation. It is evidence that January generalized materially, but not enough to declare the architecture cross-month complete.

## Next state

No February adaptation has been run in this checkpoint. Owner decision is required: either accept ~73% monthly SYNTH capture as sufficient transfer and proceed to March unchanged replay, or open February adaptation research while keeping the frozen January fallback intact.