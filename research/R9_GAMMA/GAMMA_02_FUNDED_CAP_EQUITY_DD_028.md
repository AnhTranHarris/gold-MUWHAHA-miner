# GAMMA-02 — Funded Cap Exact Equity DD 028

**Status:** COMPLETE / FULL JANUARY TICK-MARKED EQUITY QA  
**Parent:** GAMMA_02_FUNDED_CAP_UTILIZATION_027.md  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Method

For each accepted funded-cap trade, the replay reconstructs:
- exact entry tick and exact exit tick;
- trade direction from the already-earned session/state router;
- executable Ask entry / Bid liquidation for longs;
- executable Bid entry / Ask liquidation for shorts;
- the existing $0.02 modeled roundtrip cost.

Portfolio equity is marked on **every ordered January Dukascopy tick**. Open-position floating P/L is aggregated exactly by long/short count and entry-price sums.

All accepted trade P/Ls reproduce the event-ledger P/L exactly.

## Results on a $100,000 research account

| Funded ceiling | Net | Trades | Balance DD | Exact equity DD | Equity DD % of peak total equity | Minimum total equity |
|---:|---:|---:|---:|---:|---:|---:|
| 128 | +$83,897.56 | 14,107 | $3,167.52 | **$10,712.77** | 5.79% | $98,366.51 |
| 192 | +$117,400.75 | 17,647 | $3,328.20 | **$15,701.00** | 7.19% | $98,366.51 |
| 256 | **+$154,538.37** | **24,646** | $4,179.75 | **$17,547.11** | 6.86% | **$98,366.51** |

The worst equity-DD interval is common to all three tested funded ceilings:
- peak: **2026-01-30 17:55:54.148 UTC**
- trough: **2026-01-30 18:05:07.727 UTC**

The minimum total equity occurs earlier:
- **$98,366.51**
- 2026-01-05 13:30:36.581 UTC

## Interpretation

The previously reported realized balance DD materially understates intratrade heat.

The funded-cap architecture remains strongly profitable in January, but future risk optimization must use tick-marked equity DD rather than closed-trade DD.

The 256-cap frontier does NOT imply a 17.5% drawdown on the original $100K account. At its worst peak-to-trough equity event the account had already grown substantially; the exact peak-relative DD is about **6.86%**. However, the absolute $17.5K swing is operationally important and cannot be hidden.

## Scientific decision

- KEEP the profit-funded capacity mechanism as a major January breakthrough.
- DO NOT promote high-cap research frontiers based only on balance DD.
- REQUIRE exact equity-DD for all later capacity/risk finalists.
- NEXT extract the exact January-only R9 SYNTH benchmark so the hard goal comparison is no longer based on seven-month averages.
- After that, use the equity curve to target slot-turnover/profit-lock improvements without sacrificing the high-expectancy campaign inventory.

## Exact artifacts

GitHub:
- research/R9_GAMMA/helpers/gamma02_funded_cap_equity_dd_028.py
- research/R9_GAMMA/artifacts/gamma02_funded_cap_equity_dd_028.json

SHA-256:
- helper: bb83dd19b610e7d77d9dfac658aef01ee8cf4f7524dbef1919b3a7b5efd0c308
- result: 1b3dcb8555527bfda9ff978d9199a89565c2bbb739e556b8950f9ed3146f7c51

R9 SYNTH remains the hard target.
