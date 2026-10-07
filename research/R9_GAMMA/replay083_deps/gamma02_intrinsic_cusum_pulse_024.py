import sys,json,numpy as np
from numba import njit
sys.path.insert(0,'/mnt/data')
import gamma02_m1_density as gmd
import gamma02_ny_campaign_inventory_portfolio_001 as g
import gamma02_campaign_heartbeat_019 as hb
import gamma02_rebreak_latency_017 as lat
import gamma02_hour_specific_heartbeat_022 as h22

CFG={7:1000,8:500,9:250,11:1000,12:250,13:250,14:1000,15:1000}
THRESHOLDS=(50,100,200,300,500,750,1000,1500,2000,3000,5000)

@njit(cache=True)
def pulse_candidates(t,mid,h4,h1,m15,m5,threshold_raw,group_code):
    # CUSUM-like favorable intrinsic clock. At most one event per source per market tick.
    cap=1000000
    idx=np.empty(cap,np.int64);dr=np.empty(cap,np.int8);src=np.empty(cap,np.int16);hold=np.empty(cap,np.int64);tp=np.empty(cap,np.int32);sl=np.empty(cap,np.int32)
    n=0;curmin=np.int64(-1);anchor=0;prev_mid=int(mid[0]);acc=np.zeros(24,np.int64);prev_dir=np.zeros(24,np.int8);prev_elig=np.zeros(24,np.int8)
    for i in range(1,t.size):
        ti=t[i];midx=int(mid[i]);minute=(ti//60000)*60000;hour=int((ti//3600000)%24);b10=int((ti//600000)%6)
        if minute!=curmin:
            curmin=minute;anchor=midx
        eligible=False;d=0;hh=0;tt=0;ss=0
        if hour<=15 and (group_code==0 or group_code==4):
            hm=hb.london_rule(hour,int(h4[i]),int(h1[i]),int(m15[i]),int(m5[i]))
            if hm>0:
                d=1;disp=midx-anchor
                if disp>=hb.THR[hour]:eligible=True;hh=hm
        elif hour==17 and (group_code==1 or group_code==4):
            d=hb.ny_dir(17,int(h4[i]),int(h1[i]),int(m15[i]),int(m5[i]))
            if d!=0:
                disp=(midx-anchor)*d
                if disp>=hb.NY17_MIN[b10]:eligible=True;hh=hb.H17[b10];tt=hb.TP17[b10];ss=hb.SL17[b10]
        elif hour==16 and (group_code==2 or group_code==4):
            d=hb.ny_dir(16,int(h4[i]),int(h1[i]),int(m15[i]),int(m5[i]))
            if d!=0:
                disp=(midx-anchor)*d
                if disp>=500:eligible=True;hh=hb.H16[b10];tt=hb.TP16[b10];ss=hb.SL16[b10]
        elif hour==18 and (group_code==3 or group_code==4):
            d=hb.ny_dir(18,int(h4[i]),int(h1[i]),int(m15[i]),int(m5[i]))
            if d!=0:
                disp=(midx-anchor)*d
                if disp>=hb.NY18_MIN[b10] and disp<hb.NY18_MAX[b10]:eligible=True;hh=hb.H18[b10];tt=hb.TP18[b10];ss=hb.SL18[b10]
        if not eligible:
            acc[hour]=0;prev_dir[hour]=0;prev_elig[hour]=0;prev_mid=midx;continue
        if prev_elig[hour]==0 or prev_dir[hour]!=d:
            acc[hour]=0;prev_dir[hour]=d;prev_elig[hour]=1;prev_mid=midx;continue
        step=(midx-prev_mid)*d
        v=acc[hour]+step
        if v<0:v=0
        acc[hour]=v
        prev_mid=midx
        if acc[hour]>=threshold_raw:
            acc[hour]=0
            if n<cap:
                idx[n]=i;dr[n]=d;src[n]=hour;hold[n]=hh;tp[n]=tt;sl[n]=ss;n+=1
    return idx[:n],dr[:n],src[:n],hold[:n],tp[:n],sl[:n]

def pulse_events(data,threshold_raw,group_code):
    t,a,b,mid,h4,h1,m15,m5=data
    ii,dd,src,hold,tp,sl=pulse_candidates(t,mid,h4,h1,m15,m5,int(threshold_raw),int(group_code))
    if len(ii)==0:return tuple(np.empty(0,dtype=d) for d in [np.int64,np.int64,np.float64,np.int8,np.int16])
    parts=[];keys=np.stack((src,hold,tp,sl),axis=1)
    for s,h,tt,ss in np.unique(keys,axis=0):
        m=(src==s)&(hold==h)&(tp==tt)&(sl==ss);jj=ii[m];d=dd[m]
        if int(s)<=15:
            ent=np.where(d>0,a[jj],b[jj]).astype(np.int64);x=np.searchsorted(t,t[jj]+int(h),side='left');x=np.minimum(x,len(t)-1);ex=np.where(d>0,b[x],a[x]).astype(np.int64);p=((ex-ent)*d)/1000.-0.02;rs=np.full(jj.size,3,np.int8);xt=t[x]
        else:
            xt,p,rs=g.precompute_outcomes(t,a,b,jj,d,int(tt),int(ss),int(h))
        parts.append((t[jj],xt,p,rs,np.full(jj.size,int(s),np.int16)))
    arr=[np.concatenate([q[k] for q in parts]) for k in range(5)];o=np.argsort(arr[0],kind='stable');return tuple(x[o] for x in arr)

def concat(parts):
    non=[p for p in parts if p is not None and len(p[0])]
    if not non:return tuple(np.empty(0,dtype=d) for d in [np.int64,np.int64,np.float64,np.int8,np.int16])
    arr=[np.concatenate([p[k] for p in non]) for k in range(5)];o=np.argsort(arr[0],kind='stable');return tuple(x[o] for x in arr)

def union_many(parts):
    A=parts[0]
    for E in parts[1:]:
        if E is not None and len(E[0]):A=lat.union_dedup(A,E)
    return A

def subset(E,h):
    m=E[4]==h;return tuple(x[m] for x in E)

def heartbeat_frontier(data):
    B=hb.base_desk(data);parts=[]
    for h,ms in CFG.items():parts.append(subset(hb.heartbeat_events(data,ms,0),h))
    H=concat(parts);E18=hb.heartbeat_events(data,250,3)
    return union_many([B,H,E18])

def eval_arr(A,cap):
    ae,ap,asrc,ar,sk,mo=g.cap_select(*A,int(cap));return g.summarize(ae,ap,asrc,ar,sk,mo)

def run(group,cap,out):
    gm={'london':0,'ny17':1,'ny16':2,'ny18':3,'all':4};gc=gm[group]
    t,a,b,mid,h4,h1,m15,m5,es,ee=gmd.prep();data=(t,a,b,mid,h4,h1,m15,m5);A0=heartbeat_frontier(data)
    base=eval_arr(A0,cap);rows=[]
    print('BASE',json.dumps({k:base[k] for k in ['net','trades','pf','exp','balance_dd','sources']}),flush=True)
    for th in THRESHOLDS:
        E=pulse_events(data,th,gc);A=lat.union_dedup(A0,E);r=eval_arr(A,cap);r.update(threshold_raw=th,group=group,pulse_candidates=len(E[0]),candidate_events=len(A[0]),cap=cap);rows.append(r)
        print(json.dumps({k:r[k] for k in ['threshold_raw','pulse_candidates','net','trades','pf','exp','balance_dd','sources']}),flush=True)
        with open(out+'.partial','w') as f:json.dump({'candidate':'GAMMA02_INTRINSIC_CUSUM_PULSE_024','group':group,'base':base,'rows':rows},f,indent=2)
    rows.sort(key=lambda x:x['net'],reverse=True)
    with open(out,'w') as f:json.dump({'candidate':'GAMMA02_INTRINSIC_CUSUM_PULSE_024','group':group,'base':base,'rows':rows},f,indent=2)

if __name__=='__main__':
    import argparse;ap=argparse.ArgumentParser();ap.add_argument('--group',choices=['london','ny17','ny16','ny18','all'],required=True);ap.add_argument('--cap',type=int,default=128);ap.add_argument('--out',required=True);z=ap.parse_args();run(z.group,z.cap,z.out)