#!/usr/bin/env python3
"""FILTER13: new causal matured-regime memory and teacher-free cooperative failure detector.
Versioned successor to R00-054 FILTER12, not a replay engine. No same-month teacher input.
"""
from __future__ import annotations
import os,json,time,csv,gzip,hashlib,argparse
from pathlib import Path
os.environ['OMP_NUM_THREADS']='2'
import numpy as np,pandas as pd,joblib,lightgbm as lgb
from numba import njit
import R00_054_FILTER12_TRANSFER_STUDENT as m
R=Path('/mnt/data'); OUT=R/'R00_054_FILTER13_CAUSAL_REGIME_MEMORY';OUT.mkdir(exist_ok=True)
PLAN=json.loads((R/'R00_054_FILTER13_PREDECLARED_DESIGN_20261019.json').read_text())
p=OUT/'EXACT_FROZEN_PLAN.json'
if p.exists():assert json.loads(p.read_text())==PLAN
else:p.write_text(json.dumps(PLAN,indent=2)+'\n')

@njit(cache=True)
def regime_matured(t,y,ctx,subctx):
    """Each update is eligible only at t[j]+33 sec; three rolling horizons, per-class per-context.
    At any i, the current label y[i] has NOT been observed; its value is referenced later only.
    Source gap >3h causes prior windows to empty automatically; no cross-file stitching.
    """
    n=t.shape[0];res=np.zeros((n,19),np.float32)
    windows=np.array([120000,900000,3600000],np.int64)
    # 3 windows x global or contextual class hist with 3 categories [correct, opposite, neutral]
    G=np.zeros((3,3),np.int32);C=np.zeros((3,72,3),np.int32);S=np.zeros((3,12,3),np.int32)
    head=np.zeros(3,np.int64);mature=0
    for i in range(n):
        # Add newly matured historical labels, never current/future event outcomes.
        while mature<i and t[mature]+33000<=t[i]:
            cls=int(y[mature]);cid=int(ctx[mature]);sid=int(subctx[mature])
            for w in range(3):
                G[w,cls]+=1;C[w,cid,cls]+=1;S[w,sid,cls]+=1
            mature+=1
        for w in range(3):
            while head[w]<mature and t[head[w]]+33000<t[i]-windows[w]:
                j=head[w];G[w,int(y[j])]-=1;C[w,int(ctx[j]),int(y[j])]-=1;S[w,int(subctx[j]),int(y[j])]-=1
                head[w]+=1
            a=G[w,0];b=G[w,1];c=G[w,2];total=a+b+c
            off=w*3
            res[i,off]=(a+8)/(total+16)
            res[i,off+1]=(b+4)/(total+12)
            res[i,off+2]=(c+4)/(total+12)
        cid=int(ctx[i]);sid=int(subctx[i]);a=C[2,cid,0];b=C[2,cid,1];c=C[2,cid,2];total=a+b+c
        res[i,9]=(a+6)/(total+12);res[i,10]=(b+3)/(total+9);res[i,11]=(c+3)/(total+9)
        res[i,12]=np.log1p(total)
        a=S[1,sid,0];b=S[1,sid,1];c=S[1,sid,2];total=a+b+c
        res[i,13]=(a+5)/(total+10);res[i,14]=(b+3)/(total+9);res[i,15]=(c+3)/(total+9)
        res[i,16]=np.log1p(total)
        res[i,17]=res[i,0]-res[i,6]  # rapid relative to 60m historical accuracy change
        res[i,18]=res[i,2]-res[i,8]  # rapid relative to 60m neutral opportunity hazard
    return res

def get_bins(b):
    p=OUT/f'JAN_ONLY_CONTEXT_BINS_{b}.json'
    if p.exists():return json.loads(p.read_text())
    t,s,y,X,names,flags=m.getdata(b,'01')
    def qq(name):
        col=np.nan_to_num(X[:,names.index(name)].astype('float64'),nan=0,posinf=0,neginf=0)
        return [float(x) for x in np.quantile(col,[.33,.67])]
    v={'completed_volatility':qq('orig_20'),'side_relative_htf':qq('side_orig_6'),'quote_turns':qq('quote_turn_fraction_64'),'origin':'JAN predictors only, no JAN future label'}
    p.write_text(json.dumps(v,indent=2)+'\n')
    print('F13_JAN_CONTEXT_BINS',b,flush=True)
    return v

def make_full(b,month,bins):
    t,side,y,X,names,flags=m.getdata(b,month)
    hour=((t//3600000)%24).astype('int32')
    sess=np.where(hour<8,0,np.where(hour<12,1,np.where(hour<17,2,3))).astype('int32')
    trend=np.searchsorted(bins['side_relative_htf'],X[:,names.index('side_orig_6')],side='right').astype('int32')
    vol=np.searchsorted(bins['completed_volatility'],X[:,names.index('orig_20')],side='right').astype('int32')
    churn=np.searchsorted(bins['quote_turns'],X[:,names.index('quote_turn_fraction_64')],side='right').astype('int32')
    context=(sess*18+trend*6+vol*2+(churn==2)).astype('int32')
    subctx=(sess*3+trend).astype('int32')
    assert context.min()>=0 and context.max()<72 and subctx.max()<12
    hist=regime_matured(t,y,context,subctx)
    # fixed classes independent of model source target (except delayed former events)
    nr=['regime_mature_correct_2m','regime_mature_opp_2m','regime_mature_neut_2m',
    'regime_mature_correct_15m','regime_mature_opp_15m','regime_mature_neut_15m',
    'regime_mature_correct_60m','regime_mature_opp_60m','regime_mature_neut_60m',
    'same_context_correct_60m','same_context_opp_60m','same_context_neut_60m','same_context_log_count_60m',
    'same_session_trend_correct_15m','same_session_trend_opp_15m','same_session_trend_neut_15m',
    'same_session_trend_log_count','adaptive_correct_drift_2m_vs_60m','adaptive_neutral_drift_2m_vs_60m']
    XX=np.column_stack((X,hist)).astype('float32');names+=nr
    return t,side,y,XX,names,flags,context

# New error-specific student at Feb first 60%. All 19 new features genuinely available after prior label maturation.
def train_models(b,X,names,t,y):
    pivot=t[int(.60*len(t))];tr=np.flatnonzero(t<pivot-60000)[::2];va=np.flatnonzero(t>pivot+60000)
    assert t[tr[-1]]+60000<t[va[0]]
    core=[i for i,n in enumerate(names) if n.startswith('regime_mature_') or n.startswith('same_context_') or n.startswith('same_session_') or n.startswith('adaptive_')]
    past=[names.index(n) for n in ['orig_20','orig_21','orig_22','orig_23','orig_26','orig_27','orig_28','side_orig_6','side_orig_7','side_orig_8','quote_turn_fraction_64','spread_range_64','median_tick_gap_ms_64','last_bid_age_ms','last_ask_age_ms','matured_2','matured_4','N_state','O_state','S_state','R_state','M_state','session_overlap','session_rollover']]
    out={}
    for kind in ('correct','neutral','opposite'):
        sel=tr if kind!='opposite' else tr[y[tr]!=2]
        outcome=(y[sel]==(0 if kind=='correct' else 2 if kind=='neutral' else 1)).astype('int8')
        cols=np.array(core+past, dtype=int)
        fn=OUT/f'F13_EARLY_FEB_{b}_{kind}.joblib'
        if fn.exists():mdl=joblib.load(fn)['model']
        else:
            mdl=lgb.LGBMClassifier(objective='binary',n_estimators=130,num_leaves=15,max_bin=63,learning_rate=.043,
                min_child_samples=160,colsample_bytree=.86,reg_lambda=9.,random_state=13054+len(kind),n_jobs=2,verbosity=-1)
            mdl.fit(X[np.ix_(sel,cols)],outcome)
            joblib.dump({'model':mdl,'columns':cols,'features':[names[i] for i in cols],'role':kind},fn,compress=3)
        out[kind]=(mdl,cols)
    return out,tr,va

def probs(XX,models):
    p={k:v.predict_proba(XX[:,col])[:,1].astype('float32') for k,(v,col) in models.items()}
    p['survive']=(1-p['neutral'])*(1-p['opposite'])
    p['agree']=(p['correct']+p['survive'])*.5
    p['high']=np.maximum(p['correct'],p['survive'])
    p['low']=np.minimum(p['correct'],p['survive'])
    p['error_balanced']=1-(.55*p['neutral']+.45*p['opposite'])
    p['neutral_guard']=(1-p['neutral'])*(.75+.25*p['correct'])
    p['opposite_guard']=(1-p['opposite'])*(.75+.25*p['correct'])
    p['regime_agreement']=(p['survive']+p['correct']+p['error_balanced'])/3
    p['twohazard_voter']=np.maximum((1-p['neutral']),1-p['opposite'])*p['correct']
    return p

def masks(XX,ff,context):
    # Gate veto via independent observable states, no outcome labels.
    return {'none':np.ones(len(context),bool),'NO':ff[:,0].astype(bool)|ff[:,1].astype(bool),
      'SR':ff[:,2].astype(bool)|ff[:,3].astype(bool),'M':ff[:,4].astype(bool),
      'any2':ff.sum(axis=1)>=2,'regime_context':XX[:,-7]>=2.0,
      'quote_churn':XX[:,56]>.5,'anti_stale':XX[:,53]<5000,
      'rollover_only':XX[:,86]>.5,'session_overlap':XX[:,85]>.5}

def scan(b,t,y,XX,flags,context,preds,idx=None):
    if idx is not None:
        t=t[idx];y=y[idx];XX=XX[idx];flags=flags[idx];context=context[idx];preds={k:v[idx] for k,v in preds.items()}
    guards=masks(XX,flags,context);rs=[]
    for name,prob in preds.items():
        for cut in PLAN['search_grid']['cutoffs']:
            to_veto=prob<cut
            for guard,g in guards.items():
                keep=~(to_veto&g)
                v=m.evaluate(b,t,y,keep)
                v.update({'score':name,'cut':float(cut),'guard':guard})
                rs.append(v)
    return rs

def stage(b,mode):
    bins=get_bins(b)
    if mode=='fit':
        t,side,y,XX,names,flags,context=make_full(b,'02',bins);print('F13_FEB_DATA',b,XX.shape,flush=True)
        models,tr,va=train_models(b,XX,names,t,y);print('F13_MODELS_TRAINED',b,flush=True)
        P=probs(XX,models);panel=scan(b,t,y,XX,flags,context,P,va)
        pd.DataFrame(panel).to_csv(OUT/f'FEB_ALL_1100_{b}.csv',index=False)
        baseline=m.evaluate(b,t[va],y[va],np.ones(len(va),bool))
        candidate=[v for v in panel if v['new_r9_hour_misses']==0 and v['new_r9_day_misses']==0 and v['accuracy']>=baseline['accuracy']+.002]
        winner=max(candidate,key=lambda x:(x['accuracy'],x['correct']),default=None)
        if winner is None:winner={'score':'KEEP_ALL','cut':None,'guard':'none','accuracy':baseline['accuracy'],'correct':baseline['correct']}
        freeze={'broker':b,'winner':winner,'baseline':baseline,'samples_training':len(tr),'samples_calibration':len(va),'purge_60000':True,'candidates_tested':len(panel)}
        (OUT/f'FEB_FROZEN_{b}.json').write_text(json.dumps(freeze,indent=2)+'\n')
        print('F13_FEB_FROZEN',b,'baseline',round(baseline['accuracy'],5),'winner',winner['score'],winner['cut'],winner['guard'],'precision',round(winner['accuracy'],5),'correct',winner['correct'],'hoursfail',winner.get('new_r9_hour_misses'),flush=True)
    elif mode=='transfer':
        choice=json.loads((OUT/f'FEB_FROZEN_{b}.json').read_text())['winner']
        models={};
        for role in ('correct','neutral','opposite'):
            obj=joblib.load(OUT/f'F13_EARLY_FEB_{b}_{role}.joblib');models[role]=(obj['model'],obj['columns'])
        for month in ('06','07'):
            t,side,y,XX,names,flags,ctx=make_full(b,month,bins)
            P=probs(XX,models)
            if choice['score']=='KEEP_ALL':keep=np.ones(len(t),bool)
            else:keep=~((P[choice['score']]<choice['cut'])&masks(XX,flags,ctx)[choice['guard']])
            result=m.evaluate(b,t,y,keep);base=m.evaluate(b,t,y,np.ones(len(t),bool));
            result.update({'broker':b,'month':month,'baseline':base,'choice':choice,'historically_exposed':True})
            (OUT/f'TRANSFER_FROZEN_{b}_{month}.json').write_text(json.dumps(result,indent=2)+'\n')
            np.savez_compressed(OUT/f'TRANSFER_FROZEN_{b}_{month}.npz',t=t,side=side,y=y,keep=keep.astype('int8'),context=ctx,
                pcorrect=P['correct'],pneutral=P['neutral'],popposite=P['opposite'])
            print('F13_TRANSFER',b,month,result['correct'],'/',result['signals'],'precision',round(result['accuracy'],5),'baseline',base['correct'],'/',base['signals'],'extra R9 hours',result['new_r9_hour_misses'],flush=True)
    else:raise ValueError(mode)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--broker',required=True,choices=['coinexx','dukascopy']);p.add_argument('--mode',required=True,choices=['fit','transfer']);a=p.parse_args();stage(a.broker,a.mode)
