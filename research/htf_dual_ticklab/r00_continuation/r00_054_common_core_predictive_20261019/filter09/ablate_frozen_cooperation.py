#!/usr/bin/env python3
"""Predefined leave-one-lifecycle-out analysis of FEB-FROZEN FILTER09.
No re-fitting or threshold re-selection on June or July. Original event times remain fixed.
"""
import csv,json,sys
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data/R00_054_FILTER09_MONTH_INDEPENDENT');sys.path.insert(0,str(ROOT))
from run_filter09 import score
ROWS=[]
for b in ('coinexx','dukascopy'):
    freeze=json.loads((ROOT/f'FEB_FROZEN_POLICY_{b}.json').read_text())['selected'];cut=freeze['threshold']
    for m in ('06','07'):
        with np.load(ROOT/f'FROZEN_DECISIONS_{b}_{m}.npz') as f:
            t=f['t'];y=f['label'];risk=f['risk'];flags=np.column_stack([f[f'{name}_state'] for name in 'NOSRM']);original=f['keep'].astype(bool)
        assert len(flags)==len(t)
        family={'selected_frozen_original':original,'KEEP_ALL_CONTROL':np.ones(len(y),bool),'N_O_S_R_M_unconditional_risk':risk<=cut,
                'at_least_3_confirmed':~((risk>cut)&(flags.sum(axis=1)>=3)),
                'at_least_1_confirmed':~((risk>cut)&(flags.sum(axis=1)>=1)),
                'N_or_O_must_confirm':~((risk>cut)&(flags.sum(axis=1)>=2)&(flags[:,0].astype(bool)|flags[:,1].astype(bool)))}
        for index,name in enumerate('NOSRM'):
            temp=flags.copy();temp[:,index]=0
            family[f'without_{name}']=~((risk>cut)&(temp.sum(axis=1)>=2))
        for policy,mask in family.items():
            d=score(b,t,y,mask);ROWS.append({'broker':b,'month':m,'rule':policy,**d})
with (ROOT/'TRANSFER_FACET_ABLATIONS_FIXED_THRESHOLDS.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(ROWS[0]));w.writeheader();w.writerows(ROWS)
print('LEAVE_ONE_FACET_OUT_FROZEN',len(ROWS),'scores')
for label in sorted(set(r['rule'] for r in ROWS)):
    s=[r for r in ROWS if r['rule']==label];good=sum(v['correct'] for v in s);signals=sum(v['signals'] for v in s)
    print(label,good,signals,round(100*good/signals,4),sum(v['new_r9_hour_fails'] for v in s))
