"""Full-January source-exact policy OBSERVER certification; no trading actions.
Atlas drove historical witnesses; no trade censorship; strict Coinexx preentry features only.
"""
import json,hashlib,zipfile,gzip,sys
from pathlib import Path
import numpy as np,pandas as pd
from lightgbm import LGBMClassifier
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss
O=Path('/mnt/data/AR1_JAN_R5_MECHANISM_FIRST_20261118')
j=json.loads((O/'JAN_STRICT_PREENTRY_HAFIB_COMPARISON.json').read_text())
modname='clean_asof_HA_Fib_mechanism_interactions'
preds=pd.read_csv(O/'JAN_STRICT_PREENTRY_27980_POLICY_SCORES.csv.gz')
X=pd.read_csv(O/'JAN_STRICT_PREENTRY_MODEL_FEATURES.csv.gz')
z=zipfile.ZipFile('/mnt/data/AR1_JANUARY_R1_SOURCE_EXACT_PROGRESSIVE_RESEARCH_20261118.zip')
with gzip.GzipFile(fileobj=z.open('JAN_ALL_27980_CAUSAL_INDICATORS_AND_UNCHANGED_OUTCOMES.csv.gz')) as fi:d=pd.read_csv(fi)
assert preds.source_row.equals(d.source_row) and len(d)==len(X)==27980
assert d.net_cents.sum()==4152082
assert np.array_equal(preds.original_R9_net_cents.to_numpy(),d.net_cents.to_numpy())
model_features=list(X.columns);assert len(model_features)==105
Y=(d.net_cents<0).to_numpy().astype(int);L=d.leg.to_numpy()
params=dict(n_estimators=150,learning_rate=.04,num_leaves=7,max_depth=4,min_child_samples=150,colsample_bytree=.85,reg_lambda=15,verbosity=-1,n_jobs=4,random_state=2026)
fullpred=np.full(len(d),np.nan);models={}
for leg in [1,2]:
 idx=np.where(L==leg)[0];m=LGBMClassifier(**params);m.fit(X.iloc[idx][model_features],Y[idx]);fullpred[idx]=m.predict_proba(X.iloc[idx][model_features])[:,1]
 fn=O/f'JAN_AR1_STRICT_ASOF_LEG{leg}_FULL_JANUARY_FIT_BOOSTER.txt';m.booster_.save_model(str(fn));models[str(leg)]={'path':fn.name,'sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'num_trees':m.booster_.num_trees(),'n_examples':len(idx),'n_losing_examples':int(Y[idx].sum())}
assert np.isfinite(fullpred).all()
score=preds[modname+'_oof'].to_numpy(float);held=np.isfinite(score)
assert held.sum()==21069 and Y[held].sum()==2637
book_asof_original=d.book_before_cents.to_numpy(np.int64)
assert (10000+np.r_[0,np.cumsum(d.net_cents.to_numpy(np.int64)[:-1])]==book_asof_original).all()
assert d.net_cents.sum()+10000==d.book_after_cents.iloc[-1]
# Deterministic as-of trade gap untouched from original source
step=[(100,4),(700,5),(1100,9),(16200,11),(19900,14),(27500,15),(29300,23),(33200,24),(33300,30),(340100,74)]
def s100(b):
 tier=max(100,int(b//100)*100)
 return max(g for t,g in step if tier>=t)
for row in d.itertuples(): assert s100(row.book_before_cents/100)*100==row.frozen_s100_gap_cents
# Protected trade collision is measured, never blocked or stopped.
report=[]
for tag,idx in [('ALL',np.where(held)[0]),('FIRST_LEGS',np.where(held&(L==1))[0]),('SECOND_LEGS',np.where(held&(L==2))[0])]:
 p=score[idx];yy=Y[idx];idx_hi=idx[p>=.5]
 for t in [.25,.5,.75]:
  sidx=idx[p>=t];report.append({'population':tag,'probability_review_threshold':t,'evaluation_n':len(idx),'alerts':int(len(sidx)),'true_R9_loss_alerts':int(Y[sidx].sum()),'historical_profitable_collisions_if_actuated':int((d.net_cents.iloc[sidx]>0).sum()),'loss_recall':float(Y[sidx].sum()/max(1,yy.sum())),'precision':float(Y[sidx].mean()) if len(sidx) else None,'original_booked_net_if_all_alerted_usd_DIAGNOSTIC_ONLY':round(float(d.net_cents.iloc[sidx].sum())/100,2)})
scorecard=pd.DataFrame(report);scorecard.to_csv(O/'JAN_AR1_STRICT_ENTRY_RESEARCH_ALERT_VS_PROTECTED_PROFITS.csv',index=False)
# Interpret all 27 family*10 tier cells (23 disjoint atomic, 4 overlapping parent).
rows=[]
for name in list(sorted(d.atomic.unique()))+['PARENT_A','PARENT_B','PARENT_C','PARENT_D']:
 mask=(d.family==name[-1]) if name.startswith('PARENT_') else (d.atomic==name)
 for t,gap in step:
  idx=np.where(mask & d.frozen_s100_gap_cents.eq(gap*100))[0]
  oofidx=idx[held[idx]]
  rows.append({'pattern_line':name,'type':'overlapping_PARENT' if name.startswith('PARENT_') else 'atomic','S100_gap_usd':gap,'R9_trades_count':int(len(idx)),'R9_profitable_legs':int((d.net_cents.iloc[idx]>0).sum()),'R9_losing_legs':int((d.net_cents.iloc[idx]<0).sum()),'Coinexx_intrahold_DD_max_USD_quoted_only':float(d.observed_peakDD_cents.iloc[idx].max()/100) if len(idx) else None,'observational_model_chronologically_scored_count':int(len(oofidx)),'chronological_high_risk_p_ge_0p5':int((score[oofidx]>=.5).sum()),'chronological_high_risk_profitable_collisions':int(((score[oofidx]>=.5)&(d.net_cents.iloc[oofidx].to_numpy()>0)).sum())})
assert len(rows)==270 and sum(r['R9_trades_count'] for r in rows if r['type']=='atomic')==len(d)
assert sum(r['R9_profitable_legs'] for r in rows if r['type']=='atomic')==24368
pd.DataFrame(rows).to_csv(O/'JAN_27_FAMILY_X_10_TIER_STRICT_ASOF_SELFPROOF.csv',index=False)
# Check all 240 Atlas reverse engineering witnesses, including unscored train days retained.
w=pd.read_csv('/mnt/data/AR1_JAN_R2_COMPLETED_REVERSE_ENGINEERING_20261118/JAN_ATLAS_WITNESS_MATCHED_CONTROL_MAP.csv')
assert len(w)==240 and d.source_row.is_unique
look=d.set_index('source_row');dctr=pd.DataFrame({'source_row':d.source_row,'held_OOF_pred':score,'full_Jan_fit_pred_in_sample':fullpred}).set_index('source_row')
w['target_historical_net_USD']=w.target_row.map(look.net_cents)/100
w['target_R9_losing_leg']=w.target_row.map(look.net_cents).lt(0)
w['target_held_chrono_prob']=w.target_row.map(dctr.held_OOF_pred)
w['target_full_Jan_fit_prob_in_sample_ONLY']=w.target_row.map(dctr.full_Jan_fit_pred_in_sample)
w['matched_control_held_chrono_prob']=w.control_row.map(dctr.held_OOF_pred)
w['matched_control_full_Jan_fit_prob_in_sample_ONLY']=w.control_row.map(dctr.full_Jan_fit_pred_in_sample)
w['target_S100_gap_USD']=w.target_row.map(look.frozen_s100_gap_cents)/100
w['target_observed_real_quote_DD_USD']=w.target_row.map(look.observed_peakDD_cents)/100
w.to_csv(O/'JAN_240_ATLAS_WITNESS_STRICT_ASOF_POLICY_PROBABILITIES.csv',index=False)
scored=w[w.target_held_chrono_prob.notna()]
byzone=scored.groupby('source_target_type').agg(n=('target_row','count'),source_original_losing=('target_R9_losing_leg','sum'),median_held_pred=('target_held_chrono_prob','median'),mean_held_pred=('target_held_chrono_prob','mean')).reset_index()
byzone.to_csv(O/'JAN_ATLAS_WITNESS_ZONE_POLICY_SCORES.csv',index=False)
# Complete January scored ALL original rows for reproducibility; the in-sample score is *not* an empirical out-of-sample predictive result.
fullout=pd.DataFrame({'source_row':d.source_row,'R9_entry':d.entry_time_broker,'R9_exit':d.exit_time_broker,'R9_original_net_cents':d.net_cents,'R9_original_booked_balance_before_cents':d.book_before_cents,'R9_original_booked_balance_after_cents':d.book_after_cents,'S100_frozen_gap_cents':d.frozen_s100_gap_cents,'leg':d.leg,'family_atomic_retrospective_only':d.atomic,'protected_positive_R9_leg':d.net_cents>0,'protected_positive_cycle_leg':d.protected_R9_positive_cycle,'AR1_strict_entry_Jan_full_fit_DIAGNOSTIC':fullpred,'AR1_strict_entry_prior_training_held_score':score})
fullout.to_csv(O/'JAN_27980_SOURCE_EXACT_STRICT_ENTRY_RISK_OBSERVER_FULL_LEDGER.csv.gz',compression='gzip',index=False)
# Save machine-readable conclusion and hashes (do not hash gigantic original tick libraries here; R1 pinned original source hashes).
metrics=json.loads((O/'JAN_STRICT_PREENTRY_HAFIB_COMPARISON.json').read_text())
model=next(x for x in metrics['cases'] if x['name']==modname)
base=next(x for x in metrics['cases'] if x['name']=='clean_asof_market_book')
report={'status':'JANUARY historical observational risk-prediction engine self-proofed; no trade-altering account governor demonstrated',
 'source_exact_R9_trades':len(d),'source_exact_R9_original_net_USD':round(float(d.net_cents.sum())/100,2),'original_profitable_R9_legs':int((d.net_cents>0).sum()),
 'source_quoted_january_Coinexx_ticks':7699274,'original_fixed_entry_clock_correction_ms':-1000,'independent_raw_tick_parity_witnesses':len(json.loads((O/'JAN_PYTHON_STRICT_ENTRY_RAW_TICK_PARITY.json').read_text())),
 'entry_market_context_must_precede_R9_entry_ms':True,'R9_ledger_unchanged':True,'S100_10_ladder_test_exact_pass':True,
 'all_27_reporting_family_x_10_tier_cells':len(rows),'all_240_target_witnesses_reconciled':len(w),'chronological_pretrained_test_records':int(held.sum()),'chronological_R9_losing_events':int(Y[held].sum()),'all_27980_with_full_january_fitted_score_count':int(np.isfinite(fullpred).sum()),
 'model_name':modname,'predictive':model['pooled_chronological'],'baseline':base['pooled_chronological'],'absolute_AP_increment_from_HA_FIB':float(model['pooled_chronological']['AP']-base['pooled_chronological']['AP']),
 'model_trees':models,'alerts_and_profit_collision_file':'JAN_AR1_STRICT_ENTRY_RESEARCH_ALERT_VS_PROTECTED_PROFITS.csv',
 'science_constraints':['January selection/fitting and diagnostic comparison all in same month','not an independent future period','original R9 net is synthetic not verified Coinexx broker equity','no historical trades filtered/rebooked/stopped','no hypothetical executed account risk protection certified','all 27,980 records preserved','21 same-second previous-exit/next-entry causal ambiguity excluded from prior-risk signal'],
 'sha256_inputs':{nm:hashlib.sha256(Path(path).read_bytes()).hexdigest() for nm,path in [('micro_features',O/'JAN_27980_STRICT_ENTRY_CAUSAL_MICRO_HA_FIB.csv'),('strict_entry_feature_contract',O/'JAN_STRICT_PREENTRY_MODEL_FEATURES.csv.gz'),('atlas_target_control',Path('/mnt/data/AR1_JAN_R2_COMPLETED_REVERSE_ENGINEERING_20261118/JAN_ATLAS_WITNESS_MATCHED_CONTROL_MAP.csv'))]}}
(O/'JAN_AR1_STRICT_ENTRY_COMPLETED_OBSERVER_SELFPROOF_RECEIPT.json').write_text(json.dumps(report,indent=2))
print('FULL_ACCOUNT_SELFPROOF',report['status'],'N',report['source_exact_R9_trades'],'AP',model['pooled_chronological']['AP'],'baseline',base['pooled_chronological']['AP'])
print(scorecard.to_string(index=False))
print('ATLAS ZONES',byzone.to_string(index=False))
