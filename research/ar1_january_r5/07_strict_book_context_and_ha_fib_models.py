"""January source-exact strict-asof risk inference. Atlas reverse-engineered before feature/model choice.
No trade suppression, no new source data or R9 accounting modifications. Scores are observation only.
"""
from pathlib import Path
import numpy as np,pandas as pd,json,zipfile,gzip,collections,math,hashlib
from lightgbm import LGBMClassifier
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss
O=Path('/mnt/data/AR1_JAN_R5_MECHANISM_FIRST_20261118')
z=zipfile.ZipFile('/mnt/data/AR1_JANUARY_R1_SOURCE_EXACT_PROGRESSIVE_RESEARCH_20261118.zip')
with gzip.GzipFile(fileobj=z.open('JAN_ALL_27980_CAUSAL_INDICATORS_AND_UNCHANGED_OUTCOMES.csv.gz')) as fi:d=pd.read_csv(fi)
M=pd.read_csv(O/'JAN_27980_STRICT_ENTRY_CAUSAL_MICRO_HA_FIB.csv')
assert d.source_row.equals(M.source_row) and len(d)==27980 and d.net_cents.sum()==4152082
strict_entry_ms=(pd.to_datetime(d.entry_time_broker,utc=True).astype('int64')//1000000).to_numpy(np.int64)
strict_exit_ms=(pd.to_datetime(d.exit_time_broker,utc=True).astype('int64')//1000000).to_numpy(np.int64)
assert np.array_equal(M.entry_ms.to_numpy(np.int64),strict_entry_ms)
assert (d.open_ms.to_numpy(np.int64)-strict_entry_ms==1000).all()
assert (strict_exit_ms[:-1]<=strict_entry_ms[1:]).all()
# strictly earlier booked trades; no R9 trade outcomes from an equal timestamp are used for online predictors.
net=d.net_cents.to_numpy(np.int64);n=len(d)
B=pd.DataFrame(index=d.index)
B['side_is_buy']=d.side.eq('buy').astype(int)
B['leg2_at_entry']=d.leg.eq(2).astype(int)
B['ln_S100_gap']=np.log1p(d.frozen_s100_gap_cents/100)
B['ln_original_book_before']=np.log1p(d.book_before_cents/100)
B['S100_to_book']=d.frozen_s100_gap_cents/d.book_before_cents
h=pd.to_datetime(d.entry_time_broker,utc=True)
for item,part,cycle in [('entry_hour',h.dt.hour,24),('entry_minute',h.dt.minute,60)]:
 B[item+'_sin']=np.sin(part*2*np.pi/cycle)
 B[item+'_cos']=np.cos(part*2*np.pi/cycle)
# rolling prior-exit book evidence via original *full ledger*, no loss-only filter.
lastpos=-1
prefix_net=np.r_[0,np.cumsum(net)]
prefix_negative=np.r_[0,np.cumsum(np.where(net<0,net,0))]
prefix_book_hwm=np.maximum.accumulate(10000+prefix_net)

for name in ['sec_since_prior_exit','prior_realized_net_to_gap','prior_realized_loss','prior_realized_side_aligned','previous_3_realized_loss_count','previous_5_realized_loss_count','previous_10_realized_loss_count','previous_3_net_to_gap','gross_1m_to_book','net_1m_to_book','gross_5m_to_book','net_5m_to_book','gross_60m_to_book','net_60m_to_book','gross_240m_to_book','net_240m_to_book','gross_1440m_to_book','net_1440m_to_book','R9_asof_HWM_drawdown_pct','book_tie_ambiguity']:
 B[name]=0.
bf={c:B[c].to_numpy(copy=True) for c in B.columns}
for i in range(n):
 t=strict_entry_ms[i]; j=i-1
 while j>=0 and strict_exit_ms[j]>=t:j-=1
 gap=max(1,int(d.frozen_s100_gap_cents.iloc[i]));book=max(1,int(d.book_before_cents.iloc[i]))
 bf['book_tie_ambiguity'][i]=float(j!=i-1)
 if j>=0:
  bf['sec_since_prior_exit'][i]=float((t-strict_exit_ms[j])/1000)
  bf['prior_realized_net_to_gap'][i]=float(net[j]/gap)
  bf['prior_realized_loss'][i]=float(net[j]<0)
  bf['prior_realized_side_aligned'][i]=float(d.side.iloc[j]==d.side.iloc[i])
  for count in (3,5,10):
   nn=net[max(0,j-count+1):j+1]
   bf[f'previous_{count}_realized_loss_count'][i]=int((nn<0).sum())
  bf['previous_3_net_to_gap'][i]=sum(net[max(0,j-2):j+1])/gap
 for minutes in [1,5,60,240,1440]:
  early=t-minutes*60000;start=np.searchsorted(strict_exit_ms[:max(j+1,0)],early,side='left')
  bf[f'gross_{minutes}m_to_book'][i]=float(-(prefix_negative[j+1]-prefix_negative[start])/book)
  bf[f'net_{minutes}m_to_book'][i]=float((prefix_net[j+1]-prefix_net[start])/book)
 # asof high-water must not include same-second ambiguous exit
 r9_book_asof=10000+prefix_net[j+1];last_known_HWM=prefix_book_hwm[j+1]
 bf['R9_asof_HWM_drawdown_pct'][i]=max(0,(last_known_HWM-r9_book_asof)/max(1,last_known_HWM))
B=pd.DataFrame(bf)
# micro tick-sampled strictly before R9 entry
T=pd.DataFrame(index=d.index)
for k in ['quotes10','quotes60','mean_spread60_USD','disp10_USD','disp60_USD','travel10_USD','travel60_USD','max_jump10_USD','quote_staleness_ms']:
 T[k]=M[k]
side=np.where(d.side=='buy',1,-1)
T['pre_signed_momentum10']=M.disp10_USD*side
T['pre_signed_momentum60']=M.disp60_USD*side
T['pre_abs_efficiency10']=np.abs(M.disp10_USD)/(M.travel10_USD+.01)
T['pre_abs_efficiency60']=np.abs(M.disp60_USD)/(M.travel60_USD+.01)
T['micro_pre_spread_pressure']=(M.mean_spread60_USD)/(1+M.micro15s_atr)
T['micro_quote_stress']=M.quotes10*M.mean_spread60_USD
T['micro_quote_imbalance']=M.quotes10/(M.quotes60/6.+1)
# ATR and last-bar ages are purely prior bar features; zero-tick periods carry unknown state.
HA=[];FIB=[];atr=[]
for tf in [1,5,15,30]:
 p=f'micro{tf}s_'
 age=M[p+'lastbar_age_s'];stale=age>max(3*tf,5)
 for item in ['atr','lastbar_age_s']:
  k=p+item;T[k]=M[k] if item.endswith('age_s') else M[k].where(~stale,np.nan)
  atr.append(k)
 for item in ['ha_body_atr_side','ha_wick_side','ha_dir_side','ha_run','ha_flip7']:
  k=p+item;T[k]=M[k].where(~stale,np.nan);HA.append(k)
 for item in ['fib_retrace','fib_dir_side','fib_amp_atr','fib_level_dist_atr','fib_pivot_age']:
  k=p+item;v=M[k].where(~stale,np.nan).where(M[k]>-1e5,np.nan);T[k]=v;FIB.append(k)
# Scientific premise from Atlas: second-leg profitable large givebacks show strong directional HA alignment, while first-leg loss zones show near-full micro-Fibonacci retracement and reduced trend resiliency.
I=pd.DataFrame(index=d.index)
ha15=T.micro15s_ha_body_atr_side;ha5=T.micro5s_ha_body_atr_side;fib1=T.micro1s_fib_retrace
I['ha5_ha15_joint_strength']=ha15*ha5
I['ha15_ha1_conflict']=ha15*T.micro1s_ha_dir_side
I['firstleg_HA15_fib1_near_full']=(d.leg==1)*np.maximum(0,ha15)*np.exp(-np.abs(fib1-.9))
I['secondleg_HA5_HA15_Fib1_protection']=(d.leg==2)*np.maximum(0,ha15)*np.maximum(0,ha5)*np.exp(-np.abs(fib1-.3))
I['firstleg_fib1_depth_HA15_flip']=(d.leg==1)*np.clip(fib1,0,1.5)*T.micro15s_ha_flip7
I['micro1_HA_reversal_at_Fib_swing']=np.exp(-np.maximum(0,T.micro1s_fib_level_dist_atr))*T.micro1s_ha_flip7
I['micro5_ha_Fib_direction_coherence']=ha5*T.micro5s_fib_dir_side
I['micro15_ha_Fib_retrace_support']=ha15*(1-np.abs(T.micro15s_fib_retrace-.618))
I['secondleg_HA15_good_momentum']=(d.leg==2)*np.maximum(0,ha15)*np.maximum(0,T.pre_signed_momentum10)/(1+np.maximum(0,T.pre_signed_momentum10))
I['micro15_ha1_fib1_failure']=T.micro15s_ha_dir_side*(T.micro1s_ha_dir_side-T.micro15s_ha_dir_side)*np.clip(fib1,0,1.5)
I['prior_loss_HA5_fib1_risk']=B.prior_realized_loss*T.micro5s_ha_flip7*np.clip(fib1,0,1.5)
I['swing_amplitude_ha_stress']=T.micro5s_fib_amp_atr/(1+np.abs(ha15))
X=pd.concat([B,T,I],axis=1);assert not X.columns.duplicated().any()
assert not any(q in X.columns for q in ['observed_peakDD_cents','net_cents','cycle_net_cents','family','atomic'])
# Chronological block evaluation, training always earlier calendar dates. Test all legs including losses.
Y=(net<0).astype(int); DAY=d.entry_time_broker.str[:10].to_numpy();days=np.unique(DAY)
splits=[(np.where(np.isin(DAY,days[:s]))[0],np.where(np.isin(DAY,days[s:e]))[0]) for s,e in [(6,10),(10,14),(14,18),(18,21)]]
core=list(B)+['quotes10','quotes60','mean_spread60_USD','disp10_USD','disp60_USD','travel10_USD','travel60_USD','max_jump10_USD','quote_staleness_ms','pre_signed_momentum10','pre_signed_momentum60','pre_abs_efficiency10','pre_abs_efficiency60','micro_pre_spread_pressure','micro_quote_stress','micro_quote_imbalance']+atr
for k in core:assert k in X
cases={'clean_asof_market_book':core,'clean_asof_plus_ha':core+HA,'clean_asof_plus_fib':core+FIB,'clean_asof_HA_Fib_joint':core+HA+FIB,'clean_asof_HA_Fib_mechanism_interactions':core+HA+FIB+list(I)}
params=dict(n_estimators=150,learning_rate=.04,num_leaves=7,max_depth=4,min_child_samples=150,colsample_bytree=.85,reg_lambda=15,verbosity=-1,n_jobs=4,random_state=2026)
def metric(y,p):return {'AP':float(average_precision_score(y,p)),'AUC':float(roc_auc_score(y,p)),'Brier':float(brier_score_loss(y,p)),'n':int(len(y)),'losses':int(y.sum())}
allres=[];scores=pd.DataFrame({'source_row':d.source_row,'entry_time_broker':d.entry_time_broker,'original_R9_net_cents':net,'original_losing':Y,'leg':d.leg})
for tag,cols in cases.items():
 pred=np.full(n,np.nan);folds=[]
 for fidx,(tr,te) in enumerate(splits,1):
  assert strict_entry_ms[tr].max()<strict_entry_ms[te].min()
  for leg in (1,2):
   ii=tr[d.leg.iloc[tr].to_numpy()==leg];jj=te[d.leg.iloc[te].to_numpy()==leg]
   mdl=LGBMClassifier(**params);mdl.fit(X.iloc[ii][cols],Y[ii]);pred[jj]=mdl.predict_proba(X.iloc[jj][cols])[:,1]
  folds.append({'fold':fidx,'test_first':str(DAY[te[0]]),'test_last':str(DAY[te[-1]]),**metric(Y[te],pred[te])})
 sel=np.isfinite(pred);overall=metric(Y[sel],pred[sel]);by_legs={str(leg):metric(Y[sel & d.leg.eq(leg)],pred[sel & d.leg.eq(leg)]) for leg in (1,2)}
 idx=np.where(sel)[0];top=idx[np.argsort(pred[idx])[::-1][:int(len(idx)*.1)]]
 protected={'top10_n':int(len(top)),'top10_negative':int(Y[top].sum()),'top10_profitable':int((net[top]>0).sum()),'top10_net_original_USD':round(float(net[top].sum())/100,2)}
 print(tag,overall,'firstleg',by_legs['1'],'top protected',protected,flush=True)
 allres.append({'name':tag,'pooled_chronological':overall,'first_second_leg':by_legs,'top_decile':protected,'folds':folds,'feature_count':len(cols)})
 scores[tag+'_oof']=pred
(O/'JAN_STRICT_PREENTRY_HAFIB_COMPARISON.json').write_text(json.dumps({'source':'Original R9 fixed schedule, original Coinexx REAL TickLogger; strict causal at R9 textual second','original_trade_count':n,'original_net_cents':int(net.sum()),'corrected_r1_plus1s_clock_issue':True,'same_second_exit_ambiguity_count':int(B.book_tie_ambiguity.sum()),'research_only':True,'historical_month':'2026-01','model_selection_on_January':True,'cases':allres},indent=2))
scores.to_csv(O/'JAN_STRICT_PREENTRY_27980_POLICY_SCORES.csv.gz',index=False,compression='gzip')
X.to_csv(O/'JAN_STRICT_PREENTRY_MODEL_FEATURES.csv.gz',index=False,compression='gzip')
