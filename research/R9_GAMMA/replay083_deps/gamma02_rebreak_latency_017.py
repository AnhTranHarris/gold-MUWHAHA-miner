import sys,json,numpy as np
from numba import njit
sys.path.insert(0,'/mnt/data')
import gamma02_m1_density as gmd
import gamma02_ny_campaign_inventory_portfolio_001 as g
import gamma02_ny16_17_18_subphase_lifecycle_001 as cur
import gamma02_london_overlap_portfolio_001 as lo
import gamma02_time_decay_conviction_001 as td
import gamma02_one_event_per_tick_audit_014 as base
from gamma02_london_ny_hourly_conviction_002 import THR

@njit(cache=True)
def generic_rebreaks_latency(t,mid,h4,h1,reset_raw,min_elapsed_ms,start_hour=7,end_hour=18,min_depth=50):
    cap=1000000
    idx=np.empty(cap,np.int64); dr=np.empty(cap,np.int8); depth=np.empty(cap,np.int32); latency=np.empty(cap,np.int32)
    n=0; curmin=np.int64(-1); anchor=0; d=0; peak=0; armed=False; armed_at=np.int64(0)
    for i in range(t.size):
        m=(t[i]//60000)*60000; hr=int((t[i]//3600000)%24)
        if m!=curmin:
            curmin=m; anchor=int(mid[i]); d=int(h4[i]) if int(h4[i])==int(h1[i]) else 0; peak=0; armed=False; armed_at=0; continue
        if hr<start_hour or hr>end_hour or d==0: continue
        nd=int(h4[i]) if int(h4[i])==int(h1[i]) else 0
        if nd!=d:
            d=nd; anchor=int(mid[i]); peak=0; armed=False; armed_at=0
            if d==0: continue
        disp=(int(mid[i])-anchor)*d
        if peak>=min_depth and disp<=peak-reset_raw:
            if not armed:
                armed=True; armed_at=t[i]
        if armed and disp>=peak:
            lat=t[i]-armed_at
            if lat>=min_elapsed_ms:
                if n<cap:
                    idx[n]=i; dr[n]=d; depth[n]=peak; latency[n]=lat; n+=1
                armed=False; armed_at=0
        if disp>peak: peak=disp
    return idx[:n],dr[:n],depth[:n],latency[:n]

def union_dedup(primary,extra):
    E=[np.concatenate((primary[k],extra[k])) for k in range(5)]
    pri=np.r_[np.zeros(len(primary[0]),np.int8),np.ones(len(extra[0]),np.int8)]
    o=np.lexsort((pri,E[4],E[0])); E=[x[o] for x in E]
    keep=np.ones(len(E[0]),dtype=bool); keep[1:]=~((E[0][1:]==E[0][:-1])&(E[4][1:]==E[4][:-1]))
    return tuple(x[keep] for x in E)

def rb_lo(t,a,b,mid,h4,h1,m15,m5,reset,lat):
    ri,rd,rdep,rlat=generic_rebreaks_latency(t,mid,h4,h1,reset,lat,7,15,50); hr=((t[ri]//3600000)%24).astype(np.int8); parts=[]
    for hour,H4,H1,M15,M5,D,hs in lo.RULES:
        m=(hr==hour)&(h4[ri]==H4)&(h1[ri]==H1)&(m15[ri]==M15)&(m5[ri]==M5)&(rd==D)&(rdep>=THR.get(hour,0)); ii=ri[m]; dd=rd[m]
        ent=np.where(dd>0,a[ii],b[ii]); j=np.searchsorted(t,t[ii]+hs*1000,side='left'); j=np.minimum(j,len(t)-1); ex=np.where(dd>0,b[j],a[j]); p=((ex-ent)*dd)/1000.-0.02
        parts.append((t[ii],t[j],p,np.full(ii.size,3,np.int8),np.full(ii.size,hour,np.int16)))
    if not parts:return tuple(np.empty(0,dtype=d) for d in [np.int64,np.int64,np.float64,np.int8,np.int16])
    arr=[np.concatenate([q[k] for q in parts]) for k in range(5)]; o=np.argsort(arr[0],kind='stable'); return tuple(x[o] for x in arr)

def rb_ny17(t,a,b,mid,h4,h1,m15,m5,reset,lat):
    ri,rd,rdep,rlat=generic_rebreaks_latency(t,mid,h4,h1,reset,lat,16,18,50); hr=((t[ri]//3600000)%24).astype(np.int8); mins=((t[ri]//60000)%60).astype(np.int16); parts=[]; m17=td.MAP17['lateBias']
    hour=17; baseh=hr==hour; allowed=cur.SIGS[hour]; keep=np.zeros(ri.size,dtype=np.bool_)
    for q in np.nonzero(baseh)[0]:
        i=ri[q]; keep[q]=(int(h4[i]),int(h1[i]),int(m15[i]),int(m5[i]),int(rd[q])) in allowed
    for lo0,(tp,sl,hold) in cur.CFGS[hour].items():
        m=keep&(mins>=lo0)&(mins<lo0+10)&(rdep>=m17[lo0]); ii=ri[m]; dd=rd[m]; ex,p,rs=g.precompute_outcomes(t,a,b,ii,dd,tp,sl,hold)
        parts.append((t[ii],ex,p,rs,np.full(ii.size,hour,np.int16)))
    if not parts:return tuple(np.empty(0,dtype=d) for d in [np.int64,np.int64,np.float64,np.int8,np.int16])
    arr=[np.concatenate([q[k] for q in parts]) for k in range(5)]; o=np.argsort(arr[0],kind='stable'); return tuple(x[o] for x in arr)

def one(data,reset,lat,cap):
    t,a,b,mid,h4,h1,m15,m5=data
    Plo=base.build_lo(t,a,b,mid,h4,h1,m15,m5); Pny=base.build_ny(t,a,b,mid,h4,h1,m15,m5)
    if reset<=0:
        L=Plo; N=Pny
    else:
        L=union_dedup(Plo,rb_lo(t,a,b,mid,h4,h1,m15,m5,reset,lat)); N=union_dedup(Pny,rb_ny17(t,a,b,mid,h4,h1,m15,m5,reset,lat))
    arr=[np.concatenate((L[k],N[k])) for k in range(5)]; o=np.argsort(arr[0],kind='stable'); arr=[x[o] for x in arr]
    ae,ap,asrc,ar,sk,mo=g.cap_select(*arr,cap); r=g.summarize(ae,ap,asrc,ar,sk,mo); r.update(reset_raw=reset,min_elapsed_ms=lat,cap=cap,candidate_events=len(arr[0])); return r

def main(cap,out):
    t,a,b,mid,h4,h1,m15,m5,es,ee=gmd.prep(); data=(t,a,b,mid,h4,h1,m15,m5); rows=[]
    for lat in (0,250,500,1000,2000,3000,5000,10000):
        r=one(data,100,lat,cap); rows.append(r); print(json.dumps({k:r[k] for k in ['min_elapsed_ms','candidate_events','net','trades','pf','exp','balance_dd','sources']}),flush=True)
    json.dump({'candidate':'GAMMA02_REBREAK_LATENCY_017','cap':cap,'reset_raw':100,'rows':rows},open(out,'w'),indent=2)
if __name__=='__main__':
    import argparse; ap=argparse.ArgumentParser(); ap.add_argument('--cap',type=int,default=128); ap.add_argument('--out',required=True); z=ap.parse_args(); main(z.cap,z.out)