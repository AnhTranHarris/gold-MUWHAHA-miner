# DELTA R014 — Exact Rounded R010 Jan–Jul Validation

**Status:** MULTI-MONTH ROBUST REFINEMENT CANDIDATE / NOT PROMOTED  
**Parent:** `DELTA_004_COINEXX_LIKE_DUKASCOPY_RESEARCH_SURFACE`  
**Scope:** ENTRY + INITIAL-HOLD  
**Surface:** P75 DST-aware  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Canonical rule

```
I250 <= -0.55 OR H1NetATR > 0.35
```

- I250: signed Bid/Ask impulse over prior 250 ms, oriented to the R9 intended side.
- H1NetATR: signed net displacement over the last 3 completed H1 bars / completed H1 ATR(14), oriented to the intended side.
- True: flip entry side, assign reversal ownership, suppress generic opposite-side same-minute R9 rearm after owned exit.
- Ownership resets next M1 boundary.

## Exact month results

| Month | Net improvement | GL improvement | Trade retention | Winner retention |
|---|---:|---:|---:|---:|
| Jan | 15.31% | 15.20% | 86.38% | 88.81% |
| Feb | 12.04% | 12.98% | 86.60% | 86.52% |
| Mar | 12.48% | 13.83% | 86.02% | 85.89% |
| Apr | 9.67% | 11.82% | 87.48% | 87.15% |
| May | 16.74% | 15.24% | 87.13% | 91.15% |
| Jun | 14.04% | 13.79% | 86.68% | 87.77% |
| Jul | 9.91% | 11.44% | 88.79% | 89.59% |

Every month improves net loss and month-local balance drawdown.

## Aggregate Jan–Jul

R9 P75:
- trades 234,417
- winners 103,097
- GP +$29,243.07
- GL -$78,244.86
- net -$49,001.79
- aggregate win rate 43.98%

Exact rounded R010:
- trades 203,864
- winners 90,751
- GP +$25,008.31
- GL -$67,676.50
- net -$42,668.19
- aggregate win rate 44.52%

Changes:
- net-loss improvement **12.93%**
- GL improvement **13.51%**
- trade retention **86.97%**
- winner retention **88.02%**

## Interpretation

The ownership mechanism is temporally robust across the seven tested months.

The discovery Stage-A ~21% result was optimistic. The exact Jan–Jul aggregate supports a more conservative ~13% effect.

This is meaningful but below:
- the 30% high-value scoped target;
- the 80% promotion target.

Native-spread sensitivity from R010 remains a required failure.

No promotion.  
No metric lock.  
No MQL5.

## Next experiment

Preregister confidence-tiered ownership:

- moderate adverse/overextension condition -> flip;
- extreme adverse/overextension condition -> skip;
- otherwise keep R9 side.

The old timed-out confidence-tier run is ignored and cannot seed result choices.

## Provenance

- exact Jan–Jul aggregate: `26adb8ae896c526e572e44c851f64560d0dd5bc2331163143aa485491ea79ba6`
- exact January script: `7f212f9c5668a3a6e6cfa343ae94679347ac2e42961d5767bc737575ed462804`
- exact month script: `d5a043cbd50a675b69cd372755b30dbe3251fc156e88702a196bd03f600b1488`

Drive:
https://docs.google.com/document/d/157f0lIkp6RxIWELgpKxUwSIsNNJQT7d9ZMzYGyY-zm0/edit
