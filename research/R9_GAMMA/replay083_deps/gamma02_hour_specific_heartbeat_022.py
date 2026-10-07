import sys,json,numpy as np
sys.path.insert(0,'/mnt/data')
import gamma02_m1_density as gmd
import gamma02_ny_campaign_inventory_portfolio_001 as g
import gamma02_campaign_heartbeat_019 as hb
import gamma02_rebreak_latency_017 as lat

HOURS=(7,8,9,11,12,13,14,15)
INTERVALS=(0,250,500,1000,2000,5000,10000)

def concat_events(parts):
    non=[p for p in parts if p is not None and len(p[0])]
    if not non:return tuple(np.empty(0,dtype=d) for d in [np.int64,np.int64,np.float64,np.int8,np.int16])
    arr=[np.concatenate([p[k] for p in non]) for k in range(5)];o=np.argsort(arr[0],kind='stable');return tuple(x[o] for x in arr)

def union_many(parts):
    A=parts[0]
    for E in parts[1:]:
        if E is not None and len(E[0]):A=lat.union_dedup(A,E)
    return A

def subset_src(E,h):
    m=E[4]==h
    return tuple(x[m] for x in E)

def eval_cfg(B,E18,cache,cfg,cap):
    hs=[cache[(h,cfg[h])] for h in HOURS if cfg[h]>0]
    H=concat_events(hs)
    A=union_many([B,H,E18])
    ae,ap,asrc,ar,sk,mo=g.cap_select(*A,cap);r=g.summarize(ae,ap,asrc,ar,sk,mo)
    r.update(cap=cap,cfg_ms={str(h):int(cfg[h]) for h in HOURS},candidate_events=len(A[0]));return r

def run(cap,out,passes=2):
    t,a,b,mid,h4,h1,m15,m5,es,ee=gmd.prep();data=(t,a,b,mid,h4,h1,m15,m5);B=hb.base_desk(data);E18=hb.heartbeat_events(data,250,3)
    cache={}
    for ms in INTERVALS:
        if ms==0:
            for h in HOURS:cache[(h,0)]=None
        else:
            E=hb.heartbeat_events(data,ms,0)
            for h in HOURS:cache[(h,ms)]=subset_src(E,h)
    cfg={h:1000 for h in HOURS};history=[]
    base=eval_cfg(B,E18,cache,cfg,cap);history.append({'stage':'start',**base});print('START',json.dumps({k:base[k] for k in ['net','trades','pf','exp','balance_dd','cfg_ms','sources']}),flush=True)
    for p in range(passes):
        changed=False
        for h in HOURS:
            rows=[]
            old=cfg[h]
            for ms in INTERVALS:
                q=dict(cfg);q[h]=ms;r=eval_cfg(B,E18,cache,q,cap);r['tested_hour']=h;r['tested_ms']=ms;rows.append(r)
            rows.sort(key=lambda x:x['net'],reverse=True);best=rows[0];cfg[h]=best['tested_ms'];changed |= cfg[h]!=old
            history.append({'stage':f'pass{p+1}_hour{h}','alternatives':[{k:r[k] for k in ['tested_ms','net','trades','pf','exp','balance_dd']} for r in rows], 'chosen':{k:best[k] for k in ['tested_ms','net','trades','pf','exp','balance_dd','cfg_ms','sources']}})
            print('CHOOSE',p+1,h,cfg[h],round(best['net'],2),best['trades'],round(best['pf'],4),round(best['exp'],4),flush=True)
            with open(out+'.partial','w') as f:json.dump({'candidate':'GAMMA02_HOUR_SPECIFIC_HEARTBEAT_022','cfg':cfg,'history':history},f,indent=2)
        if not changed:break
    final=eval_cfg(B,E18,cache,cfg,cap)
    obj={'candidate':'GAMMA02_HOUR_SPECIFIC_HEARTBEAT_022','cfg':cfg,'final':final,'history':history}
    with open(out,'w') as f:json.dump(obj,f,indent=2)
    print('FINAL',json.dumps({k:final[k] for k in ['net','trades','pf','exp','balance_dd','cfg_ms','sources']}),flush=True)
if __name__=='__main__':
 import argparse;ap=argparse.ArgumentParser();ap.add_argument('--cap',type=int,default=128);ap.add_argument('--passes',type=int,default=2);ap.add_argument('--out',required=True);z=ap.parse_args();run(z.cap,z.out,z.passes)