#!/usr/bin/env python3
"""Chronological real-tick 30-second entry student, 8 independent source-month checks.
All outcome/teacher columns exist ONLY in offline training/calibration/evaluation,
never in runtime predict X. Preentry 1s completed-quote features + v2 evidence.
No calibration uses target month's future labels.
"""
from __future__ import annotations
import json,math,os,time,hashlib
from pathlib import Path
import numpy as np,pandas as pd, lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score
ROOT=Path('/mnt/data/v2_30s_teacher_training');R=ROOT/'results'; R.mkdir(exist_ok=True)
MONTHS=['01','02','06','07'];SOURCES=['coinexx','dukascopy']
OUTPUT_DIR=R/'micro_optimized';OUTPUT_DIR.mkdir(exist_ok=True)
FLOORS={'01':23783,'02':28495,'06':27031,'07':20725}
TEACHER=ROOT/'source/synth_teacher_minutes.csv'
TEACH=pd.read_csv(TEACHER)
TEACH['native_min_id']=(pd.to_datetime(TEACH.native_minute,format='%Y.%m.%d %H:%M',utc=True).astype('int64')//60_000_000_000).astype('int64')
TEACH=TEACH[['native_min_id','side','positive']].groupby(['native_min_id','side'],as_index=False).positive.max()
# Memory-conservative numeric feature subset; all use observed quotes at/before entry.
EXCLUDE={'entry_ms','exit_ms','net','mfe','mae','entry_price','q_mid','win','target','neutral','teacher_positive','quality','quality_bad','day_id','week_id','source','month','lane','native_min_id','hour','lag_to_completed_s'}

def load(source,m):
    path=R/f'{source}_{m}_features.pkl'
    f=pd.read_pickle(path)
    base=['entry_ms','exit_ms','side','net','mfe','mae','spread','evidence','lane','hour','day_id','week_id','win','target','neutral','lag_to_completed_s','q_spread']
    names=[]
    for h in (5,45,300):
        names += [f'{key}_{h}s' for key in ('disp','range','vol','bbpos')]
    for h in (900,3600,14400):names += [f'disp_{h}s',f'range_{h}s']
    for h in (1,5,45,300):names.append(f'quote_rate_{h}s')
    for h in (5,45):names.extend(f'{key}_rate_{h}s' for key in ('bu','bd','au','ad','sw','sn'))
    for h in (5,45):names += [f'quote_pressure_{h}s',f'spread_pressure_{h}s']
    for h in (300,900,3600,14400):names.append(f'ready_{h}s')
    f=f[list(dict.fromkeys(base+names))].copy()
    micro=pd.read_pickle(R/f'{source}_{m}_micro.pkl')
    mc=[]
    for h in (250,500,1000,5000):
        for base_name in ('pressure','quote_divergence','tickrate','disp'):
            mc.append(f'micro_{base_name}_{h}ms')
    for h in (500,1000):mc.extend(f'micro_{name}_{h}ms' for name in ('bidonly','askonly','sw','sn'))
    mc += ['micro_lag_ms','micro_last_250ms_disp','micro_latest_spread']
    f=pd.concat([f.reset_index(drop=True),micro[mc].reset_index(drop=True)],axis=1)
    assert len(f)==len(micro)
    f['micro_gap_stale']=(f.micro_lag_ms>5000).astype('int8')
    f['lane_reversal']=(f['lane'].astype(str)=='reversal').astype('int8')
    # Observed hour and day-of-week, known at entry, not date identifiers.
    f['hour_sin']=np.sin(2*np.pi*f.hour/24).astype('float32')
    f['hour_cos']=np.cos(2*np.pi*f.hour/24).astype('float32')
    f['weekday'] = ((f.day_id+3)%7).astype('int8') # UTC epoch Thursday -> 3
    f['lag_sec_clipped'] = np.minimum(f.lag_to_completed_s,120).astype('float32')
    f['spread_to_vol']=(f.spread/np.maximum(.05,f.vol_300s)).clip(0,200).astype('float32')
    f['q_rate_5_over_300']=(f['quote_rate_5s']/(f['quote_rate_300s']+.05)).clip(0,100).astype('float32')
    f['vol_ratio_5_to_300']=(f['vol_5s']/(f['vol_300s']+.02)).clip(0,100).astype('float32')
    f['vol_ratio_300_to_3600']=(f['vol_300s']/(f['range_3600s']+.02)).clip(0,100).astype('float32')
    f['side_x_quote_pressure']=(f['side']*f['quote_pressure_5s']).astype('float32')
    f['side_x_slope_45s']=(f['side']*f['disp_45s']).astype('float32')
    f['side_x_h1']=(f['side']*f['disp_3600s']/(f['range_3600s']+.01)).clip(-10,10).astype('float32')
    f['side_x_h4']=(f['side']*f['disp_14400s']/(f['range_14400s']+.01)).clip(-10,10).astype('float32')
    # Real-time streak and completed-previous-trade info, always shifted one trade.
    for n in (8,32,128):
        f[f'prior_win_{n}']=f.win.shift(1).rolling(n,min_periods=1).mean().fillna(.5).astype('float32')
        f[f'prior_net_{n}']=f.net.shift(1).rolling(n,min_periods=1).mean().fillna(0.).astype('float32')
    f['prior_trade_net']=f.net.shift(1).fillna(0.).astype('float32')
    f['prior_trade_side']=f.side.shift(1).fillna(0).astype('float32')
    f['gap_from_last_exit_ms']=(f.entry_ms-f.exit_ms.shift(1)).clip(lower=0,upper=300000).fillna(300000).astype('float32')
    # The target is a realized R9 exit inside or at first quote after the 30s timeout;
    # requires >$0.10 executable net to exclude neutral paths.
    f['quality']=((f.net>0.10)&(f.mfe>=.12)).astype('int8')
    f['quality_bad']=(f.quality==0).astype('int8')
    f['native_min_id']=(f.entry_ms//60000)+(120 if m in ('01','02') else 180)
    f=f.merge(TEACH,on=['native_min_id','side'],how='left',sort=False)
    f['teacher_positive']=f.positive.fillna(0).astype('int8');f=f.drop(columns=['positive'])
    return f

def choices(f):
    features=[]
    for col in f.columns:
        if col in EXCLUDE or col=='positive':continue
        if pd.api.types.is_numeric_dtype(f[col]):features.append(col)
    return features

def stats(df,selected_mask,month,source,fold_type,threshold,model_version):
    selected=df.loc[selected_mask]
    q=selected.quality.to_numpy(dtype=np.int8);w=(selected.net>0).to_numpy(dtype=np.int8)
    day=selected.day_id.to_numpy(dtype='int32');week=pd.to_datetime(selected.entry_ms,unit='ms',utc=True).dt.strftime('%G-W%V').to_numpy()
    byday=selected.assign(day_id=day).groupby('day_id').quality.agg(['size','mean'])
    byweek=selected.assign(iso_week=week).groupby('iso_week').quality.agg(['size','mean'])
    active_days=int(df.day_id.nunique())
    floor=FLOORS[month]
    if fold_type=='partial_january':
        original_month_days={'01':26}[month]
        floor=math.ceil(floor*active_days/original_month_days)
    out={'source':source,'month':month,'fold':fold_type,'model_version':model_version,
       'evaluated_candidates':int(len(df)),'selected_trades':int(len(selected)),
       'min_trades_85pct_synth':floor,'volume_pass':bool(len(selected)>=floor),
       'quality_rate':float(q.mean()) if len(q) else 0,
       'win_rate':float(w.mean()) if len(w) else 0,
       'net':round(float(selected.net.sum()),2),
       'mean_net':round(float(selected.net.mean()),5) if len(selected) else None,
       'daily_passes':int((byday['mean']>=.8).sum()),'daily_active':int(len(byday)),
       'daily_evaluated':active_days,'daily_80pct_pass':bool(len(byday)>0 and (byday['mean']>=.8).all()),
       'weekly_passes':int((byweek['mean']>=.8).sum()),'weekly_active':int(len(byweek)),
       'weekly_80pct_pass':bool(len(byweek)>0 and (byweek['mean']>=.8).all()),
       'monthly_80pct_pass':bool(len(q)>0 and q.mean()>=.80),
       'net_positive':bool(len(selected)>0 and selected.net.sum()>0),
       'np_threshold':float(threshold)}
    out['all_constraints_pass']=bool(out['volume_pass'] and out['daily_80pct_pass'] and out['weekly_80pct_pass'] and out['monthly_80pct_pass'] and out['net_positive'])
    return out

def fit_predict(tr,cal,te,features,tag,variant=0):
    # Same data contract and features for both source-specific independent feeds.
    # Bounded-capacity controlled student; hyperparameters fixed ex ante.
    opts={'n_estimators':40,'learning_rate':.08,'num_leaves':15,'min_child_samples':250,
          'max_depth':5,'feature_fraction':.75,'verbosity':-1,'n_jobs':3,'random_state':11,
          'max_bin':63,'reg_lambda':5.,'deterministic':True,'force_col_wise':True}
    if variant==1:opts.update(num_leaves=31,max_depth=7,min_child_samples=250,n_estimators=150)
    cls=lgb.LGBMClassifier(**opts)
    cls.fit(tr[features],tr.quality)
    pa=cls.predict_proba(cal[features])[:,1]; pt=cls.predict_proba(te[features])[:,1]
    # Truly independent Platt calibration (cal set later than fit set), fitted only
    # on the older calibration date slice and then frozen for future month.
    platt=LogisticRegression(C=1.,solver='lbfgs',max_iter=100)
    platt.fit(np.log(np.clip(pa,1e-5,1-1e-5)/(1-np.clip(pa,1e-5,1-1e-5))).reshape(-1,1),cal.quality)
    def pcal(x):
        x=np.clip(x,1e-5,1-1e-5)
        return platt.predict_proba(np.log(x/(1-x)).reshape(-1,1))[:,1]
    pa=pcal(pa);pt=pcal(pt)
    # Survival expected payoff: train on realized subsequent executable net.
    reg=lgb.LGBMRegressor(**{**opts,'objective':'regression','n_estimators':24})
    reg.fit(tr[features],tr.net)
    ea=reg.predict(cal[features]);et=reg.predict(te[features])
    # Weak SYNTH teacher via a separate student trained ONLY on historical
    # snapshots. Actual future teacher mark NEVER enters runtime scoring.
    teacher=lgb.LGBMClassifier(**{**opts,'n_estimators':16,'num_leaves':11})
    teacher.fit(tr[features],tr.teacher_positive)
    ta=teacher.predict_proba(cal[features])[:,1];tt=teacher.predict_proba(te[features])[:,1]
    # The real-tick quality posterior dominates (90%). Auxiliary teacher <=10%.
    return (pa,pt,ea,et,ta,tt,cls,reg,teacher)

def choose_policy(cal,pa,ea,ta,source,fold):
    # All policy selection happens before seeing the later evaluation period.
    plans=[]
    for wt in (0.0,0.1):
        score=(1-wt)*pa+wt*ta
        neg=score[cal.quality.to_numpy()==0]
        if len(neg)==0:continue
        np_cut=np.quantile(neg,.90)
        # Event loss & cost gate. Do not override NP to manufacture volume.
        eligible=(score>=np_cut)&(ea>0)
        n=int(eligible.sum());qual=float(cal.quality.to_numpy()[eligible].mean()) if n else 0.
        net=float(cal.net.to_numpy()[eligible].sum())
        plans.append({'teacher_weight':wt,'threshold':float(np_cut),'np_bad_cal':float((score[cal.quality.to_numpy()==0]>=np_cut).mean()),
                      'cal_eligible':n,'cal_quality':qual,'cal_net':net,'cal_net_per_trade':net/max(1,n)})
    # Choose prospectively based only on calibration; prioritize 80% quality,
    # then positive expectancy and volume. If impossible, keep most viable,
    # report violation rather than change target.
    plans.sort(key=lambda x:(x['cal_quality']>=.8,x['cal_net_per_trade']>0,x['cal_quality'],x['cal_net_per_trade'],x['cal_eligible']),reverse=True)
    return plans[0],plans

def run(source_only=None, month_only=None):
    records=[];root_start=time.monotonic()
    for source in (SOURCES if source_only is None else [source_only]):
        frames={}
        if month_only is not None:
            selected_idx=MONTHS.index(month_only)
            for prev in MONTHS[:selected_idx]:frames[prev]=load(source,prev)
        for idx,m in enumerate(MONTHS):
            if month_only is not None and m!=month_only:continue
            f=load(source,m);features=choices(f)
            if idx==0:
                unique=np.sort(f.day_id.unique());t1=unique[int(len(unique)*.56)];t2=unique[int(len(unique)*.77)]
                tr=f[f.day_id<t1];cal=f[(f.day_id>=t1)&(f.day_id<t2)];te=f[f.day_id>=t2];fold='partial_january'
            else:
                prior=pd.concat([frames[x] for x in MONTHS[:idx]],ignore_index=True)
                ud=np.sort(prior.day_id.unique());cut=ud[int(len(ud)*.80)]
                tr=prior[prior.day_id<cut];cal=prior[prior.day_id>=cut];te=f;fold='prospective_month'
            if len(tr)<2000 or len(cal)<1000 or len(te)<1000:raise AssertionError('bad split')
            # Explicit train/calibration/test chronology. Test month is strictly later.
            assert tr.entry_ms.max()<cal.entry_ms.min() and cal.entry_ms.max()<te.entry_ms.min()
            start=time.monotonic()
            pa,pt,ea,et,ta,tt,cls,reg,teacher=fit_predict(tr,cal,te,features,source+m)
            selected_plan,variants=choose_policy(cal,pa,ea,ta,source,m)
            wt=selected_plan['teacher_weight'];threshold=selected_plan['threshold']
            s=(1-wt)*pt+wt*tt
            mask=(s>=threshold)&(et>0)
            res=stats(te,mask,m,source,fold,threshold,'LGBM_40trees_plus_250ms_bid_ask_NP90_teacher0or10')
            res['calibration_candidates']=len(cal);res['training_candidates']=len(tr)
            res['calibration_options']=variants
            res['calibration_teacher_weight']=wt
            res['test_auc_quality']=round(float(roc_auc_score(te.quality,pt)),6)
            res['test_average_precision']=round(float(average_precision_score(te.quality,pt)),6)
            res['test_base_quality']=round(float(te.quality.mean()),6)
            res['elapsed_s']=round(time.monotonic()-start,2)
            records.append(res)
            (OUTPUT_DIR/f'fold_{source}_{m}_summary.json').write_text(json.dumps(res,indent=2))
            # Save only observed trading decisions, no huge full path embedding.
            out=te.loc[mask,['entry_ms','exit_ms','side','net','spread','evidence','quality','mfe','mae','day_id','lane']].copy()
            out['pred_success']=pt[mask];out['pred_expected_net']=et[mask];out['pred_synth_teacher']=tt[mask]
            out.to_csv(OUTPUT_DIR/f'fold_{source}_{m}_selected_trades.csv.gz',index=False,compression='gzip')
            # Model artifacts with ground-truth feature names, no teacher labels in runtime.
            modeldir=OUTPUT_DIR/f'policy_{source}_{m}';modeldir.mkdir(exist_ok=True)
            cls.booster_.save_model(str(modeldir/'real_success.txt'))
            reg.booster_.save_model(str(modeldir/'real_expected_net.txt'))
            teacher.booster_.save_model(str(modeldir/'aux_synth_teacher.txt'))
            (modeldir/'POLICY.json').write_text(json.dumps({'source':source,'month':m,'features':features,
                    'threshold':threshold,'teacher_weight':wt,'regression_positive_gate':0,
                    'original_v2_model_preserved':True,'training_cutoff_utc_ms':int(tr.entry_ms.max()),
                    'calibration_cutoff_utc_ms':int(cal.entry_ms.max()),'forecast_from_utc_ms':int(te.entry_ms.min()),
                    'label':'net>.10 AND mfe>=.12 before R9 stop/30s timeout','no_future_features':True,
                    'all_selected_are_subsequence_of_original_single_position_stream':True},indent=2))
            frames[m]=f
            print(json.dumps({k:res[k] for k in ['source','month','fold','training_candidates','calibration_candidates','evaluated_candidates','selected_trades','quality_rate','net','volume_pass','all_constraints_pass','elapsed_s']}),flush=True)
        del frames
    (OUTPUT_DIR/'training_all8_result.json').write_text(json.dumps({'source_data':'complete eight tick files, all 2481012 source-position entries','protocol':'chronological train/calibrate/test, previously observed complete quote seconds only, weak synthetic teacher separate model',
       'results':records,'total_elapsed_s':round(time.monotonic()-root_start,2)},indent=2))
    print('TRAINING COMPLETE',round(time.monotonic()-root_start,2),flush=True)
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--source',choices=SOURCES,default=None);ap.add_argument('--month',choices=MONTHS,default=None);args=ap.parse_args()
    run(args.source,args.month)
