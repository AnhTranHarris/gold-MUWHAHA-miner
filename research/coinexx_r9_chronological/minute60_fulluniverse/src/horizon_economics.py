"""Post-evaluation diagnostic only: quantify 5s signal prevalence and modeled quote costs.
Not a new selected trading model; tests are exposed months and never deployment certified.
"""
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score,average_precision_score
from train_full import load,build_model
rows,_=load(Path('/mnt/data/r9_m60_expanded/full_derived'))
out=[]
for teix in range(4,9):
 h=0
 train=[r for r in rows[:teix]];test=rows[teix]
 X=np.concatenate([r['feature'][r['label'][:,h]!=-1,:117] for r in train]);Y=np.concatenate([(r['label'][r['label'][:,h]!=-1,h]==1).astype('i') for r in train])
 good=test['label'][:,h]!=-1; XT=test['feature'][good,:117];YT=(test['label'][good,h]==1).astype('i');ret=test['ret'][good,h]
 model=build_model('conservative');model.fit(X,Y)
 ptr=model.predict_proba(X)[:,1];pte=model.predict_proba(XT)[:,1]
 d={'month':test['month'],'test_count':int(len(YT)),'positive_rate':float(YT.mean()),'auc':float(roc_auc_score(YT,pte)),
    'all_quote_ev':float((ret-20).mean()/100),'train_auc':float(roc_auc_score(Y,ptr)),'bands':{}}
 for q in [.50,.80,.95]:
  threshold=float(np.quantile(ptr,q));k=pte>=threshold
  d['bands'][str(q)]={'train_quantile':q,'threshold':threshold,'kept':int(k.sum()),'coverage':float(k.mean()),
     'hit_rate':float(YT[k].mean()) if k.any() else None,
     'quote_ev':float((ret[k]-20).mean()/100) if k.any() else None}
 print('HORIZON_ECON',d,flush=True)
 out.append(d)
 Path('/mnt/data/r9_m60_expanded/full_results/horizon_5sec_economics.json').write_text(json.dumps(out,indent=2)+'\n')
