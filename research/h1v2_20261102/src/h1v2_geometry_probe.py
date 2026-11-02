"""Research-only held-month diagnostic of H1V2 ordered-quote geometry.

Fixed 3-class LightGBM training Jan+Feb, June-only threshold calibration,
July untouched test. This is NOT H1V2 hindsight oracle and is NOT deployed.
The month samples are uniform from eligible 250ms events, with no candidate
selection based on future labels. No trading results or synthetic PnL inferred.
"""
from __future__ import annotations
import json, math, time
from pathlib import Path
import numpy as np
import lightgbm as lgb
from sklearn.metrics import roc_auc_score,log_loss
from h1v2_geometry import NAMES


def wilson_lower(correct,n,z=1.96):
    if n==0:return 0.
    p=correct/n;a=z*z/n
    return float((p+a*.5-z*np.sqrt((p*(1-p)+a*.25)/n))/(1+a))

def freeze_threshold(scores,pred_side,y,min_entries=150,lower=.80):
    """June ONLY: largest admitted sample with 95% Wilson lower >=0.80."""
    order=np.argsort(-scores,kind='stable')
    cor=np.cumsum(pred_side[order]==y[order]);best=0
    for count in range(min_entries,len(order)+1):
        if wilson_lower(int(cor[count-1]),count)>=lower:best=count
    if best==0:return None,0
    # Floating ties may enlarge selection; choose strict probability boundary.
    threshold=float(scores[order[best-1]])
    admitted=int(np.sum(scores>=threshold))
    if wilson_lower(int(np.sum((pred_side==y)&(scores>=threshold))),admitted)<lower:
        return None,0
    return threshold,admitted

def evaluate_month(prob,y,threshold):
    score=np.max(prob[:,1:3],axis=1)
    side=np.argmax(prob[:,1:3],axis=1)+1
    result={'samples':int(len(y)), 'population_any_strict_good_rate':float(np.mean(y!=0))}
    for fraction in (.01,.05,.10,.25):
        n=max(1,int(math.ceil(len(y)*fraction)))
        order=np.argsort(-score)[:n]
        hit=(side[order]==y[order])
        result[f'precision_top_{int(fraction*100)}pct']=float(hit.mean())
        result[f'correct_top_{int(fraction*100)}pct']=int(hit.sum())
    if threshold is None:
        result['calibrated_gate']='NO_80PCT_WILSON_ELIGIBLE_THRESHOLD'
        result['qualified_count']=0
    else:
        allowed=score>=threshold; count=int(allowed.sum());correct=int((allowed & (side==y)).sum())
        result.update(calibrated_gate='FROZEN_JUNE_THRESHOLD',threshold=threshold,
                      qualified_count=count,strict_correct=correct,
                      precision=float(correct/count) if count else None,
                      lower_wilson_95=wilson_lower(correct,count))
    return result

def run(results='/mnt/data/h1v2/results'):
    root=Path(results)
    z={}
    for month in ('01','02','06','07'):
        with np.load(root/f'h1v2_{month}_causal_geometry_atlas.npz',allow_pickle=False) as f:
            z[month]={'x':f['X'].copy(),'y':f['y'].copy(),'ts':f['ts'].copy()}
    train_x=np.concatenate([z['01']['x'],z['02']['x']]);train_y=np.concatenate([z['01']['y'],z['02']['y']])
    valid_x,valid_y=z['06']['x'],z['06']['y'];test_x,test_y=z['07']['x'],z['07']['y']
    out={'setup':{'train_months':['01','02'],'calibration_month':'06','untouched_test_month':'07',
                  'target':'strict 30s BUY or SELL vs NONE, executable R9 positive net',
                  'confidence':'95pct Wilson lower >=80pct on 150+ calibration sample actions',
                  'sample_size_per_month':len(test_y),'exhaustive_labels_precomputed_on_all_250ms_candidates':True,
                  'no_fitted_policy_approval':True},'models':{}}
    for name,cols in [('slow_5m_geometry_control',np.array([i for i,x in enumerate(NAMES) if x.endswith('_300000ms')]+[99],np.int64)),('all_subminute_geometry',np.arange(100,dtype=np.int64))]:
        st=time.monotonic();params=dict(objective='multiclass',num_class=3,learning_rate=.05,num_leaves=15,max_depth=6,
                        min_data_in_leaf=90,feature_fraction=.85,bagging_fraction=1.,verbosity=-1,seed=20261102,num_threads=4)
        model=lgb.train(params,lgb.Dataset(train_x[:,cols],label=train_y),num_boost_round=70)
        cal=model.predict(valid_x[:,cols]);test=model.predict(test_x[:,cols])
        sc=np.max(cal[:,1:3],axis=1);sides=np.argmax(cal[:,1:3],axis=1)+1
        threshold,count=freeze_threshold(sc,sides,valid_y)
        m={'n_features':len(cols),'calibration_threshold':threshold,'calibration_qualified_n':count,
           'june':evaluate_month(cal,valid_y,threshold),'july':evaluate_month(test,test_y,threshold),
           'july_log_loss':float(log_loss(test_y,test,labels=[0,1,2])),
           'elapsed_seconds':round(time.monotonic()-st,2),
           'status':'RESEARCH_DIAGNOSTIC_ONLY_NOT_AN_EXECUTABLE_POLICY'}
        out['models'][name]=m
        model.save_model(str(root/f'h1v2_{name}_janfeb_fixed.txt'))
    (root/'h1v2_geometry_probe_report.json').write_text(json.dumps(out,indent=2))
    return out
if __name__=='__main__':print(json.dumps(run(),indent=2),flush=True)
