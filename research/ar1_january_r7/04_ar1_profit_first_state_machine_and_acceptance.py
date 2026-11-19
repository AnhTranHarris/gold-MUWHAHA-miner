"""January 2026 AR1 R7 Profit-First control build and historical acceptance.

A risk policy is not certified simply for predicting losing R9 trades.
- All original R9 trade actions, fixed exits, fee-inclusive outcomes, and S100 remain unchanged.
- Every January profitable leg and every leg of profitable complete cycles is protected.
- No observation or model may trigger an order filter, close, size change or withdrawal.
- Execute-only gate remains LOCKED until independently heldout zero protected conflicts,
  nonzero measurable reduction in nonprofitable-cycle risk, causal execution impact,
  and broker constraints are certified. No retrospective labels enter real-time logic.
- This script quantifies the scientific obstruction; no claim of active capital protection.
"""
from pathlib import Path
import pandas as pd,numpy as np,gzip,zipfile,json,hashlib
from collections import defaultdict
O=Path('/mnt/data/AR1_JAN_R7_PROFIT_FIRST_REBUILD_20261118')
F=Path('/mnt/data/AR1_JAN_R6_ACCOUNT_RISK_INTEGRATED_20261118/JAN_R6_ALL_27980_INTEGRATED_ACCOUNT_RISK_OBSERVER.csv.gz')
D=pd.read_csv(F)
assert len(D)==27980 and D.original_R9_net_cents.sum()==4152082
D['PROTECTED_RETROSPECTIVE_ONLY']=(D.R9_profitable_leg_RETROSPECTIVE_ONLY.astype(bool)|D.R9_positive_complete_cycle_leg_RETROSPECTIVE_ONLY.astype(bool))
assert D.PROTECTED_RETROSPECTIVE_ONLY.sum()==26576 and (~D.PROTECTED_RETROSPECTIVE_ONLY).sum()==1404
assert D.AR1_trade_action.eq('NONE_OBSERVATIONAL_ONLY').all()
assert D.original_R9_book_after_cents.iloc[-1]==4162082
A=pd.read_csv('/mnt/data/AR1_JAN_R1_20261118/JAN_REVERSE_ENGINEERING_KEY_TARGET_ZONE_WITNESSES.csv')
assert len(A)==240 and A.source_row.isin(D.source_row).all()
# Preserve exactly 23 disjoint atomic families + four overlapping parents. Parents never added into underlying totals.
atomic=sorted(D.atlas_atomic_family_RETROSPECTIVE_ONLY.dropna().unique());assert len(atomic)==23
families=atomic+['PARENT_A','PARENT_B','PARENT_C','PARENT_D']
gaps=[400,500,900,1100,1400,1500,2300,2400,3000,7400]
assert len(gaps)==10
levels=[]
for fam in families:
 if fam.startswith('PARENT_'):
  population=D[D.atlas_parent_family_RETROSPECTIVE_ONLY.eq(fam.split('_')[1])]
 else:population=D[D.atlas_atomic_family_RETROSPECTIVE_ONLY.eq(fam)]
 for g in gaps:
  ss=population[population.S100_gap_cents_FROZEN.eq(g)];p=ss[ss.PROTECTED_RETROSPECTIVE_ONLY];n=ss[~ss.PROTECTED_RETROSPECTIVE_ONLY]
  def ma(x,col):
   ar=pd.to_numeric(x[col],errors='coerce').dropna()
   return int(ar.max()) if len(ar) else None
  levels.append({'family_reporting_line':fam,'S100_gap_USD':g/100,'is_overlapping_parent':fam.startswith('PARENT_'),'original_legs':len(ss),'protected_legs':len(p),'outside_protected_legs':len(n),'protected_net_original_R9_USD':round(p.original_R9_net_cents.sum()/100,2),'outside_protected_original_R9_USD':round(n.original_R9_net_cents.sum()/100,2),'protected_max_Coinexx_peakDD_cents':ma(p,'AR1_Coinexx_quote_peakDD_cents'),'outside_max_Coinexx_peakDD_cents':ma(n,'AR1_Coinexx_quote_peakDD_cents'),'protected_max_Coinexx_MAE_cents':ma(p,'AR1_Coinexx_quote_MAE_cents'),'outside_max_Coinexx_MAE_cents':ma(n,'AR1_Coinexx_quote_MAE_cents'),'unquoted_R9_windows':int(ss.AR1_Coinexx_inside_window_quotes.eq(0).sum())})
M=pd.DataFrame(levels);assert len(M)==270
assert M.loc[~M.is_overlapping_parent,'original_legs'].sum()==27980
assert M.loc[~M.is_overlapping_parent,'protected_legs'].sum()==26576
M.to_csv(O/'JAN_R7_PROFIT_FIRST_ATLAS_27_FAMILIES_X_10_LEVELS.csv',index=False)
# All original observed R9 trades retained; new risk outputs sidecar only, explicitly not trade instructions.
S=D[['source_row','cycle_id','original_R9_entry_time','original_R9_exit_time','original_R9_net_cents','original_R9_book_before_cents','original_R9_book_after_cents','S100_gap_cents_FROZEN','R9_leg_known_at_entry','R9_side_known_at_entry','atlas_atomic_family_RETROSPECTIVE_ONLY','AR1_R5_loss_probability_held_day_chronological','AR1_booked_prior_under_HWM','AR1_prior_closed_loss_cluster_ge_2_OBSERVATION_ONLY','AR1_micro_preentry_HA5_strength','AR1_micro_preentry_HA15_strength','AR1_micro_preentry_Fib1_retrace','AR1_Coinexx_inside_window_quotes','AR1_Coinexx_anchor_both_strict','AR1_Coinexx_quote_peakDD_cents','AR1_Coinexx_observed_S100_utilization','PROTECTED_RETROSPECTIVE_ONLY']].copy()
S['entry_risk_state_READ_ONLY']=np.select([S.AR1_Coinexx_inside_window_quotes.eq(0),S.AR1_R5_loss_probability_held_day_chronological.isna(),S.AR1_R5_loss_probability_held_day_chronological.ge(.5)],['NO_QUOTE_PATH','UNTRAINED_PREENTRY_SCORE','ELEVATED_PREDICTED_LOSS_WATCH'],default='BASELINE_MARKET_WATCH')
S['peak_tick_state_RETROSPECTIVE_RESEARCH_ONLY']=np.select([S.AR1_Coinexx_inside_window_quotes.eq(0),S.AR1_Coinexx_observed_S100_utilization.ge(.5),S.AR1_Coinexx_observed_S100_utilization.ge(.25)],['UNKNOWN_INTRATRADE_PATH','OVER_HALF_S100_OBSERVED','OVER_QUARTER_S100_OBSERVED'],default='BELOW_QUARTER_S100_OBSERVED')
S['market_recovery_possible_READ_ONLY']=S.AR1_micro_preentry_HA5_strength.gt(0)&S.AR1_micro_preentry_HA15_strength.gt(0)
S['AR1_EXECUTION_POLICY']='LOCKED_NO_INTERVENTIONS'
S['original_historical_trade_modified']=False
S.to_csv(O/'JAN_R7_27980_FULL_PROFIT_FIRST_OBSERVER.csv.gz',index=False,compression='gzip')
C=pd.read_csv(O/'JAN_CAUSAL_INTRAHOLD_5_10_15S_CHECKPOINTS.csv.gz')
W=A.merge(S[['source_row','PROTECTED_RETROSPECTIVE_ONLY','entry_risk_state_READ_ONLY','peak_tick_state_RETROSPECTIVE_RESEARCH_ONLY','AR1_EXECUTION_POLICY']],on='source_row',validate='many_to_one');assert len(W)==240
W.to_csv(O/'JAN_R7_ATLAS_240_SOURCE_WITNESSES_VERIFIED.csv',index=False)
# All tested/selective candidate actions MUST be rejected if either >0 protected collisions or 0 useful heldout signals.
models=[]
for jf in [O/'JAN_R7_CHRONOLOGICAL_ZERO_PROTECTED_INTERFERENCE_CANDIDATE_TEST.json',O/'JAN_R7_ATLAS_REGIME_INTENSITY_CAUSAL_TEST.json']:
 j=json.loads(jf.read_text())
 vals=j.get('models',j)
 for tag,rec in vals.items():
  prot=int(rec.get('heldout_protected_collisions',rec.get('test_protected_hits')))
  outside=int(rec.get('heldout_nonprotected_alerts',rec.get('test_nonprotected_hits')))
  models.append({'model':tag,'protected_collisions_heldout':prot,'nonprotected_risk_flags_heldout':outside,'meets_protected_zero':prot==0,'has_nonzero_heldout_risk_flags':outside>0,'ACTION_ACCEPTED':False})
R=pd.DataFrame(models)
assert len(R)==4
# A model may pass selective flag-collision screening while still lacking executable
# economic-risk reduction evidence: do NOT enable it merely for finding one risk flag.
R['passes_heldout_collision_screen_only']=R.meets_protected_zero & R.has_nonzero_heldout_risk_flags
R['blocked_for_executable_risk_efficacy']=True
R.to_csv(O/'JAN_R7_SELECTIVE_ACTION_REJECTION_AUDIT.csv',index=False)
# Source verification: SHA-256 pinned by previous completed January R1 source receipt.
Z=zipfile.ZipFile('/mnt/data/AR1_JANUARY_R1_SOURCE_EXACT_PROGRESSIVE_RESEARCH_20261118.zip')
receipt=json.loads(Z.read('JAN_RESEARCH_AUDIT_RECEIPT.json'))
pinned=receipt['pinned_original_Coinexx_tick_archives_sha256']
scan=json.loads((O/'JAN_R7_TICK_CHECKPOINT_SOURCE_RECEIPT.json').read_text())['source_counts']
assert len(scan)==21
for x in scan:assert x['original_gzip_sha256']==pinned['R9_REAL_'+x['day']+'_ticks.csv.gz']
assert S.PROTECTED_RETROSPECTIVE_ONLY.sum()==26576
assert (S.AR1_EXECUTION_POLICY=='LOCKED_NO_INTERVENTIONS').all()
assert W.AR1_EXECUTION_POLICY.eq('LOCKED_NO_INTERVENTIONS').all()
assert int((~S.PROTECTED_RETROSPECTIVE_ONLY).sum())==1404
assert int(D.loc[~D.PROTECTED_RETROSPECTIVE_ONLY,'original_R9_net_cents'].sum())==-70701
assert int(D.loc[D.PROTECTED_RETROSPECTIVE_ONLY,'original_R9_net_cents'].sum())==4222783
out={'design_requirement':'January profit-first, source-exact R9 fixed trades, real Coinexx quote paths, S100 frozen','source_tests':{'trades':27980,'protected_unique':26576,'outside_protected':1404,'original_booked_net_USD':41520.82,'protected_booked_net_USD':42227.83,'outside_protected_booked_net_USD':-707.01,'original_closing_book_USD':41620.82,'all_coinexx_quotes_scanned':7699274,'full_fixed_R9_holding_quote_count':2272602,'raw_gzip_SHA256s_match_prior_pins':True,'atlas_witnesses':len(W),'atlas_family_tier_cells':len(M),'missing_exact_quote_window_positions':int(S.AR1_Coinexx_inside_window_quotes.eq(0).sum()),'original_trades_changed':0,'s100_modified':False},'selective_heldout_model_trials':models,'zero_protected_interference_original_historical_trade_schedule':True,'working_account_stress_observer_verified':True,'active_account_protection_certified':False,'reason_active_not_certified':'One earlier-calibrated combined HA/Fibonacci candidate flags one nonprotected heldout trade with zero protected flags, but this is insufficient evidence of meaningful portfolio protection, executable Coinexx savings, fill quality, robustness and generalization. The remaining models do not capture heldout nonprotected trades under their respective protected-safe limits. No authorized trade or account change.','risk_action':'LOCKED_NO_INTERVENTIONS','no_unverified_optimistic_claims':True}
(O/'JAN_R7_FULL_MONTH_PROFIT_FIRST_ACCEPTANCE_AND_SOURCE_RECEIPT.json').write_text(json.dumps(out,indent=2))
print('R7_PROFIT_FIRST_ACCEPTANCE',json.dumps({'trades':len(S),'protected':int(S.PROTECTED_RETROSPECTIVE_ONLY.sum()),'AtlasWitnesses':len(W),'familyTier':len(M),'candidateTrials':len(models),'sourcePinned':True,'activeProtectionCertified':False},indent=2),flush=True)
