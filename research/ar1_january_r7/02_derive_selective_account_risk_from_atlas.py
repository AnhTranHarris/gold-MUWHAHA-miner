"""AR1 profit-first selective risk mechanism experiment, strict walk-forward.
1) January source Atlas first: protected trades are NOT low-DD; pre-defined candidate feature groups respond to this finding.
2) Learn causal nonpositive-cycle likelihood at +5/+10/+15s without future outcomes as predictors.
3) Calibrate an action ceiling using only prior-date protected trades.
4) Test on fully later January. No trades suppressed, stopped or rebooked.
A policy only passes action certification if 0 protected collisions AND >=1 unprotected useful signal with independently defensible execution.
"""
from pathlib import Path
import pandas as pd,numpy as np,json
from lightgbm import LGBMClassifier
from sklearn.metrics import average_precision_score,roc_auc_score,precision_recall_curve
O=Path('/mnt/data/AR1_JAN_R7_PROFIT_FIRST_REBUILD_20261118')
T=pd.read_csv(O/'JAN_IMMUTABLE_27980_PROTECTED_CONTEXT.csv.gz')
C=pd.read_csv(O/'JAN_CAUSAL_INTRAHOLD_5_10_15S_CHECKPOINTS.csv.gz')
D=C.merge(T,on='source_row',validate='many_to_one',how='left');assert len(D)==len(C) and len(T)==27980
D['label_N_cycle']=~D.protected_RETROSPECTIVE_ONLY.astype(bool)
D['entry_date']=D.entry_time_broker.str[:10]
D['buy']=D.side.eq('buy').astype(int)
D['leg2']=D.leg.eq(2).astype(int)
D['normalized_DD']=D.peakDD_to_checkpoint_cents/D.gap_cents
D['normalized_MFE']=D.MFE_to_checkpoint_cents/D.gap_cents
D['normalized_MAE']=D.MAE_to_checkpoint_cents/D.gap_cents
D['normalized_current']=D.liquidation_mark_from_first_quote_cents/D.gap_cents
D['intrahold_efficiency']=(D.liquidation_mark_from_first_quote_cents)/(D.total_liquidation_path_travel_cents+1.)
D['ha5_ha15_joint']=D.micro5s_ha_body_atr_side*D.micro15s_ha_body_atr_side
D['fib1_ha5_joint']=D.micro1s_fib_retrace*D.micro5s_ha_body_atr_side
D['fib5_ha15_joint']=D.micro5s_fib_retrace*D.micro15s_ha_body_atr_side
D['quote_intensity_spread']=D.quotes10*D.mean_spread60_USD
D['negative_momentum5']=np.maximum(0,-D.last_five_seconds_momentum_cents/D.gap_cents)
D['profit_protection_context']=D.normalized_MFE * np.maximum(0,D.ha5_ha15_joint)
cols_context=['elapsed_entry_s','buy','leg2','gap_cents','original_R9_book_before_cents','quotes10','quotes60','mean_spread60_USD','disp10_USD','disp60_USD','travel10_USD','travel60_USD','normalized_DD','normalized_MFE','normalized_MAE','normalized_current','intrahold_efficiency','last_spread_cents','last_five_seconds_momentum_cents','quote_count_cumulative','total_liquidation_path_travel_cents','negative_momentum5']
cols_fibha=['micro1s_ha_body_atr_side','micro5s_ha_body_atr_side','micro15s_ha_body_atr_side','micro1s_fib_retrace','micro5s_fib_retrace','micro15s_fib_retrace','ha5_ha15_joint','fib1_ha5_joint','fib5_ha15_joint','profit_protection_context']
train=D.entry_date.le('2026-01-15');cal=D.entry_date.between('2026-01-16','2026-01-20');test=D.entry_date.ge('2026-01-21')
assert train.sum() and cal.sum() and test.sum()
y=D.label_N_cycle.to_numpy(int)
results={}
for tag,features in [('base_atlas_mechanism',cols_context),('atlas_joint_advanced_HA_Fibonacci',cols_context+cols_fibha)]:
 params=dict(n_estimators=180,learning_rate=.04,num_leaves=9,max_depth=4,min_child_samples=90,min_split_gain=.025,reg_lambda=18,colsample_bytree=.88,verbosity=-1,n_jobs=4,random_state=2026)
 pred=np.full(len(D),np.nan)
 # train first/second jointly but phase becomes an explicit causal variable.
 model=LGBMClassifier(**params);model.fit(D.loc[train,features].replace([np.inf,-np.inf],np.nan),y[train])
 pred[cal]=model.predict_proba(D.loc[cal,features].replace([np.inf,-np.inf],np.nan))[:,1]
 pred[test]=model.predict_proba(D.loc[test,features].replace([np.inf,-np.inf],np.nan))[:,1]
 # trade-level aggregation across 5s/10s/15s; unavailable checkpoints remain unmodeled.
 Z=D[['source_row','entry_date','label_N_cycle','protected_RETROSPECTIVE_ONLY']].copy();Z['score']=pred
 Z=Z[cal|test].groupby('source_row',sort=True).agg({'entry_date':'first','label_N_cycle':'first','protected_RETROSPECTIVE_ONLY':'first','score':'max'}).reset_index()
 oncal=Z.entry_date.le('2026-01-20');ontest=Z.entry_date.ge('2026-01-21')
 protected_cal=Z.loc[oncal&Z.protected_RETROSPECTIVE_ONLY,'score'];threshold=float(protected_cal.max())+1e-10
 # no protected calibrated collisions by construction.  Never move this threshold using test labels.
 triggers=Z.score>threshold
 alert_cal=Z[oncal&triggers];alert_test=Z[ontest&triggers];
 ntest=Z.loc[ontest];ncal=Z.loc[oncal]
 res={'features':features,'train_trade_count':int(D.loc[train,'source_row'].nunique()),'calib_trade_count':len(ncal),'heldout_trade_count':len(ntest),'heldout_nonprotected_count':int(ntest.label_N_cycle.sum()),'heldout_protected_count':int(ntest.protected_RETROSPECTIVE_ONLY.sum()),'threshold_from_calibration_protected_max':threshold,'calib_max_protected_score':float(protected_cal.max()),'calib_nonprotected_alerts':int(alert_cal.label_N_cycle.sum()),'calib_protected_collisions':int(alert_cal.protected_RETROSPECTIVE_ONLY.sum()),'heldout_nonprotected_alerts':int(alert_test.label_N_cycle.sum()),'heldout_protected_collisions':int(alert_test.protected_RETROSPECTIVE_ONLY.sum()),'heldout_AP_per_trade':float(average_precision_score(ntest.label_N_cycle,ntest.score)),'heldout_ROC_AUC_per_trade':float(roc_auc_score(ntest.label_N_cycle,ntest.score)),'heldout_nonprotected_prevalence':float(ntest.label_N_cycle.mean()),'protected_score_tail_quantiles_calibration':{str(q):float(protected_cal.quantile(q)) for q in [.9,.99,.999,1.]},'outcome_known_only_after_original_exit':True,'rule_not_approved_for_execution':True}
 res['protected_accidental_intervention_fail']=res['heldout_protected_collisions']>0
 results[tag]=res
 Z['policy_candidate_signal_NOT_EXECUTED']=triggers
 Z['fit_name']=tag
 if triggers.any():
  flagged=Z.loc[triggers,['source_row','score','label_N_cycle','entry_date']].copy()
  detail=D.loc[D.source_row.isin(flagged.source_row),['source_row','elapsed_entry_s','checkpoint_ms','MFE_to_checkpoint_cents','MAE_to_checkpoint_cents','peakDD_to_checkpoint_cents','liquidation_mark_from_first_quote_cents','last_spread_cents']].copy()
  detail['score_at_checkpoint']=pred[D.source_row.isin(flagged.source_row)]
  detail=detail.merge(flagged,on='source_row',validate='many_to_one')
  detail['crossed_asof_calibration_limit']=detail.score_at_checkpoint>threshold
  detail.to_csv(O/f'JAN_R7_{tag}_TRIGGER_SOURCE_EXACT_CHECKPOINT_WITNESSES.csv',index=False)
 Z.to_csv(O/f'JAN_R7_{tag}_CHRONOLOGICAL_SELECTIVE_STRESS.csv.gz',index=False,compression='gzip')
 print(tag,json.dumps({k:v for k,v in res.items() if k not in ('features','protected_score_tail_quantiles_calibration')},indent=2),flush=True)
O.joinpath('JAN_R7_CHRONOLOGICAL_ZERO_PROTECTED_INTERFERENCE_CANDIDATE_TEST.json').write_text(json.dumps(results,indent=2))
