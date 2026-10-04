# DELTA R037 — Order-Flow Imbalance / Microstructure Stage-A Screen — Checkpoint 17AS

**Status:** COMPLETE / NO SURVIVOR / PUBLISHED-THRESHOLD FAMILY RETIRED  
**Unit:** R037_ORDER_FLOW_IMBALANCE_MOMENTUM_STAGE_A_SCREEN  
**Parent:** R037_PBQ_STAGE_A_SCREEN_CHECKPOINT_17AR  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Research question

Can the source-defined M1 order-flow stack from MetaQuotes Market Microstructure Parts 4–6 provide viable short-horizon XAUUSD entries under the frozen DELTA 30-second execution semantics without XAUUSD threshold calibration?

The reconstructed features were:
- bipower-variation jump intensity;
- enhanced OHLC microstructure noise;
- signed volume-weighted flow imbalance;
- late-minus-early smart-money index;
- 10-minus-30-bar flow momentum;
- the Part-6 flow-confidence gate.

Tick volume was reconstructed causally as the number of canonical source ticks in each completed M1 bar.

## Durability / execution

- prereg commit: `b6eb77574ac32a151c371a4b4774b5946c3a300e`
- producer commit: `e27e9f9136d110f7f0f8ad41899bcda62d3db797`
- producer blob: `7aa5755960e1f262667f00b17e93a162b39deff2`
- producer file SHA-256: `f6dea91c48d55eb08546d5d02b80d24332368fb0b8ff81d839c5ebb989394574`
- canonical January SHA verified
- Stage-A ticks: **4,205,709**
- local producer Git blob exactly matched the committed blob before execution
- Python compilation passed
- hard process timeout: **120 seconds**
- atomic result output: temp file + flush + fsync + os.replace
- official raw result SHA-256: `c7d07ce28fbd515674e733282c4191934a6d310cc931d158fe1ec252fd906cd0`

## Feature diagnostics

Across 15,090 usable completed M1 feature bars:

| Feature | P10 | P50 | P90 |
|---|---:|---:|---:|
| Enhanced noise | 0.5717 | 0.6743 | 0.7794 |
| Jump intensity | 0.0000 | 0.0111 | 0.0222 |
| Flow imbalance | -0.0579 | 0.0269 | 0.1143 |
| Smart-money index | -0.4928 | -0.0041 | 0.4749 |
| Flow momentum | -0.2152 | -0.0018 | 0.2164 |
| Flow confidence | 0.0000 | 0.5047 | 0.7139 |

There were 5,882 confidence-eligible bars and 4,735 Part-5 clean-noise bars.

This matters because the published flow thresholds are not grossly outside the observed XAUUSD feature distribution. Failure cannot be dismissed simply as “thresholds never fire.”

## Stage-A results

| Profile | Trades | Days | Official wins | Gross profit | Gross loss | Direct net |
|---|---:|---:|---:|---:|---:|---:|
| C01_SOURCE_FLOW_SMI | 846 | 11 | 376 | +$93.20 | -$263.07 | **-$169.87** |
| C02_FLOW_SMI_MOMENTUM | 451 | 11 | 205 | +$43.34 | -$135.93 | **-$92.59** |
| C03_PART5_CLEAN_IMBALANCE | 1,157 | 13 | 491 | +$121.91 | -$380.29 | **-$258.38** |

All three profiles pass supply and coverage but fail the economic gate materially.

## Interpretation

Adding sign-aligned flow momentum substantially reduces activity and loss versus the full source flow+SMI profile, but it remains far from the `-$1` ordinary-screen gate. The simpler Part-5 clean-noise order-imbalance gate also fails decisively.

Because XAUUSD feature distributions overlap the published threshold regions and the best profile still loses more than $90 on Stage-A, immediate threshold calibration would be a post-result rescue rather than a high-value continuation.

## Decision

**RETIRE_OFM_PUBLISHED_THRESHOLD_STAGE_A_NO_SURVIVOR.**

Do not:
- calibrate the published thresholds on the same Stage-A window;
- sweep flow/noise/jump windows;
- add session, side or weekday rescue filters;
- retune exits;
- use August;
- begin MQL5 translation.

## Next

`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

The next family should use a different state-transition mechanism rather than another directional-flow threshold.
