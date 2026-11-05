"""H10 as-of signal-quality *classifier* pilot; forward-looking outcome labels are response only.

Not an MT5 trading system, not a certified forward result, not a margin/cash backtest.
All Jan days research-exposed. Bayesian hierarchical priors + marked quote-Hawkes
features + independently gated Neyman-Pearson BUY/SELL abstention.
No true order book / executed trade flow is claimed from bid/ask quote revisions.
"""
from __future__ import annotations
import datetime, hashlib, json, pathlib, sys, time
import numpy as np
from numba import njit
from scipy.special import expit, logit
from scipy.stats import beta as beta_dist
import lightgbm as lgb
import h9_teacher_january as H

ROOT=H.ROOT
DS=np.array([250,1000,5000,15000,30000,60000,300000,900000,3600000,14400000],np.int64)
BAR=np.array([60000,300000,900000,3600000,14400000],np.int64)
DIM_BASE=25  # returns10, count4, spread1, spread_delta1, dt1, closed5, UTC hour2, weekday1
DIM_HAWKES=24
DIM=DIM_BASE+DIM_HAWKES
NAMES=[f'mid_return_{v}ms' for v in DS] + [f'quote_count_{v}ms' for v in (1000,5000,15000,60000)]+['spread_price','spread_change_5s','last_interquote_ms']+[f'closed_bar_return_{v}ms' for v in BAR]+['hour_sin','hour_cos','weekday_utc']+[f'hawkes_mark{mark}_tau{tau}ms' for mark in range(8) for tau in (500,2000,10000)]
assert len(NAMES)==DIM

@njit(cache=False)
def asof_feature_map(t,b,a,signal):
    """Causal quote-prefix ONLY; no H8 fill, no H8 outcomes and no next quote lookup.

    Sequential monotone pointers allow 1.5m source decisions without allocating a
    9m x number-of-timeframes dense cache. Closed bars use previously ended bars.
    """
    n=len(signal);X=np.empty((n,DIM),np.float32)
    ptr=np.zeros(len(DS),np.int64)
    close1=np.zeros(len(BAR),np.int64);close2=np.zeros(len(BAR),np.int64)
    for j in range(n):
        i=int(signal[j]);now=int(t[i]);mid=int(b[i])+int(a[i]);sp=int(a[i])-int(b[i])
        # Rolling as-of multiscale movement (not a forbidden current unfinished HTF bar).
        for k in range(len(DS)):
            lag=int(DS[k]);look=now-lag
            while ptr[k]+1<=i and t[ptr[k]+1]<=look:ptr[k]+=1
            q=int(ptr[k])
            X[j,k]=((mid-int(b[q])-int(a[q]))/2000.0) if now-int(t[0])>=lag else np.nan
        for k,slot in enumerate((1,2,3,5)):
            X[j,10+k]=float(np.log1p(i-int(ptr[slot])))
        X[j,14]=sp/1000.0
        q=int(ptr[2]);X[j,15]=(sp-(int(a[q])-int(b[q])))/1000.0
        X[j,16]=min(60000,now-int(t[i-1])) if i>0 else 60000.0
        # Last complete closed M1/M5/M15/H1/H4 bar returns, never unfinished bar.
        for k in range(len(BAR)):
            delta=int(BAR[k]);curstart=(now//delta)*delta
            last=curstart-1;prev=curstart-delta-1
            while close1[k]+1<=i and t[close1[k]+1]<=last:close1[k]+=1
            while close2[k]+1<=i and t[close2[k]+1]<=prev:close2[k]+=1
            c=int(close1[k]);p=int(close2[k])
            ok=(curstart-int(t[0])>=2*delta and c>p and int(t[c])>=curstart-delta and int(t[p])>=curstart-2*delta)
            X[j,17+k]=((int(b[c])+int(a[c])-int(b[p])-int(a[p]))/2000.0) if ok else np.nan
        hod=(now//3600000)%24 + (now%3600000)/3600000.0
        X[j,22]=np.sin(2*np.pi*hod/24.0)
        X[j,23]=np.cos(2*np.pi*hod/24.0)
        X[j,24]=((now//86400000+3)%7) # Jan 1970 Thursday=3 if Monday=0
        for k in range(DIM_BASE,DIM):X[j,k]=0.0
        # Quote revisions are NOT true broker order flow; weighted mark intensities are descriptive.
        low=max(1,i-32)
        for u in range(low,i+1):
            age=now-int(t[u]);
            if age<0 or age>30000:continue
            bd=int(b[u])-int(b[u-1]);ad=int(a[u])-int(a[u-1])
            mark=7
            if bd>0 and ad>0:mark=0
            elif bd<0 and ad<0:mark=1
            elif bd>0 and ad==0:mark=2
            elif bd<0 and ad==0:mark=3
            elif bd==0 and ad>0:mark=4
            elif bd==0 and ad<0:mark=5
            elif bd>0 and ad<0:mark=6
            elif bd<0 and ad>0:mark=7
            else:continue
            offset=DIM_BASE+mark*3
            X[j,offset]  +=np.exp(-age/500.0)
            X[j,offset+1]+=np.exp(-age/2000.0)
            X[j,offset+2]+=np.exp(-age/10000.0)
    return X

def future_labels(t,fill,ev,stop,censor):
    n=len(fill);good_f=fill>=0;early=ev[:,:,0];ad=ev[:,:,1];target=ev[:,:,3];sl=ev[:,:,5]
    stage=(early>=0)&((ad<0)|(early<ad))&good_f[:,None]&(stop[:,None]>=0)
    stage &= (t[np.maximum(early,0)]-t[np.maximum(fill[:,None],0)]<=15000)
    future_target=(target>=0)&(t[np.maximum(target,0)]-t[np.maximum(fill[:,None],0)]<30000)&(t[np.maximum(target,0)]>t[np.maximum(fill[:,None],0)])
    after_stop=(sl>=0)&((target<0)|(sl<=target))
    after_gap=(censor[:,None]>=0)&((target<0)|(censor[:,None]<=target))
    success=stage&future_target&(~after_stop)&(~after_gap)
    return success.astype(np.int8),stage.astype(np.int8)

def regime_buckets(X):
    # Fixed non-outcome-dependent bins, 4*3*3*4=144 per side Bayesian cells.
    spread=np.minimum(3, np.digitize(X[:,14],[.5,1.,1.5]))
    v=np.nan_to_num(np.abs(X[:,2]),nan=0.0)
    vol=np.minimum(2,np.digitize(v,[.35,1.25]))
    trend=np.sign(np.nan_to_num(X[:,5],nan=0.0)).astype(np.int32)+1
    # Four UTC session blocks only (rough descriptors; not news vintage verification).
    hour=(np.arctan2(X[:,22],X[:,23])%(2*np.pi))/(2*np.pi)*24
    session=(hour//6).astype(np.int32)
    return ((spread*3+vol)*3+trend)*4+session

def fit_bayes_prior(keys,y,train):
    # original beta-binomial shrinkage alpha=2,beta=8 (prior mean20%).
    out=[]
    for s in range(2):
        num=np.bincount(keys[train],minlength=144)
        hit=np.bincount(keys[train],weights=y[train,s],minlength=144)
        probs=(2+hit)/(10+num)
        out.append(probs)
    return np.stack(out,axis=1)

def win_prob_with_prior(model_prob,bayes_prob):
    pp=np.clip(model_prob,.00001,.99999)
    prior=np.clip(bayes_prob,.00001,.99999)
    return expit(.75*logit(pp)+.25*logit(prior))

def find_side_gate(scores,labels,calib,null_alpha=.01,error_alpha=.1):
    # NP: P(accept|incorrect) Clopper Pearson upper <=1% on independent calibration;
    # and upper credible bound on conditional accepted failure <=10%.
    null=calib & (labels==0);nnull=int(null.sum())
    for thr in (.6,.7,.8,.9,.95,.98,.995,.999):
        accept=calib&(scores>=thr)
        n=int(accept.sum());bad=int(np.sum(accept&(labels==0)))
        if n<100:continue
        cp=float(beta_dist.ppf(.95,bad+1,nnull-bad)) if bad<nnull else 1.0
        risk=float(beta_dist.ppf(.95,bad+1,n-bad)) if bad<n else 1.0
        if cp<=null_alpha and risk<=error_alpha:return dict(threshold=thr,n_calib=n,bad_calib=bad,cp_null_admission_upper=cp,posterior_selected_error_upper=risk)
    return dict(threshold=None,n_calib=0,bad_calib=None,cp_null_admission_upper=None,posterior_selected_error_upper=None)

def fit_models(X,y,keys,t_signal,model_variant,train,calib,test):
    n_features=DIM_BASE if model_variant=='NO_HAWKES' else DIM
    # Deterministic response-independent 1/4 subsample to cap CPU, original evaluation full cohort.
    sample=train & ((np.arange(len(train),dtype=np.int64)*2654435761 % 4)==0)
    p=np.zeros((len(train),2),np.float32)
    models=[]
    bayes=fit_bayes_prior(keys,y,train)
    for side in (0,1):
        ds=lgb.Dataset(X[sample,:n_features],label=y[sample,side],feature_name=NAMES[:n_features],free_raw_data=True)
        model=lgb.train({'objective':'binary','learning_rate':.055,'num_leaves':19,'min_data_in_leaf':200,'feature_fraction':1.,'bagging_fraction':1.,'verbosity':-1,'seed':41227,'num_threads':4,'deterministic':True,'force_col_wise':True},ds,num_boost_round=65)
        model_out=model.predict(X[:, :n_features],num_threads=4)
        p[:,side]=win_prob_with_prior(model_out,bayes[keys,side]).astype(np.float32)
        models.append(model)
    gates=[find_side_gate(p[:,s],y[:,s],calib) for s in (0,1)]
    # ONLINE as-of action at signal time: gate EACH SIDE BEFORE argmax. No labels used.
    eligible=np.zeros_like(p,dtype=bool)
    for s in (0,1):
        if gates[s]['threshold'] is not None:eligible[:,s]=(p[:,s]>=gates[s]['threshold'])
    score=np.where(eligible,p,-1.)
    side=np.argmax(score,axis=1)
    chosen=score[np.arange(len(score)),side]>=0
    # Per-cohort recall/rejection, not real traded pnl/occupancy.
    evaluation={}
    for tag,mask in (('TRAIN',train),('CALIB',calib),('EVAL',test)):
        ids=mask&chosen;count=int(ids.sum());ok=int(y[np.where(ids)[0],side[ids]].sum()) if count else 0
        evd={'all_original_signal_candidates':int(mask.sum()),'admitted_candidate_actions':count,'correct_first15_and_TP0300_lt30':ok,
             'incorrect_or_unfillable':count-ok,'precision_of_admissions':round(ok/count,6) if count else None,
             'abstention_rate':round(1-count/max(int(mask.sum()),1),6)}
        for s,label in enumerate(('BUY','SELL')):
            entered=mask&chosen&(side==s)
            n_s=int(entered.sum());success=int(y[entered,s].sum()) if n_s else 0
            evd[label]={'admitted':n_s,'correct':success,'incorrect':n_s-success}
        evaluation[tag]=evd
    # Without hindsight arbitration, fixed top 1% and 0.1% by out-of-sample predicted confidence
    # from calibration quantiles (diagnostics only, not a deployable NP gate).
    diagnostics={}
    for frac in (.01,.001):
        bestp=p.max(1);thr=float(np.quantile(bestp[calib],1-frac))
        idx=test&(bestp>=thr);s=np.argmax(p[idx],axis=1)
        yp=y[idx]
        cnt=int(idx.sum());hits=int(yp[np.arange(cnt),s].sum()) if cnt else 0
        diagnostics[str(frac)]={'calibration_probability_quantile':thr,'eval_candidates':cnt,'actual_correct':hits,'eval_precision':round(hits/cnt,6) if cnt else None}
    return {'variant':model_variant,'n_features':n_features,'fit_selected_train':int(sample.sum()),'asof_feature_names':NAMES[:n_features],
            'side_gates':gates,'cohort_results':evaluation,'top_probability_diagnostic':diagnostics,
            'feature_importance_buy':sorted(zip(NAMES[:n_features],models[0].feature_importance('gain')),key=lambda v:-v[1])[:12],
            'feature_importance_sell':sorted(zip(NAMES[:n_features],models[1].feature_importance('gain')),key=lambda v:-v[1])[:12]}

def run():
    start=time.monotonic();t,b,a,signal,fill,ev,stop,censor,ref,q0=H.load()
    feat=asof_feature_map(t,b,a,signal)
    assert feat.shape==(len(signal),DIM)
    # Causal future-mutation invariant: change all 100 quote fields after the selected original prefix.
    seq=signal[20000:20110]
    ref_feat=asof_feature_map(t,b,a,seq)
    mutated_b=b.copy();mutated_a=a.copy();cut=int(seq[-1])+1;mutated_b[cut:cut+100]+=20000;mutated_a[cut:cut+100]+=20000
    changed=asof_feature_map(t,mutated_b,mutated_a,seq)
    assert np.array_equal(np.nan_to_num(ref_feat,nan=-9999),np.nan_to_num(changed,nan=-9999)),'H10 FEATURE FUTURE MUTATION LEAK'
    del mutated_b,mutated_a
    y,stage=future_labels(t,fill,ev,stop,censor)
    assert y.shape==(len(signal),2)
    keys=regime_buckets(feat)
    utc_day=((t[signal]-q0)//86400000).astype(np.int32)
    train=(utc_day>=1)&(utc_day<=13)
    calib=(utc_day>=14)&(utc_day<=21)
    test=(utc_day>=22)&(utc_day<=30)
    assert not np.any(train&calib) and not np.any(test&calib)
    assert int(np.sum(train))>300000 and int(np.sum(test))>100000
    # Day cohorts are disjoint and have entire >=30s halo by construction.
    pop={'source':H.SOURCE,'month':H.MONTH,'n_asof_first_1sec_signals':len(signal),'train_n':int(train.sum()),'calib_n':int(calib.sum()),'eval_n':int(test.sum()),
         'train_success_buy':int(y[train,0].sum()),'train_success_sell':int(y[train,1].sum()),
         'calib_success_buy':int(y[calib,0].sum()),'calib_success_sell':int(y[calib,1].sum()),
         'eval_success_buy':int(y[test,0].sum()),'eval_success_sell':int(y[test,1].sum()),
         'future_mutation_asof_test':'PASS_110_ORIGINAL_SIGNALS','feature_shape':[int(d) for d in feat.shape]}
    print('H10_POPULATION',json.dumps(pop),flush=True)
    models=[]
    for name in ('NO_HAWKES','MARKED_HAWKES'):
        r=fit_models(feat,y,keys,t[signal],name,train,calib,test)
        models.append(r)
        print('H10_MODEL',name,json.dumps({'gates':r['side_gates'],'cohorts':r['cohort_results'],'top':r['top_probability_diagnostic']}),flush=True)
    report={'classification':'PREREGISTERED_ASOF_TRAIN_CALIB_EVAL_CONDITIONAL_SIGNAL_CLASSIFICATION_NOT_CASH_PORTFOLIO',
            'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_raw_sha':H.sha_file(H.ORIGINAL),'source_H8_zip_sha':H.sha_file(H.H8ZIP),
            'past_only_no_future_feature':'verified future mutation test 110 source candidate prefix',
            'source_regime_prior':'beta-binomial alpha2 beta8 per spread-vol-trend-session cell; NO actual news or Level2 LOB',
            'target':'H9 POST ENTRY first signed MID+0.10 before -0.25 by15 AND liquidation+0.30 first before risk stop under30',
            'training_and_calibration_not_blind_OOS':True,'source_label_selection_no_future':'as-of BUY or SELL highest gated score only; H8 labels used in responses/evaluation',
            'calendar_risk_valuation':'NOT EXECUTED; no account PnL or MT5 dealer fills','population':pop,'models':models,'elapsed_seconds':time.monotonic()-start}
    target=ROOT/'results'/'H10_ASOF_BAYES_MARKED_HAWKES_NEYMAN_PEARSON_JAN_DUKAS_RESEARCH_PILOT.json'
    target.write_text(json.dumps(report,indent=2,default=lambda a:float(a) if isinstance(a,np.generic) else str(a))+'\n')
    print('H10_FINAL',str(target),'seconds',round(report['elapsed_seconds'],2),flush=True)
    return report

if __name__=='__main__':run()
