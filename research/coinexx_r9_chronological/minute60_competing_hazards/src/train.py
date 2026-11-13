"""Static landmark competing-risks discrete-time hazard, five chronological folds.
Hazard pooled across time bins, true at-risk conditioning, BUY/SELL shadow actions.
All training labels known before the held-out month's first decision; missing
60s history is retained as NaN, original R9 opportunity universe preserved.
"""
from __future__ import annotations
import argparse,json,time,os,hashlib,joblib
from pathlib import Path
import numpy as np
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score,average_precision_score
from event_engine import TREND_N,FEATURE_NAMES

BINS=np.array([250,1000,3000,5000,15000],dtype=np.int32)
ROOT=Path('/mnt/data/r9_m60_competing')
BASE_FEATURES=14;HFT_FEATURES=145;FEE=20
MODELS={'r9_context':'base','existing_m60':'prior','event_trend':'trend','event_trend_flow':'flow'}
# Predeclared low-collinearity feature budget for computationally bounded pooled hazards.
# Every action enters the evaluation; only risk-set TRAINING exposures are subsampled.
OLD_HFT_IDX=np.array(list(range(14,117,6))+list(range(117,145,4)),dtype=int)

def monthly(mm):
 v=np.load(ROOT/'derived'/f'event_2026_{mm}.npz',allow_pickle=False)
 old=np.load(Path('/mnt/data/r9_m60_expanded/full_derived')/f'full_month_2026_{mm}.npz',allow_pickle=False)
 if not np.array_equal(old['entry_ordinals'],v['ordinal']) or not np.array_equal(old['entry_times'],v['entry']):
  raise RuntimeError('exact source R9 candidate entry mismatch')
 # each R9 entry yields buy and sell counterfactuals, never future-dependent selection
 raw=np.concatenate([old['features'],v['features']],axis=1)
 actions=np.repeat(raw,2,axis=0)
 action_side=np.tile(np.array([1,-1],dtype='f'),len(v['entry']))
 r9_side=np.repeat(v['r9_side'].astype('f'),2)
 barrier=np.repeat(v['stop'].astype('f'),2)
 target=np.repeat(v['target'].astype('f'),2)
 orig_spread=np.repeat(v['spread'].astype('f'),2)
 # User-facing context: existing R9 features frozen, action-specific side explicit.
 extra=np.stack([action_side,(action_side==r9_side).astype('f'),barrier,target,orig_spread],axis=1)
 X=np.concatenate([actions,extra],axis=1).astype('f')
 cause=v['cause'].reshape(-1).astype(np.int8)
 hit=v['hit_ms'].reshape(-1).astype(np.int32)
 R=v['terminal'].reshape(-1).astype(np.float32)
 dates=np.repeat(v['entry'],2)
 sess=X[:,2]
 return {'month':mm,'X':X,'cause':cause,'hit':hit,'ret':R,'time':dates,'side':action_side,
         'r9_side':r9_side,'stop':barrier,'target':target,'session':sess,'n_orig':len(v['entry'])}

def select_features(X,version):
 # existing frozen 145 raw features; extended causal event-time trend then flow;
 # action metadata appended for all comparisons to keep opponent fair.
 cols=list(range(14))
 if MODELS[version] in ('prior','trend','flow'):cols+=OLD_HFT_IDX.tolist()
 if MODELS[version] in ('trend','flow'):cols+=list(range(145,145+TREND_N))
 if MODELS[version]=='flow':cols+=list(range(145+TREND_N,145+len(FEATURE_NAMES)))
 return np.concatenate((X[:,cols],X[:,-5:]),axis=1)

def bin_index(cause,hit):
 bi=np.searchsorted(BINS,np.maximum(hit,0),side='left')
 bi=np.minimum(bi,len(BINS)-1)
 return np.where(cause>0,bi,len(BINS))

def expanded_at_risk(X,cause,hit,max_per_bin=40000):
 """Return pooled as-of (entry,bin)-risk-set exposures with interval event class."""
 good=cause!=-1
 x=X[good];k=cause[good];h=hit[good];event_bin=bin_index(k,h)
 n_bins=len(BINS);training=[];outcomes=[]
 for b in range(n_bins):
  mask=event_bin>=b
  xbin=x[mask]; event_kind=k[mask]; event_local=event_bin[mask]
  # Deterministic chronological uniform sampling; no label-based selection.
  if len(xbin)>max_per_bin:
   keep=np.linspace(0,len(xbin)-1,max_per_bin,dtype=np.int64)
   xbin=xbin[keep];event_kind=event_kind[keep];event_local=event_local[keep]
  bb=np.full((len(xbin),1),b,dtype='f')
  training.append(np.concatenate((xbin,bb),axis=1))
  outcomes.append(np.where(event_local==b,event_kind,0).astype(np.int8))
 return np.concatenate(training),np.concatenate(outcomes)

def model():
 return LGBMClassifier(objective='multiclass',num_class=3,n_estimators=45,
    learning_rate=.06,num_leaves=11,min_child_samples=130,
    reg_alpha=1.,reg_lambda=17.,colsample_bytree=.87,subsample=.85,
    subsample_freq=1,random_state=20261113,n_jobs=4,verbosity=-1,
    max_bin=31,force_col_wise=True)

def cumulative_incidence(m,X):
 s=np.ones(len(X),dtype=float)
 cf=np.zeros(len(X),dtype=float);ca=np.zeros(len(X),dtype=float)
 out={}
 for bi,t in enumerate(BINS):
  xx=np.hstack([X,np.full((len(X),1),bi,dtype='f')])
  p=m.predict_proba(xx)
  pf=np.clip(p[:,1],0,1);pa=np.clip(p[:,2],0,1)
  cf+=s*pf;ca+=s*pa
  s*=np.maximum(0,1.-pf-pa)
  if t in (5000,15000):out[int(t)]={'p_fav':cf.copy(),'p_adv':ca.copy(),'p_alive':s.copy()}
 return out

def score_month(rows,clf,version,train_score_cut):
 out={'model':version,'horizons':{}}
 for r in rows:
  X=select_features(r['X'],version)
  preds=cumulative_incidence(clf,X)
  o={'evaluation_month':r['month'],'total_r9_entries':r['n_orig'],'action_count':len(r['cause'])}
  for ms in (5000,15000):
   q=preds[ms]
   y=(r['cause']==1)&(r['hit']>=0)&(r['hit']<=ms)
   good=r['cause']!=-1
   if np.unique(y[good]).size<2:raise ValueError('degenerate target')
   pf=q['p_fav'];pa=q['p_adv']; s=q['p_alive']
   # Upper bound: scores of two sides at the SAME original R9 decision time.
   # Not a chronological trading policy, includes overlapping hypothetical actions.
   utility=pf*(r['target']-FEE)-pa*(r['stop']+FEE)-s*(FEE)
   n=len(r['cause'])//2
   buy=utility[::2];sell=utility[1::2]
   choices=np.where(buy>sell,0,1)
   best=np.arange(n)*2+choices
   r9=np.arange(n)*2+np.where(r['r9_side'][::2]==1,0,1)
   selected = best[utility[best] > 0]
   # Separate high-volume diagnostic: fixed TRAIN-only utility quantile.
   selected75=best[utility[best]>=train_score_cut[ms]]
   selected75=selected75[good[selected75]]
   selected_y=y[selected]
   o[str(ms)]={
    'auc_all_actions':float(roc_auc_score(y[good],pf[good])),
    'ap_all_actions':float(average_precision_score(y[good],pf[good])),
    'target_positive_rate':float(y[good].mean()),
    'auc_R9_action':float(roc_auc_score(y[r9][good[r9]],pf[r9][good[r9]])) if np.unique(y[r9][good[r9]]).size>1 else None,
    'action_best_side_count':int(len(best)),'positive_utility_decisions':int(len(selected)),
    'positive_utility_coverage':float(len(selected)/n),
    'quote_price_net_proxy':(float(np.mean(r['ret'][selected]-FEE)/100) if len(selected)>0 else None) if ms==15000 else None,
    'positive_utility_selected_fav_first':float(np.mean(selected_y)) if len(selected)>0 else None,
    'train_utility_q75_threshold':float(train_score_cut[ms]),
    'top25_training_policy_count':int(len(selected75)),
    'top25_training_policy_coverage':float(len(selected75)/n),
    'top25_training_policy_quote_price_net_15s':float(np.mean(r['ret'][selected75]-FEE)/100) if ms==15000 and len(selected75)>0 else None,
    'economics_note':'15s exits from observed quote side; 5s quote-price EV deliberately unavailable because no 5s liquidation path was stored',
    'no_source_fill_parity':True,
    'r9_same_entry_universe':True,
   }
  out['horizons'][r['month']]=o
 return out

def run(folds=None):
 folds=folds or [4,5,6,7,8]
 results=[];rows=[monthly(f'{i:02}') for i in range(1,10)]
 sizes=[len(r['cause']) for r in rows]
 print('LOADED',sum(z['n_orig'] for z in rows),'R9 opportunities',sum(sizes),'counterfactual sides',flush=True)
 for teix in folds:
  epoch=time.monotonic();tr=rows[:teix];ck=rows[teix]
  if max(q['time'].max() for q in tr)+60000>=ck['time'].min():
   raise RuntimeError('60s calendar purge failed')
  receipt={'train':[x['month'] for x in tr],'test':ck['month'],'source':'9 monthly original Coinexx tick gzip',
    'status':'RETROSPECTIVE_SHADOW_NOT_BROKER_FILLS','models':{}}
  for version in MODELS:
   start=time.monotonic()
   X=np.concatenate([select_features(q['X'],version) for q in tr],axis=0)
   y=np.concatenate([q['cause'] for q in tr]);h=np.concatenate([q['hit'] for q in tr]);
   xx,yy=expanded_at_risk(X,y,h);del y,h
   mod=model();mod.fit(xx,yy); del xx,yy
   # Train-only fixed utility cutoff; no evaluation-month threshold fitting.
   tp=cumulative_incidence(mod,X)
   trainstop=np.concatenate([q['stop'] for q in tr]);traintarget=np.concatenate([q['target'] for q in tr])
   score_cuts={}
   for hms in (5000,15000):
    pred=tp[hms]; pf=pred['p_fav'];pa=pred['p_adv'];alive=pred['p_alive']
    ut=pf*(traintarget-FEE)-pa*(trainstop+FEE)-alive*FEE
    score_cuts[hms]=float(np.quantile(np.maximum(ut[::2],ut[1::2]),.75))
   del X,tp,trainstop,traintarget
   val=score_month([ck],mod,version,score_cuts)
   model_dir=ROOT/'models';model_dir.mkdir(parents=True,exist_ok=True)
   model_path=model_dir/f'{version}_through_{ck["month"]}.joblib'
   joblib.dump({'classifier':mod,'family':version,'evaluated_month':ck['month'],
    'bin_end_milliseconds':BINS.tolist(),'train_utility_cutoffs':score_cuts,
    'status':'SHADOW_ONLY_NOT_DEPLOYABLE'},model_path,compress=3)
   z=val['horizons'][ck['month']];receipt['models'][version]=z
   receipt['models'][version]['model_file']=model_path.name
   receipt['models'][version]['model_sha256']=hashlib.sha256(model_path.read_bytes()).hexdigest()
   print('FOLD',ck['month'],version,'AUC5',round(z['5000']['auc_all_actions'],5),'AUC15',round(z['15000']['auc_all_actions'],5),
     'R9_AUC5',round(z['5000']['auc_R9_action'],5),'coverage5',round(z['5000']['positive_utility_coverage'],4),
     'EV5',z['5000']['quote_price_net_proxy'],'sec',round(time.monotonic()-start,1),flush=True)
  results.append(receipt)
  (ROOT/'results'/f'fold_{ck["month"]}.json').write_text(json.dumps(receipt,indent=2)+'\n')
  (ROOT/'results'/'five_fold_results.json').write_text(json.dumps({
    'status':'SHADOW_ONLY_OWNER_AUC_FAIL_BELOW_0.75','target_AUC':.80,
    'source':'original Coinexx XAUUSD 72,129,347 source quote rows',
    'training_sampling':'uniform chronological at-risk exposures max 40000 per 250ms/1s/3s/5s/15s bin; all R9 entry opportunities and both actions in evaluation',
    'quote_flow_is_volume':'NO: only raw quote revision counts and completed-second quote-price location; not traded quantity or depth',
    'new_feature_family':'exact-event-time trend-within-trend, quote activity balance and completed-second QAF',
    'barrier':'L=max(30,2*spread,1.5*sqrt(RV1)); G=max(50,1.6L), cents; modeled fee=20 cents',
    'warning':'5/15s separate targets; heldout months exposed in earlier studies; no fresh certification; counterfactual sides do not reproduce future R9 occupancy',
    'folds':results},indent=2)+'\n')
  print('COMPLETE_FOLD',ck['month'],'elapsed_s',round(time.monotonic()-epoch,1),flush=True)
 return results

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--folds',nargs='*',type=int,default=None);a=p.parse_args()
 run(a.folds)
