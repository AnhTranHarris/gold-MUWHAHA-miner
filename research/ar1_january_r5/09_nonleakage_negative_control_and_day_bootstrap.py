"""Model-level leakage negative-control and day-block uncertainty for January in-sample research."""
from pathlib import Path
import pandas as pd,numpy as np,json,zipfile,gzip
from sklearn.metrics import average_precision_score,roc_auc_score
from lightgbm import LGBMClassifier
O=Path('/mnt/data/AR1_JAN_R5_MECHANISM_FIRST_20261118')
R=json.loads((O/'JAN_STRICT_PREENTRY_HAFIB_COMPARISON.json').read_text())
X=pd.read_csv(O/'JAN_STRICT_PREENTRY_MODEL_FEATURES.csv.gz')
S=pd.read_csv(O/'JAN_STRICT_PREENTRY_27980_POLICY_SCORES.csv.gz')
true=S.original_losing.to_numpy(int);L=S.leg.to_numpy(int);D=S.entry_time_broker.str[:10].to_numpy();days=np.unique(D)
a=S.clean_asof_market_book_oof.to_numpy(float);b=S.clean_asof_HA_Fib_mechanism_interactions_oof.to_numpy(float)
valid=np.isfinite(a)&np.isfinite(b);assert valid.sum()==21069
# Fold/date bootstrap: entire days resampled together, prevents pretending trades independent.
days_test=np.unique(D[valid]);idx_by_day={d:np.where(valid&(D==d))[0] for d in days_test}
rng=np.random.default_rng(20261118);delta=[];prof=[]
for _ in range(300):
 select=rng.choice(days_test,len(days_test),replace=True)
 i=np.concatenate([idx_by_day[day] for day in select])
 if len(np.unique(true[i]))<2:continue
 delta.append(float(average_precision_score(true[i],b[i])-average_precision_score(true[i],a[i])))
ci=np.quantile(delta,[.025,.5,.975]).tolist()
# Minimal negative label control: shuffle Y within day and leg, keep clocks, strata and original feature matrix immutable.
yperm=true.copy();
for day in days:
 for leg in (1,2):
  ids=np.where((D==day)&(L==leg))[0]
  yperm[ids]=rng.permutation(yperm[ids])
assert yperm.sum()==true.sum() and not np.array_equal(yperm,true)
params=dict(n_estimators=150,learning_rate=.04,num_leaves=7,max_depth=4,min_child_samples=150,colsample_bytree=.85,reg_lambda=15,verbosity=-1,n_jobs=4,random_state=2026)
P=np.full(len(D),np.nan)
cols=list(X.columns)
for s,e in [(6,10),(10,14),(14,18),(18,21)]:
 tr=np.where(np.isin(D,days[:s]))[0];te=np.where(np.isin(D,days[s:e]))[0]
 for leg in (1,2):
  ii=tr[L[tr]==leg];jj=te[L[te]==leg]
  m=LGBMClassifier(**params);m.fit(X.iloc[ii][cols],yperm[ii]);P[jj]=m.predict_proba(X.iloc[jj][cols])[:,1]
pvalid=np.isfinite(P)
result={'original_January_loss_prevalence':float(true.mean()),'heldout_21k_loss_prevalence':float(true[valid].mean()),'day_count_evaluated':len(days_test),
 'AP_clean_baseline':float(average_precision_score(true[valid],a[valid])),'AP_atlas_HA_Fib_combined':float(average_precision_score(true[valid],b[valid])),
 'AP_increment_bootstrap_day_blocks_95pct_CI':ci,'AP_increment_daybootstrap_num':len(delta),
 'label_shuffle_per_day_and_leg_preserves_total_loss_count':bool(yperm.sum()==true.sum()),
 'negative_control_shuffled_labels_AP':float(average_precision_score(yperm[pvalid],P[pvalid])),
 'negative_control_shuffled_labels_ROC_AUC':float(roc_auc_score(yperm[pvalid],P[pvalid])),
 'negative_control_shuffled_labels_prevalence':float(yperm[pvalid].mean()),
 'original_untouched_R9_trade_N':int(len(true)),
 'understood_limits':['Repeated January model selection is in-sample, not future OOS','Higher AP does not show an executable account policy preserves R9 profits','Day bootstrap tests incremental HA-Fib uncertainty but is conditional on selected models']}
(O/'JAN_STRICT_ENTRY_NEGATIVE_CONTROL_AND_DAY_BOOTSTRAP.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
