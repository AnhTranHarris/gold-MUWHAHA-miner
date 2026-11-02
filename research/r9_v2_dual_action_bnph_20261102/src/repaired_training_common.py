"""Shared chronological calibration/evaluation primitives for repaired R9 v2."""
from __future__ import annotations
import hashlib, math
import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import roc_auc_score,log_loss
from decision import select_dual

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for c in iter(lambda:f.read(1<<20),b''):h.update(c)
    return h.hexdigest()

def masks(ts,embargo_ms=60000):
    ts=np.asarray(ts,np.int64);days=np.unique(ts//86400000)
    a=max(1,int(len(days)*.50));b=max(a+1,int(len(days)*.72))
    if b>=len(days):raise ValueError('insufficient active days')
    fit_end=int(days[a])*86400000;cal_end=int(days[b])*86400000
    tr=ts<fit_end-embargo_ms;cal=(ts>=fit_end+embargo_ms)&(ts<cal_end-embargo_ms);chk=ts>=cal_end+embargo_ms
    cd=np.unique(ts[cal]//86400000)
    if len(cd)<2:raise ValueError('calibration needs >=2 active days')
    cmid=int(cd[max(1,len(cd)//2)])*86400000
    cala=cal&(ts<cmid-embargo_ms);calb=cal&(ts>=cmid+embargo_ms)
    if not (tr.any() and cala.any() and calb.any() and chk.any()):raise ValueError('empty chronological segment')
    assert ts[tr].max()<ts[cala].min()<ts[calb].min()<ts[chk].min()
    return tr,cala,calb,chk,dict(active_days=len(days),fit_end=fit_end,calibration_end=cal_end,calibration_ab_split=cmid,embargo_ms=embargo_ms)

def action_labels(good,neutral):
    return np.where(np.asarray(good)==1,2,np.where(np.asarray(neutral)==1,1,0)).astype(np.uint8)

def fit_iso(score,y):
    iso=IsotonicRegression(out_of_bounds='clip',y_min=0.,y_max=1.)
    iso.fit(np.asarray(score,float),np.asarray(y,float));return iso

def apply_iso(iso,x):return np.asarray(iso.predict(np.asarray(x,float)),np.float64)
def iso_pack(iso):return np.asarray(iso.X_thresholds_,np.float64),np.asarray(iso.y_thresholds_,np.float64)

def shrink(q,priors,w):
    out=(1.-w)*np.asarray(q,np.float64)+w*np.asarray(priors,np.float64)[None,:,:]
    out/=out.sum(axis=2,keepdims=True);return out

def choose_prior_weight(q,y,priors):
    yy=np.asarray(y).reshape(-1);best=None
    for w in (0.,.02,.05,.10,.20):
        loss=float(log_loss(yy,shrink(q,priors,w).reshape(-1,3),labels=[0,1,2]));cand=(loss,w)
        if best is None or cand<best:best=cand
    return best[1],best[0]

def calibrate_action_probs(q,y,priors,w):
    z=shrink(q,priors,w);out=np.empty_like(z);isos={}
    for j in (0,1):
        ic=fit_iso(z[:,j,2],np.asarray(y)[:,j]==2);iw=fit_iso(z[:,j,0],np.asarray(y)[:,j]==0)
        pc=apply_iso(ic,z[:,j,2]);pw=apply_iso(iw,z[:,j,0]);excess=np.maximum(1.,pc+pw);pc/=excess;pw/=excess
        out[:,j,2]=pc;out[:,j,0]=pw;out[:,j,1]=np.maximum(0.,1.-pc-pw);isos[(j,'correct')]=ic;isos[(j,'wrong')]=iw
    return out,isos

def apply_action_calibration(q,priors,w,isos):
    z=shrink(q,priors,w);out=np.empty_like(z)
    for j in (0,1):
        pc=apply_iso(isos[(j,'correct')],z[:,j,2]);pw=apply_iso(isos[(j,'wrong')],z[:,j,0]);excess=np.maximum(1.,pc+pw);pc/=excess;pw/=excess
        out[:,j,2]=pc;out[:,j,0]=pw;out[:,j,1]=np.maximum(0.,1.-pc-pw)
    return out

def payoff_lcb_bins(pcorrect,net,bins=30,min_n=150,z=1.64):
    pcorrect=np.asarray(pcorrect);net=np.asarray(net);out=np.full((2,bins),-np.inf,np.float32);counts=np.zeros((2,bins),np.int32)
    for j in (0,1):
        idx=np.minimum(bins-1,(np.clip(pcorrect[:,j],0,1)*bins).astype(np.int32))
        for k in range(bins):
            m=(idx==k)&np.isfinite(net[:,j]);n=int(m.sum());counts[j,k]=n
            if n>=min_n:
                v=net[m,j].astype(np.float64);out[j,k]=float(v.mean()-z*v.std(ddof=1)/math.sqrt(n))
    return out,counts

def expected_from_bins(p,bins):
    nbin=bins.shape[1];idx=np.minimum(nbin-1,(np.clip(np.asarray(p)[:,:,2],0,1)*nbin).astype(np.int32))
    return np.column_stack((bins[0,idx[:,0]],bins[1,idx[:,1]]))

def raw_action_predict(models,X):
    buy,sell=models
    return np.stack((buy.predict(X,num_threads=2),sell.predict(X,num_threads=2)),axis=1)

def eval_policy(name,mask,X,good,net,opp_model,opp_iso,action_models,priors,w,isos,opp_cut,side_cut,paybins,limits,baseline_side):
    rows=np.where(mask)[0];xx=X[rows];pop=apply_iso(opp_iso,opp_model.predict(xx,num_threads=2))
    q=apply_action_calibration(raw_action_predict(action_models,xx),priors,w,isos)
    side=select_dual(q,expected_from_bins(q,paybins),side_cut,limits)
    opp_ok=(pop>=limits.min_opportunity)&(pop>opp_cut);act=np.where(opp_ok,side,0).astype(np.int8)
    chosen=act!=0;sidecol=np.where(act==1,0,1);rr=np.arange(len(act));g=np.asarray(good)[rows];nnet=np.asarray(net)[rows]
    any_good=g.any(axis=1);one_good=g.sum(axis=1)==1;neither=~any_good;truth=np.where(g[:,0]==1,1,-1);ranked=np.where(q[:,0,2]>=q[:,1,2],1,-1)
    n=int(chosen.sum());correct=int(g[rr[chosen],sidecol[chosen]].sum()) if n else 0;actual=float(np.nansum(nnet[rr[chosen],sidecol[chosen]])) if n else 0.
    selected_neither=int((chosen&neither).sum());capture=int((chosen&any_good&(act==truth)).sum())
    return dict(segment=name,events=len(rows),opportunity_auc=float(roc_auc_score(any_good,pop)) if any_good.any() and (~any_good).any() else None,
        learned_rank_unique_accuracy=float(np.mean(ranked[one_good]==truth[one_good])) if one_good.any() else None,
        baseline_unique_accuracy=float(np.mean(np.asarray(baseline_side)[rows][one_good]==truth[one_good])) if one_good.any() else None,
        selected=n,strict_correct=correct,strict_correct_rate=(correct/n if n else None),selected_net=actual,
        neither_good_events=int(neither.sum()),neither_good_selected=selected_neither,bad_opportunity_rejection=(1-selected_neither/neither.sum() if neither.sum() else None),
        any_good_events=int(any_good.sum()),correct_opportunity_capture=capture,correct_opportunity_capture_rate=(capture/any_good.sum() if any_good.sum() else None),
        selected_unique_direction_accuracy=(float(np.mean(act[chosen&one_good]==truth[chosen&one_good])) if (chosen&one_good).any() else None))
