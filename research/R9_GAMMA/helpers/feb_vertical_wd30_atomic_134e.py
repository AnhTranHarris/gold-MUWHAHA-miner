import sys,json
from pathlib import Path
import numpy as np
sys.path[:0]=['/mnt/data','/mnt/data/gamma02_jan_repro']
import feb_vertical_stack_134b as V
BASE=Path('/mnt/data/gamma02_jan_repro')
def loadq(fn):
 z=np.load(BASE/fn);Q=tuple(z[x] for x in ['E','X','R','D','P','H']);z.close();return Q
def q(z,pre):return tuple(z[pre+'_'+x] for x in ['E','X','R','D','P','H'])
D=V.load_month();z=np.load(BASE/'feb_baseline_components_133b.npz');B={k:z[k] for k in z.files};z.close();cov=q(B,'COV');cold=q(B,'COLD');asia=q(B,'ASIA02_CONT');late=q(B,'LATE21_LONG');wd=loadq('feb_wd_L30_C384_134e.npz');G=loadq('feb_learner_D_stream_133c.npz');N=loadq('feb_native_pf10_stream_134c.npz')
S,dup=V.dedup([N,cov,G,cold,asia,late]);SS,smo,ssk=V.cap(S,640);rows=[]
for gcap in [320,384,448,512,600,640,703,768]:
 Q,mo,sk=V.merge_watchdog(wd,SS,gcap);r=V.score(D,Q,False);r.update(global_cap=gcap,global_maxopen_event=mo);rows.append(r);print(json.dumps({k:r[k] for k in ['global_cap','net','trades','gross_loss','pf','win','expectancy','balance_dd','positive_days','beat_days','positive_weeks','beat_weeks','global_maxopen_event']}),flush=True)
# exact best risk-adjusted and best net
picks=[max(rows,key=lambda x:x['net']),max(rows,key=lambda x:(x['pf'],x['net']))];seen=set();final=[]
for r in picks:
 if r['global_cap'] in seen:continue
 seen.add(r['global_cap']);Q,_,_=V.merge_watchdog(wd,SS,r['global_cap']);x=V.score(D,Q,True);x['global_cap']=r['global_cap'];final.append(x);print('EXACT',json.dumps({k:x[k] for k in ['global_cap','net','trades','gross_loss','pf','win','expectancy','balance_dd','equity_dd','maxopen_exact','positive_days','beat_days','positive_weeks','beat_weeks']}),flush=True)
(BASE/'feb_vertical_wd30_atomic_134e.json').write_text(json.dumps({'rows':rows,'finalists':final},indent=2))