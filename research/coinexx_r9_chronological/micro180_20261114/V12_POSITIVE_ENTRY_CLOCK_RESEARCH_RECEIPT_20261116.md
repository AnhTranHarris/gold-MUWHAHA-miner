# Micro180 positive-cycle causal entry rebuild — actual implementation

**Research entry checkpoint 2026-11-16. No broker/native EA modifications.**

## Original target population

The existing R9-SYNTH→REAL Coinexx mapped reference retains 272,352 original
trade legs and $360,693.05 original synthetic MT5 net. The strict positive
complete-cycle target requires BOTH original R9 cycle net >0 and mapped
Coinexx quote cycle net >0 with entry/exit quote lags <=2000ms.

- A: 66,870 positive single-leg cycles
- B: 29,215 positive favorable-first/opposite cycles
- C: 9,900 positive recovery cycles with adverse first-leg precursor
- **105,985 first-leg + 39,115 second-leg = 145,100 positive-cycle entry targets**

Family C's first losing leg remains a positive COMPLETE-cycle precursor, not
falsely relabelled as an individually winning position. The merged source
maps to the first actual Coinexx quote after the NEXT original full-second
boundary; this is not the synthetic event-time executable fill.

## Actual entry-cause observation, later source segment

On independent source REAL TickLogger part01 rows 900001..1800000, at observed
positive R9 teacher ENTRY seconds:

| Family leg | observed targets | as-of M5/spread gate open | REAL 10s S1 quality passes | REAL entry bracket crossed |
|---|---:|---:|---:|---:|
| A first | 785 | 783 | 109 | 645 |
| B first | 289 | 288 | 26 | 147 |
| C first | 90 | 90 | 5 | 48 |
| B second | 285 | 285 | 29 | 105 |
| C second | 88 | 87 | 11 | 42 |

R9 synthetic entry-second behavior is not reproduced merely by imposing its
strict ten-second S1 Boolean rule on REAL quotes. The implemented alternative
uses a continuous causal market-state predictor: as-of completed S1 history,
5s/15s baskets, spread-aware minute bracket, historical 30s/60s/180s/300s
returns, acceleration, efficiency, session and completed M5 ATR. The historical
future family outcome is NEVER passed into an entry decision.

## REAL quote forward replay

The two positive-cycle hazard models were trained/frozen using an earlier
900,000 source quotes; the distinct forward sample covered rows 900001–1800000.
Execution uses an actual observed later source Bid/Ask quote. The second head
is eligible only AFTER the simulator's OWN first-leg stop/exit.

| Forward source metric | first leg | second leg after OWN first exit |
|---|---:|---:|
| Positive historical references present | 1,182 | 381 |
| Independently generated entries | 2,479 | 280 |
| Correct reference minute and side | 790 | 67 |
| Within mapped ±2000ms and ±5 cents | 181 | 12 |
| Exact mapped quote millisecond AND entry cents | 124 | 9 |

## Validation-frozen synthetic-to-real clock adjustment

On earlier validation data, the fixed 2s after-signal quote schedule was
selected instead of the original 1s next-quote schedule. On later data:
- Correct side/minute: 790 (1s) versus 787 (2s)
- Near-exact mapped time ±2000ms and price ±5c: 181 versus **196**
- Exact mapped timestamp and quote cents: **124** versus 113

A benefits more from the 2s schedule, B/C from quicker entry. The clock is
a measured trade-off. Additional phase-only and outcome-trained as-of meta
selection variants did not improve the prespecified earlier validation
objective; neither was promoted into the new router.

## Actual GitHub implementation and resumable continuation

New branch: carson/micro180-positive-cycle-entry-clock-20261116.

- v12_positive_cycle_targets.py: exact offline A/B/C winner-only supervision.
- v12_positive_clock_router.py: independent causal realtime quote entry
  controller, custom multi-horizon clock, frozen two-model gate, observable
  later Bid/Ask quote execution and own-portfolio opposite rearm. No inherited
  R9 entry method or historical R9 event input.
- run_v12_positive_coinexx_chunks.py: streams existing original REAL TickLogger
  CSV.gz parts; handles source display timestamps through source time_msc;
  bounded 200,000 quote rows per invocation; compressed candidate-only entry
  receipts, resumable own-model state checkpoints. No raw source reconstruction.
- test_v12_positive_clock_router.py + GitHub Actions: fixture contracts for
  future quote avoidance, side/price, positive A/B/C source labels, source order,
  rejection of SYNTH logs and resumability.

Frozen models + local experiment code + precise real-source forward results,
ZIP total 237,436 bytes, uploaded and verified in primary TRADING_RESEARCH:
https://drive.google.com/file/d/1o-XFHfdAylKwDtZjpW0LJ7Yh9kt6EEHB/view

The remaining ORIGINAL TickLogger source parts are not accessible in this
current runtime. No rebuilt raw data, additional broker fees or altered
original R9 economics. This branch does not claim full nine-month replay,
MT5 native compilation, broker fills, or positive independent trading PnL.
The next measurable gate is complete 145,100-target A/B/C entry concordance
using existing original source parts, processed in smaller source chunks.
