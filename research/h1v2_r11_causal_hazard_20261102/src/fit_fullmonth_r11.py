"""R11 exhaustive, per-month independent-side supervised first-passage student.

Research ONLY. Exactly all R11 v5-gap eligible 250ms events are present as
training rows, except censored outcomes receive zero supervised weight. No
future teacher labels are predictor features. This is intentionally IN-SAMPLE
self-fit per month, NOT independent out-of-sample, calibrated expectancy, or
near-perfect prospective classification. New 300s causal ordered mark graph.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,time,math,os
import numpy as np
from h1v2_teacher import read_ticks
from entry_contract import PINNED,SYNTH,MONTHS,verify_file_sha,candidate_v5
from causal_feature_stream import USE_NAMES

ROOT=pathlib.Path('/mnt/data/h1v2_r11_lab')
MAP={-1:0,0:1,1:2};CLASSES=('BAD_ADVERSE','NEUTRAL_OR_NO_STRICT','STRICT_GOOD')

def sha(path):
    with pathlib.Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def train(mon,side,raw_dir='/mnt/data',teacher_dir=ROOT/'rebuilt_teacher',graph_dir=ROOT/'graph',out_dir=ROOT/'models',trees=20):
    if mon not in MONTHS or side not in ('BUY','SELL') or trees<1:raise ValueError('bad request')
    started=time.monotonic();sidx=0 if side=='BUY' else 1
    receipt_file=pathlib.Path(graph_dir)/f'R11_CAUSAL_GRAPH_V5_{mon}_RECEIPT.json'
    featrec=json.loads(receipt_file.read_text());graph=pathlib.Path(graph_dir)/f'R11_CAUSAL_GRAPH_V5_{mon}.npy'
    if sha(graph)!=featrec['matrix_sha256']:raise ValueError('source feature hash drift')
    if featrec['source_raw_sha256']!=PINNED[mon] or tuple(featrec['feature_names'])!=USE_NAMES:raise ValueError('graph schema/source drift')
    original=pathlib.Path(teacher_dir)/f'h1v2_dukascopy_{mon}_receipt.json'
    receipt=json.loads(original.read_text());raw=pathlib.Path(raw_dir)/f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz'
    labs=pathlib.Path(teacher_dir)/f'h1v2_dukascopy_{mon}_oracle_labels.npz'
    verify_file_sha(raw,PINNED[mon]);verify_file_sha(labs,receipt['teacher_labels_sha256'])
    t,b,a=read_ticks(raw);v5=candidate_v5(t,b,a)
    X=np.load(graph,mmap_mode='r')
    if len(X)!=len(v5):raise ValueError('feature universe is not full source v5 universe')
    with np.load(labs,allow_pickle=False) as z:
        orig_ix=z['tick_index'];kept=np.isin(orig_ix,v5,assume_unique=True)
        if not np.array_equal(orig_ix[kept],v5):raise ValueError('as-of graph labels join mismatch')
        original_code=z['code'][kept,sidx].copy()
        source_net=z['net'][kept,sidx].copy()
        source_exit=z['exit_tick_index'][kept,sidx].copy()
    del t,b,a
    y=np.where(original_code==-1,0,np.where(original_code==0,1,2)).astype(np.int8)
    good_exit=(source_exit>=0)&np.isfinite(source_net)
    weights=np.where(good_exit,1.,0.).astype(np.float32)
    # Label rows with incomplete source end are present but contribute NO class target.
    assert len(y)==len(X)==len(weights)
    import lightgbm as lgb
    model=lgb.LGBMClassifier(objective='multiclass',num_class=3,n_estimators=trees,
        num_leaves=31,max_bin=63,min_child_samples=500,learning_rate=.065,
        reg_lambda=20.,colsample_bytree=.85,n_jobs=2,random_state=20261103,
        verbosity=-1,deterministic=True,force_col_wise=True)
    model.fit(X,y,sample_weight=weights,feature_name=list(USE_NAMES))
    target=pathlib.Path(out_dir);target.mkdir(parents=True,exist_ok=True)
    path=target/f'R11_{mon}_V5_GRAPH70_{side}_ALLPOP_IN_SAMPLE_T{trees}.txt'
    model.booster_.save_model(str(path))
    pfile=target/f'R11_{mon}_{side}_ALLPOP_IN_SAMPLE_PROBS.npy'
    prob=np.lib.format.open_memmap(pfile,mode='w+',dtype=np.float32,shape=(len(X),3))
    hist=np.zeros((3,3),np.int64)
    llsum=0.;briersum=0.
    for lo in range(0,len(X),250000):
        hi=min(lo+250000,len(X))
        pp=model.booster_.predict(X[lo:hi],num_threads=2).astype(np.float32)
        if pp.shape!=(hi-lo,3):raise ValueError('fit probabilities changed dimensions')
        prob[lo:hi]=pp
        valid=weights[lo:hi]>0
        truth=y[lo:hi][valid];pr=pp[valid]
        if len(truth):
            np.add.at(hist,(truth,pr.argmax(axis=1)),1)
            llsum+=float((-np.log(np.maximum(pr[np.arange(len(truth)),truth],1e-8))).sum())
            truehot=np.eye(3,dtype=np.float32)[truth]
            briersum+=float(((pr-truehot)**2).sum(axis=1).sum())
        if (lo//250000)%5==0:print(mon,side,'SCORE',hi,len(X),flush=True)
    prob.flush();del prob
    fitted=int(weights.sum());
    result={'month':mon,'side':side,'model_kind':'LightGBM independent per-side three-class on full R11 causal 300s quote graph 70 features',
        'all_source_eligible_candidate_rows':len(X),'included_supervised_rows':fitted,'excluded_source_end_censored':int((weights==0).sum()),
        'real_source_training_all_4months':False,'exact_month_in_sample_training':True,'fitted_boosting_rounds':int(model.booster_.current_iteration()),
        'strict_original_classes':CLASSES,'class_counts_full':[int((y==k).sum()) for k in range(3)],
        'training_hyperparams':{'trees':trees,'num_leaves':31,'max_bin':63,'min_child_samples':500,'learning_rate':.065,'reg_lambda':20.,'colsample_bytree':.85,'threads':2},
        'source_raw_sha256':PINNED[mon],'original_label_sha256':receipt['teacher_labels_sha256'],
        'causal_feature_sha256':featrec['matrix_sha256'],'causal_feature_columns':list(USE_NAMES),
        'model_file':path.name,'model_sha256':sha(path),
        'full_probability_file':pfile.name,'full_probability_file_sha256':sha(pfile),
        'classification_confusion_true_rows_predicted_columns':hist.tolist(),
        'in_sample_log_loss_on_valid_exits':llsum/max(fitted,1),
        'in_sample_multiclass_brier_on_valid_exits':briersum/max(fitted,1),
        'runtime_elapsed_s':round(time.monotonic()-started,2),
        'scientific_status':'FITTED_ON_ALL_VALID_SOURCE_MONTH_EVENTS_RESUBSTITUTION_ONLY_NOT_OOS_NO_APPROVED_TRADES'}
    outf=target/f'R11_{mon}_{side}_ALLPOP_IN_SAMPLE_FIT_RECEIPT.json'
    outf.write_text(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--month',required=True,choices=MONTHS);ap.add_argument('--side',required=True,choices=('BUY','SELL'))
    ap.add_argument('--trees',type=int,default=20);a=ap.parse_args()
    o=train(a.month,a.side,trees=a.trees)
    print(json.dumps({k:o[k] for k in ('month','side','all_source_eligible_candidate_rows','included_supervised_rows','excluded_source_end_censored','runtime_elapsed_s','in_sample_log_loss_on_valid_exits','in_sample_multiclass_brier_on_valid_exits','model_sha256')},indent=2),flush=True)
