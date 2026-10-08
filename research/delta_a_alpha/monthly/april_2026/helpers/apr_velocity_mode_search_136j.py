import sys,json,itertools,heapq,time,numpy as np
from pathlib import Path
sys.path.insert(0,'/mnt/data/april_vertical_work')
import apr_vertical_portfolio_136g as A
O=Path('/mnt/data/april_vertical_work')

def load(path,prefix):
 z=np.load(path);return tuple(z[f'{prefix}_{k}'] for k in ['E_MS','X_MS','R','D','P','H'])
N0={k:load(O/'apr_native_conviction_streams_136d.npz',k) for k in ['PF5','PF10','WIN80','PF20']}
N1={k:load(O/'apr_native_conviction_refine_streams_136h.npz',k) for k in ['PF12','PF15','WIN87','WIN90']}
N={**N0,**N1}
HV={k:load(O/'apr_session_grid_streams_136b.npz','HIGHVOL_'+k) for k in ['BROAD','PF8','PF20']}
AS={k:load(O/'apr_session_grid_streams_136b.npz','ASIA_'+k) for k in ['BROAD','PF8','PF20']}
REC=A.REC
SYN=dict(net=38353.96,gross_loss=-2414.22,pf=16.886688,win=.86759242,expectancy=1.207694)

def allm(s):
 return s['net']>=SYN['net'] and s['gross_loss']>=SYN['gross_loss'] and s['pf']>=SYN['pf'] and s['win']>=SYN['win'] and s['expectancy']>=SYN['expectancy'] and s['positive_weeks']==s['active_weeks']

def run():
 rows=[];t0=time.time()
 for nm,hm,am in itertools.product(N,HV,AS):
  rec=A.dedup([('NATIVE',N[nm]),('HIGHVOL',HV[hm]),('ASIA',AS[am]),('RECOVERY',REC)])
  for cap in [128,160,176,192,224,256,320,448]:
   q,mo,sk=A.caprec(rec,cap);s=A.score(q);s.update(native=nm,hv=hm,asia=am,cap=cap,maxopen=mo,skips=sk,all_metrics=allm(s));rows.append(s)
 good=[r for r in rows if r['all_metrics']]
 good.sort(key=lambda r:(-r['trades'],-r['net'],abs(r['gross_loss'])))
 # Pareto-ish top by trades/net/heat
 top_trade=good[:30]
 top_net=sorted(good,key=lambda r:(-r['net'],-r['trades']))[:30]
 top_heat=sorted(good,key=lambda r:(r['maxopen'],-r['trades'],-r['net']))[:30]
 out={'unit':'DAA_APRIL_VELOCITY_MODE_SEARCH_136J','status':'COMPLETE','all_metric_count':len(good),'top_trade':top_trade,'top_net':top_net,'top_low_heat':top_heat,'runtime_s':time.time()-t0}
 (O/'apr_velocity_mode_search_136j.json').write_text(json.dumps(out,indent=2))
 print('good',len(good),'runtime',out['runtime_s'])
 for r in top_trade[:15]: print(json.dumps({k:r[k] for k in ['native','hv','asia','cap','net','trades','gross_loss','pf','win','expectancy','balance_dd','maxopen','skips','positive_days','active_days','positive_weeks','active_weeks']}))
if __name__=='__main__':run()