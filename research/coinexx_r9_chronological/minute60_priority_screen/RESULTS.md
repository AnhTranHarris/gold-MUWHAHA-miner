# Gold MUWHAHAHA R9 — Coinexx-only CUSUM, signed quote-intensity and analytical first-passage screen

**Research date:** 2026-11-13. **Result:** DOES NOT PASS the owner's 0.75 ROC-AUC gate. **No R9 trading signal/exit changes.** QRB/QAF remains enabled in the preceding isolated R9 research branch as *telemetry only*, not as an input to trading decisions.

## Exact scope and reproducibility

- Original **72,129,347 Coinexx XAUUSD Bid/Ask quote events**, January–September 2026. Each source gzip SHA-256 checked against the preexisting immutable nine-month source receipt before feature extraction.
- Exactly **303,934 frozen original R9 decisions** from the existing hazard study; each paired with hypothetical BUY and SELL first-passage labels (607,868 action records). No new entries are selected and no trades are removed from the evaluation denominator except explicitly censored labels.
- Same completed 500-ms historical baseline and exact event-time trend/QRB/QAF feature family as the previous competing-risk training. Frozen May–September baseline reproduces **exactly** the previous published AUC to 12 decimal places.
- Frozen target: favorable/adverse first-passage at original R9 decision times, actual quote-side BUY Ask entry / Bid exit, SELL Bid entry / Ask exit. Existing stop `max(30 cents, 2×spread, 1.5×sqrt(RV_1sec))`, favorable `max(50 cents, ceil(1.6×stop))`, modeled 20-cent *price* cost. NOT actual broker fills, account currency or slippage.
- Same LightGBM hyperparameters, discretized competing-risk intervals `[250ms,1s,3s,5s,15s]`, uniform deterministic **40,000 at-risk training exposures/interval** maximum, previous train periods and **full held-out action universe**. January–April→May through January–August→September. Test months have been repeatedly exposed in previous R9 research; **NOT pristine OOS**.
- 60-second anchored-segment reset or 15-second quote gap reset for sequential CUSUM and decayed arrival intensities, from original source-ordinal quote events only. The reset is not a truly sliding CUSUM and its arbitrary segment phase is a research limitation.

## Features investigated

**CUSUM:** Prior-variance standardized midpoint quote revisions, one-sided positive/negative sequential CUSUM with `k=0.25`, numerical clamp and reset after 60 seconds or long data gaps. No future tick can enter the update. These are candidate screening states, not independently optimized trade triggers.

**Signed quote-arrival intensity:** Four predeclared exponential-decay windows (`250ms`, `1s`, `5s`, `15s`) for upward and downward midpoint quote-revision *counts*, including normalized signed imbalance and fast/slow intensity divergence. This is not actual buy/sell aggressor trade flow and is not a fitted Hawkes process.

**Analytical first-passage geometry:** Brownian constant-drift/variance approximations derived only from 5-second/15-second observed quote history, actual spread and frozen adaptive stop/target. Separate action signs and required target+spread / stop−spread distances. One feature estimates the eventual upper-before-lower hit probability; other 5s/15s *single-sided* reflection-formula approximations are not calibrated competing-risk probabilities. The final fitted hazard classifier provides the evaluated probabilities. An extreme negative-drift numerical stability bug was corrected **before final scoring**, with an additional regression test.

## Frozen identical-label five-second pooled-action ROC-AUC

| Held-out month | R9 event-trend+QRB/QAF baseline | +CUSUM | +signed intensity | +Brownian geometry | +all three |
|---|---:|---:|---:|---:|---:|
| 05 | 0.707615 | 0.708408 | 0.707877 | 0.708658 | 0.708035 |
| 06 | 0.717726 | 0.718000 | 0.717310 | 0.720073 | 0.720872 |
| 07 | 0.738305 | 0.739084 | 0.739095 | 0.740328 | 0.740711 |
| 08 | 0.736012 | 0.736044 | 0.736561 | 0.738793 | 0.739191 |
| 09 | 0.725815 | 0.726869 | 0.726660 | 0.727288 | 0.727639 |
| **Mean (equal month weights)** | 0.725095 | 0.725681 | 0.725501 | 0.727028 | 0.727290 |

**Five-second mean R9 ORIGINAL-direction AUC:** baseline 0.710256; all-three 0.712944, a lift of 0.002688. The best 5s pooled July AUC is 0.740711; **none of the 25 held-out model tests reaches 0.750**.

**Fifteen-second mean pooled-action AUC:** baseline 0.653495; all-three 0.654242; weaker long-horizon discrimination persists. **All 25 model × month 15s checks fail 0.75 as well.**

### Trade-frequency and economic result

Held-out months total **162,312 original R9 decisions**, or twice as many *hypothetical* independent BUY/SELL actions. Each one was included for evaluation. Under the previously fixed positive expected-utility rule, **zero** entries were selected for every one of the five feature families across all five months. Thus neither high trade frequency nor positive after-cost expectancy was achieved; zero-selection is a consequence of the conservative cost-adjusted screening rule, not proof that *every* conceivable exit policy fails. No full-account/on-policy trading simulation or Coinexx execution parity was conducted.

### Paired uncertainty (diagnostic only)

The original-direction five-second AUC lift from all-three features over frozen baseline was analyzed by a paired **UTC-day block bootstrap within each previously exposed month**, using identical label/order arrays and model scores. Equal-weight monthly mean lift: 0.002732; 2.5–97.5% resampling interval **[0.002138, 0.003389]** (180 replicates). This describes variability *conditional on the old exposed data* and must not be presented as pristine validation of a deployable lift. It is much smaller than the missing AUC margin.

## Scientific interpretation and stop decision

1. The **analytical spread/volatility/barrier geometry** features generated most of the small incremental AUC improvement. Keep this *as a candidate research feature*, not as a proven mathematical Brownian market law.
2. CUSUM and signed quote-update intensity contribute very little relative to already encoded event-time trend/QRB/QAF; do not assume further indicator stacking can force 0.75. No production timing/management changes are supported.
3. The user's **high trade volume requirement is not met** under the existing strict positive-utility rule; raising AUC by tiny amounts without profitable action coverage does not meet project objectives.
4. Coinexx `last`, `volume` and `volume_real` remain zero in all raw ticks (previous verified source audit). These formulas cannot recover executed trade direction, L2 depth, dealer queue position or fill/slippage latency. Repeated training on previously exposed May–September months is also not independent forward validation.
5. **Research acceptance: FAIL** owner minimum ROC-AUC 0.75 and positive utility/volume gate. Freeze source and receipts. Do not merge experimental classifiers into the R9 EA. Reconsider target/decision-time hypothesis *only if* a distinct preregistered test can produce after-cost utility and avoid repeated search on these exposed months.

## Integrity and tests

- **11 new** formula/causality tests plus **24 prior** event-hazard and MT5 math-contract tests passed locally. These do *not* compile MQL5 or prove MT5 source-to-Python parity.
- **25 saved classifiers reloaded**, and **100** historical AUC numbers reproduced exactly: pooled/R9-direction, 5s/15s for five families × five months.
- Original source-month gzip digests checked. Nine monthly derived feature receipts include source and derivative SHA-256. No original market-data bytes or production EA source changed.
- GitHub Actions CI not certified; native MT5 MetaEditor compile and live parity not claimed.

## Reproduction

Python >=3.11 with numpy, pandas, numba, scikit-learn, scipy, lightgbm, joblib; source scripts currently reference the pinned existing research root paths under `/mnt/data` and require the archived frozen research caches. Execute:

```bash
PYTHONPATH=/mnt/data/r9_m60_priority_screen/src python -m unittest discover -s /mnt/data/r9_m60_priority_screen/tests -v
PYTHONPATH=/mnt/data/r9_m60_priority_screen/src python /mnt/data/r9_m60_priority_screen/src/extract_priority.py
for i in 4 5 6 7 8; do PYTHONPATH=/mnt/data/r9_m60_priority_screen/src python /mnt/data/r9_m60_priority_screen/src/train_screen.py --fold "$i"; done
PYTHONPATH=/mnt/data/r9_m60_priority_screen/src python /mnt/data/r9_m60_priority_screen/src/verify_and_bootstrap.py
```

Use `OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=2 OMP_NUM_THREADS=2` to avoid oversubscription. Model files are intentionally marked `FAILED_UNTIL_CERTIFIED`; no trained weights are embedded in MT5.
