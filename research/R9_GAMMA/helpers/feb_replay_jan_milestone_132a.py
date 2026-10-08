import sys, json, hashlib, heapq
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/gamma02_jan_repro')

import gamma02_dynamic_watchdog_router_119 as wd
import gamma02_m1_density as gmd
import gamma02_jan_watchdog119_grid_layer_refinement_131a as wd131a
import gamma02_campaign_heartbeat_019 as hb
import jan_session_portfolio_131d as J
import jan_session_portfolio_lean_131d as L
import jan_profit_per_heat_atomic_131e as P

MONTH=2
MARKET=Path('/mnt/data/XAUUSD_DUKAS_2026_02_ticks.csv(3).gz')
BENCH=Path('/mnt/data/gamma02_jan_repro/r9_synth_feb_daily_weekly.json')
OUT=Path('/mnt/data/gamma02_jan_repro/feb_replay_jan_milestone_132a.json')


def sha256_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for ch in iter(lambda:f.read(8*1024*1024),b''): h.update(ch)
    return h.hexdigest()

# Preserve original loader, then redirect any Jan-hardcoded helper request to Feb.
_orig_prep=wd.prep_month
DATA=_orig_prep(MONTH)
t,a,b,mid,h4,h1,m15,m5=DATA[:8]
START,END=DATA[-2],DATA[-1]

def _feb_prep(_m):
    return DATA
wd.prep_month=_feb_prep
wd131a.wd.prep_month=_feb_prep
P.wd.prep_month=_feb_prep

# Rebind Jan portfolio module globals to Feb data/benchmark only; rules/parameters unchanged.
J.DATA=DATA; J.AASK=a; J.BBID=b; J.SYN=json.load(open(BENCH)); J.gmd.prep=lambda:DATA
L.J=J
P.J=J; P.L=L; P.gmd.prep=lambda:DATA

# Explicit target gate is required cross-month because Feb prep includes Jan warmup.
def build_coverage_targeted():
    D0=DATA; t,a,b,mid,h4,h1,m15,m5=D0[:8]
    E=hb.heartbeat_events(D0[:8],250,0); et,xt,pnl,reason,src=E
    idx=np.searchsorted(t,et); b10=((et//60000)%60)//10; j60=np.searchsorted(t,et-60000,side='left'); ticks60=idx-j60+1
    target=(et>=START)&(et<END)
    k=np.zeros(len(et),bool)
    k |= target&(src==9)&(b10==0)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==-1)
    k |= target&(src==11)&np.isin(b10,[2,3])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==-1)&(m5[idx]==-1)
    k |= target&(src==11)&(b10==3)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==-1)
    k |= target&(src==12)&np.isin(b10,[0,1,2])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==-1)&(m5[idx]==-1)
    k |= target&(src==12)&(b10==4)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==-1)&(ticks60<=210)
    k |= target&(src==13)&np.isin(b10,[2,3])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==-1)&(m5[idx]==-1)
    k |= target&(src==14)&(b10==3)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==-1)&(m5[idx]==1)
    k |= target&(src==15)&np.isin(b10,[2,3])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==1)
    parts=[tuple(z[k] for z in E)]
    E16=hb.heartbeat_events(D0[:8],250,2); e,x,p,r,s=E16
    i=np.searchsorted(t,e); b16=((e//60000)%60)//10; target16=(e>=START)&(e<END)
    k16=target16&(s==16)&(h4[i]==1)&(h1[i]==1)&(m15[i]==1)&(m5[i]==-1)&np.isin(b16,[0,3,4])
    parts.append(tuple(z[k16] for z in E16))
    arr=[np.concatenate([q[j] for q in parts]) for j in range(5)]; o=np.argsort(arr[0],kind='stable'); et,xt,pnl,reason,src=[z[o] for z in arr]
    # exact inherited coverage cap 512
    heap=[]; keep=[]
    for n in range(len(et)):
        now=int(et[n])
        while heap and heap[0][0]<=now: heapq.heappop(heap)
        if len(heap)>=512: continue
        keep.append(n); heapq.heappush(heap,(int(xt[n]),n))
    kk=np.asarray(keep,np.int64); et,xt,pnl=[z[kk] for z in (et,xt,pnl)]
    Ei=np.searchsorted(t,et).astype(np.int64); Xi=np.searchsorted(t,xt).astype(np.int64); Di=np.ones(len(Ei),np.int8); Ri=a[Ei].astype(np.int64); Hi=(xt-et)/1000.
    return Ei,Xi,Ri,Di,pnl.astype(float),Hi.astype(float)

def build_coldstart_targeted(ms=50,thr=450,cap=64):
    D0=DATA; t,a,b,mid,h4,h1,m15,m5=D0[:8]
    E=hb.heartbeat_events(D0[:8],ms,0); et,xt,pnl,reason,src=E
    idx=np.searchsorted(t,et); b10=((et//60000)%60)//10; j60=np.searchsorted(t,et-60000,side='left'); ticks60=idx-j60+1
    target=(et>=START)&(et<END)
    k=target&(src==12)&np.isin(b10,[4,5])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==-1)&(ticks60<=thr)
    et,xt,pnl=[z[k] for z in (et,xt,pnl)]; o=np.argsort(et,kind='stable'); et,xt,pnl=[z[o] for z in (et,xt,pnl)]
    Ei=np.searchsorted(t,et).astype(np.int64); Xi=np.searchsorted(t,xt).astype(np.int64); Di=np.ones(len(Ei),np.int8); Ri=a[Ei].astype(np.int64); Hi=(xt-et)/1000.
    return J.cap_arrays(Ei,Xi,Ri,Di,pnl.astype(float),Hi.astype(float),cap)[0]

J.build_coverage=build_coverage_targeted
J.build_coldstart=build_coldstart_targeted
P.J=J


def supplemental_parts():
    cov=build_coverage_targeted(); cold=build_coldstart_targeted(50,450,64)
    rules=[L.build_rule(k,l,st,cap) for k,l,n,st,cap in L.LEAN]
    return [cov,cold,*rules]

def score_131d():
    # exact 131D WD119 q-map/cap plus frozen supplemental session system
    wdq=J.build_watchdog()
    Q,meta=J.merge_preserve_watchdog(wdq,supplemental_parts(),512)
    meta.update(architecture='JAN_MILESTONE_131D',max_layer=None,watchdog_cap=703,cold_cap=64)
    s,_=J.score(t,*Q,'FEB_REPLAY_JAN_131D',meta)
    return s

def score_131e(cap):
    A,layer=P.build_raw(); E,X,R,D,Pn,H=A
    base=np.nonzero(layer<=35)[0]; kk=P.capsel(E[base],X[base],cap); idx=base[kk]; wdq=tuple(z[idx] for z in A)
    Q,meta=J.merge_preserve_watchdog(wdq,supplemental_parts(),512)
    meta.update(architecture='JAN_MILESTONE_131E',max_layer=35,watchdog_cap=cap,cold_cap=64,wd_net=float(np.sum(wdq[4])),wd_trades=int(len(wdq[4])))
    s,_=J.score(t,*Q,f'FEB_REPLAY_JAN_L35_C{cap}',meta)
    return s

def compact(s):
    keys=['name','net','trades','gross_profit','gross_loss','pf','win','expectancy','balance_dd','equity_dd','min_total_equity','maxopen','avg_hold_s','positive_days','beat_days','positive_weeks','beat_weeks','watchdog_cap','max_layer']
    return {k:s.get(k) for k in keys if k in s}

def main():
    rows=[]
    for fn in (score_131d,lambda:score_131e(640),lambda:score_131e(703)):
        s=fn(); rows.append(s); print(json.dumps(compact(s)),flush=True)
    bench=json.load(open(BENCH))
    obj={
      'candidate':'GAMMA_02_FEB_UNCHANGED_JAN_MILESTONE_REPLAY_132A',
      'status':'BASELINE_REPLAY_ONLY_NO_FEB_TUNING',
      'market_file':str(MARKET),'market_sha256':sha256_file(MARKET),
      'r9_synth_benchmark_file':str(BENCH),'r9_synth_source_sha256':bench['source_sha256'],
      'r9_synth_february':bench['month'],'r9_synth_daily':bench['daily'],'r9_synth_weekly':bench['weekly'],
      'execution_surface':'Dukascopy midpoint + frozen session-P75 normalized spread research surface; Python only; not Coinexx MT5 certification',
      'crossmonth_qa':'Exact January parameters/rules retained. Added only explicit START<=entry<END gating to supplemental heartbeat/coldstart sleeves so January warmup cannot leak trades into February.',
      'calendar_feature_forbidden':True,
      'rows':rows,
      'august':'SEALED','february_tuning':False
    }
    with open(OUT,'w') as f: json.dump(obj,f,indent=2)
    print('WROTE',OUT)
if __name__=='__main__': main()