import sys, numpy as np
from pathlib import Path
sys.path.insert(0,'/mnt/data/h1v2/src')
sys.path.insert(0,'/mnt/data/h1v2/source_exact/pinned_original/original_v2/src')
from h1v2_teacher import read_ticks
from router_v2_features import Quote
from router_v2_labels import ActivePath

def validate(month='01',n=320):
 t,b,a=read_ticks(f'/mnt/data/XAUUSD_DUKAS_2026_{month}_ticks.csv.gz')
 d=np.load(f'/mnt/data/h1v2/results/h1v2_dukascopy_{month}_oracle_labels.npz')
 entries=d['tick_index'];v=d['net'];outix=d['exit_tick_index']
 rng=np.random.default_rng(20261102)
 rows=np.unique(np.r_[np.linspace(0,len(entries)-1,n//2,dtype=int),rng.choice(len(entries),n//2,replace=False)])
 errs=[];compared=0
 for k in rows:
  i=int(entries[k]);q=Quote(int(t[i]),float(b[i]),float(a[i]))
  for opt,side in enumerate((1,-1)):
   path=ActivePath(q,side)
   result=None
   for j in range(i+1,min(i+25000,len(t))):
    result=path.update(Quote(int(t[j]),float(b[j]),float(a[j])))
    if result is not None:break
   if result is None:
    if outix[k,opt]!=-1:errs.append(('missing outcome',int(k),int(opt),int(outix[k,opt])))
    continue
   compared+=1
   if int(outix[k,opt])!=j or abs(float(v[k,opt])-float(result.net))>1e-4:
    errs.append((int(k),int(opt),int(outix[k,opt]),j,float(v[k,opt]),result.net,result.exit_type))
 print({'month':month,'rows':len(rows),'compared':compared,'mismatches':len(errs),'examples':errs[:8]})
 if errs:raise AssertionError(errs[:8])
if __name__=='__main__':
 for month in ['01','02','06','07']:validate(month,240)
