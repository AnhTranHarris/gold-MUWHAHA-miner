"""R25 bounded source exact, one-UTC-day each-feed experimental run.

No month or day trading performance claim. The first 12h train with 60s
embargo, and the final 12h are independently CHRONOLOGICALLY evaluated only;
all four original months historical and fully exposed, so not blind OOS.
R9 reference is post-action report only. No broker order fills or news model.
"""
from __future__ import annotations
import argparse,csv,json,hashlib,sys,time,dataclasses
from pathlib import Path
import numpy as np
import lightgbm as lgb
from r25_broker_adaptive import (
 ROOT,SOURCES,MONTHS,LANES,STOP,TARGET,TIMEOUT,CENSORED,UNFILLED,
 day_window,verify_gzip,asof_features,quote_geometry,offline_labels,
 action_features,one_position_replay,hourly_quarter_report,hindsight_cardinality)

HERE=ROOT/'h1v2_r25';ART=HERE/'artifacts';ART.mkdir(parents=True,exist_ok=True)
DAYS={'01':6,'02':10,'06':9,'07':9}
POLICIES=(('C0_VOLUME_FIRST',-1.0e20,-1.0),('C1_EV_GE_ZERO',0.0,-1.0),
          ('C2_EV_GE_75RAW',75.0,-1.0),('C3_EV_AND_PTP_GE_080',0.0,0.8),
          ('C4_VOLUME_SOFT_300RAW',-300.0,-1.0))

def sha(path):
 with open(path,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def export_csv(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',newline='',encoding='utf-8') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def small_indices(y,nmax=5000):
 n=len(y)
 if n<=nmax:return np.arange(n,dtype=np.int64)
 rng=np.random.default_rng(20261104)
 edges=np.linspace(0,n,nmax+1,dtype=np.int64)
 return np.asarray([rng.integers(edges[j],edges[j+1]) for j in range(nmax)],np.int64)

def report_stats(q,h,cutoff):
 Q=[x for x in q if x['utc_quarter_ms']>=cutoff and x['r9_synth_reference']>0]
 H=[x for x in h if x['utc_hour_ms']>=cutoff and x['r9_synth_reference']>0]
 return {'source_active_quarters_heldout':len(Q),'source_active_hours_heldout':len(H),
         'source_R9_reference_quarters_heldout':sum(x['r9_synth_reference'] for x in Q),
         'source_R9_reference_hours_heldout':sum(x['r9_synth_reference'] for x in H),
         'filled':sum(x['filled'] for x in Q),
         'tp':sum(x['tp_first'] for x in Q),'stopped_or_timed':sum(x['stopped_or_timed'] for x in Q),
         'censored':sum(x['censored'] for x in Q),'quarter_volume_pass':sum(x['volume_pass'] for x in Q),
         'quarter_joint_80_and_volume':sum(x['joint_80_and_volume'] for x in Q),
         'hour_volume_pass':sum(x['volume_pass'] for x in H),
         'hour_joint_80_and_volume':sum(x['joint_80_and_volume'] for x in H),
         'known_net_source_price_raw':round(sum(x['known_net_source_price_raw'] for x in Q),4),
         'accuracy_known_tp_vs_completed':(sum(x['tp_first'] for x in Q)/max(1,sum(x['tp_first']+x['stopped_or_timed'] for x in Q)))}

def source_day(source,mon,day=None):
 if day is None:day=DAYS[mon]
 begin=time.monotonic();pins=json.loads((ART/'raw_source_sha256.json').read_text());source_cert=verify_gzip(source,mon,pins)
 w=day_window(source,mon,day,decision_ms=1000,spread_cap=6000)
 s=w.signals
 if len(s)<100:raise RuntimeError('INSUFFICIENT_REAL_SOURCE_SIGNALS_TO_TRAIN '+source+mon)
 daystart=int(w.ref_utc_ms[0]);cutoff=daystart+12*3600000
 train=np.flatnonzero((w.t[s]<cutoff-61000));test=np.flatnonzero(w.t[s]>=cutoff)
 if len(train)<100 or len(test)<100:raise RuntimeError('INSUFFICIENT_TEMPORAL_TRAIN_TEST_SPLIT')
 x=asof_features(w);tp,st=quote_geometry(w,x)
 lab=offline_labels(w,tp,st)
 code=lab['cause'].reshape(len(s),6)
 rows=small_indices(train,5000);chosen_train=train[rows]
 X_all=action_features(x,tp,st,source)
 X_train=X_all.reshape(len(s),6,-1)[chosen_train].reshape(-1,X_all.shape[1])
 Y_train=code[chosen_train].reshape(-1)
 known=(Y_train<=TIMEOUT)
 if len(np.unique(Y_train[known]))<2:raise RuntimeError('NO_CLASS_VARIATION_TRAIN')
 model=lgb.LGBMClassifier(objective='multiclass',num_class=3,n_estimators=40,num_leaves=19,
                          learning_rate=.08,min_child_samples=90,max_bin=127,reg_lambda=6.0,
                          n_jobs=2,verbosity=-1,random_state=20261104)
 model.fit(X_train[known],Y_train[known]);train_seconds=time.monotonic()-begin
 xt=X_all.reshape(len(s),6,-1)[test].reshape(-1,X_all.shape[1])
 p=model.predict_proba(xt).reshape(len(test),6,-1)
 prob=np.zeros((len(test),6,3),np.float64)
 for j,cl in enumerate(model.classes_):prob[:,:,int(cl)]=p[:,:,j]
 spread=w.a[s[test]].astype(np.int64)-w.b[s[test]].astype(np.int64)
 ttp=np.tile(tp[test],(1,2)).astype(np.float64)
 sstop=np.tile(st[test],(1,2)).astype(np.float64)
 fee=20.0
 risk=spread[:,None]+sstop+fee
 exp_net=prob[:,:,TARGET]*ttp-prob[:,:,STOP]*risk-prob[:,:,TIMEOUT]*(spread[:,None]+fee)
 best=np.argmax(exp_net,axis=1);maxev=exp_net[np.arange(len(test)),best]
 pt=prob[np.arange(len(test)),best,TARGET]
 files=[];results=[]
 for name,floor,pfloor in POLICIES:
  acts=np.full((len(s),2),-1.,np.float64)
  acts[test,0]=np.where((maxev>=floor)&(pt>=pfloor),best,-1)
  acts[test,1]=maxev
  trades,receipt=one_position_replay(w,lab,acts)
  q,h=hourly_quarter_report(w,trades)
  qcsv=ART/f'R25_{source}_{mon}_{day:02d}_{name}_ALL96_QUARTERS.csv';hcsv=ART/f'R25_{source}_{mon}_{day:02d}_{name}_ALL24_HOURS.csv'
  tcsv=ART/f'R25_{source}_{mon}_{day:02d}_{name}_ALL_SELECTED_SOURCE_TRADE_ORDINALS.csv'
  export_csv(qcsv,q);export_csv(hcsv,h)
  if trades:
   keys=sorted(set(k for r in trades for k in r))
   export_csv(tcsv,[{k:r.get(k) for k in keys} for r in trades])
  files.extend([qcsv,hcsv]+([tcsv] if trades else []))
  results.append({'policy':name,**receipt,**report_stats(q,h,cutoff),
                  'heldout_test_signals':len(test),'train_signals':len(train),
                  'fitted_supervised_rows':int(known.sum()),'policy_exante_uses_R9_quota':False})
 # Ex-post perfect future knowledge, only original actual Bid/Ask winning intervals
 # on the last twelve hours. It cannot be conflated with causal predictions.
 wtest=dataclasses.replace(w,signals=w.signals[test]);ltest={k:v[test] for k,v in lab.items()}
 oracle=hindsight_cardinality(wtest,ltest)
 wins=[]
 for row in oracle:
  i,side,lane,f,e=map(int,row)
  wins.append({'fill_utc_ms':int(w.t[f]),'status':TARGET,
               'net_source_price_raw':float(ltest['net'][i,side,lane]),
               'source_signal_ordinal':int(w.ordinal_origin+wtest.signals[i]),
               'fill_source_ordinal':int(w.ordinal_origin+f),
               'exit_source_ordinal':int(w.ordinal_origin+e),
               'exit_utc_ms':int(w.t[e]),'side':side,'lane':lane})
 q,h=hourly_quarter_report(wtest,wins)
 oq=ART/f'R25_{source}_{mon}_{day:02d}_EXPOST_ALL96_QUARTERS.csv';oh=ART/f'R25_{source}_{mon}_{day:02d}_EXPOST_ALL24_HOURS.csv'
 export_csv(oq,q);export_csv(oh,h);files.extend([oq,oh]);results.append({'policy':'EXPOST_FUTURE_KNOWN_WINNER_CEILING_NOT_CAUSAL',**report_stats(q,h,cutoff),'future_uses_labels':True,'globally_nonoverlapping':True,'source_winning_intervals':len(oracle)})
 save=ART/f'R25_{source}_{mon}_{day:02d}_ALL6_POLICY_VS_EXPOST_RECEIPT.json'
 receipt={'source':source,'month':'2026-'+mon,'day':day,'utc_12_hour_test_start_ms':cutoff,
          'raw_source_sha':source_cert,'original_window_ordinal_origin':w.ordinal_origin,
          'total_source_quote_rows_in_window':len(w.t),'asof_source_signal_rows_for_day':len(s),
          'first_and_last_signal_source_ordinal':[int(w.ordinal_origin+s[0]),int(w.ordinal_origin+s[-1])],
          'train_candidate_count':len(train),'heldout_source_signal_count':len(test),
          'train_excluded_before_test_ms':61000,'source_fill_lag_ms':100,'fill_staleness_ms':1000,
          'spread_cap_raw':6000,'train_seconds_including_load_label':round(train_seconds,3),
          'end_to_end_elapsed_seconds':round(time.monotonic()-begin,3),
          'source_calendar_day_original_R9_reference':int(w.refq.sum()),
          'source_reference_is_action_input':False,'source_broker_actual_dealer_fill':False,
          'month_full_backtest_complete':False,'all_source_fourmonth_score_complete':False,
          'source_data_historical_in_sample':True,'chronological_pilot_heldout_not_blind_oos':True,
          'original_R9_MT5_EA_UNMODIFIED':True,'new_policy_deployable':False,
          'model_features':X_all.shape[1], 'trained_model_classes':[int(z) for z in model.classes_],
          'results':results,
          'output_files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files}}
 save.write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n',encoding='utf8')
 print(json.dumps({'source':source,'month':mon,'day':day,'signals':len(s),'train':len(train),'test':len(test),'results':results,'elapsed_s':receipt['end_to_end_elapsed_seconds']},allow_nan=False),flush=True)
 return receipt

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source',required=True,choices=SOURCES);ap.add_argument('--month',required=True,choices=MONTHS);ap.add_argument('--day',type=int,default=None)
 args=ap.parse_args();source_day(args.source,args.month,args.day)
