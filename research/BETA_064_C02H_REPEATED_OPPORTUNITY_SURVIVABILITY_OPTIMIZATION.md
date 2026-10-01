# BETA064 C02H — Repeated Opportunity + Entry→Hold Survivability Optimization

**Date:** 2026-09-30  
**Status:** RESEARCH CHILD / PARETO-BOUNDARY FINDING — NO NEW MAJOR CHECKPOINT  
**Frozen control:** Major Checkpoint 02 remains immutable  
**Scope:** ENTRY→HOLD only  
**Hold→Exit:** deferred  
**August:** sealed  
**Alpha/GAMMA:** prohibited / not used  
**MQL5:** no authorization / no change

## Objective

Repeatedly refine, repair, optimize and expand the E1–E12 Entry→Hold architecture to increase opportunity count while preserving the preferred >=85% monthly Entry→Hold survivability floor.

This unit also tested the strongest new specialist/context ideas carried forward from the preceding specialist-gap search:
- exact frozen-V2 E2 Pullback/Reacceleration + Fibonacci depth + completed Heikin-Ashi state + Hurst/Kalman adapter;
- E6D3 session-specific survival models;
- E6D3 completed 1-second micro derivative state;
- quality-reserve spending using cross-fitted derivative meta-admission;
- two-score portfolio composition for E6 vs non-E6 derivative opportunity families.

## Important reproducibility finding

The corrected V2 freeze bundle contains:
- `beta064_multidesk_v2.py`;
- frozen entry/hold/session models;
- session router and gap-fill scripts.

However `beta064_multidesk_v2.py` imports the older transient helper `/mnt/data/beta064_multidesk_loop.py`, which is not included in V1/V2, current GitHub, or Drive search.

Therefore:
- the exact V2 definitions for broadened E1/E2/E4 are recoverable from `beta064_multidesk_v2.py`;
- full exact E1–E12 parent-candidate regeneration remains incomplete without the older helper;
- C02C selected portfolio and C02E derivative opportunity generator are fully reproducible from durable artifacts and were used for the C02H expansion tests.

## Exact E2 adapter test

The exact V2 E2 parent clock is explicitly reconstructible:

`H1 direction ownership + 5m counter-move + 1m/15s reacceleration + H1 efficiency > .12`.

Jan–Jul exact E2 raw candidates:
- Jan 346 / 9.54% survival
- Feb 209 / 13.88%
- Mar 105 / 8.57%
- Apr 254 / 9.84%
- May 290 / 8.28%
- Jun 195 / 8.21%
- Jul 307 / 6.84%

Adapter features:
- causal Fibonacci retracement depth;
- completed 15s Heikin-Ashi state;
- Hurst R/S persistence;
- two-state Kalman velocity / innovation / uncertainty.

Held-out AUC changes were inconsistent:
- Jan -0.0126
- Feb -0.0094
- Mar +0.1493
- Apr -0.0238
- May +0.0644
- Jun -0.0077
- Jul +0.0055

Top-score tails remained poor (~18-20% survival), and **no six-development-month >=85% admission gate formed**.

**Decision:** reject Fib/HA/Hurst/Kalman as an E2 opportunity-expansion adapter. Do not add E17/E18-style Entry authority.

## Reproducible derivative opportunity bus

The C02E derivative generator was rerun on original Jan–Jul Dukascopy Bid/Ask ticks.

After reserving C02C control intervals, approximately 213k candidate opportunities from the stronger D3 / sweep / reclaim / break families were scored with held-out survival / first-passage / path-value models.

A strict requirement that new additions themselves maintain >=85% survival in every development month collapsed to zero additions.

This confirms the earlier C02G/C02E conclusion: derivative clocks are context/opportunity-search mechanisms, not safe standalone Entry authority.

## Quality-reserve spending

The cross-fitted selected microstate filter creates a quality reserve:

- C02C control: **5,519 trades / 88.20% survival / +$6,012.177 diagnostic value**
- reserve-filtered base: **5,094 trades / 89.20% survival / +$5,691.102 diagnostic value**

The reserve was then spent on held-out-scored idle derivative opportunities.

### First fixed conservative expansion

Stable threshold selected by six of seven threshold-search folds:

`score = P_survive × (0.40 + 0.60 × P_first_passage)`
`score >= 0.3096195462`

Result:
- **5,566 trades**
- **+496 vs Major Checkpoint 02**
- **+47 vs C02C**
- weighted survivability **86.60%**
- weakest month **85.59%**
- diagnostic value **+$5,362.795**
- derivative additions: 472
- additions standalone survival approximately 55-61% by month
- additions diagnostic value negative in aggregate.

The monthly 85% floor is preserved, but the quality/value degradation is too large to call this superior to C02C/C02D.

### Threshold Pareto frontier

Among settings that remain above 5,519 total trades and keep every observed month >=85%:

| score threshold | trades | weighted survival | weakest month | diagnostic value |
|---:|---:|---:|---:|---:|
| 0.30950 | 5,569 | 86.55% | 85.59% | +$5,353.412 |
| 0.30975 | 5,563 | 86.59% | 85.57% | +$5,366.452 |
| 0.31000 | 5,552 | 86.69% | 85.65% | +$5,390.536 |
| 0.31050 | 5,542 | 86.77% | 85.65% | +$5,399.987 |
| **0.31125** | **5,527** | **86.77%** | **85.70%** | **+$5,382.979** |

The last row is the highest-survival setting that still exceeds the 5,519-trade C02C count in this fixed-threshold search.

## E6 session and micro refinements

### Session-specific E6D3 models

Top 1% held-out survival:
- Australia ~57.4%
- Asia ~55.4%
- Middle East ~60.1%
- Europe ~53.2%
- UK ~54.2%
- New York ~54.9%

**Decision:** session-specific E6D3 modeling does not rescue standalone quality.

### Completed 1-second microstate meta-adapter

Added same-timestamp completed 1s velocity, acceleration, jerk, spread and quote-activity state.

Held-out survival AUC change versus the prior E6D3 meta score:
- Jan +0.00045
- Feb +0.00038
- Mar +0.00192
- Apr -0.00039
- May +0.00267
- Jun +0.00361
- Jul +0.00332

Best practical ranked tail:
- top 0.3%: ~60.5% survival

**Decision:** microstate improves discrimination slightly but not enough for Entry authority. This is consistent with C02G.

## Two-score composition

E6D3 was ranked with the micro-enhanced score and non-E6 derivative families with their separate held-out score.

Best count/survival solution above 5,519 trades:
- 5,533 trades
- 86.72% weighted survival
- weakest month 85.15%
- +$5,335.792 diagnostic value

This is inferior to the simpler 0.31125 frontier on survival/value and adds only six trades.

**Decision:** reject added two-score complexity.

## Current Pareto decision

Repeated research now shows three distinct operating points.

### Major Checkpoint 02 — immutable control
- 5,070 trades
- 88.44% weighted survival
- +$5,782.071 diagnostic value
- every observed month >85%

### C02D — strongest robust balanced expansion
- **5,469 trades**
- **+399 / +7.87% opportunities vs frozen**
- **88.39% weighted survival**
- **+$5,981.67 diagnostic value**
- **7/7 leave-one-month-out months >=85%**
- all observed months >=85%

This remains the strongest setting satisfying most quant requirements simultaneously.

### C02C — higher-count observed child
- **5,519 trades**
- **+449 / +8.86% opportunities vs frozen**
- **88.20% weighted survival**
- **+$6,012.177 diagnostic value**
- every observed month >=85%
- historical threshold-reselection LOMO 6/7, February ~84.95%

C02C has the best observed combination of count and diagnostic value but is not as robust as C02D.

### C02H derivative frontier — maximum count while keeping observed monthly floor
- up to 5,527-5,569 trades
- 86.55%-86.77% weighted survival
- every observed month >=85% for selected fixed thresholds
- materially lower diagnostic value
- new additions themselves are far below 85% standalone survival

**Decision:** C02H derivative count expansion is **not promoted**. The extra 8-50 trades beyond C02C are not worth the survivability/value degradation.

## Scientific conclusion

The current opportunity/survivability frontier has been meaningfully characterized.

The best quality-preserving increase is not another new Entry clock. It is the session-conditioned parent architecture already represented by C02C/C02D.

For the next material jump beyond ~5.5k trades without sacrificing quality, BETA needs one of:

1. recovery of the missing exact historical parent candidate helper so rejected parent states can be replayed exactly;
2. a genuinely orthogonal new specialist with independently >=85% held-out Entry→Hold survival;
3. materially stronger state discrimination that raises new-opportunity standalone survival above the current ~55-60% derivative ceiling.

Further threshold mining of the existing derivative bus is rejected due diminishing returns and increasing selection bias.

## Recommended carry-forward

- **Use C02D as the robust research reference child.**
- **Keep C02C as the higher-opportunity observed research child.**
- Do not promote C02H derivative expansion.
- Continue search for orthogonal specialists only when reconstructible and independently validated.
- Preserve C02G derivative state as same-timestamp context.
- Keep E11 saturated/frozen.
- Keep Hold→Exit deferred.
- Keep August sealed.
- No MQL5 change.
