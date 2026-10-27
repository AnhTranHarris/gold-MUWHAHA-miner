#!/usr/bin/env python3
"""Independent R9 SYNTH floor audit over BOTH June+July broker files.
Month source files overlap UTC month boundaries for Coinexx. Counts are
aggregated by true UTC interval BEFORE comparing immutable R9 reference.
"""
from pathlib import Path
import zipfile,io,json
import numpy as np,pandas as pd

ROOT=Path('/mnt/data/r00_054_20261026_a01')
F44=Path('/mnt/data/source/R00_054_F44_OUT_OF_FIT_COOPERATIVE_ERROR_ARBITER_20261020.zip')
ORIG=Path('/mnt/data/source/R00_054_FILTER08_FOUR_MONTH_70PCT_OVERFIT_RESEARCH_20261019.zip')
with zipfile.ZipFile(ORIG) as z:
    q=pd.read_csv(io.BytesIO(z.read('FILTER08/FOUR_MONTH_HOUR_DAY_WEEK_MONTH_R9_QUOTAS.csv')))
with zipfile.ZipFile(F44) as z:
    cut=json.loads(z.read('F44/F44_FEB_FROZEN_POLICIES.json'))['OOF_min_err']['threshold']
    output={}
    for broker in ['coinexx','dukascopy']:
        sources=[];keep=[];base=[]
        for month in ['06','07']:
            with np.load(io.BytesIO(z.read(f'F44/F44_PREDICTIONS_{broker}_{month}.npz'))) as a:
                sources.append((a['t'].copy(),a['truth'].copy()))
                base.append((a['OOF_min_err']>=cut).copy())
            with np.load(ROOT/f'frozen_mask_{broker}_{month}.npz') as m:
                assert np.array_equal(sources[-1][0],m['t'])
                keep.append(m['keep'].copy())
        t=np.concatenate([x[0] for x in sources]);y=np.concatenate([x[1] for x in sources]);
        kc=np.concatenate(keep);kb=np.concatenate(base);ku=np.ones(len(t),dtype=bool)
        dt=pd.to_datetime(t,unit='ms',utc=True)
        keys={'hour':dt.strftime('%Y-%m-%dT%H:00:00+00:00'),
              'day':dt.strftime('%Y-%m-%d'),
              'iso_week':dt.strftime('%G-W%V'),
              'month':dt.strftime('%Y-%m')}
        res={}
        for level in keys:
            ref=q[(q.broker==broker)&(q.level==level)]
            if level!='iso_week':ref=ref[ref.utc_key.str.startswith(('2026-06','2026-07'))]
            else:ref=ref[ref.utc_key.isin(np.unique(keys[level]))]
            def score(k):
                got=pd.Series(((y==0)&k).astype('int8')).groupby(keys[level]).sum()
                val=ref.utc_key.map(got).fillna(0).to_numpy(dtype=int)
                fail=(val<ref.required_correct_90pct.to_numpy())&(ref.r9_reference.to_numpy()>0)
                return val,fail
            vu,fu=score(ku);vc,fc=score(kc);vb,fb=score(kb)
            res[level]={'eligible':int((ref.r9_reference>0).sum()),
                        'unfiltered_absolute_fail':int(fu.sum()),
                        'candidate_absolute_fail':int(fc.sum()),
                        'candidate_new_fail_vs_unfiltered':int((fc&~fu).sum()),
                        'f44_baseline_absolute_fail':int(fb.sum()),
                        'f44_baseline_new_fail_vs_unfiltered':int((fb&~fu).sum()),
                        'candidate_first_new_fail':ref.loc[fc&~fu,['utc_key','r9_reference','required_correct_90pct']].head(12).to_dict('records')}
        output[broker]=res
(ROOT/'independent_june_july_global_r9_quotas.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(output,indent=2))
