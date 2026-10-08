# GAMMA-02 — January Session-Firm Daily/Weekly Breakthrough 131D

**Status:** COMPLETE / DURABLE PYTHON RESEARCH CHECKPOINT  
**Parent:** `GAMMA02_DYNAMIC_RENEWAL_WATCHDOG_119`  
**Selected frontier:** `WD119_COVERAGE_LEAN4_COLD64`  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Owner objective

January is being rebuilt as an unknown-deployment-date, firm-style system rather than a monthly headline curve. Every January trading day and ISO week is scored against the exact January R9 SYNTH period. Month/week/day labels are forbidden as execution features.

The research process deliberately generated many distinct hypotheses, then tested them on ordered January ticks. “Hallucinate” in the owner instruction means aggressive hypothesis generation; no hypothesis becomes evidence until replayed and persisted.

## Timeout recovery / reproducibility

The prior UI timed out after creating a causal earlier-session coverage helper and result in Library but before promotion. Recovery followed the durable-state protocol:

1. GitHub cursor was read first.
2. Library was searched for artifacts newer than the cursor.
3. The recovered helper/result were materialized.
4. The exact coverage helper was rerun.
5. The rerun result was byte-identical to the saved Library JSON.

Recovered coverage result SHA-256:

`e685ebd2a9a5d23615439b57a0daaa8fcd4549e7dd5018f4bd85455d3851e3ad`

This checkpoint then continued only the smallest missing January unit.

## Exact benchmark

R9 SYNTH January:

- net: **+$41,520.82**
- trades: **27,980**
- gross loss: **-$1,827.87**
- PF: **23.7154**
- win rate: **87.09%**
- expectancy: **+$1.48395/trade**

January raw market SHA-256:

`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

## Breakthrough architecture

The architecture is now an asymmetric session portfolio rather than one universal grid.

### 1. Watchdog-119 — NY/high-renewal owner

The refined Watchdog remains untouched as the parent high-renewal specialist. Explicit same-tick scaling inside this known grid is preserved.

### 2. Recovered earlier-session causal coverage

The recovered V3 sleeve exploits completed HTF state + 10-minute subphase cells across UTC source-hours 9/11/12/13/14/15/16. It is complementary to Watchdog and had zero cross-sleeve overlap in its recovered exact replay.

### 3. Cold-start/source12 microgrid

A small `source12` desk uses:

- final two 10-minute bins,
- completed H4/H1/M15/M5 = `+,+,+,-`,
- causal prior-60-second quote density <=450,
- 50 ms event interval,
- cap 64.

It is retained specifically because cap64 is the best risk/reliability point that pushes W01 above R9 SYNTH without materially inflating portfolio heat.

### 4. Four lean state/session desks

The broad rescue portfolio was rejected. Only four lower-loss state cells survive:

- **ASIA02_CONT:** UTC 02, H4/H1/M15/M5 `+,+,-,-`, long; step 50; cap64; TP/SL/hold = 12/4/300s raw geometry.
- **LONDON10_ROTATE_LONG:** UTC 10, `+,-,-,-`, long; step50; cap16; 120s lifecycle.
- **OVERLAP13_SHORT:** UTC 13, `+,-,+,-`, short; step50; cap16; 12/4/300s.
- **LATE21_LONG:** UTC 21, `+,-,-,-`, long; step50; cap32; 120s lifecycle.

Supplemental desks are globally de-duplicated to at most one new physical ticket per market tick. The pre-existing explicit Watchdog grid scaling is not silently collapsed.

## Selected firm-style frontier

`WD119_COVERAGE_LEAN4_COLD64`

- net: **+$207,653.32**
- trades: **88,958**
- gross profit: **+$212,728.42**
- gross loss: **$-5,075.10**
- PF: **41.9161**
- win rate: **97.96%**
- expectancy: **+$2.3343/trade**
- balance DD: **~$818.71**
- full-tick equity DD: **~$62,763.84**
- max open: **703**
- positive R9-SYNTH trading days: **21/21**
- days beating same-date R9 SYNTH: **13/21**
- positive ISO weeks: **5/5**
- weeks beating same-week R9 SYNTH: **5/5**

The candidate produces about **5.00×** R9 SYNTH January net. Excluding January 30 entirely, it still produces **$67,633.55** versus **$34,628.80** R9 SYNTH, or **1.95×**. Therefore the January result is no longer solely dependent on the January-30 Watchdog event, although that event still dominates full-month dollars and heat.

## Week-by-week firm comparison

| ISO week | R9 SYNTH net | Candidate net | Capture | Candidate trades | Verdict |
|---|---:|---:|---:|---:|---|
| 2026-W01 | $1,027.95 | **$1,217.78** | **1.18×** | 95 | PASS |
| 2026-W02 | $5,332.33 | **$8,091.31** | **1.52×** | 2,524 | PASS |
| 2026-W03 | $5,817.38 | **$18,316.62** | **3.15×** | 2,639 | PASS |
| 2026-W04 | $7,692.42 | **$16,718.60** | **2.17×** | 2,576 | PASS |
| 2026-W05 | $21,650.74 | **$163,309.01** | **7.54×** | 81,124 | PASS |

This is the first current January architecture to beat R9 SYNTH net in **all five January ISO weeks** while retaining Watchdog-119.

## Day-by-day comparison

| Date | R9 SYNTH | Candidate | Ratio | Daily verdict |
|---|---:|---:|---:|---|
| 2026-01-02 | $1,027.95 | $1,217.78 | 1.18× | PASS |
| 2026-01-05 | $1,304.58 | $1,706.81 | 1.31× | PASS |
| 2026-01-06 | $906.38 | $959.61 | 1.06× | PASS |
| 2026-01-07 | $1,163.88 | $549.88 | 0.47× | below |
| 2026-01-08 | $1,052.15 | $56.01 | 0.05× | below |
| 2026-01-09 | $905.34 | $4,819.00 | 5.32× | PASS |
| 2026-01-12 | $1,287.71 | $7,343.82 | 5.70× | PASS |
| 2026-01-13 | $1,183.15 | $10,074.92 | 8.52× | PASS |
| 2026-01-14 | $1,110.96 | $12.20 | 0.01× | below |
| 2026-01-15 | $1,110.54 | $353.78 | 0.32× | below |
| 2026-01-16 | $1,125.02 | $531.90 | 0.47× | below |
| 2026-01-19 | $743.89 | $5,302.46 | 7.13× | PASS |
| 2026-01-20 | $1,009.98 | $2,533.76 | 2.51× | PASS |
| 2026-01-21 | $2,612.38 | $493.29 | 0.19× | below |
| 2026-01-22 | $1,589.48 | $6,748.55 | 4.25× | PASS |
| 2026-01-23 | $1,736.69 | $1,640.54 | 0.94× | below |
| 2026-01-26 | $2,979.62 | $12,609.60 | 4.23× | PASS |
| 2026-01-27 | $2,554.57 | $3,727.50 | 1.46× | PASS |
| 2026-01-28 | $3,502.79 | $4,065.41 | 1.16× | PASS |
| 2026-01-29 | $5,721.74 | $2,886.73 | 0.50× | below |
| 2026-01-30 | $6,892.02 | $140,019.77 | 20.32× | PASS |

The system is positive on **all 21 R9-SYNTH trading days**, but it does not yet beat SYNTH every day. The weakest relative days remain January 8, 14, 15, 16, 21, 23, and 29. Those should be treated as diagnostic states, not as permission to introduce calendar-date rules.

## Rejected hypotheses in this pass

- Broad Asia continuation ladder: too much turnover/loss for roughly PF 1.09.
- London07 rotation: positive but gross-loss expensive.
- Overlap16 long: negative January 2 and gross-loss expensive.
- Brute rescue portfolio: reached 21/21 positive days but bought coverage with too much mediocre inventory.
- High-cap firm-scout variants: higher headline net but materially worse gross loss/heat.
- Using a day/week profit target as an entry feature: forbidden; R9 SYNTH daily/weekly values are evaluation benchmarks only.

## Key interpretation

The owner's memory of a session/hourly-grid concept is supported by the January experiment. Different XAUUSD trading phases require different mechanisms:

`Asia state continuation → London/overlap state cells → NY Watchdog high-renewal harvesting → late-session continuation`

A single universal grid is inferior to state/session ownership.

However, the principal unresolved risk has now become even clearer:

**full-tick equity DD remains ~$62,763.84 because Watchdog W05 synchronized inventory is unchanged.**

Adding more session coverage is no longer the highest-value next move. The next breakthrough should increase **profit per unit of Watchdog heat**, not simply open more positions.

## Next atomic research unit

`GAMMA_02_JAN_WD119_PROFIT_PER_HEAT_AND_VIRTUAL_RENEWAL_131E`

Priority hypotheses:

1. **Virtual renewal / physical runner:** continue observing the Watchdog renewal ladder but allow one physical ticket to harvest several virtual levels when persistence is earned.
2. **Causal heat gear:** layer30/35/full Watchdog capacity selected by pre-entry renewal density/state quality, never by future P/L.
3. **Earned tranche capacity:** additional physical grid layers only after already-realized profit finances the extra heat.
4. **Persistence-to-runner transition:** convert selected grid children from repeated close/reopen harvesting into a ratcheted runner when favorable renewal continues.
5. Preserve the 131D daily/weekly session architecture as a regression gate: **21/21 positive days and 5/5 weeks beating R9 SYNTH must not be casually destroyed.**

## Durable hashes

Compact artifact SHA-256:

`fc5d1ea59eeefa5720100e36352e3e7445e7c99aebdc5083bc4ba1dce6d4d42f`

Exact helper/dependency hashes are embedded in the compact JSON artifact.
