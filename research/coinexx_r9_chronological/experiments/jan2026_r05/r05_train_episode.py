"""January ONLY, source-only teacher-forced R9 first/second/exit risk sets.
Original R9 fixed trade windows label supervised training. No target endpoints or realized original booked dollars enter predictor features.
Streaming 1.652M existing causal quote-second states without duplicate raw tick data.
"""
from __future__ import annotations
import os,json,time
from pathlib import Path
import numpy as np,pandas as pd,lightgbm as lgb
from sklearn.metrics import roc_auc_score
O=Path(__file__).parent
S=Path('/mnt/data/r9_jan_r03/r03_phase_seconds.csv.gz')
M=Path('/mnt/data/jan2026_forensic_metrics/2026-01_ALL_27980_TRADES_manifest.csv')
REF=pd.read_csv(M)
assert len(REF)==27980 and (REF.original_booked_net_usd>0).sum()==24368
R={}
EXIT_F=['age','entry_phase','side','leg','mark_c','peak_c','trough_c','drawdown_c','spread_c','gap_ms','phase','hour','minute_disp','minute_range','minute_ticks','m1_disp','m5_disp','m15_disp','h1_disp','m5_atr','m15_atr','h1_atr','ret1','ret5','ret10','ret20','ret30','ret60','eff10','eff30','quotes10','quotes60','quote_imbalance10','m5_position','m15_position','h1_position']
REARM_F=['age_since_first_exit','first_side','first_exit_phase','first_age','first_mark_c','phase','spread_c','gap_ms','hour','minute_disp','minute_range','minute_ticks','m1_disp','m5_disp','m15_disp','h1_disp','m5_atr','m15_atr','h1_atr','ret1','ret5','ret10','ret20','ret30','ret60','eff10','eff30','quotes10','quotes60','quote_imbalance10','m5_position','m15_position','h1_position']
EXTRA=list(set(EXIT_F+REARM_F)-{'age','entry_phase','side','leg','mark_c','peak_c','trough_c','drawdown_c','age_since_first_exit','first_side','first_exit_phase','first_age','first_mark_c'})

def teacher():
 t0=time.time();rows=[]
 ent=REF.entry_sec.to_numpy('int64');ext=REF.exit_sec.to_numpy('int64')
 pieces=[]
 for chunk in pd.read_csv(S,chunksize=130000):
  t=chunk.sec.to_numpy('int64');idx=np.searchsorted(ent,t,side='right')-1
  valid=(idx>=0)&(t<=ext[np.maximum(idx,0)])
  z=chunk.loc[valid,['sec','ms','bid_c','ask_c']+EXTRA].copy();z['ref_id']=idx[valid];pieces.append(z)
 a=pd.concat(pieces,ignore_index=True);del pieces
 a.sort_values(['ref_id','sec'],kind='stable',inplace=True)
 # Strict exact source quote at entry AND exit seconds, no guessed source quotes.
 grp=a.groupby('ref_id',sort=False)
 first=grp.first();last=grp.last();valid_ids=first.index[(first.sec.to_numpy()==ent[first.index]) & (last.sec.to_numpy()==ext[last.index]) &(ext[first.index]>ent[first.index])]
 a=a[a.ref_id.isin(valid_ids)].copy();g=a.groupby('ref_id',sort=False)
 sgn=np.where(REF.iloc[a.ref_id].side.to_numpy()=='BUY',1,-1)
 entry_bid=g.bid_c.transform('first').to_numpy('int64');entry_ask=g.ask_c.transform('first').to_numpy('int64')
 entry_price=np.where(sgn==1,entry_ask,entry_bid)
 mark=np.where(sgn==1,a.bid_c.to_numpy(),a.ask_c.to_numpy());profit=sgn*(mark-entry_price)
 a['age']=a.sec.to_numpy()-ent[a.ref_id];a['entry_phase']=ent[a.ref_id]%60;a['side']=sgn;a['leg']=REF.iloc[a.ref_id].leg.to_numpy();a['mark_c']=profit
 a['peak_c']=a.groupby('ref_id').mark_c.cummax().to_numpy();a['trough_c']=a.groupby('ref_id').mark_c.cummin().to_numpy();a['drawdown_c']=a.peak_c-a.mark_c
 a['y_exit']=(a.sec.to_numpy()==ext[a.ref_id]);a['r9_booked_positive_target']=REF.iloc[a.ref_id].original_booked_net_usd.to_numpy()>0
 # Training weighs the EXIT event vs every at-risk HOLD; no original outcome feature used.
 a[['ref_id','sec','ms']+EXIT_F+['y_exit','r9_booked_positive_target']].to_csv(O/'r05_exit_teacher.csv.gz',index=False,compression={'method':'gzip','compresslevel':1})
 R['exit_teacher']={'rows':len(a),'complete_source_paired_trades':len(valid_ids),'positive_events':int(a.y_exit.sum()),'feature_columns':EXIT_F,'original_booked_winners_covered':int(REF.iloc[valid_ids].original_booked_net_usd.gt(0).sum())}
 # Source-observed state at first exit and entry for training conditional second-leg admissions.
 real_at_first_exit=a[(a.leg==1)&a.y_exit].copy();real_at_first_exit['first_row']=real_at_first_exit.ref_id
 # Need ALL observed seconds for rearm risk within original first-exit minute, but not beyond :47;
 # build separate from original source only once, reusing the same R03 features.
 first_ref=REF[REF.leg==1].copy();first_ref['minute_id']=first_ref.entry_sec//60
 first_map=dict(zip(first_ref.minute_id,first_ref.index))
 second_ref=REF[REF.leg==2].copy();sec_map=dict(zip(second_ref.entry_sec//60,second_ref.entry_sec))
 fixed=real_at_first_exit.set_index('first_row')[['mark_c','age']]
 trainparts=[];first_idx=np.array(sorted(fixed.index),dtype=np.int64)
 fm=np.array(first_ref.minute_id,dtype=np.int64);fi=first_ref.index.to_numpy('int64')
 for ch in pd.read_csv(S,chunksize=140000):
  sec=ch.sec.to_numpy('int64');minute=sec//60; j=np.searchsorted(fm,minute)
  good=(j<len(fm)) & (fm[np.minimum(j,len(fm)-1)]==minute)
  rid=np.full(len(ch),-1,dtype=np.int64);rid[good]=fi[j[good]]
  isvalid=rid>=0;v=np.where(isvalid)[0]
  # Prior R9 first exit is a supervised risk-set boundary, never used in runtime.
  if len(v):
   valid=isvalid & (sec>ext[np.maximum(rid,0)]) & ((sec%60)<=47) & np.isin(rid,first_idx)
  else:continue
  z=ch.loc[valid,['sec','ms']+EXTRA].copy();rr=rid[valid];z['first_ref_id']=rr
  z['age_since_first_exit']=z.sec.to_numpy()-ext[rr];z['first_exit_phase']=ext[rr]%60;z['first_age']=ext[rr]-ent[rr]
  z['first_side']=np.where(REF.iloc[rr].side.to_numpy()=='BUY',1,-1);z['first_mark_c']=fixed.loc[rr,'mark_c'].to_numpy()
  target=z.sec.to_numpy()==pd.Series(z.sec.to_numpy()//60).map(sec_map).to_numpy()
  z['y_rearm']=target.astype(np.int8);trainparts.append(z[['first_ref_id','sec']+REARM_F+['y_rearm']])
 b=pd.concat(trainparts,ignore_index=True)
 # do not label post second-leg entry seconds as negative - censor once reference second leg arrives
 second_times=pd.Series(b.sec.to_numpy()//60).map(sec_map).to_numpy(dtype=float)
 b=b[(~np.isfinite(second_times))|(b.sec.to_numpy()<=second_times)].copy()
 b.to_csv(O/'r05_rearm_teacher.csv.gz',index=False,compression={'method':'gzip','compresslevel':1})
 R['rearm_teacher']={'rows':len(b),'positive_events':int(b.y_rearm.sum()),'first_episode_count':int(b.first_ref_id.nunique()),'feature_columns':REARM_F}
 (O/'r05_teacher_receipt.json').write_text(json.dumps(R,indent=2));print(json.dumps({'elapsed_s':round(time.time()-t0,2),**R},indent=2),flush=True)

# Boosting machinery and tree serialization for direct transparent C++ source-ordinal inference.
def export_forest(model,out,features):
 dump=model.booster_.dump_model();trees=dump['tree_info'];nodes=[];metadata=[]
 def flatten(node,bank):
  k=len(bank);bank.append(None)
  if 'leaf_value' in node:
   bank[k]=[-1,0.0,-1,-1,float(node['leaf_value']),1];return k
  l=flatten(node['left_child'],bank);r=flatten(node['right_child'],bank)
  bank[k]=[int(node['split_feature']),float(node['threshold']),l,r,0.0,1 if node.get('default_left',True) else 0];return k
 for tree in trees:
  bank=[];flatten(tree['tree_structure'],bank);nodes.append(bank)
 # Determine initial intercept by independently computing a few samples; first tree includes init intercept in LightGBM often.
 import numpy as np
 with open(out,'w') as w:
  w.write('R05FOREST 1 '+str(len(features))+' '+str(len(nodes))+'\n')
  w.write(' '.join(features)+'\n')
  for bank in nodes:
   w.write(str(len(bank))+'\n')
   for f,t,l,r,v,dl in bank:w.write(f'{f} {t:.16g} {l} {r} {v:.16g} {dl}\n')
 return len(nodes),sum(len(x) for x in nodes)

def fit():
 t0=time.time();a=pd.read_csv(O/'r05_exit_teacher.csv.gz');b=pd.read_csv(O/'r05_rearm_teacher.csv.gz')
 # No original booked profits or lookahead metadata included in X.
 for name,df,features,ycol in [('exit',a,EXIT_F,'y_exit'),('rearm',b,REARM_F,'y_rearm')]:
  x=df[features].to_numpy('float32');y=df[ycol].to_numpy('int8')
  weights=np.where(y==1,6.0,1.0).astype('float32')
  model=lgb.LGBMClassifier(n_estimators=95,learning_rate=.075,num_leaves=17,max_depth=7,min_child_samples=160,reg_lambda=16.,verbosity=-1,n_jobs=4)
  model.fit(x,y,sample_weight=weights)
  model.booster_.save_model(str(O/f'r05_{name}_hazard_lgb.txt'))
  pr=model.predict_proba(x)[:,1]
  # Raw training AUC is merely a diagnostic, not execution performance.
  meta={'rows':len(df),'labels':int(y.sum()),'AUC_JAN_TRAIN_ONLY':round(float(roc_auc_score(y,pr)),5),'trees':95,'features':features,'top_features':sorted(zip(features,model.feature_importances_.astype(int).tolist()),key=lambda t:-t[1])[:12]}
  nt,nn=export_forest(model,O/f'r05_{name}_forest.txt',features)
  meta['forest_nodes']=nn;R[name]=meta
 (O/'r05_fit_receipt.json').write_text(json.dumps({'label_use':'offline January only','runtime_labels_forbidden':True,'elapsed_s':round(time.time()-t0,2),**R},indent=2));print(json.dumps({'elapsed_s':round(time.time()-t0,2),**R},indent=2),flush=True)
if __name__=='__main__':
 import sys
 if sys.argv[1]=='prep':teacher()
 elif sys.argv[1]=='fit':fit()
 else:raise ValueError('Usage prep|fit')
