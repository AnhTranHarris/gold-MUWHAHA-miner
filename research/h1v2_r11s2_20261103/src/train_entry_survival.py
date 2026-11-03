"""H1V2-R11S2, four separate in-sample source-month as-of-feature students, bounded fitting.

Targets: strict first 15s favorable + full 30s no-adverse, separately for BUY
and SELL. Source 70-feature causal quote graph; features NEVER contain future
labels. Research ONLY; in-sample self-fit does not imply prospective accuracy.
Past R11 and original H1V2 teacher, H1V2-R11S future oracle remain immutable.
"""
from __future__ import annotations
import pathlib,json,hashlib,os,time,math,argparse
import numpy as np
import pandas as pd
import lightgbm as lgb
from numba import njit

ROOT=pathlib.Path('/mnt/data/h1v2_r11_s2_full_month')
LAB=pathlib.Path('/mnt/data/h1v2_r11_lab/survival/full_population')
GRAPH=pathlib.Path('/mnt/data/h1v2_r11_lab/graph')
RAW=pathlib.Path('/mnt/data')
SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}
SOURCE_SHA={'01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d','06':'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2','07':'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7'}
CLASS=('ADVERSE30','SURVIVE30_NOT_FAVORABLE15','SURVIVE30_AND_FAVORABLE15')
FRACTIONS=(.005,.01,.025,.05,.10,.20,.35,.50,1.0)

def digest(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def labels(file,side):
    if side not in ('BUY','SELL'):raise ValueError('side')
    with np.load(file,allow_pickle=False) as z:
        coverage=(z['h15_coverage']&z['h30_coverage']).copy()
        survivor=z[f'h30_{side}_survives_no_adverse'].copy()
        favorable=z[f'h15_{side}_survives_and_favorable'].copy()
        t=z['entry_utc_ms'].copy();ix=z['source_tick_ordinal'].copy()
    code=np.where(~survivor,0,np.where(favorable,2,1)).astype(np.uint8)
    return code,coverage,t,ix

def verify_inputs(mon):
    if mon not in SOURCE_SHA:raise ValueError(mon)
    raw=RAW/f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz'
    if digest(raw)!=SOURCE_SHA[mon]:raise ValueError('raw SHA mismatch '+mon)
    zfile=LAB/f'month_{mon}'/f'R11S_{mon}_ALL_V5_CANDIDATE_H15_H30_EXACT_SURVIVAL_LABELS.npz'
    manifest=json.loads((LAB/f'month_{mon}'/f'R11S_{mon}_FULL_SOURCE_LABEL_MANIFEST.json').read_text())
    if digest(zfile)!=manifest['full_population_sha256'] or manifest['source_raw_sha256']!=SOURCE_SHA[mon]:raise ValueError('full label SHA mismatch '+mon)
    graph=GRAPH/f'R11_CAUSAL_GRAPH_V5_{mon}.npy'
    rec=json.loads((GRAPH/f'R11_CAUSAL_GRAPH_V5_{mon}_RECEIPT.json').read_text())
    if digest(graph)!=rec['matrix_sha256'] or rec['source_raw_sha256']!=SOURCE_SHA[mon]:raise ValueError('graph SHA mismatch '+mon)
    x=np.load(graph,mmap_mode='r')
    if x.shape!=(manifest['candidate_rows'],70):raise ValueError('feature row/column mismatch '+mon)
    return x,zfile,manifest,rec

@njit(cache=True)
def _replay_30sec(utc_ms,prob_b,prob_s,y_b,y_s,covered,cut):
    n=len(utc_ms);outidx=np.empty(n,np.int32);side=np.empty(n,np.int8)
    count=0;win=0;wrong=0;neu=0;censored=0;last_entry=-9223372036854775000
    for i in range(n):
        b=prob_b[i];s=prob_s[i];score=b if b>=s else s
        if score<cut or utc_ms[i]<=last_entry+30000:continue
        si=0 if b>=s else 1
        outidx[count]=i;side[count]=si;count+=1;last_entry=utc_ms[i]
        if not covered[i]:censored+=1
        elif (y_b[i] if si==0 else y_s[i])==2:win+=1
        elif (y_b[i] if si==0 else y_s[i])==1:neu+=1
        else:wrong+=1
    return outidx[:count],side[:count],win,neu,wrong,censored

def fit(mon,side,rounds=24,max_train_rows=400000):
    st=time.monotonic();ROOT.joinpath('models').mkdir(exist_ok=True,parents=True)
    X,zfile,manifest,feat=verify_inputs(mon)
    y,complete,t,ix=labels(zfile,side)
    if len(y)!=len(X) or not np.all(np.diff(ix)>0) or not np.all(np.diff(t)>=0):raise ValueError('candidate or source chronology')
    classcount=np.bincount(y[complete],minlength=3)
    print('TRAIN START',mon,side,'rows',len(y),'class_counts_valid',classcount.tolist(),flush=True)
    w=complete.astype(np.float32)
    w[y==2]*=1.5
    # Deterministic calendar-wide systematic training subset, bounded to avoid
    # the 4GB cgroup memory limit. Every full month row is scored, and ALL
    # full source labels and chronology are audited; do not call this 100% fit.
    trainidx=np.unique(np.linspace(0,len(X)-1,min(max_train_rows,len(X)),dtype=np.int64))
    Xt=np.asarray(X[trainidx],dtype=np.float32);yt=y[trainidx];wt=w[trainidx]
    print("BOUNDED_FULL_CALENDAR_TRAIN_ROWS",mon,side,len(trainidx),"of",len(y),flush=True)
    params=dict(objective='multiclass',num_class=3,learning_rate=.08,num_leaves=63,
        min_data_in_leaf=180,lambda_l2=12.,max_bin=31,feature_fraction=.85,
        num_threads=2,verbosity=-1,deterministic=True,force_col_wise=True,seed=20261103)
    trainer=lgb.Dataset(Xt,label=yt,weight=wt,feature_name=feat['feature_names'],free_raw_data=True)
    model=lgb.train(params,trainer,num_boost_round=rounds)
    path=ROOT/'models'/f'R11S2_{mon}_{side}_FULLPOP_SAME_MONTH_15FAV30SURV_{rounds}TREES.txt'
    model.save_model(str(path))
    outfile=ROOT/'models'/f'R11S2_{mon}_{side}_FULLPOP_SAME_MONTH_PGOOD.npy'
    scores=np.lib.format.open_memmap(outfile,mode='w+',dtype=np.float32,shape=(len(X),))
    confusion=np.zeros((3,3),dtype=np.int64);sumnll=0.;nvalid=0
    for lo in range(0,len(X),250000):
        hi=min(lo+250000,len(X));pp=model.predict(X[lo:hi],num_threads=2)
        if pp.shape!=(hi-lo,3) or not np.isfinite(pp).all():raise ValueError('probabilities nonfinite/wrong shape')
        scores[lo:hi]=pp[:,2].astype(np.float32)
        valid=complete[lo:hi];yy=y[lo:hi][valid];p=pp[valid]
        if len(yy):
            np.add.at(confusion,(yy,p.argmax(axis=1)),1)
            sumnll+=float((-np.log(np.maximum(p[np.arange(len(yy)),yy],1e-9))).sum());nvalid+=len(yy)
    scores.flush();del scores
    receipt=dict(month=mon,side=side,source_raw_sha256=SOURCE_SHA[mon],exact_full_label_sha256=manifest['full_population_sha256'],
                 source_causal_feature_sha256=feat['matrix_sha256'],eligible_rows=len(y),all_valid_supervised_rows=nvalid,
                 source_end_or_gap_censored=int((~complete).sum()),class_order=CLASS,class_counts=classcount.tolist(),
                 label_definition='ADVERSE30 / SURVIVE30_NOT_FAVORABLE15 / SURVIVE30_AND_FAVORABLE15',
                 training_subsample_is_complete=False,train_rows_actual=len(trainidx),all_source_month_rows_scored=len(y),
                 stratified_training_full_month_time_span=True,in_sample_train_and_score_month=mon,
                 full_month_feature_causal_past_only=True,
                 classifier_weights={'BAD':1,'NEUTRAL':1,'SURVIVE30_FAV15':1.5},
                 strict_calibrated_probabilities=False,model_trees=model.current_iteration(),hyperparameters=params,
                 code_file_sha256=digest(__file__),
                 model_sha256=digest(path),model_file=path.name,full_month_pgood_sha256=digest(outfile),full_month_pgood_file=outfile.name,
                 in_sample_nll=sumnll/nvalid,confusion_true_rows_predicted_columns=confusion.tolist(),
                 runtime_seconds=time.monotonic()-st,
                 status='TRAIN_400K_SYSTEMATIC_MONTH_SAMPLE_SCORE_100PCT_SOURCE_MONTH_IN_SAMPLE_ONLY_NOT_OOS_NOT_DEPLOYABLE')
    recpath=ROOT/'models'/f'R11S2_{mon}_{side}_COMPLETE_FIT_RECEIPT.json';recpath.write_text(json.dumps(receipt,indent=2))
    print('TRAIN DONE',mon,side,'nll',round(receipt['in_sample_nll'],5),'model',receipt['model_sha256'],'s',round(receipt['runtime_seconds'],2),flush=True)
    return receipt

def evaluate(mon):
    st=time.monotonic();ROOT.joinpath('replay').mkdir(exist_ok=True,parents=True)
    # Read-only replay uses the two already-frozen score arrays, never the 1.1GB
    # graph matrix. Label SHA and both saved model/score SHA stay mandatory.
    # Training-stage source/graph SHA was separately checked before fitting.
    zfile=LAB/f'month_{mon}'/f'R11S_{mon}_ALL_V5_CANDIDATE_H15_H30_EXACT_SURVIVAL_LABELS.npz'
    manifest=json.loads((LAB/f'month_{mon}'/f'R11S_{mon}_FULL_SOURCE_LABEL_MANIFEST.json').read_text())
    feat=json.loads((GRAPH/f'R11_CAUSAL_GRAPH_V5_{mon}_RECEIPT.json').read_text())
    if digest(zfile)!=manifest['full_population_sha256'] or feat['source_raw_sha256']!=SOURCE_SHA[mon]:
        raise ValueError('replay original label SHA or feature source manifest mismatch')
    b,covered,t,ix=labels(zfile,'BUY');s,covered2,t2,ix2=labels(zfile,'SELL')
    if not np.array_equal(covered,covered2) or not np.array_equal(t,t2) or not np.array_equal(ix,ix2):raise ValueError('side join')
    scores=[];rs=[]
    for side in ('BUY','SELL'):
        rec=json.loads((ROOT/'models'/f'R11S2_{mon}_{side}_COMPLETE_FIT_RECEIPT.json').read_text())
        model=ROOT/'models'/rec['model_file'];pfile=ROOT/'models'/rec['full_month_pgood_file']
        if rec['model_sha256']!=digest(model) or rec['full_month_pgood_sha256']!=digest(pfile):raise ValueError('model or fullscore drift')
        if rec['exact_full_label_sha256']!=manifest['full_population_sha256'] or rec['source_causal_feature_sha256']!=feat['matrix_sha256']:raise ValueError('feature-label receipt mismatch')
        scores.append(np.load(pfile,mmap_mode='r'));rs.append(rec)
    pb,ps=scores
    if len(pb)!=len(t) or len(ps)!=len(t):raise ValueError('scored month rows mismatch')
    print('REPLAY INPUTS HASH-VERIFIED',mon,len(t),flush=True)
    mx=np.maximum(pb,ps)
    active=np.unique(t//86400000)
    report={'month':mon,'full_250ms_source_rows':len(t),'raw_sha256':SOURCE_SHA[mon],'original_full_pop_label_sha256':manifest['full_population_sha256'],
        'causal_graph_sha256':feat['matrix_sha256'],'models':{rec['side']:dict(model_sha256=rec['model_sha256'],score_sha256=rec['full_month_pgood_sha256'],trees=rec['model_trees'],in_sample_nll=rec['in_sample_nll']) for rec in rs},
        'model_prob_is_calibrated':False,'policies':{},'full_month_scored_fraction':1.0,
        'in_sample_selection_thresholds_derived_from_scored_same_month':True,
        'scientific_status':'CAUSAL_ASOF_FEATURE_IN_SAMPLE_RANKING_DIAGNOSTIC_NOT_FORESIGHT'}
    for f in FRACTIONS:
        cut=float(np.quantile(mx,1.-f)) if f<1 else float(np.nextafter(mx.min(),-np.inf))
        rows,side,w,n,bad,censored=_replay_30sec(t,pb,ps,b,s,covered,cut)
        if len(rows)>1 and not np.all(np.diff(t[rows])>30000):raise ValueError('overlapping fixed 30s positions')
        times=pd.to_datetime(t[rows],unit='ms',utc=True)
        daily=times.strftime('%Y-%m-%d')
        weekly=times.strftime('%G-W%V')
        day_counts={d:0 for d in pd.to_datetime(active*86400000,unit='ms',utc=True).strftime('%Y-%m-%d')}
        week_counts={d:0 for d in pd.to_datetime(active*86400000,unit='ms',utc=True).strftime('%G-W%V')}
        for k,v in pd.Series(daily).value_counts().items():day_counts[k]=int(v)
        for k,v in pd.Series(weekly).value_counts().items():week_counts[k]=int(v)
        selected_class=np.where(side==0,b[rows],s[rows])
        observed=covered[rows]
        detailed=[]
        for tday in sorted(day_counts):
            sel=np.asarray(daily)==tday
            nsel=int(sel.sum());validsel=sel&observed
            win_i=int(((selected_class==2)&validsel).sum());bad_i=int(((selected_class==0)&validsel).sum());neu_i=int(((selected_class==1)&validsel).sum());cens_i=int((sel&~observed).sum())
            detailed.append(dict(utc_day=tday,source_active=True,entries=nsel,goal_15fav_30survive=win_i,adverse30=bad_i,neutral30=neu_i,censored=cens_i,goal_on_scored=win_i/(win_i+bad_i+neu_i) if win_i+bad_i+neu_i else None))
        detailed_weeks=[]
        for ww in sorted(week_counts):
            sel=np.asarray(weekly)==ww;nsel=int(sel.sum());validsel=sel&observed
            win_i=int(((selected_class==2)&validsel).sum());bad_i=int(((selected_class==0)&validsel).sum());neu_i=int(((selected_class==1)&validsel).sum());cens_i=int((sel&~observed).sum())
            detailed_weeks.append(dict(iso_week=ww,source_active=True,entries=nsel,goal_15fav_30survive=win_i,adverse30=bad_i,neutral30=neu_i,censored=cens_i,goal_on_scored=win_i/(win_i+bad_i+neu_i) if win_i+bad_i+neu_i else None))
        trace=ROOT/'replay'/f'R11S2_{mon}_FITMONTH_FRACTION{str(f).replace(".","p")}_30SEC_TRACE.npz'
        np.savez_compressed(trace,entry_tick_ordinal=ix[rows],entry_utc_ms=t[rows],BUY_side=(side==0),
            hindsight_class=np.where(side==0,b[rows],s[rows]),source_censor=~covered[rows],training_only_candidate_score=mx[rows])
        rec={'fraction':f,'month_score_threshold':cut,'candidate_signals':int((mx>=cut).sum()) if f<1 else len(t),'selected_nonoverlap_30s':len(rows),
            'survive30_and_favorable15':w,'survive30_without_favorable15':n,'adverse30':bad,
            'censored_unscored':censored,'strict_goal_rate_on_completed':(w/(w+n+bad)) if w+n+bad else None,
            'synth_85pct_floor':math.ceil(.85*SYNTH[mon]),'synth_85pct_volume_pass':len(rows)>=math.ceil(.85*SYNTH[mon]),
            'zero_active_source_days':sum(v==0 for v in day_counts.values()),'zero_active_source_iso_weeks':sum(v==0 for v in week_counts.values()),
            'per_active_day_all':detailed,'per_iso_week_all':detailed_weeks,
            'active_days_below_80pct_goal':sum(d['goal_on_scored'] is not None and d['goal_on_scored']<.8 for d in detailed),
            'active_weeks_below_80pct_goal':sum(d['goal_on_scored'] is not None and d['goal_on_scored']<.8 for d in detailed_weeks),
            'trace_file':trace.name,'trace_sha256':digest(trace)}
        report['policies'][str(f)]=rec
        print('RANK REPLAY',mon,f,'trades',len(rows),'strict15+30',round(rec['strict_goal_rate_on_completed'] or 0,4),'85%quota',rec['synth_85pct_volume_pass'],flush=True)
    report['runtime_seconds']=round(time.monotonic()-st,2)
    path=ROOT/'replay'/f'R11S2_{mon}_FULLSOURCE_IN_SAMPLE_15S30S_RANKING_RECEIPT.json';path.write_text(json.dumps(report,indent=2))
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--month',required=True,choices=list(SOURCE_SHA));p.add_argument('--action',choices=('BUY','SELL','evaluate'),required=True);p.add_argument('--trees',type=int,default=24);p.add_argument('--train-rows',type=int,default=400000);a=p.parse_args()
    if a.action=='evaluate':result=evaluate(a.month)
    else:result=fit(a.month,a.action,a.trees,a.train_rows)
    print('H1V2_R11S2_COMPLETE',a.month,a.action,result.get('status',result.get('scientific_status')))
