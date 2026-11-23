"""R04 January fitted REAL outcome meta-label, recorded original 0.01 lot $0.02 fee.
At-risk features are strictly observable at the original R03-generated entry quote.
No R9 synthetic outcome label is used. In-sample model will be independently replayed.
"""
import os
import json,time
from pathlib import Path
import numpy as np,pandas as pd,lightgbm as lgb
R=Path(os.environ.get('R9_R03_FOLDER','/mnt/data/r9_jan_r03'));O=Path(__file__).parent
F=['phase','minute','hour','spread_c','gap_ms','minute_disp','minute_range','minute_ticks','m1_disp','m5_disp','m15_disp','h1_disp','m5_atr','m15_atr','h1_atr','ret1','ret5','ret10','ret20','ret30','ret60','ret300','eff10','eff30','eff60','range10','range60','quotes10','quotes60','quote_imbalance10','m5_position','m15_position','h1_position']
M=['side','leg']+F
trades=pd.read_csv(R/'r03_repro_profit_v02.csv')
trades['net_cash_cents']=trades.net_quote_cents-2
entries=set(trades.entry_time_msc.to_numpy())
w=[]
for df in pd.read_csv(R/'r03_phase_seconds.csv.gz',usecols=['ms']+F,chunksize=160000):
 sub=df[df.ms.isin(entries)]
 if len(sub):w.append(sub)
feat=pd.concat(w,ignore_index=True).set_index('ms')
training=trades.join(feat,on='entry_time_msc',validate='one_to_one')
assert not training[F].isna().any().any()
assert len(training)==37052
X=training[M].to_numpy(dtype='float32')
y=training.net_cash_cents.to_numpy()
# Two independent heads: probability trade clears actual fee; expected cash return severity.
cl=lgb.LGBMClassifier(objective='binary',n_estimators=240,learning_rate=.05,num_leaves=23,max_depth=7,min_child_samples=55,reg_lambda=22,n_jobs=4,verbosity=-1)
cl.fit(X,y>0)
reg=lgb.LGBMRegressor(objective='huber',alpha=.7,n_estimators=240,learning_rate=.05,num_leaves=23,max_depth=7,min_child_samples=55,reg_lambda=22,n_jobs=4,verbosity=-1)
reg.fit(X,y)
cl.booster_.save_model(str(O/'r04_prob_feeprofit_lgb.txt'));reg.booster_.save_model(str(O/'r04_cash_expectancy_huber_lgb.txt'))
pr=cl.predict_proba(X)[:,1];er=reg.predict(X)
from sklearn.metrics import roc_auc_score
q=[]
for level in (.40,.55,.70,.85):
 mask=(pr>=level) & (er>0)
 z=y[mask]
 q.append({'threshold':level,'kept':int(mask.sum()),'fee_winners':int((z>0).sum()),'sum_cash_usd':round(float(z.sum())/100,2),'mean_cash_usd':round(float(z.mean())/100,4) if len(z) else None})
receipt={'source':'R03 original full January independently generated V02 entries, R9 fixed trade labels excluded','training_rows':len(training),'fee_per_trade_cents':2,'fee_positive_base':int((y>0).sum()),'fee_net_base_cents':int(y.sum()),'train_AUC_in_sample':round(float(roc_auc_score(y>0,pr)),5),'train_cash_prediction_corr':round(float(np.corrcoef(y,er)[0,1]),5),'cohort_filter_proxy_NOT_executable':q,'feat':M,'warning':'All metrics in this script are fitted on January outcomes; masks are static cohort filtering and NOT a dynamically re-simulated portfolio. R04 standalone replay mandatory before acceptance.'}
(O/'r04_fit_receipt.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({k:v for k,v in receipt.items() if k!='feat'},indent=2),flush=True)
