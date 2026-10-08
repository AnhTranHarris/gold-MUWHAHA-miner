import sys,json,numpy as np
from numba import njit
sys.path.insert(0,'/mnt/data')
import gamma02_m1_density as gmd
import gamma02_ny_campaign_inventory_portfolio_001 as g
import gamma02_one_event_per_tick_audit_014 as base
import gamma02_rebreak_latency_017 as lat
import gamma02_rebreak_desk_specific_018 as desk

# Current conservative desk-specific base:
LO_RESET=50; LO_LAT=0; NY17_RESET=500; NY17_LAT=1000
# Hour-specific London conviction thresholds from conservative base.
THR=np.array([0,0,0,0,0,0,0,1000,3000,0,0,2000,0,4000,4000,3000,0,0,0,0,0,0,0,0],dtype=np.int32)
# NY17 lateBias minimum displacement by 10m subphase.
NY17_MIN=np.array([8000,8000,6000,3000,1000,0],dtype=np.int32)
# NY18 lateClean displacement bands.
NY18_MIN=np.array([0,0,500,500,2000,1000],dtype=np.int32)
NY18_MAX=np.array([1_000_000_000,1_000_000_000,1_000_000_000,1_000_000_000,1_000_000_000,6000],dtype=np.int32)
# NY lifecycle arrays from earned subphase map.
TP16=np.array([40000,0,40000,40000,40000,0],dtype=np.int32)
SL16=np.array([20000,40000,40000,60000,60000,40000],dtype=np.int32)
H16=np.array([1200000,1200000,900000,1200000,1200000,1200000],dtype=np.int64)
TP17=np.array([80000,80000,120000,80000,0,120000],dtype=np.int32)
SL17=np.array([40000,40000,60000,40000,60000,120000],dtype=np.int32)
H17=np.array([1800000]*6,dtype=np.int64)
TP18=np.array([12000,12000,12000,8000,4000,4000],dtype=np.int32)
SL18=np.array([8000,8000,6000,8000,1000,2000],dtype=np.int32)
H18=np.array([60000,60000,20000,30000,5000,10000],dtype=np.int64)

@njit(cache=True)
def london_rule(hour,h4,h1,m15,m5):
    # returns hold_ms or 0 when not an earned London/overlap state
    if h4!=1 or h1!=1:return 0
    if hour==7:
        if m15==-1 and m5==-1:return 1800000
    elif hour==8:
        if m15==-1 and m5==-1:return 300000
        if m15==-1 and m5==1:return 900000
    elif hour==9:
        if (m15==-1 and m5==-1) or (m15==1 and m5==-1):return 1800000
    elif hour==11:
        if m15==-1 and m5==-1:return 1800000
        if m15==-1 and m5==1:return 1800000
        if m15==1 and m5==-1:return 900000
    elif hour==12:
        if m15==-1 and m5==-1:return 1800000
        if m15==-1 and m5==1:return 900000
        if m15==1 and m5==-1:return 1800000
    elif hour==13:
        if (m15==-1 and m5==-1) or (m15==-1 and m5==1) or (m15==1 and m5==-1):return 1800000
    elif hour==14:
        if m15==-1 and m5==-1:return 1800000
        if m15==-1 and m5==1:return 900000
    elif hour==15:
        if (m15==-1 and m5==1) or (m15==1 and m5==-1) or (m15==1 and m5==1):return 1800000
    return 0

@njit(cache=True)
def ny_dir(hour,h4,h1,m15,m5):
    if hour==16:
        if h4==-1 and h1==-1 and m15==-1 and m5==-1:return -1
        if h4==1 and h1==1 and m15==1 and m5==-1:return 1
        if h4==1 and h1==1 and m15==-1 and m5==1:return 1
    elif hour==17:
        if h4==-1 and h1==-1 and m15==-1 and m5==-1:return -1
        if h4==1 and h1==1 and m15==-1 and m5==-1:return 1
    elif hour==18:
        if h4==-1 and h1==-1 and m15==-1 and m5==-1:return -1
    return 0

@njit(cache=True)
def heartbeat_candidates(t,mid,h4,h1,m15,m5,interval_ms,group_code):
    # group: 0 London/overlap, 1 NY17, 2 NY16, 3 NY18, 4 all
    cap=2000000
    idx=np.empty(cap,np.int64); dr=np.empty(cap,np.int8); src=np.empty(cap,np.int16); hold=np.empty(cap,np.int64); tp=np.empty(cap,np.int32); sl=np.empty(cap,np.int32)
    n=0;curmin=np.int64(-1);anchor=0;last_fire=np.full(24,np.int64(-10**18));last_eligible=np.zeros(24,np.int8)
    for i in range(t.size):
        ti=t[i]; minute=(ti//60000)*60000; hour=int((ti//3600000)%24); b10=int((ti//600000)%6)
        if minute!=curmin:
            curmin=minute;anchor=int(mid[i])
        eligible=False; d=0; hh=0; tt=0; ss=0
        if hour<=15 and ((group_code==0) or group_code==4):
            hm=london_rule(hour,int(h4[i]),int(h1[i]),int(m15[i]),int(m5[i]))
            if hm>0:
                d=1; disp=(int(mid[i])-anchor)
                if disp>=THR[hour]:
                    eligible=True;hh=hm;tt=0;ss=0
        elif hour==17 and ((group_code==1) or group_code==4):
            d=ny_dir(17,int(h4[i]),int(h1[i]),int(m15[i]),int(m5[i]))
            if d!=0:
                disp=(int(mid[i])-anchor)*d
                if disp>=NY17_MIN[b10]:
                    eligible=True;hh=H17[b10];tt=TP17[b10];ss=SL17[b10]
        elif hour==16 and ((group_code==2) or group_code==4):
            d=ny_dir(16,int(h4[i]),int(h1[i]),int(m15[i]),int(m5[i]))
            if d!=0:
                disp=(int(mid[i])-anchor)*d
                if disp>=500:
                    eligible=True;hh=H16[b10];tt=TP16[b10];ss=SL16[b10]
        elif hour==18 and ((group_code==3) or group_code==4):
            d=ny_dir(18,int(h4[i]),int(h1[i]),int(m15[i]),int(m5[i]))
            if d!=0:
                disp=(int(mid[i])-anchor)*d
                if disp>=NY18_MIN[b10] and disp<NY18_MAX[b10]:
                    eligible=True;hh=H18[b10];tt=TP18[b10];ss=SL18[b10]
        if not eligible:
            last_eligible[hour]=0
            continue
        # heartbeat starts on first eligible tick and then at interval while eligibility persists
        fire=False
        if last_eligible[hour]==0: fire=True
        elif ti-last_fire[hour]>=interval_ms: fire=True
        last_eligible[hour]=1
        if fire:
            last_fire[hour]=ti
            if n<cap:
                idx[n]=i;dr[n]=d;src[n]=hour;hold[n]=hh;tp[n]=tt;sl[n]=ss;n+=1
    return idx[:n],dr[:n],src[:n],hold[:n],tp[:n],sl[:n]

def heartbeat_events(data,interval_ms,group_code):
    t,a,b,mid,h4,h1,m15,m5=data
    ii,dd,src,hold,tp,sl=heartbeat_candidates(t,mid,h4,h1,m15,m5,int(interval_ms),int(group_code))
    # outcome loop by unique lifecycle group for speed
    parts=[]
    keys=np.stack((src,hold,tp,sl),axis=1)
    if len(ii)==0:return tuple(np.empty(0,dtype=d) for d in [np.int64,np.int64,np.float64,np.int8,np.int16])
    # numpy unique rows
    uniq=np.unique(keys,axis=0)
    for s,h,tt,ss in uniq:
        m=(src==s)&(hold==h)&(tp==tt)&(sl==ss); jj=ii[m]; d=dd[m]
        if int(s)<=15:
            ent=np.where(d>0,a[jj],b[jj]).astype(np.int64); x=np.searchsorted(t,t[jj]+int(h),side='left');x=np.minimum(x,len(t)-1); ex=np.where(d>0,b[x],a[x]).astype(np.int64);p=((ex-ent)*d)/1000.-0.02;rs=np.full(jj.size,3,np.int8);xt=t[x]
        else:
            xt,p,rs=g.precompute_outcomes(t,a,b,jj,d,int(tt),int(ss),int(h))
        parts.append((t[jj],xt,p,rs,np.full(jj.size,int(s),np.int16)))
    arr=[np.concatenate([q[k] for q in parts]) for k in range(5)];o=np.argsort(arr[0],kind='stable');return tuple(x[o] for x in arr)

def union_dedup(primary,extra):return lat.union_dedup(primary,extra)

def base_desk(data):
    t,a,b,mid,h4,h1,m15,m5=data
    Plo=base.build_lo(t,a,b,mid,h4,h1,m15,m5);Pny=base.build_ny(t,a,b,mid,h4,h1,m15,m5)
    L=union_dedup(Plo,lat.rb_lo(t,a,b,mid,h4,h1,m15,m5,LO_RESET,LO_LAT))
    N=union_dedup(Pny,lat.rb_ny17(t,a,b,mid,h4,h1,m15,m5,NY17_RESET,NY17_LAT))
    arr=[np.concatenate((L[k],N[k])) for k in range(5)];o=np.argsort(arr[0],kind='stable');return tuple(x[o] for x in arr)

def eval_interval(data,B,interval_ms,group_code,cap):
    H=heartbeat_events(data,interval_ms,group_code);A=union_dedup(B,H)
    ae,ap,asrc,ar,sk,mo=g.cap_select(*A,cap);r=g.summarize(ae,ap,asrc,ar,sk,mo)
    r.update(interval_ms=int(interval_ms),group_code=int(group_code),heartbeat_candidates=len(H[0]),candidate_events=len(A[0]),cap=int(cap));return r

def run(group,cap,out):
    gm={'london':0,'ny17':1,'ny16':2,'ny18':3,'all':4};gc=gm[group]
    t,a,b,mid,h4,h1,m15,m5,es,ee=gmd.prep();data=(t,a,b,mid,h4,h1,m15,m5);B=base_desk(data)
    rows=[]
    for ms in (250,500,1000,2000,5000,10000,15000,30000,60000):
        r=eval_interval(data,B,ms,gc,cap);rows.append(r);print(json.dumps({k:r[k] for k in ['interval_ms','heartbeat_candidates','candidate_events','net','trades','pf','exp','balance_dd','sources']}),flush=True)
        # atomic partial save after each interval
        with open(out+'.partial','w') as f:json.dump({'candidate':'GAMMA02_CAMPAIGN_HEARTBEAT_UNIQUE_TICK_019','group':group,'cap':cap,'rows':rows},f,indent=2)
    rows.sort(key=lambda x:x['net'],reverse=True)
    with open(out,'w') as f:json.dump({'candidate':'GAMMA02_CAMPAIGN_HEARTBEAT_UNIQUE_TICK_019','group':group,'cap':cap,'rows':rows},f,indent=2)

if __name__=='__main__':
    import argparse;ap=argparse.ArgumentParser();ap.add_argument('--group',choices=['london','ny17','ny16','ny18','all'],required=True);ap.add_argument('--cap',type=int,default=128);ap.add_argument('--out',required=True);z=ap.parse_args();run(z.group,z.cap,z.out)