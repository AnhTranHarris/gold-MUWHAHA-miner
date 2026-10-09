"""FEB047 constrained exit-queue neighborhood, all February in-sample; no day/date as signal."""
import sys,json,time,itertools
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/feb047');import profit_protect_047 as v
from queued_reduce_only_047 import run
O=Path('/mnt/data/feb047')
rows=[]
parameters=[]
for retreat,wind,batch,cool,pmin,side,needdd in itertools.product([2.,3.,4.],[12,36],[16,32,48],[60.,120.],[3.,7.],[400],[0.,5000.]):
    parameters.append(dict(retreat_usd=retreat,window_samples=wind,min_profit=pmin,close_batch=batch,cooldown_seconds=cool,side_limit=side,source_only=True,require_dd=needdd))
print('PARAMETERS',len(parameters),flush=True)
t0=time.monotonic()
for i,p in enumerate(parameters):
    ex,px,n,actions,cps,ps=run(v.E,v.X,v.R,v.D,v.P,v.S,v.t,v.a,v.b,v.exit_order,v.monitor,**p,max_orders_sec=10)
    row={'i':i,'params':p,'net':round(float(px.sum()),3),'early_exits':int(n),'actions':int(actions),'max_closes_per_sec':int(cps),'max_orders_per_second':int(ps)}
    if row['net']>=199000:row.update(v.evaluate(ex,px))
    rows.append(row)
    if i%30==0:
        (O/'FEB047_QUEUED_SCREEN.json').write_text(json.dumps(rows,indent=2));print('PROGRESS',i,'elapsed',round(time.monotonic()-t0,1),'qualified',sum(x.get('net',0)>=200000 for x in rows),flush=True)
(O/'FEB047_QUEUED_SCREEN.json').write_text(json.dumps(rows,indent=2))
q=sorted([r for r in rows if r.get('net',0)>=200000 and r.get('dd',1e9)<19308.087],key=lambda r:(r['dd'],-r['net']))
print('COMPLETE',len(rows),'qualified',len(q),'elapsed',round(time.monotonic()-t0,1),flush=True)
for r in q[:15]:print('FRONTIER',json.dumps(r),flush=True)
if q:
    r=q[0];ex,px,*_=run(v.E,v.X,v.R,v.D,v.P,v.S,v.t,v.a,v.b,v.exit_order,v.monitor,**r['params'],max_orders_sec=10)
    assert abs(v.evaluate(ex,px)['dd']-r['dd'])<.001
    np.savez_compressed(O/'FEB047_QUEUED_SCREEN_BEST.npz',E=v.E,X=ex,R=v.R,D=v.D,P=px,S=v.S)
    (O/'FEB047_QUEUED_SCREEN_BEST.json').write_text(json.dumps(r,indent=2))