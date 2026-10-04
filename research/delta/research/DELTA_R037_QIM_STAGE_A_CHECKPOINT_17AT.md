# DELTA R037 — Queue Imbalance / Microprice Stage-A Screen — Checkpoint 17AT

**Status:** COMPLETE / PREDICTIVE EDGE PRESENT / NO EXECUTABLE SURVIVOR  
**Unit:** R037_QUEUE_IMBALANCE_MICROPRICE_STAGE_A_SCREEN  
**Parent:** R037_OFM_STAGE_A_SCREEN_CHECKPOINT_17AS  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Research question

Can causal best-bid/best-ask quoted-volume imbalance provide a high-frequency XAUUSD entry edge that survives the frozen DELTA P75 spread/cost and 30-second initial-hold execution semantics?

Queue imbalance is reconstructed exactly as:

`I = (bid_volume - ask_volume) / (bid_volume + ask_volume)`

The three preregistered event thresholds are fixed at `|I| >= 0.25 / 0.50 / 0.75`. A new proposal requires a causal transition into the strong-imbalance state or an opposite-sign strong regime. No XAUUSD threshold fitting or exit retuning was performed.

## Source basis

The family is grounded in:
- Gould & Bonart: queue imbalance predicts the direction of the next mid-price movement;
- Stoikov: microprice adjusts mid-price using spread and bid/ask imbalance;
- Cont, Kukanov & Stoikov: short-horizon price changes are strongly linked to best-bid/ask order-flow imbalance.

## Durability / execution

- prereg commit: `c2390a95eebf1c60c0a75f0d524916948211286a`
- producer commit: `3f11c0bfc632a6c018dc6e28304e2c4e51adfd7a`
- producer blob: `daadafa78b941bfda18daaa277b40600bf942495`
- producer SHA-256: `37f08a0df5f5a1777ddc53ed1487608b63dde457e528cd5562fd666143e4f251`
- canonical January SHA verified
- Stage-A ticks: **4,205,709**
- all 4,205,709 ticks contain valid positive bid+ask quoted volume
- exact local Git blob matched the committed producer before official compute
- Python compilation passed
- official process hard timeout: **120 seconds**
- atomic result output: temp file + flush + fsync + `os.replace`
- official raw result SHA-256: `c7d4e7bd85dba68f40b8b0df340889d7fa4c8e7bc1cedaa0646f22cc1d8b62e0`

## Predictive result

Queue imbalance contains real short-horizon directional information.

| Profile | Events | Next nonzero mid accuracy | 250ms | 1s | 5s |
|---|---:|---:|---:|---:|---:|
| C01_QI_025 | 338,904 | **56.95%** | 56.45% | 54.80% | 52.02% |
| C02_QI_050 | 119,475 | **55.79%** | 55.39% | 54.22% | 51.34% |
| C03_QI_075 | 26,123 | **57.00%** | 56.92% | 55.57% | 51.81% |

The signal decays with horizon, exactly as a microstructure signal should.

## Executable Stage-A economics

| Profile | Trades | Days | Official wins | Gross profit | Gross loss | Direct net |
|---|---:|---:|---:|---:|---:|---:|
| C01_QI_025 | 85,749 | 14 | 42,084 | +$9,092.92 | -$23,917.78 | **-$15,682.35** |
| C02_QI_050 | 35,100 | 14 | 16,574 | +$3,501.00 | -$10,230.52 | **-$7,080.52** |
| C03_QI_075 | 10,190 | 14 | 4,796 | +$1,026.63 | -$2,991.59 | **-$2,066.86** |

All three profiles pass supply/day coverage and predictive-direction gates, but fail executable economics by a very large margin.

## Interpretation

This result separates **information edge** from **tradeable edge**.

Raw queue imbalance predicts the next quote move above chance, but the effect is too short-lived and too dense to overcome executable spread, commission, stop behavior and the frozen 30-second lifecycle. Even the strongest fixed threshold still generates more than ten thousand Stage-A trades and loses more than $2,000.

Therefore the correct decision is not to tune QIM thresholds, sessions, sides or exits on the same window.

## Decision

**RETIRE_QIM_STAGE_A_NO_EXECUTABLE_SURVIVOR.**

Do not:
- threshold-sweep QIM on Stage-A;
- rescue with session/side/weekday filters;
- retune the 30-second execution;
- access August;
- begin MQL5.

The predictive result remains valuable research evidence: microstructure state contains short-horizon information, but raw QIM is not an economically valid standalone entry trigger under DELTA execution.

## Next

`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

Prioritize a sparse causal **state-transition** mechanism rather than another dense directional threshold.
