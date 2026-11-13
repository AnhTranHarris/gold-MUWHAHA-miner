import json,hashlib,zipfile,statistics
from pathlib import Path
import numpy as np
p=Path('/mnt/data/r9_m60_priority_screen')
folds=[json.loads((p/'results'/f'fold_{i:02}.json').read_text()) for i in range(5,10)]
unc=json.loads((p/'results'/'model_replay_and_uncertainty.json').read_text())
order=['frozen_baseline','cusum_only','signed_intensity_only','brownian_geometry_only','all_three']
fmt=lambda x:f'{x:.6f}'
rows=[]
for f in folds:
 rows.append('| '+f['test_month']+' | '+' | '.join(fmt(f['models'][n]['5000']['all_actions_auc']) for n in order)+' |')
means={n:{'auc5':float(np.mean([f['models'][n]['5000']['all_actions_auc'] for f in folds])),
 'auc15':float(np.mean([f['models'][n]['15000']['all_actions_auc'] for f in folds])),
 'r9_5':float(np.mean([f['models'][n]['5000']['r9_action_auc'] for f in folds])),
 'strict_entries':int(sum(f['models'][n]['5000']['strict_utility_positive_count'] for f in folds))} for n in order}
orig=json.loads(Path('/mnt/data/r9_m60_competing/results/diagnostic_summary.json').read_text())
for mm in range(5,10):
 gold=f'{mm:02}'
 f=folds[mm-5]
 x=f['models']['frozen_baseline']['5000']['all_actions_auc']
 y=orig['event_trend_flow']['5000']['auc_by_month'][gold]
 if abs(x-y)>1e-12:raise RuntimeError(f'baseline parity failure {gold} {x} {y}')
raw=json.loads(Path('/mnt/data/r9_m60_expanded/source_receipt.json').read_text())
record_count=sum(raw['source_months'][f'{i:02}']['rows'] for i in range(1,10))
entry_count=sum(f['n_eval_entry_opportunities'] for f in folds)
md=f'''# Gold MUWHAHAHA R9 — Coinexx-only CUSUM, signed quote-intensity and analytical first-passage screen

**Research date:** 2026-11-13. **Result:** DOES NOT PASS the owner's 0.75 ROC-AUC gate. **No R9 trading signal/exit changes.** QRB/QAF remains enabled in the preceding isolated R9 research branch as *telemetry only*, not as an input to trading decisions.

## Exact scope and reproducibility

- Original **{record_count:,} Coinexx XAUUSD Bid/Ask quote events**, January–September 2026. Each source gzip SHA-256 checked against the preexisting immutable nine-month source receipt before feature extraction.
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
{chr(10).join(rows)}
| **Mean (equal month weights)** | {' | '.join(fmt(means[n]['auc5']) for n in order)} |

**Five-second mean R9 ORIGINAL-direction AUC:** baseline {means['frozen_baseline']['r9_5']:.6f}; all-three {means['all_three']['r9_5']:.6f}, a lift of {means['all_three']['r9_5']-means['frozen_baseline']['r9_5']:.6f}. The best 5s pooled July AUC is {max(f['models']['all_three']['5000']['all_actions_auc'] for f in folds):.6f}; **none of the 25 held-out model tests reaches 0.750**.

**Fifteen-second mean pooled-action AUC:** baseline {means['frozen_baseline']['auc15']:.6f}; all-three {means['all_three']['auc15']:.6f}; weaker long-horizon discrimination persists. **All 25 model × month 15s checks fail 0.75 as well.**

### Trade-frequency and economic result

Held-out months total **{entry_count:,} original R9 decisions**, or twice as many *hypothetical* independent BUY/SELL actions. Each one was included for evaluation. Under the previously fixed positive expected-utility rule, **zero** entries were selected for every one of the five feature families across all five months. Thus neither high trade frequency nor positive after-cost expectancy was achieved; zero-selection is a consequence of the conservative cost-adjusted screening rule, not proof that *every* conceivable exit policy fails. No full-account/on-policy trading simulation or Coinexx execution parity was conducted.

### Paired uncertainty (diagnostic only)

The original-direction five-second AUC lift from all-three features over frozen baseline was analyzed by a paired **UTC-day block bootstrap within each previously exposed month**, using identical label/order arrays and model scores. Equal-weight monthly mean lift: {unc['mean_monthly_delta_paired_day_bootstrap']['mean']:.6f}; 2.5–97.5% resampling interval **[{unc['mean_monthly_delta_paired_day_bootstrap']['p025']:.6f}, {unc['mean_monthly_delta_paired_day_bootstrap']['p975']:.6f}]** (180 replicates). This describes variability *conditional on the old exposed data* and must not be presented as pristine validation of a deployable lift. It is much smaller than the missing AUC margin.

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
'''
(p/'RESULTS.md').write_text(md)
summary={'asof':'2026-11-13','raw_ticks':record_count,'total_R9_decisions':303934,
 'heldout_r9_decisions':entry_count, 'feature_families':order,'means':means,
 'max_pooled_auc5':float(max(f['models']['all_three']['5000']['all_actions_auc'] for f in folds)),
 'gate_0_75_passes':0,'model_month_checks':25,'positive_utility_entries':0,
 'saved_models_replayed':unc['verified_models'],'saved_auc_values_replayed':unc['verified_auc_values'],
 'bootstrap_r9side_5s':unc['mean_monthly_delta_paired_day_bootstrap'],
 'not_pristine_oos':True,'production_EA_modified':False}
(p/'results'/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
# Integrity SHA256 receipt of original research output/zip component files.
files=[*sorted((p/'src').glob('*.py')),*sorted((p/'tests').glob('*.py')),*sorted((p/'results').glob('*.json')),*sorted((p/'models').glob('*.joblib')),p/'RESULTS.md',p/'create_report.py',p/'r9_m60_priority_screen_ci.yml']
manifest=[]
for f in files:
 manifest.append({'path':str(f.relative_to(p)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(p/'MANIFEST.json').write_text(json.dumps({'files':manifest,'total':len(files),'untrusted_market_data_not_included':True},indent=2)+'\n')
source=p.parent/'R9_M60_CUSUM_QuoteIntensity_Brownian_20261113_SOURCE_MODELS_EVIDENCE.zip'
with zipfile.ZipFile(source,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in [*files,p/'MANIFEST.json']:
  z.write(f,arcname=str(f.relative_to(p)))
with zipfile.ZipFile(source) as z:
 bad=z.testzip()
 assert bad is None
 print('SOURCE',source,'members',len(z.namelist()),'bytes',source.stat().st_size)
cache=p.parent/'R9_M60_Coinexx_CUSUM_QuoteIntensity_Cache_JanSep_20261113.zip'
with zipfile.ZipFile(cache,'w',compression=zipfile.ZIP_STORED) as z:
 for f in sorted((p/'derived').glob('*')):
  if f.is_file():z.write(f,arcname=str(f.relative_to(p)))
with zipfile.ZipFile(cache) as z:
 bad=z.testzip();assert bad is None
 print('CACHE',cache,'members',len(z.namelist()),'bytes',cache.stat().st_size)
print('RESULTS',len(md),'chars','summary',summary)
