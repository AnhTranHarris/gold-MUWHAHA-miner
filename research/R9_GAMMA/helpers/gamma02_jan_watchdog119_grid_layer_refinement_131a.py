"""GAMMA-02 January Watchdog-119 grid-layer refinement 131A.

Purpose
-------
Re-examine January from the frozen Watchdog-119 lineage without replacing its
causal admission logic.  The only candidate changes are:
  * child renewal quantum by already-known UTC/New-York 10-minute subphase; and
  * global child concurrency cap.

No month label is an execution feature.  This helper is January discovery only.
The frozen Watchdog proof remains: exact completed H4/H1/M15/M5 signature,
first-parent scout, four consecutive profitable q-renewals with <=60 s hold,
and immediate relock after any losing/slow realized child.

Important execution-surface caveat
----------------------------------
This lineage intentionally inherits stmr_base.materialize(), which reconstructs
an executable Ask/Bid surface around the Dukascopy midpoint using the frozen
session P75 spread model.  Results must therefore be described as the current
GAMMA-02 normalized-spread research surface, NOT raw-Dukascopy quote parity or
Coinexx MT5 certification.
"""
import hashlib, heapq, json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

import gamma02_dynamic_watchdog_router_119 as wd
import gamma02_m1_density as gmd
import gamma02_ny17_quantum_minute_window_075 as w
import gamma02_083_global_child_cap_087 as cap
import gamma02_funded_cap_equity_dd_028 as eq
from gamma02_083_heat_parent_ownership_084 import renewal_owned

DAY = 86_400_000
MARKET = Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
SYNTH = {
    'net': 41520.82,
    'trades': 27980,
    'pf': 23.715411927544082,
    'win': 0.8709077912794854,
    'expectancy': 1.4839463902787706,
    'avg_hold_s': 16.462687634024302,
    'gross_loss': -1827.87,
    'balance_dd': 3.40,
}

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def weekly_realized(t, X, P, H):
    buckets={}
    for k in range(len(P)):
        dt=datetime.fromtimestamp(int(t[int(X[k])])/1000,tz=timezone.utc)
        y,wk,_=dt.isocalendar(); key=f'{y}-W{wk:02d}'
        buckets.setdefault(key,[]).append(k)
    out={}
    for key,ix in sorted(buckets.items()):
        p=P[np.asarray(ix,np.int64)]; h=H[np.asarray(ix,np.int64)]
        gp=float(p[p>0].sum()); gl=float(p[p<=0].sum()); bal=0.;peak=0.;bdd=0.
        for v in p:
            bal+=float(v);peak=max(peak,bal);bdd=max(bdd,peak-bal)
        out[key]={
            'net':float(p.sum()),'gross_profit':gp,'gross_loss':gl,'trades':int(len(p)),
            'pf':float(gp/-gl if gl<0 else 999.),'win':float(np.mean(p>0)),
            'expectancy':float(np.mean(p)),'avg_hold_s':float(np.mean(h)),
            'closed_trade_balance_dd':float(bdd),
        }
    return out

def build(qmap, capn):
    # Bind every inherited helper to the same target-gated January prep as 119.
    def pp(): return wd.prep_month(1)
    gmd.prep=pp
    D,pei,pxi,pd,src,mins,disp=w.prep()
    t,a,b,mid,h4,h1,m15,m5=D[:8]; start,end=D[-2],D[-1]; pt=t[pei]
    lm=wd.local_minute(pt); lh=lm//60; lmin=lm%60
    target=(pt>=start)&(pt<end)
    macro=(h4[pei]!=0)&(h4[pei]==h1[pei])&(pd==h4[pei])
    # Frozen 119 local-NY window. January's parent stream here is NY17-derived.
    base=target&macro&(lh>=12)&(lh<=13)
    sigcode=((h4[pei]+1)*81+(h1[pei]+1)*27+(m15[pei]+1)*9+(m5[pei]+1)*3+(pd+1)).astype(np.int16)
    keys=np.stack((pt//DAY,lh,lmin//10,sigcode),axis=1)
    cand=np.nonzero(base)[0]
    cells=np.unique(keys[cand],axis=0) if len(cand) else np.empty((0,4),np.int64)
    parts=[]; bins=[]; cstats=[]
    for key in cells:
        day,hh,b10,sc=[int(x) for x in key]
        jj=np.nonzero(base&(keys[:,0]==day)&(keys[:,1]==hh)&(keys[:,2]==b10)&(keys[:,3]==sc))[0]
        if not len(jj): continue
        q=int(qmap[b10])
        A=renewal_owned(t,a,b,pei[jj],pxi[jj],pd[jj],q,0,0,2)
        E,X,R,Dd,P,H,O=A[:7]
        if not len(E):
            cstats.append((len(jj),0,0,0));continue
        by=[[] for _ in range(len(jj))]
        for ci,oo in enumerate(O): by[int(oo)].append(ci)
        order=np.argsort(t[pei[jj]],kind='stable')
        heap=[]; admitted=np.zeros(len(jj),np.bool_); streak=0; gate=False; unlocks=0; relocks=0
        first=int(order[0]); admitted[first]=True
        for ci in by[first]: heapq.heappush(heap,(int(t[X[ci]]),int(ci)))
        for po in order[1:]:
            po=int(po); now=int(t[pei[jj[po]]])
            while heap and heap[0][0]<=now:
                _,ci=heapq.heappop(heap)
                good=(P[ci]>0 and H[ci]<=60.)
                old=gate; streak=streak+1 if good else 0; gate=streak>=4
                if gate and not old: unlocks+=1
                if old and not gate: relocks+=1
            if gate:
                admitted[po]=True
                for ci in by[po]: heapq.heappush(heap,(int(t[X[ci]]),int(ci)))
        keep=np.nonzero(admitted[O])[0]
        if len(keep):
            parts.append((E[keep],X[keep],R[keep],Dd[keep],P[keep],H[keep],np.full(len(keep),2,np.int8)))
            bins.append(np.full(len(keep),b10,np.int8))
        cstats.append((len(jj),int(admitted.sum()),unlocks,relocks))
    if not parts: raise RuntimeError('no January Watchdog children')
    arr=[np.concatenate([p[k] for p in parts]) for k in range(7)]
    bb=np.concatenate(bins)
    order=np.lexsort((np.arange(len(arr[0])),arr[0]));Q=tuple(x[order] for x in arr);bb=bb[order]
    r,B=cap.one(Q,int(capn))
    # Recreate accepted indices so subphase labels stay aligned with cap.one.
    E,X,R,Dd,P,H,S=Q; heap=[]; keep=[]
    for k in range(len(E)):
        now=int(E[k])
        while heap and heap[0][0]<=now: heapq.heappop(heap)
        if len(heap)>=capn: continue
        keep.append(k); heapq.heappush(heap,(int(X[k]),k))
    kk=np.asarray(keep,np.int64); bb=bb[kk]
    E,X,R,Dd,P,H,S=B
    gp=float(P[P>0].sum()); gl=float(P[P<=0].sum())
    ex=eq.exact_equity_sweep(t,a,b,E,X,R,Dd,P); peak_total=100000.+ex[3]
    bybin={}
    for z in np.unique(bb):
        m=bb==z;p=P[m];g=float(p[p>0].sum());l=float(p[p<=0].sum())
        bybin[str(int(z))]={
            'quantum_raw':int(qmap[int(z)]),'net':float(p.sum()),'trades':int(len(p)),
            'gross_profit':g,'gross_loss':l,'pf':float(g/-l if l<0 else 999.),
            'win':float(np.mean(p>0)),'expectancy':float(np.mean(p)),'avg_hold_s':float(np.mean(H[m]))
        }
    r.update({
        'qmap_raw':[int(x) for x in qmap], 'gross_profit':gp,'gross_loss':gl,
        'balance_dd':float(ex[2]),'equity_dd':float(ex[4]),
        'equity_dd_pct_peak':float(ex[4]/peak_total*100),
        'peak_total_equity':float(peak_total),'minimum_total_equity':float(100000.+ex[5]),
        'min_equity_time_utc':eq.iso(t,ex[6]),'equity_dd_peak_time_utc':eq.iso(t,ex[7]),
        'equity_dd_trough_time_utc':eq.iso(t,ex[8]),'maxopen_exact':int(ex[9]),
        'admitted_parents':sum(x[1] for x in cstats),'total_parents':sum(x[0] for x in cstats),
        'unlocks':sum(x[2] for x in cstats),'relocks':sum(x[3] for x in cstats),
        'by_10m_subphase':bybin,'weekly_realized':weekly_realized(t,X,P,H),
    })
    return r

CASES = {
    'control': ('WD119_FROZEN_CONTROL', [1250]*6, 703),
    'q1190': ('WD119_Q1190_CONTROL_CAP703', [1190]*6, 703),
    'working': ('WD119_SUBPHASE_Q1190_Q1100_CAP703', [1190,1190,1190,1190,1190,1100], 703),
    'profit': ('WD119_SUBPHASE_Q1190_Q1100_CAP1152_PROFIT_FRONTIER', [1190,1190,1190,1190,1190,1100], 1152),
    'aggressive': ('WD119_SUBPHASE_Q1190_Q1100_CAP1408_AGGRESSIVE_FRONTIER', [1190,1190,1190,1190,1190,1100], 1408),
}

def envelope(rows):
    return {
        'candidate':'GAMMA_02_JAN_WATCHDOG119_GRID_LAYER_REFINEMENT_131A',
        'status':'JANUARY_DISCOVERY_COMPLETE_PYTHON_RESEARCH_ONLY',
        'market_file':str(MARKET),'market_sha256':sha256_file(MARKET),
        'parent_watchdog_helper_sha256':sha256_file(Path(__file__).with_name('gamma02_dynamic_watchdog_router_119.py')),
        'execution_surface':'Dukascopy midpoint + frozen session-P75 normalized spread from stmr_base.materialize; not raw-Dukascopy fill parity and not Coinexx MT5 certification',
        'r9_synth_january':SYNTH,
        'selection':{
            'working_base':'WD119_SUBPHASE_Q1190_Q1100_CAP703',
            'profit_frontier_over_200k':'WD119_SUBPHASE_Q1190_Q1100_CAP1152_PROFIT_FRONTIER',
            'aggressive_diagnostic_frontier':'WD119_SUBPHASE_Q1190_Q1100_CAP1408_AGGRESSIVE_FRONTIER',
            'reason':'cap703 improves the frozen 119 economics/realized-loss profile without increasing max-open or monthly full-tick equity DD; cap1152 proves >$200K remains available from the same Watchdog family but raises heat and is not the working base.'
        },
        'invalidated_or_rejected_in_same_reexamination':[
            'adding local-NY hour 11/source16: higher net but gross loss and balance DD deteriorated sharply',
            'naive hard-stop overlays: reduced equity DD but destroyed Watchdog economics/win rate/PF',
            'naive 30/60/90/120-second forced child timeouts: reduced equity DD but destroyed net/PF',
            'simple aggregate-floating-loss admission gates: did not solve the core heat problem cleanly',
            'same-tick multiplicity caps reduced heat but surrendered too much economic capture at tested bounds',
        ],
        'rows':rows,
        'next':'JAN_WATCHDOG119_EQUITY_HEAT_REFINEMENT_131B: attack synchronized floating heat without replacing Watchdog admission or sacrificing the cap703 working-base economics; then arbitrary-start/capital overlays before February.',
        'august':'SEALED','mql5':'NOT_AUTHORIZED'
    }

def run_case(case):
    name,qmap,capn=CASES[case]
    r=build(qmap,capn);r['name']=name;return r

def main(out, case='all'):
    if case!='all':
        obj=envelope([run_case(case)])
        with open(out,'w') as f: json.dump(obj,f,indent=2)
        return
    rows=[]
    partial=out+'.partial'
    for key in ('control','q1190','working','profit','aggressive'):
        r=run_case(key);rows.append(r)
        with open(partial,'w') as f: json.dump(envelope(rows),f,indent=2)
        print(json.dumps({k:r.get(k) for k in ['name','net','gross_loss','trades','pf','win','expectancy','avg_hold_s','balance_dd','equity_dd','minimum_total_equity','maxopen_exact','unique_ticks','cluster_fraction','max_cluster','skips']}),flush=True)
    with open(out,'w') as f: json.dump(envelope(rows),f,indent=2)

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--case',choices=['all',*CASES.keys()],default='all');z=ap.parse_args();main(z.out,z.case)
