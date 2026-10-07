# GAMMA-02 — Funded Cap Utilization 027

**Status:** COMPLETE / PARITY VERIFIED / DURABLE  
**Parent:** GAMMA_02_PROFIT_FUNDED_CAPACITY_026  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Parity

The exact funded-cap selector was rebuilt from durable helpers and reproduced the parent economics exactly:

- +$154,538.37 net
- 24,646 trades
- PF 4.0910969109
- +$6.2703226 expectancy/trade
- realized balance DD ~$4,179.75
- max open 256
- 58,579 skipped candidate entries

Funding rule:
- start cap 64
- +64 slots per $2,500 current realized cumulative net
- max cap 256

## Exact unlock chronology

- 64 slots from first candidate on **2026-01-02 12:45:00.044 UTC**
- 64 -> 128 at **2026-01-12 15:00:25.967 UTC**, realized net $2,531.85
- 128 -> 192 at **2026-01-13 15:04:46.957 UTC**, realized net $6,116.65
- 192 -> 256 at **2026-01-14 11:53:41.781 UTC**, realized net $7,998.01

No contractions occurred in this January replay.

## Utilization

| Allowed cap | Candidate events | Accepted | Skipped | Skip rate | Mean utilization |
|---:|---:|---:|---:|---:|---:|
| 64 | 15,758 | 1,393 | 14,365 | **91.16%** | 96.06% |
| 128 | 3,733 | 943 | 2,790 | **74.74%** | 90.82% |
| 192 | 1,604 | 799 | 805 | **50.19%** | 79.52% |
| 256 | 62,130 | 21,511 | 40,619 | **65.38%** | 84.56% |

At every cap level, median/P90/P99 utilization at candidate moments is 100%.

## Interpretation

The profit-funded ceiling is real and binding.

The mechanism is not merely a decorative risk governor:
- the initial 64-slot phase suppresses the majority of early eligible entries;
- the system reaches 256 by Jan 14;
- even at 256, nearly two-thirds of candidate events arrive while capacity is already full.

This implies that future profit improvement cannot be evaluated only by signal quality. **Inventory turnover and capital-slot efficiency are now primary bottlenecks.**

The main scientific question after this checkpoint is:
> Can the architecture free or recycle slots faster without destroying the high-expectancy campaign inventory?

Do not answer that by hiding extra exposure. Any new mechanism must report its total simultaneous 0.01-ticket heat explicitly.

## QA note

The historical profit-funded helper accidentally swapped source/reason array labels in its attribution output. Net, trade count, cap admission, PF, expectancy, and DD are unaffected because the selector uses entry time, exit time, and P/L for admission. This utilization helper corrects attribution ordering.

## Exact artifacts

GitHub:
- research/R9_GAMMA/helpers/gamma02_funded_cap_utilization_027.py
- research/R9_GAMMA/artifacts/gamma02_funded_cap_utilization_027.json

SHA-256:
- helper: 4468b54e3adc02d3cb2814551b33566c3329f08214662fbc80aebe093163539a
- JSON: 8a6ce26e4896f1fdf8507405c39d31f3b3168418389abf99b2684dd214e396dd

## Next

1. full ordered-tick equity-DD certification for the lower-cap funded finalists;
2. exact January-only R9 SYNTH benchmark extraction;
3. then test slot-turnover / profit-lock mechanisms only if they remain causal and exposure-explicit;
4. freeze January architecture before Jan-Jul validation.

R9 SYNTH remains the hard target.
