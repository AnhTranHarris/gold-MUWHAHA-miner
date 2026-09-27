# R9B Gamma — Causal Recertification Baseline 014

## Status
**VERIFIED_DURABLE_CAUSAL_BASELINE**

This recovery unit establishes the reproducible Jan–Jul baseline produced by the three reconstructed causal Gamma helper roles. It is the scientific restart point for future Gamma research.

The historical `R9B_Gamma_2_Structure_Aware_Sweep_Reclaim` result remains preserved as a historical comparison/oracle benchmark. It is **not** relabeled as causal or deployable because its exact runtime helper source could not be recovered and the near-target compatibility reconstructions require retrospective/future-completed-second timestamp ownership.

## Frozen reconstructed helpers
- `r9b_screen.py` — commit `24125d9b3eb32243349385903b2e63e5d5cfad11`
- `r9b_r8_recert.py` — commit `40e83b7dfbf59ef37459728dd625ed5e98a7ff96`
- `r8_sweep_lifecycle_screen.py` — commit `5676801a6842eeb627cc12d272f17c2642d50c7e`

## Jan–Jul causal result
| Month | Trades | Winners | Win rate | Net | Gross loss | PF |
|---|---:|---:|---:|---:|---:|---:|
| Jan | 28,088 | 19,087 | 67.95% | -$4,510.09 | -$11,511.55 | 0.608 |
| Feb | 28,188 | 18,834 | 66.82% | -$4,450.96 | -$13,668.41 | 0.674 |
| Mar | 35,573 | 24,169 | 67.94% | -$6,589.63 | -$16,505.80 | 0.601 |
| Apr | 26,683 | 18,068 | 67.71% | -$4,735.75 | -$10,883.58 | 0.565 |
| May | 25,525 | 17,412 | 68.22% | -$4,425.30 | -$9,751.75 | 0.546 |
| Jun | 27,710 | 18,828 | 67.95% | -$5,345.32 | -$10,875.75 | 0.509 |
| Jul | 25,807 | 16,744 | 64.88% | -$5,342.88 | -$9,528.55 | 0.439 |

Aggregate:
- trades: **197,574**
- winners: **133,142**
- win rate: **67.3884%**
- net: **-$35,399.9130**
- gross profit: **+$47,325.4690**
- gross loss: **-$82,725.3820**
- PF: **0.572079**
- raw signals before non-overlap: **244,792**
- maximum monthly realized-sequence drawdown observed: **$6,594.31**

## Interpretation
The rebuilt causal stack is stable across Jan–Mar discovery, April, May–Jun forward, and July stress. Its conversion remains near 65–68% rather than the historical ~82%. This persistence across every month supports the source-equivalence conclusion: the historical uplift is not explained by a normal month-specific calibration difference.

The recovery objective is therefore complete at the implementation/reproducibility level:
1. helper loss has been repaired;
2. the rebuilt helper sources are durable;
3. deterministic causal replay is available;
4. the unrecoverable historical benchmark is isolated from deployable logic;
5. future research has a clean chronological baseline.

## Next research unit
**R9B_GAMMA2_CAUSAL_BRIDGE_RECOVERY_015**

Goal: recover the lost economic bridge from the corrected causal baseline using only reconstructible, causal state/ownership/lifecycle mechanisms. Preserve trade density where economically justified, score gross loss first, successful trades second, net third. Reuse prior 010–020 diagnostic insights only as hypotheses; revalidate them against this recertified baseline before promotion.

August remains sealed.
