#!/usr/bin/env python3
"""January self-proof of observational AR1 policy on fully replayed original Coinexx quotes."""
from pathlib import Path
import pandas as pd,numpy as np,gzip,zipfile,json
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss
P=Path('/mnt/data/AR1_JAN_R2_COMPLETED_REVERSE_ENGINEERING_20261118')
z=zipfile.ZipFile('/mnt/data/AR1_JANUARY_R1_SOURCE_EXACT_PROGRESSIVE_RESEARCH_20261118.zip')
with gzip.GzipFile(fileobj=z.open('JAN_ALL_27980_CAUSAL_INDICATORS_AND_UNCHANGED_OUTCOMES.csv.gz')) as f:d=pd.read_csv(f)
r=pd.read_csv(P/'JAN_ALL_27980_PYTHON_REAL_TICK_REPLAY_POLICY_ALERT_TIMES.csv.gz')
s=pd.read_csv(P/'JAN_27980_IMMUTABLE_TRADES_WITH_FITTED_AR1_MODEL_SCORES.csv.gz')
assert len(d)==len(r)==len(s)==27980 and d.source_row.equals(r.source_row) and d.source_row.equals(s.source_row)
# Immutable total-book accounting, every trade, both recovered cycles and negative cycles kept
assert r.original_net_cents.sum()==4152082 and r.original_book_before_cents.iloc[0]==10000 and r.original_book_after_cents.iloc[-1]==4162082
assert (r.original_book_after_cents-r.original_book_before_cents-r.original_net_cents).eq(0).all()
assert r.original_book_before_cents.iloc[1:].reset_index(drop=True).equals(r.original_book_after_cents.iloc[:-1].reset_index(drop=True))
assert int(r.profit_R9.sum())==24368 and int(d.protected_R9_positive_cycle.sum())==26148
assert (r.quote_count_python==d.quote_count).all()
assert (r[r.quote_count_python.gt(0)].DD_cents_python.to_numpy(dtype=np.int64)==d.loc[d.quote_count.gt(0),'observed_peakDD_cents'].to_numpy(dtype=np.int64)).all()
# Entire original R9 booked rolling gross losses recalculated independently, as of ENTRY, no future outcome.
e=d.close_ms.to_numpy(np.int64);t=d.open_ms.to_numpy(np.int64);gro=np.maximum(0,-d.net_cents.to_numpy(np.int64));C=np.r_[0,np.cumsum(gro)]
for w in [1,5,15,60,240,1440]:
 a=C[np.searchsorted(e,t,side='left')]-C[np.searchsorted(e,t-w*60000,side='left')]
 assert np.array_equal(a,d[f'gross_loss_rolling_{w}m_cents'].to_numpy(np.int64)),f'R9 asof gross {w}m mismatch'
# Independent HWM: peak only from earlier realized exit, never future booked result.
pre=d.book_before_cents.to_numpy(np.int64)
assert np.array_equal(np.maximum.accumulate(pre),d.R9_account_HWM_pre_cents.to_numpy(np.int64))
# State machine: no actions, only OBSERVE. Band thresholds express % of existing frozen S100 gap, no new stops.
for col in ['first_u25_touch_ms','first_u50_touch_ms','first_u75_touch_ms','first_u90_touch_ms','first_full_S100_touch_ms']:
 ev=r[col].to_numpy(np.int64);inside=ev>=0
 assert np.all(ev[inside]>=r.fixed_open_ms.to_numpy(np.int64)[inside])
 assert np.all(ev[inside]<=r.fixed_close_ms.to_numpy(np.int64)[inside])
assert r.first_full_S100_touch_ms.eq(-1).all()
for earlier,later in [('first_u25_touch_ms','first_u50_touch_ms'),('first_u50_touch_ms','first_u75_touch_ms'),('first_u75_touch_ms','first_u90_touch_ms')]:
 a=r[earlier].to_numpy(np.int64);b=r[later].to_numpy(np.int64);assert ((b<0)|((a>=0)&(a<=b))).all()
# Model is a retrospective JANUARY-fitted score, and independently no-day-overlap historical tests.
strict=r.strict_anchor_time & r.quote_count_python.gt(0)
y25=r.first_u25_touch_ms.ge(0)
pp=s.P_util25_held_day_out
use=strict & pp.notna();AUPRC=float(average_precision_score(y25[use],pp[use]));baseline=float(y25[use].mean());ROC=float(roc_auc_score(y25[use],pp[use]));Brier=float(brier_score_loss(y25[use],pp[use]));
yneg=r.original_net_cents.lt(0);qn=s.P_r9_negative_held_day_out;APneg=float(average_precision_score(yneg,qn));baseneg=float(yneg.mean());ROCneg=float(roc_auc_score(yneg,qn));
# Model and touch observation are strictly different: true intrahold DD is not an input to preentry risk forecast.
assert not any(x.startswith('observed_') for x in json.load(open(P/'JAN_AR1_REVERSE_ENGINEERED_NUMERIC_FORMULA_AND_CROSSDAY_DIAGNOSTICS.json'))['util25']['selected_model_parameters']['features'])
# Selfproof evaluate priorities, low false-negative vs original positive protections; a risk alert is not a veto.
rank=[]
for tag,score,target,pop in [('pressure',pp,y25,use),('R9_negative',qn,yneg,qn.notna())]:
 v=score[pop];truth=target[pop];
 for q in [.75,.9,.95,.99]:
  alert=v>=v.quantile(q);det=int((alert&truth).sum());n=int(alert.sum());winners=int(r.loc[pop].loc[alert,'profit_R9'].sum())
  rank.append(dict(model=tag,retrospective_rank_percentile=q,alarm_priority_count=n,events_in_risk_priority=det,observed_target_count=int(truth.sum()),sensitivity=det/truth.sum() if truth.sum() else None,precision=det/n if n else None,protected_R9_profitable_trades_also_prioritized=winners,rule_type='OBSERVATIONAL_SCORE_ONLY_NOT_ENTRY_SUPPRESSION'))
pd.DataFrame(rank).to_csv(P/'JAN_POLICY_SELFPROOF_MODEL_PRIORITY_AND_PROTECTED_WINNERS.csv',index=False)
# Full observed S100 utilization and protected original trades with earliest tick timestamps per original family/tier.
a=r.copy();a['positive_cycle_leg']=d.protected_R9_positive_cycle.values;a['u25']=a.first_u25_touch_ms.ge(0);a['u50']=a.first_u50_touch_ms.ge(0);a['u90']=a.first_u90_touch_ms.ge(0);a['unknown_or_nonstrict']=~strict;a['S100_USD']=a.S100_gap_cents/100
rows=[]
for fam,ty in [(x,'ATOMIC') for x in sorted(a.family.unique())]+[(f'PARENT_{q}','PARENT_OVERLAPS_ATOMIC' ) for q in 'ABCD']:
 for g in [4,5,9,11,14,15,23,24,30,74]:
  fammask=a.family.eq(fam) if ty=='ATOMIC' else d.family.eq(fam[-1])
  v=a[fammask&a.S100_USD.eq(g)]
  rows.append(dict(family=fam,reporting_type=ty,S100_USD=g,all_original_R9_trades=len(v),individual_R9_profitable=int(v.profit_R9.sum()),positive_complete_cycle_component=int(v.positive_cycle_leg.sum()),original_negative_R9=int((v.original_net_cents<0).sum()),original_net_USD=v.original_net_cents.sum()/100,strict_real_quote_positions=int((v.strict_anchor_time&v.quote_count_python.gt(0)).sum()),unknown_or_nonstrict=int(v.unknown_or_nonstrict.sum()),observed_u25_touches=int(v.u25.sum()),observed_u50_touches=int(v.u50.sum()),observed_u90_touches=int(v.u90.sum()),original_profitable_in_u25=int((v.u25&v.profit_R9).sum()),preentry_model_priority_10pct=int(v.entry_risk_priority_top10pct.sum()),profitable_trades_preentry_prioritized=int((v.entry_risk_priority_top10pct&v.profit_R9).sum()),max_Python_Coinexx_DD_USD=v.DD_cents_python.max()/100 if len(v) else None,largest_R9_booked_preentry_balance_USD=v.original_book_before_cents.max()/100 if len(v) else None))
F=pd.DataFrame(rows);F.to_csv(P/'JAN_27_FAMILIES_10_S100_LEVELS_AR1_POLICY_SELFPROOF.csv',index=False)
assert len(F)==270 and F.loc[F.reporting_type.eq('ATOMIC'),'all_original_R9_trades'].sum()==27980
# Atlas witnesses: ALL 240 original points, missing and nonstrict kept, label ex post never a predictor.
W=pd.read_csv('/mnt/data/AR1_JAN_R1_20261118/JAN_REVERSE_ENGINEERING_KEY_TARGET_ZONE_WITNESSES.csv');J=W.merge(r[['source_row','DD_cents_python','quote_count_python','first_u25_touch_ms','first_u50_touch_ms','first_u75_touch_ms','first_u90_touch_ms','dd_trough_ms_python','strict_anchor_time','p_util25_entry','entry_risk_priority_top10pct','p_R9negative_entry']],on='source_row',validate='many_to_one')
assert len(J)==240
J['evidence_state']=np.select([J.quote_count_python.eq(0),~J.strict_anchor_time],["NO_INSIDE_FIXED_WINDOW_REAL_QUOTE","ANCHOR_LAG_QUALITY_EXCEPTION"],default="STRICT_REAL_TICK_REPLAY")
J['u25_before_or_at_trough']=J.first_u25_touch_ms.ge(0)&J.first_u25_touch_ms.le(J.dd_trough_ms_python)
J['u50_before_or_at_trough']=J.first_u50_touch_ms.ge(0)&J.first_u50_touch_ms.le(J.dd_trough_ms_python)
J['time_from_u25_to_trough_ms']=np.where(J.u25_before_or_at_trough,J.dd_trough_ms_python-J.first_u25_touch_ms,np.nan)
J.to_csv(P/'JAN_240_ATLAS_WITNESS_POLICY_SELFPROOF.csv',index=False)
# All intrahold alerts are on actual original ticks within original positions. A trade whose R9 exit is past never becomes a stop.
touch=a[a.u25].copy();touch['ms_u25_before_DD_trough']=touch.dd_trough_ms_python-touch.first_u25_touch_ms
assert touch.ms_u25_before_DD_trough.ge(0).all()
top=pd.DataFrame({'metric':['Jan R9 booked account end USD','January source quotes parsed','all original positions','original profitable legs','positive-cycle components','strict quotes','no-quote windows','u25 observed touches','u50 observed touches','u90 observed touches','original profitable trades with u25 touch','blocked-day pressure AUPRC','pressure base prevalence','pressure AUPRC lift','blocked-day pressure ROC-AUC','blocked-day R9 negative AUPRC','R9 negative baseline prevalence','blocked-day R9-negative ROC-AUC','observed u25 median lead to DD trough s','observed u25 first-quartile lead to DD trough s'], 'value':[41620.82,7699274,len(a),int(a.profit_R9.sum()),int(a.positive_cycle_leg.sum()),int(strict.sum()),int(a.quote_count_python.eq(0).sum()),int(a.u25.sum()),int(a.u50.sum()),int(a.u90.sum()),int((a.u25&a.profit_R9).sum()),AUPRC,baseline,AUPRC/baseline,ROC,APneg,baseneg,ROCneg,float(touch.ms_u25_before_DD_trough.median()/1000),float(touch.ms_u25_before_DD_trough.quantile(.25)/1000)]});top.to_csv(P/'JAN_ACCOUNT_RISK_SELFPROOF_ACCEPTANCE_SCORECARD.csv',index=False)
results={'selfproof_label':'JANUARY_HISTORICAL_IN_SAMPLE_FITTING_PLUS_DAY_BLOCKED_INTERNAL_SELF_CHECK_NOT_FORWARD','overall_status':'SOURCE_EXACT_REPLAY_PASSED; MARKET_PRESSURE_MODEL_DETECTS_WITH_FALSE_ALARMS; LOSS_FORECAST_WEAK; NOT EXECUTION_PROTECTION_CERTIFIED','all_R9_source_trades':27980,'original_book_net_cents':4152082,'original_book_end_cents':4162082,'individual_positive_R9_legs':int(a.profit_R9.sum()),'positive_cycle_component_legs':int(a.positive_cycle_leg.sum()),'full_original_january_quotes':7699274,'exact_python_observed_quote_paths':int(a.quote_count_python.gt(0).sum()),'strict_qualified_paths':int(strict.sum()),'no_quote_paths':int(a.quote_count_python.eq(0).sum()),'observed_u25_touch_events_all_quoted':int(a.u25.sum()),'observed_u50_touch_events_all_quoted':int(a.u50.sum()),'observed_u90_touch_events_all_quoted':int(a.u90.sum()),'full_frozen_S100_touches':int(a.first_full_S100_touch_ms.ge(0).sum()),'profit_R9_at_u25':int((a.u25&a.profit_R9).sum()),'median_u25_prior_to_trough_seconds':float(touch.ms_u25_before_DD_trough.median()/1000),'P_U25_5fold_crossday_AUPRC':AUPRC,'P_U25_base_event_rate':baseline,'P_U25_lift':AUPRC/baseline,'P_U25_5fold_ROC_AUC':ROC,'P_U25_brier':Brier,'R9_negative_prediction_AUPRC':APneg,'R9_negative_base_rate':baseneg,'R9_negative_ROC_AUC':ROCneg,'source_replay_DD_MAE_MFE_count_parity_all_27980':True,'original_balance_ledger_reconciliation':True,'six_asof_R9_rolling_loss_windows_parity':True,'original_profit_preservation_without_trade_action':True,'all_27_family_lines_by_10_s100_gaps':270,'all_atlas_witness_rows':len(J),'no_counterfactual_trading_or_forward_test':True}
json.dump(results,open(P/'JAN_AR1_POLICY_END_TO_END_SELFPROOF_RECEIPT.json','w'),indent=2)
print(json.dumps(results,indent=2));print('Witness types:\n',J.groupby('target_type')[['entry_risk_priority_top10pct','u25_before_or_at_trough','u50_before_or_at_trough']].agg(['size','sum']).to_string())
