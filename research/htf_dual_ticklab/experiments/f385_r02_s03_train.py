#!/usr/bin/env python3
"""F385-R02-S03: frozen January/February fit and February CAL-only selection;
June/July historically exposed diagnostics; no same-month FILTER08 teacher inference.
"""
import os
os.environ.update(OMP_NUM_THREADS='3',OPENBLAS_NUM_THREADS='3',MKL_NUM_THREADS='3')
import numpy as np, pathlib, zipfile,io,hashlib,json,time,sys,gc
import lightgbm as lgb
from sklearn.metrics import roc_auc_score
P=pathlib.Path('/mnt/data');OUT=P/'F385_R02_S03_RESEARCH_ONLY';M=('01','02','06','07');B=('coinexx','dukascopy')
Z=zipfile.ZipFile(P/'F383_R01_R02_EIGHTCELL_FOURMONTH_UNAPPROVED_RESEARCH_COMPLETE_20261024.zip')
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def identity(b,m):
 d=np.load(OUT/f'F385_S03_{b}_{m}_SOURCE_EVENT_IDENTITY.npz');return {k:d[k].copy() for k in d.files}
def ref(b,m):
 d=np.load(io.BytesIO(Z.read(f'F383_{b}_{m}_SOURCE_EVENT_MASK_AND_THREE_SCORES.npz')));return {k:d[k].copy() for k in d.files}
def xload(b,m):return np.load(OUT/f'F385_S03_{b}_{m}_T0_FEATURES.npy',mmap_mode='r')
def cut(t,frac):return int(np.searchsorted(t,t[0]+(t[-1]-t[0])*frac))
def mask_interval(t,a,b,purge=40000):
 s=cut(t,a);e=cut(t,b) if b<1 else len(t)
 if b<1:e=int(np.searchsorted(t,t[e]-purge))
 return np.arange(s,e,dtype=np.int32)
def metrics(t,side,truth,veto,amb):
 n=len(truth);assert len(veto)==n and not np.any(veto&amb)
 right=truth==0;wrong=~right
 m={'events':n,'correct_total':int(right.sum()),'wrong_total':int(wrong.sum()),'opposite_total':int((truth==1).sum()),'neutral_total':int((truth==2).sum()),'wrong_rejected':int((wrong&veto).sum()),'correct_lost':int((right&veto).sum()),'opposite_rejected':int(((truth==1)&veto).sum()),'neutral_rejected':int(((truth==2)&veto).sum()),'ambiguous_never_veto':int(amb.sum())}
 m['correct_retained']=m['correct_total']-m['correct_lost'];m['incorrect_rejection_rate']=m['wrong_rejected']/max(1,m['wrong_total']);m['correct_retention_rate']=m['correct_retained']/max(1,m['correct_total']);m['veto_wrong_to_right_ratio']=m['wrong_rejected']/max(1,m['correct_lost']);m['kept_correct_precision']=m['correct_retained']/max(1,n-m['wrong_rejected']-m['correct_lost'])
 # Original R9 SYNTH 4178 quota rows NOT present in this bundle. These are necessary proxy floors, NOT a certified R9 test.
 for key,period in [('hour',3600000),('day',86400000)]:
  bucket=t//period;_,group=np.unique(bucket,return_inverse=True);nr=np.bincount(group,weights=right.astype(np.float64));kept=np.bincount(group,weights=(right&~veto).astype(np.float64));ok=nr>0
  m[f'original_correct_{key}_bins']=int(ok.sum());m[f'original_correct_{key}_bins_below90pct']=int(np.sum(ok&(kept<.9*nr)));m[f'original_correct_{key}_min_retention']=float(np.min(kept[ok]/nr[ok])) if ok.any() else None
  # R9 90% SYNTH correct quota may be stricter and on different eligible signals; not interchangeable.
 k=t//3600000*3+(side+1)//2;_,g=np.unique(k,return_inverse=True);tot=np.bincount(g);v=np.bincount(g,weights=veto.astype(float));w=np.bincount(g,weights=wrong.astype(float));m['same_hour_side_random_expected_wrong']=float(np.sum(v*w/tot));m['wrong_above_matched_random']=m['wrong_rejected']-m['same_hour_side_random_expected_wrong']
 return m

def main():
 for b in B:
  for m in M:
   if not (OUT/f'F385_S03_{b}_{m}_T0_FEATURES.npy').exists():raise RuntimeError(f'Missing exact feature cache {b} {m}')
  d={m:identity(b,m) for m in M}
  for m in M:
   r=ref(b,m)
   for key in ('t','side','truth','original_index'):assert np.array_equal(d[m][key],r[key]),(b,m,key)
   del r
  # Train on Jan and Feb FIT70, with 40s label-horizon embargo; no June/July fitting.
  train=[];targets=[]
  for m in ('01','02'):
   t=d[m]['t'];ii=mask_interval(t,0,.70);ii=ii[::5];train.append(np.asarray(xload(b,m)[ii],np.float32));targets.append(d[m]['truth'][ii]);print('TRAIN_SOURCE',b,m,len(ii),flush=True)
  X=np.concatenate(train);Y=np.concatenate(targets)
  del train,targets;gc.collect()
  model=lgb.LGBMClassifier(objective='multiclass',num_class=3,n_estimators=110,num_leaves=511,min_child_samples=65,max_bin=127,learning_rate=.045,reg_lambda=4.0,colsample_bytree=.88,subsample=.9,subsample_freq=1,n_jobs=3,verbosity=-1,random_state=38503 if b=='coinexx' else 38504)
  ts=time.time();model.fit(X,Y);print('TRAINED',b,len(X),'sec',round(time.time()-ts,1),flush=True)
  modfile=OUT/f'F385_S03_{b}_JANFEB_NATIVE_137D_511L_110TREE_IS.txt';modfile.write_text(model.booster_.model_to_string());del X,Y;gc.collect()
  score={}
  for m in M:
   x=xload(b,m);s=np.empty((len(x),3),np.float32)
   for j in range(0,len(x),32768):s[j:j+32768]=model.predict_proba(x[j:j+32768]).astype(np.float32)
   score[m]=s;print('SCORED',b,m,len(s),flush=True)
  del model;gc.collect()
  # Predeclared 8 non-equivalent policies, CAL from Feb 70-80 only; select before looking at Feb VAL or June/July.
  def getrisk(s,mode):
   if mode=='opposite':return s[:,1]
   if mode=='neutral':return s[:,2]
   if mode=='wrong_sum':return s[:,1]+s[:,2]
   if mode=='opposite_guard':return s[:,1]-.5*s[:,0]
   if mode=='neutral_guard':return s[:,2]-.5*s[:,0]
   if mode=='maxwrong_guard':return np.maximum(s[:,1],s[:,2])-.5*s[:,0]
   if mode=='opp_neutral_consensus':return np.minimum(s[:,1],s[:,2])
   if mode=='wrong_margin':return s[:,1]+s[:,2]-s[:,0]
   raise ValueError(mode)
  cal=mask_interval(d['02']['t'],.70,.80);caltruth=d['02']['truth'][cal];calamb=d['02']['ambiguous_same_ms'][cal]
  variants=[]
  for mode in ('opposite','neutral','wrong_sum','opposite_guard','neutral_guard','maxwrong_guard','opp_neutral_consensus','wrong_margin'):
   risk=getrisk(score['02'],mode);goodrisk=risk[cal][(caltruth==0)&(~calamb)]
   for q in (.95,.975,.99,.995,.999):
    threshold=float(np.quantile(goodrisk,q));v=(risk[cal]>threshold)&(~calamb)
    bad=int(((caltruth!=0)&v).sum());good=int(((caltruth==0)&v).sum())
    variants.append({'mode':mode,'correct_CAL_quantile':q,'threshold':threshold,'CAL_wrong_rejected':bad,'CAL_correct_lost':good,'CAL_wrong_to_right':bad/max(good,1)})
  qualified=[x for x in variants if x['CAL_wrong_to_right']>=20 and x['CAL_wrong_rejected']>=500]
  if qualified:sel=max(qualified,key=lambda z:z['CAL_wrong_rejected']);status='CAL_20_TO_1_CANDIDATE_REQUIRES_VAL_AND_R9'
  else:sel=next(z for z in variants if z['mode']=='wrong_sum' and z['correct_CAL_quantile']==.995);status='NO_CAL_20_TO_1_500_WRONG_QUALIFIER_PARK'
  report={'experiment':'F385-R02-S03','status':'HISTORICALLY_EXPOSED_RESEARCH_ONLY_UNAPPROVED','selection_status':status,'broker':b,'original_t0':True,'fit':'January and February first 70% each; every 5th event, 40s embargo; no June/July fitting','calibration':'February 70-80% only, 40s purge before 80%; frozen before Feb VAL and June/July','validation':'February 80-90% then 90-100% exposed diagnostic; June/July historically exposed transfer, never blind','model':{'sha256':sha(modfile),'trees':110,'leaves':511,'features':137,'three_class':True},'CAL_qualified_20to1_500bad':len(qualified),'selected_CAL_only':sel,'all_40_CAL_trials':variants,'cells':{},'reference_f383':'frozen earlier 4month trained scores; not an independent out-of-sample comparator'}
  for m in M:
   s=score[m];t=d[m]['t'];side=d[m]['side'];truth=d[m]['truth'];amb=d[m]['ambiguous_same_ms']
   risk=getrisk(s,sel['mode']);v=(risk>sel['threshold'])&~amb
   cell=metrics(t,side,truth,v,amb)
   for label,a,bb in ([('fit',0,.70),('cal',.70,.80),('val',.80,.90),('diag',.90,1)] if m in ('01','02') else [('historical_full',0,1)]):
    if m=='01' and label in ('cal','val','diag'):continue # Jan late precedes Feb training, not validation.
    idx=mask_interval(t,a,bb) if bb<1 else np.arange(cut(t,a),len(t))
    cell[label]={'events':len(idx),'wrong_rejected':int(np.sum(v[idx]&(truth[idx]!=0))),'correct_lost':int(np.sum(v[idx]&(truth[idx]==0)))}
   try:
    refdata=ref(b,m);idx=mask_interval(t,.80,.90) if m=='02' else np.arange(len(t))
    cell['new_wrong_auc']=float(roc_auc_score((truth[idx]!=0).astype(int),s[idx,1]+s[idx,2]))
    cell['f383_4month_fitted_wrong_auc_comparator']=float(roc_auc_score((truth[idx]!=0).astype(int),1-refdata['correct_score'][idx]))
    cell['new_opp_auc']=float(roc_auc_score((truth[idx]==1).astype(int),s[idx,1]))
    cell['new_neutral_auc']=float(roc_auc_score((truth[idx]==2).astype(int),s[idx,2]))
   except ValueError:pass
   report['cells'][m]=cell
   np.savez_compressed(OUT/f'F385_S03_{b}_{m}_FULL_EVENT_SCORES_MASK.npz',original_index=d[m]['original_index'],t=t,side=side,truth=truth,ambiguous_same_ms=amb,opposite_score=s[:,1],neutral_score=s[:,2],correct_score=s[:,0],selected_veto=v)
   print('RESULT',b,m,cell['wrong_rejected'],cell['correct_lost'],'AUC',cell.get('new_wrong_auc'),flush=True)
  report['score_mask_sha256']={m:sha(OUT/f'F385_S03_{b}_{m}_FULL_EVENT_SCORES_MASK.npz') for m in M}
  (OUT/f'F385_S03_{b}_CAL_FROZEN_RESEARCH_SCIENCE.json').write_text(json.dumps(report,indent=2))
  print('BROKER_COMPLETE',b,status,sel,flush=True)
 print('ALL_SCORED',flush=True)
if __name__=='__main__':main()
