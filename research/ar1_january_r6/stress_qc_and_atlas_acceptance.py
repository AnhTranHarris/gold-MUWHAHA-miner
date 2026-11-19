#!/usr/bin/env python3
"""Independent January R6 acceptance and stress analysis, no policy retuning.
Derives only diagnostic/non-operative combinations of immutable R9 booked outcomes
and live-causal Coinexx/AR1 telemetry; never rebooks trades or changes exits.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss
O=Path('/mnt/data/AR1_JAN_R6_ACCOUNT_RISK_INTEGRATED_20261118')
D=pd.read_csv(O/'JAN_R6_ALL_27980_INTEGRATED_ACCOUNT_RISK_OBSERVER.csv.gz')
S=pd.read_csv(O/'JAN_R6_POLICY_RUNTIME_STATE_MACHINE_REPLAY.csv.gz')
T=pd.read_csv(O/'JAN_R6_ALL_27980_REAL_TICK_EVENT_TIMES.csv.gz')
P=pd.read_csv(O/'JAN_R6_MISSING_TICK_PROXY_AND_MASKED_KNOWN_STRESS.csv')
A=pd.read_csv(O/'JAN_R6_ATLAS_240_WITNESS_INTEGRATED_POLICY_STRESS.csv')
C=pd.read_csv(O/'JAN_R6_27_FAMILIES_X_10_FROZEN_S100_POLICY_STRESS.csv')
assert len(D)==len(S)==len(T)==27980 and len(A)==240 and len(C)==270
assert D.source_row.equals(S.source_row) and D.source_row.equals(T.source_row)
assert D.original_R9_net_cents.sum()==4152082 and D.original_R9_book_after_cents.iloc[-1]==4162082
assert S.trade_action.eq('NONE_OBSERVATIONAL_ONLY').all()
assert (D.S100_gap_cents_FROZEN==D.original_R9_book_before_cents*0+ D.S100_gap_cents_FROZEN).all()
assert T.time_first_full_S100_ms.eq(-1).all()
sc=D.AR1_R5_loss_probability_held_day_chronological.notna().to_numpy()
p=D.AR1_R5_loss_probability_held_day_chronological.to_numpy(float)
y=D.original_R9_net_cents.to_numpy()<0
prof=D.original_R9_net_cents.to_numpy()>0
net=D.original_R9_net_cents.to_numpy()
rows=[]
for thr in (.25,.5,.75):
 hi=sc&(p>=thr)
 rows.append({'threshold_DIAGNOSTIC_ONLY':thr,'scored_population':int(sc.sum()),'alert_count':int(hi.sum()),'original_R9_negative_alerts':int((hi&y).sum()),
     'original_R9_profitable_collisions':int((hi&prof).sum()),'original_R9_positive_net_sum_in_flagged_winners_USD_DESCRIPTIVE':round(float(net[hi&prof].sum()/100),2),
     'loss_recall':float((hi&y).sum()/y[sc].sum()),'loss_precision':float((hi&y).sum()/hi.sum()),
     'PERCENT_OF_18k_ORIGINAL_PROFITABLE_LEGS_ALERTED':float((hi&prof).sum()/prof[sc].sum()*100)})
pd.DataFrame(rows).to_csv(O/'JAN_R6_DIAGNOSTIC_ALERT_THRESHOLD_SENSITIVITY.csv',index=False)

# Explicitly test untrained early-capital coverage, missingness, and stressed dates.
D['day']=D.original_R9_entry_time.str[:10]
byday=[]
for name,g in D.groupby('day',sort=True):
 v=g.AR1_R5_loss_probability_held_day_chronological.notna()
 if v.any():
  gt=g.loc[v];truth=gt.original_R9_net_cents.lt(0).to_numpy(bool)
  score=gt.AR1_R5_loss_probability_held_day_chronological.to_numpy(float)
  high=score>=.5
  AP=float(average_precision_score(truth,score))
  brier=float(brier_score_loss(truth,score))
  roc=float(roc_auc_score(truth,score)) if 0<truth.sum()<len(truth) else None
  losers=int(truth.sum());falses=int(((~truth)&high).sum())
 else:
  AP=brier=roc=None;losers=falses=0
 byday.append({'day':name,'original_trades':len(g),'model_earlier_jan_trained_count':int(v.sum()),'original_R9_losers':int(g.original_R9_net_cents.lt(0).sum()),
     'model_AP':AP,'model_Brier':brier,'model_ROC':roc,'model_held_loss_count':losers,
     'model_diagnostic_high_alert_profitable_or_zero_count':falses,
     'Coinexx_no_inside_quote_count':int(g.AR1_Coinexx_exact_path_status.eq('NO_OBSERVED_INSIDE_QUOTE').sum()),
     'Coinexx_observed_u25_count':int(g.AR1_Coinexx_first_u25_msc.ge(0).sum()),
     'Coinexx_observed_u50_count':int(g.AR1_Coinexx_first_u50_msc.ge(0).sum())})
pd.DataFrame(byday).to_csv(O/'JAN_R6_DAYWISE_CHRONOLOGICAL_STRESS.csv',index=False)

# Stress test mutually distinguishable AND/OR diagnostic regimes (no actual trading action).
flag=sc&(p>=.5)
book=D.AR1_booked_prior_under_HWM.to_numpy(bool)
cluster=D.AR1_prior_closed_loss_cluster_ge_2_OBSERVATION_ONLY.to_numpy(bool)
quarter=D.AR1_Coinexx_first_u25_msc.to_numpy(int)>=0
half=D.AR1_Coinexx_first_u50_msc.to_numpy(int)>=0
conds={
 'LOSS_SCORE_ONLY':flag,
 'BOOK_UNDERWATER_ONLY':book,
 'PREVIOUS_CLOSED_LOSS_CLUSTER_ONLY':cluster,
 'LOSS_SCORE_AND_BOOK_UNDERWATER':flag&book,
 'LOSS_SCORE_AND_PRIOR_LOSS_CLUSTER':flag&cluster,
 'LOSS_SCORE_AND_OBSERVED_COINEXX_U25':flag&quarter,
 'LOSS_SCORE_AND_OBSERVED_COINEXX_U50':flag&half,
 'BOOK_UNDERWATER_AND_OBSERVED_U25':book&quarter,
 'HIGH_P_UNDERWATER_OR_PRIOR_CLUSTER':flag&(book|cluster),
 'OBSERVED_QUOTE_U25_INDEPENDENT':quarter,
 'OBSERVED_QUOTE_U50_INDEPENDENT':half,
}
comb=[]
for name,mask in conds.items():
 comb.append({'NONOPERATIVE_CONJUNCTION':name,'tagged_original_trades':int(mask.sum()),
  'historical_loss_legs':int((mask&y).sum()),'historical_winning_legs':int((mask&prof).sum()),
  'historical_net_cents_in_tagged_original_trades_DIAGNOSTIC':int(net[mask].sum()),
  'cohort_R9_profitable_cycle_legs_tagged':int((mask&D.R9_positive_complete_cycle_leg_RETROSPECTIVE_ONLY.to_numpy(bool)).sum()),
  'original_booked_account_path_unmodified':True})
pd.DataFrame(comb).to_csv(O/'JAN_R6_CONJUNCTIVE_RISK_STATE_STRESS.csv',index=False)

# Booked original negative-run source witnesses, detect cycle-preservation conflicts.
losses=y
runs=[];i=0
while i<len(losses):
 if not losses[i]:i+=1;continue
 j=i
 while j<len(losses) and losses[j]:j+=1
 ix=np.arange(i,j);available=ix[sc[ix]]
 runs.append({'first_source_row':int(D.source_row.iloc[i]),'last_source_row':int(D.source_row.iloc[j-1]),'length':j-i,
  'original_R9_booked_total_loss_USD':round(float(net[ix].sum())/100,2),
  'frozen_gap_first_USD':int(D.S100_gap_cents_FROZEN.iloc[i])/100,
  'model_scored_leg_count':int(len(available)),
  'model_preentry_p_ge05_count':int((p[available]>=.5).sum()),
  'first_event_held_p':float(p[i]) if sc[i] else None,
  'R9_book_before_cents':int(D.original_R9_book_before_cents.iloc[i]),
  'R9_book_after_cents':int(D.original_R9_book_after_cents.iloc[j-1])})
 i=j
runs=pd.DataFrame(runs)
runs.to_csv(O/'JAN_R6_ALL_ORIGINAL_NEGATIVE_BOOKED_LOSS_EPISODES.csv.gz',compression='gzip',index=False)
assert int(runs.length.sum())==3606
assert runs.length.max()==4
# 240 witness scores accepted even if warmup untrained.
assert set(A.target_row).issubset(set(D.source_row))
assert C.loc[~C.overlapping_parent,'all_original_R9_trades'].sum()==27980
# Proxy masked test status: report marginal and late-day undercoverage.
proxy=json.load(open(O/'JAN_R6_PROXY_GAP_STRESS_RECEIPT.json'))
source=json.load(open(O/'JAN_R6_INTEGRATED_STRESS_TEST_RECEIPT.json'))
receipt={
 'integration_completed':True,'full_source_replay_completed':True,'observational_risk_state_machine_completed':True,
 'source_exact_parity_mismatch_count':0,'risk_domains_integrated':['BOOKED_BALANCE_HWM','BOOKED_GROSS_LOSS_CLUSTER','STRICT_ENTRY_R5_LOSS_PROB','FIB_HA_COINEXX_MICROSTRUCTURE','INTRAHOLD_S100_UTILIZATION','QUOTE_MISSINGNESS_PROXY'],
 'original_R9_trades':len(D),'original_R9_profitable_legs':int(prof.sum()),'original_R9_negative_legs':int(y.sum()),
 'original_source_28k_total_net_usd':round(net.sum()/100,2),'R9_original_closing_book_usd':41620.82,
 'original_source_Coinexx_real_quotes':source['source_exact_original_Coinexx_REAL_quotes_read'],
 'source_original_negative_consecutive_episodes':len(runs),'longest_negative_original_consecutive_run':int(runs.length.max()),
 'at_held_day_p_0_5':rows[1], 'mask_proxy_stats':proxy,
 'all_ten_S100_tiers_reconciled':source['S100_reference_ladder_all_27980_reconciles'],
 'all_27x10_family_tier_cells':len(C),'atlas_witness_rows':len(A),
 'original_untrained_earliest_6911_cases':int((~sc).sum()),
 'profit_interference_stress_NOT_A_REAL_TRADE_FILTER':True,
 'no_original_books_or_trades_modified':True,
 'actual_account_capital_protection_under_exec_INTERVENTIONS':'NOT_TESTED',
 'latest_held_day_true_generalization':'UNKNOWN',
 'undercoverage_of_nominal_P95_proxy':'FAILED_NOMINAL_95_PERCENT_TARGET',
 'conservative_proxy_P975_masked_historical_coverage':'INTERNAL_RESEARCH_ONLY_PASSING_95_PERCENT_BUT_NOT_INDEPENDENT',
 'risk_policy_authorized_action':'NONE_OBSERVATIONAL_ONLY',
}
(O/'JAN_R6_INTEGRATED_ACCEPTANCE_SCORECARD.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({k:v for k,v in receipt.items() if k!='mask_proxy_stats'},indent=2))
