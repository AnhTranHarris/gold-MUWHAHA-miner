# DELTA 004 — Coinexx-Like Dukascopy Research Surface Report

**Status:** VERIFIED_DURABLE  
**Parent:** `DELTA_003_COINEXX_R9_PARITY_CALIBRATION`  
**Strategy optimization:** NONE  
**August 2026:** SEALED / NOT ACCESSED

## 1. Objective

Create a separately labeled modeled quote/execution surface that keeps Dukascopy's independent central price chronology while applying Coinexx-derived spread and execution economics.

This unit does not replace `DUKAS_NATIVE`, does not modify the canonical Dukascopy files, and does not produce a trading candidate.

## 2. Frozen spread profiles

Spread evidence comes only from the full January R9 REAL Coinexx logger.

Coinexx point = $0.01.

| Session | P50 | P75 | P90 |
|---|---:|---:|---:|
| OFF | 19 | 20 | 35 |
| LONDON | 19 | 20 | 34 |
| OVERLAP | 19 | 21 | 23 |
| NEW_YORK | 19 | 21 | 37 |

Default research surface: **P75**.

Reason:
- P75 is an observed Coinexx spread percentile;
- it is deliberately more conservative than the median P50 surface;
- it was frozen before the accepted DELTA_004 rerun;
- P90 remains a stress surface rather than the default.

No SYNTH outcome was used to create these values.

## 3. Quote transformation

For every Dukascopy tick:

1. timestamp and source ordinal are preserved;
2. the original Dukascopy Bid/Ask midpoint defines the independent central market path;
3. the current causal R9 session selects the frozen Coinexx spread;
4. modeled Bid is placed around the midpoint on the Coinexx $0.01 tick grid;
5. modeled Ask = modeled Bid + frozen spread.

Maximum midpoint quantization error is **$0.005**.

Therefore the modeled quote surface changes friction/quote geometry but does not choose direction from future information.

## 4. Cross-month warm-up

For February through July, replay prepends the final **90 minutes** of the preceding month's raw Dukascopy ticks as read-only state warm-up.

Purpose:
- completed-S1 state;
- completed-M5 ATR state;
- previous M5 close/true range.

Scoring begins at the current month's first tick. Warm-up ticks cannot open scored trades.

January remains an explicit cold start because December 2025 is outside the registered corpus.

## 5. Execution economics inherited from DELTA_003

The modeled surface uses:
- fixed 0.01 lot;
- $1 P/L for each $1 XAUUSD move at 0.01 lot;
- -$0.01 entry commission;
- -$0.01 exit commission;
- BUY entry Ask / exit Bid;
- SELL entry Bid / exit Ask;
- first-executable-quote protective stop behavior;
- R9 OnTick/lifecycle/rearm ordering from the verified Coinexx adapter.

## 6. Accepted P75 Jan-Jul result

### Aggregate

| Metric | R9 REAL | P75 modeled Dukascopy | Error |
|---|---:|---:|---:|
| Total trades | 236,647 | **234,417** | **-0.94%** |
| Winning trades | 102,385 | **104,294** | **+1.86%** |
| Gross profit | $30,180.23 | **$29,243.07** | **-3.11%** |
| Gross loss | -$80,465.51 | **-$78,244.86** | **-2.76% loss magnitude** |
| Net profit | -$50,285.28 | **-$49,001.79** | **-2.55% loss magnitude** |

Every preregistered aggregate tolerance passes.

## 7. Month-by-month P75 control

| Month | Trades | Wins | Gross Profit | Gross Loss | Net |
|---|---:|---:|---:|---:|---:|
| Jan | 33,373 | 14,768 | $3,943.27 | -$10,981.92 | -$7,038.65 |
| Feb | 33,711 | 15,210 | $6,004.07 | -$12,296.71 | -$6,292.64 |
| Mar | 38,065 | 17,143 | $5,824.28 | -$13,506.96 | -$7,682.68 |
| Apr | 32,543 | 14,650 | $3,853.01 | -$10,572.64 | -$6,719.63 |
| May | 32,505 | 14,170 | $3,382.50 | -$10,576.12 | -$7,193.62 |
| Jun | 33,610 | 15,143 | $3,606.06 | -$10,663.61 | -$7,057.55 |
| Jul | 30,610 | 13,210 | $2,629.88 | -$9,646.90 | -$7,017.02 |

Worst absolute monthly calibration errors:
- trade count: **5.54%**;
- winning trades: **11.97%**;
- gross profit: **16.68%**;
- gross-loss magnitude: **9.62%**;
- net-loss magnitude: **14.17%**.

All remain inside the preregistered monthly tolerances.

## 8. Sensitivity profiles

### P50 — median friction

Jan-Jul:
- trades: 233,778
- wins: 105,990
- gross profit: $29,640.11
- gross loss: -$75,168.08
- net: -$45,527.97

P50 is deliberately retained as the lower-friction sensitivity surface rather than the default.

### P90 — stress friction

Jan-Jul:
- trades: 40,699
- wins: 17,812
- gross profit: $5,189.30
- gross loss: -$14,433.40
- net: -$9,244.10

Many P90 session spreads exceed R9's $0.25 spread gate, so activity collapses. This is useful as a stress state, not as the primary research surface.

## 9. Why this matters

Before DELTA_004, unmodified R9 on native Dukascopy January produced only 289 trades because native Dukascopy spread is much wider than Coinexx.

After explicitly modeling Coinexx friction while preserving the independent Dukascopy central path, R9's seven-month activity and economics land close to the R9 REAL Coinexx baseline.

That indicates the laboratory can now separate three layers:

1. **strategy/state machine** — verified against R9;
2. **broker/execution friction** — calibrated from Coinexx REAL evidence;
3. **underlying market path** — independently supplied by Dukascopy.

This is the intended research architecture.

## 10. Surface names

The following labels are mandatory:

- `DUKAS_NATIVE` — untouched Dukascopy Bid/Ask.
- `DUKAS_COINEXX_LIKE_P50` — modeled median Coinexx friction.
- `DUKAS_COINEXX_LIKE_P75` — default modeled research surface.
- `DUKAS_COINEXX_LIKE_P90` — modeled stress friction.
- `COINEXX_PARITY` — preserved R9 REAL logger/report parity surface.

Results from these surfaces must never be silently mixed.

## 11. Canonical implementation

- `research/delta/lab/coinexx_like_surface.py`
- `research/delta/reference/DELTA_004_COINEXX_SPREAD_PROFILES.json`
- `research/delta/qa/DELTA_004_COINEXX_LIKE_DUKASCOPY_QA.py`
- `research/delta/checkpoints/DELTA_004_SURFACE_QA.json`

## 12. Readiness

DELTA now has:
- exact Coinexx R9 state/accounting parity;
- untouched native Dukascopy execution;
- a separate Coinexx-like modeled Dukascopy research surface;
- month isolation;
- prior-month state warm-up;
- P50/P75/P90 execution-cost sensitivity.

The lab is ready for the first owner-governed January candidate campaign.

No MQL5 candidate translation is authorized by this unit.
