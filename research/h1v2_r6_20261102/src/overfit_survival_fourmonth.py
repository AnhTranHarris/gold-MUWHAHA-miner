"""Explicitly overfit H1V2 R6 quote-arrival-survival factorized policy on ALL four months.

Future R2 labels (including JULY) are used to train. Evaluation scores the exact
same training rows. This is an intentionally contaminated oracle/student
MEMORIZATION research probe, not a causal OOS or live strategy.
"""
from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
from four_month_competing_risks import load,wilson
from fitted_quote_excitation import predict
from fit_survival_rejection import ROOT,R5,MONTHS,train_heads,score,precision_report

def run(super_capacity=False):
    t0=time.monotonic();market=load();source=json.loads((R5/'R5_FITTED_EXCITATION_RESULTS.json').read_text())
    fitted=np.asarray(source['controls']['cross']['coefficient_matrix'],np.float64)
    data={};provenance={}
    for m in MONTHS:
        b,p,mark,k,t=market[m]
        with np.load(R5/f'R5_MARK_1SEC_{m}.npz') as q,np.load(ROOT/f'R6_SURVIVAL_ASOF_{m}.npz') as r:
            if not np.array_equal(r['ix'],q['ix']) or not np.array_equal(r['ts'],t):
                raise ValueError('R6 raw ordinal history join mismatch')
            rate=predict(q['X'],fitted).astype(np.float32)
            survive=r['X'].copy()
        up=rate[:,[0,2,4]].sum(axis=1);down=rate[:,[1,3,5]].sum(axis=1)
        extra=np.column_stack([rate,up-down,np.log1p(up+down),(up-down)/(up+down+1e-6)]).astype(np.float32)
        x=np.nan_to_num(np.column_stack((b,p,mark,extra,survive)).astype(np.float32),nan=-999.,posinf=-999.,neginf=-999.)
        data[m]={'x':x,'k':k,'ts':t,'ix':None}
        provenance[m]={'rows':len(x),'strict_possible':int((k==3).any(axis=1).sum())}
    # Caution: no reused July-withheld heads; new distinct all4 model files.
    config=((120,90),(63,47)) if super_capacity else ((65,48),(43,31))
    tag='R6_FOURMONTH_SUPERCAP_EXPLICIT_TRAIN_LEAKAGE' if super_capacity else 'R6_FOURMONTH_EXPLICIT_TRAIN_LEAKAGE'
    models=train_heads(data,MONTHS,tag,rounds=config[0],leaves=config[1])
    out={'status':'ALL_FOUR_RESUBSTITUTION_EXPLICIT_TRAIN_LABEL_CONTAMINATION',
         'train_and_score_same_months':list(MONTHS),'training_count':60000,
         'model':'R6 as-of past geometry+80 quote ordinal survival+6-mark fitted asof intensity',
         'rounds_opportunity':config[0][0],'rounds_direction':config[0][1], 'leaves_opportunity':config[1][0],'leaves_direction':config[1][1],
         'classes':'WRONG NEUTRAL WEAK_GOOD STRONG_GOOD','months':{},'provenance':provenance,
         'warning':'IN-SAMPLE MEMORIZATION; exact same 60k source candidate rows labels trained and evaluated; not independent predictions, not volume, not profit, no deployed model.'}
    for m in MONTHS:
        sc,_,_=score(*models,data[m]);out['months'][m]=precision_report(sc,data[m]['k'])
        print('R6 TRAIN same month',m,'top150',out['months'][m]['top'][1],flush=True)
    out['elapsed_seconds']=round(time.monotonic()-t0,2)
    (ROOT/('R6_SUPERCAP_FOUR_MONTH_TRAIN_RESUBSTITUTION.json' if super_capacity else 'R6_EXPLICIT_FOUR_MONTH_TRAIN_RESUBSTITUTION.json')).write_text(json.dumps(out,indent=2))
    return out
if __name__=='__main__':
 import sys
 run(super_capacity='--super' in sys.argv)
