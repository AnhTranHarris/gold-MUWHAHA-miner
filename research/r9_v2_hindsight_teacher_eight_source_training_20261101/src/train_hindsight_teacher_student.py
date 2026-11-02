#!/usr/bin/env python3
"""Chronological real-tick teacher/student research with no runtime hindsight columns.

Consumes ALL eight full-month as-of quote feature datasets. Full source-month
processing is never sampled. Train<=date, calibrate later, evaluate later still;
then refit the final research student on all eight months (not OOS). Outputs
per-day/week/month selected-positive fractions and SYNTH count comparisons.

NOTE: applying a selective filter to an existing realized stream is an OFFLINE
candidate-decision backtest, not a fresh position-aware tick replay. Skipped
trades open opportunities that are absent from the original stream. This must
not be represented as actual recomputed EA trades.
"""
from __future__ import annotations
import json,zipfile,csv,io,math,hashlib,time
from pathlib import Path
import pandas as pd,numpy as np,lightgbm as lgb
ROOT=Path('/mnt/data/r9_v2_eight_source_training_20261101')
SRC=Path('/mnt/data/R9_V2_HIGH_VOLUME_EVENT_STREAM_REPAIR_FULL_RECOVERY_20261101.zip')
MON=('01','02','06','07');BROKERS=('coinexx','dukascopy');SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}
DATES={'01':('2026-01-12','2026-01-19'),'02':('2026-02-11','2026-02-18'),'06':('2026-06-10','2026-06-17'),'07':('2026-07-10','2026-07-17')}
BASE_COLS=['spread','evidence','side','lane_code','utc_hour','utc_weekday','ready_900000','ready_3600000','ready_14400000']
FEATURES=None

def read_teacher():
 with zipfile.ZipFile(SRC) as z:
  with z.open('original_teacher/synth_teacher_minutes.csv') as f:
   t=pd.read_csv(f)
 t=t[t.positive>0].copy()
 t['minute_ts']=pd.to_datetime(t.native_minute,format='%Y.%m.%d %H:%M',utc=True).astype('int64')//10**6
 t['side']=t.side.astype(np.int8)
 return set(zip(t.minute_ts.to_numpy(np.int64),t.side.to_numpy(np.int8)))

def load(src,month,teacher=None):
 path=ROOT/'checkpoints'/f'{src}_{month}_tick_asof.pkl.gz'
 df=pd.read_pickle(path,compression='gzip')
 # Month data are UTC; teacher R9 SYNTH minutes are Coinexx server-native.
 # This is only used as weight metadata during supervised training.
 offset=(120 if month in ('01','02') else 180)*60000
 tm=((df.entry_ms.to_numpy(np.int64)+offset)//60000)*60000
 if teacher is not None:
  df['offline_teacher_marker']=np.fromiter(((int(t),int(s)) in teacher for t,s in zip(tm,df.side.to_numpy(np.int8))),dtype=np.uint8,count=len(df))
 # Never expose timestamps that determine target month/day as runtime features.
 df['broker_id']=int(src=='dukascopy')
 return df

def feature_names(df):
 return BASE_COLS+['broker_id']+[c for c in df.columns if c.startswith(('mid_displacement_','spread_mean_','bid_displacement_','ask_displacement_','revision_imbalance_','spread_compress_','realized_vol_','tick_rate_'))]

def numpy_x(df,columns):
 return df[columns].to_numpy(dtype=np.float32,copy=True)

def metrics(df,selected,probs,scope):
 sel=df.loc[selected];N=len(df);n=len(sel)
 day=sel.groupby('day',sort=True).agg(n=('net','size'),wins=('label_30s_win','sum'),net=('net','sum'))
 week=sel.groupby('week',sort=True).agg(n=('net','size'),wins=('label_30s_win','sum'),net=('net','sum'))
 all_days=sorted(df.day.unique());all_weeks=sorted(df.week.unique())
 checks={'day':{},'week':{}}
 for period,ls,agg in [('day',all_days,day),('week',all_weeks,week)]:
  for key in ls:
   if key in agg.index:
    v=agg.loc[key];cnt=int(v['n']);wins=int(v['wins']);net=float(v['net'])
   else:cnt=wins=0;net=0.
   checks[period][str(key)]={'trades':cnt,'30s_win_rate':round(wins/cnt,5) if cnt else None,'net':round(net,2),'80pct_pass':bool(cnt>0 and wins/cnt>=.8)}
 gross=float(sel.net.clip(lower=0).sum());loss=float(-sel.net.clip(upper=0).sum())
 return {'scope':scope,'full_candidate_count':N,'selected_count':n,'selected_rate':round(n/N,5) if N else 0.,
         '30s_win_count':int(sel.label_30s_win.sum()),'30s_win_rate':round(float(sel.label_30s_win.mean()),5) if n else None,
         'profit_net':round(float(sel.net.sum()),2),'profit_factor':round(gross/loss,5) if loss else None,
         'late_close_selected':int((sel.duration_ms>30000).sum()),'neutral_selected':int(sel.label_30s_neutral.sum()),
         '80pct_month_pass':bool(n>0 and sel.label_30s_win.mean()>=.8),
         'daily_passes':sum(v['80pct_pass'] for v in checks['day'].values()),'daily_total':len(checks['day']),
         'weekly_passes':sum(v['80pct_pass'] for v in checks['week'].values()),'weekly_total':len(checks['week']),
         'periods':checks}

def fit(train,columns):
 x=numpy_x(train,columns);y=train.label_30s_win.to_numpy(np.uint8)
 weights=np.ones(len(train),dtype=np.float32)
 # SYNTH R9 as a WEAK 5% teacher of verified positive real paths ONLY.
 weights[(y==1)&(train.offline_teacher_marker.to_numpy()==1)]=1.05
 model=lgb.LGBMClassifier(n_estimators=105,max_depth=7,num_leaves=27,learning_rate=.055,
    min_child_samples=180,subsample=.8,colsample_bytree=.82,reg_lambda=10.,n_jobs=4,
    verbosity=-1,random_state=20261101,deterministic=True,force_col_wise=True)
 model.fit(x,y,sample_weight=weights,feature_name=columns)
 return model

def calibrate(cal,model,cols):
 # Candidate thresholds chosen on *past calibration* only. No test-period tuning.
 p=model.predict_proba(numpy_x(cal,cols))[:,1]
 bad=p[cal.label_30s_win.to_numpy()==0]
 quantiles=[.70,.8,.9,.95,.98,.995]
 variants=[]
 for alpha in quantiles:
  threshold=float(np.quantile(bad,alpha)) if len(bad)>100 else 1.0
  accepted=(p>threshold)
  # Selective utility objective includes NP false positive rate and profit
  w=cal.loc[accepted]
  positive=int(w.label_30s_win.sum())
  win=positive/len(w) if len(w) else 0.
  net=float(w.net.sum())
  variants.append({'bad_rejection_quantile':alpha,'threshold':threshold,'count':len(w),
                   'winrate':win,'net':net,'meets_80pct':bool(win>=.8)})
 # Conservative: prefer configurations with 80% + positive net, then most
 # count; if none, choose with best utility rather than faking a passing model.
 eligible=[x for x in variants if x['meets_80pct'] and x['net']>0]
 if eligible: chosen=max(eligible,key=lambda x:x['count'])
 else: chosen=max(variants,key=lambda x:(x['net'],x['winrate']))
 return chosen,variants

def run():
 stamp=time.monotonic();out=ROOT/'results';out.mkdir(exist_ok=True)
 teacher=read_teacher(); print('teacher marked minutes',len(teacher),flush=True)
 all_previous=[];results={};models=[]
 for month in MON:
  month_dfs=[load(source,month,teacher) for source in BROKERS]
  current=pd.concat(month_dfs,ignore_index=True)
  cols=feature_names(current)
  a,b=DATES[month]
  fit_current=current[current.day<=a]
  calibration=current[(current.day>a)&(current.day<=b)]
  check=current[current.day>b]
  train=pd.concat(all_previous+[fit_current],ignore_index=True)
  print('START',month,'train',len(train),'cal',len(calibration),'check',len(check),flush=True)
  model=fit(train,cols)
  chosen,variants=calibrate(calibration,model,cols)
  test_probs=model.predict_proba(numpy_x(check,cols))[:,1]
  score_mask=(test_probs>chosen['threshold'])
  month_rec={'fit_days':sorted(train.day.unique())[-30:],'calibration_dates':(a,b),'eval_min_date':str(check.day.min()),
    'fit_count':len(train),'calibration_count':len(calibration),'test_count':len(check),
    'np_selection':chosen,'np_calibration_variants':variants,'per_source':{}}
  for source in BROKERS:
   sub=check[check.source==source];selected=score_mask[check.source.to_numpy()==source];pp=test_probs[check.source.to_numpy()==source]
   month_rec['per_source'][source]=metrics(sub,selected,pp,f'{source}_{month}_CHRONOLOGICAL_CHECK')
   print('SCORE',source,month,'selected',int(selected.sum()),'winpct',month_rec['per_source'][source]['30s_win_rate'],'net',month_rec['per_source'][source]['profit_net'],'daily',month_rec['per_source'][source]['daily_passes'],'/',month_rec['per_source'][source]['daily_total'],flush=True)
  model.booster_.save_model(str(ROOT/'checkpoints'/f'chrono_model_{month}.txt'))
  (ROOT/'checkpoints'/f'chrono_model_{month}_feature_names.json').write_text(json.dumps(cols,indent=2))
  results[month]=month_rec
  (out/f'walkforward_{month}.json').write_text(json.dumps(month_rec,indent=2))
  all_previous.append(current)
 del current,train,calibration,check,all_previous
 (out/'walkforward_all.json').write_text(json.dumps(results,indent=2))
 print('CHRONO DONE',round(time.monotonic()-stamp,1),flush=True)
 return results
if __name__=='__main__':run()
