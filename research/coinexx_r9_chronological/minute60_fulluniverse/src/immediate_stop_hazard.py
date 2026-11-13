"""Exploratory NO-FUTURE feature model: predict immediate (<=1s) adverse-first exit.
This is a distinct adverse-selection target, NOT the owner's original 15s
favorable-first ROC-AUC; never report as substitute or promote as trading edge.
"""
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score,average_precision_score
from train_full import load,build_model
root=Path('/mnt/data/r9_m60_expanded/full_results')
rows,columns=load(Path('/mnt/data/r9_m60_expanded/full_derived'))
results=[]
for i in range(4,9):
 trX=np.concatenate([z['feature'] for z in rows[:i]])
 # existing load() intentionally excludes future hit times; retrieve them only for training target.
 ys=[]
 for z in rows[:i]:
  d=np.load(Path('/mnt/data/r9_m60_expanded/full_derived')/f"full_month_2026_{z['month']}.npz")
  label=d['labels'][:,1];hit=d['hit_ms'][:,1]
  ys.append(((label==0)&(hit>=0)&(hit<=1000)).astype('i'))
 trY=np.concatenate(ys)
 evalrow=rows[i];d=np.load(Path('/mnt/data/r9_m60_expanded/full_derived')/f"full_month_2026_{evalrow['month']}.npz")
 ty=((d['labels'][:,1]==0)&(d['hit_ms'][:,1]>=0)&(d['hit_ms'][:,1]<=1000)).astype('i')
 out={'month':evalrow['month'],'test_count':len(ty),'immediate_stop_frac':float(ty.mean()),'models':{}}
 for name,n in [('r9_only',14),('hft_full',145)]:
  m=build_model('conservative');m.fit(trX[:,:n],trY)
  p=m.predict_proba(evalrow['feature'][:,:n])[:,1];p_tr=m.predict_proba(trX[:,:n])[:,1]
  cut=float(np.quantile(p_tr,.8));safe=p<=cut
  true_win=d['labels'][:,1]==1
  exret=d['terminal_return'][:,1]-20
  out['models'][name]={'auc':float(roc_auc_score(ty,p)),'train_auc':float(roc_auc_score(trY,p_tr)),
   'ap':float(average_precision_score(ty,p)),'safe_kept_count':int(safe.sum()),
   'safe_kept_fraction':float(safe.mean()),'safe_immediate_stop_frac':float(ty[safe].mean()),
   'safe_favorable_frac':float(true_win[safe].mean()),'safe_quote_ev':float(exret[safe].mean()/100)}
 print('STOP_HAZARD',out,flush=True)
 results.append(out)
 root.joinpath('immediate_stop_1sec_diagnostic.json').write_text(json.dumps({'classification':'DIAGNOSTIC_DISTINCT_TARGET_NOT_PROFIT',
  'target':'source observed <=1s adverse passage from original R9 side','models':results},indent=2)+'\n')
