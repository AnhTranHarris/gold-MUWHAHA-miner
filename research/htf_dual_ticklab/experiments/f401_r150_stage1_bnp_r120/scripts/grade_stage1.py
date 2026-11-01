"""Frozen-Feb original-event same-supply Stage1 incremental comparison."""
import json
from pathlib import Path
import numpy as np
from r150_stage1_regime_probe import cuts, mask, grade
M=Path('/mnt/data/r150_repair_advanced/models'); S=Path('/mnt/data/r150_lean_candidate/staged')
months=('01','02','06','07')
data={m:{k:np.array(z[k]) for k in z.files} for m in months for z in [np.load(S/f'dukascopy_{m}.npz')]}
scores={}
for m in months:
  with np.load(M/f'scores_control_{m}_SCORES.npz') as z:baseline={k:np.array(z[k]) for k in z.files}
  advanced={k:baseline[k].copy() if k=='guardian' else np.load(M/f'r120_conditional_{m}_{k}.npy') for k in ('guardian','opposite','neutral')}
  scores[m]={'baseline':baseline,'regime':advanced}
cal={k:cuts(data['02'],scores['02'][k]) for k in ('baseline','regime')}
report={'source':'Original F395 Dukascopy event IDs; R120 pre-t0 phase state; J2/L2/M2 previously four-month-trained, historically exposed','models':{},'incremental':{}}
for k in ('baseline','regime'):
 report['models'][k]={m:grade(data[m],scores[m][k],cal[k]) for m in months}
for m in months:
 a=report['models']['baseline'][m];b=report['models']['regime'][m]
 masks={k:mask(data[m],scores[m][k],cal[k]) for k in ('baseline','regime')}
 y=data[m]['truth']
 report['incremental'][m]={kk:b[kk]-a[kk] for kk in ('bad_veto','correct_lost','neutral_veto','opposite_veto','auc_opposite','auc_neutral')}
 report['incremental'][m].update(new_unique_bad=int((masks['regime']&~masks['baseline']&(y!=0)).sum()),
                                 new_unique_good_lost=int((masks['regime']&~masks['baseline']&(y==0)).sum()),
                                 bad_surrendered=int((~masks['regime']&masks['baseline']&(y!=0)).sum()),
                                 good_recovered=int((~masks['regime']&masks['baseline']&(y==0)).sum()))
report['status']='RESEARCH_DIAGNOSTIC_NOT_APPROVED_NOT_OOS_NOT_REAL_T1_PENDING_VERIFIED'
out=Path('/mnt/data/r150_repair_advanced/receipts/DK_STAGE1_FEB_FROZEN_RESULTS.json');out.write_text(json.dumps(report,indent=2))
print(json.dumps(report['incremental'],indent=2))
print('June/July counts:',[(k,report['models'][k]['06']['bad_veto'],report['models'][k]['06']['correct_lost'],report['models'][k]['07']['bad_veto'],report['models'][k]['07']['correct_lost']) for k in ('baseline','regime')])
