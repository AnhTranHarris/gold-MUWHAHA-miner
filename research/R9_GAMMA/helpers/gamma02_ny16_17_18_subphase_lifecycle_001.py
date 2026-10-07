import sys,json,time,numpy as np
sys.path.insert(0,'/mnt/data')
import gamma02_m1_density as gmd
import gamma02_ny_campaign_inventory_portfolio_001 as g

CFG16={
  0:(40000,20000,1200000),
 10:(0,40000,1200000),
 20:(40000,40000,900000),
 30:(40000,60000,1200000),
 40:(40000,60000,1200000),
 50:(0,40000,1200000),
}
CFG17={
  0:(80000,40000,1800000),
 10:(80000,40000,1800000),
 20:(120000,60000,1800000),
 30:(80000,40000,1800000),
 40:(0,60000,1800000),
 50:(120000,120000,1800000),
}
CFG18={
  0:(12000,8000,60000),
 10:(12000,8000,60000),
 20:(12000,6000,20000),
 30:(8000,8000,30000),
 40:(4000,1000,5000),
 50:(4000,2000,10000),
}

SIGS={16:g.SIG16,17:g.SIG17,18:g.SIG18}
CFGS={16:CFG16,17:CFG17,18:CFG18}

def build_hour(t,a,b,h4,h1,m15,m5,ei,ed,eh,ess,hour):
    p=np.nonzero((eh==hour)&(ess==4))[0]
    idx=ei[p];dr=ed[p]
    keep=np.zeros(idx.size,dtype=np.bool_)
    allowed=SIGS[hour]
    for k,i in enumerate(idx):
        sig=(int(h4[i]),int(h1[i]),int(m15[i]),int(m5[i]),int(dr[k]))
        if sig in allowed: keep[k]=True
    idx=idx[keep];dr=dr[keep]
    mins=((t[idx]//60000)%60).astype(np.int16)
    parts=[]
    for lo,(tp,sl,hold) in CFGS[hour].items():
        m=(mins>=lo)&(mins<lo+10)
        ii=idx[m];dd=dr[m]
        ex,pnl,rs=g.precompute_outcomes(t,a,b,ii,dd,tp,sl,hold)
        times=t[ii];src=np.full(times.size,hour,dtype=np.int8)
        parts.append((times,ex,pnl,rs,src))
    arr=[np.concatenate([q[j] for q in parts]) for j in range(5)]
    o=np.argsort(arr[0],kind='stable')
    return tuple(x[o] for x in arr)

def prepare():
    t,a,b,mid,h4,h1,m15,m5,es,ee=gmd.prep()
    ei,ed,eh,ess,edisp=g.build_perm_extension_events(t,mid,h4,h1,m15,m5,2,50,200)
    specs=[build_hour(t,a,b,h4,h1,m15,m5,ei,ed,eh,ess,h) for h in (16,17,18)]
    arr=[np.concatenate([q[j] for q in specs]) for j in range(5)]
    o=np.argsort(arr[0],kind='stable')
    return tuple(x[o] for x in arr)

def run_cap(arr,cap):
    ae,ap,asrc,ar,sk,mo=g.cap_select(*arr,int(cap))
    out=g.summarize(ae,ap,asrc,ar,sk,mo)
    out['cap']=int(cap);out['cfg16']=CFG16;out['cfg17']=CFG17;out['cfg18']=CFG18
    return out

def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--caps',default='16,32,64,96,128,160,192,256');ap.add_argument('--out',required=True)
    z=ap.parse_args();caps=[int(x) for x in z.caps.split(',') if x]
    st=time.time();arr=prepare();rows=[run_cap(arr,c) for c in caps]
    obj={'candidate':'GAMMA02_NY16_17_18_SUBPHASE_LIFECYCLE_001','rows':rows,'elapsed_s':round(time.time()-st,3)}
    with open(z.out,'w') as f:json.dump(obj,f,indent=2)
    for r in rows:
        print(json.dumps({k:r[k] for k in ['cap','net','trades','pf','exp','win','balance_dd','maxopen','sources']}),flush=True)
if __name__=='__main__':main()
