"""AR1 January R7: Atlas N-cycle survival-regime mechanism, not a generic new classifier.
Full original cycle end timing is enforced. Only PRIOR complete cycles enter online features.
The 100/500 prior-cycle intensities and previous 15/60/240m values are computed causally;
all 27,980 original R9 trades retained; 5/10/15s checkpoints as separate views.
"""
from pathlib import Path
import pandas as pd,numpy as np, zipfile,gzip,json
from lightgbm import LGBMClassifier
from sklearn.metrics import average_precision_score,roc_auc_score
O=Path('/mnt/data/AR1_JAN_R7_PROFIT_FIRST_REBUILD_20261118')
Z=zipfile.ZipFile('/mnt/data/AR1_JANUARY_R1_SOURCE_EXACT_PROGRESSIVE_RESEARCH_20261118.zip')
with gzip.GzipFile(fileobj=Z.open('JAN_ALL_27980_CAUSAL_INDICATORS_AND_UNCHANGED_OUTCOMES.csv.gz')) as f:R=pd.read_csv(f)
C=pd.read_csv(O/'JAN_CAUSAL_INTRAHOLD_5_10_15S_CHECKPOINTS.csv.gz');T=pd.read_csv(O/'JAN_IMMUTABLE_27980_PROTECTED_CONTEXT.csv.gz')
assert len(R)==len(T)==27980 and R.source_row.equals(T.source_row)
R['end_ms']=pd.to_datetime(R.exit_time_broker,utc=True).astype('int64')//1000000
R['entry_ms_strict']=pd.to_datetime(R.entry_time_broker,utc=True).astype('int64')//1000000
Q=R.groupby('cycle_id',sort=False).agg(end_ms=('end_ms','max'),net_cents=('net_cents','sum'),cycle_net_cents=('cycle_net_cents','first')).sort_values('end_ms').reset_index()
assert np.array_equal(Q.net_cents,Q.cycle_net_cents), 'cycle reconciliation failure'
assert Q.end_ms.is_monotonic_increasing
end=Q.end_ms.to_numpy(np.int64);neg=(Q.net_cents.to_numpy(np.int64)<=0).astype(int);pn=np.r_[0,np.cumsum(neg)]
entry=R.entry_ms_strict.to_numpy(np.int64)
prior_idx=np.searchsorted(end,entry,side='left')
A=pd.DataFrame({'source_row':R.source_row})
for k in [50,200,500]:
 start=np.maximum(0,prior_idx-k);available=prior_idx-start;raw=pn[prior_idx]-pn[start]
 # beta(1,19) prior only when no prior cycles; fixed prior, not test-learned
 A[f'prior_nonpositive_cycle_rate_{k}']=(raw+1.)/(available+20.)
 A[f'prior_nonpositive_cycle_count_{k}']=raw
for minutes in [15,60,240]:
 lo=np.searchsorted(end,entry-minutes*60000,side='left');raw=pn[prior_idx]-pn[lo]
 A[f'prior_nonpositive_cycles_{minutes}m']=raw
 A[f'prior_all_cycles_{minutes}m']=prior_idx-lo
A['known_prior_cycle_count']=prior_idx
D=C.merge(T,on='source_row',validate='many_to_one');D=D.merge(A,on='source_row',validate='many_to_one')
D['N']=~D.protected_RETROSPECTIVE_ONLY.astype(bool);D['day']=D.entry_time_broker.str[:10]
D['buy']=D.side.eq('buy').astype(int);D['leg2']=D.leg.eq(2).astype(int)
D['norm_dd']=D.peakDD_to_checkpoint_cents/D.gap_cents
D['norm_mae']=D.MAE_to_checkpoint_cents/D.gap_cents
D['norm_mfe']=D.MFE_to_checkpoint_cents/D.gap_cents
D['norm_current_mark']=D.liquidation_mark_from_first_quote_cents/D.gap_cents
D['ha5_ha15_joint']=D.micro5s_ha_body_atr_side*D.micro15s_ha_body_atr_side
D['ha5_fib1_joint']=D.micro5s_ha_body_atr_side*D.micro1s_fib_retrace
D['ha15_fib5_joint']=D.micro15s_ha_body_atr_side*D.micro5s_fib_retrace
D['signed_trend_recovery']=(D.last_five_seconds_momentum_cents/(D.gap_cents))*(D.ha5_ha15_joint)
D['score_proxy']=D.R5_held_day_loss_score.fillna(0)
base=['elapsed_entry_s','buy','leg2','gap_cents','original_R9_book_before_cents','quotes10','quotes60','mean_spread60_USD','disp10_USD','disp60_USD','travel10_USD','travel60_USD','norm_dd','norm_mae','norm_mfe','norm_current_mark','last_spread_cents','last_five_seconds_momentum_cents','quote_count_cumulative','total_liquidation_path_travel_cents']
addon=['micro1s_ha_body_atr_side','micro5s_ha_body_atr_side','micro15s_ha_body_atr_side','micro1s_fib_retrace','micro5s_fib_retrace','micro15s_fib_retrace','ha5_ha15_joint','ha5_fib1_joint','ha15_fib5_joint','signed_trend_recovery']
causal=[c for c in A.columns if c!='source_row']
train=D.day.le('2026-01-15');cal=D.day.between('2026-01-16','2026-01-20');test=D.day.ge('2026-01-21')
y=D.N.to_numpy(int)
res={}
for tag,features in [('cycle_intensity_market',base+causal),('cycle_intensity_market_joint_HA_FIB',base+causal+addon)]:
 mdl=LGBMClassifier(n_estimators=160,learning_rate=.035,num_leaves=9,max_depth=4,min_child_samples=80,reg_lambda=20,min_split_gain=.025,verbosity=-1,n_jobs=4,random_state=2026)
 mdl.fit(D.loc[train,features],y[train]);p=np.full(len(D),np.nan);sel=cal|test;p[sel]=mdl.predict_proba(D.loc[sel,features])[:,1]
 V=D[['source_row','day','N','protected_RETROSPECTIVE_ONLY']].copy();V['p']=p;V=V[sel].groupby('source_row').agg({'day':'first','N':'first','protected_RETROSPECTIVE_ONLY':'first','p':'max'}).reset_index()
 cc=V.day.le('2026-01-20');tt=V.day.ge('2026-01-21');threshold=V.loc[cc&V.protected_RETROSPECTIVE_ONLY,'p'].max()+1e-10
 hits=V.p>threshold
 perf={'heldout_n':int(tt.sum()),'heldout_unprotected_n':int(V.loc[tt,'N'].sum()),'heldout_AP':float(average_precision_score(V.loc[tt,'N'],V.loc[tt,'p'])),'heldout_AUC':float(roc_auc_score(V.loc[tt,'N'],V.loc[tt,'p'])),'prior_only_calibrated_ceiling':float(threshold),'calibration_nonprotected_hits':int((cc&hits&V.N).sum()),'calibration_protected_hits':int((cc&hits&V.protected_RETROSPECTIVE_ONLY).sum()),'test_nonprotected_hits':int((tt&hits&V.N).sum()),'test_protected_hits':int((tt&hits&V.protected_RETROSPECTIVE_ONLY).sum()),'time_provenance':'only completed full cycles ending strictly before original R9 textual entry'}
 res[tag]=perf
 V['candidate_not_executed']=hits;V.to_csv(O/f'JAN_R7_{tag}_HELD_DAY_PROFIT_PROTECTION_STRESS.csv.gz',index=False,compression='gzip')
 print(tag,perf,flush=True)
O.joinpath('JAN_R7_ATLAS_REGIME_INTENSITY_CAUSAL_TEST.json').write_text(json.dumps({'models':res,'no_historical_trade_changed':True},indent=2))
