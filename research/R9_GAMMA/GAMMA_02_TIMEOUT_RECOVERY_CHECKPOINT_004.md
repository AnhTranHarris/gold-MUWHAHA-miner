# GAMMA-02 — Timeout Recovery Checkpoint 004

**Status:** RECOVERED / DURABLE / IDLE AT ATOMIC BOUNDARY  
**Recovered at:** 2026-10-07 after repeated UI message-delivery timeout  
**Pre-timeout GitHub head:** 3c8bcec3f1cb34337dffa400a81d92f3fefa1271  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Recovery audit

No GAMMA-02 worker process survived the timeout.

The UI timed out after several later experiments had already completed. Exact runtime artifacts were recovered and copied to persistent Library under:

`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/`

Completed recovered units include:
- NY16/17/18 subphase lifecycle integration;
- source-slot economics;
- causal M1 displacement quality map;
- conviction-depth screens for caps 64/96/128/192/256/384/512;
- source-priority/preemption test;
- turnover-efficiency test;
- time-decay conviction routing;
- continuous London/overlap markout stream.

## Continuous NY subphase lifecycle baseline

Recovered exact helper SHA-256:
`3a222847d8e29fe097fa133a469feb4b393252fce22c9be5188943a451d19926`

Recovered result SHA-256:
`a5ac9cf27cd407fca95787335cc96203e25e563f7d95231ed73656489c38ef89`

Selected rows:
- cap 64: +$24,897.92 / 4,466 trades / PF 3.7466 / +$5.575 expectancy;
- cap 128: +$48,595.02 / 7,547 / PF 4.0928 / +$6.439 expectancy;
- cap 256: +$88,783.65 / 11,050 / PF 4.5768 / +$8.035 expectancy.

## Conviction-depth breakthrough

The filter is strictly causal: favorable M1 displacement already achieved at entry. No future trade result is used as a feature.

Exact helper SHA-256:
`ebe6fb3fcf1b65b60a6e3d9355c289333f2d6fc6462274de5ca108ee646aed8d`

Key January research frontiers:

| Cap | Min16 | Min17 | Min18 | Net | Trades | PF | Exp/trade | Realized balance DD |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 64 | $0.50 | $1.50 | $2.00 | +$26,631.06 | 3,573 | 5.1086 | +$7.453 | $986.80 |
| 128 | $0.50 | $3.00 | $1.00 | +$50,019.16 | 6,512 | 5.0512 | +$7.681 | $1,730.15 |
| 192 | $1.00 | $6.00 | $0.00 | +$72,924.27 | 8,130 | 6.2359 | +$8.970 | $2,120.53 |
| 256 | $0.50 | $6.00 | $0.00 | +$93,178.58 | 9,212 | 6.8762 | +$10.115 | $2,120.53 |
| 384 | $0.00 | $6.00 | $0.00 | +$131,967.67 | 10,809 | 8.0354 | +$12.209 | $3,381.96 |
| 512 | $0.50 | $6.00 | $0.00 | **+$169,268.99** | **11,688** | **9.6805** | **+$14.482** | $4,274.25 |

High caps are research heat frontiers only.

The cap-512 source attribution:
- 16 UTC: +$62,582.80 / 4,139 trades / PF ~10.02 / +$15.12 expectancy;
- 17 UTC: +$89,134.03 / 1,210 / PF ~430 / +$73.66 expectancy;
- 18 UTC: +$17,552.16 / 6,339 / PF ~2.42 / +$2.77 expectancy.

## Exposure-efficient / time-decay results

Source preemption did not improve the cap-64 quality frontier.

A 16-UTC shortened lifecycle plus 17-UTC full campaign improved cap-64:
- +$27,228.80 / 3,550 trades / PF 5.912 / +$7.670 expectancy / DD ~$986.80.

Time-decay conviction routing further improved the cap-128 frontier:
- `lateBias + lateClean`: **+$54,805.38 / 5,767 trades / PF 6.800 / +$9.503 expectancy / DD ~$1,602.63**
- `lateBias + lateTight`: +$54,660.88 / 4,980 / PF 7.818 / +$10.976 expectancy / DD ~$1,424.28.

These filters remain causal: UTC subphase and already-realized favorable M1 displacement only.

## Community cross-check

Current community research remains hypothesis support rather than inherited performance:
- MetaQuotes safe-pyramiding work emphasizes adding only into favorable movement, coordinated stops, and aggregate heat.
- MetaQuotes trend/pyramiding research emphasizes heavy-tail trend capture.
- Community scalper reports support parallel specialists and limited add-ons, but are anecdotal and not treated as evidence.

## London / overlap discovery stream

A continuous full-January markout ledger for UTC 07-15 has completed.

Helper SHA-256:
`a237386cf53cf8aad8abd2f63040a7277a7ca1184e7a5c702da84e6b1b21a414`

Result SHA-256:
`5e5f474706e6f6ba816a1a701992f213c032e097ecc7f6273ad24fffd930f7d9`

This unit is diagnostic markout only. Its independent event PnL MUST NOT be added to the NY portfolio until a capped integrated replay is completed.

## Next atomic units

1. Audit the strongest London/overlap state/hour signatures from the completed continuous markout stream.
2. Build capped London/overlap specialists using only causal state/time/displacement variables.
3. Integrate those specialists with the NY time-decay frontier in one global position ledger.
4. Prefer quality improvements and slot efficiency before merely increasing global cap.
5. Exact full-tick equity-DD replay for finalists.
6. January R9-SYNTH exact monthly benchmark extraction.
7. Jan-Jul validation only after January architecture freezes.

No completed unit above should be rerun after another UI timeout.
