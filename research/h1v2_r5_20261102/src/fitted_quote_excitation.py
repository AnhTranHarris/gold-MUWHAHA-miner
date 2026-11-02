"""H1V2 R5: fitted nonnegative six-mark quote-excitation, research only.

Predict the next 1s SIX quote-revision mark counts from past-only decays
of previously observed quote revisions. This is a discrete-time intensity
proxy with Poisson quasi-likelihood, NOT a continuous-time Hawkes MLE.
Critically, no future counts or teacher-side outcomes enter as-of features.
"""
from __future__ import annotations
import json,hashlib,time
from pathlib import Path
import numpy as np
from numba import njit
from scipy.optimize import minimize
from scipy.special import gammaln
from h1v2_teacher import read_ticks
from h1v2_freeze import PINNED
from marked_quote_sequences import mark_quotes
MONTHS=('01','02','06','07')
ROOT=Path('/mnt/data/h1v2_r5/results')
@njit(cache=True)
def next_marks(t,mark,ix,horizon_ms=1000):
    """Count only future ordinal j>ix with t[j]<=t[ix]+horizon_ms.
    Same-ms later rows ARE future events; never include them in X.
    """
    out=np.zeros((len(ix),6),np.int16)
    for row in range(len(ix)):
        i=ix[row];hi=np.searchsorted(t,t[i]+horizon_ms,side='right')
        for j in range(i+1,hi):
            m=mark[j]
            if m>0:out[row,m-1]+=1
    return out

def extract_targets(raw_root=Path('/mnt/data'),marked_root=Path('/mnt/data/h1v2_r4/results'),out_root=ROOT):
    out_root=Path(out_root);out_root.mkdir(parents=True,exist_ok=True)
    receipts={}
    for m in MONTHS:
        raw=Path(raw_root)/f'XAUUSD_DUKAS_2026_{m}_ticks.csv.gz'
        sha=hashlib.sha256(raw.read_bytes()).hexdigest()
        if sha!=PINNED[m]:raise ValueError(f'raw source mismatch {m}')
        t,b,a=read_ticks(raw)
        with np.load(Path(marked_root)/f'H1V2_R4_MARKED_ATLAS_{m}.npz') as z:
            ix=z['ix'];ts=z['ts'];xx=z['Xmark'];cc=z['side_class']
            if not np.array_equal(t[ix],ts):raise ValueError('label join mismatch')
            assert len(ix)==15000
            marks=mark_quotes(b,a)
            yy=next_marks(t,marks,ix)
            assert yy.shape==(15000,6)
            # 18 250ms/1s/5s exponential past-only mark weights.
            excitation=xx[:,30:48].copy()
            out=out_root/f'R5_MARK_1SEC_{m}.npz'
            np.savez_compressed(out,ts=ts,ix=ix,X=excitation,Y=yy,side_class=cc)
            receipts[m]={'rows':len(ix),'six_mark_future_total':yy.sum(axis=0).astype(int).tolist(),
               'raw_sha256':sha,'target_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
               'same_ms_ordinal_policy':'future j > ix, even when t[j]==t[ix]; past excitation from R4 j<=ix'}
    (out_root/'R5_TARGET_SOURCE_RECEIPTS.json').write_text(json.dumps(receipts,indent=2))
    return receipts

def design(x,mode):
    x=np.asarray(x,dtype=np.float64)
    if mode=='null':return np.ones((len(x),1),dtype=np.float64)
    if mode=='cross':return np.column_stack((np.ones(len(x)),x))
    raise ValueError(mode)

def fit_poisson(X,Y,mode='cross',iterations=160,penalty=.002):
    """Nonnegative linear conditional intensity, fitted Poisson score.

    Each of 6 target rates: lambda = mu+lagged mark excitation, all >=0.
    For self-only the three lag coefficients correspond to same mark.
    SciPy L-BFGS-B with EXACT gradient, not simulated hyperparameter claims.
    """
    X=np.asarray(X,np.float64);Y=np.asarray(Y,np.float64)
    coefs=np.zeros((6,19),np.float64)
    for k in range(6):
        cols=np.asarray([0] if mode=='null' else ([0,1+k,7+k,13+k] if mode=='self' else list(range(19))),np.int64)
        base=np.ones((len(X),1),np.float64)
        design_matrix=base if mode=='null' else np.column_stack((base,X))[:,cols]
        yy=Y[:,k]
        mean_y=max(float(yy.mean()),1e-5)
        init=np.zeros(len(cols));init[0]=max(.01,mean_y*.75)
        def fn(w):
            lam=np.maximum(design_matrix@w,1e-8)
            f=float(np.mean(lam-yy*np.log(lam)) +penalty*np.sum(w[1:]**2))
            grad=design_matrix.T@(1.-yy/lam)/len(yy)
            grad[1:]+=2.*penalty*w[1:]
            return f,np.asarray(grad,np.float64)
        res=minimize(fn,init,jac=True,method='L-BFGS-B',bounds=[(1e-4,None)]+[(0.,None)]*(len(cols)-1),options={'maxiter':iterations,'ftol':1e-10})
        coefs[k,cols]=res.x
        assert np.all(coefs[k]>=0) and np.all(np.isfinite(res.x))
    return coefs

def predict(X,c):
    return np.maximum(np.column_stack((np.ones(len(X)),X.astype(np.float64)))@c.T,1e-8)

def diagnostics(Y,rates):
    yy=Y.astype(np.float64);rr=np.maximum(rates,1e-8)
    return {'mean_poisson_nll':float(np.mean(rr-yy*np.log(rr)+gammaln(yy+1))),
       'predicted_sum':rr.mean(axis=0).tolist(),
       'actual_sum':yy.mean(axis=0).tolist(),
       'sign_pressure_correlation':float(np.corrcoef((rr[:,[0,2,4]].sum(axis=1)-rr[:,[1,3,5]].sum(axis=1)),(yy[:,[0,2,4]].sum(axis=1)-yy[:,[1,3,5]].sum(axis=1)))[0,1])}

def run(root=ROOT):
    root=Path(root);data={}
    for m in MONTHS:
        with np.load(root/f'R5_MARK_1SEC_{m}.npz') as z:
            data[m]=(z['X'].copy(),z['Y'].copy())
    x=np.vstack([data[m][0] for m in ('01','02')]);y=np.vstack([data[m][1] for m in ('01','02')]);receipt={}
    for mode in ('null','self','cross'):
        t0=time.monotonic();coeff=fit_poisson(x,y,mode)
        mrec={'trained_months':['01','02'],'mode':mode,'fit_seconds':round(time.monotonic()-t0,2),'coefficient_matrix':coeff.tolist(),'eval':{}}
        for m in MONTHS:
            mx,my=data[m];rates=predict(mx,coeff)
            mrec['eval'][m]=diagnostics(my,rates)
            np.savez_compressed(root/f'R5_FITTED_INTENSITY_{mode}_{m}.npz',rates=rates.astype(np.float32),ts=0+np.arange(len(mx)))
        receipt[mode]=mrec
        print('fit',mode,'July nll',mrec['eval']['07']['mean_poisson_nll'],'seconds',mrec['fit_seconds'],flush=True)
    null=receipt['null']['eval']['07']['mean_poisson_nll']
    for mode in ('self','cross'):
        receipt[mode]['july_loglik_gain_over_null_per_one_mark_target']=null-receipt[mode]['eval']['07']['mean_poisson_nll']
    (root/'R5_FITTED_EXCITATION_RESULTS.json').write_text(json.dumps({'scientific_status':'FITTED_DISCRETE_TIME_INTENSITY_NOT_CONTINUOUS_HAWKES','controls':receipt},indent=2))
    return receipt
if __name__=='__main__':
    print(json.dumps(extract_targets(),indent=2),flush=True)
    run()
