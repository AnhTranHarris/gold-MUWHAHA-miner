"""Experimental causal admission with fixed paced UTC-hour limits.

Compare to unfiltered original Feb-frozen R00-068 on identical approved broker
source time/quote indices; never select hindsight top-scoring events per hour.
"""
import sys,json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit
ROOT=Path(__file__).resolve().parents[2];HERE=ROOT/'r00_074_pacer';OUT=HERE/'results';OUT.mkdir(exist_ok=True,parents=True)
B=('coinexx','dukascopy')

@njit(cache=True)
def emit_mask(t,prio,quota,threshold,lead=8):
    n=len(t);chosen=np.zeros(n,dtype=np.bool_)
    old_hour=-1;accepted=0
    for i in range(n):
        h=t[i]//3600000
        if h!=old_hour:
            old_hour=h;accepted=0
        second=(t[i]//1000)%3600
        floor_now=min(quota,lead+(second*quota)//3600)
        # Admission is strictly current-time / current-feature / emitted-so-far;
        # no lookahead to hour completion, or y labels.
        if accepted<quota and (prio[i]>=threshold or accepted<floor_now):
            chosen[i]=True;accepted+=1
    return chosen


def get(b,m):
    with np.load(ROOT/f'r00_073_arbiter/results/ALL_DIRECTIONS_{b}_{m}.npz') as z:
        d={k:z[k].copy() for k in z.files}
    with np.load(ROOT/f'r00_070_experiment/results/score_{m}_{b}_R00_068_FEB_protected_reference.npz') as z:
        assert np.array_equal(z['quote_index'],d['quote_index']) and np.array_equal(z['ts_ms'],d['ts_ms'])
        d['base_score']=z['score'].copy()
    with np.load(ROOT/f'r00_070_experiment/features/structural_{b}_{m}.npz') as z:
        assert np.array_equal(z['quote_index'],d['quote_index'])
        d['struct']=z['structure'].copy()
    return d


def policies(d):
    score=np.abs(d['base_score']);b=d['reference_side'];e=d['expert_emissions'];stage=d['expert_stage']
    agree=(np.sign(d['binary_score'])==b)&(np.sign(d['deep_score'])==b)
    goodtri=np.sign(d['ternary_score'])==b
    both=(agree&goodtri).astype(np.float32)
    life=(np.sum((stage==2)|(stage==3)|(stage==4),axis=1)>=1).astype(np.float32)
    exp=np.sum(e==b[:,None],axis=1).astype(np.float32)
    structural=d['struct'];top=np.nan_to_num(structural[:,7])+np.nan_to_num(structural[:,24]);aligned=(np.sign(top)==b).astype(np.float32)
    p=d['predicted_base_reliability'];co=np.abs(d['binary_score'])
    # Three orthogonal priority channels; all are known as of the event tick.
    priorities={
     'base_strength':score,
     'tri_agreement':score+.045*both,
     'episode_cooperation':score+.035*life+.025*np.minimum(exp,3),
     'completed_HTF':score+.035*aligned,
     'broker_meta_reliability':score+.20*(p-.6),
     'microstructure_consensus':.55*score+.10*co+.035*both+.025*life,
    }
    specs={'U_all_events':(0,0,'base_strength')}
    for Q in (130,150,180,240):
        for label,thr in [('lo',.05),('hi',.09)]:
            for strategy in ('base_strength','tri_agreement','episode_cooperation','completed_HTF','broker_meta_reliability','microstructure_consensus'):
                specs[f'Q{Q}_{label}_{strategy}']=(Q,thr,strategy)
    return priorities,specs


def score(b,m):
    d=get(b,m);t=d['ts_ms'];y=d['y'];side=d['reference_side'];pri,specs=policies(d);rows=[]
    full=(side==y)&(y!=0)
    for name,(q,thr,pname) in specs.items():
        use=np.ones(len(t),bool) if q==0 else emit_mask(t,pri[pname],q,thr)
        correct=full&use
        rows.append(dict(broker=b,month=m,policy=name,events=int(use.sum()),correct=int(correct.sum()),accuracy=float(correct.sum()/max(int(use.sum()),1)),BUY=int((use&(side==1)).sum()),SELL=int((use&(side==-1)).sum()),nonempty_hours=int(len(np.unique(t[use]//3600000))),original_candidate_events=len(t)))
        # Keep event membership for every tested policy, enables independent verification.
        np.packbits(use).tofile(OUT/f'selected_{b}_{m}_{name}.packbits')
    pd.DataFrame(rows).to_csv(OUT/f'ALL_074_POLICIES_{b}_{m}.csv',index=False)
    print('074',b,m,'top by accuracy',sorted([(z['policy'],z['accuracy'],z['events']) for z in rows],key=lambda x:-x[1])[:4],flush=True)


def freeze():
    f=pd.concat([pd.read_csv(OUT/f'ALL_074_POLICIES_{b}_02.csv') for b in B])
    gr=f.groupby('policy').agg(events=('events','sum'),correct=('correct','sum'),nonempty_hours=('nonempty_hours','sum'),original_candidate_events=('original_candidate_events','sum'))
    gr['accuracy']=gr.correct/gr.events;gr['eligible']=(gr.events>=.20*gr.original_candidate_events)&(gr.nonempty_hours>=.95*gr.loc['U_all_events','nonempty_hours'])
    gr.sort_values('accuracy',ascending=False).to_csv(OUT/'FEB_074_ALL_SCORES.csv')
    ok=gr[gr.eligible];w=str(ok.sort_values(['accuracy','correct'],ascending=[False,False]).index[0]) if not ok.empty else 'U_all_events'
    r={'policy':w,'fit':'Jan-073','select':'Feb-2026','events':int(gr.loc[w,'events']),'correct':int(gr.loc[w,'correct']),'accuracy':float(gr.loc[w,'accuracy']),'nonempty_hours':int(gr.loc[w,'nonempty_hours']),'transfer_never_selected':True}
    (OUT/'FROZEN_FEB_POLICY.json').write_text(json.dumps(r,indent=2));print('074 FEB frozen',r,flush=True)


def transfer():
    sel=json.loads((OUT/'FROZEN_FEB_POLICY.json').read_text())['policy']
    f=pd.concat([pd.read_csv(OUT/f'ALL_074_POLICIES_{b}_{m}.csv') for b in B for m in ('06','07')]);gr=f.groupby('policy').agg(events=('events','sum'),correct=('correct','sum'),BUY=('BUY','sum'),SELL=('SELL','sum'));gr['accuracy']=gr.correct/gr.events;gr.to_csv(OUT/'TRANSFER_074_ALL_POLICIES.csv')
    print('074 EXPOSED TRANSFER selected',sel,gr.loc[sel].to_dict(),'control',gr.loc['U_all_events'].to_dict(),flush=True)
    # exact R9 SYNTH hourly/day denominator from the source-aligned original R00-070 ledger.
    orig=pd.read_csv(ROOT/'r00_070_experiment/results/R00_070_071_FULL_R9_HOUR_DAY_DENOMINATORS.csv.gz')
    orig=orig[(orig.policy=='R00_068_PROTECTED')&(orig.interval.isin(['hour','day']))]
    assert len(orig)>1000
    rows=[]
    for b in B:
     for m in ('06','07'):
      d=get(b,m);t=d['ts_ms'];y=d['y'];side=d['reference_side'];pri,specs=policies(d);full=(side==y)&(y!=0)
      for name in ('U_all_events',sel):
       q,thr,pname=specs[name]
       use=np.ones(len(t),bool) if q==0 else emit_mask(t,pri[pname],q,thr)
       for typ,div in (('hour',3600000),('day',86400000)):
        keys=t//div;hit=np.unique(keys)
        cnt=pd.DataFrame({'UTC_reference_key':keys[use],'correct':full[use].astype('int8')}).groupby('UTC_reference_key').agg(emitted=('correct','size'),correct=('correct','sum')) if use.any() else pd.DataFrame(columns=['emitted','correct'])
        ref=orig[(orig.broker==b)&(orig.month==int(m))&(orig.interval==typ)]
        assert len(ref)>0,(b,m,typ)
        for row in ref.itertuples():
         key=int(row.UTC_reference_key)
         val=cnt.loc[key] if key in cnt.index else None
         emit=int(val.emitted) if val is not None else 0
         good=int(val.correct) if val is not None else 0
         rows.append(dict(broker=b,month=m,interval=typ,key=key,policy=name,R9_SYNTH_trades=int(row.R9_SYNTH_trades),floor90=int(row.floor90),emitted=emit,correct=good,volume_pass=(emit>=int(row.floor90)),correct_count_pass=(good>=int(row.floor90))))
    table=pd.DataFrame(rows);table.to_csv(OUT/'TRANSFER_074_R9_HOUR_DAY_ALL_ROWS.csv',index=False)
    summ=table.groupby(['policy','interval']).agg(rows=('key','size'),volume_pass=('volume_pass','sum'),correct_count_pass=('correct_count_pass','sum'),R9_SYNTH_trades=('R9_SYNTH_trades','sum'),emitted=('emitted','sum'),correct=('correct','sum')).reset_index();summ.to_csv(OUT/'TRANSFER_074_R9_COVERAGE_SUMMARY.csv',index=False)
    print('074 HOURLY DAY',summ.to_string(index=False),flush=True)

if __name__=='__main__':
 action=sys.argv[1]
 if action=='score':score(sys.argv[2],sys.argv[3])
 if action=='freeze':freeze()
 if action=='transfer':transfer()
