"""R117 original-signal t0 lifecycle specialists; no broker operations."""
from pathlib import Path
import argparse, gc, importlib.util, json, os, sys, time
import numpy as np
import pandas as pd
import lightgbm as lgb
from numba import njit

R=Path(__file__).resolve().parent; W=R.parent
spec=importlib.util.spec_from_file_location('r116_source_helpers',W/'research_r116/run.py')
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
original,splits,sha,write_json,ARC_SHA,ARCHIVE=(getattr(previous,n) for n in ('original','splits','sha','write_json','ARC_SHA','ARCHIVE'))
sys.path.insert(0,str(W/'repo/research/htf_dual_ticklab'))
from htf_ticklab.source_registry import verify
MONTHS=('01','02','06','07'); WIDTHS=(60000,300000,900000,3600000,28800000)

@njit(cache=True)
def transduce(tm,bid,ask,et,width):
    # 2 directions x14: valid, state, crosses, failures, seconds since transition,
    # outside fraction, max penetration/range, displacement/range, completed body,
    # log range, compression, current/previous quote-rate, seconds since publication,
    # signed last displacement from published close/range.
    out=np.zeros((len(et),2,14),np.float32)
    if len(tm)==0:return out
    bk=tm[0]//width; op=(bid[0]+ask[0])/2; hi=op;lo=op;cl=op;count=0
    valid=False; ph=0.;pl=0.;po=0.;pc=0.;pr=.05;pn=0
    state=np.zeros(2,np.int64);cross=np.zeros(2,np.int64);fail=np.zeros(2,np.int64)
    change=np.zeros(2,np.int64);outside=np.zeros(2,np.int64);peak=np.zeros(2)
    seen=0;pub=0;lastmid=0.;lasttm=0;e=0
    for i in range(len(tm)+1):
        now=tm[i] if i<len(tm) else np.iinfo(np.int64).max
        while e<len(et) and et[e]<=now:
            # A new bucket with no consumed quote has no published previous-bar
            # state yet. Abstain instead of retaining stale state across a gap.
            usable=valid and et[e]//width==bk
            if usable:
                for d in range(2):
                    sign=1. if d==0 else -1.;level=ph if d==0 else pl
                    out[e,d,0]=1.;out[e,d,1]=state[d];out[e,d,2]=cross[d];out[e,d,3]=fail[d]
                    out[e,d,4]=(et[e]-change[d])/1000
                    out[e,d,5]=outside[d]/max(1,seen)
                    out[e,d,6]=peak[d]/pr;out[e,d,7]=sign*(lastmid-level)/pr
                    out[e,d,8]=sign*(pc-po)/pr;out[e,d,9]=np.log1p(pr)
                    out[e,d,10]=abs(pc-po)/pr<.5
                    out[e,d,11]=(seen/max(1.,(lasttm-pub)/1000))/(pn/(width/1000)+.01)
                    out[e,d,12]=(et[e]-pub)/1000;out[e,d,13]=sign*(lastmid-pc)/pr
            e+=1
        if i==len(tm):break
        key=tm[i]//width;mid=(bid[i]+ask[i])/2
        if key!=bk:
            valid=key==bk+1 and count>0
            ph=hi;pl=lo;po=op;pc=cl;pr=max(.05,ph-pl);pn=count
            bk=key;op=mid;hi=mid;lo=mid;count=0;seen=0;pub=key*width
            for d in range(2):
                state[d]=0;cross[d]=0;fail[d]=0;change[d]=tm[i];outside[d]=0;peak[d]=0
        if valid:
            seen+=1;eps=max(.01,(ask[i]-bid[i])*.5)
            for d in range(2):
                sign=1. if d==0 else -1.;level=ph if d==0 else pl
                enter=bid[i]>level if d==0 else ask[i]<level
                leave=ask[i]<level-eps if d==0 else bid[i]>level+eps
                if enter and (state[d]==0 or state[d]==2):
                    cross[d]+=1;state[d]=1 if fail[d]==0 else 3;change[d]=tm[i]
                elif leave and (state[d]==1 or state[d]==3):
                    fail[d]+=1;state[d]=2;change[d]=tm[i]
                if enter:outside[d]+=1
                peak[d]=max(peak[d],sign*(mid-level))
        hi=max(hi,mid);lo=min(lo,mid);cl=mid;count+=1;lastmid=mid;lasttm=tm[i]
    return out

def lifecycle(tm,bid,ask,t,side):
    allx=np.stack([transduce(tm,bid,ask,t,w) for w in WIDTHS],axis=1)
    # Place original-side state first and opposite-side state second.
    ix=np.arange(len(t)); own=(side<0).astype(int)
    x=np.stack([allx[ix,:,own,:],allx[ix,:,1-own,:]],axis=2)
    return x.reshape(len(t),-1)

def gates(x):
    z=x.reshape(len(x),5,2,14);own=z[:,:,0,:];opp=z[:,:,1,:]
    return np.column_stack(((own[:,:,1]==2).any(axis=1),
        np.isin(opp[:,:,1],[1,3]).any(axis=1),
        (np.isin(own[:,:,1],[1,3])&(own[:,:,8]>=.5)).any(axis=1)))

def prepare(month):
    if (R/'cache'/f'{month}.json').exists():raise RuntimeError('existing preparation')
    assert sha(ARCHIVE)==ARC_SHA
    p=W/f'sources/XAUUSD_DUKAS_2026_{month}_ticks.csv.gz';digest=sha(p);verify(p.name,'dukascopy',digest)
    a=original(month)
    df=pd.read_csv(p,usecols=['timestamp_ms_utc','bid_raw','ask_raw'])
    tm=df.timestamp_ms_utc.to_numpy(np.int64);bid=df.bid_raw.to_numpy(float)/1000;ask=df.ask_raw.to_numpy(float)/1000
    assert np.all(np.diff(tm)>=0) and np.all(ask>=bid)
    x=lifecycle(tm,bid,ask,a['t'],a['original_side']);g=gates(x)
    np.save(R/'cache'/f'state_{month}.npy',x)
    np.savez_compressed(R/'cache'/f'events_{month}.npz',**a,gates=g)
    write_json(R/'cache'/f'{month}.json',dict(events=len(x),quotes=len(tm),source_sha256=digest,
        state_sha256=sha(R/'cache'/f'state_{month}.npy'),code_sha256=sha(__file__),plan_sha256=sha(R/'PLAN.md'),
        gates=g.sum(axis=0).tolist(),unique_eligible=int(g.any(axis=1).sum())))
    print('prepared',month,x.shape,g.sum(axis=0),flush=True)

def features(month):
    # Read only native/completed geometry columns from existing pinned cache.
    m=json.loads((W/'research_r116/cache'/f'{month}.json').read_text())
    p=W/'research_r116/cache'/f'x_{month}.npy';assert sha(p)==m['files'][f'cache/x_{month}.npy']
    x=np.load(p,mmap_mode='r')[:,:167]
    return np.column_stack((x,np.load(R/'cache'/f'state_{month}.npy')))

def fit():
    a=np.load(R/'cache/events_01.npz');x=features('01');base=splits(a['t'])['FIT'];y=a['truth_class']
    target=np.where(y==0,0,np.where(a['kept']==0,2,1));g=a['gates']
    for head in range(3):
        path=R/'models'/f'expert_{head}.txt';meta=path.with_suffix('.json')
        mask=base&g[:,head]
        ds=lgb.Dataset(x[mask],label=target[mask],free_raw_data=False)
        model=lgb.Booster(model_file=str(path)) if path.exists() else None
        rounds=model.current_iteration() if model else 0
        params=dict(objective='multiclass',num_class=3,learning_rate=.06,num_leaves=127,
            min_data_in_leaf=64,max_bin=127,lambda_l2=5,feature_fraction=.9,num_threads=4,
            verbosity=-1,seed=1172026+head,deterministic=True,force_col_wise=True)
        while rounds<128:
            model=lgb.train(params,ds,num_boost_round=min(16,128-rounds),init_model=model,keep_training_booster=True)
            rounds=model.current_iteration();tmp=path.with_suffix('.tmp');model.save_model(str(tmp));os.replace(tmp,path)
            write_json(meta,dict(rounds=rounds,eligible_fit_rows=int(mask.sum()),target_counts=np.bincount(target[mask],minlength=3).tolist(),
                sha256=sha(path),plan_sha256=sha(R/'PLAN.md'),run_sha256=sha(__file__)))
            print('fit',head,rounds,int(mask.sum()),flush=True)
        del ds,model;gc.collect()

def predict(month):
    out=R/'results'/f'prob_{month}.npy'
    if out.exists():raise RuntimeError('existing predictions')
    x=features(month);p=np.zeros((len(x),3,3),np.float32)
    for h in range(3):
        model=lgb.Booster(model_file=str(R/'models'/f'expert_{h}.txt'))
        for s in range(0,len(x),25000):p[s:s+25000,h]=model.predict(x[s:s+25000],num_threads=4)
    np.save(out,p);print('predicted',month,flush=True)

def risk(p,g):return np.max(np.where(g,p[:,:,2]/(p[:,:,0]+1e-6),0),axis=1)

def calibrate():
    out=R/'results/FROZEN.json'
    if out.exists():raise RuntimeError('already frozen')
    a=np.load(R/'cache/events_01.npz');p=np.load(R/'results/prob_01.npy');r=risk(p,a['gates'])
    cal=splits(a['t'])['CAL'];good=a['truth_class']==0;ses=(a['t']//21600000)%4
    cells=[('all',cal,.01)]
    for s in (-1,1):
        for h in range(4):
            m=cal&(a['original_side']==s)&(ses==h)
            if (m&good).sum()>=100:cells.append((f'{s}_{h}',m,.02))
    cuts=[]
    for name,m,budget in cells:
        v=np.sort(r[m&good])[::-1];allowed=int(np.floor(budget*len(v)))
        # Strict > at value of first prohibited good; equal-score events all retained.
        cuts.append(dict(cell=name,correct=len(v),allowed=allowed,cut=float(v[allowed])))
    cut=max(0.,max(c['cut'] for c in cuts))
    write_json(out,dict(cut=cut,rule='strict_greater',cells=cuts,plan_sha256=sha(R/'PLAN.md')))
    print('frozen',cut,flush=True)

def counts(a,v,m):
    y=a['truth_class'];teacher=a['kept']==0;v=v&m
    return dict(n=int(m.sum()),correct=int(((y==0)&m).sum()),incorrect=int(((y!=0)&m).sum()),
        incorrect_veto=int((v&(y!=0)).sum()),correct_lost=int((v&(y==0)).sum()),
        opposite_veto=int((v&(y==1)).sum()),neutral_veto=int((v&(y==2)).sum()),
        teacher_wrong_overlap=int((v&teacher&(y!=0)).sum()),wrong_not_vetoed_by_teacher=int((v&~teacher&(y!=0)).sum()),
        unique_30s_time_buckets=int(np.unique((a['t'][v]//30000)*2+(a['original_side'][v]>0)).size))

def score(month):
    a=np.load(R/'cache'/f'events_{month}.npz');src=original(month)
    for k in src:assert np.array_equal(a[k],src[k])
    p=np.load(R/'results'/f'prob_{month}.npy');r=risk(p,a['gates'])
    f=json.loads((R/'results/FROZEN.json').read_text());v=r>f['cut']
    masks=splits(a['t']) if month=='01' else {};masks['FULL_MIXED' if month=='01' else 'FULL_EXPOSED']=np.ones(len(v),bool)
    report=dict(month=month,counts={k:counts(a,v,m) for k,m in masks.items()},raw_gates={},cells=[])
    for h in range(3):report['raw_gates'][str(h)]={k:counts(a,a['gates'][:,h],m) for k,m in masks.items()}
    report['raw_union']={k:counts(a,a['gates'].any(axis=1),m) for k,m in masks.items()}
    for s in (-1,1):
        for h in range(4):
            m=(a['original_side']==s)&((a['t']//21600000)%4==h)
            report['cells'].append(dict(side=s,session=h,**counts(a,v,m)))
    np.savez_compressed(R/'results'/f'mask_{month}.npz',**src,veto=v,risk=r,gates=a['gates'])
    write_json(R/'results'/f'score_{month}.json',report)
    print('score',month,report['counts'],flush=True)

if __name__=='__main__':
    q=argparse.ArgumentParser();q.add_argument('stage',choices=['prepare','fit','predict','calibrate','score']);q.add_argument('--month',choices=MONTHS);a=q.parse_args()
    if a.stage in ('fit','calibrate'):globals()[a.stage]()
    else:globals()[a.stage](a.month)
