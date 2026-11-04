"""R&D VNext C4: time-purged, source-conditioned competing-path + net-value WAIT.

Add-only. No source H1V2/R9 rewrite. No valid blind OOS: months exposed.
C3 full already-executed, causal-source-ordinal trade trace is the candidate
population, so C4 is a conservative SUBSET replay, NOT a rescheduling upper.
"""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
import numpy as np
import lightgbm as lgb
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss
from vnext import (BASE,load_month,prefix_features,policy,source_report,quota,
                   sha,SRC,MONTHS,QUARTER_MS)

BINS=(('M00_P55',.55,False),('M01_P65',.65,False),('M02_P75',.75,False),('M03_P55_NETPOS',.55,True))
TRAIN_END_DAY=9;CAL_START_DAY=11;CAL_END_DAY=19;TEST_START_DAY=21

def original_trace(source,mon):
 p=BASE/'h1v2_vnext'/'results'/source/mon/f'VNEXT_C3_{source}_{mon}_FULL_SOURCE_SELECTED_TRADE_ORDINALS.npz'
 if not p.exists():raise FileNotFoundError('ORIGINAL_C3_COMPLETE_SOURCE_MONTH_RECEIPT_MISSING '+str(p))
 with np.load(p,allow_pickle=False) as f:
  return np.column_stack([f['source_quote_signal_ordinal'],f['source_quote_fill_ordinal'],f['source_quote_exit_ordinal'],f['class_code'],f['side_buy0_sell1'],f['intended_horizon_ms'],f['source_realized_net_raw']]).astype(np.int64),sha(p)

def asof_matrix(t,b,a,source,trace):
 """Never read exit price, class label, future fill/exit ordinal into model X."""
 signal=trace[:,0].astype(np.int32)
 gap=np.flatnonzero(np.diff(t)>15000).astype(np.int32)+1
 epoch=np.r_[0,gap];e=epoch[np.searchsorted(epoch,signal,side='right')-1]
 features=prefix_features(t,b,a,signal,t[signal]-t[e])
 side,h,tp,stop,score=policy(features,source,3)
 # Decisional non-leak parity: original C3 trade side/h must reconstruct exactly
 # from original as-of quote-prefix features, not saved future labels.
 if np.any(side<0) or not np.array_equal(side.astype(np.int64),trace[:,4]) or not np.array_equal(h.astype(np.int64),trace[:,5]):
  raise AssertionError('PREVIOUS_CAUSAL_SIGNAL_POLICY_PARITY_DRIFT')
 spread=features[:,0]
 conditional=np.column_stack((features,
                            side.astype(np.float32),h.astype(np.float32)/1000,
                            tp.astype(np.float32),stop.astype(np.float32),
                            np.clip(score,0,100),
                            stop/(spread+100),tp/(spread+100),
                            np.log1p(np.maximum(features[:,10],0)))).astype(np.float32)
 if not np.all(np.isfinite(conditional)):raise AssertionError('ASOF_FEATURE_NAN')
 return conditional

def chronological_splits(t,trace,mon):
 sigms=t[trace[:,0].astype(np.int32)]
 first=int(np.datetime64('2026-'+mon+'-01T00:00:00','ms').astype(np.int64))
 day=(sigms-first)//86400000 + 1
 completed=np.isin(trace[:,3],np.array([0,1,2]))
 # >=24h purge from train to calibration and from calibration to test.
 train=completed&(day<=TRAIN_END_DAY)
 calibration=completed&(day>=CAL_START_DAY)&(day<=CAL_END_DAY)
 test=completed&(day>=TEST_START_DAY)
 if not train.any() or not calibration.any() or not test.any():raise AssertionError('NOT_ALL_CHRONOLOGICAL_SPLITS_PRESENT')
 assert not np.any(train&test) and not np.any(train&calibration) and not np.any(calibration&test)
 return train,calibration,test,day

def fit_predict(source,mon,outroot=BASE/'h1v2_vnext'/'meta'):
 begin=time.perf_counter();trace,old_hash=original_trace(source,mon)
 t,b,a=load_month(source,mon)
 X=asof_matrix(t,b,a,source,trace)
 train,cal,test,day=chronological_splits(t,trace,mon)
 y=np.where(trace[:,3]==1,1,np.where(trace[:,3]==0,0,2)).astype(np.int32)
 net=trace[:,6].astype(np.float32)
 # This C3 selected cohort is causal at decision time, but action and outcome
 # label are historical. No quota or reference clock labels are model features.
 classifier=lgb.LGBMClassifier(objective='multiclass',num_class=3,n_estimators=100,
   learning_rate=.045,num_leaves=15,max_depth=5,min_child_samples=120,
   reg_lambda=8.,colsample_bytree=.8,subsample=.85,subsample_freq=1,
   random_state=20261104,n_jobs=2,verbose=-1)
 classifier.fit(X[train],y[train])
 reg=lgb.LGBMRegressor(objective='huber',alpha=.8,n_estimators=100,
   learning_rate=.045,num_leaves=15,max_depth=5,min_child_samples=120,
   reg_lambda=8.,colsample_bytree=.8,subsample=.85,subsample_freq=1,
   random_state=20261104,n_jobs=2,verbose=-1)
 reg.fit(X[train],np.clip(net[train],-10000,10000))
 probs=np.asarray(classifier.predict_proba(X),dtype=np.float32)
 if probs.shape!=(len(trace),3):raise AssertionError('PROBABILITY_DIMENSION_ERROR')
 if not np.all(np.isfinite(probs)) or not np.allclose(probs.sum(axis=1),1,atol=2e-4):raise AssertionError('RISK_PROBABILITY_MASS_DRIFT')
 expected=np.asarray(reg.predict(X),np.float32)
 out=outroot/source/mon;out.mkdir(parents=True,exist_ok=True)
 pm=out/f'C4_{source}_{mon}_PURGED_COMPETING_CAUSE_MODEL.txt';classifier.booster_.save_model(str(pm))
 pn=out/f'C4_{source}_{mon}_PURGED_QUOTED_NET_REGRESSION_MODEL.txt';reg.booster_.save_model(str(pn))
 qt,ref=quota(mon)
 def diagnostics(mask):
  cm=mask&np.isin(trace[:,3],[0,1,2])
  yy=trace[cm,3]==1
  pp=probs[cm,1]
  return {'candidate_completed':int(cm.sum()),'observed_target_first':int(yy.sum()),'base_positive_fraction':float(yy.mean()),'roc_auc':float(roc_auc_score(yy,pp)),'average_precision':float(average_precision_score(yy,pp)),'brier':float(brier_score_loss(yy,pp)),'observed_net_raw':int(trace[cm,6].sum())}
 phases={'train_earlier_days':diagnostics(train),'calibration_days':diagnostics(cal),'later_day_test':diagnostics(test)}
 results=[]
 for name,threshold,require_positive_net in BINS:
  mask=test&(probs[:,1]>=threshold)
  if require_positive_net:mask&=(expected>0)
  selected=trace[mask]
  # Frozen C3 positions are all non-overlapping (each C4 is a SUBSET). No
  # past event changes, no optimistic reschedule of formerly busy periods.
  if len(selected)>1:
   f=selected[:,1];ex=selected[:,2]
   if np.any(t[f[1:]]<=t[ex[:-1]]):raise AssertionError('FILTERED_SOURCE_POSITION_OVERLAP')
  buckets=source_report(source,mon,4,t,selected,qt,ref)
  bp={}
  for kind,frame in buckets.items():
   p=out/f'C4_{name}_{source}_{mon}_FULL_{kind.upper()}_UTC.csv'
   frame.to_csv(p,index=False);bp[p.name]={'sha256':sha(p),'bytes':p.stat().st_size,'rows':len(frame)}
  act=selected[:,3]
  lateRef=np.array([d>=TEST_START_DAY for d in ((qt-qt[0])//86400000+1)])
  aQ=buckets['quarter']
  lateH=np.array([d>=TEST_START_DAY for d in ((qt[::4]-qt[0])//86400000+1)])
  aH=buckets['hour']
  summary={'policy':name,'source':source,'month':mon,'train_through_day':TRAIN_END_DAY,'calibration_days':f'{CAL_START_DAY}-{CAL_END_DAY}','test_from_day':TEST_START_DAY,
     'is_conservative_subset_of_preexecuted_C3':True,'no_rescheduling_freed_slots':True,
     'source_original_R9_test_quarter_reference_total':int(ref[lateRef].sum()),
     'selected_test_completed':int(len(selected)),'target_first':int(np.count_nonzero(act==1)),
     'stop_first':int(np.count_nonzero(act==0)),'timeout':int(np.count_nonzero(act==2)),
     'test_precision':float(np.mean(act==1)) if len(selected) else None,'test_quoted_net_raw':int(selected[:,6].sum()),
     'test_active_quarters':int((aQ.R9_reference_active&lateRef).sum()),
     'test_quarter_count_met':int((aQ.r9_count_met&lateRef).sum()),'test_quarter_joint':int((aQ.joint_correct_count_met&lateRef).sum()),
     'test_active_hours':int((aH.R9_reference_active&lateH).sum()),
     'test_hour_count_met':int((aH.r9_count_met&lateH).sum()),'test_hour_joint':int((aH.joint_correct_count_met&lateH).sum()),
     'candidate_phase_diagnostics':phases,'full_UTC_outputs':bp}
  results.append(summary)
  print(json.dumps({k:summary[k] for k in ('policy','source','month','selected_test_completed','target_first','test_precision','test_quoted_net_raw','test_quarter_joint','test_hour_joint')}),flush=True)
 scores=out/f'C4_{source}_{mon}_ALL_ORIGINAL_C3_SOURCE_ACTION_ORDINAL_SCORE_AND_LABELS.npz'
 np.savez_compressed(scores,signal_source_ordinal=trace[:,0],original_fill_quote_ordinal=trace[:,1],original_exit_quote_ordinal=trace[:,2],original_historical_outcome_code=trace[:,3],source_quote_net_raw=trace[:,6],asof_probability_STOP=probs[:,0],asof_probability_TARGET=probs[:,1],asof_probability_TIMEOUT=probs[:,2],asof_expected_net_quoted_raw=expected,train_mask=train,cal_mask=cal,test_mask=test)
 receipt={'source':source,'month':mon,'original_full_c3_source_SHA':old_hash,'current_raw_source_sha':sha((BASE/f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz') if source=='DUKASCOPY_RAW' else BASE/f'XAUUSD_MT5_BROKER_2026_{mon}_ticks_ALL.csv.gz'),
       'classifier_model_sha256':sha(pm),'quoted_net_regressor_sha256':sha(pn),'all_original_candidate_scores_sha256':sha(scores),'original_trace_rows':len(trace),
       'model_purged_chronological_phase_metrics':phases,'four_frozen_gates':results,'elapsed_s':round(time.perf_counter()-begin,2),
       'no_original_EA_modifications':True,'not_a_blind_OOS':True,'not_tradeable':True,'c3_remaining_candidates_not_rescheduled':True}
 f=out/f'C4_{source}_{mon}_ATOMIC_RECEIPT.json';f.write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
 return receipt

def main():
 p=argparse.ArgumentParser();p.add_argument('--source',required=True,choices=SRC);p.add_argument('--month',required=True,choices=MONTHS);a=p.parse_args();fit_predict(a.source,a.month)
if __name__=='__main__':main()
