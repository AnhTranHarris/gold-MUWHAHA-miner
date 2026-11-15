"""Predeclared, limited-complexity as-of-entry nonlinear profit mapping.

Frozen time split 2026-01..04 train, 05..06 calibrate, 07..09 later study
(not independent untouched OOS because the overall program used Jan-Sep).
Outcome is original V9 executed quote model, NOT tradable filtered system:
re-arming and capacity shift if entries actually filtered out.
"""
from __future__ import annotations
import numpy as np,pandas as pd,json,sys,joblib
from pathlib import Path
import os
from sklearn.ensemble import HistGradientBoostingRegressor,HistGradientBoostingClassifier
from sklearn.metrics import mean_squared_error,roc_auc_score,average_precision_score
from scipy.stats import spearmanr
ROOT=Path(os.environ.get('CFAEL_V13_OUTPUT','/mnt/data/cfael_v13'))
all=pd.concat([pd.read_csv(ROOT/f'{m:02d}_causal_entry_features.csv.gz') for m in range(1,10)],ignore_index=True)
all=all[all.original_net.notna()].copy()
all['month_num']=all['month'].astype(int)
features=[x for x in all.columns if x not in ('original_net','original_win','month','month_num','entry_ordinal','entry_time_msc','exit_reason')]
features=[x for x in features if x!='side']+['side']
# Source and outcome cannot leak into X; timestamps/month IDs excluded.
train=all[all.month_num<=4];cal=all[(all.month_num>=5)&(all.month_num<=6)];test=all[all.month_num>=7]
X=lambda d:d[features].to_numpy(dtype=np.float64)
reg=HistGradientBoostingRegressor(learning_rate=.06,max_iter=85,max_leaf_nodes=15,min_samples_leaf=350,l2_regularization=12.,max_bins=96,random_state=20261115,early_stopping=False)
reg.fit(X(train),train.original_net)
# Separate narrow classifier diagnostic, not a trading veto.
cls=HistGradientBoostingClassifier(learning_rate=.06,max_iter=85,max_leaf_nodes=15,min_samples_leaf=350,l2_regularization=12.,max_bins=96,random_state=20261115,early_stopping=False)
cls.fit(X(train),train.original_win.astype(int))
for d in (train,cal,test):
 d.loc[:,'pred_net']=reg.predict(X(d))
 d.loc[:,'pred_win']=cls.predict_proba(X(d))[:,1]
# Freeze thresholds on May-Jun only. A rank threshold is never tuned to Jul-Sep net.
thresholds={str(q):float(cal.pred_net.quantile(q)) for q in (.90,.95,.99)}
# Calibration reveals whether this is even worth selecting; no threshold backfit.
def score(d):
 rows=[]
 for key,tt in [('ALL',-np.inf)]+[(f'CAL_TOP_{int(q*100)}PCT',p) for q,p in zip((.90,.95,.99),thresholds.values())]:
  z=d[d.pred_net>=tt]
  w=z.original_net
  rows.append(dict(tier=key,n=len(z),share=round(len(z)/len(d),5),modeled_net_sum=round(w.sum(),2),
   modeled_mean_net=round(w.mean(),5),positive_frac=round((w>0).mean(),5),
   mean_pred_net=round(z.pred_net.mean(),5),by_month={str(k):dict(n=len(g),mean_net=round(g.original_net.mean(),5),net=round(g.original_net.sum(),2),win=round((g.original_net>0).mean(),5)) for k,g in z.groupby('month_num')}))
 return rows
out=dict(snapshot_count=len(all),candidate_source_sha_pins_verified=True,features=features,
 train_months=list(range(1,5)),calibration_months=[5,6],later_months=[7,8,9],
 no_leak_future_measures_in_training=True,
 qualification='Existing V9 outcome associations only. Changing entry signals changes future on-policy rearm/cap, so this is not new strategy PnL.',
 note='All Jan-Sep dates are prior development data; later is chronologically separated but not independent untouched OOS.',
 calibration_thresholds=thresholds,
 training=score(train),calibration=score(cal),later=score(test),
 metrics={name:{'rmse':round(np.sqrt(mean_squared_error(d.original_net,d.pred_net)),5),'win_auc':round(roc_auc_score(d.original_win,d.pred_win),5),
 'pred_net_spearman':round(float(spearmanr(d.pred_net,d.original_net).statistic),5)} for name,d in [('train',train),('cal',cal),('later',test)]})
(ROOT/'V13_PROFIT_MAP_CHRONOLOGICAL_RESULT.json').write_text(json.dumps(out,indent=2))
joblib.dump({'reg':reg,'cls':cls,'features':features,'thresholds':thresholds},ROOT/'V13_RESEARCH_ONLY_profit_mapper.joblib')
print('metrics',out['metrics']);print('thresholds',thresholds)
for a in ('training','calibration','later'):
 print(a,[(x['tier'],x['n'],x['modeled_mean_net'],x['positive_frac']) for x in out[a]])
