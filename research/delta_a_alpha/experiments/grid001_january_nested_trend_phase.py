from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np

from grid001_january_event_label_lab import load, materialize, PRICE_SCALE
from grid001_january_early_thesis_failure import m1_atr_gap, gen_events
from grid001_january_nested_trend_state import proof_trades
from grid001_january_parent_opposed_reclaim_route import parent_reclaim

MULTS=((0.5,'A05'),(1.0,'A10'),(1.5,'A15'))

def state_age_series(t,mid,tf_ms):
    bucket=t//tf_ms
    starts=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]
    ends=np.r_[starts[1:]-1,len(t)-1]
    bars=bucket[starts]
    closes=mid[ends].astype(float)
    ser=np.full(len(closes),np.nan)
    if len(closes)>=7:
        d=np.abs(np.diff(closes)); cs=np.r_[0.0,np.cumsum(d)]
        j=np.arange(6,len(closes)); net=closes[j]-closes[j-6]; path=cs[j]-cs[j-6]
        ser[j]=np.divide(net,path,out=np.zeros_like(net),where=path>0)
    state=np.zeros(len(closes),np.int8)
    state[ser>=.5]=1; state[ser<=-.5]=-1
    age=np.zeros(len(closes),np.int32)
    for i in range(len(closes)):
        if state[i]==0: age[i]=0
        elif i>0 and state[i]==state[i-1]: age[i]=age[i-1]+1
        else: age[i]=1
    return bars,state,age

def map_state(t,qidx,bars,state,age,tf_ms):
    qb=t[qidx]//tf_ms
    bi=np.searchsorted(bars,qb,side='left')-1
    s=np.zeros(len(qidx),np.int8); ag=np.zeros(len(qidx),np.int32)
    ok=bi>=0
    s[ok]=state[bi[ok]]; ag[ok]=age[bi[ok]]
    return s,ag

def stats(x):
    x=np.asarray(x,float); gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {'n':int(len(x)),'net':float(x.sum()),'gross_profit':gp,'gross_loss':gl,
            'pf':gp/abs(gl) if gl<0 else None,
            'expected':float(x.mean()) if len(x) else None,
            'win_pct':100*float((x>0).mean()) if len(x) else None}

def phase(age):
    out=np.zeros(len(age),np.int8)
    out[(age>=1)&(age<=2)]=1
    out[(age>=3)&(age<=6)]=2
    out[age>=7]=3
    return out

def group_stats(pnl,mask,owner_tf,relation,ph,disc):
    out={}
    for tfcode,tfname in [(5,'5m'),(15,'15m')]:
        for relcode,relname in [(1,'ALIGNED'),(-1,'OPPOSED')]:
            for phcode,phname in [(1,'EARLY'),(2,'MATURE'),(3,'EXTENDED')]:
                m=mask&(owner_tf==tfcode)&(relation==relcode)&(ph==phcode)
                out[f'{tfname}_{relname}_{phname}']={
                    'full':stats(pnl[m]),
                    'discovery':stats(pnl[m&disc]),
                    'validation':stats(pnl[m&~disc])
                }
    out['PARENT_NEUTRAL']={
        'full':stats(pnl[mask&(relation==0)]),
        'discovery':stats(pnl[mask&(relation==0)&disc]),
        'validation':stats(pnl[mask&(relation==0)&~disc])
    }
    out['PARENT_CONFLICT']={
        'full':stats(pnl[mask&(relation==2)]),
        'discovery':stats(pnl[mask&(relation==2)&disc]),
        'validation':stats(pnl[mask&(relation==2)&~disc])
    }
    return out

def variant(t,a,b,mid,mult,b5,s5,a5,b15,s15,a15):
    gaps=m1_atr_gap(t,b,mult)
    ei,ed,eg=gen_events(t,a,b,gaps)
    pi,pbe=proof_trades(t,a,b,ei,ed,eg)
    opened=pi>=0
    idx=np.where(opened,pi,ei)
    st5,ag5=map_state(t,idx,b5,s5,a5,300000)
    st15,ag15=map_state(t,idx,b15,s15,a15,900000)
    side=np.where(ed<0,-1,1).astype(np.int8)

    owner_tf=np.zeros(len(ei),np.int8)
    owner_dir=np.zeros(len(ei),np.int8)
    owner_age=np.zeros(len(ei),np.int32)
    relation=np.zeros(len(ei),np.int8)

    same=(st15!=0)&(st5==st15)
    own15=(st15!=0)&((st5==0)|same)
    own5=(st5!=0)&(st15==0)
    conflict=(st5!=0)&(st15!=0)&(st5!=st15)

    owner_tf[own15]=15; owner_dir[own15]=st15[own15]; owner_age[own15]=ag15[own15]
    owner_tf[own5]=5; owner_dir[own5]=st5[own5]; owner_age[own5]=ag5[own5]

    relation[(owner_dir!=0)&(owner_dir==side)]=1
    relation[(owner_dir!=0)&(owner_dir==-side)]=-1
    relation[conflict]=2
    ph=phase(owner_age)
    disc=ei<2*len(t)//3

    proof_groups=group_stats(pbe,opened,owner_tf,relation,ph,disc)
    parent_opp=opened&(relation==-1)
    rpnl,rentered,_=parent_reclaim(t,a,b,ei,ed,eg,pi,parent_opp)
    rm=rentered==1
    reclaim_groups=group_stats(rpnl,rm,owner_tf,relation,ph,disc)

    return {
      'opened':int(opened.sum()),
      'parent_reclaim_trades':int(rm.sum()),
      'population':{
        'owner_15m':int(np.sum(opened&(owner_tf==15))),
        'owner_5m':int(np.sum(opened&(owner_tf==5))),
        'neutral':int(np.sum(opened&(relation==0))),
        'conflict':int(np.sum(opened&(relation==2)))
      },
      'proof_groups':proof_groups,
      'parent_reclaim_groups':reclaim_groups
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('source',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    z=ap.parse_args()

    t,sa,sb=load(z.source)
    a,b,maxe=materialize(t,sa,sb)
    mid=(a.astype(np.int64)+b.astype(np.int64))/2.0
    b5,s5,a5=state_age_series(t,mid,300000)
    b15,s15,a15=state_age_series(t,mid,900000)

    out={
      'schema':'delta-a-alpha-grid001-january-nested-trend-phase-v1',
      'unit':'DAA_GRID_001_JANUARY_NESTED_TREND_PHASE_001',
      'status':'COMPLETE',
      'surface':'DUKAS_COINEXX_LIKE_P75',
      'ticks':int(len(t)),
      'phase_bins':{'EARLY':'1-2','MATURE':'3-6','EXTENDED':'>=7'},
      'variants':{
        name:variant(t,a,b,mid,m,b5,s5,a5,b15,s15,a15)
        for m,name in MULTS
      },
      'max_midpoint_quantization_error_price':float(maxe/(2*PRICE_SCALE))
    }
    z.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':
    main()
